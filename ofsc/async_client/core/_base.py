"""Base class for AsyncOFSCore - contains all non-user methods."""

from datetime import date
from typing import Optional
from urllib.parse import urljoin

import httpx

from ...exceptions import (
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
from ...models import (
    Activity,
    ActivityCapacityCategoriesResponse,
    ActivityListResponse,
    BulkUpdateRequest,
    CreateSubscriptionRequest,
    DailyExtractFiles,
    DailyExtractFolders,
    EventListResponse,
    GetActivitiesParams,
    Inventory,
    InventoryListResponse,
    LinkedActivitiesResponse,
    LinkedActivity,
    OFSConfig,
    OFSResponseList,
    RequiredInventoriesResponse,
    RequiredInventory,
    ResourcePreference,
    ResourcePreferencesResponse,
    SubmittedFormsResponse,
    Subscription,
    SubscriptionListResponse,
)


class _AsyncOFSCoreBase:
    """Base class for AsyncOFSCore - all non-user methods."""

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

    async def create_activity(self, activity: Activity) -> Activity:
        """Create a new activity.

        :param activity: Activity data to create
        :type activity: Activity
        :return: Created activity with assigned ID
        :rtype: Activity
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCValidationError: If request data is invalid (400, 422)
        :raises OFSCConflictError: If activity already exists (409)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        url = urljoin(self.baseUrl, "/rest/ofscCore/v1/activities")

        try:
            response = await self._client.post(
                url,
                headers=self.headers,
                content=activity.model_dump_json(exclude_none=True),
            )
            response.raise_for_status()
            data = response.json()

            return Activity.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, "Failed to create activity")
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def update_activity(self, activity_id: int, data: dict) -> Activity:
        """Update an existing activity using a partial update (PATCH).

        :param activity_id: The unique identifier of the activity
        :type activity_id: int
        :param data: Fields to update (partial update)
        :type data: dict
        :return: Updated activity
        :rtype: Activity
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCNotFoundError: If activity not found (404)
        :raises OFSCValidationError: If request data is invalid (400, 422)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        url = urljoin(self.baseUrl, f"/rest/ofscCore/v1/activities/{activity_id}")

        try:
            response = await self._client.patch(url, headers=self.headers, json=data)
            response.raise_for_status()
            result = response.json()

            return Activity.model_validate(result)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, f"Failed to update activity {activity_id}")
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def delete_activity(self, activity_id: int) -> None:
        """Delete an activity.

        :param activity_id: The unique identifier of the activity
        :type activity_id: int
        :return: None
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCNotFoundError: If activity not found (404)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        url = urljoin(self.baseUrl, f"/rest/ofscCore/v1/activities/{activity_id}")

        try:
            response = await self._client.delete(url, headers=self.headers)
            response.raise_for_status()
            # 204 No Content - nothing to return
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, f"Failed to delete activity {activity_id}")
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

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

    async def create_customer_inventory(
        self, activity_id: int, inventory: Inventory
    ) -> Inventory:
        """Create a customer inventory item for an activity.

        :param activity_id: The unique identifier of the activity
        :type activity_id: int
        :param inventory: Inventory data to create
        :type inventory: Inventory
        :return: Created inventory item
        :rtype: Inventory
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCNotFoundError: If activity not found (404)
        :raises OFSCValidationError: If request data is invalid (400, 422)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        url = urljoin(
            self.baseUrl,
            f"/rest/ofscCore/v1/activities/{activity_id}/customerInventories",
        )

        try:
            response = await self._client.post(
                url,
                headers=self.headers,
                content=inventory.model_dump_json(exclude_none=True),
            )
            response.raise_for_status()
            data = response.json()

            return Inventory.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e,
                f"Failed to create customer inventory for activity {activity_id}",
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

    async def set_file_property(
        self,
        activity_id: int,
        label: str,
        content: bytes,
        media_type: str,
        filename: Optional[str] = None,
    ) -> None:
        """Upload a file property for an activity.

        :param activity_id: The unique identifier of the activity
        :type activity_id: int
        :param label: The label of the file property
        :type label: str
        :param content: Binary file content
        :type content: bytes
        :param media_type: MIME type of the file (e.g., 'image/jpeg', 'application/pdf')
        :type media_type: str
        :param filename: Optional filename for Content-Disposition header
        :type filename: Optional[str]
        :return: None
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCNotFoundError: If activity not found (404)
        :raises OFSCValidationError: If request data is invalid (400, 422)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        url = urljoin(
            self.baseUrl, f"/rest/ofscCore/v1/activities/{activity_id}/{label}"
        )
        # Binary upload: override Content-Type with the file's media type
        headers = {**self.headers, "Content-Type": media_type}
        if filename:
            headers["Content-Disposition"] = f'attachment; filename="{filename}"'

        try:
            response = await self._client.put(url, headers=headers, content=content)
            response.raise_for_status()
            # 204 No Content - nothing to return
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e, f"Failed to set file property {label} for activity {activity_id}"
            )
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def delete_file_property(self, activity_id: int, label: str) -> None:
        """Delete a file property from an activity.

        :param activity_id: The unique identifier of the activity
        :type activity_id: int
        :param label: The label of the file property
        :type label: str
        :return: None
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCNotFoundError: If activity or file property not found (404)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        url = urljoin(
            self.baseUrl, f"/rest/ofscCore/v1/activities/{activity_id}/{label}"
        )

        try:
            response = await self._client.delete(url, headers=self.headers)
            response.raise_for_status()
            # 204 No Content - nothing to return
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e,
                f"Failed to delete file property {label} for activity {activity_id}",
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

    async def link_activities(
        self, activity_id: int, link: LinkedActivity
    ) -> LinkedActivity:
        """Create a link between two activities.

        :param activity_id: The unique identifier of the source activity
        :type activity_id: int
        :param link: Link data with toActivityId, linkType, and optional fields
        :type link: LinkedActivity
        :return: Created activity link
        :rtype: LinkedActivity
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCNotFoundError: If activity not found (404)
        :raises OFSCValidationError: If request data is invalid (400, 422)
        :raises OFSCConflictError: If link already exists (409)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        url = urljoin(
            self.baseUrl, f"/rest/ofscCore/v1/activities/{activity_id}/linkedActivities"
        )

        try:
            response = await self._client.post(
                url,
                headers=self.headers,
                content=link.model_dump_json(exclude_none=True),
            )
            response.raise_for_status()
            data = response.json()

            # API may return only HATEOAS links without the full LinkedActivity fields
            if "fromActivityId" not in data:
                return link
            return LinkedActivity.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e, f"Failed to link activities for activity {activity_id}"
            )
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def unlink_activities(self, activity_id: int) -> None:
        """Remove all activity links for an activity.

        :param activity_id: The unique identifier of the activity
        :type activity_id: int
        :return: None
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
            response = await self._client.delete(url, headers=self.headers)
            response.raise_for_status()
            # 204 No Content - nothing to return
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e, f"Failed to unlink activities for activity {activity_id}"
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

    async def set_activity_link(
        self,
        activity_id: int,
        linked_activity_id: int,
        link_type: str,
        data: dict,
    ) -> LinkedActivity:
        """Create or update a specific link between two activities.

        :param activity_id: The unique identifier of the source activity
        :type activity_id: int
        :param linked_activity_id: The unique identifier of the linked activity
        :type linked_activity_id: int
        :param link_type: The type of link
        :type link_type: str
        :param data: Link data (e.g., minIntervalValue, alerts)
        :type data: dict
        :return: Activity link details
        :rtype: LinkedActivity
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCNotFoundError: If activity not found (404)
        :raises OFSCValidationError: If request data is invalid (400, 422)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        url = urljoin(
            self.baseUrl,
            f"/rest/ofscCore/v1/activities/{activity_id}/linkedActivities/{linked_activity_id}/linkTypes/{link_type}",
        )

        try:
            response = await self._client.put(url, headers=self.headers, json=data)
            response.raise_for_status()
            result = response.json()

            # API may return only HATEOAS links without the full LinkedActivity fields
            if "fromActivityId" not in result:
                return LinkedActivity.model_validate(
                    {
                        "fromActivityId": activity_id,
                        "toActivityId": linked_activity_id,
                        "linkType": link_type,
                    }
                )
            return LinkedActivity.model_validate(result)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e,
                f"Failed to set link {link_type} between activities {activity_id} and {linked_activity_id}",
            )
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def delete_activity_link(
        self, activity_id: int, linked_activity_id: int, link_type: str
    ) -> None:
        """Delete a specific link between two activities.

        :param activity_id: The unique identifier of the source activity
        :type activity_id: int
        :param linked_activity_id: The unique identifier of the linked activity
        :type linked_activity_id: int
        :param link_type: The type of link
        :type link_type: str
        :return: None
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCNotFoundError: If link not found (404)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        url = urljoin(
            self.baseUrl,
            f"/rest/ofscCore/v1/activities/{activity_id}/linkedActivities/{linked_activity_id}/linkTypes/{link_type}",
        )

        try:
            response = await self._client.delete(url, headers=self.headers)
            response.raise_for_status()
            # 204 No Content - nothing to return
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e,
                f"Failed to delete link {link_type} between activities {activity_id} and {linked_activity_id}",
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

    async def set_required_inventories(
        self, activity_id: int, inventories: list[RequiredInventory]
    ) -> None:
        """Set required inventories for an activity (replaces existing list).

        :param activity_id: The unique identifier of the activity
        :type activity_id: int
        :param inventories: List of required inventory items
        :type inventories: list[RequiredInventory]
        :return: None
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCNotFoundError: If activity not found (404)
        :raises OFSCValidationError: If request data is invalid (400, 422)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        url = urljoin(
            self.baseUrl,
            f"/rest/ofscCore/v1/activities/{activity_id}/requiredInventories",
        )
        payload = {"items": [inv.model_dump(exclude_none=True) for inv in inventories]}

        try:
            response = await self._client.put(url, headers=self.headers, json=payload)
            response.raise_for_status()
            # 204 No Content - nothing to return
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e, f"Failed to set required inventories for activity {activity_id}"
            )
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def delete_required_inventories(self, activity_id: int) -> None:
        """Delete all required inventories for an activity.

        :param activity_id: The unique identifier of the activity
        :type activity_id: int
        :return: None
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
            response = await self._client.delete(url, headers=self.headers)
            response.raise_for_status()
            # 204 No Content - nothing to return
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e,
                f"Failed to delete required inventories for activity {activity_id}",
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

    async def set_resource_preferences(
        self, activity_id: int, preferences: list[ResourcePreference]
    ) -> None:
        """Set resource preferences for an activity (replaces existing list).

        :param activity_id: The unique identifier of the activity
        :type activity_id: int
        :param preferences: List of resource preference items
        :type preferences: list[ResourcePreference]
        :return: None
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCNotFoundError: If activity not found (404)
        :raises OFSCValidationError: If request data is invalid (400, 422)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        url = urljoin(
            self.baseUrl,
            f"/rest/ofscCore/v1/activities/{activity_id}/resourcePreferences",
        )
        payload = {
            "items": [pref.model_dump(exclude_none=True) for pref in preferences]
        }

        try:
            response = await self._client.put(url, headers=self.headers, json=payload)
            response.raise_for_status()
            # 204 No Content - nothing to return
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e, f"Failed to set resource preferences for activity {activity_id}"
            )
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def delete_resource_preferences(self, activity_id: int) -> None:
        """Delete all resource preferences for an activity.

        :param activity_id: The unique identifier of the activity
        :type activity_id: int
        :return: None
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
            response = await self._client.delete(url, headers=self.headers)
            response.raise_for_status()
            # 204 No Content - nothing to return
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e,
                f"Failed to delete resource preferences for activity {activity_id}",
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
