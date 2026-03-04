from datetime import time
from enum import Enum
from typing import Any, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, RootModel, field_validator
from typing_extensions import Annotated

from ._base import (
    EntityEnum,
    OFSResponseList,
    SharingEnum,
    Status,
    Translation,
    TranslationList,
)

# region Metadata / Activity Type Groups


class ActivityTypeGroup(BaseModel):
    label: str
    name: str
    _activityTypes: Annotated[Optional[list[dict]], "activityTypes"] = []
    translations: TranslationList

    @property
    def activityTypes(self):
        return (
            [_activityType["label"] for _activityType in self._activityTypes]
            if self._activityTypes is not None
            else []
        )


class ActivityTypeGroupList(RootModel[list[ActivityTypeGroup]]):
    def __iter__(self):  # type: ignore[override]
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]


class ActivityTypeGroupListResponse(OFSResponseList[ActivityTypeGroup]):
    pass


# endregion Metadata / Activity Type Groups

# region Metadata / Activity Types


class ActivityTypeColors(BaseModel):
    cancelled: Annotated[Optional[str], Field(alias="cancelled")]
    completed: Annotated[Optional[str], Field(alias="completed")]
    enroute: Annotated[Optional[str], Field(alias="enroute")] = None
    notdone: Annotated[Optional[str], Field(alias="notdone")]
    notOrdered: Annotated[Optional[str], Field(alias="notOrdered")]
    pending: Annotated[Optional[str], Field(alias="pending")]
    started: Annotated[Optional[str], Field(alias="started")]
    suspended: Annotated[Optional[str], Field(alias="suspended")]
    warning: Annotated[Optional[str], Field(alias="warning")]


class ActivityTypeFeatures(BaseModel):
    model_config = ConfigDict(extra="allow")
    allowCreationInBuckets: Optional[bool] = False
    allowMassActivities: Optional[bool] = False
    allowMoveBetweenResources: Optional[bool] = False
    allowNonScheduled: Optional[bool] = False
    allowRepeatingActivities: Optional[bool] = False
    allowReschedule: Optional[bool] = False
    allowToCreateFromIncomingInterface: Optional[bool] = False
    allowToSearch: Optional[bool] = False
    calculateActivityDurationUsingStatistics: Optional[bool] = False
    calculateDeliveryWindow: Optional[bool] = False
    calculateTravel: Optional[bool] = False
    disableLocationTracking: Optional[bool] = False
    enableDayBeforeTrigger: Optional[bool] = False
    enableNotStartedTrigger: Optional[bool] = False
    enableReminderAndChangeTriggers: Optional[bool] = False
    enableSwWarningTrigger: Optional[bool] = False
    isSegmentingEnabled: Optional[bool] = False
    isTeamworkAvailable: Optional[bool] = False
    slaAndServiceWindowUseCustomerTimeZone: Optional[bool] = False
    supportOfInventory: Optional[bool] = False
    supportOfLinks: Optional[bool] = False
    supportOfNotOrderedActivities: Optional[bool] = False
    supportOfPreferredResources: Optional[bool] = False
    supportOfRequiredInventory: Optional[bool] = False
    supportOfTimeSlots: Optional[bool] = False
    supportOfWorkSkills: Optional[bool] = False
    supportOfWorkZones: Optional[bool] = False


class ActivityTypeTimeSlots(BaseModel):
    label: str


class ActivityType(BaseModel):
    active: bool
    colors: Optional[ActivityTypeColors] = None
    defaultDuration: int
    features: Optional[ActivityTypeFeatures] = None
    groupLabel: Optional[str]
    label: str
    name: str
    segmentMaxDuration: Optional[int] = None
    segmentMinDuration: Optional[int] = None
    timeSlots: Optional[list[ActivityTypeTimeSlots]] = None
    translations: TranslationList


class ActivityTypeList(RootModel[list[ActivityType]]):
    def __iter__(self):  # type: ignore[override]
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]


class ActivityTypeListResponse(OFSResponseList[ActivityType]):
    pass


# endregion Metadata / Activity Types

# region Metadata / Applications


class ApplicationsResourcestoAllow(BaseModel):
    resourceId: str
    resourceInternalId: int


class Application(BaseModel):
    label: str
    name: str
    resourcesToAllow: Optional[list[ApplicationsResourcestoAllow]] = None
    allowedCorsDomains: Optional[list[str]] = None
    IPAddressesToAllow: Optional[list[str]] = None
    status: str
    tokenService: str


class ApplicationListResponse(OFSResponseList[Application]):
    pass


class Link(BaseModel):
    """Represents a link in API responses."""

    rel: str
    href: str
    model_config = ConfigDict(extra="allow")


