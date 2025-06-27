"""Authentication and configuration models for OFSC Python Wrapper v3.0.

This module contains models related to:
- OFSC client configuration and credentials
- OAuth2 authentication requests and responses
- API error handling models
- Base API client infrastructure
"""

import base64
import logging
from typing import Optional
from urllib.parse import urljoin

import requests
from cachetools import TTLCache, cached
from pydantic import BaseModel, ConfigDict, ValidationInfo, field_validator

from ofsc.common import FULL_RESPONSE, wrap_return


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


class OFSApi:
    """Base API client class for legacy v2 authentication.
    
    Note: This will be replaced by the new v3.0 client architecture
    in ofsc.client.base.BaseOFSClient
    """
    
    def __init__(self, config: OFSConfig) -> None:
        self._config = config

    @property
    def config(self) -> OFSConfig:
        return self._config

    @cached(
        cache=TTLCache(maxsize=5, ttl=3300),
        key=lambda self, auth: f"{auth.grant_type}_{auth.assertion}",
    )
    def token(self, auth: OFSOAuthRequest = OFSOAuthRequest()) -> requests.Response:
        """Get OAuth2 token (legacy v2 implementation)"""
        headers = {
            "Authorization": "Basic " + self.config.basicAuthString.decode("utf-8"),
            "Content-Type": "application/x-www-form-urlencoded",
        }
        url = urljoin(self.config.baseURL, "rest/ofscCore/v1/token")
        data = auth.model_dump()
        return requests.post(url, data=data, headers=headers)

    @wrap_return(response_type=FULL_RESPONSE, expected=[200])
    def authorization_test(
        self, auth: OFSOAuthRequest = OFSOAuthRequest()
    ) -> requests.Response:
        """Test authorization credentials"""
        url = urljoin(self.config.baseURL, "rest/ofscCore/v1/authorize/test")
        headers = {
            "Authorization": "Bearer " + self.token(auth).json()["access_token"],
            "Content-Type": "application/json",
        }
        return requests.get(url, headers=headers)