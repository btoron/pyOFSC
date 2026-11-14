"""Service request models for OFSC Core API."""

import datetime
from typing import Optional, Union

from pydantic import BaseModel, ConfigDict


class ServiceRequest(BaseModel):
    """Service request returned by OFSC. Custom properties are kept as extra fields."""

    requestId: Optional[int] = None
    resourceId: Optional[str] = None
    resourceInternalId: Optional[int] = None
    activityId: Optional[int] = None
    inventoryId: Optional[int] = None
    date: Optional[str] = None
    created: Optional[str] = None
    requestType: Optional[str] = None
    model_config = ConfigDict(extra="allow")


class ServiceRequestCreate(BaseModel):
    """Body for creating a service request.

    Exactly one of activityId, resourceId or inventoryId must be provided.
    Custom properties may be supplied as extra fields.
    """

    activityId: Optional[int] = None
    resourceId: Optional[str] = None
    inventoryId: Optional[int] = None
    date: Optional[Union[datetime.date, str]] = None
    requestType: Optional[str] = None
    model_config = ConfigDict(extra="allow")
