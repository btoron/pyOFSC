"""Capacity models for pyOFSC.

These models correspond to the Oracle Field Service Capacity API endpoints.
"""

from typing import Optional, Union

from pydantic import BaseModel, ConfigDict, field_validator

from ._base import CsvList


# region Capacity v1 - Available Capacity


class CapacityRequest(BaseModel):
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
            raise ValueError(f"Expected list[str], CsvList, str, dict with 'value' key, or None, got {type(v)}")

    def get_areas_list(self) -> list[str]:
        """Get areas as a list of strings"""
        return self.areas.to_list() if self.areas is not None else []

    def get_categories_list(self) -> list[str]:
        """Get categories as a list of strings"""
        return self.categories.to_list() if self.categories is not None else []

    def get_dates_list(self) -> list[str]:
        """Get dates as a list of strings"""
        return self.dates.to_list()

    def get_fields_list(self) -> list[str]:
        """Get fields as a list of strings"""
        return self.fields.to_list() if self.fields is not None else []


class CapacityMetrics(BaseModel):
    """Model for capacity metrics with count and optional minutes arrays"""

    count: list[int] = []
    minutes: Optional[list[int]] = None


class CapacityCategoryItem(BaseModel):
    """Model for capacity category items with metrics"""

    label: str
    calendar: CapacityMetrics
    available: Optional[CapacityMetrics] = None


class CapacityAreaResponseItem(BaseModel):
    """Model for capacity area response with proper nested structure"""

    label: str
    name: Optional[str] = None
    calendar: Optional[CapacityMetrics] = None
    available: Optional[CapacityMetrics] = None
    categories: list[CapacityCategoryItem] = []


class CapacityResponseItem(BaseModel):
    """Model for individual capacity response item by date"""

    date: str
    areas: list[CapacityAreaResponseItem] = []


class GetCapacityResponse(BaseModel):
    """Model for complete capacity response"""

    items: list[CapacityResponseItem] = []


# endregion


# region Capacity v2 - Quota


class QuotaTimeInterval(BaseModel):
    """Model for quota time interval data"""

    timeFrom: str
    timeTo: str
    quota: Optional[int] = None
    used: Optional[int] = None
    quotaIsClosed: Optional[bool] = None
    quotaIsAutoClosed: Optional[bool] = None
    model_config = ConfigDict(extra="allow")


class QuotaCategoryItem(BaseModel):
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
    intervals: list[QuotaTimeInterval] = []
    model_config = ConfigDict(extra="allow")


class QuotaAreaItem(BaseModel):
    """Model for quota area items with quota-specific fields"""

    label: Optional[str] = None
    name: Optional[str] = None
    maxAvailable: Optional[int] = None
    otherActivities: Optional[int] = None
    quota: Optional[int] = None
    quotaPercent: Optional[float] = None
    minQuota: Optional[int] = None
    used: Optional[int] = None
    usedQuotaPercent: Optional[float] = None
    bookedActivities: Optional[int] = None
    quotaIsClosed: Optional[bool] = None
    quotaIsAutoClosed: Optional[bool] = None
    intervals: list[QuotaTimeInterval] = []
    categories: list[QuotaCategoryItem] = []
    model_config = ConfigDict(extra="allow")


class QuotaResponseItem(BaseModel):
    """Model for individual quota response item by date"""

    date: str
    areas: list[QuotaAreaItem] = []


class GetQuotaResponse(BaseModel):
    """Model for complete quota response"""

    items: list[QuotaResponseItem] = []


class GetQuotaRequest(BaseModel):
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
            raise ValueError(f"Expected list[str], CsvList, str, dict with 'value' key, or None, got {type(v)}")

    def get_areas_list(self) -> list[str]:
        """Get areas as a list of strings"""
        return self.areas.to_list() if self.areas is not None else []

    def get_categories_list(self) -> list[str]:
        """Get categories as a list of strings"""
        return self.categories.to_list() if self.categories is not None else []

    def get_dates_list(self) -> list[str]:
        """Get dates as a list of strings"""
        return self.dates.to_list()


# Quota v2 Update models


class QuotaUpdateCategory(BaseModel):
    """Model for a quota category update item"""

    label: str
    quota: Optional[int] = None
    quotaIsClosed: Optional[bool] = None
    model_config = ConfigDict(extra="allow")


class QuotaUpdateArea(BaseModel):
    """Model for a quota area update item"""

    label: str
    quota: Optional[int] = None
    quotaIsClosed: Optional[bool] = None
    categories: list[QuotaUpdateCategory] = []
    model_config = ConfigDict(extra="allow")


class QuotaUpdateItem(BaseModel):
    """Model for a single date quota update"""

    date: str
    areas: list[QuotaUpdateArea] = []
    model_config = ConfigDict(extra="allow")


class QuotaUpdateRequest(BaseModel):
    """Request model for updating quota via PATCH /rest/ofscCapacity/v2/quota"""

    items: list[QuotaUpdateItem]
    model_config = ConfigDict(extra="allow")


