"""Authentication classes for OFSC v3.0 clients."""

import base64
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional

import httpx
from cachetools import TTLCache
from pydantic import BaseModel, ConfigDict

from .exceptions import OFSAuthenticationException, OFSConnectionException

logger = logging.getLogger(__name__)


class TokenExpiredError(OFSAuthenticationException):
    """Raised when OAuth2 token has expired."""

    pass


class BaseAuth(ABC):
    """Abstract base class for authentication methods."""

    @abstractmethod
    def get_headers(self) -> Dict[str, str]:
        """Get authentication headers for HTTP requests."""
        pass

    @abstractmethod
    def is_valid(self) -> bool:
        """Check if authentication is valid."""
        pass


class BasicAuth(BaseAuth):
    """Basic Authentication using client_id and client_secret."""

    def __init__(self, instance: str, client_id: str, client_secret: str):
        """Initialize Basic Auth.

        Args:
            instance: OFSC instance name
            client_id: Client ID for authentication
            client_secret: Client secret for authentication
        """
        self.instance = instance
        self.client_id = client_id
        self.client_secret = client_secret

        # Create the basic auth string
        auth_user = f"{client_id}@{instance}"
        credentials = f"{auth_user}:{client_secret}"
        self.auth_string = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")

    def get_headers(self) -> Dict[str, str]:
        """Get Basic Auth headers."""
        return {
            "Authorization": f"Basic {self.auth_string}",
            "Content-Type": "application/json",
        }

    def is_valid(self) -> bool:
        """Basic Auth is always valid if credentials are provided."""
        return bool(self.client_id and self.client_secret)


class OAuth2TokenResponse(BaseModel):
    """OAuth2 token response model."""

    access_token: str
    token_type: str = "Bearer"
    expires_in: Optional[int] = None
    refresh_token: Optional[str] = None
    scope: Optional[str] = None

    model_config = ConfigDict(extra="ignore")


class OAuth2Auth(BaseAuth):
    """OAuth2 Authentication with automatic token refresh."""

    def __init__(
        self,
        instance: str,
        client_id: str,
        client_secret: str,
        base_url: Optional[str] = None,
        client: Optional[httpx.Client] = None,
    ):
        """Initialize OAuth2 Auth.

        Args:
            instance: OFSC instance name
            client_id: Client ID for OAuth2
            client_secret: Client secret for OAuth2
            base_url: Custom base URL (auto-generated if not provided)
            client: httpx.Client instance (creates new if not provided)
        """
        self.instance = instance
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = base_url or f"https://{instance}.fs.ocs.oraclecloud.com"
        self._client = client or httpx.Client()
        self._owns_client = client is None

        # Token management
        self._token: Optional[OAuth2TokenResponse] = None
        self._token_expires_at: Optional[datetime] = None

        # Create cache for token storage (TTL of 50 minutes)
        self._token_cache = TTLCache(maxsize=1, ttl=3000)

    def __del__(self):
        """Cleanup resources."""
        if self._owns_client and self._client:
            self._client.close()

    def get_headers(self) -> Dict[str, str]:
        """Get OAuth2 headers with valid token."""
        token = self._get_valid_token()
        return {
            "Authorization": f"Bearer {token.access_token}",
            "Content-Type": "application/json",
        }

    def is_valid(self) -> bool:
        """Check if OAuth2 authentication is valid."""
        try:
            token = self._get_valid_token()
            return bool(token and token.access_token)
        except Exception:
            return False

    def _get_valid_token(self) -> OAuth2TokenResponse:
        """Get a valid OAuth2 token, refreshing if necessary."""
        # Check if we have a cached valid token
        if self._token and self._token_expires_at:
            # Add 5 minute buffer before expiration
            if datetime.now(timezone.utc) < (
                self._token_expires_at - timedelta(minutes=5)
            ):
                return self._token

        # Token expired or doesn't exist, get a new one
        logger.debug("Requesting new OAuth2 token")
        self._token = self._request_token()

        # Set expiration time
        if self._token.expires_in:
            self._token_expires_at = datetime.now(timezone.utc) + timedelta(
                seconds=self._token.expires_in
            )
        else:
            # Default to 1 hour if no expires_in provided
            self._token_expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

        return self._token

    def _request_token(self) -> OAuth2TokenResponse:
        """Request a new OAuth2 token from the server."""
        token_url = f"{self.base_url.rstrip('/')}/rest/oauthTokenService/v2/token"

        # Create Basic Auth for token request
        basic_auth_str = base64.b64encode(
            f"{self.client_id}@{self.instance}:{self.client_secret}".encode("utf-8")
        ).decode("utf-8")

        headers = {
            "Authorization": f"Basic {basic_auth_str}",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        data = {"grant_type": "client_credentials"}

        try:
            response = self._client.post(token_url, headers=headers, data=data)
            response.raise_for_status()

            token_data = response.json()
            logger.debug("Successfully obtained OAuth2 token")

            return OAuth2TokenResponse(**token_data)

        except httpx.HTTPStatusError as e:
            logger.error(
                f"OAuth2 token request failed: {e.response.status_code} - {e.response.text}"
            )
            raise OFSAuthenticationException(
                f"Failed to obtain OAuth2 token: {e.response.status_code}"
            )
        except Exception as e:
            logger.error(f"OAuth2 token request error: {e}")
            raise OFSConnectionException(f"OAuth2 token request failed: {e}")

    def get_token(self) -> OAuth2TokenResponse:
        """Get a valid OAuth2 token (simplified interface for compatibility).

        This method provides a simplified interface that's compatible with
        the legacy oauth.py implementation while using the modern token
        management system internally.

        Returns:
            OAuth2TokenResponse with access token and metadata
        """
        return self._get_valid_token()

    def refresh_token(self) -> OAuth2TokenResponse:
        """Manually refresh the OAuth2 token."""
        logger.info("Manually refreshing OAuth2 token")
        self._token = self._request_token()

        if self._token.expires_in:
            self._token_expires_at = datetime.now(timezone.utc) + timedelta(
                seconds=self._token.expires_in
            )
        else:
            self._token_expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

        return self._token

    def revoke_token(self):
        """Revoke the current OAuth2 token."""
        if self._token:
            # In a full implementation, we'd call the revoke endpoint
            # For now, just clear the local token
            self._token = None
            self._token_expires_at = None
            logger.info("OAuth2 token revoked")


def create_auth(
    instance: str,
    client_id: str,
    client_secret: str,
    use_oauth2: bool = False,
    base_url: Optional[str] = None,
    client: Optional[httpx.Client] = None,
) -> BaseAuth:
    """Factory function to create appropriate authentication.

    Args:
        instance: OFSC instance name
        client_id: Client ID for authentication
        client_secret: Client secret for authentication
        use_oauth2: Whether to use OAuth2 instead of Basic Auth
        base_url: Custom base URL (auto-generated if not provided)
        client: httpx.Client instance for OAuth2 (creates new if not provided)

    Returns:
        Appropriate authentication instance
    """
    if use_oauth2:
        return OAuth2Auth(
            instance=instance,
            client_id=client_id,
            client_secret=client_secret,
            base_url=base_url,
            client=client,
        )
    else:
        return BasicAuth(
            instance=instance, client_id=client_id, client_secret=client_secret
        )
