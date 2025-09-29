"""Capacity API models for OFSC Python Wrapper v3.0.

This module contains Pydantic models for OFSC Capacity API endpoints:
- Capacity areas and area configuration
- Capacity categories and category management
- Capacity metrics and responses
- Quota management and quota responses
- Time intervals and capacity calculations
- Booking options and booking management
"""

from typing import Any, Dict, List, Optional

from pydantic import (
    AnyHttpUrl,
    BaseModel,
    ConfigDict,
    Field,
    RootModel,
    field_validator,
)
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


class CapacityAreaLink(BaseOFSResponse):
    """Link reference for related capacity area resources"""

    href: AnyHttpUrl


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

    # Relationship links (only present in individual responses)
    workZones: Optional[CapacityAreaLink] = None
    organizations: Optional[CapacityAreaLink] = None
    capacityCategories: Optional[CapacityAreaLink] = None
    timeIntervals: Optional[CapacityAreaLink] = None
    timeSlots: Optional[CapacityAreaLink] = None


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

    def __len__(self):
        return len(self.root)


class CapacityCategoryResponse(BaseOFSResponse):
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


class CapacityCategoryRequest(BaseModel):
    """Request model for creating or updating capacity categories"""

    label: str
    name: str
    active: bool = True
    timeSlots: Optional[List[Dict[str, str]]] = None  # List of {"label": "value"}
    workSkills: Optional[List[Dict[str, Any]]] = (
        None  # List with label, ratio, startDate
    )
    workSkillGroups: Optional[List[Dict[str, str]]] = None
    translations: Optional[TranslationList] = None


class CapacityCategoryListResponse(OFSResponseList[CapacityCategoryResponse]):
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


# Capacity Area Sub-Resource Models
class CapacityAreaTimeInterval(BaseOFSResponse):
    """Time interval model for capacity area time intervals endpoint"""

    timeFrom: str
    timeTo: Optional[str] = None  # Some intervals only have timeFrom


class CapacityAreaTimeIntervalListResponse(OFSResponseList[CapacityAreaTimeInterval]):
    """Paginated response for capacity area time intervals"""

    pass


class CapacityAreaTimeSlot(BaseOFSResponse):
    """Time slot model for capacity area time slots endpoint"""

    label: str
    name: str
    timeFrom: str
    timeTo: str


class CapacityAreaTimeSlotListResponse(OFSResponseList[CapacityAreaTimeSlot]):
    """Paginated response for capacity area time slots"""

    pass


class CapacityAreaWorkzone(BaseOFSResponse):
    """Work zone model for capacity area work zones endpoint"""

    # For v2 endpoint (detailed)
    workZoneLabel: Optional[str] = None
    workZoneName: Optional[str] = None


class CapacityAreaWorkzoneListResponse(OFSResponseList[CapacityAreaWorkzone]):
    """Paginated response for capacity area work zones"""

    pass


class CapacityAreaCategory(BaseOFSResponse):
    """Capacity category model for capacity area categories endpoint"""

    label: str
    name: str
    status: Optional[str] = None  # active/inactive status


class CapacityAreaCategoryListResponse(OFSResponseList[CapacityAreaCategory]):
    """Paginated response for capacity area categories"""

    pass


class CapacityAreaOrganization(BaseOFSResponse):
    """Organization model for capacity area organizations endpoint"""

    label: str
    name: str
    type: str


class CapacityAreaOrganizationListResponse(OFSResponseList[CapacityAreaOrganization]):
    """Paginated response for capacity area organizations"""

    pass


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


# Booking-related models for Capacity API endpoints


class TimeSlotDictionary(BaseOFSResponse):
    """Time slot dictionary entry for booking options"""

    label: str = Field(description="The label of the timeslot")
    name: str = Field(description="The name of the timeslot")
    timeFrom: str = Field(description="The start time of the timeslot")
    timeTo: str = Field(description="The end time of the timeslot")


class BookingTimeSlot(BaseOFSResponse):
    """Time slot information for booking options"""

    label: Optional[str] = Field(None, description="The label of the time slot")
    reason: Optional[str] = Field(
        None, description="The reason the timeslot is not used for activity booking"
    )
    remainingQuota: Optional[int] = Field(
        None, description="The available quota after activity booking"
    )
    originalQuota: Optional[int] = Field(
        None, description="The minimum quota value defined on a time slot level"
    )


