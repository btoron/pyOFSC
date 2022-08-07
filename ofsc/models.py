import base64
import typing
from enum import Enum
from functools import lru_cache
from typing import Any, List

from pydantic import BaseModel, validator


class OFSConfig(BaseModel):
    baseURL: str
    clientID: str
    secret: str
    companyName: str

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


class TranslationEnum(str, Enum):
    en: "en"
    es: "es"
    pt: "pt"


class Translation(BaseModel):
    language: TranslationEnum = "en"
    name: str


class Workskill(BaseModel):
    label: str
    active: bool = True
    name: str = ""
    sharing: SharingEnum
    translations: List[Translation] = []

    @validator("translations", always=True)
    def set_default(cls, field_value, values):
        return field_value or [Translation(name=values["name"])]


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
