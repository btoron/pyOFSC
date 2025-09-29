"""Tests for OFSC exception hierarchy and error handling."""

import json
import pytest
from unittest.mock import Mock

try:
    import httpx
except ImportError:
    httpx = None

from ofsc.exceptions import (
    OFSException,
    OFSAPIException,
    OFSAuthenticationException,
    OFSAuthorizationException,
    OFSValidationException,
    OFSConfigurationException,
    OFSConnectionException,
    OFSRateLimitException,
    OFSResourceNotFoundException,
    OFSServerException,
    OFSTimeoutException,
    create_exception_from_response,
    STATUS_CODE_EXCEPTIONS,
)


class TestOFSExceptionHierarchy:
    """Test the exception hierarchy structure and inheritance."""

    def test_base_exception_inheritance(self):
        """Test that all exceptions inherit from OFSException."""
        exception_classes = [
            OFSAPIException,
            OFSAuthenticationException,
            OFSAuthorizationException,
            OFSValidationException,
            OFSConfigurationException,
            OFSConnectionException,
            OFSRateLimitException,
            OFSResourceNotFoundException,
            OFSServerException,
            OFSTimeoutException,
        ]

        for exc_class in exception_classes:
            assert issubclass(exc_class, OFSException)
            print(f"✅ {exc_class.__name__} inherits from OFSException")

    def test_api_exception_inheritance(self):
        """Test that API-related exceptions inherit from OFSAPIException."""
        api_exception_classes = [
            OFSAuthenticationException,
            OFSAuthorizationException,
            OFSRateLimitException,
            OFSResourceNotFoundException,
            OFSServerException,
        ]

        for exc_class in api_exception_classes:
            assert issubclass(exc_class, OFSAPIException)
            print(f"✅ {exc_class.__name__} inherits from OFSAPIException")

    def test_connection_exception_inheritance(self):
        """Test that connection-related exceptions inherit correctly."""
        assert issubclass(OFSTimeoutException, OFSConnectionException)
        print("✅ OFSTimeoutException inherits from OFSConnectionException")


class TestOFSExceptionFeatures:
    """Test exception features and context handling."""

    def test_basic_exception_creation(self):
        """Test basic exception creation with message."""
        exc = OFSException("Test error message")

        assert str(exc) == "Test error message"
        assert exc.message == "Test error message"
        assert exc.status_code is None
        assert exc.error_code is None
        assert exc.request_details == {}

    def test_exception_with_context(self):
        """Test exception creation with full context."""
        request_details = {"url": "https://test.example.com", "method": "GET"}

        exc = OFSException(
            "API error occurred",
            status_code=400,
            error_code="INVALID_REQUEST",
            request_details=request_details,
        )

        assert exc.message == "API error occurred"
        assert exc.status_code == 400
        assert exc.error_code == "INVALID_REQUEST"
        assert exc.request_details == request_details

        # Test string representation includes context
        exc_str = str(exc)
        assert "API error occurred" in exc_str
        assert "(HTTP 400)" in exc_str
        assert "[INVALID_REQUEST]" in exc_str
        assert "https://test.example.com" in exc_str

    def test_exception_to_dict(self):
        """Test exception serialization to dictionary."""
        exc = OFSAPIException(
            "Test API error", status_code=500, error_code="INTERNAL_ERROR"
        )

        exc_dict = exc.to_dict()

        expected_keys = {
            "exception_type",
            "message",
            "status_code",
            "error_code",
            "request_details",
        }
        assert set(exc_dict.keys()) == expected_keys

        assert exc_dict["exception_type"] == "OFSAPIException"
        assert exc_dict["message"] == "Test API error"
        assert exc_dict["status_code"] == 500
        assert exc_dict["error_code"] == "INTERNAL_ERROR"

    def test_validation_exception_with_errors(self):
        """Test validation exception with validation error details."""
        validation_errors = [
            {"field": "name", "message": "Field required"},
            {"field": "email", "message": "Invalid email format"},
        ]

        exc = OFSValidationException(
            "Validation failed", validation_errors=validation_errors
        )

        assert exc.validation_errors == validation_errors
        assert len(exc.validation_errors) == 2

    def test_rate_limit_exception_with_retry_after(self):
        """Test rate limit exception with retry-after header."""
        exc = OFSRateLimitException(
            "Rate limit exceeded", status_code=429, retry_after=60
        )

        assert exc.retry_after == 60
        assert exc.status_code == 429


