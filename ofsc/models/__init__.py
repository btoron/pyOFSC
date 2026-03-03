from datetime import date
from enum import Enum
from typing import Dict, Literal, Optional

from pydantic import (
    AliasChoices,
    AnyHttpUrl,
    BaseModel,
    ConfigDict,
    Field,
    RootModel,
    field_validator,
    model_validator,
)

from ._base import (
    CsvList as CsvList,
    EntityEnum as EntityEnum,
    OFSApi as OFSApi,
    OFSAPIError as OFSAPIError,
    OFSConfig as OFSConfig,
    OFSOAuthRequest as OFSOAuthRequest,
    OFSResponseBoundedList as OFSResponseBoundedList,
    OFSResponseList as OFSResponseList,
    OFSResponseUnboundedList as OFSResponseUnboundedList,
    SharingEnum as SharingEnum,
    Status as Status,
    Translation as Translation,
    TranslationList as TranslationList,
)

from .users import (
    CollaborationGroup as CollaborationGroup,
    CollaborationGroupsResponse as CollaborationGroupsResponse,
    User as User,
    UserCreate as UserCreate,
    UserListResponse as UserListResponse,
)

from .metadata import (
    ActivityType as ActivityType,
    ActivityTypeColors as ActivityTypeColors,
    ActivityTypeFeatures as ActivityTypeFeatures,
    ActivityTypeGroup as ActivityTypeGroup,
    ActivityTypeGroupList as ActivityTypeGroupList,
    ActivityTypeGroupListResponse as ActivityTypeGroupListResponse,
    ActivityTypeList as ActivityTypeList,
    ActivityTypeListResponse as ActivityTypeListResponse,
    ActivityTypeTimeSlots as ActivityTypeTimeSlots,
    ApiEntity as ApiEntity,
    ApiMethod as ApiMethod,
    Application as Application,
    ApplicationApiAccess as ApplicationApiAccess,
    ApplicationApiAccessList as ApplicationApiAccessList,
    ApplicationApiAccessListResponse as ApplicationApiAccessListResponse,
    ApplicationListResponse as ApplicationListResponse,
    ApplicationsResourcestoAllow as ApplicationsResourcestoAllow,
    BaseApiAccess as BaseApiAccess,
    CapacityApiAccess as CapacityApiAccess,
    CapacityArea as CapacityArea,
    CapacityAreaConfiguration as CapacityAreaConfiguration,
    CapacityAreaList as CapacityAreaList,
    CapacityAreaListResponse as CapacityAreaListResponse,
    CapacityAreaParent as CapacityAreaParent,
    CapacityCategory as CapacityCategory,
    CapacityCategoryListResponse as CapacityCategoryListResponse,
    Condition as Condition,
    EnumerationValue as EnumerationValue,
    EnumerationValueList as EnumerationValueList,
    Form as Form,
    FormList as FormList,
    FormListResponse as FormListResponse,
    InboundApiAccess as InboundApiAccess,
    InventoryType as InventoryType,
    InventoryTypeList as InventoryTypeList,
    InventoryTypeListResponse as InventoryTypeListResponse,
    Item as Item,
    ItemList as ItemList,
    Language as Language,
    LanguageList as LanguageList,
    LanguageListResponse as LanguageListResponse,
    LanguageTranslation as LanguageTranslation,
    Link as Link,
    LinkTemplate as LinkTemplate,
    LinkTemplateAssignmentConstraint as LinkTemplateAssignmentConstraint,
    LinkTemplateInterval as LinkTemplateInterval,
    LinkTemplateList as LinkTemplateList,
    LinkTemplateListResponse as LinkTemplateListResponse,
    LinkTemplateSchedulingConstraint as LinkTemplateSchedulingConstraint,
    LinkTemplateTranslation as LinkTemplateTranslation,
    LinkTemplateType as LinkTemplateType,
    MapLayer as MapLayer,
    MapLayerList as MapLayerList,
    MapLayerListResponse as MapLayerListResponse,
    NonWorkingReason as NonWorkingReason,
    NonWorkingReasonList as NonWorkingReasonList,
    NonWorkingReasonListResponse as NonWorkingReasonListResponse,
    Organization as Organization,
    OrganizationList as OrganizationList,
    OrganizationListResponse as OrganizationListResponse,
    OrganizationType as OrganizationType,
    parse_application_api_access as parse_application_api_access,
    Property as Property,
    PropertyList as PropertyList,
    PropertyListResponse as PropertyListResponse,
    ResourceType as ResourceType,
    ResourceTypeList as ResourceTypeList,
    ResourceTypeListResponse as ResourceTypeListResponse,
    RoutingActivityGroup as RoutingActivityGroup,
    RoutingPlan as RoutingPlan,
    RoutingPlanConfig as RoutingPlanConfig,
    RoutingPlanData as RoutingPlanData,
    RoutingPlanExport as RoutingPlanExport,
    RoutingPlanList as RoutingPlanList,
    RoutingProfile as RoutingProfile,
    RoutingProfileList as RoutingProfileList,
    RoutingProviderGroup as RoutingProviderGroup,
    ShapeHintActionType as ShapeHintActionType,
    ShapeHintButton as ShapeHintButton,
    ShapeHintColumn as ShapeHintColumn,
    Shift as Shift,
    ShiftDecoration as ShiftDecoration,
    ShiftList as ShiftList,
    ShiftListResponse as ShiftListResponse,
    ShiftType as ShiftType,
    SimpleApiAccess as SimpleApiAccess,
    StructuredApiAccess as StructuredApiAccess,
    TimeSlot as TimeSlot,
    TimeSlotListResponse as TimeSlotListResponse,
    Workskill as Workskill,
    WorkskillAssignment as WorkskillAssignment,
    WorkskillAssignmentList as WorkskillAssignmentList,
    WorkskillCondition as WorkskillCondition,
    WorkskillConditionList as WorkskillConditionList,
    WorkskillGroup as WorkskillGroup,
    WorkskillGroupList as WorkskillGroupList,
    WorkskillGroupListResponse as WorkskillGroupListResponse,
    WorkskillList as WorkskillList,
    WorkskillListResponse as WorkskillListResponse,
    Workzone as Workzone,
    WorkzoneList as WorkzoneList,
    WorkzoneListResponse as WorkzoneListResponse,
)

