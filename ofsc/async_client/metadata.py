"""Async version of OFSMetadata API module."""

from pathlib import Path
from typing import Tuple
from urllib.parse import quote_plus, urljoin

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
    ActivityType,
    ActivityTypeGroup,
    ActivityTypeGroupListResponse,
    ActivityTypeListResponse,
    Application,
    ApplicationApiAccess,
    ApplicationApiAccessListResponse,
    ApplicationListResponse,
    CapacityArea,
    CapacityAreaListResponse,
    CapacityCategory,
    CapacityCategoryListResponse,
    EnumerationValue,
    EnumerationValueList,
    Form,
    FormListResponse,
    InventoryType,
    InventoryTypeListResponse,
    Language,
    LanguageListResponse,
    LinkTemplate,
    LinkTemplateListResponse,
    MapLayer,
    MapLayerListResponse,
    NonWorkingReason,
    NonWorkingReasonListResponse,
    OFSConfig,
    Organization,
    OrganizationListResponse,
    Property,
    PropertyListResponse,
    ResourceTypeListResponse,
    RoutingPlanData,
    RoutingPlanList,
    RoutingProfileList,
    Shift,
    ShiftListResponse,
    TimeSlot,
    TimeSlotListResponse,
    Workskill,
    WorkskillListResponse,
    WorkskillGroup,
    WorkskillGroupListResponse,
    WorkskillConditionList,
    Workzone,
    WorkzoneListResponse,
)


