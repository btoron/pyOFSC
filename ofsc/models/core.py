"""Core API models for OFSC Python Wrapper v3.0.

This module contains Pydantic models for OFSC Core API endpoints:
- Resources and resource management
- Activities and activity operations
- Bulk update operations and responses
- User management and authentication
- Locations and geographical data
- Daily extracts and file operations
- Calendar and scheduling models
"""

from datetime import date
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import (
    AliasChoices,
    AnyHttpUrl,
    BaseModel,
    ConfigDict,
    Field,
    RootModel,
    model_validator,
)

from .base import BaseOFSResponse, OFSResponseList, Link as BaseLink


# Resources
class Resource(BaseOFSResponse):
    """Resource definition and configuration"""

    resourceId: Optional[str] = None
    parentResourceId: Optional[str] = None
    resourceInternalId: Optional[int] = None
    resourceType: str
    name: str
    status: str = "active"
    organization: str = "default"
    language: str
    languageISO: Optional[str] = None
    timeZone: str
    timeZoneIANA: Optional[str] = None
    timeZoneDiff: Optional[int] = None
    timeFormat: str = "24-hour"
    dateFormat: str = "mm/dd/yy"
    email: Optional[str] = None
    phone: Optional[str] = None
    durationStatisticsInitialRatio: Optional[float] = None
    # Related resource links
    inventories: Optional[Dict[str, Any]] = None
    users: Optional[Dict[str, Any]] = None
    workZones: Optional[Dict[str, Any]] = None
    workSkills: Optional[Dict[str, Any]] = None
    model_config = ConfigDict(extra="allow")


class ResourceListResponse(OFSResponseList[Resource]):
    """Paginated response for resource lists"""

    pass


# Activities
class Activity(BaseOFSResponse):
    """Activity definition and configuration"""

    activityId: Optional[int] = None
    activityType: Optional[str] = None
    date: Optional[str] = None
    model_config = ConfigDict(extra="allow")


class GetActivityRequest(BaseOFSResponse):
    """Request model for activity queries"""

    dateFrom: Optional[date] = None
    dateTo: Optional[date] = None
    fields: Optional[list[str]] = None
    includeChildren: Optional[str] = "all"
    offset: Optional[int] = 0
    includeNonScheduled: Optional[bool] = False
    limit: Optional[int] = 5000
    q: Optional[str] = None
    model_config = ConfigDict(extra="allow")
    resources: list[str]

    @model_validator(mode="after")
    def check_date_range(self):
        if self.dateFrom and self.dateTo and self.dateFrom > self.dateTo:
            raise ValueError("dateFrom must be before dateTo")
        if not self.includeNonScheduled:
            if self.dateFrom is None or self.dateTo is None:
                raise ValueError(
                    "dateFrom and dateTo are required when includeNonScheduled is False"
                )
        return self


class BulkUpdateActivityItem(BaseOFSResponse):
    """Activity item for bulk update operations"""

    activityId: Optional[int] = None
    activityType: Optional[str] = None
    date: Optional[str] = None
    # Include common activity fields for bulk operations
    status: Optional[str] = None
    resourceId: Optional[str] = None
    customerId: Optional[str] = None
    customerNumber: Optional[str] = None
    model_config = ConfigDict(extra="allow")


# Bulk Update Operations
class BulkUpdateParameters(BaseOFSResponse):
    """Parameters for bulk update operations"""

    fallbackResource: Optional[str] = None
    identifyActivityBy: Optional[str] = None
    ifExistsThenDoNotUpdateFields: Optional[List[str]] = None
    ifInFinalStatusThen: Optional[str] = None
    inventoryPropertiesUpdateMode: Optional[str] = None


class BulkUpdateRequest(BaseOFSResponse):
    """Request model for bulk update operations"""

    activities: List[BulkUpdateActivityItem]
    updateParameters: BulkUpdateParameters


class ActivityKeys(BaseOFSResponse):
    """Activity key identifiers"""

    activityId: Optional[int] = None
    apptNumber: Optional[str] = None
    customerNumber: Optional[str] = None


class ActivityListResponse(OFSResponseList[Activity]):
    """Paginated response for activity lists"""

    pass


class BulkUpdateError(BaseOFSResponse):
    """Error information for bulk update operations"""

    errorDetail: Optional[str] = None
    operation: Optional[str] = None


