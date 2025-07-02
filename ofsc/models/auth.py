"""Authentication and configuration models for OFSC Python Wrapper v3.0.

This module contains models related to:
- OFSC client configuration and credentials
- OAuth2 authentication requests and responses
- API error handling models
- Base API client infrastructure
"""

import base64
from abc import ABC
from typing import Optional, TYPE_CHECKING

from pydantic import ConfigDict, ValidationInfo, field_validator

from .base import BaseOFSResponse

if TYPE_CHECKING:
    from ..auth import BaseAuth, BasicAuth, OAuth2Auth  # noqa: F401


class OFSConfig(BaseOFSResponse):
    """Configuration model for OFSC client credentials and settings.
    
    Enhanced to internally manage auth objects for backward compatibility
    while using the modern authentication system.
    """
    clientID: str
    secret: str
    companyName: str
    useToken: bool = False
    root: Optional[str] = None
    baseURL: Optional[str] = None
    auto_raise: bool = True
    auto_model: bool = True
    
    # Private field to cache auth instance
    _auth_instance: Optional['BaseAuth'] = None

    @property
    def basicAuthString(self) -> bytes:
        """Generate Basic Auth string for HTTP headers (legacy compatibility)"""
        return base64.b64encode(
            bytes(self.clientID + "@" + self.companyName + ":" + self.secret, "utf-8")
        )

    model_config = ConfigDict(validate_assignment=True, arbitrary_types_allowed=True)

    @field_validator("baseURL")
    @classmethod
    def set_base_URL(cls, url, info: ValidationInfo) -> str:
        """Auto-generate base URL from company name if not provided"""
        return url or f"https://{info.data['companyName']}.fs.ocs.oraclecloud.com"
    
    def _get_auth_instance(self) -> 'BaseAuth':
        """Get or create appropriate auth instance based on configuration."""
        if self._auth_instance is None:
            # Import here to avoid circular imports
            from ..auth import BasicAuth, OAuth2Auth
            
            if self.useToken:
                self._auth_instance = OAuth2Auth(
                    instance=self.companyName,
                    client_id=self.clientID,
                    client_secret=self.secret,
                    base_url=self.baseURL
                )
            else:
                self._auth_instance = BasicAuth(
                    instance=self.companyName,
                    client_id=self.clientID,
                    client_secret=self.secret
                )
        
        return self._auth_instance
    
    def get_auth_headers(self) -> dict:
        """Get authentication headers using modern auth system."""
        return self._get_auth_instance().get_headers()


class OFSOAuthRequest(BaseOFSResponse):
    """OAuth2 authentication request model"""
    assertion: Optional[str] = None
    grant_type: str = "client_credentials"
    # ofs_dynamic_scope: Optional[str] = None


class OFSAPIError(BaseOFSResponse):
    """Model for OFSC API error responses"""
    type: str
    title: str
    status: int
    detail: str


class OFSApi(ABC):
    """Abstract base API client class for OFSC v2 compatibility.
    
    This abstract class defines the interface that all OFSC API clients
    must implement. It provides common configuration and base URL handling.
    
    Note: For v3.0, this will be replaced by the new client architecture
    in ofsc.client.base.BaseOFSClient
    """
    
    def __init__(self, config: OFSConfig) -> None:
        self._config = config

    @property
    def config(self) -> OFSConfig:
        """Get the configuration object."""
        return self._config
    
    @property
    def baseUrl(self) -> Optional[str]:
        """Get the base URL for API requests."""
        return self._config.baseURL
    
    @property
    def headers(self) -> dict:
        """Get headers for API requests using modern auth system.
        
        Now uses the internal auth objects managed by OFSConfig
        for both Basic Auth and OAuth2 authentication.
        """
        return self._config.get_auth_headers()