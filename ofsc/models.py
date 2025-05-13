import base64
import logging
from datetime import date
from enum import Enum
from typing import Any, Dict, Generic, List, Optional, TypeVar
from urllib.parse import urljoin

import requests
from cachetools import TTLCache, cached
from pydantic import (
    AliasChoices,
    AnyHttpUrl,
    BaseModel,
    ConfigDict,
    Field,
    RootModel,
    ValidationInfo,
    field_validator,
    model_validator,
)
from typing_extensions import Annotated

from ofsc.common import FULL_RESPONSE, wrap_return

T = TypeVar("T")


class OFSResponseList(BaseModel, Generic[T]):
    model_config = ConfigDict(extra="allow")

    items: List[T] = []
    offset: Annotated[Optional[int], Field(alias="offset")] = None
    limit: Annotated[Optional[int], Field(alias="limit")] = None
    hasMore: Annotated[Optional[bool], Field(alias="hasMore")] = False
    totalResults: int = -1

    @model_validator(mode="after")
    def check_coherence(self):
        if self.totalResults != len(self.items) and self.hasMore is False:
            self.totalResults = len(self.items)
        return self

    def __len__(self):
        return len(self.items)

    def __iter__(self):
        return iter(self.items)

    def __getitem__(self, item):
        return self.items[item]

    def __contains__(self, item):
        return item in self.items

    def __next__(self):
        return next(self.items)


class OFSConfig(BaseModel):
    clientID: str
    secret: str
    companyName: str
    useToken: bool = False
    root: Optional[str] = None
    baseURL: Optional[str] = None
    auto_raise: bool = True
    auto_model: bool = True

    @property
    def basicAuthString(self):
        return base64.b64encode(
            bytes(self.clientID + "@" + self.companyName + ":" + self.secret, "utf-8")
        )

    model_config = ConfigDict(validate_assignment=True)

    @field_validator("baseURL")
    def set_base_URL(cls, url, info: ValidationInfo):
        return url or f"https://{info.data['companyName']}.fs.ocs.oraclecloud.com"


class OFSOAuthRequest(BaseModel):
    assertion: Optional[str] = None
    grant_type: str = "client_credentials"
    # ofs_dynamic_scope: Optional[str] = None


class OFSAPIError(BaseModel):
    type: str
    title: str
    status: int
    detail: str


class OFSApi:
    def __init__(self, config: OFSConfig) -> None:
        self._config = config

    @property
    def config(self) -> OFSConfig:
        return self._config

    @property
    def baseUrl(self):
        return self._config.baseURL

    @cached(
        cache=TTLCache(maxsize=1, ttl=3000)
    )  # Cache of token results for 50 minutes
    @wrap_return(response_type=FULL_RESPONSE, expected=[200])
    def token(self, auth: OFSOAuthRequest = OFSOAuthRequest()) -> requests.Response:
        headers = {}
        logging.info(f"Getting token with {auth.grant_type}")
        if (
            auth.grant_type == "client_credentials"
            or auth.grant_type == "urn:ietf:params:oauth:grant-type:jwt-bearer"
        ):
            headers["Authorization"] = "Basic " + self._config.basicAuthString.decode(
                "utf-8"
            )
        else:
            raise NotImplementedError(
                f"grant_type {auth.grant_type} not implemented yet"
            )
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        url = urljoin(self.baseUrl, "/rest/oauthTokenService/v2/token")
        response = requests.post(
            url, data=auth.model_dump(exclude_none=True), headers=headers
        )
        return response

    # Wrapper for requests not included in the standard methods
    def call(
        self, *, method: str, partialUrl: str, additionalHeaders: dict = {}, **kwargs
    ) -> requests.Response:
        headers = self.headers | additionalHeaders
        url = urljoin(self.baseUrl, partialUrl)
        headers = self.headers
        response = requests.request(method, url, headers=headers, **kwargs)
        return response

    @property
    def headers(self):
        self._headers = {}
        self._headers["Content-Type"] = "application/json;charset=UTF-8"

        if not self._config.useToken:
            self._headers["Authorization"] = (
                "Basic " + self._config.basicAuthString.decode("utf-8")
            )
        else:
            self._token = self.token().json()["access_token"]
            self._headers["Authorization"] = f"Bearer {self._token}"
            print(f"Not implemented {self._token}")
        return self._headers


class SharingEnum(str, Enum):
    no_sharing = "no sharing"
    maximal = "maximal"
    minimal = "minimal"
    summary = "summary"


class EntityEnum(str, Enum):
    activity = "activity"
    inventory = "inventory"
    resource = "resource"
    service_request = "service request"
    user = "user"


# class TranslationEnum(str, Enum):
#     en = "en"
#     es = "es"
#     pt = "pt"
#     fr = "fr"
#     br = "br"
#     el = "el"
#     cs = "cs"


# Work skills
class Translation(BaseModel):
    language: str = "en"
    name: str
    languageISO: Optional[str] = None


