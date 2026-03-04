from datetime import date
from typing import Literal, Optional

from pydantic import (
    AnyHttpUrl,
    BaseModel,
    ConfigDict,
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

from .resources import (
    AssignedLocation as AssignedLocation,
    AssignedLocationsResponse as AssignedLocationsResponse,
    BaseUser as BaseUser,
    Calendar as Calendar,
    CalendarView as CalendarView,
    CalendarViewItem as CalendarViewItem,
    CalendarViewItemRecordType as CalendarViewItemRecordType,
    CalendarViewList as CalendarViewList,
    CalendarViewShift as CalendarViewShift,
    CalendarsListResponse as CalendarsListResponse,
    Location as Location,
    LocationList as LocationList,
    LocationListResponse as LocationListResponse,
    PositionHistoryItem as PositionHistoryItem,
    PositionHistoryResponse as PositionHistoryResponse,
    Recurrence as Recurrence,
    RecurrenceType as RecurrenceType,
    Resource as Resource,
    ResourceCreate as ResourceCreate,
    ResourceAssistant as ResourceAssistant,
    ResourceAssistantsResponse as ResourceAssistantsResponse,
    ResourceList as ResourceList,
    ResourceListResponse as ResourceListResponse,
    ResourcePlan as ResourcePlan,
    ResourcePlansResponse as ResourcePlansResponse,
    ResourceRouteActivity as ResourceRouteActivity,
    ResourceRouteResponse as ResourceRouteResponse,
    ResourceUsersListResponse as ResourceUsersListResponse,
    ResourceWorkScheduleItem as ResourceWorkScheduleItem,
    ResourceWorkScheduleResponse as ResourceWorkScheduleResponse,
    ResourceWorkScheduleResponseList as ResourceWorkScheduleResponseList,
    ResourceWorkskillAssignment as ResourceWorkskillAssignment,
    ResourceWorkskillListResponse as ResourceWorkskillListResponse,
    ResourceWorkzoneAssignment as ResourceWorkzoneAssignment,
    ResourceWorkzoneListResponse as ResourceWorkzoneListResponse,
    WeekDay as WeekDay,
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

from .inventories import (
    Inventory as Inventory,
    InventoryCreate as InventoryCreate,
    InventoryCustomAction as InventoryCustomAction,
    InventoryListResponse as InventoryListResponse,
    RequiredInventoriesResponse as RequiredInventoriesResponse,
    RequiredInventory as RequiredInventory,
)

from .statistics import (
    ActivityDurationStat as ActivityDurationStat,
    ActivityDurationStatsList as ActivityDurationStatsList,
    ActivityTravelStat as ActivityTravelStat,
    ActivityTravelStatsList as ActivityTravelStatsList,
    AirlineDistanceData as AirlineDistanceData,
    AirlineDistanceBasedTravel as AirlineDistanceBasedTravel,
    AirlineDistanceBasedTravelList as AirlineDistanceBasedTravelList,
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

from .capacity import (
    ActivityBookingOptionsResponse as ActivityBookingOptionsResponse,
    BookingArea as BookingArea,
    BookingClosingScheduleItem as BookingClosingScheduleItem,
    BookingClosingScheduleResponse as BookingClosingScheduleResponse,
    BookingClosingScheduleUpdateRequest as BookingClosingScheduleUpdateRequest,
    BookingDate as BookingDate,
    BookingFieldDependency as BookingFieldDependency,
    BookingFieldsDependenciesResponse as BookingFieldsDependenciesResponse,
    BookingGridActivity as BookingGridActivity,
    BookingGridArea as BookingGridArea,
    BookingGridDateItem as BookingGridDateItem,
    BookingGridTimeSlot as BookingGridTimeSlot,
    BookingStatusEntry as BookingStatusEntry,
    BookingStatusItem as BookingStatusItem,
    BookingStatusesResponse as BookingStatusesResponse,
    BookingStatusesUpdateRequest as BookingStatusesUpdateRequest,
    BookingTimeSlot as BookingTimeSlot,
    CapacityAreaResponseItem as CapacityAreaResponseItem,
    CapacityCategoryItem as CapacityCategoryItem,
    CapacityMetrics as CapacityMetrics,
    CapacityRequest as CapacityRequest,
    CapacityResponseItem as CapacityResponseItem,
    GetCapacityResponse as GetCapacityResponse,
    GetQuotaRequest as GetQuotaRequest,
    GetQuotaResponse as GetQuotaResponse,
    QuotaAreaItem as QuotaAreaItem,
    QuotaCategoryItem as QuotaCategoryItem,
    QuotaResponseItem as QuotaResponseItem,
    QuotaTimeInterval as QuotaTimeInterval,
    QuotaUpdateArea as QuotaUpdateArea,
    QuotaUpdateCategory as QuotaUpdateCategory,
    QuotaUpdateItem as QuotaUpdateItem,
    QuotaUpdateRequest as QuotaUpdateRequest,
    QuotaUpdateResponse as QuotaUpdateResponse,
    ShowBookingGridRequest as ShowBookingGridRequest,
    ShowBookingGridResponse as ShowBookingGridResponse,
)

# endregion