# region Core / Activities


class Activity(BaseModel):
    activityId: Optional[int] = None
    activityType: Optional[str] = None
    date: Optional[str] = None
    model_config = ConfigDict(extra="allow")


class GetActivitiesParams(BaseModel):
    """Parameters for get_activities API endpoint.

    Note: offset and limit are handled separately as method parameters.
    """

    resources: Optional[list[str]] = None
    includeChildren: Optional[Literal["none", "immediate", "all"]] = "all"
    q: Optional[str] = None
    dateFrom: Optional[date] = None
    dateTo: Optional[date] = None
    fields: Optional[list[str]] = None
    includeNonScheduled: Optional[bool] = False
    svcWorkOrderId: Optional[int] = None

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def validate_date_requirements(self):
        # dateFrom and dateTo must both be specified or both be None
        if (self.dateFrom is None) != (self.dateTo is None):
            raise ValueError(
                "dateFrom and dateTo must both be specified or both omitted"
            )

        # Check date range is valid
        if self.dateFrom and self.dateTo and self.dateFrom > self.dateTo:
            raise ValueError("dateFrom must be before or equal to dateTo")

        # If no dates and no svcWorkOrderId, must have includeNonScheduled=True
        if self.dateFrom is None and self.svcWorkOrderId is None:
            if not self.includeNonScheduled:
                raise ValueError(
                    "Either dateFrom/dateTo, svcWorkOrderId, or includeNonScheduled=True is required"
                )

        return self

    def to_api_params(self) -> dict:
        """Convert to API query parameters."""
        params = {}
        if self.resources:
            params["resources"] = ",".join(self.resources)
        if self.includeChildren:
            params["includeChildren"] = self.includeChildren
        if self.q:
            params["q"] = self.q
        if self.dateFrom:
            params["dateFrom"] = self.dateFrom.isoformat()
        if self.dateTo:
            params["dateTo"] = self.dateTo.isoformat()
        if self.fields:
            params["fields"] = ",".join(self.fields)
        if self.includeNonScheduled:
            params["includeNonScheduled"] = "true"
        if self.svcWorkOrderId:
            params["svcWorkOrderId"] = self.svcWorkOrderId
        return params


