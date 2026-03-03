"""User models for OFSC Core API."""

from typing import Optional

from pydantic import BaseModel, ConfigDict

from ._base import OFSResponseList


class User(BaseModel):
    """Full user response model."""

    model_config = ConfigDict(extra="allow")

    login: str
    name: Optional[str] = None
    userType: Optional[str] = None
    status: Optional[str] = None
    language: Optional[str] = None
    timeZone: Optional[str] = None
    timeZoneIANA: Optional[str] = None
    mainResourceId: Optional[str] = None
    resources: list[str] = []
    resourceInternalIds: list[int] = []
    dateFormat: Optional[str] = None
    longDateFormat: Optional[str] = None
    timeFormat: Optional[str] = None
    weekStart: Optional[str] = None
    selfAssignment: Optional[bool] = None
    passwordTemporary: Optional[bool] = None
    loginAttempts: Optional[int] = None
    createdTime: Optional[str] = None
    lastLoginTime: Optional[str] = None
    lastUpdatedTime: Optional[str] = None
    organizationalUnit: Optional[str] = None


class UserCreate(BaseModel):
    """User creation model enforcing required fields."""

    name: str
    userType: str
    language: str
    timeZone: str
    resources: list[str]
    password: str
    mainResourceId: Optional[str] = None
    status: Optional[str] = None
    dateFormat: Optional[str] = None
    timeFormat: Optional[str] = None
    weekStart: Optional[str] = None
    selfAssignment: Optional[bool] = None


class UserListResponse(OFSResponseList[User]):
    """Paginated list response for users."""

    pass


class CollaborationGroup(BaseModel):
    """A single collaboration group."""

    name: str


class CollaborationGroupsResponse(BaseModel):
    """Response containing a list of collaboration groups."""

    items: list[CollaborationGroup] = []

    def __iter__(self):  # type: ignore[override]
        return iter(self.items)

    def __getitem__(self, item):
        return self.items[item]

    def __len__(self):
        return len(self.items)
