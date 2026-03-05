"""Async version of OFSOauth2 API module."""

from urllib.parse import urljoin

import httpx

from ..exceptions import (
    OFSCAuthenticationError,
    OFSCAuthorizationError,
    OFSCConflictError,
    OFSCNetworkError,
    OFSCNotFoundError,
    OFSCRateLimitError,
    OFSCServerError,
    OFSCValidationError,
)
from ..models import OAuthTokenResponse, OFSConfig, OFSOAuthRequest


class AsyncOFSOauth2:
    """Async version of OFSOauth2 API module."""

    def __init__(self, config: OFSConfig, client: httpx.AsyncClient):
        self._config = config
        self._client = client

    @property
    def config(self) -> OFSConfig:
        return self._config

    @property
    def baseUrl(self) -> str:
        if self._config.baseURL is None:
            raise ValueError("Base URL is not configured")
        return self._config.baseURL

    @property
    def _auth_headers(self) -> dict:
        """Build Basic auth headers for token requests (always Basic, never Bearer)."""
        return {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": "Basic " + self._config.basicAuthString.decode("utf-8"),
        }

    def _handle_http_error(self, e: httpx.HTTPStatusError, context: str = "") -> None:
        """Convert httpx exceptions to OFSC exceptions with error details."""
        status = e.response.status_code
        try:
            error_data = e.response.json()
            detail = error_data.get("detail", e.response.text)
            error_type = error_data.get("type", "about:blank")
            title = error_data.get("title", "")
        except Exception:
            detail = e.response.text
            error_type = "about:blank"
            title = f"HTTP {status}"

        message = f"{context}: {detail}" if context else detail
        error_map = {
            401: OFSCAuthenticationError,
            403: OFSCAuthorizationError,
            404: OFSCNotFoundError,
            409: OFSCConflictError,
            429: OFSCRateLimitError,
        }
        if status in error_map:
            raise error_map[status](
                message,
                status_code=status,
                response=e.response,
                error_type=error_type,
                title=title,
                detail=detail,
            ) from e
        elif 400 <= status < 500:
            raise OFSCValidationError(
                message,
                status_code=status,
                response=e.response,
                error_type=error_type,
                title=title,
                detail=detail,
            ) from e
        else:
            raise OFSCServerError(
                message,
                status_code=status,
                response=e.response,
                error_type=error_type,
                title=title,
                detail=detail,
            ) from e

    async def get_token(self, request: OFSOAuthRequest = OFSOAuthRequest()) -> OAuthTokenResponse:
        """Get OAuth access token via v2 endpoint (AU002P).

        Args:
            request: Token request parameters (default: client_credentials grant)

        Returns:
            OAuthTokenResponse: Token response with access_token, token_type, expires_in

        Raises:
            OFSCAuthenticationError: If credentials are invalid (401)
            OFSCAuthorizationError: If client lacks permissions (403)
            OFSCValidationError: For invalid request parameters (400/422)
            OFSCNetworkError: For network/transport errors
        """
        url = urljoin(self.baseUrl, "/rest/oauthTokenService/v2/token")
        try:
            response = await self._client.post(
                url,
                headers=self._auth_headers,
                data=request.model_dump(exclude_none=True),
            )
            response.raise_for_status()
            return OAuthTokenResponse.model_validate(response.json())
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, "Failed to get token")
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e
