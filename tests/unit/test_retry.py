"""Tests for retry logic and circuit breaker functionality."""

import asyncio
import time
import pytest
from unittest.mock import Mock, patch

from ofsc.retry import (
    RetryConfig,
    CircuitBreakerConfig,
    CircuitBreaker,
    RetryHandler,
    CircuitBreakerState,
    with_retry,
    with_circuit_breaker,
    with_fault_tolerance
)
from ofsc.exceptions import (
    OFSException,
    OFSConnectionException,
    OFSTimeoutException,
    OFSRateLimitException,
    OFSServerException
)


class TestRetryConfig:
    """Test retry configuration."""
    
    def test_default_config(self):
        """Test default retry configuration values."""
        config = RetryConfig()
        
        assert config.max_attempts == 3
        assert config.initial_delay == 1.0
        assert config.max_delay == 60.0
        assert config.exponential_base == 2.0
        assert config.jitter is True
        assert 429 in config.retry_on_status_codes
        assert 500 in config.retry_on_status_codes
        assert OFSConnectionException in config.retry_on_exceptions
    
    def test_custom_config(self):
        """Test custom retry configuration."""
        config = RetryConfig(
            max_attempts=5,
            initial_delay=0.5,
            max_delay=30.0,
            exponential_base=1.5,
            jitter=False
        )
        
        assert config.max_attempts == 5
        assert config.initial_delay == 0.5
        assert config.max_delay == 30.0
        assert config.exponential_base == 1.5
        assert config.jitter is False


class TestCircuitBreakerConfig:
    """Test circuit breaker configuration."""
    
    def test_default_config(self):
        """Test default circuit breaker configuration."""
        config = CircuitBreakerConfig()
        
        assert config.failure_threshold == 5
        assert config.timeout_seconds == 60.0
        assert config.expected_exception == OFSException
        assert config.name == "default"
    
    def test_custom_config(self):
        """Test custom circuit breaker configuration."""
        config = CircuitBreakerConfig(
            failure_threshold=3,
            timeout_seconds=30.0,
            expected_exception=OFSConnectionException,
            name="test_breaker"
        )
        
        assert config.failure_threshold == 3
        assert config.timeout_seconds == 30.0
        assert config.expected_exception == OFSConnectionException
        assert config.name == "test_breaker"


class TestRetryHandler:
    """Test retry logic functionality."""
    
    def test_successful_function_no_retry(self):
        """Test that successful functions are not retried."""
        config = RetryConfig(max_attempts=3)
        retry_handler = RetryHandler(config)
        
        mock_func = Mock(return_value="success")
        decorated_func = retry_handler(mock_func)
        
        result = decorated_func("arg1", kwarg1="value1")
        
        assert result == "success"
        assert mock_func.call_count == 1
        mock_func.assert_called_with("arg1", kwarg1="value1")
    
    def test_retry_on_retryable_exception(self):
        """Test retry behavior on retryable exceptions."""
        config = RetryConfig(max_attempts=3, initial_delay=0.01)  # Fast retry for testing
        retry_handler = RetryHandler(config)
        
        mock_func = Mock(side_effect=[
            OFSConnectionException("Connection failed"),
            OFSConnectionException("Connection failed"),
            "success"
        ])
        decorated_func = retry_handler(mock_func)
        
        result = decorated_func()
        
        assert result == "success"
        assert mock_func.call_count == 3
    
    def test_no_retry_on_non_retryable_exception(self):
        """Test that non-retryable exceptions are not retried."""
        config = RetryConfig(max_attempts=3)
        retry_handler = RetryHandler(config)
        
        mock_func = Mock(side_effect=ValueError("Not retryable"))
        decorated_func = retry_handler(mock_func)
        
        with pytest.raises(ValueError, match="Not retryable"):
            decorated_func()
        
        assert mock_func.call_count == 1
    
    def test_retry_exhaustion(self):
        """Test behavior when all retry attempts are exhausted."""
        config = RetryConfig(max_attempts=2, initial_delay=0.01)
        retry_handler = RetryHandler(config)
        
        mock_func = Mock(side_effect=OFSTimeoutException("Timeout"))
        decorated_func = retry_handler(mock_func)
        
        with pytest.raises(OFSTimeoutException, match="Timeout"):
            decorated_func()
        
        assert mock_func.call_count == 2
    
    def test_delay_calculation(self):
        """Test exponential backoff delay calculation."""
        config = RetryConfig(
            initial_delay=1.0,
            exponential_base=2.0,
            max_delay=10.0,
            jitter=False
        )
        retry_handler = RetryHandler(config)
        
        # Test delay calculation for different attempts
        delay_0 = retry_handler._calculate_delay(0, OFSServerException("Error"))
        delay_1 = retry_handler._calculate_delay(1, OFSServerException("Error"))
        delay_2 = retry_handler._calculate_delay(2, OFSServerException("Error"))
        
        assert delay_0 == 1.0  # 1.0 * 2^0
        assert delay_1 == 2.0  # 1.0 * 2^1
        assert delay_2 == 4.0  # 1.0 * 2^2
    
    def test_max_delay_enforcement(self):
        """Test that delays don't exceed max_delay."""
        config = RetryConfig(
            initial_delay=1.0,
            exponential_base=2.0,
            max_delay=3.0,
            jitter=False
        )
        retry_handler = RetryHandler(config)
        
        delay_5 = retry_handler._calculate_delay(5, OFSServerException("Error"))
        assert delay_5 == 3.0  # Capped at max_delay
    
    def test_rate_limit_retry_after(self):
        """Test handling of Retry-After header in rate limit exceptions."""
        config = RetryConfig(max_delay=100.0, jitter=False)
        retry_handler = RetryHandler(config)
        
        rate_limit_exc = OFSRateLimitException("Rate limited", retry_after=30)
        delay = retry_handler._calculate_delay(0, rate_limit_exc)
        
        assert delay == 30.0
    
    @pytest.mark.asyncio
    async def test_async_retry(self):
        """Test retry logic with async functions."""
        config = RetryConfig(max_attempts=3, initial_delay=0.01)
        retry_handler = RetryHandler(config)
        
        call_count = 0
        
        async def async_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise OFSConnectionException("Connection failed")
            return "async_success"
        
        decorated_func = retry_handler(async_func)
        result = await decorated_func()
        
        assert result == "async_success"
        assert call_count == 3