class BulkUpdateActivityItem(Activity):
    activityId: Optional[int] = None
    activityType: Optional[str] = None
    date: Optional[str] = None
    model_config = ConfigDict(extra="allow")


# CORE / BulkUpdaterequest


class BulkUpdateParameters(BaseModel):
    fallbackResource: Optional[str] = None
    identifyActivityBy: Optional[str] = None
    ifExistsThenDoNotUpdateFields: Optional[list[str]] = None
    ifInFinalStatusThen: Optional[str] = None
    inventoryPropertiesUpdateMode: Optional[str] = None


class BulkUpdateRequest(BaseModel):
    activities: list[BulkUpdateActivityItem]
    updateParameters: BulkUpdateParameters


class ActivityKeys(BaseModel):
    activityId: Optional[int] = None
    apptNumber: Optional[str] = None
    customerNumber: Optional[str] = None


class BulkUpdateError(BaseModel):
    errorDetail: Optional[str] = None
    operation: Optional[str] = None


class BulkUpdateWarning(BaseModel):
    code: Optional[int] = None
    message: Optional[int] = None


class BulkUpdateResult(BaseModel):
    activityKeys: Optional[ActivityKeys] = None
    errors: Optional[list[BulkUpdateError]] = None
    operationsFailed: Optional[list[str]] = None
    operationsPerformed: Optional[list[str]] = None
    warnings: Optional[list[BulkUpdateWarning]] = None


class BulkUpdateResponse(BaseModel):
    results: Optional[list[BulkUpdateResult]] = None


# Core / Activities - List Responses and Nested Models


class ActivityListResponse(OFSResponseList[Activity]):
    """List response for activities with pagination."""

    pass


# Core / Activities - Submitted Forms


class FormIdentifier(BaseModel):
    """Form identifier with submit ID and label."""

    formSubmitId: Optional[int] = None
    formLabel: Optional[str] = None


class SubmittedForm(BaseModel):
    """Submitted form associated with an activity."""

    formIdentifier: Optional[FormIdentifier] = None
    user: Optional[str] = None
    time: Optional[str] = None
    model_config = ConfigDict(extra="allow")


class SubmittedFormsResponse(BaseModel):
    """Response for submitted forms with pagination."""

    items: list[SubmittedForm] = []
    offset: Optional[int] = None
    limit: Optional[int] = None
    totalResults: Optional[int] = None
    hasMore: Optional[bool] = None


# Core / Activities - Resource Preferences


class ResourcePreference(BaseModel):
    """Resource preference for an activity."""

    resourceId: Optional[str] = None
    resourceInternalId: Optional[int] = None
    preferenceType: Optional[str] = None  # required, preferred, forbidden


class ResourcePreferencesResponse(BaseModel):
    """Response for resource preferences (no pagination)."""

    items: list[ResourcePreference] = []


# Core / Activities - Required Inventories


class RequiredInventory(BaseModel):
    """Required inventory item for an activity."""

    inventoryType: str
    model: str
    quantity: float


class RequiredInventoriesResponse(BaseModel):
    """Response for required inventories."""

    items: list[RequiredInventory] = []
    offset: Optional[int] = None
    limit: Optional[int] = None
    totalResults: Optional[int] = None


# Core / Activities - Inventories (Common for customer/installed/deinstalled)


class Inventory(BaseModel):
    """Inventory item (customer, installed, or deinstalled)."""

    inventoryId: Optional[int] = None
    activityId: Optional[int] = None
    inventoryType: Optional[str] = None
    status: Optional[str] = None  # customer, resource, installed, deinstalled
    quantity: Optional[float] = None
    serialNumber: Optional[str] = None
    model_config = ConfigDict(extra="allow")


