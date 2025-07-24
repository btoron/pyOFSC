"""Base models and foundational classes for OFSC Python Wrapper v3.0.

This module contains the core model infrastructure used by all other model modules:
- Base response types and generic list handling
- Utility classes like CsvList for API parameter handling
- Common enums and translation support
- TypeVar definitions and base configurations
"""

from enum import Enum
from typing import TYPE_CHECKING, Dict, Generic, List, Optional, Type, TypeVar

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    PrivateAttr,
    RootModel,
    model_validator,
)
from typing_extensions import Annotated

if TYPE_CHECKING:
    import httpx

T = TypeVar("T")
TBaseOFSResponse = TypeVar("TBaseOFSResponse", bound="BaseOFSResponse")


class CsvList(BaseModel):
    """Auxiliary model to represent a list of strings as comma-separated values"""

    value: str = ""

    @classmethod
    def from_list(cls, string_list: List[str]) -> "CsvList":
        """Create CsvList from a list of strings

        Args:
            string_list: List of strings to convert to CSV format

        Returns:
            CsvList instance with comma-separated values
        """
        if not string_list:
            return cls(value="")
        return cls(value=",".join(string_list))

    def to_list(self) -> List[str]:
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


class Link(BaseModel):
    """Hyperlink reference for API resources"""

    rel: str
    href: str
    mediaType: Optional[str] = None


class BaseOFSResponse(BaseModel):
    """Base class for all OFSC API responses that provides raw response access.

    This class allows Pydantic models to store and access the raw httpx response
    object, enabling access to headers, status codes, and other HTTP metadata
    while still providing the convenience of validated model fields.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")

    _raw_response: Optional["httpx.Response"] = PrivateAttr(default=None)
    links: Optional[List[Link]] = None

    @property
    def raw_response(self) -> Optional["httpx.Response"]:
        """Access the raw httpx response object.

        Returns:
            The original httpx.Response object if available, None otherwise.
            Provides access to response.status_code, response.headers, etc.
        """
        return self._raw_response

    @classmethod
    def from_response(cls: Type[TBaseOFSResponse], response: "httpx.Response", **kwargs) -> TBaseOFSResponse:
        """Create model instance from httpx response.

        Args:
            response: The httpx.Response object to parse
            **kwargs: Additional arguments passed to model_validate

        Returns:
            An instance of the model with raw_response populated

        Raises:
            ValidationError: If the response JSON doesn't match the model schema
            OFSException: If the response indicates an HTTP error (4xx/5xx)
        """
        # Check for HTTP errors first - always raise exceptions (R7.3)
        if response.status_code >= 400:
            from ..exceptions import create_exception_from_response
            raise create_exception_from_response(response)
        
        # Remove metadata if present (API metadata, not model data)
        data = response.json()
        if isinstance(data, dict) and "_metadata" in data:
            data = {k: v for k, v in data.items() if k != "_metadata"}
        
        instance = cls.model_validate(data, **kwargs)
        instance._raw_response = response
        return instance

    @property
    def status_code(self) -> Optional[int]:
        """Convenience property to access response status code."""
        return self._raw_response.status_code if self._raw_response else None

    @property
    def headers(self) -> Optional[Dict[str, str]]:
        """Convenience property to access response headers."""
        return dict(self._raw_response.headers) if self._raw_response else None


class OFSResponseList(BaseOFSResponse, Generic[T]):
    """Generic response list model for paginated OFSC API responses.

    This class handles the standard OFSC list response format with pagination
    metadata and provides list-like access to the contained items. It is the
    standard pattern for all v3.0 API list responses, replacing the older
    RootModel[List[T]] pattern.

    Usage:
        - Used ONLY as return types from API methods that return lists
        - Never use as input parameters - use List[T] or specific request models instead
        - Provides automatic pagination metadata (offset, limit, hasMore, totalResults)
        - Supports iteration and indexing like a regular list via the 'items' field

    Example:
        class PropertyListResponse(OFSResponseList[Property]):
            pass
    """

    items: List[T] = []
    offset: Annotated[Optional[int], Field(alias="offset")] = None
    limit: Annotated[Optional[int], Field(alias="limit")] = None
    hasMore: Annotated[Optional[bool], Field(alias="hasMore")] = False
    totalResults: int = -1
    links: Optional[List[Link]] = None

    @model_validator(mode="after")
    def check_coherence(self):
        if self.totalResults != len(self.items) and self.hasMore is False:
            self.totalResults = len(self.items)
        return self

    def __len__(self):
        return len(self.items)

    def __iter__(self):
        return iter(self.items)

    def __getitem__(self, item):
        return self.items[item]

    def __contains__(self, item):
        return item in self.items

    def __next__(self):
        return next(self.items)


# Common Enums used across multiple model types
class SharingEnum(str, Enum):
    """Sharing level enumeration for work skills and other shared resources"""

    area = "area"
    category = "category"
    maximal = "maximal"
    no_sharing = "no sharing"
    private = "private"
    summary = "summary"


class EntityEnum(str, Enum):
    """Entity type enumeration for properties and other multi-entity models"""

    activity = "activity"
    inventory = "inventory"
    resource = "resource"
    service_request = "service request"
    user = "user"


# Translation support classes
class Translation(BaseModel):
    """Translation model for internationalized text content"""

    language: str = "en"
    name: str
    languageISO: Optional[str] = None


class TranslationList(RootModel[List[Translation]]):
    """List of translations with mapping utilities"""

    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]

    def __len__(self):
        return len(self.root)

    def map(self) -> Dict[str, Translation]:
        """Create a mapping of language codes to translation objects"""
        return {translation.language: translation for translation in self.root}
