"""Authentication and configuration models for OFSC Python Wrapper v3.0.

This module contains models related to:
- OFSC client configuration and credentials
- OAuth2 authentication requests and responses
- API error handling models
- Base API client infrastructure
"""

import base64
from abc import ABC
from typing import Optional

from pydantic import BaseModel, ConfigDict, ValidationInfo, field_validator


class OFSConfig(BaseModel):
    """Configuration model for OFSC client credentials and settings.
    
    Note: This is the legacy v2 configuration model. For v3.0, this will be
    replaced with the new configuration system in client/base.py
    """
    clientID: str
    secret: str
    companyName: str
    useToken: bool = False
    root: Optional[str] = None
    baseURL: Optional[str] = None
    auto_raise: bool = True
    auto_model: bool = True

    @property
    def basicAuthString(self):
        """Generate Basic Auth string for HTTP headers"""
        return base64.b64encode(
            bytes(self.clientID + "@" + self.companyName + ":" + self.secret, "utf-8")
        )

    model_config = ConfigDict(validate_assignment=True)

    @field_validator("baseURL")
    def set_base_URL(cls, url, info: ValidationInfo):
        """Auto-generate base URL from company name if not provided"""
        return url or f"https://{info.data['companyName']}.fs.ocs.oraclecloud.com"


class OFSOAuthRequest(BaseModel):
    """OAuth2 authentication request model"""
    assertion: Optional[str] = None
    grant_type: str = "client_credentials"
    # ofs_dynamic_scope: Optional[str] = None


class OFSAPIError(BaseModel):
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
        """Get headers for API requests.
        
        Default implementation for backward compatibility.
        Subclasses can override this for custom behavior.
        """
        _headers = {}
        _headers["Content-Type"] = "application/json;charset=UTF-8"

        if not self._config.useToken:
            _headers["Authorization"] = (
                "Basic " + self._config.basicAuthString.decode("utf-8")
            )
        else:
            # Token-based auth would require actual HTTP implementation
            raise NotImplementedError(
                "Token-based authentication requires HTTP functionality. "
                "This will be implemented in Phase 1.6 with httpx migration."
            )
        return _headers