class ApiMethod(BaseModel):
    """Represents an API method permission."""

    label: str
    status: str  # "on" or "off"
    model_config = ConfigDict(extra="allow")


class ApiEntity(BaseModel):
    """Represents an API entity permission."""

    label: str
    access: str  # "ReadWrite", "ReadOnly", etc.
    model_config = ConfigDict(extra="allow")


class BaseApiAccess(BaseModel):
    """Base class for application API access with common fields."""

    label: str
    name: str
    status: Status
    links: Optional[list[Link]] = None


class SimpleApiAccess(BaseApiAccess):
    """API access for simple APIs with entity-based permissions.

    Used by: coreAPI, metadataAPI, statisticsAPI, fieldCollaborationAPI
    """

    apiEntities: list[ApiEntity]
    model_config = ConfigDict(extra="forbid")


class CapacityApiAccess(BaseApiAccess):
    """API access for capacity API with method-based permissions.

    Used by: capacityAPI
    """

    apiMethods: list[ApiMethod]
    model_config = ConfigDict(extra="forbid")


class StructuredApiAccess(BaseApiAccess):
    """API access for structured APIs with no detailed permissions.

    Used by: partsCatalogAPI, outboundAPI
    """

    model_config = ConfigDict(extra="forbid")


class InboundApiAccess(BaseApiAccess):
    """API access for inbound API with field configurations.

    Used by: inboundAPI
    """

    activityFields: Optional[list[Any]] = None
    inventoryFields: Optional[list[Any]] = None
    providerFields: Optional[list[Any]] = None
    model_config = ConfigDict(extra="forbid")


# Mapping of API labels to their types
API_TYPE_MAP = {
    "coreAPI": SimpleApiAccess,
    "metadataAPI": SimpleApiAccess,
    "statisticsAPI": SimpleApiAccess,
    "fieldCollaborationAPI": SimpleApiAccess,
    "capacityAPI": CapacityApiAccess,
    "inboundAPI": InboundApiAccess,
    # Default to StructuredApiAccess for others
}


def parse_application_api_access(
    data: dict[str, Any],
) -> Union[SimpleApiAccess, CapacityApiAccess, InboundApiAccess, StructuredApiAccess]:
    """Parse API access data into the appropriate subclass based on label.

    Args:
        data: Raw API response data

    Returns:
        Appropriate ApplicationApiAccess subclass instance
    """
    label = data.get("label", "")
    access_class = API_TYPE_MAP.get(label, StructuredApiAccess)
    return access_class.model_validate(data)


# Type alias for the discriminated union
ApplicationApiAccess = Union[
    SimpleApiAccess, CapacityApiAccess, InboundApiAccess, StructuredApiAccess
]


class ApplicationApiAccessList(RootModel[list[ApplicationApiAccess]]):
    """List of application API accesses."""

    def __iter__(self):  # type: ignore[override]
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]


class ApplicationApiAccessListResponse(BaseModel):
    """Response from GET /rest/ofscMetadata/v1/applications/{label}/apiAccess."""

    items: list[ApplicationApiAccess]
    links: Optional[list[Link]] = None
    model_config = ConfigDict(extra="allow")

    @field_validator("items", mode="before")
    @classmethod
    def parse_items(cls, v):
        """Parse each item into the appropriate ApplicationApiAccess subclass.

        Note: List endpoint returns basic fields only, so items will be
        StructuredApiAccess unless they have permission details.
        """
        if isinstance(v, list):
            parsed_items = []
            for item in v:
                if isinstance(item, dict):
                    # List responses only have basic fields, use StructuredApiAccess
                    # unless the item has detailed permission fields
                    if (
                        "apiEntities" in item
                        or "apiMethods" in item
                        or "activityFields" in item
                    ):
                        parsed_items.append(parse_application_api_access(item))
                    else:
                        # Basic fields only - use StructuredApiAccess
                        parsed_items.append(StructuredApiAccess.model_validate(item))
                else:
                    parsed_items.append(item)
            return parsed_items
        return v


# endregion Metadata / Applications

# region Metadata / Capacity Areas


class CapacityAreaParent(BaseModel):
    label: str
    name: Optional[str] = None


class CapacityAreaConfiguration(BaseModel):
    isTimeSlotBase: bool
    byCapacityCategory: str
    byDay: str
    byTimeSlot: str
    isAllowCloseOnWorkzoneLevel: bool
    definitionLevel: list[str]