class BookingArea(BaseOFSResponse):
    """Booking area information for activity booking options"""

    label: str = Field(description="The label of the area")
    name: Optional[str] = Field(None, description="The name of the area")
    bucket: Optional[str] = Field(
        None, description="The external identifier of the bucket"
    )
    timeZone: Optional[str] = Field(None, description="The IANA name of the time zone")
    timeZoneDiff: Optional[int] = Field(
        None, description="The time zone difference in minutes"
    )
    categories: Optional[List[str]] = Field(
        None, description="The list of capacity categories matching the activity"
    )
    reason: Optional[str] = Field(
        None, description="The reason for the unavailability of booking options"
    )
    remainingQuota: Optional[int] = Field(
        None, description="The quota available on the day level after booking"
    )
    originalQuota: Optional[int] = Field(
        None, description="The quota value defined on a day level"
    )
    timeSlots: Optional[List[BookingTimeSlot]] = Field(
        None, description="The list of time slots at which the activity can be started"
    )


class BookingDate(BaseOFSResponse):
    """Booking date information for activity booking options"""

    date: str = Field(description="The date for booking options", format="date")
    areas: List[BookingArea] = Field(
        description="The array of available booking options within capacity areas"
    )


class ActivityBookingOptionsResponse(BaseOFSResponse):
    """Response model for activity booking options endpoint"""

    duration: Optional[int] = Field(
        None, description="The estimated duration of the activity in minutes"
    )
    travelTime: Optional[int] = Field(
        None, description="The average travel time (in minutes) to the activity"
    )
    categories: Optional[List[str]] = Field(
        None, description="The array of capacity categories returned for the activity"
    )
    timeSlotsDictionary: Optional[List[TimeSlotDictionary]] = Field(
        None, description="The dictionary of time slots"
    )
    workZone: Optional[str] = Field(
        None, description="The label of the work zone determined for the activity"
    )
    dates: List[BookingDate] = Field(
        description="The array of available booking options for each day"
    )


class BookingStatusState(BaseOFSResponse):
    """Booking status state information"""

    state: str = Field(
        description="The state of the booking status", pattern="^(open|closed)$"
    )
    scheduledCloseTime: Optional[str] = Field(
        None, description="The scheduled date and time when the booking closes"
    )
    closedAt: Optional[str] = Field(
        None, description="The date and time when the booking was closed"
    )


class BookingStatusItem(BaseOFSResponse):
    """Individual booking status item"""

    category: Optional[str] = Field(
        None, description="The label of the capacity category"
    )
    workZone: Optional[str] = Field(None, description="The label of the work zone")
    timeFrom: Optional[str] = Field(None, description="The start time in HH:MM format")
    timeTo: Optional[str] = Field(None, description="The end time in HH:MM format")
    bookingStatus: BookingStatusState = Field(
        description="The booking status information"
    )


class BookingStatus(BaseOFSResponse):
    """Booking status for a specific date and area"""

    date: str = Field(description="The date specified in the request", format="date")
    area: str = Field(
        description="The label of the capacity area", min_length=1, max_length=40
    )
    statuses: List[BookingStatusItem] = Field(description="Array of booking statuses")


class BookingStatusListResponse(OFSResponseList[BookingStatus]):
    """Response model for booking statuses endpoint"""

    pass


class BookingClosingSchedule(BaseOFSResponse):
    """Booking closing schedule configuration"""

    area: str = Field(
        description="The label of the area from which the booking is closed",
        min_length=1,
        max_length=40,
    )
    dayOffset: int = Field(
        description="The offset determines the day on which the booking is closed",
        ge=1,
        le=255,
    )
    category: Optional[str] = Field(
        None,
        description="The label of the capacity category for which the booking is closed",
    )
    workZone: Optional[str] = Field(
        None, description="The label of the work zone from which the booking is closed"
    )
    startTime: Optional[str] = Field(
        None, description="The start time of the booking closing schedule"
    )
    endTime: Optional[str] = Field(
        None, description="The end time of the booking closing schedule"
    )
    closeTime: Optional[str] = Field(
        None, description="The time at which the booking is closed"
    )


class BookingClosingScheduleListResponse(OFSResponseList[BookingClosingSchedule]):
    """Response model for booking closing schedule endpoint"""

    pass


# Quota v2 models (newer API version with enhanced structure)


class QuotaV2WorkZone(BaseOFSResponse):
    """Work zone quota status for v2 API"""

    label: str = Field(description="The label of a work zone")
    quotaIsClosed: Optional[bool] = Field(
        None, description="Indicates if the booking has been closed at this level"
    )
    quotaIsAutoClosed: Optional[bool] = Field(
        None, description="Indicates if the booking has been closed automatically"
    )
    quotaIsReopened: Optional[bool] = Field(
        None, description="Indicates if the booking has been manually reopened"
    )