class BulkUpdateWarning(BaseOFSResponse):
    """Warning information for bulk update operations"""

    code: Optional[int] = None
    message: Optional[int] = None


class BulkUpdateResult(BaseOFSResponse):
    """Result of bulk update operations"""

    activityKeys: Optional[ActivityKeys] = None
    errors: Optional[List[BulkUpdateError]] = None
    operationsFailed: Optional[List[str]] = None
    operationsPerformed: Optional[List[str]] = None
    warnings: Optional[List[BulkUpdateWarning]] = None


class BulkUpdateResponse(BaseOFSResponse):
    """Response for bulk update operations"""

    results: Optional[List[BulkUpdateResult]] = None


# Users
class User(BaseOFSResponse):
    """User definition and configuration"""

    login: str
    status: Optional[str] = "active"
    language: Optional[str] = None
    languageISO: Optional[str] = None
    timeFormat: Optional[str] = "24-hour"
    dateFormat: Optional[str] = "mm/dd/yy"
    longDateFormat: Optional[str] = None
    timeZoneDiff: Optional[int] = None
    timeZone: Optional[str] = None
    timeZoneIANA: Optional[str] = None
    createdTime: Optional[str] = None
    lastLoginTime: Optional[str] = None
    lastPasswordChangeTime: Optional[str] = None
    organizationalUnit: Optional[str] = None
    lastUpdatedTime: Optional[str] = None
    weekStart: Optional[str] = "default"
    userType: Optional[str] = None
    model_config = ConfigDict(extra="allow")


class BaseUser(BaseOFSResponse):
    """Base user model for simple use cases"""

    login: str


class ResourceUsersListResponse(OFSResponseList[BaseUser]):
    """Response for resource user lists"""

    @property
    def users(self) -> List[str]:
        return [item.login for item in self.items]


class ResourcePosition(BaseOFSResponse):
    """Resource position information"""

    resourceId: str
    errorMessage: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    lastUpdated: Optional[str] = None
    accuracy: Optional[float] = None
    model_config = ConfigDict(extra="allow")


class ResourcePositionListResponse(OFSResponseList[ResourcePosition]):
    """Response for resource position lists"""

    pass


# Calendar and Scheduling
class RecurrenceType(str, Enum):
    """Recurrence type enumeration for calendar events"""

    daily = "daily"
    weekly = "weekly"
    everyday = "everyday"
    yearly = "yearly"


class WeekDay(str, Enum):
    """Week day enumeration"""

    Sunday = "Sun"
    Monday = "Mon"
    Tuesday = "Tue"
    Wednesday = "Wed"
    Thursday = "Thu"
    Friday = "Fri"
    Saturday = "Sat"


class Recurrence(BaseOFSResponse):
    """Recurrence configuration for calendar events"""

    dayFrom: Optional[date] = None
    dayTo: Optional[date] = None
    recurEvery: int = Field(ge=1, le=255)
    recurrenceType: RecurrenceType
    weekDays: Optional[List[str]] = None

    @model_validator(mode="after")
    def check_week_days(cls, values):
        if values.recurrenceType == RecurrenceType.weekly and not values.weekDays:
            raise ValueError("weekDays is required for weekly recurrence")
        if values.recurrenceType == RecurrenceType.yearly and not values.dayFrom:
            raise ValueError("dayFrom is required for yearly recurrence")
        if values.recurrenceType == RecurrenceType.yearly and not values.dayTo:
            raise ValueError("dayTo is required for yearly recurrence")
        return values


class CalendarViewItemRecordType(str, Enum):
    """Calendar view item record type enumeration"""

    schedule = "schedule"
    shift = "shift"
    extra_shift = "extra_shift"
    working = "working"
    extra_working = "extra_working"
    non_working = "non-working"
    error = "error"


class CalendarViewItem(BaseOFSResponse):
    """Calendar view item configuration"""

    comments: Optional[str] = None
    nonWorkingReason: Optional[str] = None
    points: Optional[int] = None
    recordType: CalendarViewItemRecordType
    scheduleLabel: Optional[str] = None
    shiftLabel: Optional[str] = None
    workTimeEnd: Optional[str] = None
    workTimeStart: Optional[str] = None


class CalendarViewList(RootModel[List[CalendarViewItem]]):
    """List of calendar view items"""

    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]


