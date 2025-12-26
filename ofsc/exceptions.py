from typing import Optional

import httpx


class OFSAPIException(Exception):
    def __init__(self, *args: object, **kwargs) -> None:
        super().__init__(*args)
        for key, value in kwargs.items():
            match key:
                case "status":
                    setattr(self, "status_code", int(value))
                case _:
                    setattr(self, key, value)


class OFSCApiError(OFSAPIException):
    """API-level errors (HTTP errors) with OFSC error details"""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response: Optional[httpx.Response] = None,
        error_type: Optional[str] = None,
        title: Optional[str] = None,
        detail: Optional[str] = None,
    ):
        super().__init__(message, status=status_code)
        self.response = response
        self.error_type = error_type
        self.title = title
        self.detail = detail


class OFSCAuthenticationError(OFSCApiError):
    """Authentication failed (401)"""

    pass


class OFSCAuthorizationError(OFSCApiError):
    """Authorization failed (403)"""

    pass


class OFSCNotFoundError(OFSCApiError):
    """Resource not found (404)"""

    pass


class OFSCConflictError(OFSCApiError):
    """Resource conflict (409)"""

    pass


class OFSCValidationError(OFSCApiError):
    """Validation error (400, 422)"""

    pass


class OFSCRateLimitError(OFSCApiError):
    """Rate limit exceeded (429)"""

    pass


class OFSCServerError(OFSCApiError):
    """Server error (5xx)"""

    pass


class OFSCNetworkError(OFSAPIException):
    """Network/transport errors"""

    pass
