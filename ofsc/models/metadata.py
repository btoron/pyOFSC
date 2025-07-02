"""Metadata API models for OFSC Python Wrapper v3.0.

This module contains Pydantic models for OFSC Metadata API endpoints:
- Properties and property management
- Work skills and work skill conditions
- Work zones and geographical areas
- Activity types and activity type groups
- Resource types and organizational structures
- Applications and system configuration
- Inventory types and related metadata
"""

from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from typing_extensions import Annotated

from .base import (
    BaseOFSResponse,
    EntityEnum,
    Link,
    OFSResponseList,
    SharingEnum,
    Translation,
    TranslationList,
)

if TYPE_CHECKING:
    pass


# API Access Enums
class ApiAccessStatus(str, Enum):
    """Status values for API access configuration"""
    ACTIVE = "active"
    INACTIVE = "inactive"


class ApiAccessLabel(str, Enum):
    """Standard API access labels available in OFSC"""
    PARTS_CATALOG_API = "partsCatalogAPI"
    CAPACITY_API = "capacityAPI" 
    CORE_API = "coreAPI"
    FIELD_COLLABORATION_API = "fieldCollaborationAPI"
    INBOUND_API = "inboundAPI"
    METADATA_API = "metadataAPI"
    OUTBOUND_API = "outboundAPI"
    STATISTICS_API = "statisticsAPI"


class ApiAccessVisibility(str, Enum):
    """Visibility levels for API access entities"""
    READ_ONLY = "ReadOnly"
    READ_WRITE = "ReadWrite" 
    MANDATORY = "Mandatory"
    HIDDEN = "Hidden"


class ApiMethodStatus(str, Enum):
    """Status for API methods"""
    ON = "on"
    OFF = "off"


class ExportMediaType(str, Enum):
    """Supported media types for export endpoints"""
    JSON = "application/json"
    CSV = "text/csv"
    XML = "application/xml"
    OCTET_STREAM = "application/octet-stream"


# Activity Types and Groups
class ActivityTypeColors(BaseOFSResponse):
    """Color scheme configuration for activity types"""

    cancelled: Annotated[Optional[str], Field(alias="cancelled")]
    completed: Annotated[Optional[str], Field(alias="completed")]
    notdone: Annotated[Optional[str], Field(alias="notdone")]
    notOrdered: Annotated[Optional[str], Field(alias="notOrdered")]
    pending: Annotated[Optional[str], Field(alias="pending")]
    started: Annotated[Optional[str], Field(alias="started")]
    suspended: Annotated[Optional[str], Field(alias="suspended")]
    warning: Annotated[Optional[str], Field(alias="warning")]
    enroute: Annotated[Optional[str], Field(alias="enroute")]


class ActivityTypeFeatures(BaseOFSResponse):
    """Feature flags and capabilities for activity types"""

    model_config = ConfigDict(extra="allow")  # Activity Types Features
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


class ActivityTypeTimeSlots(BaseOFSResponse):
    """Time slot configuration for activity types"""

    label: str


class ActivityType(BaseOFSResponse):
    """Activity type definition with features and configuration"""

    active: bool
    colors: Optional[ActivityTypeColors]
    defaultDuration: int
    features: Optional[ActivityTypeFeatures]
    groupLabel: Optional[str]
    label: str
    name: str
    segmentMaxDuration: Optional[int] = None
    segmentMinDuration: Optional[int] = None
    timeSlots: Optional[List[ActivityTypeTimeSlots]] = None
    translations: TranslationList


class ActivityTypeListResponse(OFSResponseList[ActivityType]):
    """Paginated response for activity type lists"""

    pass


class ActivityTypeGroupItem(BaseModel):
    """Item representing an activity type in a group"""

    label: str


class ActivityTypeGroup(BaseOFSResponse):
    """Activity type group for organization and categorization"""

    label: str
    name: str
    activityTypes: list[ActivityTypeGroupItem] = []
    translations: Optional[TranslationList] = None


class ActivityTypeGroupListResponse(OFSResponseList[ActivityTypeGroup]):
    """Paginated response for activity type group lists"""

    pass


