"""Resource models for OFSC Core API."""

from datetime import date
from enum import Enum
from typing import Dict, Optional

from pydantic import (
    AliasChoices,
    BaseModel,
    ConfigDict,
    Field,
    RootModel,
    model_validator,
)

from ._base import OFSResponseList


class Resource(BaseModel):
    resourceId: Optional[str] = None
    parentResourceId: Optional[str] = None
    resourceType: str
    name: str
    status: str = "active"
    organization: str = "default"
    language: str
    languageISO: Optional[str] = None
    timeZone: str
    timeFormat: str = "24-hour"
    dateFormat: str = "mm/dd/yy"
    email: Optional[str] = None
    phone: Optional[str] = None
    model_config = ConfigDict(extra="allow")


class ResourceCreate(BaseModel):
    """Resource creation model enforcing required fields."""

    model_config = ConfigDict(extra="allow")

    parentResourceId: str
    resourceType: str
    name: str
    language: str
    timeZone: str
    status: Optional[str] = None
    organization: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    timeFormat: Optional[str] = None
    dateFormat: Optional[str] = None


class ResourceList(RootModel[list[Resource]]):
    def __iter__(self):  # type: ignore[override]
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]


class BaseUser(BaseModel):
    login: str


class ResourceUsersListResponse(OFSResponseList[BaseUser]):
    @property
    def users(self) -> list[str]:
        return [item.login for item in self.items]


class RecurrenceType(str, Enum):
    daily = "daily"
    weekly = "weekly"
    everyday = "everyday"
    yearly = "yearly"


class WeekDay(str, Enum):
    Sunday = "Sun"
    Monday = "Mon"
    Tuesday = "Tue"
    Wednesday = "Wed"
    Thursday = "Thu"
    Friday = "Fri"
    Saturday = "Sat"


class Recurrence(BaseModel):
    dayFrom: Optional[date] = None
    dayTo: Optional[date] = None
    # OFS omits recurEvery for "everyday" recurrences (#218)
    recurEvery: Optional[int] = Field(default=None, ge=1, le=255)
    recurrenceType: RecurrenceType
    weekDays: Optional[list[str]] = None

    @model_validator(mode="after")
    def check_week_days(self):
        if self.recurrenceType == RecurrenceType.weekly and not self.weekDays:
            raise ValueError("weekDays is required for weekly recurrence")
        if self.recurrenceType == RecurrenceType.yearly and not self.dayFrom:
            raise ValueError("dayFrom is required for yearly recurrence")
        if self.recurrenceType == RecurrenceType.yearly and not self.dayTo:
            raise ValueError("dayTo is required for yearly recurrence")
        return self


class CalendarViewItemRecordType(str, Enum):
    schedule = "schedule"
    shift = "shift"
    extra_shift = "extra_shift"
    working = "working"
    extra_working = "extra_working"
    non_working = "non-working"
    error = "error"


class CalendarViewItem(BaseModel):
    comments: Optional[str] = None
    nonWorkingReason: Optional[str] = None
    points: Optional[int] = None
    recordType: CalendarViewItemRecordType
    scheduleLabel: Optional[str] = None
    shiftLabel: Optional[str] = None
    workTimeEnd: Optional[str] = None
    workTimeStart: Optional[str] = None


class CalendarViewList(RootModel[list[CalendarViewItem]]):
    def __iter__(self):  # type: ignore[override]
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]


class CalendarViewShift(BaseModel):
    regular: Optional[CalendarViewItem] = Field(default=None)
    on_call: Optional[CalendarViewItem] = Field(default=None, validation_alias=AliasChoices("onCall", "on-call"))


class CalendarView(RootModel[Dict[str, CalendarViewShift]]):
    def __iter__(self):  # type: ignore[override]
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]


