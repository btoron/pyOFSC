"""Inventory models for OFSC Core API."""

from typing import Optional

from pydantic import BaseModel, ConfigDict, model_validator


class RequiredInventory(BaseModel):
    """Required inventory item for an activity."""

    inventoryType: str
    model: str
    quantity: float


class RequiredInventoriesResponse(BaseModel):
    """Response for required inventories."""

    items: list[RequiredInventory] = []
    offset: Optional[int] = None
    limit: Optional[int] = None
    totalResults: Optional[int] = None


class Inventory(BaseModel):
    """Inventory item (customer, installed, or deinstalled)."""

    inventoryId: Optional[int] = None
    activityId: Optional[int] = None
    resourceId: Optional[str] = None
    inventoryType: Optional[str] = None
    status: Optional[str] = None  # customer, resource, installed, deinstalled
    quantity: Optional[float] = None
    serialNumber: Optional[str] = None
    model_config = ConfigDict(extra="allow")


class InventoryListResponse(BaseModel):
    """Response for inventory lists."""

    items: list[Inventory] = []
    offset: Optional[str | int] = None  # Can be string or int from API
    limit: Optional[str | int] = None  # Can be string or int from API
    totalResults: Optional[int] = None


class InventoryCreate(BaseModel):
    """Inventory creation model with required inventoryType and context."""

    inventoryType: str
    resourceId: Optional[str] = None
    resourceInternalId: Optional[int] = None
    activityId: Optional[int] = None
    status: Optional[str] = None
    serialNumber: Optional[str] = None
    quantity: Optional[float] = None
    model_config = ConfigDict(extra="allow")

    @model_validator(mode="after")
    def require_context(self):
        if not any([self.resourceId, self.resourceInternalId, self.activityId]):
            raise ValueError("At least one of 'resourceId', 'resourceInternalId', or 'activityId' must be set")
        return self


class InventoryCustomAction(BaseModel):
    """Body for inventory custom-action (install/deinstall/undo) operations."""

    activityId: Optional[int] = None
    quantity: Optional[float] = None