class CapacityArea(BaseModel):
    label: str
    name: Optional[str] = None
    type: Optional[str] = "area"
    status: Optional[Status] = Status.active
    configuration: Optional[CapacityAreaConfiguration] = None
    parentLabel: Optional[str] = None
    parent: Annotated[Optional[CapacityAreaParent], Field(alias="parent")] = None
    translations: Annotated[Optional[TranslationList], Field(alias="translations")] = (
        None
    )
    # Note: as of 24A the additional fields returned are just HREFs so we won't include them here


class CapacityAreaList(RootModel[list[CapacityArea]]):
    def __iter__(self):  # type: ignore[override]
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]


class CapacityAreaListResponse(OFSResponseList[CapacityArea]):
    pass


class CapacityAreaCapacityCategory(BaseModel):
    label: str
    name: Optional[str] = None
    status: Optional[str] = None


class CapacityAreaCapacityCategoriesResponse(BaseModel):
    items: list[CapacityAreaCapacityCategory] = []

    def __iter__(self):  # type: ignore
        return iter(self.items)

    def __getitem__(self, item):
        return self.items[item]

    def __len__(self):
        return len(self.items)


class CapacityAreaWorkZone(BaseModel):
    workZoneLabel: str
    workZoneName: Optional[str] = None


class CapacityAreaWorkZonesResponse(BaseModel):
    items: list[CapacityAreaWorkZone] = []

    def __iter__(self):  # type: ignore
        return iter(self.items)

    def __getitem__(self, item):
        return self.items[item]

    def __len__(self):
        return len(self.items)


class CapacityAreaWorkZoneV1(BaseModel):
    label: str


class CapacityAreaWorkZonesV1Response(BaseModel):
    items: list[CapacityAreaWorkZoneV1] = []

    def __iter__(self):  # type: ignore
        return iter(self.items)

    def __getitem__(self, item):
        return self.items[item]

    def __len__(self):
        return len(self.items)


class CapacityAreaTimeSlot(BaseModel):
    label: str
    name: Optional[str] = None
    timeFrom: Optional[str] = None
    timeTo: Optional[str] = None


class CapacityAreaTimeSlotsResponse(BaseModel):
    items: list[CapacityAreaTimeSlot] = []

    def __iter__(self):  # type: ignore
        return iter(self.items)

    def __getitem__(self, item):
        return self.items[item]

    def __len__(self):
        return len(self.items)


class CapacityAreaTimeInterval(BaseModel):
    timeFrom: Optional[str] = None
    timeTo: Optional[str] = None


class CapacityAreaTimeIntervalsResponse(BaseModel):
    items: list[CapacityAreaTimeInterval] = []

    def __iter__(self):  # type: ignore
        return iter(self.items)

    def __getitem__(self, item):
        return self.items[item]

    def __len__(self):
        return len(self.items)


class CapacityAreaOrganization(BaseModel):
    label: str
    name: Optional[str] = None
    type: Optional[str] = None


class CapacityAreaOrganizationsResponse(BaseModel):
    items: list[CapacityAreaOrganization] = []

    def __iter__(self):  # type: ignore
        return iter(self.items)

    def __getitem__(self, item):
        return self.items[item]

    def __len__(self):
        return len(self.items)


class CapacityAreaChildrenResponse(BaseModel):
    items: list[CapacityArea] = []

    def __iter__(self):  # type: ignore
        return iter(self.items)

    def __getitem__(self, item):
        return self.items[item]

    def __len__(self):
        return len(self.items)


# endregion Metadata / Capacity Areas

# region Metadata / Capacity Categories


class Item(BaseModel):
    label: str
    name: Optional[str] = None


class ItemList(RootModel[list[Item]]):
    def __iter__(self):  # type: ignore[override]
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]


class CapacityCategory(BaseModel):
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
    pass


# endregion Metadata / Capacity Categories

# region Metadata / Forms


class Form(BaseModel):
    """Form entity in Oracle Field Service.

    From swagger:
    - label: required, min 1, max 40 chars
    - name: required, min 1, max 255 chars
    - translations: array of Translation objects (optional, returned if no language param)
    - content: JSON string describing form content (optional, only in FormDetails)
    """

    label: str
    name: str
    translations: Annotated[Optional[TranslationList], Field(alias="translations")] = (
        None
    )
    content: Optional[str] = None
    model_config = ConfigDict(extra="allow")


class FormList(RootModel[list[Form]]):
    def __iter__(self):  # type: ignore[override]
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]


class FormListResponse(OFSResponseList[Form]):
    """Response from GET /rest/ofscMetadata/v1/forms."""

    pass


# endregion Metadata / Forms

# region Metadata / Inventory Types