class TestCircuitBreaker:
    """Test circuit breaker functionality."""
    
    def test_initial_state(self):
        """Test circuit breaker initial state."""
        config = CircuitBreakerConfig(name="test_breaker")
        breaker = CircuitBreaker(config)
        
        assert breaker.state == CircuitBreakerState.CLOSED
        assert breaker.stats.failure_count == 0
        assert breaker.stats.success_count == 0
    
    def test_successful_calls(self):
        """Test circuit breaker with successful calls."""
        config = CircuitBreakerConfig(failure_threshold=3)
        breaker = CircuitBreaker(config)
        
        mock_func = Mock(return_value="success")
        decorated_func = breaker(mock_func)
        
        # Multiple successful calls
        for _ in range(5):
            result = decorated_func()
            assert result == "success"
        
        assert breaker.state == CircuitBreakerState.CLOSED
        assert breaker.stats.success_count == 5
        assert breaker.stats.failure_count == 0
    
    def test_circuit_breaker_opens_on_failures(self):
        """Test that circuit breaker opens after threshold failures."""
        config = CircuitBreakerConfig(failure_threshold=3, name="test_breaker")
        breaker = CircuitBreaker(config)
        
        mock_func = Mock(side_effect=OFSConnectionException("Connection failed"))
        decorated_func = breaker(mock_func)
        
        # First few failures should pass through
        for i in range(3):
            with pytest.raises(OFSConnectionException):
                decorated_func()
            
            if i < 2:
                assert breaker.state == CircuitBreakerState.CLOSED
        
        # After threshold, circuit should be open
        assert breaker.state == CircuitBreakerState.OPEN
        assert breaker.stats.failure_count == 3
    
    def test_circuit_breaker_rejects_when_open(self):
        """Test that open circuit breaker rejects calls."""
        config = CircuitBreakerConfig(failure_threshold=2, timeout_seconds=60.0)
        breaker = CircuitBreaker(config)
        
        # Force circuit to open
        mock_func = Mock(side_effect=OFSConnectionException("Connection failed"))
        decorated_func = breaker(mock_func)
        
        # Trigger failures to open circuit
        for _ in range(2):
            with pytest.raises(OFSConnectionException):
                decorated_func()
        
        assert breaker.state == CircuitBreakerState.OPEN
        
        # Now calls should be rejected without calling the function
        mock_func.reset_mock()
        with pytest.raises(OFSConnectionException, match="Circuit breaker.*is OPEN"):
            decorated_func()
        
        assert mock_func.call_count == 0  # Function should not be called
    
    def test_circuit_breaker_half_open_transition(self):
        """Test transition to half-open state after timeout."""
        config = CircuitBreakerConfig(
            failure_threshold=2,
            timeout_seconds=0.1  # Short timeout for testing
        )
        breaker = CircuitBreaker(config)
        
        # Open the circuit
        mock_func = Mock(side_effect=OFSConnectionException("Connection failed"))
        decorated_func = breaker(mock_func)
        
        for _ in range(2):
            with pytest.raises(OFSConnectionException):
                decorated_func()
        
        assert breaker.state == CircuitBreakerState.OPEN
        
        # Wait for timeout
        time.sleep(0.15)
        
        # Next call should transition to half-open
        with pytest.raises(OFSConnectionException):
            decorated_func()
        
        # Should be in half-open state during the call
        # (It will go back to open after the failure)
        assert breaker.state == CircuitBreakerState.OPEN
    
    def test_circuit_breaker_closes_on_success_in_half_open(self):
        """Test that circuit breaker closes on success in half-open state."""
        config = CircuitBreakerConfig(failure_threshold=2, timeout_seconds=0.1)
        breaker = CircuitBreaker(config)
        
        # Open the circuit
        mock_func = Mock(side_effect=OFSConnectionException("Connection failed"))
        decorated_func = breaker(mock_func)
        
        for _ in range(2):
            with pytest.raises(OFSConnectionException):
                decorated_func()
        
        assert breaker.state == CircuitBreakerState.OPEN
        
        # Wait for timeout and set up success
        time.sleep(0.15)
        mock_func.side_effect = None
        mock_func.return_value = "success"
        
        # Successful call should close circuit
        result = decorated_func()
        
        assert result == "success"
        assert breaker.state == CircuitBreakerState.CLOSED
        assert breaker.stats.failure_count == 0
    
    def test_manual_reset(self):
        """Test manual circuit breaker reset."""
        config = CircuitBreakerConfig(failure_threshold=2)
        breaker = CircuitBreaker(config)
        
        # Open the circuit
        mock_func = Mock(side_effect=OFSConnectionException("Connection failed"))
        decorated_func = breaker(mock_func)
        
        for _ in range(2):
            with pytest.raises(OFSConnectionException):
                decorated_func()
        
        assert breaker.state == CircuitBreakerState.OPEN
        
        # Manual reset
        breaker.reset()
        
        assert breaker.state == CircuitBreakerState.CLOSED
        assert breaker.stats.failure_count == 0
    
    @pytest.mark.asyncio
    async def test_async_circuit_breaker(self):
        """Test circuit breaker with async functions."""
        config = CircuitBreakerConfig(failure_threshold=2)
        breaker = CircuitBreaker(config)
        
        async def async_func():
            raise OFSConnectionException("Async connection failed")
        
        decorated_func = breaker(async_func)
        
        # Trigger failures
        for _ in range(2):
            with pytest.raises(OFSConnectionException):
                await decorated_func()
        
        assert breaker.state == CircuitBreakerState.OPEN


