import base64
import typing
from enum import Enum
from functools import lru_cache
from typing import Any, List, Optional

from pydantic import BaseModel, Extra, validator


class OFSConfig(BaseModel):
    baseURL: str
    clientID: str
    secret: str
    companyName: str
    root: Optional[str]

    @property
    def authString(self):
        return base64.b64encode(
            bytes(self.clientID + "@" + self.companyName + ":" + self.secret, "utf-8")
        )


class OFSApi:
    def __init__(self, config: OFSConfig) -> None:
        self._config = config
        self.headers = {}
        self.headers["Authorization"] = "Basic " + self._config.authString.decode(
            "utf-8"
        )

    @property
    def config(self):
        return self._config

    @property
    def baseUrl(self):
        return self._config.baseURL


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
