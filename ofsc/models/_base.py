"""Base types and generic models for pyOFSC.

These symbols are extracted into their own module to break the circular
dependency that arises when domain sub-modules (e.g. users.py) need
OFSResponseList while __init__.py also imports from those sub-modules.
"""

import base64
import logging
from enum import Enum
from typing import Generic, Optional, TypeVar
from urllib.parse import urljoin

import requests
from cachetools import TTLCache, cached
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    RootModel,
    ValidationInfo,
    field_validator,
)
from typing_extensions import Annotated

from ..common import FULL_RESPONSE, wrap_return

# region Generic Models

T = TypeVar("T")


class CsvList(BaseModel):
    """Auxiliary model to represent a list of strings as comma-separated values"""

    value: str = ""

    @classmethod
    def from_list(cls, string_list: list[str]) -> "CsvList":
        """Create CsvList from a list of strings

        Args:
            string_list: List of strings to convert to CSV format

        Returns:
            CsvList instance with comma-separated values
        """
        if not string_list:
            return cls(value="")
        return cls(value=",".join(string_list))

    def to_list(self) -> list[str]:
        """Convert CsvList to a list of strings

        Returns:
            List of strings split by commas, empty list if value is empty
        """
        if not self.value or self.value.strip() == "":
            return []
        return [item.strip() for item in self.value.split(",") if item.strip()]

    def __str__(self) -> str:
        """String representation returns the CSV value"""
        return self.value

    def __repr__(self) -> str:
        """Representation shows both CSV and list format"""
        return f"CsvList(value='{self.value}', list={self.to_list()})"


class OFSResponseBoundedList(BaseModel, Generic[T]):
    model_config = ConfigDict(extra="allow")

    items: list[T] = []
    offset: Annotated[Optional[int], Field(alias="offset")] = None
    limit: Annotated[Optional[int], Field(alias="limit")] = None
    hasMore: Annotated[Optional[bool], Field(alias="hasMore")] = False

    def __len__(self):
        return len(self.items)

    def __iter__(self):  # type: ignore
        return iter(self.items)

    def __getitem__(self, item):
        return self.items[item]

    def __contains__(self, item):
        return item in self.items


class OFSResponseUnboundedList(BaseModel, Generic[T]):
    model_config = ConfigDict(extra="allow")

    items: list[T] = []
    offset: Annotated[Optional[int], Field(alias="offset")] = None
    limit: Annotated[Optional[int], Field(alias="limit")] = None
    totalResults: int = -1

    def __len__(self):
        return len(self.items)

    def __iter__(self):  # type: ignore
        return iter(self.items)

    def __getitem__(self, item):
        return self.items[item]

    def __contains__(self, item):
        return item in self.items


class OFSResponseList(BaseModel, Generic[T]):
    model_config = ConfigDict(extra="allow")

    items: list[T] = []
    offset: Annotated[Optional[int], Field(alias="offset")] = None
    limit: Annotated[Optional[int], Field(alias="limit")] = None
    hasMore: Annotated[Optional[bool], Field(alias="hasMore")] = False
    totalResults: int = -1

    # @model_validator(mode="after")
    # def check_coherence(self):
    #     if self.totalResults != len(self.items) and self.hasMore is False:
    #         self.totalResults = len(self.items)
    #     return self

    def __len__(self):
        return len(self.items)

    def __iter__(self):  # type: ignore
        return iter(self.items)

    def __getitem__(self, item):
        return self.items[item]

    def __contains__(self, item):
        return item in self.items


class OFSConfig(BaseModel):
    clientID: str
    secret: str
    companyName: str
    useToken: bool = False
    access_token: Optional[str] = None
    root: Optional[str] = None
    baseURL: Optional[str] = None
    auto_raise: bool = True
    auto_model: bool = True

    @property
    def basicAuthString(self):
        return base64.b64encode(bytes(self.clientID + "@" + self.companyName + ":" + self.secret, "utf-8"))

    model_config = ConfigDict(validate_assignment=True)

    @field_validator("baseURL")
    def set_base_URL(cls, url, info: ValidationInfo):
        if url:
            return url
        company_name = info.data.get("companyName")
        if company_name is None:
            return url
        return f"https://{company_name}.fs.ocs.oraclecloud.com"


class OFSOAuthRequest(BaseModel):
    model_config = ConfigDict(frozen=True)
    assertion: Optional[str] = None
    grant_type: str = "client_credentials"
    # ofs_dynamic_scope: Optional[str] = None


class OAuthTokenResponse(BaseModel):
    """Response from OFSC OAuth token endpoints (AU001P / AU002P)."""

    access_token: str
    token_type: str
    expires_in: int


class OFSAPIError(BaseModel):
    type: str
    title: str
    status: int
    detail: str


class OFSApi:
    def __init__(self, config: OFSConfig) -> None:
        self._config = config

    @property
    def config(self) -> OFSConfig:
        return self._config

    @property
    def baseUrl(self) -> str:
        """Return the base URL. The validator ensures this is never None."""
        return self._config.baseURL  # type: ignore[return-value]

    @cached(cache=TTLCache(maxsize=1, ttl=3000))  # Cache of token results for 50 minutes
    @wrap_return(response_type=FULL_RESPONSE, expected=[200])
    def token(self, auth: OFSOAuthRequest = OFSOAuthRequest()) -> requests.Response:
        headers = {}
        logging.info(f"Getting token with {auth.grant_type}")
        if auth.grant_type == "client_credentials" or auth.grant_type == "urn:ietf:params:oauth:grant-type:jwt-bearer":
            headers["Authorization"] = "Basic " + self._config.basicAuthString.decode("utf-8")
        else:
            raise NotImplementedError(f"grant_type {auth.grant_type} not implemented yet")
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        url = urljoin(self.baseUrl, "/rest/oauthTokenService/v2/token")
        response = requests.post(url, data=auth.model_dump(exclude_none=True), headers=headers)
        return response

    # Wrapper for requests not included in the standard methods
    def call(self, *, method: str, partialUrl: str, additionalHeaders: dict = {}, **kwargs) -> requests.Response:
        headers = self.headers | additionalHeaders
        url = urljoin(self.baseUrl, partialUrl)
        headers = self.headers
        response = requests.request(method, url, headers=headers, **kwargs)
        return response

    @property
    def headers(self):
        self._headers = {}
        self._headers["Content-Type"] = "application/json;charset=UTF-8"

        if not self._config.useToken:
            self._headers["Authorization"] = "Basic " + self._config.basicAuthString.decode("utf-8")
        else:
            self._token = self.token().json()["access_token"]
            self._headers["Authorization"] = f"Bearer {self._token}"
            print(f"Not implemented {self._token}")
        return self._headers


class SharingEnum(str, Enum):
    no_sharing = "no sharing"
    maximal = "maximal"
    minimal = "minimal"
    summary = "summary"


class EntityEnum(str, Enum):
    activity = "activity"
    inventory = "inventory"
    resource = "resource"
    service_request = "service request"
    user = "user"


class Status(str, Enum):
    """Base status enum for entities with active/inactive states."""

    active = "active"
    inactive = "inactive"


# class TranslationEnum(str, Enum):
#     en = "en"
#     es = "es"
#     pt = "pt"
#     fr = "fr"
#     br = "br"
#     el = "el"
#     cs = "cs"


# Work skills
class Translation(BaseModel):
    language: str = "en"
    name: str
    languageISO: Optional[str] = None


class TranslationList(RootModel[list[Translation]]):
    def __iter__(self):  # type: ignore[override]
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]

    def map(self):
        return {translation.language: translation for translation in self.root}


# endregion Generic Models