class ResourceWorkScheduleItem(BaseModel):
    comments: Optional[str] = None
    endDate: Optional[date] = None
    isWorking: Optional[bool] = None
    nonWorkingReason: Optional[str] = None
    points: Optional[int] = None
    recordType: CalendarViewItemRecordType
    recurrence: Optional[Recurrence] = Recurrence(recurEvery=1, recurrenceType=RecurrenceType.daily)
    scheduleItemId: Optional[int] = None
    scheduleLabel: Optional[str] = None
    scheduleShifts: Optional[list[CalendarViewItem]] = None
    shiftLabel: Optional[str] = None
    shiftType: Optional[str] = None
    startDate: Optional[date] = date.today()
    workTimeEnd: Optional[str] = None
    workTimeStart: Optional[str] = None


class ResourceWorkScheduleResponseList(RootModel[list[ResourceWorkScheduleItem]]):
    def __iter__(self):  # type: ignore[override]
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]


class ResourceWorkScheduleResponse(OFSResponseList[ResourceWorkScheduleItem]):
    pass


class Location(BaseModel):
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


class LocationList(RootModel[list[Location]]):
    def __iter__(self):  # type: ignore[override]
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]


class AssignedLocation(BaseModel):
    start: Optional[int] = None
    end: Optional[int] = None
    homeZoneCenter: Optional[int] = None


class AssignedLocationsResponse(BaseModel):
    mon: Optional[AssignedLocation] = None
    tue: Optional[AssignedLocation] = None
    wed: Optional[AssignedLocation] = None
    thu: Optional[AssignedLocation] = None
    fri: Optional[AssignedLocation] = None
    sat: Optional[AssignedLocation] = None
    sun: Optional[AssignedLocation] = None
    model_config = ConfigDict(extra="allow")


class LocationListResponse(OFSResponseList[Location]):
    pass


class ResourceListResponse(OFSResponseList[Resource]):
    """Paginated list of resources."""

    pass


class ResourceAssistant(BaseModel):
    """Assistant resource assignment."""

    resourceId: Optional[str] = None
    parentResourceId: Optional[str] = None
    model_config = ConfigDict(extra="allow")


class ResourceAssistantsResponse(OFSResponseList[ResourceAssistant]):
    """List of assistant resources."""

    pass


class ResourceWorkskillAssignment(BaseModel):
    """Workskill assigned to a resource."""

    workSkill: Optional[str] = None
    ratio: Optional[int] = None
    startDate: Optional[str] = None
    model_config = ConfigDict(extra="allow")


class ResourceWorkskillListResponse(OFSResponseList[ResourceWorkskillAssignment]):
    """Workskills assigned to a resource."""

    pass


class ResourceWorkzoneAssignment(BaseModel):
    """Workzone assigned to a resource."""

    workZone: Optional[str] = None
    workZoneItemId: Optional[int] = None
    workZoneStatus: Optional[str] = None
    ratio: Optional[int] = None
    startDate: Optional[str] = None
    recurrence: Optional[str] = None
    recurEvery: Optional[int] = None
    type: Optional[str] = None
    model_config = ConfigDict(extra="allow")


class ResourceWorkzoneListResponse(OFSResponseList[ResourceWorkzoneAssignment]):
    """Workzones assigned to a resource."""

    pass


class PositionHistoryItem(BaseModel):
    """Position history entry."""

    time: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    model_config = ConfigDict(extra="allow")


class PositionHistoryResponse(OFSResponseList[PositionHistoryItem]):
    """Position history response."""

    pass


class ResourceRouteActivity(BaseModel):
    """Activity in a resource route."""

    activityId: Optional[int] = None
    activityType: Optional[str] = None
    status: Optional[str] = None
    model_config = ConfigDict(extra="allow")


class ResourceRouteResponse(OFSResponseList[ResourceRouteActivity]):
    """Resource route for a specific date."""

    routeStartTime: Optional[str] = None


class ResourcePlan(BaseModel):
    """Resource routing plan."""

    label: Optional[str] = None
    name: Optional[str] = None
    model_config = ConfigDict(extra="allow")


class ResourcePlansResponse(OFSResponseList[ResourcePlan]):
    """Resource plans response."""

    pass


