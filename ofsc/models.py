import base64
from enum import Enum
from typing import Any, List, Optional
from urllib.parse import urljoin

import requests
from cachetools import TTLCache, cached
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    RootModel,
    ValidationInfo,
    field_validator,
)
from pydantic_settings import BaseSettings
from typing_extensions import Annotated

from ofsc.common import FULL_RESPONSE, JSON_RESPONSE, wrap_return


class OFSConfig(BaseModel):
    clientID: str
    secret: str
    companyName: str
    useToken: bool = False
    root: Optional[str] = None
    baseURL: Optional[str] = None

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
    ofs_dynamic_scope: Optional[str] = None


class OFSApi:
    def __init__(self, config: OFSConfig) -> None:
        self._config = config

    @property
    def config(self):
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
        if auth.grant_type == "client_credentials":
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

    @property
    def headers(self):
        self._headers = {}
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


WorkskillList = RootModel[List[Workskill]]


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


WorskillConditionList = RootModel[List[WorkskillCondition]]


# Workzones
class Workzone(BaseModel):
    workZoneLabel: str
    workZoneName: str
    status: str
    travelArea: str
    keys: List[Any]


WorkzoneList = RootModel[List[Workzone]]


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

    model_config = ConfigDict(extra="allow")


PropertyList = RootModel[List[Property]]


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


ResourceList = RootModel[List[Resource]]


class ResourceType(BaseModel):
    label: str
    name: str
    active: bool
    role: str  # TODO: change to enum
    model_config = ConfigDict(extra="allow")


ResourceTypeList = RootModel[List[ResourceType]]


# Core / Activities
class BulkUpdateActivityItem(BaseModel):
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
