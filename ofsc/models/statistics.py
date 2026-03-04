"""Pydantic models for OFSC Statistics API."""

from typing import Optional

from pydantic import BaseModel, ConfigDict

from ._base import OFSResponseList


# region Statistics / Activity Duration Stats


class ActivityDurationStat(BaseModel):
    resourceId: Optional[str] = None
    akey: Optional[str] = None
    override: Optional[int] = None
    avg: Optional[int] = None
    dev: Optional[int] = None
    count: Optional[int] = None
    level: Optional[str] = None
    model_config = ConfigDict(extra="allow")


class ActivityDurationStatsList(OFSResponseList[ActivityDurationStat]):
    pass


# endregion


# region Statistics / Activity Travel Stats


class ActivityTravelStat(BaseModel):
    tkey: Optional[str] = None
    fkey: Optional[str] = None
    override: Optional[int] = None
    avg: Optional[int] = None
    dev: Optional[int] = None
    count: Optional[int] = None
    region: Optional[str] = None
    keyId: Optional[int] = None
    org: Optional[list[str]] = None
    model_config = ConfigDict(extra="allow")


class ActivityTravelStatsList(OFSResponseList[ActivityTravelStat]):
    pass


# endregion


# region Statistics / Airline Distance Based Travel


class AirlineDistanceData(BaseModel):
    distance: Optional[int] = None
    estimated: Optional[int] = None
    override: Optional[int] = None
    model_config = ConfigDict(extra="allow")


class AirlineDistanceBasedTravel(BaseModel):
    level: Optional[str] = None
    key: Optional[str] = None
    keyId: Optional[int] = None
    org: Optional[list[str]] = None
    data: list[AirlineDistanceData] = []
    model_config = ConfigDict(extra="allow")


class AirlineDistanceBasedTravelList(OFSResponseList[AirlineDistanceBasedTravel]):
    pass


# endregion
