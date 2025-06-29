"""Capacity API models for OFSC Python Wrapper v3.0.

This module contains Pydantic models for OFSC Capacity API endpoints:
- Capacity areas and area configuration
- Capacity categories and category management
- Capacity metrics and responses
- Quota management and quota responses
- Time intervals and capacity calculations
"""

from typing import List, Optional

from pydantic import ConfigDict, Field, RootModel, field_validator
from typing_extensions import Annotated

from .base import BaseOFSResponse, CsvList, OFSResponseList, TranslationList


# Capacity Areas
class CapacityAreaParent(BaseOFSResponse):
    """Parent capacity area reference"""

    label: str
    name: Optional[str] = None


class CapacityAreaConfiguration(BaseOFSResponse):
    """Configuration settings for capacity areas"""

    isTimeSlotBase: bool
    byCapacityCategory: str
    byDay: str
    byTimeSlot: str
    isAllowCloseOnWorkzoneLevel: bool
    definitionLevel: List[str]


class CapacityArea(BaseOFSResponse):
    """Capacity area definition and configuration"""

    label: str
    name: Optional[str] = None
    type: Optional[str] = "area"
    status: Optional[str] = "active"
    configuration: Optional[CapacityAreaConfiguration] = None
    parentLabel: Optional[str] = None
    parent: Annotated[Optional[CapacityAreaParent], Field(alias="parent")] = None
    translations: Annotated[Optional[TranslationList], Field(alias="translations")] = (
        None
    )
    # Note: as of 24A the additional fields returned are just HREFs so we won't include them here


class CapacityAreaListResponse(OFSResponseList[CapacityArea]):
    """Paginated response for capacity area lists"""

    pass


# Capacity Categories
class Item(BaseOFSResponse):
    """Generic item model for capacity categories"""

    label: str
    name: Optional[str] = None
    last_updated_by: Optional[str] = None
    last_update_date: Optional[str] = None
    last_update_login: Optional[str] = None
    created_by: Optional[str] = None
    creation_date: Optional[str] = None
    ratio: Optional[float] = None
    startDate: Optional[str] = None


class ItemList(RootModel[List[Item]]):
    """List of generic items"""

    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]


class CapacityCategory(BaseOFSResponse):
    """Capacity category definition and configuration"""

    label: str
    name: str
    timeSlots: Optional[ItemList] = None
    translations: Annotated[Optional[TranslationList], Field(alias="translations")] = (
        None
    )
    workSkillGroups: Optional[ItemList] = None
    workSkills: Optional[ItemList] = None
    active: bool
    model_config = ConfigDict(extra="allow")


class CapacityCategoryListResponse(OFSResponseList[CapacityCategory]):
    """Paginated response for capacity category lists"""

    pass


# Capacity Request and Response Models
class CapacityRequest(BaseOFSResponse):
    """Request model for capacity queries with CsvList support for string arrays

    Accepts list[str], CsvList, or str for string array parameters but converts internally to CsvList
    """

    aggregateResults: Optional[bool] = None
    areas: Optional[CsvList] = None
    availableTimeIntervals: str = "all"
    calendarTimeIntervals: str = "all"
    categories: Optional[CsvList] = None
    dates: CsvList
    fields: Optional[CsvList] = None

    @field_validator("areas", "categories", "dates", "fields", mode="before")
    @classmethod
    def convert_to_csvlist(cls, v):
        """Convert list[str], CsvList, str, or dict to CsvList"""
        if v is None:
            return None
        elif isinstance(v, list):
            return CsvList.from_list(v)
        elif isinstance(v, CsvList):
            return v
        elif isinstance(v, str):
            # Handle string input as CSV
            return CsvList(value=v)
        elif isinstance(v, dict) and "value" in v:
            # Handle dict from JSON deserialization
            return CsvList(value=v["value"])
        else:
            raise ValueError(
                f"Expected list[str], CsvList, str, dict with 'value' key, or None, got {type(v)}"
            )

    def get_areas_list(self) -> List[str]:
        """Get areas as a list of strings"""
        return self.areas.to_list() if self.areas is not None else []

    def get_categories_list(self) -> List[str]:
        """Get categories as a list of strings"""
        return self.categories.to_list() if self.categories is not None else []

    def get_dates_list(self) -> List[str]:
        """Get dates as a list of strings"""
        return self.dates.to_list()

    def get_fields_list(self) -> List[str]:
        """Get fields as a list of strings"""
        return self.fields.to_list() if self.fields is not None else []


class CapacityMetrics(BaseOFSResponse):
    """Model for capacity metrics with count and optional minutes arrays"""

    count: List[int] = []
    minutes: Optional[List[int]] = None