class TranslationList(RootModel[List[Translation]]):
    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]

    def map(self):
        return {translation.language: translation for translation in self.root}


class Workskill(BaseModel):
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


class WorkskillList(RootModel[List[Workskill]]):
    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]


class Condition(BaseModel):
    label: str
    function: str
    value: Any = None
    valueList: list = []


class WorkskillCondition(BaseModel):
    internalId: int
    label: str
    requiredLevel: int
    preferableLevel: int
    conditions: List[Condition]
    dependencies: Any = None


class WorskillConditionList(RootModel[List[WorkskillCondition]]):
    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]


# Workzones
class Workzone(BaseModel):
    workZoneLabel: str
    workZoneName: str
    status: str
    travelArea: str
    keys: List[Any]


class WorkzoneList(RootModel[List[Workzone]]):
    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]


class Property(BaseModel):
    label: str
    name: str
    type: str
    entity: Optional[EntityEnum] = None
    gui: Optional[str] = None
    translations: Annotated[TranslationList, Field(validate_default=True)] = []

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

    model_config = ConfigDict(extra="ignore")


class PropertyList(RootModel[List[Property]]):
    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]


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


class ResourceList(RootModel[List[Resource]]):
    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]


class ResourceType(BaseModel):
    label: str
    name: str
    active: bool
    role: str  # TODO: change to enum
    model_config = ConfigDict(extra="allow")


class ResourceTypeList(RootModel[List[ResourceType]]):
    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]


# Core / Activities
class Activity(BaseModel):
    activityId: Optional[int] = None
    activityType: Optional[str] = None
    date: Optional[str] = None
    model_config = ConfigDict(extra="allow")


class GetActivityRequest(BaseModel):
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
        return self
        if not self.includeNonScheduled:
            if self.dateFrom is None or self.dateTo is None:
                raise ValueError(
                    "dateFrom and dateTo are required when includeNonScheduled is False"
                )
        return self


class BulkUpdateActivityItem(Activity):
    activityId: Optional[int] = None
    activityType: Optional[str] = None
    date: Optional[str] = None
    model_config = ConfigDict(extra="allow")


# CORE / BulkUpdaterequest


class BulkUpdateParameters(BaseModel):
    fallbackResource: Optional[str] = None
    identifyActivityBy: Optional[str] = None
    ifExistsThenDoNotUpdateFields: Optional[List[str]] = None
    ifInFinalStatusThen: Optional[str] = None
    inventoryPropertiesUpdateMode: Optional[str] = None


class BulkUpdateRequest(BaseModel):
    activities: List[BulkUpdateActivityItem]
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
    errors: Optional[List[BulkUpdateError]] = None
    operationsFailed: Optional[List[str]] = None
    operationsPerformed: Optional[List[str]] = None
    warnings: Optional[List[BulkUpdateWarning]] = None


class BulkUpdateResponse(BaseModel):
    results: Optional[List[BulkUpdateResult]] = None


# region Activity Type Groups


class ActivityTypeGroup(BaseModel):
    label: str
    name: str
    _activityTypes: Annotated[Optional[List[dict]], "activityTypes"] = []
    translations: TranslationList

    @property
    def activityTypes(self):
        return [_activityType["label"] for _activityType in self._activityTypes]


class ActivityTypeGroupList(RootModel[List[ActivityTypeGroup]]):
    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]


class ActivityTypeGroupListResponse(OFSResponseList[ActivityTypeGroup]):
    pass


# endregion

# region Activity Types


class ActivityTypeColors(BaseModel):
    cancelled: Annotated[Optional[str], Field(alias="cancelled")]
    completed: Annotated[Optional[str], Field(alias="completed")]
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


class ActivityTypeList(RootModel[List[ActivityType]]):
    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]


class ActivityTypeListResponse(OFSResponseList[ActivityType]):
    pass


# endregion

# region Capacity Areas


class CapacityAreaParent(BaseModel):
    label: str
    name: Optional[str] = None


class CapacityAreaConfiguration(BaseModel):
    isTimeSlotBase: bool
    byCapacityCategory: str
    byDay: str
    byTimeSlot: str
    isAllowCloseOnWorkzoneLevel: bool
    definitionLevel: List[str]


class CapacityArea(BaseModel):
    label: str
    name: Optional[str] = None
    type: Optional[str] = "area"
    status: Optional[str] = "active"
    configuration: CapacityAreaConfiguration = None
    parentLabel: Optional[str] = None
    parent: Annotated[Optional[CapacityAreaParent], Field(alias="parent")] = None
    status: str
    translations: Annotated[Optional[TranslationList], Field(alias="translations")] = (
        None
    )
    # Note: as of 24A the additional fields returned are just HREFs so we won't include them here


class CapacityAreaList(RootModel[List[CapacityArea]]):
    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]


class CapacityAreaListResponse(OFSResponseList[CapacityArea]):
    pass


# endregion
# region 202403 Capacity Categories
class Item(BaseModel):
    label: str
    name: Optional[str] = None