class InventoryType(BaseModel):
    label: str
    translations: Annotated[Optional[TranslationList], Field(alias="translations")] = (
        None
    )
    active: bool = True
    model_property: Optional[str] = Field(default=None, alias="modelProperty")
    non_serialized: bool = Field(default=False, alias="nonSerialized")
    quantityPrecision: Optional[int] = 0
    model_config = ConfigDict(extra="allow", populate_by_name=True)


class InventoryTypeList(RootModel[list[InventoryType]]):
    def __iter__(self):  # type: ignore[override]
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]


class InventoryTypeListResponse(OFSResponseList[InventoryType]):
    pass


# endregion Metadata / Inventory Types

# region Metadata / Languages


class LanguageTranslation(BaseModel):
    """Translation of a language name into another language."""

    language: str
    languageISO: str
    name: str


class Language(BaseModel):
    """Language configuration in OFSC."""

    label: str
    code: str
    name: str
    active: bool
    translations: list[LanguageTranslation]


class LanguageList(RootModel[list[Language]]):
    """List of languages."""

    def __iter__(self):  # type: ignore[override]
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]


class LanguageListResponse(OFSResponseList[Language]):
    """Response for get_languages with pagination metadata."""

    pass


# endregion Metadata / Languages

# region Metadata / Link Templates


class LinkTemplateType(str, Enum):
    finishToStart = "finishToStart"
    startToStart = "startToStart"
    simultaneous = "simultaneous"
    related = "related"


class LinkTemplateInterval(str, Enum):
    unlimited = "unlimited"
    adjustable = "adjustable"
    nonAdjustable = "nonAdjustable"


class LinkTemplateSchedulingConstraint(str, Enum):
    sameDay = "sameDay"
    differentDays = "differentDays"


class LinkTemplateAssignmentConstraint(str, Enum):
    sameResource = "sameResource"
    differentResources = "differentResources"


class LinkTemplateTranslation(BaseModel):
    language: str
    name: str
    reverseName: Optional[str] = None


class LinkTemplate(BaseModel):
    label: str
    reverseLabel: Optional[str] = None
    active: bool
    linkType: LinkTemplateType
    minInterval: Optional[LinkTemplateInterval] = None
    maxInterval: Optional[LinkTemplateInterval] = None
    minIntervalValue: Optional[int] = None
    schedulingConstraint: Optional[LinkTemplateSchedulingConstraint] = None
    assignmentConstraints: Optional[LinkTemplateAssignmentConstraint] = None
    translations: list[LinkTemplateTranslation]


class LinkTemplateList(RootModel[list[LinkTemplate]]):
    def __iter__(self):  # type: ignore[override]
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]


class LinkTemplateListResponse(OFSResponseList[LinkTemplate]):
    pass


# endregion Metadata / Link Templates

# region Metadata / Map Layers


class ShapeHintActionType(str, Enum):
    """Action type for shape hint button."""

    plugin = "plugin"
    form = "form"


class ShapeHintColumn(BaseModel):
    """Shape hint column configuration for map layers.

    From swagger: required fields are defaultName, sourceColumn, pluginFormField
    """

    defaultName: str
    sourceColumn: str
    pluginFormField: str


class ShapeHintButton(BaseModel):
    """Shape hint button configuration for map layers.

    From swagger: actionType is enum ["plugin", "form"], label is required
    """

    actionType: ShapeHintActionType
    label: str


class MapLayer(BaseModel):
    """Map layer (CustomMapLayer) configuration in OFSC.

    From swagger:
    - label: required, max 24 chars, pattern ^[A-Za-z0-9_]+$
    - status: enum ["active", "inactive"]
    - text: read-only, name in user's language
    - translations: required for PUT/POST
    """

    label: str
    status: Optional[Status] = None
    text: Optional[str] = None  # Read-only name in user's language
    translations: Annotated[Optional[TranslationList], Field(alias="translations")] = (
        None
    )
    shapeTitleColumn: Optional[str] = None
    tableColumns: Optional[list[str]] = None
    shapeHintColumns: Optional[list[ShapeHintColumn]] = None
    shapeHintButton: Optional[ShapeHintButton] = None
    model_config = ConfigDict(extra="allow")


class MapLayerList(RootModel[list[MapLayer]]):
    def __iter__(self):  # type: ignore[override]
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]


class MapLayerListResponse(OFSResponseList[MapLayer]):
    """Response from GET /rest/ofscMetadata/v1/mapLayers (CustomMapLayers)."""

    pass


class PopulateStatusResponse(BaseModel):
    """Response from GET populate status endpoints (map layers, workzone shapes)."""

    status: Optional[str] = None
    time: Optional[str] = None
    downloadId: Optional[int] = None


# endregion Metadata / Map Layers

# region Metadata / Non-working Reasons


class NonWorkingReason(BaseModel):
    label: str
    name: str
    active: bool
    translations: TranslationList