class AsyncOFSMetadata:
    """Async version of OFSMetadata API module."""

    def __init__(self, config: OFSConfig, client: httpx.AsyncClient):
        self._config = config
        self._client = client

    @property
    def config(self) -> OFSConfig:
        return self._config

    @property
    def baseUrl(self) -> str:
        if self._config.baseURL is None:
            raise ValueError("Base URL is not configured")
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

        Args:
            response: The httpx Response object

        Returns:
            dict: Error information with type, title, and detail keys
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

        Args:
            e: The httpx HTTPStatusError exception
            context: Additional context for the error message

        Raises:
            OFSCAuthenticationError: For 401 errors
            OFSCAuthorizationError: For 403 errors
            OFSCNotFoundError: For 404 errors
            OFSCConflictError: For 409 errors
            OFSCRateLimitError: For 429 errors
            OFSCValidationError: For 400, 422 errors
            OFSCServerError: For 5xx errors
            OFSCApiError: For other HTTP errors
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

    # region Activity Type Groups

    async def get_activity_type_groups(
        self, offset: int = 0, limit: int = 100
    ) -> ActivityTypeGroupListResponse:
        """Get activity type groups with pagination.

        Args:
            offset: Starting record number (default 0)
            limit: Maximum number of activity type groups to return (default 100)

        Returns:
            ActivityTypeGroupListResponse: List of activity type groups with pagination info

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        url = urljoin(self.baseUrl, "/rest/ofscMetadata/v1/activityTypeGroups")
        params = {"offset": offset, "limit": limit}

        try:
            response = await self._client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            # Remove links if not in model
            if "links" in data and not hasattr(ActivityTypeGroupListResponse, "links"):
                del data["links"]

            return ActivityTypeGroupListResponse.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, "Failed to get activity type groups")
            raise  # This will never execute, but satisfies type checker
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def get_activity_type_group(self, label: str) -> ActivityTypeGroup:
        """Get a single activity type group by label.

        Args:
            label: The activity type group label to retrieve

        Returns:
            ActivityTypeGroup: The activity type group details

        Raises:
            OFSCNotFoundError: If activity type group not found (404)
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        encoded_label = quote_plus(label)
        url = urljoin(
            self.baseUrl, f"/rest/ofscMetadata/v1/activityTypeGroups/{encoded_label}"
        )

        try:
            response = await self._client.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            # Remove links if not in model
            if "links" in data and not hasattr(ActivityTypeGroup, "links"):
                del data["links"]

            return ActivityTypeGroup.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, f"Failed to get activity type group '{label}'")
            raise  # This will never execute, but satisfies type checker
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    # endregion

    # region Activity Types

    async def get_activity_types(
        self, offset: int = 0, limit: int = 100
    ) -> ActivityTypeListResponse:
        """Get activity types with pagination.

        Args:
            offset: Starting record number (default 0)
            limit: Maximum number of activity types to return (default 100)

        Returns:
            ActivityTypeListResponse: List of activity types with pagination info

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        url = urljoin(self.baseUrl, "/rest/ofscMetadata/v1/activityTypes")
        params = {"offset": offset, "limit": limit}

        try:
            response = await self._client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            # Remove links if not in model
            if "links" in data and not hasattr(ActivityTypeListResponse, "links"):
                del data["links"]

            return ActivityTypeListResponse.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, "Failed to get activity types")
            raise  # This will never execute, but satisfies type checker
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def get_activity_type(self, label: str) -> ActivityType:
        """Get a single activity type by label.

        Args:
            label: The activity type label to retrieve

        Returns:
            ActivityType: The activity type details

        Raises:
            OFSCNotFoundError: If activity type not found (404)
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        encoded_label = quote_plus(label)
        url = urljoin(
            self.baseUrl, f"/rest/ofscMetadata/v1/activityTypes/{encoded_label}"
        )

        try:
            response = await self._client.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            # Remove links if not in model
            if "links" in data and not hasattr(ActivityType, "links"):
                del data["links"]

            return ActivityType.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, f"Failed to get activity type '{label}'")
            raise  # This will never execute, but satisfies type checker
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    # endregion

    # region Applications

    async def get_applications(self) -> ApplicationListResponse:
        """Get all applications.

        Returns:
            ApplicationListResponse: List of applications

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        url = urljoin(self.baseUrl, "/rest/ofscMetadata/v1/applications")

        try:
            response = await self._client.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            if "links" in data:
                del data["links"]
            return ApplicationListResponse.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, "Failed to get applications")
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def get_application(self, label: str) -> Application:
        """Get a single application by label.

        Args:
            label: The application label to retrieve

        Returns:
            Application: The application details

        Raises:
            OFSCNotFoundError: If application not found (404)
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        encoded_label = quote_plus(label)
        url = urljoin(
            self.baseUrl, f"/rest/ofscMetadata/v1/applications/{encoded_label}"
        )

        try:
            response = await self._client.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            if "links" in data:
                del data["links"]
            return Application.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, f"Failed to get application '{label}'")
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def get_application_api_accesses(
        self, label: str
    ) -> ApplicationApiAccessListResponse:
        """Get all API accesses for an application.

        Args:
            label: The application label

        Returns:
            ApplicationApiAccessListResponse: List of API accesses

        Raises:
            OFSCNotFoundError: If application not found (404)
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        encoded_label = quote_plus(label)
        url = urljoin(
            self.baseUrl,
            f"/rest/ofscMetadata/v1/applications/{encoded_label}/apiAccess",
        )

        try:
            response = await self._client.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            if "links" in data:
                del data["links"]
            return ApplicationApiAccessListResponse.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e, f"Failed to get API accesses for application '{label}'"
            )
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def get_application_api_access(
        self, label: str, access_id: str
    ) -> ApplicationApiAccess:
        """Get a single API access for an application.

        Args:
            label: The application label
            access_id: The API access ID (e.g., "capacityAPI", "coreAPI")

        Returns:
            ApplicationApiAccess: The API access details

        Raises:
            OFSCNotFoundError: If application or API access not found (404)
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        encoded_label = quote_plus(label)
        encoded_access_id = quote_plus(access_id)
        url = urljoin(
            self.baseUrl,
            f"/rest/ofscMetadata/v1/applications/{encoded_label}/apiAccess/{encoded_access_id}",
        )

        try:
            response = await self._client.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            if "links" in data:
                del data["links"]
            # Import parse function from models
            from ..models import parse_application_api_access

            return parse_application_api_access(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e,
                f"Failed to get API access '{access_id}' for application '{label}'",
            )
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    # endregion

    # region Capacity Areas

    async def get_capacity_areas(
        self,
        expandParent: bool = False,
        fields: list[str] | None = None,
        activeOnly: bool = False,
        areasOnly: bool = False,
    ) -> CapacityAreaListResponse:
        """Get all capacity areas with optional filtering.

        Args:
            expandParent: If True, expands parent area details
            fields: List of fields to return (default: all fields)
            activeOnly: If True, return only active areas
            areasOnly: If True, return only areas (not categories)

        Returns:
            CapacityAreaListResponse: List of capacity areas

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        url = urljoin(self.baseUrl, "/rest/ofscMetadata/v1/capacityAreas")

        # Build params - None values are excluded by httpx
        params = {}
        if expandParent:
            params["expand"] = "parent"
        if fields:
            params["fields"] = ",".join(fields)
        if activeOnly:
            params["status"] = "active"
        if areasOnly:
            params["type"] = "area"

        try:
            response = await self._client.get(
                url, headers=self.headers, params=params if params else None
            )
            response.raise_for_status()
            data = response.json()
            if "links" in data and not hasattr(CapacityAreaListResponse, "links"):
                del data["links"]
            return CapacityAreaListResponse.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, "Failed to get capacity areas")
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def get_capacity_area(self, label: str) -> CapacityArea:
        """Get a single capacity area by label.

        Args:
            label: The capacity area label to retrieve

        Returns:
            CapacityArea: The capacity area details

        Raises:
            OFSCNotFoundError: If capacity area not found (404)
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        encoded_label = quote_plus(label)
        url = urljoin(
            self.baseUrl, f"/rest/ofscMetadata/v1/capacityAreas/{encoded_label}"
        )

        try:
            response = await self._client.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            if "links" in data and not hasattr(CapacityArea, "links"):
                del data["links"]
            return CapacityArea.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, f"Failed to get capacity area '{label}'")
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    # endregion

    # region Capacity Categories

    async def get_capacity_categories(
        self, offset: int = 0, limit: int = 100
    ) -> CapacityCategoryListResponse:
        """Get all capacity categories with pagination.

        Args:
            offset: Starting record number (default 0)
            limit: Maximum number to return (default 100)

        Returns:
            CapacityCategoryListResponse: List of capacity categories

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        url = urljoin(self.baseUrl, "/rest/ofscMetadata/v1/capacityCategories")
        params = {"offset": offset, "limit": limit}

        try:
            response = await self._client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            if "links" in data and not hasattr(CapacityCategoryListResponse, "links"):
                del data["links"]
            return CapacityCategoryListResponse.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, "Failed to get capacity categories")
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def get_capacity_category(self, label: str) -> CapacityCategory:
        """Get a single capacity category by label.

        Args:
            label: The capacity category label to retrieve

        Returns:
            CapacityCategory: The capacity category details

        Raises:
            OFSCNotFoundError: If capacity category not found (404)
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        encoded_label = quote_plus(label)
        url = urljoin(
            self.baseUrl, f"/rest/ofscMetadata/v1/capacityCategories/{encoded_label}"
        )

        try:
            response = await self._client.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            if "links" in data and not hasattr(CapacityCategory, "links"):
                del data["links"]
            return CapacityCategory.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, f"Failed to get capacity category '{label}'")
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    # endregion

    # region Forms

    async def get_forms(self, offset: int = 0, limit: int = 100) -> FormListResponse:
        """Get all forms with pagination.

        Args:
            offset: Starting record number (default 0)
            limit: Maximum number to return (default 100)

        Returns:
            FormListResponse: List of forms

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        url = urljoin(self.baseUrl, "/rest/ofscMetadata/v1/forms")
        params = {"offset": offset, "limit": limit}

        try:
            response = await self._client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            if "links" in data and not hasattr(FormListResponse, "links"):
                del data["links"]
            return FormListResponse.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, "Failed to get forms")
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def get_form(self, label: str) -> Form:
        """Get a single form by label.

        Args:
            label: The form label to retrieve

        Returns:
            Form: The form details

        Raises:
            OFSCNotFoundError: If form not found (404)
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        encoded_label = quote_plus(label)
        url = urljoin(self.baseUrl, f"/rest/ofscMetadata/v1/forms/{encoded_label}")

        try:
            response = await self._client.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            if "links" in data and not hasattr(Form, "links"):
                del data["links"]
            return Form.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, f"Failed to get form '{label}'")
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    # endregion

    # region Inventory Types

    async def get_inventory_types(
        self, offset: int = 0, limit: int = 100
    ) -> InventoryTypeListResponse:
        """Get inventory types with pagination.

        Args:
            offset: Starting record number (default 0)
            limit: Maximum number to return (default 100)

        Returns:
            InventoryTypeListResponse: List with pagination info

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        url = urljoin(self.baseUrl, "/rest/ofscMetadata/v1/inventoryTypes")
        params = {"offset": offset, "limit": limit}

        try:
            response = await self._client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            # Remove links if not in model
            if "links" in data and not hasattr(InventoryTypeListResponse, "links"):
                del data["links"]

            return InventoryTypeListResponse.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, "Failed to get inventory types")
            raise  # This will never execute, but satisfies type checker
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def get_inventory_type(self, label: str) -> InventoryType:
        """Get a single inventory type by label.

        Args:
            label: The inventory type label

        Returns:
            InventoryType: The inventory type details

        Raises:
            OFSCNotFoundError: If inventory type not found (404)
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        encoded_label = quote_plus(label)
        url = urljoin(
            self.baseUrl, f"/rest/ofscMetadata/v1/inventoryTypes/{encoded_label}"
        )

        try:
            response = await self._client.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            # Remove links if not in model
            if "links" in data and not hasattr(InventoryType, "links"):
                del data["links"]

            return InventoryType.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, f"Failed to get inventory type '{label}'")
            raise  # This will never execute, but satisfies type checker
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    # endregion

    # region Languages

    async def get_languages(
        self, offset: int = 0, limit: int = 100
    ) -> LanguageListResponse:
        """Get languages with pagination.

        Args:
            offset: Starting record number (default 0)
            limit: Maximum number to return (default 100)

        Returns:
            LanguageListResponse: List with pagination info

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        url = urljoin(self.baseUrl, "/rest/ofscMetadata/v1/languages")
        params = {"offset": offset, "limit": limit}

        try:
            response = await self._client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            # Remove links if not in model
            if "links" in data and not hasattr(LanguageListResponse, "links"):
                del data["links"]

            return LanguageListResponse.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, "Failed to get languages")
            raise  # This will never execute, but satisfies type checker
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def get_language(self, label: str) -> Language:
        raise NotImplementedError("Async method not yet implemented")

    # endregion

    # region Link Templates

    async def get_link_templates(
        self, offset: int = 0, limit: int = 100
    ) -> LinkTemplateListResponse:
        """Get link templates with pagination.

        Args:
            offset: Starting record number (default 0)
            limit: Maximum number to return (default 100)

        Returns:
            LinkTemplateListResponse: List with pagination info

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        url = urljoin(self.baseUrl, "/rest/ofscMetadata/v1/linkTemplates")
        params = {"offset": offset, "limit": limit}

        try:
            response = await self._client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            if "links" in data and not hasattr(LinkTemplateListResponse, "links"):
                del data["links"]
            return LinkTemplateListResponse.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, "Failed to get link templates")
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def get_link_template(self, label: str) -> LinkTemplate:
        """Get a single link template by label.

        Args:
            label: The link template label

        Returns:
            LinkTemplate: The link template details

        Raises:
            OFSCNotFoundError: If link template not found (404)
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        encoded_label = quote_plus(label)
        url = urljoin(
            self.baseUrl, f"/rest/ofscMetadata/v1/linkTemplates/{encoded_label}"
        )

        try:
            response = await self._client.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            if "links" in data and not hasattr(LinkTemplate, "links"):
                del data["links"]
            return LinkTemplate.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, f"Failed to get link template '{label}'")
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    # endregion

    # region Map Layers

    async def get_map_layers(
        self, offset: int = 0, limit: int = 100
    ) -> MapLayerListResponse:
        """Get all map layers with pagination.

        Args:
            offset: Starting record number (default 0)
            limit: Maximum number to return (default 100)

        Returns:
            MapLayerListResponse: List of map layers

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        url = urljoin(self.baseUrl, "/rest/ofscMetadata/v1/mapLayers")
        params = {"offset": offset, "limit": limit}

        try:
            response = await self._client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            if "links" in data and not hasattr(MapLayerListResponse, "links"):
                del data["links"]
            return MapLayerListResponse.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, "Failed to get map layers")
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def get_map_layer(self, label: str) -> MapLayer:
        """Get a single map layer by label.

        Args:
            label: The map layer label to retrieve

        Returns:
            MapLayer: The map layer details

        Raises:
            OFSCNotFoundError: If map layer not found (404)
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        encoded_label = quote_plus(label)
        url = urljoin(self.baseUrl, f"/rest/ofscMetadata/v1/mapLayers/{encoded_label}")

        try:
            response = await self._client.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            if "links" in data and not hasattr(MapLayer, "links"):
                del data["links"]
            return MapLayer.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, f"Failed to get map layer '{label}'")
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    # endregion

    # region Non-working Reasons

    async def get_non_working_reasons(
        self, offset: int = 0, limit: int = 100
    ) -> NonWorkingReasonListResponse:
        """Get non-working reasons with pagination.

        Args:
            offset: Starting record number (default 0)
            limit: Maximum number of non-working reasons to return (default 100)

        Returns:
            NonWorkingReasonListResponse: List of non-working reasons with pagination info

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        url = urljoin(self.baseUrl, "/rest/ofscMetadata/v1/nonWorkingReasons")
        params = {"offset": offset, "limit": limit}

        try:
            response = await self._client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            # Remove links if not in model
            if "links" in data and not hasattr(NonWorkingReasonListResponse, "links"):
                del data["links"]

            return NonWorkingReasonListResponse.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, "Failed to get non-working reasons")
            raise  # This will never execute, but satisfies type checker
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def get_non_working_reason(self, label: str) -> NonWorkingReason:
        """Get a single non-working reason by label.

        Note:
            The Oracle Field Service API does not support retrieving individual
            non-working reasons by label. This method raises NotImplementedError.
            Use get_non_working_reasons() and filter the results instead.

        Args:
            label: The non-working reason label to retrieve

        Raises:
            NotImplementedError: This operation is not supported by the API
        """
        raise NotImplementedError(
            "Oracle Field Service API does not support retrieving individual non-working reasons by label. "
            "Use get_non_working_reasons() and filter the results instead."
        )

    # endregion

    # region Organizations

    async def get_organizations(self) -> OrganizationListResponse:
        """Get all organizations.

        Returns:
            OrganizationListResponse: List of organizations

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        url = urljoin(self.baseUrl, "/rest/ofscMetadata/v1/organizations")

        try:
            response = await self._client.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            if "links" in data and not hasattr(OrganizationListResponse, "links"):
                del data["links"]
            return OrganizationListResponse.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, "Failed to get organizations")
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def get_organization(self, label: str) -> Organization:
        """Get a single organization by label.

        Args:
            label: The organization label

        Returns:
            Organization: The organization details

        Raises:
            OFSCNotFoundError: If organization not found (404)
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        encoded_label = quote_plus(label)
        url = urljoin(
            self.baseUrl, f"/rest/ofscMetadata/v1/organizations/{encoded_label}"
        )

        try:
            response = await self._client.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            if "links" in data and not hasattr(Organization, "links"):
                del data["links"]
            return Organization.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, f"Failed to get organization '{label}'")
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    # endregion

    # region Plugins

    async def import_plugin_file(self, plugin: Path) -> None:
        """Import a plugin from a file.

        Args:
            plugin: Path to the plugin XML file

        Returns:
            None on success (204 No Content)

        Raises:
            OFSCValidationError: If plugin XML is invalid (400)
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        url = urljoin(
            self.baseUrl, "/rest/ofscMetadata/v1/plugins/custom-actions/import"
        )

        try:
            # Read file content and create multipart form data
            files = {"pluginFile": (plugin.name, plugin.read_text(), "text/xml")}
            response = await self._client.post(url, headers=self.headers, files=files)
            response.raise_for_status()
            # 204 No Content - return None
            return None
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, f"Failed to import plugin from '{plugin}'")
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def import_plugin(self, plugin: str) -> None:
        """Import a plugin from a string.

        Args:
            plugin: Plugin XML content as string

        Returns:
            None on success (204 No Content)

        Raises:
            OFSCValidationError: If plugin XML is invalid (400)
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        url = urljoin(
            self.baseUrl, "/rest/ofscMetadata/v1/plugins/custom-actions/import"
        )

        try:
            # Create multipart form data from string content
            files = {"pluginFile": ("plugin.xml", plugin, "text/xml")}
            response = await self._client.post(url, headers=self.headers, files=files)
            response.raise_for_status()
            # 204 No Content - return None
            return None
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, "Failed to import plugin")
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    # endregion

    # region Properties

    async def get_properties(
        self, offset: int = 0, limit: int = 100
    ) -> PropertyListResponse:
        """Get properties with pagination.

        Args:
            offset: Starting record number (default 0)
            limit: Maximum number of properties to return (default 100)

        Returns:
            PropertyListResponse: List of properties with pagination info

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        url = urljoin(self.baseUrl, "/rest/ofscMetadata/v1/properties")
        params = {"offset": offset, "limit": limit}

        try:
            response = await self._client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            # Remove links if not in model
            if "links" in data and not hasattr(PropertyListResponse, "links"):
                del data["links"]

            return PropertyListResponse.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, "Failed to get properties")
            raise  # This will never execute, but satisfies type checker
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def get_property(self, label: str) -> Property:
        """Get a single property by label.

        Args:
            label: The property label to retrieve

        Returns:
            Property: The property details

        Raises:
            OFSCNotFoundError: If property not found (404)
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        url = urljoin(self.baseUrl, f"/rest/ofscMetadata/v1/properties/{label}")

        try:
            response = await self._client.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            # Remove links if not in model
            if "links" in data and not hasattr(Property, "links"):
                del data["links"]

            return Property.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, f"Failed to get property '{label}'")
            raise  # This will never execute, but satisfies type checker
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def create_or_replace_property(self, property: Property) -> Property:
        """Create or replace a property.

        Args:
            property: The property object to create or replace

        Returns:
            Property: The created or updated property

        Raises:
            OFSCValidationError: If validation fails (400)
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        url = urljoin(
            self.baseUrl, f"/rest/ofscMetadata/v1/properties/{property.label}"
        )

        try:
            response = await self._client.put(
                url,
                headers=self.headers,
                content=property.model_dump_json(exclude_none=True).encode("utf-8"),
            )
            response.raise_for_status()
            data = response.json()
            # Remove links if not in model
            if "links" in data and not hasattr(Property, "links"):
                del data["links"]

            return Property.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e, f"Failed to create or replace property '{property.label}'"
            )
            raise  # This will never execute, but satisfies type checker
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def get_enumeration_values(
        self, label: str, offset: int = 0, limit: int = 100
    ) -> EnumerationValueList:
        """Get enumeration values for a property.

        Args:
            label: The property label
            offset: Starting record number (default 0)
            limit: Maximum number of values to return (default 100)

        Returns:
            EnumerationValueList: List of enumeration values with pagination info

        Raises:
            OFSCNotFoundError: If property not found (404)
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        url = urljoin(
            self.baseUrl, f"/rest/ofscMetadata/v1/properties/{label}/enumerationList"
        )
        params = {"offset": offset, "limit": limit}

        try:
            response = await self._client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            # Remove links if not in model
            if "links" in data and not hasattr(EnumerationValueList, "links"):
                del data["links"]

            return EnumerationValueList.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e, f"Failed to get enumeration values for property '{label}'"
            )
            raise  # This will never execute, but satisfies type checker
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def create_or_update_enumeration_value(
        self, label: str, value: Tuple[EnumerationValue, ...]
    ) -> EnumerationValueList:
        """Create or update enumeration values for a property.

        Args:
            label: The property label
            value: Tuple of EnumerationValue objects to create or update

        Returns:
            EnumerationValueList: Updated list of enumeration values

        Raises:
            OFSCNotFoundError: If property not found (404)
            OFSCValidationError: If validation fails (400)
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        url = urljoin(
            self.baseUrl,
            f"/rest/ofscMetadata/v1/properties/{label}/enumerationList",
        )
        data = {"items": [item.model_dump() for item in value]}

        try:
            response = await self._client.put(url, headers=self.headers, json=data)
            response.raise_for_status()
            response_data = response.json()
            # Remove links if not in model
            if "links" in response_data and not hasattr(EnumerationValueList, "links"):
                del response_data["links"]

            return EnumerationValueList.model_validate(response_data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e,
                f"Failed to create or update enumeration values for property '{label}'",
            )
            raise  # This will never execute, but satisfies type checker
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    # endregion

    # region Resource Types

    async def get_resource_types(self) -> ResourceTypeListResponse:
        """Get all resource types.

        Returns:
            ResourceTypeListResponse: List of resource types

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        url = urljoin(self.baseUrl, "/rest/ofscMetadata/v1/resourceTypes")

        try:
            response = await self._client.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            # Remove links if not in model
            if "links" in data and not hasattr(ResourceTypeListResponse, "links"):
                del data["links"]

            return ResourceTypeListResponse.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, "Failed to get resource types")
            raise  # This will never execute, but satisfies type checker
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    # endregion

    # region Routing Profiles

    async def get_routing_profiles(
        self, offset: int = 0, limit: int = 100
    ) -> RoutingProfileList:
        """Get all routing profiles with pagination.

        Args:
            offset: Starting record number (default 0)
            limit: Maximum number to return (default 100)

        Returns:
            RoutingProfileList: List of routing profiles with pagination info

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        url = urljoin(self.baseUrl, "/rest/ofscMetadata/v1/routingProfiles")
        params = {"offset": offset, "limit": limit}

        try:
            response = await self._client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            # Remove links if not in model
            if "links" in data and not hasattr(RoutingProfileList, "links"):
                del data["links"]

            return RoutingProfileList.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, "Failed to get routing profiles")
            raise  # This will never execute, but satisfies type checker
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def get_routing_profile_plans(
        self, profile_label: str, offset: int = 0, limit: int = 100
    ) -> RoutingPlanList:
        """Get all routing plans for a routing profile.

        Args:
            profile_label: Routing profile label
            offset: Starting record number (default 0)
            limit: Maximum number to return (default 100)

        Returns:
            RoutingPlanList: List of routing plans with pagination info

        Raises:
            OFSCNotFoundError: If routing profile not found (404)
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        encoded_label = quote_plus(profile_label)
        url = urljoin(
            self.baseUrl, f"/rest/ofscMetadata/v1/routingProfiles/{encoded_label}/plans"
        )
        params = {"offset": offset, "limit": limit}

        try:
            response = await self._client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            # Remove links if not in model
            if "links" in data and not hasattr(RoutingPlanList, "links"):
                del data["links"]

            return RoutingPlanList.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e, f"Failed to get routing plans for profile '{profile_label}'"
            )
            raise  # This will never execute, but satisfies type checker
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def export_routing_plan(
        self, profile_label: str, plan_label: str
    ) -> RoutingPlanData:
        """Export a routing plan.

        Args:
            profile_label: Routing profile label
            plan_label: Routing plan label

        Returns:
            RoutingPlanData: Complete routing plan configuration

        Raises:
            OFSCNotFoundError: If routing profile or plan not found (404)
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        encoded_profile = quote_plus(profile_label)
        encoded_plan = quote_plus(plan_label)
        url = urljoin(
            self.baseUrl,
            f"/rest/ofscMetadata/v1/routingProfiles/{encoded_profile}/plans/{encoded_plan}/custom-actions/export",
        )

        # Use Accept: application/octet-stream to get the actual plan data
        headers = self.headers.copy()
        headers["Accept"] = "application/octet-stream"

        try:
            response = await self._client.get(url, headers=headers)
            response.raise_for_status()
            # Response is JSON in bytes, need to parse it
            data = response.json()
            # Remove links if not in model
            if "links" in data and not hasattr(RoutingPlanData, "links"):
                del data["links"]

            return RoutingPlanData.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e,
                f"Failed to export routing plan '{plan_label}' from profile '{profile_label}'",
            )
            raise  # This will never execute, but satisfies type checker
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def export_plan_file(self, profile_label: str, plan_label: str) -> bytes:
        """Export a routing plan as binary file.

        Args:
            profile_label: Routing profile label
            plan_label: Routing plan label

        Returns:
            bytes: Raw binary content of the routing plan file

        Raises:
            OFSCNotFoundError: If routing profile or plan not found (404)
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        encoded_profile = quote_plus(profile_label)
        encoded_plan = quote_plus(plan_label)
        url = urljoin(
            self.baseUrl,
            f"/rest/ofscMetadata/v1/routingProfiles/{encoded_profile}/plans/{encoded_plan}/custom-actions/export",
        )

        # Use Accept: application/octet-stream for binary download
        headers = self.headers.copy()
        headers["Accept"] = "application/octet-stream"

        try:
            response = await self._client.get(url, headers=headers)
            response.raise_for_status()
            return response.content
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e,
                f"Failed to export plan file '{plan_label}' from profile '{profile_label}'",
            )
            raise  # This will never execute, but satisfies type checker
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def import_routing_plan(self, profile_label: str, plan_data: bytes) -> None:
        """Import a routing plan.

        Args:
            profile_label: Routing profile label
            plan_data: Binary plan data to import

        Returns:
            None: Success returns None

        Raises:
            OFSCNotFoundError: If routing profile not found (404)
            OFSCConflictError: If plan already exists (409)
            OFSCValidationError: If validation fails (400)
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        encoded_profile = quote_plus(profile_label)
        url = urljoin(
            self.baseUrl,
            f"/rest/ofscMetadata/v1/routingProfiles/{encoded_profile}/plans/custom-actions/import",
        )

        # Use Content-Type: application/octet-stream for binary upload
        headers = self.headers.copy()
        headers["Content-Type"] = "application/octet-stream"

        try:
            response = await self._client.put(url, headers=headers, content=plan_data)
            response.raise_for_status()
            # API returns success message, no need to parse
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e, f"Failed to import routing plan to profile '{profile_label}'"
            )
            raise  # This will never execute, but satisfies type checker
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def force_import_routing_plan(
        self, profile_label: str, plan_data: bytes
    ) -> None:
        """Force import a routing plan (overwrite if exists).

        Args:
            profile_label: Routing profile label
            plan_data: Binary plan data to import

        Returns:
            None: Success returns None

        Raises:
            OFSCNotFoundError: If routing profile not found (404)
            OFSCValidationError: If validation fails (400)
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        encoded_profile = quote_plus(profile_label)
        url = urljoin(
            self.baseUrl,
            f"/rest/ofscMetadata/v1/routingProfiles/{encoded_profile}/plans/custom-actions/forceImport",
        )

        # Use Content-Type: application/octet-stream for binary upload
        headers = self.headers.copy()
        headers["Content-Type"] = "application/octet-stream"

        try:
            response = await self._client.put(url, headers=headers, content=plan_data)
            response.raise_for_status()
            # API returns success message, no need to parse
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e, f"Failed to force import routing plan to profile '{profile_label}'"
            )
            raise  # This will never execute, but satisfies type checker
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def start_routing_plan(
        self,
        profile_label: str,
        plan_label: str,
        resource_external_id: str,
        date: str,
    ) -> None:
        """Start a routing plan for a resource on a specific date.

        Args:
            profile_label: Routing profile label
            plan_label: Routing plan label
            resource_external_id: External ID of the resource
            date: Date in format YYYY-MM-DD

        Returns:
            None

        Raises:
            OFSCNotFoundError: If routing profile, plan, or resource not found (404)
            OFSCValidationError: If validation fails (400)
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        encoded_profile = quote_plus(profile_label)
        encoded_plan = quote_plus(plan_label)
        url = urljoin(
            self.baseUrl,
            f"/rest/ofscMetadata/v1/routingProfiles/{encoded_profile}/plans/{encoded_plan}/{resource_external_id}/{date}/custom-actions/start",
        )

        try:
            response = await self._client.post(url, headers=self.headers)
            response.raise_for_status()
            # POST returns 200 with empty or minimal response
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e,
                f"Failed to start routing plan '{plan_label}' for resource '{resource_external_id}' on date '{date}'",
            )
            raise  # This will never execute, but satisfies type checker
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    # endregion

    # region Shifts

    async def get_shifts(self, offset: int = 0, limit: int = 100) -> ShiftListResponse:
        """Get all shifts with pagination.

        Args:
            offset: Starting record number (default 0)
            limit: Maximum number to return (default 100)

        Returns:
            ShiftListResponse: List of shifts

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        url = urljoin(self.baseUrl, "/rest/ofscMetadata/v1/shifts")
        params = {"offset": offset, "limit": limit}

        try:
            response = await self._client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            if "links" in data and not hasattr(ShiftListResponse, "links"):
                del data["links"]
            return ShiftListResponse.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, "Failed to get shifts")
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def get_shift(self, label: str) -> Shift:
        """Get a single shift by label.

        Args:
            label: The shift label to retrieve

        Returns:
            Shift: The shift details

        Raises:
            OFSCNotFoundError: If shift not found (404)
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        encoded_label = quote_plus(label)
        url = urljoin(self.baseUrl, f"/rest/ofscMetadata/v1/shifts/{encoded_label}")

        try:
            response = await self._client.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            if "links" in data and not hasattr(Shift, "links"):
                del data["links"]
            return Shift.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, f"Failed to get shift '{label}'")
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    # endregion

    # region Time Slots

    async def get_time_slots(
        self, offset: int = 0, limit: int = 100
    ) -> TimeSlotListResponse:
        """Get time slots with pagination.

        Args:
            offset: Starting record number (default 0)
            limit: Maximum number of time slots to return (default 100)

        Returns:
            TimeSlotListResponse: List of time slots with pagination info

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        url = urljoin(self.baseUrl, "/rest/ofscMetadata/v1/timeSlots")
        params = {"offset": offset, "limit": limit}

        try:
            response = await self._client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            # Remove links if not in model
            if "links" in data and not hasattr(TimeSlotListResponse, "links"):
                del data["links"]

            return TimeSlotListResponse.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, "Failed to get time slots")
            raise  # This will never execute, but satisfies type checker
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def get_time_slot(self, label: str) -> TimeSlot:
        """Get a single time slot by label.

        Note:
            The Oracle Field Service API does not support retrieving individual
            time slots by label. This method raises NotImplementedError.
            Use get_time_slots() and filter the results instead.

        Args:
            label: The time slot label to retrieve

        Returns:
            TimeSlot: The time slot details

        Raises:
            NotImplementedError: This operation is not supported by the Oracle API
        """
        raise NotImplementedError(
            "Oracle Field Service API does not support retrieving individual time slots by label. "
            "Use get_time_slots() and filter the results instead."
        )

    # endregion

    # region Work Skills

    async def get_workskills(
        self, offset: int = 0, limit: int = 100
    ) -> WorkskillListResponse:
        """Get all work skills with pagination.

        Args:
            offset: Starting record number (default 0)
            limit: Maximum number to return (default 100)

        Returns:
            WorkskillListResponse: List of work skills with pagination info

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        url = urljoin(self.baseUrl, "/rest/ofscMetadata/v1/workSkills")
        params = {"offset": offset, "limit": limit}

        try:
            response = await self._client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            if "links" in data:
                del data["links"]
            return WorkskillListResponse.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, "Failed to get work skills")
            raise  # This will never execute, but satisfies type checker
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def get_workskill(self, label: str) -> Workskill:
        """Get a single work skill by label.

        Args:
            label: The work skill label to retrieve

        Returns:
            Workskill: The work skill details

        Raises:
            OFSCNotFoundError: If work skill not found (404)
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        encoded_label = quote_plus(label)
        url = urljoin(self.baseUrl, f"/rest/ofscMetadata/v1/workSkills/{encoded_label}")

        try:
            response = await self._client.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            if "links" in data:
                del data["links"]
            return Workskill.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, f"Failed to get work skill '{label}'")
            raise  # This will never execute, but satisfies type checker
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def create_or_update_workskill(self, skill: Workskill) -> Workskill:
        """Create or update a work skill.

        Args:
            skill: The work skill to create or update

        Returns:
            Workskill: The created or updated work skill

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCValidationError: If validation fails (400, 422)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        encoded_label = quote_plus(skill.label)
        url = urljoin(self.baseUrl, f"/rest/ofscMetadata/v1/workSkills/{encoded_label}")

        try:
            response = await self._client.put(
                url, headers=self.headers, json=skill.model_dump(exclude_none=True)
            )
            response.raise_for_status()
            data = response.json()
            if "links" in data:
                del data["links"]
            return Workskill.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e, f"Failed to create/update work skill '{skill.label}'"
            )
            raise  # This will never execute, but satisfies type checker
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def delete_workskill(self, label: str) -> None:
        """Delete a work skill.

        Args:
            label: The work skill label to delete

        Raises:
            OFSCNotFoundError: If work skill not found (404)
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        encoded_label = quote_plus(label)
        url = urljoin(self.baseUrl, f"/rest/ofscMetadata/v1/workSkills/{encoded_label}")

        try:
            response = await self._client.delete(url, headers=self.headers)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, f"Failed to delete work skill '{label}'")
            raise  # This will never execute, but satisfies type checker
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def get_workskill_conditions(self) -> WorkskillConditionList:
        """Get all work skill conditions.

        Returns:
            WorkskillConditionList: List of work skill conditions

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        url = urljoin(self.baseUrl, "/rest/ofscMetadata/v1/workSkillConditions")

        try:
            response = await self._client.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            items = data.get("items", [])
            return WorkskillConditionList.model_validate(items)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, "Failed to get work skill conditions")
            raise  # This will never execute, but satisfies type checker
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def replace_workskill_conditions(
        self, data: WorkskillConditionList
    ) -> WorkskillConditionList:
        """Replace all work skill conditions.

        Note: Conditions not provided in the request are removed from the system.

        Args:
            data: List of work skill conditions to replace all existing ones

        Returns:
            WorkskillConditionList: The updated list of work skill conditions

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCValidationError: If validation fails (400, 422)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        url = urljoin(self.baseUrl, "/rest/ofscMetadata/v1/workSkillConditions")
        body = {"items": [item.model_dump(exclude_none=True) for item in data]}

        try:
            response = await self._client.put(url, headers=self.headers, json=body)
            response.raise_for_status()
            response_data = response.json()
            items = response_data.get("items", [])
            return WorkskillConditionList.model_validate(items)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, "Failed to replace work skill conditions")
            raise  # This will never execute, but satisfies type checker
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def get_workskill_groups(self) -> WorkskillGroupListResponse:
        """Get all work skill groups.

        Returns:
            WorkskillGroupListResponse: List of work skill groups with pagination info

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        url = urljoin(self.baseUrl, "/rest/ofscMetadata/v1/workSkillGroups")

        try:
            response = await self._client.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            if "links" in data:
                del data["links"]
            return WorkskillGroupListResponse.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, "Failed to get work skill groups")
            raise  # This will never execute, but satisfies type checker
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def get_workskill_group(self, label: str) -> WorkskillGroup:
        """Get a single work skill group by label.

        Args:
            label: The work skill group label to retrieve

        Returns:
            WorkskillGroup: The work skill group details

        Raises:
            OFSCNotFoundError: If work skill group not found (404)
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        encoded_label = quote_plus(label)
        url = urljoin(
            self.baseUrl, f"/rest/ofscMetadata/v1/workSkillGroups/{encoded_label}"
        )

        try:
            response = await self._client.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            if "links" in data:
                del data["links"]
            return WorkskillGroup.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, f"Failed to get work skill group '{label}'")
            raise  # This will never execute, but satisfies type checker
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def create_or_update_workskill_group(
        self, data: WorkskillGroup
    ) -> WorkskillGroup:
        """Create or update a work skill group.

        Args:
            data: The work skill group to create or update

        Returns:
            WorkskillGroup: The created or updated work skill group

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCValidationError: If validation fails (400, 422)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        encoded_label = quote_plus(data.label)
        url = urljoin(
            self.baseUrl, f"/rest/ofscMetadata/v1/workSkillGroups/{encoded_label}"
        )

        try:
            response = await self._client.put(
                url, headers=self.headers, json=data.model_dump(exclude_none=True)
            )
            response.raise_for_status()
            response_data = response.json()
            if "links" in response_data:
                del response_data["links"]
            return WorkskillGroup.model_validate(response_data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e, f"Failed to create/update work skill group '{data.label}'"
            )
            raise  # This will never execute, but satisfies type checker
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def delete_workskill_group(self, label: str) -> None:
        """Delete a work skill group.

        Args:
            label: The work skill group label to delete

        Raises:
            OFSCNotFoundError: If work skill group not found (404)
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        encoded_label = quote_plus(label)
        url = urljoin(
            self.baseUrl, f"/rest/ofscMetadata/v1/workSkillGroups/{encoded_label}"
        )

        try:
            response = await self._client.delete(url, headers=self.headers)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, f"Failed to delete work skill group '{label}'")
            raise  # This will never execute, but satisfies type checker
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    # endregion

    # region Work Zones

    async def get_workzones(
        self, offset: int = 0, limit: int = 100
    ) -> WorkzoneListResponse:
        """Get workzones with pagination.

        Args:
            offset: Starting record number (default 0)
            limit: Maximum number of workzones to return (default 100)

        Returns:
            WorkzoneListResponse: List of workzones with pagination info

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        url = urljoin(self.baseUrl, "/rest/ofscMetadata/v1/workZones")
        params = {"offset": offset, "limit": limit}

        try:
            response = await self._client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            # Remove links if not in model
            if "links" in data and not hasattr(WorkzoneListResponse, "links"):
                del data["links"]

            return WorkzoneListResponse.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, "Failed to get workzones")
            raise  # This will never execute, but satisfies type checker
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def get_workzone(self, label: str) -> Workzone:
        """Get a single workzone by label.

        Args:
            label: The workzone label to retrieve

        Returns:
            Workzone: The workzone details

        Raises:
            OFSCNotFoundError: If workzone not found (404)
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        url = urljoin(self.baseUrl, f"/rest/ofscMetadata/v1/workZones/{label}")

        try:
            response = await self._client.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            # Remove links if not in model
            if "links" in data and not hasattr(Workzone, "links"):
                del data["links"]

            return Workzone.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, f"Failed to get workzone '{label}'")
            raise  # This will never execute, but satisfies type checker
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def create_workzone(self, workzone: Workzone) -> Workzone:
        """Create a new workzone.

        Args:
            workzone: The workzone object to create

        Returns:
            Workzone: The created workzone

        Raises:
            OFSCConflictError: If the workzone already exists (409)
            OFSCValidationError: If validation fails (400)
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        url = urljoin(self.baseUrl, "/rest/ofscMetadata/v1/workZones")

        try:
            response = await self._client.post(
                url,
                headers=self.headers,
                content=workzone.model_dump_json(exclude_none=True),
            )
            response.raise_for_status()
            data = response.json()
            # Remove links if not in model
            if "links" in data and not hasattr(Workzone, "links"):
                del data["links"]

            return Workzone.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e, f"Failed to create workzone '{workzone.workZoneLabel}'"
            )
            raise  # This will never execute, but satisfies type checker
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def replace_workzone(
        self, workzone: Workzone, auto_resolve_conflicts: bool = False
    ) -> Workzone | None:
        """Replace an existing workzone.

        Args:
            workzone: The workzone object with updated data
            auto_resolve_conflicts: If True, automatically resolve conflicts (default False)

        Returns:
            Workzone | None: The updated workzone if status is 200, None if status is 204

        Raises:
            OFSCNotFoundError: If workzone not found (404)
            OFSCConflictError: If there are conflicts (409)
            OFSCValidationError: If validation fails (400)
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        url = urljoin(
            self.baseUrl,
            f"/rest/ofscMetadata/v1/workZones/{workzone.workZoneLabel}",
        )

        params = {}
        if auto_resolve_conflicts:
            params["autoResolveConflicts"] = "true"

        try:
            response = await self._client.put(
                url,
                headers=self.headers,
                content=workzone.model_dump_json(exclude_none=True),
                params=params if params else None,
            )
            response.raise_for_status()

            # API returns 200 with body or 204 with no content
            if response.status_code == 204:
                return None

            data = response.json()
            # Remove links if not in model
            if "links" in data and not hasattr(Workzone, "links"):
                del data["links"]

            return Workzone.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e, f"Failed to replace workzone '{workzone.workZoneLabel}'"
            )
            raise  # This will never execute, but satisfies type checker
        except OFSCNetworkError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    # endregion
