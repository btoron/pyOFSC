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
    CalendarsListResponse,
    CreateSubscriptionRequest,
    DailyExtractFiles,
    DailyExtractFolders,
    EventListResponse,
    GetActivitiesParams,
    InventoryListResponse,
    LinkedActivitiesResponse,
    LinkedActivity,
    Location,
    LocationListResponse,
    OFSConfig,
    OFSResponseList,
    PositionHistoryResponse,
    RequiredInventoriesResponse,
    Resource,
    ResourceAssistantsResponse,
    ResourceListResponse,
    ResourcePlansResponse,
    ResourcePreferencesResponse,
    ResourceRouteResponse,
    ResourceUsersListResponse,
    ResourceWorkScheduleItem,
    ResourceWorkScheduleResponse,
    ResourceWorkskillListResponse,
    ResourceWorkzoneListResponse,
    SubmittedFormsResponse,
    Subscription,
    SubscriptionListResponse,
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
        self, params: GetActivitiesParams | dict, offset: int = 0, limit: int = 100
    ) -> ActivityListResponse:
        """Get activities list with filters and pagination.

        :param params: Query parameters (accepts GetActivitiesParams or dict)
        :type params: GetActivitiesParams | dict
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
        # Validate params through model
        if isinstance(params, dict):
            validated_params = GetActivitiesParams.model_validate(params)
        else:
            validated_params = params

        # Convert to API params and add pagination
        api_params = validated_params.to_api_params()
        api_params["offset"] = offset
        api_params["limit"] = limit

        url = urljoin(self.baseUrl, "/rest/ofscCore/v1/activities")

        try:
            response = await self._client.get(
                url, headers=self.headers, params=api_params
            )
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

    async def get_events(self, params: dict) -> EventListResponse:
        """Get events from subscriptions.

        Args:
            params: Query parameters (e.g., subscriptionId, since, offset, limit)

        Returns:
            EventListResponse: List of events

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        url = urljoin(self.baseUrl, "/rest/ofscCore/v1/events")

        try:
            response = await self._client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()

            return EventListResponse.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, "Failed to get events")
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    # endregion

    # region Resources

    def _build_expand_param(
        self,
        inventories: bool,
        workskills: bool,
        workzones: bool,
        workschedules: bool,
    ) -> str | None:
        """Build expand query parameter for resource requests."""
        parts = []
        if inventories:
            parts.append("inventories")
        if workskills:
            parts.append("workSkills")
        if workzones:
            parts.append("workZones")
        if workschedules:
            parts.append("workSchedules")
        return ",".join(parts) if parts else None

    async def get_assigned_locations(
        self,
        resource_id: str,
        date_from: date,
        date_to: date,
    ) -> AssignedLocationsResponse:
        """Get assigned locations for a resource."""
        url = urljoin(
            self.baseUrl, f"/rest/ofscCore/v1/resources/{resource_id}/assignedLocations"
        )
        params = {
            "dateFrom": date_from.isoformat(),
            "dateTo": date_to.isoformat(),
        }

        try:
            response = await self._client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()

            return AssignedLocationsResponse.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e, f"Failed to get assigned locations for resource '{resource_id}'"
            )
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def get_calendars(self) -> CalendarsListResponse:
        """Get all calendars."""
        url = urljoin(self.baseUrl, "/rest/ofscCore/v1/calendars")

        try:
            response = await self._client.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()

            if "links" in data:
                del data["links"]

            return CalendarsListResponse.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, "Failed to get calendars")
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def get_position_history(
        self, resource_id: str, position_date: date
    ) -> PositionHistoryResponse:
        """Get position history for a resource on a specific date."""
        url = urljoin(
            self.baseUrl, f"/rest/ofscCore/v1/resources/{resource_id}/positionHistory"
        )
        params = {"date": position_date.isoformat()}

        try:
            response = await self._client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()

            if "links" in data:
                del data["links"]

            return PositionHistoryResponse.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e, f"Failed to get position history for resource '{resource_id}'"
            )
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def get_resource(
        self,
        resource_id: str,
        expand_inventories: bool = False,
        expand_workskills: bool = False,
        expand_workzones: bool = False,
        expand_workschedules: bool = False,
    ) -> Resource:
        """Get a single resource by ID."""
        url = urljoin(self.baseUrl, f"/rest/ofscCore/v1/resources/{resource_id}")

        params = {}
        expand = self._build_expand_param(
            expand_inventories,
            expand_workskills,
            expand_workzones,
            expand_workschedules,
        )
        if expand:
            params["expand"] = expand

        try:
            response = await self._client.get(
                url, headers=self.headers, params=params if params else None
            )
            response.raise_for_status()
            data = response.json()

            return Resource.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, f"Failed to get resource '{resource_id}'")
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def get_resource_assistants(
        self, resource_id: str
    ) -> ResourceAssistantsResponse:
        """Get assistant resources."""
        url = urljoin(
            self.baseUrl, f"/rest/ofscCore/v1/resources/{resource_id}/assistants"
        )

        try:
            response = await self._client.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()

            if "links" in data:
                del data["links"]

            return ResourceAssistantsResponse.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e, f"Failed to get assistants for resource '{resource_id}'"
            )
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def get_resource_calendar(
        self, resource_id: str, date_from: date, date_to: date
    ) -> CalendarView:
        """Get calendar view for a resource."""
        url = urljoin(
            self.baseUrl,
            f"/rest/ofscCore/v1/resources/{resource_id}/workSchedules/calendarView",
        )
        params = {"dateFrom": date_from.isoformat(), "dateTo": date_to.isoformat()}

        try:
            response = await self._client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()

            if "links" in data:
                del data["links"]

            return CalendarView.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e, f"Failed to get calendar for resource '{resource_id}'"
            )
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def get_resource_children(
        self, resource_id: str, offset: int = 0, limit: int = 100
    ) -> ResourceListResponse:
        """Get child resources."""
        url = urljoin(
            self.baseUrl, f"/rest/ofscCore/v1/resources/{resource_id}/children"
        )
        params = {"offset": offset, "limit": limit}

        try:
            response = await self._client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()

            if "links" in data:
                del data["links"]

            return ResourceListResponse.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e, f"Failed to get children for resource '{resource_id}'"
            )
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def get_resource_descendants(
        self,
        resource_id: str,
        offset: int = 0,
        limit: int = 100,
        fields: list[str] | None = None,
        expand_inventories: bool = False,
        expand_workskills: bool = False,
        expand_workzones: bool = False,
        expand_workschedules: bool = False,
    ) -> ResourceListResponse:
        """Get descendant resources."""
        url = urljoin(
            self.baseUrl, f"/rest/ofscCore/v1/resources/{resource_id}/descendants"
        )

        params = {"offset": offset, "limit": limit}
        if fields:
            params["resourceFields"] = ",".join(fields)
        expand = self._build_expand_param(
            expand_inventories,
            expand_workskills,
            expand_workzones,
            expand_workschedules,
        )
        if expand:
            params["expand"] = expand

        try:
            response = await self._client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()

            if "links" in data:
                del data["links"]

            return ResourceListResponse.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e, f"Failed to get descendants for resource '{resource_id}'"
            )
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def get_resource_inventories(self, resource_id: str) -> InventoryListResponse:
        """Get inventories assigned to a resource."""
        url = urljoin(
            self.baseUrl, f"/rest/ofscCore/v1/resources/{resource_id}/inventories"
        )

        try:
            response = await self._client.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()

            if "links" in data:
                del data["links"]

            return InventoryListResponse.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e, f"Failed to get inventories for resource '{resource_id}'"
            )
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def get_resource_location(
        self, resource_id: str, location_id: int
    ) -> Location:
        """Get a single location for a resource."""
        url = urljoin(
            self.baseUrl,
            f"/rest/ofscCore/v1/resources/{resource_id}/locations/{location_id}",
        )

        try:
            response = await self._client.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()

            return Location.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e,
                f"Failed to get location {location_id} for resource '{resource_id}'",
            )
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def get_resource_locations(self, resource_id: str) -> LocationListResponse:
        """Get locations for a resource."""
        url = urljoin(
            self.baseUrl, f"/rest/ofscCore/v1/resources/{resource_id}/locations"
        )

        try:
            response = await self._client.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()

            if "links" in data:
                del data["links"]

            return LocationListResponse.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e, f"Failed to get locations for resource '{resource_id}'"
            )
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def get_resource_plans(self, resource_id: str) -> ResourcePlansResponse:
        """Get routing plans for a resource."""
        url = urljoin(self.baseUrl, f"/rest/ofscCore/v1/resources/{resource_id}/plans")

        try:
            response = await self._client.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()

            if "links" in data:
                del data["links"]

            return ResourcePlansResponse.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e, f"Failed to get plans for resource '{resource_id}'"
            )
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def get_resource_route(
        self, resource_id: str, route_date: date, offset: int = 0, limit: int = 100
    ) -> ResourceRouteResponse:
        """Get route for a resource on a specific date."""
        url = urljoin(
            self.baseUrl,
            f"/rest/ofscCore/v1/resources/{resource_id}/routes/{route_date.isoformat()}",
        )
        params = {"offset": offset, "limit": limit}

        try:
            response = await self._client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()

            if "links" in data:
                del data["links"]

            return ResourceRouteResponse.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e,
                f"Failed to get route for resource '{resource_id}' on {route_date.isoformat()}",
            )
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def get_resource_users(self, resource_id: str) -> ResourceUsersListResponse:
        """Get users assigned to a resource."""
        url = urljoin(self.baseUrl, f"/rest/ofscCore/v1/resources/{resource_id}/users")

        try:
            response = await self._client.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()

            if "links" in data:
                del data["links"]

            return ResourceUsersListResponse.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e, f"Failed to get users for resource '{resource_id}'"
            )
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def get_resource_workschedules(
        self, resource_id: str, actual_date: date
    ) -> ResourceWorkScheduleResponse:
        """Get workschedules for a resource."""
        url = urljoin(
            self.baseUrl, f"/rest/ofscCore/v1/resources/{resource_id}/workSchedules"
        )
        params = {"actualDate": actual_date.isoformat()}

        try:
            response = await self._client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()

            if "links" in data:
                del data["links"]

            return ResourceWorkScheduleResponse.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e, f"Failed to get workschedules for resource '{resource_id}'"
            )
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def get_resource_workskills(
        self, resource_id: str
    ) -> ResourceWorkskillListResponse:
        """Get workskills assigned to a resource."""
        url = urljoin(
            self.baseUrl, f"/rest/ofscCore/v1/resources/{resource_id}/workSkills"
        )

        try:
            response = await self._client.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()

            if "links" in data:
                del data["links"]

            return ResourceWorkskillListResponse.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e, f"Failed to get workskills for resource '{resource_id}'"
            )
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def get_resource_workzones(
        self, resource_id: str
    ) -> ResourceWorkzoneListResponse:
        """Get workzones assigned to a resource."""
        url = urljoin(
            self.baseUrl, f"/rest/ofscCore/v1/resources/{resource_id}/workZones"
        )

        try:
            response = await self._client.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()

            if "links" in data:
                del data["links"]

            return ResourceWorkzoneListResponse.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e, f"Failed to get workzones for resource '{resource_id}'"
            )
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def get_resources(
        self,
        offset: int = 0,
        limit: int = 100,
        fields: list[str] | None = None,
        expand_inventories: bool = False,
        expand_workskills: bool = False,
        expand_workzones: bool = False,
        expand_workschedules: bool = False,
    ) -> ResourceListResponse:
        """Get all resources with pagination."""
        url = urljoin(self.baseUrl, "/rest/ofscCore/v1/resources")

        params = {"offset": offset, "limit": limit}
        if fields:
            params["fields"] = ",".join(fields)
        expand = self._build_expand_param(
            expand_inventories,
            expand_workskills,
            expand_workzones,
            expand_workschedules,
        )
        if expand:
            params["expand"] = expand

        try:
            response = await self._client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()

            if "links" in data:
                del data["links"]

            return ResourceListResponse.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, "Failed to get resources")
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    # TODO: Implement remaining resource write operations (create, update, delete)
    async def create_resource(self, resourceId: str, data):
        raise NotImplementedError("Async method not yet implemented")

    async def create_resource_from_obj(self, resourceId: str, data: dict):
        raise NotImplementedError("Async method not yet implemented")

    async def update_resource(
        self, resourceId: str, data: dict, identify_by_internal_id: bool = False
    ):
        raise NotImplementedError("Async method not yet implemented")

    async def set_resource_users(self, *, resource_id: str, users: tuple[str, ...]):
        raise NotImplementedError("Async method not yet implemented")

    async def delete_resource_users(self, resource_id: str):
        raise NotImplementedError("Async method not yet implemented")

    async def set_resource_workschedules(
        self, resource_id: str, data: ResourceWorkScheduleItem
    ) -> ResourceWorkScheduleResponse:
        raise NotImplementedError("Async method not yet implemented")

    async def bulk_update_resource_workzones(self, *, data):
        raise NotImplementedError("Async method not yet implemented")

    async def bulk_update_resource_workskills(self, *, data):
        raise NotImplementedError("Async method not yet implemented")

    async def bulk_update_resource_workschedules(self, *, data):
        raise NotImplementedError("Async method not yet implemented")

    async def create_resource_location(
        self, resource_id: str, *, location: Location
    ) -> Location:
        raise NotImplementedError("Async method not yet implemented")

    async def delete_resource_location(self, resource_id: str, location_id: int):
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
        """Get available daily extract dates (folders).

        Returns:
            DailyExtractFolders: Response containing available extract dates

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        url = urljoin(self.baseUrl, "/rest/ofscCore/v1/folders/dailyExtract/folders/")

        try:
            response = await self._client.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()

            return DailyExtractFolders.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, "Failed to get daily extract dates")
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def get_daily_extract_files(self, date: str) -> DailyExtractFiles:
        """Get files available for a specific daily extract date.

        Args:
            date: Date string in YYYY-MM-DD format

        Returns:
            DailyExtractFiles: Response containing available files for the date

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCNotFoundError: If the date doesn't exist (404)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        url = urljoin(
            self.baseUrl,
            f"/rest/ofscCore/v1/folders/dailyExtract/folders/{date}/files",
        )

        try:
            response = await self._client.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()

            return DailyExtractFiles.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e, f"Failed to get daily extract files for date '{date}'"
            )
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def get_daily_extract_file(self, date: str, filename: str) -> bytes:
        """Download a specific daily extract file.

        Args:
            date: Date string in YYYY-MM-DD format
            filename: Name of the file to download

        Returns:
            bytes: Raw file content as bytes

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCNotFoundError: If the file doesn't exist (404)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        url = urljoin(
            self.baseUrl,
            f"/rest/ofscCore/v1/folders/dailyExtract/folders/{date}/files/{filename}",
        )

        headers = self.headers.copy()
        headers["Accept"] = "application/octet-stream"

        try:
            response = await self._client.get(url, headers=headers)
            response.raise_for_status()

            return response.content
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e, f"Failed to get daily extract file '{filename}' for date '{date}'"
            )
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    # endregion

    # region Subscriptions

    async def create_subscription(
        self, subscription: CreateSubscriptionRequest
    ) -> Subscription:
        """Create a new event subscription.

        Args:
            subscription: Subscription request with events and title

        Returns:
            Subscription: Created subscription with ID

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCValidationError: If request data is invalid (400)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        url = urljoin(self.baseUrl, "/rest/ofscCore/v1/events/subscriptions")

        try:
            response = await self._client.post(
                url,
                headers=self.headers,
                content=subscription.model_dump_json(exclude_none=True),
            )
            response.raise_for_status()
            data = response.json()

            return Subscription.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, "Failed to create subscription")
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def delete_subscription(self, subscription_id: str) -> None:
        """Delete an event subscription.

        Args:
            subscription_id: ID of the subscription to delete

        Returns:
            None

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCNotFoundError: If subscription doesn't exist (404)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        url = urljoin(
            self.baseUrl, f"/rest/ofscCore/v1/events/subscriptions/{subscription_id}"
        )

        try:
            response = await self._client.delete(url, headers=self.headers)
            response.raise_for_status()
            # 204 No Content - nothing to return
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e, f"Failed to delete subscription '{subscription_id}'"
            )
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def get_subscription(self, subscription_id: str) -> Subscription:
        """Get details of a specific subscription.

        Args:
            subscription_id: ID of the subscription

        Returns:
            Subscription: Subscription details

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCNotFoundError: If subscription doesn't exist (404)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        url = urljoin(
            self.baseUrl,
            f"/rest/ofscCore/v1/events/subscriptions/{subscription_id}",
        )

        try:
            response = await self._client.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()

            return Subscription.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e, f"Failed to get subscription '{subscription_id}'"
            )
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def get_subscriptions(self) -> SubscriptionListResponse:
        """Get all event subscriptions.

        Returns:
            SubscriptionListResponse: List of all subscriptions

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        url = urljoin(self.baseUrl, "/rest/ofscCore/v1/events/subscriptions")

        try:
            response = await self._client.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()

            return SubscriptionListResponse.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, "Failed to get subscriptions")
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

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