class ActivityTypeGroupRequest(BaseModel):
    """Request model for creating or updating activity type groups.
    
    DEPRECATED: This model is no longer used by the create_or_replace_activity_type_group
    method, which now takes label and optional translations directly.
    """

    name: str = Field(min_length=1, max_length=255, description="Display name of the activity type group")
    activityTypes: Optional[List[ActivityTypeGroupItem]] = Field(
        default=None, description="List of activity types to include in the group"
    )
    translations: Optional[TranslationList] = Field(
        default=None, description="Multi-language translations for the group name"
    )

    @model_validator(mode='after')
    def ensure_translations(self):
        """Auto-generate default English translation from name if no translations provided."""
        if not self.translations or (self.translations and len(self.translations.root) == 0):
            # Generate default English translation from name
            default_translation = Translation(
                language="en",
                name=self.name,
                languageISO="en-US"
            )
            self.translations = TranslationList([default_translation])
        return self


# Applications
class ApplicationsResourcestoAllow(BaseOFSResponse):
    """Resource access configuration for applications"""

    userType: str
    resourceTypes: List[str]


class Application(BaseOFSResponse):
    """Application definition and configuration"""

    # TODO: Improve the model
    model_config = ConfigDict(extra="allow")  # Applications
    label: str
    name: str
    activityTypes: List[str] = []
    resourceTypes: List[str] = []
    resourcesAllowed: List[ApplicationsResourcestoAllow] = []
    defaultApplication: bool = False


class ApplicationListResponse(OFSResponseList[Application]):
    """Paginated response for application lists"""

    pass


# Application API Access Models
class ApplicationApiAccessMethod(BaseOFSResponse):
    """API method configuration for capacity API"""
    
    label: str = Field(min_length=1, max_length=80)
    status: ApiMethodStatus


class ApplicationApiAccessEntity(BaseOFSResponse):
    """API entity configuration for core/metadata APIs"""
    
    label: str = Field(min_length=1, max_length=80)
    access: ApiAccessVisibility


class ApplicationApiAccessContext(BaseOFSResponse):
    """Field visibility configuration for inbound API"""
    
    label: str = Field(min_length=1, max_length=255)
    visibilities: Optional[List[Dict[str, Any]]] = []
    valuesVisibility: Optional[List[Dict[str, Any]]] = []


class ApplicationApiAccess(BaseOFSResponse):
    """Individual API access configuration for an application"""
    
    label: str = Field(min_length=1, max_length=255)
    name: str = Field(min_length=1, max_length=255)
    status: ApiAccessStatus
    links: Optional[List[Link]] = []
    
    # Optional detailed configuration (present in individual access endpoint)
    apiMethods: Optional[List[ApplicationApiAccessMethod]] = []
    apiEntities: Optional[List[ApplicationApiAccessEntity]] = []
    activityFields: Optional[List[ApplicationApiAccessContext]] = []
    inventoryFields: Optional[List[ApplicationApiAccessContext]] = []
    providerFields: Optional[List[ApplicationApiAccessContext]] = []
    userFields: Optional[List[Dict[str, Any]]] = []  # Complex nested structure
    requestFields: Optional[List[ApplicationApiAccessContext]] = []


class ApplicationApiAccessListResponse(OFSResponseList[ApplicationApiAccess]):
    """Response for application API access list endpoint (ID 10)"""
    
    pass


# Conditions (used by Work Skills)
class Condition(BaseOFSResponse):
    """Condition definition for work skill requirements"""

    label: str
    function: str
    value: Any = None
    valueList: list = []
    last_updated_by: Optional[str] = None
    last_update_date: Optional[str] = None
    last_update_login: Optional[str] = None
    created_by: Optional[str] = None
    creation_date: Optional[str] = None


# Enumeration Values
class EnumerationValue(BaseOFSResponse):
    """Enumeration value for dropdown and selection fields"""

    label: str
    name: Optional[str] = None  # Not present in API response, derived from translations
    translations: Optional[TranslationList] = None
    active: bool = True


class EnumerationValueList(OFSResponseList[EnumerationValue]):
    """Paginated response for enumeration value lists"""

    pass


# Inventory Types
class InventoryType(BaseOFSResponse):
    """Inventory type definition and configuration"""

    label: str
    name: str
    active: bool = True
    translations: Annotated[TranslationList, Field(validate_default=True)] = (
        TranslationList([])
    )
    modelProperty: Optional[str] = None
    nonSerialized: bool = False
    quantityPrecision: Optional[int] = None
    unitOfMeasurement: Optional[str] = None


class InventoryTypeListResponse(OFSResponseList[InventoryType]):
    """Paginated response for inventory type lists"""

    pass


