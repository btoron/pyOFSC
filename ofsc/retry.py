"""Retry logic with exponential backoff and circuit breaker for OFSC Python Wrapper v3.0.

This module provides robust retry mechanisms for handling transient failures
and circuit breaker patterns for fault tolerance.

Requirements covered:
- R7.4: Retry logic with exponential backoff
- R7.5: Circuit breaker pattern for fault tolerance
"""

import asyncio
import random
import time
import logging
from enum import Enum
from typing import Optional, Callable, Any, Union, TYPE_CHECKING
from dataclasses import dataclass, field
from datetime import datetime, timedelta

if TYPE_CHECKING:
    import httpx

from .exceptions import (
    OFSException,
    OFSConnectionException,
    OFSTimeoutException,
    OFSRateLimitException,
    OFSServerException
)


logger = logging.getLogger(__name__)


class CircuitBreakerState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"       # Normal operation
    OPEN = "open"          # Failing, all requests rejected
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""
    
    max_attempts: int = 3
    initial_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True
    retry_on_status_codes: tuple = (429, 500, 502, 503, 504)
    retry_on_exceptions: tuple = (
        OFSConnectionException,
        OFSTimeoutException,
        OFSRateLimitException,
        OFSServerException
    )


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker behavior."""
    
    failure_threshold: int = 5
    timeout_seconds: float = 60.0
    expected_exception: type = OFSException
    name: str = "default"


@dataclass
class CircuitBreakerStats:
    """Statistics for circuit breaker monitoring."""
    
    failure_count: int = 0
    success_count: int = 0
    last_failure_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None
    state_transitions: list = field(default_factory=list)


class CircuitBreaker:
    """Circuit breaker implementation for fault tolerance.
    
    The circuit breaker prevents cascading failures by tracking the number
    of failures and temporarily stopping requests when a threshold is reached.
    """
    
    def __init__(self, config: CircuitBreakerConfig):
        """Initialize circuit breaker.
        
        Args:
            config: Circuit breaker configuration
        """
        self.config = config
        self.state = CircuitBreakerState.CLOSED
        self.stats = CircuitBreakerStats()
        self._last_failure_time: Optional[datetime] = None
        
        logger.info(f"Circuit breaker '{config.name}' initialized")
    
    def __call__(self, func: Callable) -> Callable:
        """Decorator to wrap functions with circuit breaker."""
        if asyncio.iscoroutinefunction(func):
            async def async_wrapper(*args, **kwargs):
                return await self._call_async(func, *args, **kwargs)
            return async_wrapper
        else:
            def sync_wrapper(*args, **kwargs):
                return self._call_sync(func, *args, **kwargs)
            return sync_wrapper
    
    def _call_sync(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection (sync)."""
        if self.state == CircuitBreakerState.OPEN:
            if self._should_attempt_reset():
                self._transition_to_half_open()
            else:
                raise OFSConnectionException(
                    f"Circuit breaker '{self.config.name}' is OPEN",
                    error_code="CIRCUIT_BREAKER_OPEN"
                )
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.config.expected_exception as e:
            self._on_failure(e)
            raise
    
    async def _call_async(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection (async)."""
        if self.state == CircuitBreakerState.OPEN:
            if self._should_attempt_reset():
                self._transition_to_half_open()
            else:
                raise OFSConnectionException(
                    f"Circuit breaker '{self.config.name}' is OPEN",
                    error_code="CIRCUIT_BREAKER_OPEN"
                )
        
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except self.config.expected_exception as e:
            self._on_failure(e)
            raise
    
    def _should_attempt_reset(self) -> bool:
        """Check if circuit breaker should attempt to reset."""
        if self._last_failure_time is None:
            return False
        
        time_since_failure = datetime.now() - self._last_failure_time
        return time_since_failure.total_seconds() >= self.config.timeout_seconds
    
    def _transition_to_half_open(self):
        """Transition circuit breaker to half-open state."""
        self.state = CircuitBreakerState.HALF_OPEN
        self.stats.state_transitions.append(
            (datetime.now(), "HALF_OPEN")
        )
        logger.info(f"Circuit breaker '{self.config.name}' -> HALF_OPEN")
    
    def _on_success(self):
        """Handle successful function execution."""
        self.stats.success_count += 1
        self.stats.last_success_time = datetime.now()
        
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.state = CircuitBreakerState.CLOSED
            self.stats.failure_count = 0
            self.stats.state_transitions.append(
                (datetime.now(), "CLOSED")
            )
            logger.info(f"Circuit breaker '{self.config.name}' -> CLOSED")
    
    def _on_failure(self, exception: Exception):
        """Handle failed function execution."""
        self.stats.failure_count += 1
        self.stats.last_failure_time = datetime.now()
        self._last_failure_time = datetime.now()
        
        logger.warning(
            f"Circuit breaker '{self.config.name}' failure "
            f"({self.stats.failure_count}/{self.config.failure_threshold}): {exception}"
        )
        
        if (self.state in (CircuitBreakerState.CLOSED, CircuitBreakerState.HALF_OPEN) and
            self.stats.failure_count >= self.config.failure_threshold):
            self.state = CircuitBreakerState.OPEN
            self.stats.state_transitions.append(
                (datetime.now(), "OPEN")
            )
            logger.error(f"Circuit breaker '{self.config.name}' -> OPEN")
    
    def reset(self):
        """Manually reset circuit breaker to closed state."""
        self.state = CircuitBreakerState.CLOSED
        self.stats.failure_count = 0
        self._last_failure_time = None
        self.stats.state_transitions.append(
            (datetime.now(), "CLOSED (MANUAL_RESET)")
        )
        logger.info(f"Circuit breaker '{self.config.name}' manually reset")


class RetryHandler:
    """Handles retry logic with exponential backoff."""
    
    def __init__(self, config: RetryConfig):
        """Initialize retry handler.
        
        Args:
            config: Retry configuration
        """
        self.config = config
    
    def __call__(self, func: Callable) -> Callable:
        """Decorator to wrap functions with retry logic."""
        if asyncio.iscoroutinefunction(func):
            async def async_wrapper(*args, **kwargs):
                return await self._retry_async(func, *args, **kwargs)
            return async_wrapper
        else:
            def sync_wrapper(*args, **kwargs):
                return self._retry_sync(func, *args, **kwargs)
            return sync_wrapper
    
    def _retry_sync(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with retry logic (sync)."""
        last_exception = None
        
        for attempt in range(self.config.max_attempts):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                
                if not self._should_retry(e, attempt):
                    break
                
                if attempt < self.config.max_attempts - 1:  # Don't delay on final attempt
                    delay = self._calculate_delay(attempt, e)
                    logger.warning(
                        f"Attempt {attempt + 1}/{self.config.max_attempts} failed: {e}. "
                        f"Retrying in {delay:.2f}s"
                    )
                    time.sleep(delay)
        
        # All retry attempts failed
        logger.error(f"All {self.config.max_attempts} retry attempts failed")
        if last_exception:
            raise last_exception
    
    async def _retry_async(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with retry logic (async)."""
        last_exception = None
        
        for attempt in range(self.config.max_attempts):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                
                if not self._should_retry(e, attempt):
                    break
                
                if attempt < self.config.max_attempts - 1:  # Don't delay on final attempt
                    delay = self._calculate_delay(attempt, e)
                    logger.warning(
                        f"Attempt {attempt + 1}/{self.config.max_attempts} failed: {e}. "
                        f"Retrying in {delay:.2f}s"
                    )
                    await asyncio.sleep(delay)
        
        # All retry attempts failed
        logger.error(f"All {self.config.max_attempts} retry attempts failed")
        if last_exception:
            raise last_exception
    
    def _should_retry(self, exception: Exception, attempt: int) -> bool:
        """Determine if we should retry based on exception and attempt number."""
        if attempt >= self.config.max_attempts - 1:
            return False
        
        # Check if exception type is retryable
        if isinstance(exception, self.config.retry_on_exceptions):
            return True
        
        # Check if it's an OFSException with retryable status code
        if hasattr(exception, 'status_code') and exception.status_code:
            if exception.status_code in self.config.retry_on_status_codes:
                return True
        
        return False
    
    def _calculate_delay(self, attempt: int, exception: Exception) -> float:
        """Calculate delay for next retry attempt."""
        # Handle rate limiting with Retry-After header
        if isinstance(exception, OFSRateLimitException) and hasattr(exception, 'retry_after'):
            if exception.retry_after:
                return min(exception.retry_after, self.config.max_delay)
        
        # Exponential backoff
        delay = self.config.initial_delay * (self.config.exponential_base ** attempt)
        delay = min(delay, self.config.max_delay)
        
        # Add jitter to prevent thundering herd
        if self.config.jitter:
            jitter_range = delay * 0.1  # 10% jitter
            delay += random.uniform(-jitter_range, jitter_range)
        
        return max(0, delay)


def with_retry(config: Optional[RetryConfig] = None) -> Callable:
    """Decorator factory for adding retry logic to functions.
    
    Args:
        config: Optional retry configuration (uses defaults if not provided)
        
    Returns:
        Decorator function
    """
    if config is None:
        config = RetryConfig()
    
    return RetryHandler(config)


def with_circuit_breaker(config: Optional[CircuitBreakerConfig] = None) -> Callable:
    """Decorator factory for adding circuit breaker to functions.
    
    Args:
        config: Optional circuit breaker configuration (uses defaults if not provided)
        
    Returns:
        Decorator function
    """
    if config is None:
        config = CircuitBreakerConfig()
    
    return CircuitBreaker(config)


def with_fault_tolerance(
    retry_config: Optional[RetryConfig] = None,
    circuit_breaker_config: Optional[CircuitBreakerConfig] = None
) -> Callable:
    """Decorator factory combining retry logic and circuit breaker.
    
    Args:
        retry_config: Optional retry configuration
        circuit_breaker_config: Optional circuit breaker configuration
        
    Returns:
        Decorator function that applies both retry and circuit breaker
    """
    def decorator(func: Callable) -> Callable:
        # Apply circuit breaker first, then retry
        if circuit_breaker_config:
            func = with_circuit_breaker(circuit_breaker_config)(func)
        
        if retry_config:
            func = with_retry(retry_config)(func)
        
        return func
    
    return decorator