class NonWorkingReasonList(RootModel[list[NonWorkingReason]]):
    def __iter__(self):  # type: ignore[override]
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]


class NonWorkingReasonListResponse(OFSResponseList[NonWorkingReason]):
    pass


# endregion Metadata / Non-working Reasons

# region Metadata / Organizations


class OrganizationType(str, Enum):
    contractor = "contractor"
    inhouse = "inhouse"


class Organization(BaseModel):
    label: str
    name: str
    translations: TranslationList
    type: OrganizationType


class OrganizationList(RootModel[list[Organization]]):
    def __iter__(self):  # type: ignore[override]
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]


class OrganizationListResponse(OFSResponseList[Organization]):
    pass


# endregion Metadata / Organizations

# region Metadata / Plugins
# endregion Metadata / Plugins

# region Metadata / Properties


class Property(BaseModel):
    label: str
    name: str
    type: str
    entity: Optional[EntityEnum] = None
    gui: Optional[str] = None
    translations: Annotated[Optional[TranslationList], Field(validate_default=True)] = (
        None
    )

    @field_validator("translations")
    def set_default(cls, field_value, values):
        if field_value is None:
            return TranslationList([Translation(name=values.data.get("name"))])
        return field_value

    @field_validator("gui")
    @classmethod
    def gui_match(cls, v):
        if v not in [
            "text",
            "checkbox",
            "combobox",
            "radiogroup",
            "file",
            "signature",
            "image",
            "url",
            "phone",
            "email",
            "capture",
            "geo",
            "attachments",
        ]:
            raise ValueError(f"{v} is not a valid GUI value")
        return v

    model_config = ConfigDict(extra="ignore")


class PropertyList(RootModel[list[Property]]):
    def __iter__(self):  # type: ignore[override]
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]


class PropertyListResponse(OFSResponseList[Property]):
    """Response model for list of properties"""

    pass


class EnumerationValue(BaseModel):
    active: bool
    label: str
    translations: TranslationList

    @property
    def map(self):
        return {translation.language: translation for translation in self.translations}


class EnumerationValueList(OFSResponseList[EnumerationValue]):
    pass


# endregion Metadata / Properties

# region Metadata / Resource Types


class ResourceType(BaseModel):
    label: str
    name: str
    active: bool
    role: str  # TODO: change to enum
    model_config = ConfigDict(extra="allow")


class ResourceTypeList(RootModel[list[ResourceType]]):
    def __iter__(self):  # type: ignore[override]
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]


class ResourceTypeListResponse(OFSResponseList[ResourceType]):
    pass


# endregion Metadata / Resource Types

# region Metadata / Routing Profiles


class RoutingProfile(BaseModel):
    """Model for routing profile entity

    A routing profile is a group of routing plans that enables assignment
    to multiple buckets without duplicating plans.
    """

    profileLabel: str = Field(
        ..., description="Unique identifier for the routing profile"
    )
    model_config = ConfigDict(extra="allow")


class RoutingProfileList(OFSResponseList[RoutingProfile]):
    """Response model for list of routing profiles"""

    pass


class RoutingPlan(BaseModel):
    """Model for routing plan entity

    A routing plan is a configuration within a routing profile that defines
    routing behavior and parameters.
    """

    planLabel: str = Field(..., description="Unique identifier for the routing plan")
    model_config = ConfigDict(extra="allow")


class RoutingPlanList(OFSResponseList[RoutingPlan]):
    """Response model for list of routing plans within a profile"""

    pass


class RoutingPlanExport(BaseModel):
    """Model for routing plan export response

    Contains links to download the exported routing plan data.
    """

    mediaType: str = Field(
        default="application/octet-stream",
        description="MIME type of the exported content",
    )
    links: list[Link] = Field(default_factory=list, description="Download links")
    model_config = ConfigDict(extra="allow")


class RoutingProviderGroup(BaseModel):
    """Model for provider group within a routing activity group"""

    priority: str = Field(description="Priority value for this provider group")
    filterLabel: str = Field(description="Filter label identifying the provider")
    model_config = ConfigDict(extra="allow")