class TestFaultToleranceIntegration:
    """Test integration of retry and circuit breaker."""
    
    def test_with_fault_tolerance_decorator(self):
        """Test combined fault tolerance decorator."""
        retry_config = RetryConfig(max_attempts=2, initial_delay=0.01)
        circuit_config = CircuitBreakerConfig(failure_threshold=3)
        
        @with_fault_tolerance(retry_config, circuit_config)
        def test_func():
            raise OFSConnectionException("Test error")
        
        # Should retry and then fail
        with pytest.raises(OFSConnectionException):
            test_func()
    
    def test_with_retry_decorator(self):
        """Test standalone retry decorator."""
        config = RetryConfig(max_attempts=2, initial_delay=0.01)
        
        call_count = 0
        
        @with_retry(config)
        def test_func():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise OFSTimeoutException("Timeout")
            return "success"
        
        result = test_func()
        assert result == "success"
        assert call_count == 2
    
    def test_with_circuit_breaker_decorator(self):
        """Test standalone circuit breaker decorator."""
        config = CircuitBreakerConfig(failure_threshold=2)
        
        @with_circuit_breaker(config)
        def test_func():
            raise OFSServerException("Server error")
        
        # First two calls should pass through
        for _ in range(2):
            with pytest.raises(OFSServerException):
                test_func()
        
        # Third call should be rejected by circuit breaker
        with pytest.raises(OFSConnectionException, match="Circuit breaker.*is OPEN"):
            test_func()


class TestRetryConditions:
    """Test retry condition logic."""
    
    def test_should_retry_with_status_codes(self):
        """Test retry decision based on status codes."""
        config = RetryConfig(retry_on_status_codes=(429, 500, 503))
        retry_handler = RetryHandler(config)
        
        # Create mock exceptions with status codes
        retryable_exc = Mock()
        retryable_exc.status_code = 500
        
        non_retryable_exc = Mock()
        non_retryable_exc.status_code = 400
        
        assert retry_handler._should_retry(retryable_exc, 0) is True
        assert retry_handler._should_retry(non_retryable_exc, 0) is False
    
    def test_should_retry_with_exception_types(self):
        """Test retry decision based on exception types."""
        config = RetryConfig()
        retry_handler = RetryHandler(config)
        
        retryable_exc = OFSConnectionException("Connection failed")
        non_retryable_exc = ValueError("Value error")
        
        assert retry_handler._should_retry(retryable_exc, 0) is True
        assert retry_handler._should_retry(non_retryable_exc, 0) is False
    
    def test_should_not_retry_on_last_attempt(self):
        """Test that retry is not attempted on the last allowed attempt."""
        config = RetryConfig(max_attempts=3)
        retry_handler = RetryHandler(config)
        
        retryable_exc = OFSConnectionException("Connection failed")
        
        assert retry_handler._should_retry(retryable_exc, 0) is True  # Attempt 1
        assert retry_handler._should_retry(retryable_exc, 1) is True  # Attempt 2
        assert retry_handler._should_retry(retryable_exc, 2) is False # Attempt 3 (last)