@pytest.mark.skipif(httpx is None, reason="httpx not available")
class TestExceptionFromResponse:
    """Test exception creation from HTTP responses."""

    def test_status_code_mapping(self):
        """Test that status codes map to correct exception types."""
        test_cases = [
            (400, OFSValidationException),
            (401, OFSAuthenticationException),
            (403, OFSAuthorizationException),
            (404, OFSResourceNotFoundException),
            (429, OFSRateLimitException),
            (500, OFSServerException),
            (502, OFSServerException),
            (503, OFSServerException),
            (504, OFSTimeoutException),
            (418, OFSAPIException),  # Unmapped status code
        ]

        for status_code, expected_exception_class in test_cases:
            response = Mock(spec=httpx.Response)
            response.status_code = status_code
            response.url = httpx.URL("https://test.example.com/api/test")
            response.request = Mock()
            response.request.method = "GET"
            response.content = b'{"error": "Test error"}'
            response.json.return_value = {"error": "Test error"}
            response.reason_phrase = "Test Error"
            response.headers = {}

            exc = create_exception_from_response(response)

            assert isinstance(exc, expected_exception_class)
            assert exc.status_code == status_code
            print(f"✅ Status {status_code} -> {expected_exception_class.__name__}")

    def test_response_with_json_error_details(self):
        """Test exception creation with JSON error details."""
        response = Mock(spec=httpx.Response)
        response.status_code = 400
        response.url = httpx.URL("https://test.example.com/api/test")
        response.request = Mock()
        response.request.method = "POST"
        response.content = b'{"message": "Invalid request", "code": "VALIDATION_ERROR", "details": "Name field is required"}'
        response.json.return_value = {
            "message": "Invalid request",
            "code": "VALIDATION_ERROR",
            "details": "Name field is required",
        }

        exc = create_exception_from_response(response)

        assert isinstance(exc, OFSValidationException)
        assert exc.message == "Invalid request"
        assert exc.error_code == "VALIDATION_ERROR"
        assert exc.details == "Name field is required"

    def test_response_with_invalid_json(self):
        """Test exception creation when response has invalid JSON."""
        response = Mock(spec=httpx.Response)
        response.status_code = 500
        response.url = httpx.URL("https://test.example.com/api/test")
        response.request = Mock()
        response.request.method = "GET"
        response.content = b"Invalid JSON content"
        response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        response.reason_phrase = "Internal Server Error"

        exc = create_exception_from_response(response)

        assert isinstance(exc, OFSServerException)
        assert "HTTP 500" in exc.message
        assert "Internal Server Error" in exc.message

    def test_rate_limit_response_with_retry_after(self):
        """Test rate limit exception with Retry-After header."""
        response = Mock(spec=httpx.Response)
        response.status_code = 429
        response.url = httpx.URL("https://test.example.com/api/test")
        response.request = Mock()
        response.request.method = "GET"
        response.content = b'{"message": "Rate limit exceeded"}'
        response.json.return_value = {"message": "Rate limit exceeded"}
        response.headers = {"Retry-After": "120"}

        exc = create_exception_from_response(response)

        assert isinstance(exc, OFSRateLimitException)
        assert exc.retry_after == 120

    def test_custom_error_message(self):
        """Test exception creation with custom message."""
        response = Mock(spec=httpx.Response)
        response.status_code = 404
        response.url = httpx.URL("https://test.example.com/api/resource/123")
        response.request = Mock()
        response.request.method = "GET"
        response.content = b""
        response.json.side_effect = json.JSONDecodeError("No JSON", "", 0)

        custom_message = "Resource with ID 123 not found"
        exc = create_exception_from_response(response, message=custom_message)

        assert isinstance(exc, OFSResourceNotFoundException)
        assert exc.message == custom_message


class TestStatusCodeMapping:
    """Test the status code to exception mapping."""

    def test_status_code_exceptions_completeness(self):
        """Test that STATUS_CODE_EXCEPTIONS covers expected codes."""
        expected_codes = {400, 401, 403, 404, 429, 500, 502, 503, 504}
        actual_codes = set(STATUS_CODE_EXCEPTIONS.keys())

        assert actual_codes == expected_codes
        print(f"✅ Status code mapping covers: {sorted(actual_codes)}")

    def test_status_code_exceptions_types(self):
        """Test that all mapped exceptions are OFSException subclasses."""
        for status_code, exception_class in STATUS_CODE_EXCEPTIONS.items():
            assert issubclass(exception_class, OFSException)
            print(f"✅ {status_code} -> {exception_class.__name__}")


class TestLegacyCompatibility:
    """Test backward compatibility features."""

    def test_legacy_alias(self):
        """Test that legacy OFSAPIError alias works."""
        from ofsc.exceptions import OFSAPIError

        # OFSAPIError should be an alias for OFSAPIException
        assert OFSAPIError is OFSAPIException

        # Should be able to create instances
        exc = OFSAPIError("Legacy error")
        assert isinstance(exc, OFSAPIException)
        assert isinstance(exc, OFSException)

    def test_kwargs_compatibility(self):
        """Test that old-style kwargs still work."""
        exc = OFSException("Test error", status=400, custom_field="test_value")

        # status should be mapped to status_code
        assert exc.status_code == 400

        # custom field should be set as attribute
        assert exc.custom_field == "test_value"
