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

from typing import TYPE_CHECKING, Any, List, Optional

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr, RootModel, field_validator
from typing_extensions import Annotated

from .base import BaseOFSResponse, EntityEnum, OFSResponseList, SharingEnum, Translation, TranslationList

if TYPE_CHECKING:
    import httpx


# Common models
class Link(BaseOFSResponse):
    """Hyperlink reference for API resources"""
    rel: str
    href: str
    mediaType: Optional[str] = None


# Work Skills
class Workskill(BaseOFSResponse):
    """Work skill definition with internationalization support"""
    label: str
    active: bool = True
    name: str = ""
    sharing: SharingEnum
    translations: Annotated[Optional[TranslationList], Field(validate_default=True)] = None
    links: Optional[List[Link]] = None
    
    model_config = ConfigDict(extra="allow")

    @field_validator("translations")
    def set_default(cls, field_value, values):
        return field_value or TranslationList(
            [Translation(name=values.data.get("name"))]
        )


class WorkskillList(RootModel[List[Workskill]]):
    """List of work skills"""
    
    _raw_response: Optional['httpx.Response'] = PrivateAttr(default=None)
    
    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]
    
    @classmethod
    def from_response(cls, response: 'httpx.Response'):
        """Create instance from httpx response."""
        instance = cls.model_validate(response.json())
        instance._raw_response = response
        return instance
    
    @property
    def raw_response(self) -> Optional['httpx.Response']:
        """Access the raw httpx response object."""
        return self._raw_response


class Condition(BaseOFSResponse):
    """Condition definition for work skill requirements"""
    label: str
    function: str
    value: Any = None
    valueList: list = []


class WorkskillCondition(BaseOFSResponse):
    """Work skill condition with requirements and dependencies"""
    internalId: int
    label: str
    requiredLevel: int
    preferableLevel: int
    conditions: List[Condition]
    dependencies: Any = None


class WorskillConditionList(RootModel[List[WorkskillCondition]]):
    """List of work skill conditions"""
    
    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]


# Work Zones
class Workzone(BaseOFSResponse):
    """Work zone definition with geographical boundaries"""
    workZoneLabel: str
    workZoneName: str
    status: str
    travelArea: str
    keys: List[Any]


class WorkzoneList(RootModel[List[Workzone]]):
    """List of work zones"""
    
    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]


# Properties
class Property(BaseOFSResponse):
    """Property definition for custom fields and attributes"""
    label: str
    name: str
    type: str
    entity: Optional[EntityEnum] = None
    gui: Optional[str] = None
    translations: Annotated[TranslationList, Field(validate_default=True)] = []
    links: Optional[List[Link]] = None

    @field_validator("translations")
    def set_default(cls, field_value, values):
        return field_value or [Translation(name=values.name)]

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

    model_config = ConfigDict(extra="allow")


class PropertyList(RootModel[List[Property]]):
    """List of properties"""
    
    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]


# Resource Types
class ResourceType(BaseOFSResponse):
    """Resource type definition and configuration"""
    label: str
    name: str
    features: Optional[dict] = None
    
    model_config = ConfigDict(extra="allow")


class ResourceTypeList(RootModel[List[ResourceType]]):
    """List of resource types"""
    
    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]


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


class ActivityTypeFeatures(BaseOFSResponse):
    """Feature flags and capabilities for activity types"""
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
    links: Optional[List[Link]] = None
    
    model_config = ConfigDict(extra="allow")


class ActivityTypeList(RootModel[List[ActivityType]]):
    """List of activity types"""
    
    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]


class ActivityTypeListResponse(OFSResponseList[ActivityType]):
    """Paginated response for activity type lists"""
    pass


class ActivityTypeGroup(BaseOFSResponse):
    """Activity type group for organization and categorization"""
    label: str
    name: str
    active: bool
    translations: Optional[TranslationList] = None


class ActivityTypeGroupList(RootModel[List[ActivityTypeGroup]]):
    """List of activity type groups"""
    
    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]


class ActivityTypeGroupListResponse(OFSResponseList[ActivityTypeGroup]):
    """Paginated response for activity type group lists"""
    pass


# Inventory Types
class InventoryType(BaseOFSResponse):
    """Inventory type definition and configuration"""
    internalId: Optional[int] = None
    label: str
    name: str
    trackingRequired: bool = False
    quantityRequired: bool = False
    unitOfMeasure: Optional[str] = None
    minimumQuantity: Optional[int] = None
    minimumInternalQuantity: Optional[int] = None
    minimumModelInternalQuantity: Optional[int] = None
    minimumModelQuantity: Optional[int] = None
    maximumQuantity: Optional[int] = None
    
    model_config = ConfigDict(extra="allow")


class InventoryTypeList(RootModel[List[InventoryType]]):
    """List of inventory types"""
    
    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]


class InventoryTypeListResponse(OFSResponseList[InventoryType]):
    """Paginated response for inventory type lists"""
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
    assignedWorkSkills: List[WorksSkillAssignments] = []
    active: bool = True
    
    model_config = ConfigDict(extra="allow")


class WorkSkillAssignmentsList(RootModel[List[WorksSkillAssignments]]):
    """List of work skill assignments"""
    
    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]


class WorkSkillGroupList(RootModel[List[WorkSkillGroup]]):
    """List of work skill groups"""
    
    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]


class WorkSkillGroupListResponse(OFSResponseList[WorkSkillGroup]):
    """Paginated response for work skill group lists"""
    pass


# Enumeration Values
class EnumerationValue(BaseOFSResponse):
    """Enumeration value for dropdown and selection fields"""
    label: str
    name: str
    translations: Optional[TranslationList] = None
    active: bool = True


class EnumerationValueList(OFSResponseList[EnumerationValue]):
    """Paginated response for enumeration value lists"""
    pass


# Applications
class ApplicationsResourcestoAllow(BaseOFSResponse):
    """Resource access configuration for applications"""
    userType: str
    resourceTypes: List[str]


class Application(BaseOFSResponse):
    """Application definition and configuration"""
    label: str
    name: str
    activityTypes: List[str] = []
    resourceTypes: List[str] = []
    resourcesAllowed: List[ApplicationsResourcestoAllow] = []
    defaultApplication: bool = False


class ApplicationListResponse(OFSResponseList[Application]):
    """Paginated response for application lists"""
    pass


# Organizations
class Organization(BaseOFSResponse):
    """Organization definition and hierarchy"""
    label: str
    name: str
    parentLabel: Optional[str] = None
    status: str = "active"
    organizationType: Optional[str] = None
    
    model_config = ConfigDict(extra="allow")


class OrganizationList(RootModel[List[Organization]]):
    """List of organizations"""
    
    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]


class OrganizationListResponse(OFSResponseList[Organization]):
    """Paginated response for organization lists"""
    pass