class CapacityCategoryItem(BaseOFSResponse):
    """Model for capacity category items with metrics"""

    label: str
    calendar: CapacityMetrics
    available: Optional[CapacityMetrics] = None


class CapacityAreaResponseItem(BaseOFSResponse):
    """Model for capacity area response with proper nested structure"""

    label: str
    name: Optional[str] = None
    calendar: Optional[CapacityMetrics] = None
    available: Optional[CapacityMetrics] = None
    categories: List[CapacityCategoryItem] = []


class CapacityResponseItem(BaseOFSResponse):
    """Model for individual capacity response item by date"""

    date: str
    areas: List[CapacityAreaResponseItem] = []


class GetCapacityResponse(BaseOFSResponse):
    """Model for complete capacity response"""

    items: List[CapacityResponseItem] = []


# Quota Models
class QuotaTimeInterval(BaseOFSResponse):
    """Model for quota time interval data"""

    timeFrom: str
    timeTo: str
    quota: Optional[int] = None
    used: Optional[int] = None
    quotaIsClosed: Optional[bool] = None
    quotaIsAutoClosed: Optional[bool] = None
    model_config = ConfigDict(extra="allow")


class QuotaCategoryItem(BaseOFSResponse):
    """Model for quota category items with category-specific quota fields"""

    label: Optional[str] = None
    maxAvailable: Optional[int] = None
    quota: Optional[int] = None
    quotaPercentDay: Optional[float] = None
    quotaPercentCategory: Optional[float] = None
    minQuota: Optional[int] = None
    used: Optional[int] = None
    usedQuotaPercent: Optional[float] = None
    bookedActivities: Optional[int] = None
    quotaIsClosed: Optional[bool] = None
    quotaIsAutoClosed: Optional[bool] = None
    intervals: List[QuotaTimeInterval] = []
    model_config = ConfigDict(extra="allow")


class QuotaAreaItem(BaseOFSResponse):
    """Model for quota area items with quota-specific fields"""

    label: Optional[str] = None
    name: Optional[str] = None
    maxAvailable: Optional[int] = None
    otherActivities: Optional[int] = None
    quota: Optional[int] = None
    quotaPercent: Optional[float] = None  # Changed to float
    minQuota: Optional[int] = None
    used: Optional[int] = None
    usedQuotaPercent: Optional[float] = None  # Changed to float
    bookedActivities: Optional[int] = None
    quotaIsClosed: Optional[bool] = None  # Added
    quotaIsAutoClosed: Optional[bool] = None  # Added
    intervals: List[QuotaTimeInterval] = []  # Added
    categories: List[QuotaCategoryItem] = []  # Added
    model_config = ConfigDict(extra="allow")


class QuotaResponseItem(BaseOFSResponse):
    """Model for individual quota response item by date"""

    date: str
    areas: List[QuotaAreaItem] = []


class GetQuotaResponse(BaseOFSResponse):
    """Model for complete quota response"""

    items: List[QuotaResponseItem] = []


class GetQuotaRequest(BaseOFSResponse):
    """Request model for quota queries with comprehensive parameters

    Accepts list[str] or CsvList for string array parameters but converts internally to CsvList
    """

    aggregateResults: Optional[bool] = None
    areas: Optional[CsvList] = None
    categories: Optional[CsvList] = None
    categoryLevel: Optional[bool] = None
    dates: CsvList  # Required parameter
    intervalLevel: Optional[bool] = None
    returnStatuses: Optional[bool] = None
    timeSlotLevel: Optional[bool] = None

    @field_validator("areas", "categories", "dates", mode="before")
    @classmethod
    def convert_to_csvlist(cls, v):
        """Convert list[str], CsvList, str, or dict to CsvList"""
        if v is None:
            return None
        elif isinstance(v, list):
            return CsvList.from_list(v)
        elif isinstance(v, CsvList):
            return v
        elif isinstance(v, str):
            # Handle string input as CSV
            return CsvList(value=v)
        elif isinstance(v, dict) and "value" in v:
            # Handle dict from JSON deserialization
            return CsvList(value=v["value"])
        else:
            raise ValueError(
                f"Expected list[str], CsvList, str, dict with 'value' key, or None, got {type(v)}"
            )

    def get_areas_list(self) -> List[str]:
        """Get areas as a list of strings"""
        return self.areas.to_list() if self.areas is not None else []

    def get_categories_list(self) -> List[str]:
        """Get categories as a list of strings"""
        return self.categories.to_list() if self.categories is not None else []

    def get_dates_list(self) -> List[str]:
        """Get dates as a list of strings"""
        return self.dates.to_list()