class CalendarViewShift(BaseOFSResponse):
    """Calendar view shift configuration"""

    regular: Optional[CalendarViewItem] = Field(default=None)
    on_call: Optional[CalendarViewItem] = Field(
        default=None, validation_alias=AliasChoices("onCall", "on-call")
    )


class CalendarView(RootModel[Dict[str, CalendarViewShift]]):
    """Calendar view with shift assignments"""

    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]


# Resource Work Schedule
class ResourceWorkScheduleItem(BaseOFSResponse):
    """Resource work schedule item configuration"""

    comments: Optional[str] = None
    endDate: Optional[date] = None
    isWorking: Optional[bool] = None
    nonWorkingReason: Optional[str] = None
    points: Optional[int] = None
    recordType: CalendarViewItemRecordType
    recurrence: Optional[Recurrence] = None
    scheduleItemId: Optional[int] = None
    scheduleLabel: Optional[str] = None
    scheduleShifts: Optional[List[CalendarViewItem]] = None
    shiftLabel: Optional[str] = None
    shiftType: Optional[str] = None
    startDate: Optional[date] = date.today()
    workTimeEnd: Optional[str] = None
    workTimeStart: Optional[str] = None


class ResourceWorkScheduleResponse(OFSResponseList[ResourceWorkScheduleItem]):
    """Paginated response for resource work schedules"""

    pass


# Locations
class Location(BaseOFSResponse):
    """Location definition and configuration"""

    label: str
    postalCode: Optional[str] = ""
    city: Optional[str] = ""
    state: Optional[str] = ""
    address: Optional[str] = ""
    longitude: Optional[float] = None
    latitude: Optional[float] = None
    country: str = "US"
    locationId: Optional[int] = None
    status: Optional[str] = None


class AssignedLocation(BaseOFSResponse):
    """Assigned location configuration"""

    start: Optional[int] = None
    end: Optional[int] = None
    homeZoneCenter: Optional[int] = None


class AssignedLocationsRequest(BaseModel):
    """Request model for setting assigned locations by day of week"""

    mon: Optional[AssignedLocation] = None
    tue: Optional[AssignedLocation] = None
    wed: Optional[AssignedLocation] = None
    thu: Optional[AssignedLocation] = None
    fri: Optional[AssignedLocation] = None
    sat: Optional[AssignedLocation] = None
    sun: Optional[AssignedLocation] = None
    model_config = ConfigDict(extra="allow")


class AssignedLocationsResponse(BaseOFSResponse):
    """Response for assigned locations by day of week"""

    mon: Optional[AssignedLocation] = None
    tue: Optional[AssignedLocation] = None
    wed: Optional[AssignedLocation] = None
    thu: Optional[AssignedLocation] = None
    fri: Optional[AssignedLocation] = None
    sat: Optional[AssignedLocation] = None
    sun: Optional[AssignedLocation] = None
    model_config = ConfigDict(extra="allow")


class LocationListResponse(OFSResponseList[Location]):
    """Paginated response for location lists"""

    pass


# Daily Extracts
class Link(BaseOFSResponse):
    """Link model for daily extract files"""

    href: AnyHttpUrl
    rel: str
    mediaType: Optional[str] = None


class DailyExtractItem(BaseOFSResponse):
    """Daily extract item configuration"""

    name: str
    bytes: Optional[int] = None
    mediaType: Optional[str] = None
    links: list[BaseLink]


class DailyExtractItemList(BaseOFSResponse):
    """List of daily extract items"""

    items: list[DailyExtractItem] = []


class DailyExtractFolders(BaseOFSResponse):
    """Daily extract folders configuration"""

    name: str = "folders"
    folders: Optional[DailyExtractItemList] = None


class DailyExtractFiles(BaseOFSResponse):
    """Daily extract files configuration"""

    name: str = "files"
    files: Optional[DailyExtractItemList] = None


class Subscription(BaseOFSResponse):
    """Subscription definition and configuration"""

    subscriptionId: Optional[str] = None
    name: str
    description: Optional[str] = None
    status: str = "active"
    organization: str = "default"


class SubscriptionList(OFSResponseList[Subscription]):
    @property
    def subscriptions(self) -> List[Subscription]:
        return [item for item in self.items] if self.items else []


class UserListResponse(OFSResponseList[User]):
    """Paginated response for user lists"""

    @property
    def users(self) -> List[User]:
        return [item for item in self.items] if self.items else []