class RoutingActivityGroup(BaseModel):
    """Model for activity group within a routing plan"""

    activity_location: str = Field(
        description="Location type (e.g., 'resource_routing_date', 'bucket_routing_date')"
    )
    unacceptable_overdue: int = Field(
        default=0, description="Unacceptable overdue time"
    )
    overdue_cost: int = Field(default=50, description="Cost for overdue activities")
    non_assignment_cost: int = Field(
        default=0, description="Cost for non-assigned activities"
    )
    sla_cost_coeff: int = Field(default=3, description="SLA cost coefficient")
    sla_overdue_cost: int = Field(default=-1, description="SLA overdue cost")
    sla_violation_fact_cost: int = Field(
        default=-1, description="SLA violation fact cost"
    )
    is_multiday: int = Field(default=0, description="Is multiday activity")
    autoordering_type: int = Field(default=0, description="Auto-ordering type")
    sla_policy: int = Field(default=0, description="SLA policy")
    bundling_policy: int = Field(default=0, description="Bundling policy")
    filterLabel: str = Field(description="Filter label for this activity group")
    providerGroups: list[RoutingProviderGroup] = Field(
        default_factory=list, description="List of provider groups"
    )
    model_config = ConfigDict(extra="allow")


class RoutingPlanConfig(BaseModel):
    """Model for complete routing plan configuration

    Contains all routing plan settings including optimization parameters,
    time limits, costs, and activity group configurations.
    """

    # Basic plan information
    rpname: str = Field(description="Routing plan name")
    rpactive: int = Field(default=1, description="Plan active status (0/1)")
    rptype: str = Field(default="manual", description="Plan type")
    rpdate: int = Field(default=0, description="Plan date")
    rp_label: str = Field(description="Routing plan label")
    rpdescription: Optional[str] = Field(default="", description="Plan description")

    # Time settings
    rpfrom_time: Optional[str] = Field(default=None, description="Start time")
    rpto_time: Optional[str] = Field(default=None, description="End time")
    rpinterval: Optional[str] = Field(default=None, description="Time interval")
    rpweekdays: Optional[str | int] = Field(
        default=None, description="Weekdays (string or int)"
    )
    rptime_limit: int = Field(default=30, description="Time limit in minutes")
    rptime_slr_limit_percent: int = Field(
        default=50, description="SLR time limit percentage"
    )

    # Optimization settings
    rpoptimization: str = Field(default="fastest", description="Optimization type")
    rpgoal_based_optimization: str = Field(
        default="maximize_jobs", description="Goal-based optimization strategy"
    )
    rpauto_ordering: int = Field(default=0, description="Auto ordering enabled")

    # Fitness coefficients
    rpfitness_coeff_uniformity: float = Field(
        default=0.0, description="Fitness coefficient for uniformity"
    )
    rpfitness_coeff_window_reservation: float = Field(
        default=0.2, description="Fitness coefficient for window reservation"
    )

    # Dynamic settings
    rpdynamic_cut_time: int = Field(default=0, description="Dynamic cut time")
    rpdynamic_cut_nappt: int = Field(
        default=0, description="Dynamic cut number of appointments"
    )
    rpinvert_cut: int = Field(default=0, description="Invert cut setting")

    # Zone and distance settings
    rphome_zone_radius_overstep_weight: int = Field(
        default=4, description="Home zone radius overstep weight"
    )
    rpunacceptable_travel_time: int = Field(
        default=0, description="Unacceptable travel time"
    )
    rpunacceptable_travel_distance: int = Field(
        default=0, description="Unacceptable travel distance"
    )

    # Machine operation settings
    rpmachine_operation_deadline_shift: int = Field(
        default=20, description="Machine operation deadline shift"
    )

    # SLR and points settings
    rpuse_slr: int = Field(default=0, description="Use SLR")
    rpload_technicians_by_points: int = Field(
        default=0, description="Load technicians by points"
    )
    rpdefault_appt_points: int = Field(
        default=0, description="Default appointment points"
    )
    rpget_technician_points_from_calendar: int = Field(
        default=0, description="Get technician points from calendar"
    )
    rpdefault_tech_points: int = Field(default=0, description="Default tech points")
    rpcalendar_point_size: int = Field(default=0, description="Calendar point size")
    rpcalendar_reserved: int = Field(default=0, description="Calendar reserved")

    # Assurance and skill settings
    rpassurance_still_limit: Optional[int] = Field(
        default=20, description="Assurance still limit"
    )
    rpinsufficient_skill_factor: float = Field(
        default=1.0, description="Insufficient skill factor"
    )

    # Center point settings
    rpdefault_center_point_radius: int = Field(
        default=0, description="Default center point radius"
    )
    rpcenter_point_enable: int = Field(default=0, description="Center point enabled")

    # Inventory and reoptimization
    rpuse_required_inventory: int = Field(
        default=0, description="Use required inventory"
    )
    rpreoptimization_enable: int = Field(
        default=1, description="Reoptimization enabled"
    )
    rpreoptimization_reduce_overdue_threshold: Optional[int] = Field(
        default=None, description="Reoptimization reduce overdue threshold"
    )

    # Algorithm and bundling
    rpimmediate_algorithm: str = Field(default="", description="Immediate algorithm")
    rpbundling_from: int = Field(default=0, description="Bundling from")
    rpbundling_to: int = Field(default=0, description="Bundling to")

    # Assignment settings
    rpassignment_from: int = Field(default=0, description="Assignment from")
    rpassignment_to: int = Field(default=1, description="Assignment to")
    rpassign_bucket_resource: int = Field(
        default=1, description="Assign bucket resource"
    )

    # Subtype and broadcast
    rpsubtype: str = Field(default="normal", description="Plan subtype")
    rpbroadcast_timeout: int = Field(default=0, description="Broadcast timeout")

    # Advanced settings
    rpadvanced_reoptimization_cost_override: int = Field(
        default=0, description="Advanced reoptimization cost override"
    )
    rpadvanced_reoptimization_cost: int = Field(
        default=0, description="Advanced reoptimization cost"
    )
    rpadvanced_reserved_part_of_service_window_override: int = Field(
        default=0, description="Advanced reserved part of service window override"
    )
    rpadvanced_reserved_part_of_service_window: int = Field(
        default=0, description="Advanced reserved part of service window"
    )

    # Routing and workzone
    rprouting_to_contractor: int = Field(default=0, description="Routing to contractor")
    rpignore_workzone_mismatch: int = Field(
        default=0, description="Ignore workzone mismatch"
    )

    # Inventory waiting
    rpinventory_waiting_days: int = Field(
        default=0, description="Inventory waiting days"
    )

    # Daily distance
    daily_distance_limit_is_used: int = Field(
        default=0, description="Daily distance limit is used"
    )
    unacceptable_daily_distance: Optional[int] = Field(
        default=None, description="Unacceptable daily distance"
    )

    # Flags and recommendations
    flags: int = Field(default=0, description="Plan flags")
    rprecomended_min_time_limit: int = Field(
        default=-1, description="Recommended min time limit"
    )
    rprecomended_max_time_limit: int = Field(
        default=-1, description="Recommended max time limit"
    )
    rprecomended_balanced_time_limit: int = Field(
        default=-1, description="Recommended balanced time limit"
    )

    # Related labels
    messageFlowLabel: str = Field(
        default="MessageFlowIsNotSet", description="Message flow label"
    )
    warehouseVisitWorkTypeLabel: str = Field(
        default="ActivityTypeIsNotSet", description="Warehouse visit work type label"
    )
    predecessorLabel: str = Field(
        default="RoutingPlanLabelIsNotSet", description="Predecessor label"
    )
    triggerFilterLabel: str = Field(default="Other", description="Trigger filter label")

    # Activity groups
    activityGroups: list[RoutingActivityGroup] = Field(
        default_factory=list, description="List of activity groups"
    )

    # Audit fields
    last_updated_by: str = Field(default="", description="Last updated by")
    last_update_date: str = Field(default="", description="Last update date")
    last_update_login: str = Field(default="", description="Last update login")
    created_by: str = Field(default="", description="Created by")
    creation_date: str = Field(default="", description="Creation date")

    model_config = ConfigDict(extra="allow")


