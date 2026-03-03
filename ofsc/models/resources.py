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
    recurEvery: int = Field(ge=1, le=255)
    recurrenceType: RecurrenceType
    weekDays: Optional[list[str]] = None

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
    on_call: Optional[CalendarViewItem] = Field(
        default=None, validation_alias=AliasChoices("onCall", "on-call")
    )


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
    recurrence: Optional[Recurrence] = Recurrence(
        recurEvery=1, recurrenceType=RecurrenceType.daily
    )
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

    workZoneLabel: Optional[str] = None
    ratio: Optional[int] = None
    startDate: Optional[str] = None
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