class QuotaV2CategoryInterval(BaseOFSResponse):
    """Quota interval information within a category for v2 API"""

    timeFrom: str = Field(
        description="The start time of the time interval in HH:MM format"
    )
    timeTo: str = Field(description="The end time of the time interval in HH:MM format")
    quota: Optional[int] = Field(None, description="The quota value in minutes")
    used: Optional[int] = Field(
        None, description="The amount of consumed capacity in minutes"
    )
    quotaIsClosed: Optional[bool] = Field(
        None, description="Indicates if the booking has been closed"
    )
    quotaIsAutoClosed: Optional[bool] = Field(
        None, description="Indicates if automatically closed by schedule"
    )
    scheduledCloseTime: Optional[str] = Field(
        None, description="The scheduled date and time when booking closes"
    )
    closedAt: Optional[str] = Field(
        None, description="The date and time when booking was closed"
    )
    workZones: Optional[List[QuotaV2WorkZone]] = Field(
        None, description="Work zone quota statuses"
    )


class QuotaV2AreaCategory(BaseOFSResponse):
    """Capacity category quota information for area in v2 API"""

    label: str = Field(description="The label of the Capacity Category")
    maxAvailable: Optional[int] = Field(
        None, description="The total working time of the resources for the category"
    )
    maxAvailableByPlans: Optional[int] = Field(
        None, description="The total working time for the category based on plans"
    )
    quota: Optional[int] = Field(None, description="The quota value in minutes")
    quotaPercent: Optional[float] = Field(
        None, description="The quota value in percent"
    )
    quotaPercentDay: Optional[float] = Field(
        None, description="The quota value as a percent of daily quota"
    )
    quotaPercentCategory: Optional[float] = Field(
        None, description="The quota value as a percent of category quota"
    )
    minQuota: Optional[int] = Field(
        None, description="The minimal quota value in minutes"
    )
    used: Optional[int] = Field(
        None, description="The amount of consumed capacity in minutes"
    )
    usedQuotaPercent: Optional[float] = Field(
        None, description="The used quota as a percent"
    )
    bookedActivities: Optional[int] = Field(
        None, description="The number of booked activities"
    )
    quotaIsClosed: Optional[bool] = Field(
        None, description="Indicates if the booking has been closed"
    )
    quotaIsAutoClosed: Optional[bool] = Field(
        None, description="Indicates if automatically closed by schedule"
    )
    scheduledCloseTime: Optional[str] = Field(
        None, description="The scheduled date and time when booking closes"
    )
    closedAt: Optional[str] = Field(
        None, description="The date and time when booking was closed"
    )
    workZones: Optional[List[QuotaV2WorkZone]] = Field(
        None, description="Work zone quota statuses"
    )
    intervals: Optional[List[QuotaV2CategoryInterval]] = Field(
        None, description="Interval quota information"
    )


class QuotaV2TimeSlotCategory(BaseOFSResponse):
    """Category quota information within a time slot for v2 API"""

    label: str = Field(description="The label of the Capacity Category")
    maxAvailable: Optional[int] = Field(
        None, description="The total working time of the resources for the category"
    )
    quota: Optional[int] = Field(None, description="The quota value in minutes")
    quotaPercent: Optional[float] = Field(
        None, description="The quota value in percent"
    )
    quotaPercentDay: Optional[float] = Field(
        None, description="The quota value as a percent of daily quota"
    )
    quotaPercentCategory: Optional[float] = Field(
        None, description="The quota value as a percent of category quota"
    )
    minQuota: Optional[int] = Field(
        None, description="The minimal quota value in minutes"
    )
    used: Optional[int] = Field(
        None, description="The amount of consumed capacity in minutes"
    )
    usedQuotaPercent: Optional[float] = Field(
        None, description="The used quota as a percent"
    )
    bookedActivities: Optional[int] = Field(
        None, description="The number of booked activities"
    )
    quotaIsClosed: Optional[bool] = Field(
        None, description="Indicates if the booking has been closed"
    )
    quotaIsAutoClosed: Optional[bool] = Field(
        None, description="Indicates if automatically closed by schedule"
    )
    scheduledCloseTime: Optional[str] = Field(
        None, description="The scheduled date and time when booking closes"
    )
    closedAt: Optional[str] = Field(
        None, description="The date and time when booking was closed"
    )
    workZones: Optional[List[QuotaV2WorkZone]] = Field(
        None, description="Work zone quota statuses"
    )