class RoutingPlanData(BaseModel):
    """Complete routing plan export response

    Contains the full routing plan configuration along with signature
    and version information. Fields are optional as API may return
    different formats (metadata only vs full plan data).
    """

    routing_plan: Optional[RoutingPlanConfig] = Field(
        default=None, description="Complete routing plan configuration"
    )
    sign: Optional[str] = Field(
        default=None, description="Signature for the routing plan"
    )
    version: Optional[str] = Field(
        default=None, description="Version of the routing plan format"
    )
    mediaType: Optional[str] = Field(
        default=None, description="Media type of the export response"
    )
    model_config = ConfigDict(extra="allow")


# endregion Metadata / Routing Profiles

# region Metadata / Shifts


class ShiftType(str, Enum):
    """Type of a shift."""

    regular = "regular"
    on_call = "on-call"


class ShiftDecoration(str, Enum):
    """Decoration color for on-call shifts."""

    yellow = "yellow"
    orange = "orange"
    red = "red"
    blue = "blue"
    green = "green"
    purple = "purple"


class Shift(BaseModel):
    """Shift configuration in OFSC.

    From swagger and actual API response:
    - label: the shift identifier (e.g., "8-17", "on-call")
    - name: the display name (e.g., "First shift 8-17")
    - active: boolean, whether shift appears in dropdown
    - type: enum ["regular", "on-call"]
    - workTimeStart: time (HH:MM:SS format)
    - workTimeEnd: time (HH:MM:SS format)
    - points: optional, integer
    - decoration: optional, enum for on-call shifts (6 colors)
    """

    label: str
    name: str
    active: bool
    type: Optional[ShiftType] = None
    workTimeStart: time
    workTimeEnd: time
    points: Optional[int] = None
    decoration: Optional[ShiftDecoration] = None
    model_config = ConfigDict(extra="allow")


