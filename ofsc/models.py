import base64
import typing
from enum import Enum
from typing import Any, List, Optional
from urllib.parse import urljoin

import requests
from cachetools import TTLCache, cached
from pydantic import BaseModel, Extra, validator

from ofsc.common import FULL_RESPONSE, JSON_RESPONSE, wrap_return


class OFSConfig(BaseModel):
    clientID: str
    secret: str
    companyName: str
    useToken: bool = False
    root: Optional[str]
    baseURL: Optional[str]

    @property
    def basicAuthString(self):
        return base64.b64encode(
            bytes(self.clientID + "@" + self.companyName + ":" + self.secret, "utf-8")
        )

    class Config:
        validate_assignment = True

    @validator("baseURL")
    def set_base_URL(cls, url, values):
        print(values)
        return url or f"https://{values['companyName']}.fs.ocs.oraclecloud.com"


class OFSOAuthRequest(BaseModel):
    assertion: Optional[str]
    grant_type: str = "client_credentials"
    ofs_dynamic_scope: Optional[str]


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
            url, data=auth.dict(exclude_none=True), headers=headers
        )
        return response

    @property
    def headers(self):
        self._headers = {}
        if not self._config.useToken:
            self._headers[
                "Authorization"
            ] = "Basic " + self._config.basicAuthString.decode("utf-8")
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
    languageISO: Optional[str]


class TranslationList(BaseModel):
    __root__: List[Translation]

    def __iter__(self):
        return iter(self.__root__)

    def __getitem__(self, item):
        return self.__root__[item]


class Workskill(BaseModel):
    label: str
    active: bool = True
    name: str = ""
    sharing: SharingEnum
    translations: Optional[TranslationList]

    @validator("translations", always=True)
    def set_default(cls, field_value, values):
        return field_value or [Translation(name=values["name"])]


class WorkskillList(BaseModel):
    __root__: List[Workskill]

    def __iter__(self):
        return iter(self.__root__)

    def __getitem__(self, item):
        return self.__root__[item]


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
    dependencies: Any


class WorskillConditionList(BaseModel):
    __root__: List[WorkskillCondition]

    def __iter__(self):
        return iter(self.__root__)

    def __getitem__(self, item):
        return self.__root__[item]


# Workzones
class Workzone(BaseModel):
    workZoneLabel: str
    workZoneName: str
    status: str
    travelArea: str
    keys: List[Any]


class WorkzoneList(BaseModel):
    __root__: List[Workzone]

    def __iter__(self):
        return iter(self.__root__)

    def __getitem__(self, item):
        return self.__root__[item]


class Property(BaseModel):
    label: str
    name: str
    type: str
    entity: Optional[EntityEnum]
    gui: Optional[str]
    translations: TranslationList = []

    @validator("translations", always=True)
    def set_default(cls, field_value, values):
        return field_value or [Translation(name=values["name"])]

    @validator("gui")
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

    class Config:
        extra = Extra.allow  # or 'allow' str


class PropertyList(BaseModel):
    __root__: List[Property]

    def __iter__(self):
        return iter(self.__root__)

    def __getitem__(self, item):
        return self.__root__[item]


class Resource(BaseModel):
    resourceId: Optional[str]
    parentResourceId: Optional[str]
    resourceType: str
    name: str
    status: str = "active"
    organization: str = "default"
    language: str
    languageISO: Optional[str]
    timeZone: str
    timeFormat: str = "24-hour"
    dateFormat: str = "mm/dd/yy"
    email: Optional[str]
    phone: Optional[str]

    class Config:
        extra = Extra.allow  # or 'allow' str


class ResourceList(BaseModel):
    __root__: List[Resource]

    def __iter__(self):
        return iter(self.__root__)

    def __getitem__(self, item):
        return self.__root__[item]


class ResourceType(BaseModel):
    label: str
    name: str
    active: bool
    role: str  # TODO: change to enum

    class Config:
        extra = Extra.allow  # or 'allow' str


class ResourceTypeList(BaseModel):
    __root__: List[ResourceType]

    def __iter__(self):
        return iter(self.__root__)

    def __getitem__(self, item):
        return self.__root__[item]


# Core / Activities
class BulkUpdateActivityItem(BaseModel):
    activityId: Optional[int]
    activityType: Optional[str]
    date: Optional[str]

    class Config:
        extra = Extra.allow  # or 'allow' str


# CORE / BulkUpdaterequest


class BulkUpdateParameters(BaseModel):
    fallbackResource: Optional[str]
    identifyActivityBy: Optional[str]
    ifExistsThenDoNotUpdateFields: Optional[List[str]]
    ifInFinalStatusThen: Optional[str]
    inventoryPropertiesUpdateMode: Optional[str]


class BulkUpdateRequest(BaseModel):
    activities: List[BulkUpdateActivityItem]
    updateParameters: BulkUpdateParameters


class ActivityKeys(BaseModel):
    activityId: Optional[int]
    apptNumber: Optional[str]
    customerNumber: Optional[str]


class BulkUpdateError(BaseModel):
    errorDetail: Optional[str]
    operation: Optional[str]


class BulkUpdateWarning(BaseModel):
    code: Optional[int]
    message: Optional[int]


class BulkUpdateResult(BaseModel):
    activityKeys: Optional[ActivityKeys]
    errors: Optional[List[BulkUpdateError]]
    operationsFailed: Optional[List[str]]
    operationsPerformed: Optional[List[str]]
    warnings: Optional[List[BulkUpdateWarning]]


class BulkUpdateResponse(BaseModel):
    results: Optional[List[BulkUpdateResult]]
