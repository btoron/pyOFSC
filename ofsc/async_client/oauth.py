"""Async version of OFSOauth2 API module."""

from urllib.parse import urljoin

import httpx

from ..exceptions import OFSCNetworkError
from ._base import AsyncClientBase
from ..models import OAuthTokenResponse, OFSOAuthRequest


class AsyncOFSOauth2(AsyncClientBase):
    """Async version of OFSOauth2 API module."""

    @property
    def _auth_headers(self) -> dict:
        """Build Basic auth headers for token requests (always Basic, never Bearer)."""
        return {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": "Basic " + self._config.basicAuthString.decode("utf-8"),
        }

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