class InventoryListResponse(BaseModel):
    """Response for inventory lists."""

    items: list[Inventory] = []
    offset: Optional[str | int] = None  # Can be string or int from API
    limit: Optional[str | int] = None  # Can be string or int from API
    totalResults: Optional[int] = None


# Core / Activities - Linked Activities


class LinkedActivity(BaseModel):
    """Linked activity relationship."""

    fromActivityId: int
    toActivityId: int
    linkType: str
    minIntervalValue: Optional[int] = None
    alerts: Optional[int] = None


class LinkedActivitiesResponse(BaseModel):
    """Response for linked activities (no pagination)."""

    items: list[LinkedActivity] = []


# Core / Activities - Capacity Categories


class ActivityCapacityCategory(BaseModel):
    """Capacity category for an activity."""

    capacityCategory: str


class ActivityCapacityCategoriesResponse(BaseModel):
    """Response for activity capacity categories."""

    items: list[ActivityCapacityCategory] = []
    totalResults: Optional[int] = None


# endregion Core / Activities


# region Core / Resources


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


# endregion Core / Resources


# region Core / Daily Extracts


class DailyExtractLink(BaseModel):
    """Link in daily extract responses."""

    href: AnyHttpUrl
    rel: str
    mediaType: Optional[str] = None


class DailyExtractItem(BaseModel):
    name: str
    bytes: Optional[int] = None
    mediaType: Optional[str] = None
    links: list[DailyExtractLink]


class DailyExtractItemList(BaseModel):
    items: list[DailyExtractItem] = []


class DailyExtractFolders(BaseModel):
    name: str = "folders"
    folders: Optional[DailyExtractItemList] = None


class DailyExtractFiles(BaseModel):
    name: str = "files"
    files: Optional[DailyExtractItemList] = None


# endregion Core / Daily Extracts


# region Core / Events & Subscriptions


class Subscription(BaseModel):
    """Subscription to OFSC events."""

    subscriptionId: Optional[str] = None
    title: Optional[str] = None
    events: list[str] = []
    apiVersion: Optional[str] = None
    active: Optional[bool] = None
    createdTime: Optional[str] = None
    links: Optional[list[dict]] = None
    model_config = ConfigDict(extra="allow")


class SubscriptionListResponse(OFSResponseList[Subscription]):
    """Paginated list of subscriptions."""

    pass


class CreateSubscriptionRequest(BaseModel):
    """Request to create a new subscription."""

    events: list[str]
    title: str
    apiVersion: Optional[str] = None
    model_config = ConfigDict(extra="allow")


class Event(BaseModel):
    """OFSC event from subscription."""

    eventType: Optional[str] = None
    subscriptionId: Optional[str] = None
    eventTime: Optional[str] = None
    activityId: Optional[int] = None
    resourceId: Optional[str] = None
    model_config = ConfigDict(extra="allow")


class EventListResponse(OFSResponseList[Event]):
    """List of events."""

    pass


# endregion Core / Events & Subscriptions


# region Capacity


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
            raise ValueError(
                f"Expected list[str], CsvList, str, dict with 'value' key, or None, got {type(v)}"
            )

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
    quotaPercent: Optional[float] = None  # Changed to float
    minQuota: Optional[int] = None
    used: Optional[int] = None
    usedQuotaPercent: Optional[float] = None  # Changed to float
    bookedActivities: Optional[int] = None
    quotaIsClosed: Optional[bool] = None  # Added
    quotaIsAutoClosed: Optional[bool] = None  # Added
    intervals: list[QuotaTimeInterval] = []  # Added
    categories: list[QuotaCategoryItem] = []  # Added
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
            raise ValueError(
                f"Expected list[str], CsvList, str, dict with 'value' key, or None, got {type(v)}"
            )

    def get_areas_list(self) -> list[str]:
        """Get areas as a list of strings"""
        return self.areas.to_list() if self.areas is not None else []

    def get_categories_list(self) -> list[str]:
        """Get categories as a list of strings"""
        return self.categories.to_list() if self.categories is not None else []

    def get_dates_list(self) -> list[str]:
        """Get dates as a list of strings"""
        return self.dates.to_list()


# endregion
