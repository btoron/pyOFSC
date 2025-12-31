"""Async version of OFSCore API module."""

from datetime import date
from typing import Optional
from urllib.parse import urljoin

import httpx

from ..exceptions import (
    OFSCApiError,
    OFSCAuthenticationError,
    OFSCAuthorizationError,
    OFSCConflictError,
    OFSCNetworkError,
    OFSCNotFoundError,
    OFSCRateLimitError,
    OFSCServerError,
    OFSCValidationError,
)
from ..models import (
    Activity,
    ActivityCapacityCategoriesResponse,
    ActivityListResponse,
    AssignedLocationsResponse,
    BulkUpdateRequest,
    CalendarView,
    DailyExtractFiles,
    DailyExtractFolders,
    InventoryListResponse,
    LinkedActivitiesResponse,
    LinkedActivity,
    Location,
    LocationListResponse,
    OFSConfig,
    OFSResponseList,
    RequiredInventoriesResponse,
    ResourcePreferencesResponse,
    ResourceUsersListResponse,
    ResourceWorkScheduleItem,
    ResourceWorkScheduleResponse,
    SubmittedFormsResponse,
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

    def _parse_error_response(self, response: httpx.Response) -> dict:
        """Parse OFSC error response format.

        OFSC API returns errors in the format:
        {
            "type": "string",
            "title": "string",
            "detail": "string"
        }

        :param response: The httpx Response object
        :type response: httpx.Response
        :return: Error information with type, title, and detail keys
        :rtype: dict
        """
        try:
            error_data = response.json()
            return {
                "type": error_data.get("type", "about:blank"),
                "title": error_data.get("title", ""),
                "detail": error_data.get("detail", response.text),
            }
        except Exception:
            # If response is not JSON or doesn't match format
            return {
                "type": "about:blank",
                "title": f"HTTP {response.status_code}",
                "detail": response.text,
            }

    def _handle_http_error(self, e: httpx.HTTPStatusError, context: str = "") -> None:
        """Convert httpx exceptions to OFSC exceptions with error details.

        :param e: The httpx HTTPStatusError exception
        :type e: httpx.HTTPStatusError
        :param context: Additional context for the error message
        :type context: str
        :raises OFSCAuthenticationError: For 401 errors
        :raises OFSCAuthorizationError: For 403 errors
        :raises OFSCNotFoundError: For 404 errors
        :raises OFSCConflictError: For 409 errors
        :raises OFSCRateLimitError: For 429 errors
        :raises OFSCValidationError: For 400, 422 errors
        :raises OFSCServerError: For 5xx errors
        :raises OFSCApiError: For other HTTP errors
        """
        status = e.response.status_code
        error_info = self._parse_error_response(e.response)

        # Build message with detail
        message = (
            f"{context}: {error_info['detail']}" if context else error_info["detail"]
        )

        error_map = {
            401: OFSCAuthenticationError,
            403: OFSCAuthorizationError,
            404: OFSCNotFoundError,
            409: OFSCConflictError,
            429: OFSCRateLimitError,
        }

        if status in error_map:
            raise error_map[status](
                message,
                status_code=status,
                response=e.response,
                error_type=error_info["type"],
                title=error_info["title"],
                detail=error_info["detail"],
            ) from e
        elif 400 <= status < 500:
            raise OFSCValidationError(
                message,
                status_code=status,
                response=e.response,
                error_type=error_info["type"],
                title=error_info["title"],
                detail=error_info["detail"],
            ) from e
        elif 500 <= status < 600:
            raise OFSCServerError(
                message,
                status_code=status,
                response=e.response,
                error_type=error_info["type"],
                title=error_info["title"],
                detail=error_info["detail"],
            ) from e
        else:
            raise OFSCApiError(
                message,
                status_code=status,
                response=e.response,
                error_type=error_info["type"],
                title=error_info["title"],
                detail=error_info["detail"],
            ) from e

    # region Activities

    async def get_activities(
        self, params: dict, offset: int = 0, limit: int = 100
    ) -> ActivityListResponse:
        """Get activities list with filters and pagination.

        :param params: Query parameters (dateFrom, dateTo, resources, etc.)
        :type params: dict
        :param offset: Starting record number (default 0)
        :type offset: int
        :param limit: Maximum number to return (default 100)
        :type limit: int
        :return: List of activities with pagination info
        :rtype: ActivityListResponse
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCValidationError: If parameters are invalid (400)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        url = urljoin(self.baseUrl, "/rest/ofscCore/v1/activities")
        params = {**params, "offset": offset, "limit": limit}

        try:
            response = await self._client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()

            return ActivityListResponse.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, "Failed to get activities")
            raise  # This will never execute, but satisfies type checker
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def get_activity(self, activity_id: int) -> Activity:
        """Get a single activity by ID.

        :param activity_id: The unique identifier of the activity
        :type activity_id: int
        :return: Activity details
        :rtype: Activity
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCNotFoundError: If activity not found (404)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        url = urljoin(self.baseUrl, f"/rest/ofscCore/v1/activities/{activity_id}")

        try:
            response = await self._client.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()

            return Activity.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, f"Failed to get activity {activity_id}")
            raise  # This will never execute, but satisfies type checker
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

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

    async def get_capacity_categories(
        self, activity_id: int
    ) -> ActivityCapacityCategoriesResponse:
        """Get capacity categories for an activity.

        :param activity_id: The unique identifier of the activity
        :type activity_id: int
        :return: Capacity categories with totalResults
        :rtype: ActivityCapacityCategoriesResponse
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCNotFoundError: If activity not found (404)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        url = urljoin(
            self.baseUrl,
            f"/rest/ofscCore/v1/activities/{activity_id}/capacityCategories",
        )

        try:
            response = await self._client.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()

            return ActivityCapacityCategoriesResponse.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e, f"Failed to get capacity categories for activity {activity_id}"
            )
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def get_customer_inventories(
        self, activity_id: int, offset: int = 0, limit: int = 100
    ) -> InventoryListResponse:
        """Get customer inventories for an activity.

        :param activity_id: The unique identifier of the activity
        :type activity_id: int
        :param offset: Starting record number (default 0)
        :type offset: int
        :param limit: Maximum number to return (default 100)
        :type limit: int
        :return: List of customer inventories
        :rtype: InventoryListResponse
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCNotFoundError: If activity not found (404)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        url = urljoin(
            self.baseUrl,
            f"/rest/ofscCore/v1/activities/{activity_id}/customerInventories",
        )
        params = {"offset": offset, "limit": limit}

        try:
            response = await self._client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()

            return InventoryListResponse.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e, f"Failed to get customer inventories for activity {activity_id}"
            )
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def get_deinstalled_inventories(
        self, activity_id: int, offset: int = 0, limit: int = 100
    ) -> InventoryListResponse:
        """Get deinstalled inventories for an activity.

        :param activity_id: The unique identifier of the activity
        :type activity_id: int
        :param offset: Starting record number (default 0)
        :type offset: int
        :param limit: Maximum number to return (default 100)
        :type limit: int
        :return: List of deinstalled inventories
        :rtype: InventoryListResponse
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCNotFoundError: If activity not found (404)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        url = urljoin(
            self.baseUrl,
            f"/rest/ofscCore/v1/activities/{activity_id}/deinstalledInventories",
        )
        params = {"offset": offset, "limit": limit}

        try:
            response = await self._client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()

            return InventoryListResponse.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e, f"Failed to get deinstalled inventories for activity {activity_id}"
            )
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def get_file_property(
        self,
        activity_id: int,
        label: str,
        media_type: str = "application/octet-stream",
    ) -> bytes:
        """Get file property content for an activity.

        :param activity_id: The unique identifier of the activity
        :type activity_id: int
        :param label: The label of the file property
        :type label: str
        :param media_type: MIME type for Accept header (default: application/octet-stream)
        :type media_type: str
        :return: Binary file content
        :rtype: bytes
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCNotFoundError: If activity or file property not found (404)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        url = urljoin(
            self.baseUrl, f"/rest/ofscCore/v1/activities/{activity_id}/{label}"
        )
        headers = {**self.headers, "Accept": media_type}

        try:
            response = await self._client.get(url, headers=headers)
            response.raise_for_status()

            return response.content
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e, f"Failed to get file property {label} for activity {activity_id}"
            )
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def get_installed_inventories(
        self, activity_id: int, offset: int = 0, limit: int = 100
    ) -> InventoryListResponse:
        """Get installed inventories for an activity.

        :param activity_id: The unique identifier of the activity
        :type activity_id: int
        :param offset: Starting record number (default 0)
        :type offset: int
        :param limit: Maximum number to return (default 100)
        :type limit: int
        :return: List of installed inventories
        :rtype: InventoryListResponse
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCNotFoundError: If activity not found (404)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        url = urljoin(
            self.baseUrl,
            f"/rest/ofscCore/v1/activities/{activity_id}/installedInventories",
        )
        params = {"offset": offset, "limit": limit}

        try:
            response = await self._client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()

            return InventoryListResponse.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e, f"Failed to get installed inventories for activity {activity_id}"
            )
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def get_linked_activities(self, activity_id: int) -> LinkedActivitiesResponse:
        """Get linked activities for an activity.

        :param activity_id: The unique identifier of the activity
        :type activity_id: int
        :return: List of linked activities
        :rtype: LinkedActivitiesResponse
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCNotFoundError: If activity not found (404)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        url = urljoin(
            self.baseUrl, f"/rest/ofscCore/v1/activities/{activity_id}/linkedActivities"
        )

        try:
            response = await self._client.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()

            return LinkedActivitiesResponse.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e, f"Failed to get linked activities for activity {activity_id}"
            )
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def get_activity_link(
        self, activity_id: int, linked_activity_id: int, link_type: str
    ) -> LinkedActivity:
        """Get specific activity link details.

        :param activity_id: The unique identifier of the activity
        :type activity_id: int
        :param linked_activity_id: The unique identifier of the linked activity
        :type linked_activity_id: int
        :param link_type: The type of link
        :type link_type: str
        :return: Activity link details
        :rtype: LinkedActivity
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCNotFoundError: If activity or link not found (404)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        url = urljoin(
            self.baseUrl,
            f"/rest/ofscCore/v1/activities/{activity_id}/linkedActivities/{linked_activity_id}/linkTypes/{link_type}",
        )

        try:
            response = await self._client.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()

            return LinkedActivity.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e,
                f"Failed to get link {link_type} between activities {activity_id} and {linked_activity_id}",
            )
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def get_required_inventories(
        self, activity_id: int
    ) -> RequiredInventoriesResponse:
        """Get required inventories for an activity.

        :param activity_id: The unique identifier of the activity
        :type activity_id: int
        :return: List of required inventories
        :rtype: RequiredInventoriesResponse
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCNotFoundError: If activity not found (404)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        url = urljoin(
            self.baseUrl,
            f"/rest/ofscCore/v1/activities/{activity_id}/requiredInventories",
        )

        try:
            response = await self._client.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()

            return RequiredInventoriesResponse.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e, f"Failed to get required inventories for activity {activity_id}"
            )
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def get_resource_preferences(
        self, activity_id: int
    ) -> ResourcePreferencesResponse:
        """Get resource preferences for an activity.

        :param activity_id: The unique identifier of the activity
        :type activity_id: int
        :return: List of resource preferences
        :rtype: ResourcePreferencesResponse
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCNotFoundError: If activity not found (404)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        url = urljoin(
            self.baseUrl,
            f"/rest/ofscCore/v1/activities/{activity_id}/resourcePreferences",
        )

        try:
            response = await self._client.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()

            return ResourcePreferencesResponse.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e, f"Failed to get resource preferences for activity {activity_id}"
            )
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def get_submitted_forms(
        self, activity_id: int, offset: int = 0, limit: int = 100
    ) -> SubmittedFormsResponse:
        """Get submitted forms for an activity.

        :param activity_id: The unique identifier of the activity
        :type activity_id: int
        :param offset: Starting record number (default 0)
        :type offset: int
        :param limit: Maximum number to return (default 100)
        :type limit: int
        :return: List of submitted forms with pagination
        :rtype: SubmittedFormsResponse
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCNotFoundError: If activity not found (404)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        url = urljoin(
            self.baseUrl, f"/rest/ofscCore/v1/activities/{activity_id}/submittedForms"
        )
        params = {"offset": offset, "limit": limit}

        try:
            response = await self._client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()

            return SubmittedFormsResponse.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e, f"Failed to get submitted forms for activity {activity_id}"
            )
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

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
