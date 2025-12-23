"""Async version of OFSCore API module."""

from datetime import date
from typing import Optional

import httpx

from ..models import (
    Activity,
    AssignedLocationsResponse,
    BulkUpdateRequest,
    CalendarView,
    DailyExtractFiles,
    DailyExtractFolders,
    Location,
    LocationListResponse,
    OFSConfig,
    OFSResponseList,
    ResourceUsersListResponse,
    ResourceWorkScheduleItem,
    ResourceWorkScheduleResponse,
)


class AsyncOFSCore:
    """Async version of OFSCore API module."""

    def __init__(self, config: OFSConfig, client: httpx.AsyncClient):
        self._config = config
        self._client = client

    @property
    def config(self) -> OFSConfig:
        return self._config

    @property
    def baseUrl(self) -> str:
        return self._config.baseURL

    @property
    def headers(self) -> dict:
        """Build authorization headers."""
        headers = {"Content-Type": "application/json;charset=UTF-8"}
        if not self._config.useToken:
            headers["Authorization"] = "Basic " + self._config.basicAuthString.decode(
                "utf-8"
            )
        else:
            raise NotImplementedError("Token-based auth not yet implemented for async")
        return headers

    # region Activities

    async def get_activities(self, params: dict):
        raise NotImplementedError("Async method not yet implemented")

    async def get_activity(self, activity_id: int):
        raise NotImplementedError("Async method not yet implemented")

    async def update_activity(self, activity_id: int, data):
        raise NotImplementedError("Async method not yet implemented")

    async def delete_activity(self, activity_id: int):
        raise NotImplementedError("Async method not yet implemented")

    async def search_activities(self, params: dict):
        raise NotImplementedError("Async method not yet implemented")

    async def move_activity(self, activity_id: int, data):
        raise NotImplementedError("Async method not yet implemented")

    async def bulk_update(self, data: BulkUpdateRequest):
        raise NotImplementedError("Async method not yet implemented")

    async def get_file_property(
        self,
        activityId: int,
        label: str,
        mediaType: str = "application/octet-stream",
    ):
        raise NotImplementedError("Async method not yet implemented")

    # endregion

    # region Events

    async def get_events(self, params: dict):
        raise NotImplementedError("Async method not yet implemented")

    # endregion

    # region Resources

    async def get_resource(
        self,
        resource_id: str,
        inventories: bool = False,
        workSkills: bool = False,
        workZones: bool = False,
        workSchedules: bool = False,
    ):
        raise NotImplementedError("Async method not yet implemented")

    async def create_resource(self, resourceId: str, data):
        raise NotImplementedError("Async method not yet implemented")

    async def create_resource_from_obj(self, resourceId: str, data: dict):
        raise NotImplementedError("Async method not yet implemented")

    async def update_resource(
        self, resourceId: str, data: dict, identify_by_internal_id: bool = False
    ):
        raise NotImplementedError("Async method not yet implemented")

    async def get_position_history(self, resource_id: str, date: str):
        raise NotImplementedError("Async method not yet implemented")

    async def get_resource_route(
        self,
        resource_id: str,
        date: str,
        activityFields: Optional[str] = None,
        offset: int = 0,
        limit: int = 100,
    ):
        raise NotImplementedError("Async method not yet implemented")

    async def get_resource_descendants(
        self,
        resource_id: str,
        resourceFields: Optional[str] = None,
        offset: int = 0,
        limit: int = 100,
        inventories: bool = False,
        workSkills: bool = False,
        workZones: bool = False,
        workSchedules: bool = False,
    ):
        raise NotImplementedError("Async method not yet implemented")

    async def get_resources(
        self,
        canBeTeamHolder: Optional[bool] = None,
        canParticipateInTeam: Optional[bool] = None,
        fields: Optional[list[str]] = None,
        offset: int = 0,
        limit: int = 100,
        inventories: bool = False,
        workSkills: bool = False,
        workZones: bool = False,
        workSchedules: bool = False,
    ):
        raise NotImplementedError("Async method not yet implemented")

    async def get_resource_users(self, resource_id: str) -> ResourceUsersListResponse:
        raise NotImplementedError("Async method not yet implemented")

    async def set_resource_users(self, *, resource_id: str, users: tuple[str, ...]):
        raise NotImplementedError("Async method not yet implemented")

    async def delete_resource_users(self, resource_id: str):
        raise NotImplementedError("Async method not yet implemented")

    async def get_resource_workschedules(
        self, resource_id: str, actualDate: date
    ) -> ResourceWorkScheduleResponse:
        raise NotImplementedError("Async method not yet implemented")

    async def set_resource_workschedules(
        self, resource_id: str, data: ResourceWorkScheduleItem
    ) -> ResourceWorkScheduleResponse:
        raise NotImplementedError("Async method not yet implemented")

    async def get_resource_calendar(
        self, resource_id: str, dateFrom: date, dateTo: date
    ) -> CalendarView:
        raise NotImplementedError("Async method not yet implemented")

    async def get_resource_inventories(self, resource_id: str):
        raise NotImplementedError("Async method not yet implemented")

    async def get_resource_assigned_locations(self, resource_id: str):
        raise NotImplementedError("Async method not yet implemented")

    async def get_resource_workzones(self, resource_id: str):
        raise NotImplementedError("Async method not yet implemented")

    async def get_resource_workskills(self, resource_id: str):
        raise NotImplementedError("Async method not yet implemented")

    async def bulk_update_resource_workzones(self, *, data):
        raise NotImplementedError("Async method not yet implemented")

    async def bulk_update_resource_workskills(self, *, data):
        raise NotImplementedError("Async method not yet implemented")

    async def bulk_update_resource_workschedules(self, *, data):
        raise NotImplementedError("Async method not yet implemented")

    async def get_resource_locations(self, resource_id: str) -> LocationListResponse:
        raise NotImplementedError("Async method not yet implemented")

    async def create_resource_location(
        self, resource_id: str, *, location: Location
    ) -> Location:
        raise NotImplementedError("Async method not yet implemented")

    async def delete_resource_location(self, resource_id: str, location_id: int):
        raise NotImplementedError("Async method not yet implemented")

    async def get_assigned_locations(
        self,
        resource_id: str,
        *,
        dateFrom: date = None,
        dateTo: date = None,
    ) -> AssignedLocationsResponse:
        raise NotImplementedError("Async method not yet implemented")

    async def set_assigned_locations(
        self, resource_id: str, data: AssignedLocationsResponse
    ) -> AssignedLocationsResponse:
        raise NotImplementedError("Async method not yet implemented")

    # endregion

    # region Users

    async def get_users(self, offset: int = 0, limit: int = 100):
        raise NotImplementedError("Async method not yet implemented")

    async def get_user(self, login: str):
        raise NotImplementedError("Async method not yet implemented")

    async def update_user(self, login: str, data):
        raise NotImplementedError("Async method not yet implemented")

    async def create_user(self, login: str, data):
        raise NotImplementedError("Async method not yet implemented")

    async def delete_user(self, login: str):
        raise NotImplementedError("Async method not yet implemented")

    # endregion

    # region Daily Extract

    async def get_daily_extract_dates(self) -> DailyExtractFolders:
        raise NotImplementedError("Async method not yet implemented")

    async def get_daily_extract_files(self, date: str) -> DailyExtractFiles:
        raise NotImplementedError("Async method not yet implemented")

    async def get_daily_extract_file(self, date: str, filename: str) -> bytes:
        raise NotImplementedError("Async method not yet implemented")

    # endregion

    # region Subscriptions

    async def get_subscriptions(self):
        raise NotImplementedError("Async method not yet implemented")

    async def create_subscription(self, data):
        raise NotImplementedError("Async method not yet implemented")

    async def delete_subscription(self, subscription_id: str):
        raise NotImplementedError("Async method not yet implemented")

    async def get_subscription_details(self, subscription_id: str):
        raise NotImplementedError("Async method not yet implemented")

    # endregion

    # region Helper Methods

    async def get_all_activities(
        self,
        *,
        root: Optional[str] = None,
        date_from: date = None,
        date_to: date = None,
        activity_fields: Optional[list[str]] = None,
        additional_fields: Optional[list[str]] = None,
        initial_offset: int = 0,
        include_non_scheduled: bool = False,
        limit: int = 5000,
    ) -> OFSResponseList[Activity]:
        raise NotImplementedError("Async method not yet implemented")

    async def get_all_properties(self, initial_offset: int = 0, limit: int = 100):
        raise NotImplementedError("Async method not yet implemented")

    # endregion