class ShiftUpdate(BaseModel):
    """Shift update payload — excludes immutable 'type' field."""

    label: str
    name: str
    active: bool
    workTimeStart: time
    workTimeEnd: time
    points: Optional[int] = None
    decoration: Optional[ShiftDecoration] = None
    model_config = ConfigDict(extra="forbid")


class ShiftList(RootModel[list[Shift]]):
    def __iter__(self):  # type: ignore[override]
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]


class ShiftListResponse(OFSResponseList[Shift]):
    """Response from GET /rest/ofscMetadata/v1/shifts."""

    pass


# endregion Metadata / Shifts

# region Metadata / Time Slots


class TimeSlot(BaseModel):
    """Time slot model for Oracle Field Service."""

    label: str
    name: str
    active: bool
    isAllDay: bool
    timeStart: Optional[time] = None
    timeEnd: Optional[time] = None


class TimeSlotListResponse(OFSResponseList[TimeSlot]):
    """Response model for list of time slots."""

    pass


# endregion Metadata / Time Slots

# region Metadata / Work Skills


class Workskill(BaseModel):
    """Work skill entity in OFSC.

    A work skill represents a specific capability or expertise that can be
    assigned to resources and required by activities.
    """

    label: str
    active: bool = True
    name: str = ""
    sharing: SharingEnum
    translations: Annotated[Optional[TranslationList], Field(validate_default=True)] = (
        None
    )

    @field_validator("translations")
    def set_default(cls, field_value, values):
        return field_value or TranslationList(
            [Translation(name=values.data.get("name"))]
        )


class WorkskillList(RootModel[list[Workskill]]):
    def __iter__(self):  # type: ignore[override]
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]


class WorkskillListResponse(OFSResponseList[Workskill]):
    """Response from GET /rest/ofscMetadata/v1/workSkills."""

    pass


class Condition(BaseModel):
    """Condition for work skill conditions."""

    label: str
    function: str
    value: Any = None
    valueList: list = []


class WorkskillCondition(BaseModel):
    """Work skill condition configuration in OFSC."""

    internalId: int
    label: str
    requiredLevel: int
    preferableLevel: int
    conditions: list[Condition]
    dependencies: Any = None


class WorkskillConditionList(RootModel[list[WorkskillCondition]]):
    """List of work skill conditions."""

    def __iter__(self):  # type: ignore[override]
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]


class WorkskillAssignment(BaseModel):
    """Work skill assignment for work skill groups."""

    label: str
    ratio: int = Field(gt=0, lt=101)
    model_config = ConfigDict(extra="forbid")


class WorkskillAssignmentList(RootModel[list[WorkskillAssignment]]):
    """List of work skill assignments."""

    def __iter__(self):  # type: ignore[override]
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]


class WorkskillGroup(BaseModel):
    """Work skill group configuration in OFSC.

    Work skill groups combine multiple work skills with ratios for
    assignment to resources and capacity categories.
    """

    label: str
    name: str
    active: bool
    assignToResource: bool
    addToCapacityCategory: bool
    workSkills: WorkskillAssignmentList
    translations: TranslationList
    model_config = ConfigDict(extra="ignore")


class WorkskillGroupList(RootModel[list[WorkskillGroup]]):
    """List of work skill groups."""

    def __iter__(self):  # type: ignore[override]
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]


class WorkskillGroupListResponse(OFSResponseList[WorkskillGroup]):
    """Response from GET /rest/ofscMetadata/v1/workSkillGroups."""

    pass


# endregion Metadata / Work Skills

# region Metadata / Work Zones


class Workzone(BaseModel):
    workZoneLabel: str
    workZoneName: str
    status: Status
    travelArea: str
    keys: Optional[list[str]] = None
    shapes: Optional[list[str]] = None
    organization: Optional[str] = None


class WorkzoneList(RootModel[list[Workzone]]):
    def __iter__(self):  # type: ignore[override]
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]


class WorkzoneListResponse(OFSResponseList[Workzone]):
    """Response model for list of workzones"""

    pass


class WorkZoneKeyElement(BaseModel):
    label: str
    length: Optional[int] = None
    function: Optional[str] = None
    order: Optional[int] = None
    apiParameterName: Optional[str] = None


class WorkZoneKeyResponse(BaseModel):
    current: list[WorkZoneKeyElement]
    pending: Optional[list[WorkZoneKeyElement]] = None


# endregion Metadata / Work Zones