class ItemList(RootModel[List[Item]]):
    def __iter__(self):
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


#  endregion

# region 202405 Inventory Types


class InventoryType(BaseModel):
    label: str
    translations: Annotated[Optional[TranslationList], Field(alias="translations")] = (
        None
    )
    active: bool = True
    model_property: Optional[str] = None
    non_serialized: bool = False
    quantityPrecision: Optional[int] = 0
    model_config = ConfigDict(extra="allow")


class InventoryTypeList(RootModel[List[InventoryType]]):
    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]


class InventoryTypeListResponse(OFSResponseList[InventoryType]):
    pass


# region 202404 Metadata - Time Slots
# endregion
# region 202404 Metadata - Workzones
# endregion

# region 202410 Work Skill Groups


class WorksSkillAssignments(BaseModel):
    label: str
    ratio: int = Field(gt=0, lt=101)
    model_config = ConfigDict(extra="forbid")


class WorkSkillAssignmentsList(RootModel[List[WorksSkillAssignments]]):
    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]


class WorkSkillGroup(BaseModel):
    label: str
    name: str
    active: bool
    assignToResource: bool
    addToCapacityCategory: bool
    workSkills: WorkSkillAssignmentsList
    translations: TranslationList
    model_config = ConfigDict(extra="ignore")


class WorkSkillGroupList(RootModel[List[WorkSkillGroup]]):
    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]


class WorkSkillGroupListResponse(OFSResponseList[WorkSkillGroup]):
    pass


# endregion
# region Users
class BaseUser(BaseModel):
    login: str


class ResourceUsersListResponse(OFSResponseList[BaseUser]):
    @property
    def users(self) -> List[str]:
        return [item.login for item in self.items]


class EnumerationValue(BaseModel):
    active: bool
    label: str
    translations: TranslationList

    @property
    def map(self):
        return {translation.language: translation for translation in self.translations}


class EnumerationValueList(OFSResponseList[EnumerationValue]):
    pass


# endregion
# region 202412 Applications


class ApplicationsResourcestoAllow(BaseModel):
    resourceId: str
    resourceInternalId: int


class Application(BaseModel):
    label: str
    name: str
    resourcesToAllow: List[ApplicationsResourcestoAllow] = None
    allowedCorsDomains: List[str] = None
    IPAddressesToAllow: List[str] = None
    status: str
    tokenService: str


class ApplicationListResponse(OFSResponseList[Application]):
    pass


class Organization(BaseModel):
    label: str
    name: str
    translations: TranslationList
    type: str


class OrganizationList(RootModel[List[Organization]]):
    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]


class OrganizationListResponse(OFSResponseList[Organization]):
    pass


# endregion
# region 202411 Calendars
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


class CalendarViewList(RootModel[List[CalendarViewItem]]):
    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]


class CalendarViewShift(BaseModel):
    regular: Optional[CalendarViewItem] = Field(default=None)
    on_call: Optional[CalendarViewItem] = Field(
        default=None, validation_alias=AliasChoices("onCall", "on-call")
    )


class CalendarView(RootModel[Dict[str, CalendarViewShift]]):
    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]


# endregion
# region 202503 ResourceWorkSchedule


class ResourceWorkScheduleItem(BaseModel):
    comments: Optional[str] = None
    endDate: Optional[date] = None
    isWorking: Optional[bool] = None
    nonWorkingReason: Optional[str] = None
    points: Optional[int] = None
    recordType: CalendarViewItemRecordType
    recurrence: Optional[Recurrence] = Recurrence(recurEvery=1, recurrenceType="daily")
    scheduleItemId: Optional[int] = None
    scheduleLabel: Optional[str] = None
    scheduleShifts: Optional[List[CalendarViewItem]] = None
    shiftLabel: Optional[str] = None
    shiftType: Optional[str] = None
    startDate: Optional[date] = date.today()
    workTimeEnd: Optional[str] = None
    workTimeStart: Optional[str] = None


class ResourceWorkScheduleResponseList(RootModel[List[ResourceWorkScheduleItem]]):
    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]


class ResourceWorkScheduleResponse(OFSResponseList[ResourceWorkScheduleItem]):
    pass


# endregion


# region 202504 Locations
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


class LocationList(RootModel[List[Location]]):
    def __iter__(self):
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


# endregion
# region 202505 Daily Extracts


class Link(BaseModel):
    href: AnyHttpUrl
    rel: str
    mediaType: Optional[str] = None


class DailyExtractItem(BaseModel):
    name: str
    bytes: Optional[int] = None
    mediaType: Optional[str] = None
    links: list[Link]


class DailyExtractItemList(BaseModel):
    items: list[DailyExtractItem] = []


class DailyExtractFolders(BaseModel):
    name: str = "folders"
    folders: Optional[DailyExtractItemList] = None


class DailyExtractFiles(BaseModel):
    name: str = "files"
    files: Optional[DailyExtractItemList] = None