# Organizations
class Organization(BaseOFSResponse):
    """Organization definition and hierarchy"""

    label: str
    name: str
    type: str
    translations: Annotated[TranslationList, Field(validate_default=True)] = (
        TranslationList([])
    )


class OrganizationListResponse(OFSResponseList[Organization]):
    """Paginated response for organization lists"""

    pass


# Properties
class PropertyRequest(BaseModel):
    """Request model for creating or updating properties"""
    
    label: str
    name: str
    type: str
    entity: Optional[EntityEnum] = None
    gui: Optional[str] = None
    translations: Optional[TranslationList] = None

    @field_validator("type")
    @classmethod
    def type_match(cls, v):
        if v not in [
            "field",
            "integer", 
            "string",
            "enumeration",
            "file",
            "attachments",
        ]:
            raise ValueError(f"{v} is not a valid property type")
        return v

    @field_validator("gui")
    @classmethod
    def gui_match(cls, v):
        if v is not None and v not in [
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
        ]:
            raise ValueError(f"{v} is not a valid GUI value")
        return v


class PropertyResponse(BaseOFSResponse):
    """Property definition for custom fields and attributes"""

    # TODO - Add validation for combinations of entity and type for extra validation

    label: str
    name: str
    type: str
    entity: Optional[EntityEnum] = None
    gui: Optional[str] = None
    translations: Annotated[TranslationList, Field(validate_default=True)] = (
        TranslationList([])
    )
    links: Optional[List[Link]] = None

    @field_validator("type")
    @classmethod
    def type_match(cls, v):
        if v not in [
            "field",
            "integer",
            "string",
            "enumeration",
            "file",
            "attachments",
        ]:
            raise ValueError(f"{v} is not a valid property type")
        return v

    @field_validator("translations")
    @classmethod
    def set_default(cls, field_value, info):
        return field_value or []

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
        ]:
            raise ValueError(f"{v} is not a valid GUI value")
        return v

    model_config = ConfigDict(extra="allow")  # Properties


class PropertyListResponse(OFSResponseList[PropertyResponse]):
    """Paginated response for property lists"""

    pass


# Resource Types
class ResourceType(BaseOFSResponse):
    """Resource type definition and configuration"""

    label: str
    name: str
    active: bool
    role: str
    translations: Annotated[TranslationList, Field(validate_default=True)] = (
        TranslationList([])
    )


class ResourceTypeListResponse(OFSResponseList[ResourceType]):
    """Paginated response for resource type lists"""

    pass


# Time Slots
class TimeSlot(BaseOFSResponse):
    """Time slot definition with start/end times and all-day support"""

    label: str
    name: str
    active: bool = True
    isAllDay: bool = False
    timeStart: Optional[str] = None
    timeEnd: Optional[str] = None


class TimeSlotListResponse(OFSResponseList[TimeSlot]):
    """Paginated response for time slot lists"""

    pass


# Work Skills
class Workskill(BaseOFSResponse):
    """Work skill definition with internationalization support"""

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


class WorkskillListResponse(OFSResponseList[Workskill]):
    """Paginated response for work skill lists"""

    pass


class WorkskillCondition(BaseOFSResponse):
    """Work skill condition with requirements and dependencies"""

    internalId: int
    label: str
    requiredLevel: int
    preferableLevel: int
    conditions: Optional[List[Condition]] = None
    dependencies: Optional[Any] = None


class WorkskillConditionListResponse(OFSResponseList[WorkskillCondition]):
    """Paginated response for work skill condition lists"""

    pass


# Work Skill Groups
class WorksSkillAssignments(BaseOFSResponse):
    """Work skill assignment configuration"""

    workSkillLabel: str
    level: int


class WorkSkillGroup(BaseOFSResponse):
    """Work skill group definition and assignments"""

    label: str
    name: str
    workSkills: List[WorksSkillAssignments] = []
    addToCapacityCategory: bool = False
    assignToResource: bool = False
    translations: Annotated[Optional[TranslationList], Field(validate_default=True)] = (
        TranslationList([])  # Default to empty list if not provided
    )
    active: bool = True


class WorkSkillGroupListResponse(OFSResponseList[WorkSkillGroup]):
    """Paginated response for work skill group lists"""

    pass


# Work Zones
class Workzone(BaseOFSResponse):
    """Work zone definition with geographical boundaries"""

    workZoneName: str
    workZoneLabel: str
    status: str
    travelArea: str
    keys: Optional[List[Any]]
    shapes: Optional[List[Any]] = []


