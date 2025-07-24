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


class ActivityProperty(BaseOFSResponse):
    """Activity property value"""
    
    value: Optional[Any] = None
    model_config = ConfigDict(extra="allow")


class ActivitySubmittedForm(BaseOFSResponse):
    """Submitted form data for an activity"""
    
    formId: Optional[str] = None
    formName: Optional[str] = None
    submittedTime: Optional[str] = None
    formData: Optional[Dict[str, Any]] = None
    model_config = ConfigDict(extra="allow")


class ActivitySubmittedFormListResponse(OFSResponseList[ActivitySubmittedForm]):
    """Response for activity submitted forms"""
    
    pass


class ActivityMultidaySegment(BaseOFSResponse):
    """Activity multiday segment information"""
    
    segmentId: Optional[int] = None
    date: Optional[str] = None
    startTime: Optional[str] = None
    endTime: Optional[str] = None
    duration: Optional[int] = None
    status: Optional[str] = None
    model_config = ConfigDict(extra="allow")


class ActivityMultidaySegmentListResponse(OFSResponseList[ActivityMultidaySegment]):
    """Response for activity multiday segments"""
    
    pass


class ActivityCapacityCategory(BaseOFSResponse):
    """Activity capacity category information"""
    
    categoryId: Optional[int] = None
    categoryLabel: str
    timeSlotId: Optional[int] = None
    requiredCapacity: Optional[int] = None
    model_config = ConfigDict(extra="allow")


class ActivityCapacityCategoryListResponse(OFSResponseList[ActivityCapacityCategory]):
    """Response for activity capacity categories"""
    
    pass


class ActivityResourcePreference(BaseOFSResponse):
    """Activity resource preference information"""
    
    resourceId: str
    preferenceType: Optional[str] = "preferred"  # preferred, required, excluded
    priority: Optional[int] = None
    model_config = ConfigDict(extra="allow")


class ActivityResourcePreferenceListResponse(OFSResponseList[ActivityResourcePreference]):
    """Response for activity resource preferences"""
    
    pass


class ActivityRequiredInventory(BaseOFSResponse):
    """Activity required inventory information"""
    
    inventoryType: str
    quantity: int = 1
    serialNumber: Optional[str] = None
    model: Optional[str] = None
    requiredCapacity: Optional[int] = None
    model_config = ConfigDict(extra="allow")


class ActivityRequiredInventoryListResponse(OFSResponseList[ActivityRequiredInventory]):
    """Response for activity required inventories"""
    
    pass


class ActivityCustomerInventory(BaseOFSResponse):
    """Activity customer inventory information"""
    
    inventoryId: Optional[int] = None
    inventoryType: str
    serialNumber: Optional[str] = None
    model: Optional[str] = None
    quantity: int = 1
    customerId: Optional[str] = None
    status: Optional[str] = "available"
    model_config = ConfigDict(extra="allow")


class ActivityCustomerInventoryListResponse(OFSResponseList[ActivityCustomerInventory]):
    """Response for activity customer inventories"""
    
    pass


class ActivityInstalledInventory(BaseOFSResponse):
    """Activity installed inventory information"""
    
    inventoryId: int
    inventoryType: str
    serialNumber: Optional[str] = None
    model: Optional[str] = None
    quantity: int = 1
    installedTime: Optional[str] = None
    installedBy: Optional[str] = None
    model_config = ConfigDict(extra="allow")


class ActivityInstalledInventoryListResponse(OFSResponseList[ActivityInstalledInventory]):
    """Response for activity installed inventories"""
    
    pass


class ActivityDeinstalledInventory(BaseOFSResponse):
    """Activity deinstalled inventory information"""
    
    inventoryId: int
    inventoryType: str
    serialNumber: Optional[str] = None
    model: Optional[str] = None
    quantity: int = 1
    deinstalledTime: Optional[str] = None
    deinstalledBy: Optional[str] = None
    reason: Optional[str] = None
    model_config = ConfigDict(extra="allow")


class ActivityDeinstalledInventoryListResponse(OFSResponseList[ActivityDeinstalledInventory]):
    """Response for activity deinstalled inventories"""
    
    pass


class ActivityLinkType(str, Enum):
    """Activity link type enumeration"""
    
    predecessor = "predecessor"
    successor = "successor"
    parent = "parent"
    child = "child"
    related = "related"


class ActivityLink(BaseOFSResponse):
    """Activity link information"""
    
    linkedActivityId: int
    linkType: ActivityLinkType
    description: Optional[str] = None
    createdTime: Optional[str] = None
    model_config = ConfigDict(extra="allow")