class QuotaV2AreaTimeSlot(BaseOFSResponse):
    """Time slot quota information for area in v2 API"""

    label: str = Field(description="Label of the time slot")
    maxAvailable: Optional[int] = Field(
        None, description="The total working time of the resources"
    )
    otherActivities: Optional[int] = Field(
        None, description="Total travel time and duration of non-capacity activities"
    )
    quota: Optional[int] = Field(None, description="The quota value in minutes")
    quotaPercent: Optional[float] = Field(
        None, description="The quota value in percent"
    )
    quotaPercentDay: Optional[float] = Field(
        None, description="The quota value as a percent of daily quota"
    )
    minQuota: Optional[int] = Field(
        None, description="The minimal quota value in minutes"
    )
    used: Optional[int] = Field(
        None, description="The amount of consumed capacity in minutes"
    )
    usedQuotaPercent: Optional[float] = Field(
        None, description="The used quota as a percent"
    )
    bookedActivities: Optional[int] = Field(
        None, description="The number of booked activities"
    )
    quotaIsClosed: Optional[bool] = Field(
        None, description="Indicates if the booking has been closed"
    )
    quotaIsAutoClosed: Optional[bool] = Field(
        None, description="Indicates if automatically closed by schedule"
    )
    scheduledCloseTime: Optional[str] = Field(
        None, description="The scheduled date and time when booking closes"
    )
    closedAt: Optional[str] = Field(
        None, description="The date and time when booking was closed"
    )
    categories: Optional[List[QuotaV2TimeSlotCategory]] = Field(
        None, description="Category quota information"
    )


class QuotaV2AreaInterval(BaseOFSResponse):
    """Area interval quota information for v2 API"""

    timeFrom: str = Field(
        description="The start time of the time interval in HH:MM format"
    )
    timeTo: str = Field(description="The end time of the time interval in HH:MM format")
    quotaIsClosed: Optional[bool] = Field(
        None, description="Indicates if the booking has been closed"
    )
    quotaIsAutoClosed: Optional[bool] = Field(
        None, description="Indicates if automatically closed by schedule"
    )
    scheduledCloseTime: Optional[str] = Field(
        None, description="The scheduled date and time when booking closes"
    )
    closedAt: Optional[str] = Field(
        None, description="The date and time when booking was closed"
    )


class QuotaV2Area(BaseOFSResponse):
    """Capacity area quota information for v2 API"""

    label: Optional[str] = Field(
        None,
        description="The label of the Capacity Area (not returned for aggregated results)",
    )
    maxAvailable: Optional[int] = Field(
        None, description="The total working time of the resources"
    )
    maxAvailableByPlans: Optional[int] = Field(
        None, description="The total working time based on plans"
    )
    otherActivities: Optional[int] = Field(
        None, description="Total travel time and duration of non-capacity activities"
    )
    quota: Optional[int] = Field(None, description="The quota value in minutes")
    quotaPercent: Optional[float] = Field(
        None, description="The quota value in percent"
    )
    minQuota: Optional[int] = Field(
        None, description="The minimal quota value in minutes"
    )
    used: Optional[int] = Field(
        None, description="The amount of consumed capacity in minutes"
    )
    usedQuotaPercent: Optional[float] = Field(
        None, description="The used quota as a percent"
    )
    bookedActivities: Optional[int] = Field(
        None, description="The number of booked activities"
    )
    quotaIsClosed: Optional[bool] = Field(
        None, description="Indicates if the booking has been closed"
    )
    quotaIsAutoClosed: Optional[bool] = Field(
        None, description="Indicates if automatically closed by schedule"
    )
    scheduledCloseTime: Optional[str] = Field(
        None, description="The scheduled date and time when booking closes"
    )
    closedAt: Optional[str] = Field(
        None, description="The date and time when booking was closed"
    )
    intervals: Optional[List[QuotaV2AreaInterval]] = Field(
        None, description="Interval information"
    )
    categories: Optional[List[QuotaV2AreaCategory]] = Field(
        None, description="Category quota information"
    )
    timeSlots: Optional[List[QuotaV2AreaTimeSlot]] = Field(
        None, description="Time slot quota information"
    )


class QuotaV2ResponseItem(BaseOFSResponse):
    """Individual quota response item by date for v2 API"""

    date: str = Field(description="Date in the YYYY-MM-DD format", format="date")
    areas: List[QuotaV2Area] = Field(
        description="Array of quota information for each capacity area"
    )


class GetQuotaV2Response(BaseOFSResponse):
    """Response model for quota v2 endpoint"""

    items: List[QuotaV2ResponseItem] = Field(
        description="Array of quota information for each requested date"
    )