class WorkzoneListResponse(OFSResponseList[Workzone]):
    """Paginated response for work zone lists"""

    pass


# Work Zone Key Configuration
class WorkZoneKeyField(BaseOFSResponse):
    """Work zone key field definition"""

    label: str = Field(description="Field label identifier")
    length: int = Field(description="Maximum length for this field")
    function: str = Field(description="Function applied to the field (e.g., 'caseInsensitive')")
    order: int = Field(description="Order of this field in the key")
    apiParameterName: str = Field(description="API parameter name for this field")


class WorkZoneKeyResponse(BaseOFSResponse):
    """Work zone key configuration response"""

    current: List[WorkZoneKeyField] = Field(default=[], description="Current work zone key fields")
    pending: List[WorkZoneKeyField] = Field(default=[], description="Pending work zone key fields")
    links: Optional[List[Link]] = Field(default=[], description="Related links")


# Languages
class Language(BaseOFSResponse):
    """Language metadata and configuration"""

    label: str
    code: str
    name: str
    active: bool
    translations: Optional[TranslationList] = []


class LanguageListResponse(OFSResponseList[Language]):
    """Paginated response for language lists"""

    pass


# Non-Working Reasons
class NonWorkingReason(BaseOFSResponse):
    """Non-working reason metadata"""

    label: str
    name: str
    active: bool
    translations: Optional[TranslationList] = []


class NonWorkingReasonListResponse(OFSResponseList[NonWorkingReason]):
    """Paginated response for non-working reason lists"""

    pass


# Shifts
class Shift(BaseOFSResponse):
    """Shift metadata and configuration"""

    label: str
    name: str
    active: bool
    type: str
    points: Optional[int] = None
    workTimeStart: Optional[str] = None
    workTimeEnd: Optional[str] = None
    links: Optional[List[Link]] = []


class ShiftListResponse(OFSResponseList[Shift]):
    """Paginated response for shift lists"""

    pass


# Forms
class Form(BaseOFSResponse):
    """Form metadata and configuration"""

    label: str
    name: str
    translations: Optional[TranslationList] = []
    links: Optional[List[Link]] = []
    content: Optional[str] = None  # Individual form endpoint includes full form content


class FormListResponse(OFSResponseList[Form]):
    """Paginated response for form lists"""

    pass


# Link Templates
class LinkTemplateTranslation(BaseOFSResponse):
    """Translation for link template names"""

    language: str
    name: str
    reverseName: Optional[str] = None  # Not all templates have reverse names


class LinkTemplate(BaseOFSResponse):
    """Link template metadata and configuration"""

    label: str
    reverseLabel: Optional[str] = None  # Not all templates have reverse labels
    active: bool
    linkType: Optional[str] = None  # Some templates don't have link types
    minInterval: Optional[str] = None  # Some templates don't have intervals
    maxInterval: Optional[str] = None
    minIntervalValue: Optional[int] = None
    maxIntervalValue: Optional[int] = None
    translations: Optional[List[LinkTemplateTranslation]] = []
    links: Optional[List[Link]] = []


class LinkTemplateListResponse(OFSResponseList[LinkTemplate]):
    """Paginated response for link template lists"""

    pass


# Routing Profiles
class RoutingProfile(BaseOFSResponse):
    """Routing profile metadata"""

    profileLabel: str


class RoutingProfileListResponse(OFSResponseList[RoutingProfile]):
    """Paginated response for routing profile lists"""

    pass


# Routing Plans
class RoutingPlan(BaseOFSResponse):
    """Routing plan metadata for a routing profile"""

    planLabel: str


class RoutingPlanListResponse(OFSResponseList[RoutingPlan]):
    """Paginated response for routing plan lists"""

    pass


# Routing Plan Export
class RoutingPlanExportResponse(BaseOFSResponse):
    """Response for routing plan export endpoint with download information or actual data"""

    # For export metadata response (without Accept header)
    mediaType: Optional[str] = Field(default=None, description="MIME type of the exported content")
    links: Optional[List[Link]] = Field(default=[], description="Download links for the exported content")
    
    # For actual routing plan data response (with Accept header)
    routing_plan: Optional[Dict[str, Any]] = Field(default=None, description="Actual routing plan configuration")
    sign: Optional[str] = Field(default=None, description="Digital signature for the routing plan")
    version: Optional[str] = Field(default=None, description="Version of the routing plan format")
    
    model_config = ConfigDict(extra="allow")  # Allow additional fields for complex routing plan data


