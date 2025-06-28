"""Exception hierarchy for OFSC Python Wrapper v3.0.

This module provides a comprehensive typed exception hierarchy for different
error scenarios that can occur when interacting with OFSC APIs.

Requirements covered:
- R7.1: Typed exceptions for different error scenarios
- R7.2: Error context with status code and request details
- R7.3: Always raise exceptions on errors
"""

from typing import Optional, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    import httpx


class OFSException(Exception):
    """Base exception for all OFSC-related errors.
    
    This is the root exception that all other OFSC exceptions inherit from.
    It provides common error context and logging capabilities.
    """
    
    def __init__(
        self,
        message: str,
        *,
        status_code: Optional[int] = None,
        response: Optional['httpx.Response'] = None,
        request_details: Optional[Dict[str, Any]] = None,
        error_code: Optional[str] = None,
        **kwargs
    ) -> None:
        """Initialize OFSC exception with rich context.
        
        Args:
            message: Human-readable error message
            status_code: HTTP status code if applicable
            response: Raw httpx response object
            request_details: Dictionary with request context (URL, method, etc.)
            error_code: API-specific error code
            **kwargs: Additional context attributes
        """
        super().__init__(message)
        
        self.message = message
        self.status_code = status_code
        self.response = response
        self.request_details = request_details or {}
        self.error_code = error_code
        
        # Set additional attributes from kwargs
        for key, value in kwargs.items():
            if key == "status":
                self.status_code = int(value)
            else:
                setattr(self, key, value)
        
        # Extract additional context from response if available
        if response is not None:
            self.status_code = response.status_code
            self.request_details.update({
                'url': str(response.url),
                'method': response.request.method if response.request else None,
                'headers': dict(response.headers) if hasattr(response, 'headers') else None
            })
    
    def __str__(self) -> str:
        """Return formatted error message with context."""
        parts = [self.message]
        
        if self.status_code:
            parts.append(f"(HTTP {self.status_code})")
        
        if self.error_code:
            parts.append(f"[{self.error_code}]")
        
        if self.request_details.get('url'):
            parts.append(f"URL: {self.request_details['url']}")
        
        return " ".join(parts)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for logging/serialization."""
        return {
            'exception_type': self.__class__.__name__,
            'message': self.message,
            'status_code': self.status_code,
            'error_code': self.error_code,
            'request_details': self.request_details
        }


class OFSAPIException(OFSException):
    """Exception for API-related errors.
    
    Raised when the OFSC API returns an error response or when
    there are issues with API communication.
    """
    pass


class OFSAuthenticationException(OFSAPIException):
    """Exception for authentication-related errors.
    
    Raised when authentication fails, tokens are invalid,
    or authorization is denied.
    """
    pass


class OFSAuthorizationException(OFSAPIException):
    """Exception for authorization-related errors.
    
    Raised when the authenticated user doesn't have permission
    to access the requested resource.
    """
    pass


class OFSValidationException(OFSException):
    """Exception for data validation errors.
    
    Raised when request data or response data fails validation,
    including Pydantic model validation errors.
    """
    
    def __init__(
        self,
        message: str,
        *,
        validation_errors: Optional[list] = None,
        **kwargs
    ) -> None:
        super().__init__(message, **kwargs)
        self.validation_errors = validation_errors or []


class OFSConfigurationException(OFSException):
    """Exception for configuration-related errors.
    
    Raised when there are issues with client configuration,
    missing required parameters, or invalid settings.
    """
    pass


class OFSConnectionException(OFSException):
    """Exception for network/connection-related errors.
    
    Raised when there are network connectivity issues,
    timeouts, or other transport-level problems.
    """
    pass


class OFSRateLimitException(OFSAPIException):
    """Exception for rate limiting errors.
    
    Raised when API rate limits are exceeded.
    """
    
    def __init__(
        self,
        message: str,
        *,
        retry_after: Optional[int] = None,
        **kwargs
    ) -> None:
        super().__init__(message, **kwargs)
        self.retry_after = retry_after


class OFSResourceNotFoundException(OFSAPIException):
    """Exception for resource not found errors.
    
    Raised when a requested resource (activity, resource, etc.)
    is not found or doesn't exist.
    """
    pass


class OFSServerException(OFSAPIException):
    """Exception for server-side errors.
    
    Raised when the OFSC API encounters internal server errors
    or is temporarily unavailable.
    """
    pass


class OFSTimeoutException(OFSConnectionException):
    """Exception for request timeout errors.
    
    Raised when a request exceeds the configured timeout period.
    """
    pass


# Exception mapping for HTTP status codes
STATUS_CODE_EXCEPTIONS = {
    400: OFSValidationException,
    401: OFSAuthenticationException,
    403: OFSAuthorizationException,
    404: OFSResourceNotFoundException,
    429: OFSRateLimitException,
    500: OFSServerException,
    502: OFSServerException,
    503: OFSServerException,
    504: OFSTimeoutException
}


def create_exception_from_response(
    response: 'httpx.Response',
    message: Optional[str] = None
) -> OFSException:
    """Create appropriate exception from HTTP response.
    
    Args:
        response: The httpx response object
        message: Optional custom error message
        
    Returns:
        Appropriate OFSException subclass instance
    """
    status_code = response.status_code
    
    # Try to extract error details from response
    error_details = {}
    try:
        if response.content:
            data = response.json()
            if isinstance(data, dict):
                message = message or data.get('message', data.get('error', f'HTTP {status_code}'))
                error_details['error_code'] = data.get('code', data.get('errorCode'))
                error_details['details'] = data.get('details', data.get('errorDetails'))
    except Exception:
        # Fallback if response parsing fails
        pass
    
    if not message:
        message = f"HTTP {status_code}: {response.reason_phrase or 'Unknown error'}"
    
    # Select appropriate exception class
    exception_class = STATUS_CODE_EXCEPTIONS.get(status_code, OFSAPIException)
    
    # Add rate limit info for 429 errors
    if status_code == 429 and exception_class == OFSRateLimitException:
        retry_after = response.headers.get('Retry-After')
        if retry_after:
            try:
                error_details['retry_after'] = int(retry_after)
            except ValueError:
                pass
    
    return exception_class(
        message,
        status_code=status_code,
        response=response,
        **error_details
    )


# Legacy compatibility
OFSAPIError = OFSAPIException  # For backward compatibility