"""Base models and foundational classes for OFSC Python Wrapper v3.0.

This module contains the core model infrastructure used by all other model modules:
- Base response types and generic list handling
- Utility classes like CsvList for API parameter handling  
- Common enums and translation support
- TypeVar definitions and base configurations
"""

from datetime import date
from enum import Enum
from typing import Any, Dict, Generic, List, Optional, TypeVar

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    RootModel,
    ValidationInfo,
    field_validator,
    model_validator,
)
from typing_extensions import Annotated

T = TypeVar("T")


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


class OFSResponseList(BaseModel, Generic[T]):
    """Generic response list model for paginated OFSC API responses.
    
    This class handles the standard OFSC list response format with pagination
    metadata and provides list-like access to the contained items.
    """
    model_config = ConfigDict(extra="allow")

    items: List[T] = []
    offset: Annotated[Optional[int], Field(alias="offset")] = None
    limit: Annotated[Optional[int], Field(alias="limit")] = None
    hasMore: Annotated[Optional[bool], Field(alias="hasMore")] = False
    totalResults: int = -1

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

    def map(self):
        """Create a mapping of language codes to translation objects"""
        return {translation.language: translation for translation in self.root}