class Calendar(BaseModel):
    """Calendar definition."""

    label: Optional[str] = None
    name: Optional[str] = None
    model_config = ConfigDict(extra="allow")


class CalendarsListResponse(OFSResponseList[Calendar]):
    """List of calendars."""

    pass


class ResourcePosition(BaseModel):
    """A position reported for a resource (setPositions request item)."""

    resourceId: str
    time: str
    lat: float
    lng: float
    alt: Optional[int] = None
    dir: Optional[float] = None
    spd: Optional[float] = None
    acc: Optional[int] = None


class SetPositionsError(BaseModel):
    itemIndex: Optional[int] = None
    message: Optional[str] = None
    model_config = ConfigDict(extra="allow")


class SetPositionsResponse(BaseModel):
    """Summary of a setPositions call."""

    itemsProcessed: Optional[int] = None
    itemsFailed: Optional[int] = None
    errors: Optional[list[SetPositionsError]] = None
    model_config = ConfigDict(extra="allow")


class LastKnownPosition(BaseModel):
    resourceId: Optional[str] = None
    time: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    errorMessage: Optional[str] = None
    model_config = ConfigDict(extra="allow")


class LastKnownPositionsResponse(BaseModel):
    items: list[LastKnownPosition] = Field(default_factory=list)
    totalResults: Optional[int] = None
    offset: Optional[int] = None
    hasMore: Optional[bool] = None
    model_config = ConfigDict(extra="allow")


class ResourceInArea(BaseModel):
    """A resource found by getResourcesInArea; fields vary so extras are kept."""

    resourceId: Optional[str] = None
    model_config = ConfigDict(extra="allow")


class ResourcesInAreaResponse(BaseModel):
    items: list[ResourceInArea] = Field(default_factory=list)
    totalResults: Optional[int] = None
    offset: Optional[int] = None
    limit: Optional[int] = None
    model_config = ConfigDict(extra="allow")


class NearbyActivitiesCoordinates(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class FindNearbyActivitiesResponse(BaseModel):
    """Activities near a resource; each item is a raw activity record."""

    items: list[dict] = Field(default_factory=list)
    coordinates: Optional[NearbyActivitiesCoordinates] = None
    model_config = ConfigDict(extra="allow")


class BulkUpdateResourceInventoriesResult(BaseModel):
    resourceId: Optional[str] = None
    created: Optional[int] = None
    updated: Optional[int] = None
    deleted: Optional[int] = None
    errors: Optional[list[dict]] = None
    model_config = ConfigDict(extra="allow")


class BulkUpdateResourceInventoriesResponse(BaseModel):
    created: Optional[int] = None
    updated: Optional[int] = None
    deleted: Optional[int] = None
    itemsFailed: Optional[int] = None
    results: list[BulkUpdateResourceInventoriesResult] = Field(default_factory=list)
    model_config = ConfigDict(extra="allow")


class MatchingResource(BaseModel):
    """Resource match from findMatchingResources."""

    resource: Optional[dict] = None
    fitness: Optional[dict] = None
    estimatedCompleteDate: Optional[str] = None
    schedule: Optional[dict] = None
    model_config = ConfigDict(extra="allow")


class FindMatchingResourcesResponse(BaseModel):
    totalResults: Optional[int] = None
    offset: Optional[int] = None
    limit: Optional[int] = None
    actualAtTime: Optional[str] = None
    items: list[MatchingResource] = Field(default_factory=list)
    model_config = ConfigDict(extra="allow")


class UrgentAssignmentResource(BaseModel):
    """Resource match from findResourcesForUrgentAssignment."""

    nearestRoutingBucket: Optional[str] = None
    startTime: Optional[str] = None
    estimatedAvailability: Optional[str] = None
    longitude: Optional[str] = None
    latitude: Optional[str] = None
    resourceDetails: Optional[dict] = None
    model_config = ConfigDict(extra="allow")


class FindUrgentResourcesResponse(BaseModel):
    items: list[UrgentAssignmentResource] = Field(default_factory=list)
    model_config = ConfigDict(extra="allow")