class ActivityLinkListResponse(OFSResponseList[ActivityLink]):
    """Response for activity links"""
    
    pass


class ActivityMoveRequest(BaseOFSResponse):
    """Request for moving an activity"""
    
    targetResourceId: Optional[str] = None
    targetDate: Optional[str] = None
    targetTime: Optional[str] = None
    moveReason: Optional[str] = None
    preserveTimeWindow: Optional[bool] = True
    model_config = ConfigDict(extra="allow")


class ActivityMoveResponse(BaseOFSResponse):
    """Response for activity move operations"""
    
    activityId: int
    previousResourceId: Optional[str] = None
    newResourceId: Optional[str] = None
    previousDate: Optional[str] = None
    newDate: Optional[str] = None
    moveTime: Optional[str] = None
    model_config = ConfigDict(extra="allow")


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


# Inventory Management
class Inventory(BaseOFSResponse):
    """Inventory item definition and configuration"""
    
    inventoryId: Optional[int] = None
    inventoryType: Optional[str] = None
    serialNumber: Optional[str] = None
    model: Optional[str] = None
    quantity: Optional[int] = None
    status: Optional[str] = None
    resourceId: Optional[str] = None
    activityId: Optional[int] = None
    model_config = ConfigDict(extra="allow")


class InventoryListResponse(OFSResponseList[Inventory]):
    """Paginated response for inventory lists"""
    
    pass


class ResourceInventory(BaseOFSResponse):
    """Resource inventory association"""
    
    inventoryId: int
    inventoryType: str
    serialNumber: Optional[str] = None
    model: Optional[str] = None
    quantity: int = 1
    status: Optional[str] = "available"
    model_config = ConfigDict(extra="allow")


class ResourceInventoryListResponse(OFSResponseList[ResourceInventory]):
    """Response for resource inventory lists"""
    
    pass


class ResourceWorkSkill(BaseOFSResponse):
    """Resource work skill association"""
    
    workSkillId: Optional[int] = None
    workSkillLabel: str
    level: Optional[int] = None
    status: Optional[str] = "active"
    model_config = ConfigDict(extra="allow")


class ResourceWorkSkillListResponse(OFSResponseList[ResourceWorkSkill]):
    """Response for resource work skills"""
    
    pass


class ResourceWorkZone(BaseOFSResponse):
    """Resource work zone association"""
    
    workZoneId: Optional[int] = None
    workZoneLabel: str
    status: Optional[str] = "active"
    model_config = ConfigDict(extra="allow")


class ResourceWorkZoneListResponse(OFSResponseList[ResourceWorkZone]):
    """Response for resource work zones"""
    
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


# Resource Schedule Management Models
class WorkScheduleRequest(BaseOFSResponse):
    """Request model for creating work schedule items"""
    
    recordType: CalendarViewItemRecordType
    startDate: date
    endDate: Optional[date] = None
    workTimeStart: Optional[str] = None
    workTimeEnd: Optional[str] = None
    scheduleLabel: Optional[str] = None
    shiftLabel: Optional[str] = None
    shiftType: Optional[str] = None
    isWorking: Optional[bool] = True
    nonWorkingReason: Optional[str] = None
    comments: Optional[str] = None
    points: Optional[int] = None
    recurrence: Optional[Recurrence] = None
    model_config = ConfigDict(extra="allow")


class CalendarItem(BaseOFSResponse):
    """Calendar item information"""
    
    calendarId: Optional[int] = None
    calendarName: str
    description: Optional[str] = None
    calendarType: Optional[str] = None
    status: Optional[str] = "active"
    organization: Optional[str] = "default"
    model_config = ConfigDict(extra="allow")


class CalendarListResponse(OFSResponseList[CalendarItem]):
    """Response for calendar lists"""
    
    pass


class BulkScheduleUpdateItem(BaseOFSResponse):
    """Individual resource schedule update for bulk operations"""
    
    resourceId: str
    scheduleItems: List[WorkScheduleRequest]
    model_config = ConfigDict(extra="allow")


class BulkScheduleUpdateRequest(BaseOFSResponse):
    """Request model for bulk work schedule updates"""
    
    resources: List[BulkScheduleUpdateItem]
    updateParameters: Optional[Dict[str, Any]] = None
    model_config = ConfigDict(extra="allow")


class BulkScheduleUpdateResponse(BaseOFSResponse):
    """Response for bulk schedule update operations"""
    
    successCount: Optional[int] = None
    errorCount: Optional[int] = None
    errors: Optional[List[Dict[str, Any]]] = None
    model_config = ConfigDict(extra="allow")