class QuotaUpdateResponse(BaseModel):
    """Response model for quota update"""

    items: list[QuotaResponseItem] = []
    model_config = ConfigDict(extra="allow")


# endregion


# region Activity Booking Options


class BookingTimeSlot(BaseModel):
    """A booking time slot within a booking date/area"""

    timeSlotLabel: Optional[str] = None
    timeFrom: Optional[str] = None
    timeTo: Optional[str] = None
    available: Optional[bool] = None
    quota: Optional[int] = None
    used: Optional[int] = None
    model_config = ConfigDict(extra="allow")


class BookingArea(BaseModel):
    """A booking area within a booking date"""

    label: Optional[str] = None
    name: Optional[str] = None
    timeSlots: list[BookingTimeSlot] = []
    model_config = ConfigDict(extra="allow")


class BookingDate(BaseModel):
    """A booking date with areas and time slots"""

    date: Optional[str] = None
    areas: list[BookingArea] = []
    model_config = ConfigDict(extra="allow")


class ActivityBookingOptionsResponse(BaseModel):
    """Response model for GET /rest/ofscCapacity/v1/activityBookingOptions"""

    items: list[BookingDate] = []
    model_config = ConfigDict(extra="allow")


# endregion


# region Booking Closing Schedule


class BookingClosingScheduleItem(BaseModel):
    """A booking closing schedule item for an area"""

    areaLabel: Optional[str] = None
    date: Optional[str] = None
    closingTime: Optional[str] = None
    model_config = ConfigDict(extra="allow")


class BookingClosingScheduleResponse(BaseModel):
    """Response model for GET /rest/ofscCapacity/v1/bookingClosingSchedule"""

    items: list[BookingClosingScheduleItem] = []
    model_config = ConfigDict(extra="allow")


class BookingClosingScheduleUpdateRequest(BaseModel):
    """Request model for PATCH /rest/ofscCapacity/v1/bookingClosingSchedule"""

    items: list[BookingClosingScheduleItem]
    model_config = ConfigDict(extra="allow")


# endregion


# region Booking Statuses


class BookingStatusEntry(BaseModel):
    """A single booking status entry"""

    label: Optional[str] = None
    name: Optional[str] = None
    model_config = ConfigDict(extra="allow")


class BookingStatusItem(BaseModel):
    """A booking status item for an area/date"""

    areaLabel: Optional[str] = None
    date: Optional[str] = None
    status: Optional[str] = None
    statuses: list[BookingStatusEntry] = []
    model_config = ConfigDict(extra="allow")


class BookingStatusesResponse(BaseModel):
    """Response model for GET /rest/ofscCapacity/v1/bookingStatuses"""

    items: list[BookingStatusItem] = []
    model_config = ConfigDict(extra="allow")


class BookingStatusesUpdateRequest(BaseModel):
    """Request model for PATCH /rest/ofscCapacity/v1/bookingStatuses"""

    items: list[BookingStatusItem]
    model_config = ConfigDict(extra="allow")


# endregion


# region Show Booking Grid


class BookingGridActivity(BaseModel):
    """Activity data for show booking grid request"""

    activityType: Optional[str] = None
    duration: Optional[int] = None
    workSkills: Optional[list[str]] = None
    model_config = ConfigDict(extra="allow")


class BookingGridTimeSlot(BaseModel):
    """A time slot in the booking grid response"""

    timeSlotLabel: Optional[str] = None
    timeFrom: Optional[str] = None
    timeTo: Optional[str] = None
    available: Optional[bool] = None
    model_config = ConfigDict(extra="allow")


class BookingGridDateItem(BaseModel):
    """A date item in the booking grid response"""

    date: Optional[str] = None
    timeSlots: list[BookingGridTimeSlot] = []
    model_config = ConfigDict(extra="allow")


class BookingGridArea(BaseModel):
    """An area in the booking grid response"""

    label: Optional[str] = None
    name: Optional[str] = None
    dates: list[BookingGridDateItem] = []
    model_config = ConfigDict(extra="allow")


class ShowBookingGridRequest(BaseModel):
    """Request model for POST /rest/ofscCapacity/v1/showBookingGrid"""

    dates: Union[list[str], str]
    areas: Optional[Union[list[str], str]] = None
    activity: Optional[BookingGridActivity] = None
    model_config = ConfigDict(extra="allow")


class ShowBookingGridResponse(BaseModel):
    """Response model for POST /rest/ofscCapacity/v1/showBookingGrid"""

    items: list[BookingGridArea] = []
    model_config = ConfigDict(extra="allow")


# endregion


# region Booking Fields Dependencies


class BookingFieldDependency(BaseModel):
    """A booking field dependency definition"""

    fieldName: Optional[str] = None
    dependsOn: Optional[list[str]] = None
    model_config = ConfigDict(extra="allow")


class BookingFieldsDependenciesResponse(BaseModel):
    """Response model for GET /rest/ofscCapacity/v1/bookingFieldsDependencies"""

    items: list[BookingFieldDependency] = []
    model_config = ConfigDict(extra="allow")


# endregion