# Resource Property Management Models
class ResourcePropertyValue(BaseOFSResponse):
    """Resource property value"""
    
    value: Optional[Any] = None
    model_config = ConfigDict(extra="allow")


class ResourcePropertyRequest(BaseOFSResponse):
    """Request model for setting resource properties"""
    
    value: Any
    model_config = ConfigDict(extra="allow")


# Resource Location Management Models
class ResourceLocationRequest(BaseOFSResponse):
    """Request model for creating/updating resource locations"""
    
    label: str
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postalCode: Optional[str] = None
    country: Optional[str] = "US"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    timeZone: Optional[str] = None
    model_config = ConfigDict(extra="allow")


class PositionHistoryItem(BaseOFSResponse):
    """Individual position history entry"""
    
    timestamp: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    accuracy: Optional[float] = None
    speed: Optional[float] = None
    heading: Optional[float] = None
    altitude: Optional[float] = None
    model_config = ConfigDict(extra="allow")


class PositionHistory(OFSResponseList[PositionHistoryItem]):
    """Response for resource position history"""
    
    pass


# Route Planning & Operations Models
class ResourcePlan(BaseOFSResponse):
    """Resource plan information"""
    
    planId: Optional[int] = None
    planName: str
    description: Optional[str] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    status: Optional[str] = "active"
    planType: Optional[str] = None
    model_config = ConfigDict(extra="allow")


class ResourcePlanListResponse(OFSResponseList[ResourcePlan]):
    """Response for resource plans"""
    
    pass


class RouteInfo(BaseOFSResponse):
    """Route information for a specific date"""
    
    routeId: Optional[int] = None
    routeDate: str
    routeStatus: Optional[str] = None
    totalDistance: Optional[float] = None
    totalDuration: Optional[int] = None
    activities: Optional[List[Dict[str, Any]]] = None
    waypoints: Optional[List[Dict[str, Any]]] = None
    model_config = ConfigDict(extra="allow")


class NearbyActivity(BaseOFSResponse):
    """Nearby activity information"""
    
    activityId: int
    activityType: Optional[str] = None
    distance: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address: Optional[str] = None
    timeWindow: Optional[str] = None
    model_config = ConfigDict(extra="allow")


class NearbyActivityListResponse(OFSResponseList[NearbyActivity]):
    """Response for nearby activities"""
    
    pass


class RouteActivationRequest(BaseOFSResponse):
    """Request for route activation/deactivation"""
    
    reason: Optional[str] = None
    forceActivation: Optional[bool] = False
    model_config = ConfigDict(extra="allow")


# Bulk Operations & Service Requests Models
class BulkSkillUpdateItem(BaseOFSResponse):
    """Individual resource skill update for bulk operations"""
    
    resourceId: str
    workSkills: List[Dict[str, Any]]
    model_config = ConfigDict(extra="allow")


class BulkSkillUpdateRequest(BaseOFSResponse):
    """Request for bulk work skill updates"""
    
    resources: List[BulkSkillUpdateItem]
    updateParameters: Optional[Dict[str, Any]] = None
    model_config = ConfigDict(extra="allow")


class BulkZoneUpdateItem(BaseOFSResponse):
    """Individual resource zone update for bulk operations"""
    
    resourceId: str
    workZones: List[Dict[str, Any]]
    model_config = ConfigDict(extra="allow")


class BulkZoneUpdateRequest(BaseOFSResponse):
    """Request for bulk work zone updates"""
    
    resources: List[BulkZoneUpdateItem]
    updateParameters: Optional[Dict[str, Any]] = None
    model_config = ConfigDict(extra="allow")


class BulkInventoryUpdateItem(BaseOFSResponse):
    """Individual resource inventory update for bulk operations"""
    
    resourceId: str
    inventories: List[Dict[str, Any]]
    model_config = ConfigDict(extra="allow")


class BulkInventoryUpdateRequest(BaseOFSResponse):
    """Request for bulk inventory updates"""
    
    resources: List[BulkInventoryUpdateItem]
    updateParameters: Optional[Dict[str, Any]] = None
    model_config = ConfigDict(extra="allow")


class ResourceMatchRequest(BaseOFSResponse):
    """Request for finding matching resources"""
    
    activityId: Optional[int] = None
    activityType: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    date: Optional[str] = None
    timeWindow: Optional[str] = None
    skills: Optional[List[str]] = None
    maxDistance: Optional[float] = None
    model_config = ConfigDict(extra="allow")


class UrgentAssignmentRequest(BaseOFSResponse):
    """Request for urgent assignment resources"""
    
    activityId: int
    urgencyLevel: Optional[str] = "high"
    maxTravelTime: Optional[int] = None
    maxDistance: Optional[float] = None
    model_config = ConfigDict(extra="allow")


class SetPositionsRequest(BaseOFSResponse):
    """Request for setting resource positions"""
    
    positions: List[Dict[str, Any]]
    timestamp: Optional[str] = None
    model_config = ConfigDict(extra="allow")


class LastKnownPosition(BaseOFSResponse):
    """Last known position information"""
    
    resourceId: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    timestamp: Optional[str] = None
    accuracy: Optional[float] = None
    model_config = ConfigDict(extra="allow")


class LastKnownPositionListResponse(OFSResponseList[LastKnownPosition]):
    """Response for last known positions"""
    
    pass


class ResourcesInAreaQuery(BaseOFSResponse):
    """Query parameters for resources in area"""
    
    latitude: float
    longitude: float
    radius: float
    radiusUnit: Optional[str] = "km"
    resourceTypes: Optional[List[str]] = None
    model_config = ConfigDict(extra="allow")


class ServiceRequest(BaseOFSResponse):
    """Service request information"""
    
    requestId: Optional[str] = None
    requestType: Optional[str] = None
    customerId: Optional[str] = None
    customerName: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = "normal"
    status: Optional[str] = "open"
    createdTime: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address: Optional[str] = None
    model_config = ConfigDict(extra="allow")


class ServiceRequestListResponse(OFSResponseList[ServiceRequest]):
    """Response for service requests"""
    
    pass


class ServiceRequestProperty(BaseOFSResponse):
    """Service request property value"""
    
    value: Optional[Any] = None
    model_config = ConfigDict(extra="allow")


# Additional Response Models for Full Model Compliance
class RouteActivationResponse(BaseOFSResponse):
    """Response for route activation/deactivation operations"""
    
    success: Optional[bool] = None
    message: Optional[str] = None
    routeId: Optional[int] = None
    routeDate: Optional[str] = None
    activationTime: Optional[str] = None
    model_config = ConfigDict(extra="allow")


class BulkSkillUpdateResponse(BaseOFSResponse):
    """Response for bulk work skill update operations"""
    
    successCount: Optional[int] = None
    errorCount: Optional[int] = None
    processedResources: Optional[List[str]] = None
    errors: Optional[List[Dict[str, Any]]] = None
    model_config = ConfigDict(extra="allow")


class BulkZoneUpdateResponse(BaseOFSResponse):
    """Response for bulk work zone update operations"""
    
    successCount: Optional[int] = None
    errorCount: Optional[int] = None
    processedResources: Optional[List[str]] = None
    errors: Optional[List[Dict[str, Any]]] = None
    model_config = ConfigDict(extra="allow")


class BulkInventoryUpdateResponse(BaseOFSResponse):
    """Response for bulk inventory update operations"""
    
    successCount: Optional[int] = None
    errorCount: Optional[int] = None
    processedResources: Optional[List[str]] = None
    errors: Optional[List[Dict[str, Any]]] = None
    model_config = ConfigDict(extra="allow")


class ResourceMatchResponse(BaseOFSResponse):
    """Response for resource matching operations"""
    
    matchedResources: Optional[List[Dict[str, Any]]] = None
    totalMatches: Optional[int] = None
    searchCriteria: Optional[Dict[str, Any]] = None
    model_config = ConfigDict(extra="allow")


class UrgentAssignmentResponse(BaseOFSResponse):
    """Response for urgent assignment resource finding"""
    
    availableResources: Optional[List[Dict[str, Any]]] = None
    recommendedResource: Optional[Dict[str, Any]] = None
    urgencyLevel: Optional[str] = None
    estimatedResponseTime: Optional[int] = None
    model_config = ConfigDict(extra="allow")


class SetPositionsResponse(BaseOFSResponse):
    """Response for setting resource positions"""
    
    successCount: Optional[int] = None
    errorCount: Optional[int] = None
    processedPositions: Optional[List[Dict[str, Any]]] = None
    errors: Optional[List[Dict[str, Any]]] = None
    model_config = ConfigDict(extra="allow")


class ResourcesInAreaResponse(BaseOFSResponse):
    """Response for resources in area queries"""
    
    resources: Optional[List[Dict[str, Any]]] = None
    totalFound: Optional[int] = None
    searchArea: Optional[Dict[str, Any]] = None
    model_config = ConfigDict(extra="allow")
