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
    ActivityTypeGroup,
    ActivityTypeGroupListResponse,
    ActivityTypeListResponse,
    Application,
    ApplicationListResponse,
    CapacityArea,
    CapacityAreaListResponse,
    CapacityCategory,
    CapacityCategoryListResponse,
    EnumerationValue,
    EnumerationValueList,
    InventoryType,
    InventoryTypeListResponse,
    OFSConfig,
    Organization,
    OrganizationListResponse,
    Property,
    PropertyListResponse,
    RoutingPlanData,
    RoutingPlanList,
    RoutingProfileList,
    TimeSlot,
    TimeSlotListResponse,
    Workskill,
    WorkSkillGroup,
    WorkSkillGroupListResponse,
    Workzone,
    WorkzoneListResponse,
    WorskillConditionList,
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
        raise NotImplementedError("Async method not yet implemented")

    async def get_activity_type(self, label: str):
        raise NotImplementedError("Async method not yet implemented")

    # endregion

    # region Applications

    async def get_applications(self) -> ApplicationListResponse:
        raise NotImplementedError("Async method not yet implemented")

    async def get_application(self, label: str) -> Application:
        raise NotImplementedError("Async method not yet implemented")

    async def get_application_api_accesses(self, label: str):
        raise NotImplementedError("Async method not yet implemented")

    async def get_application_api_access(self, label: str, accessId: str):
        raise NotImplementedError("Async method not yet implemented")

    # endregion

    # region Capacity Areas

    async def get_capacity_areas(
        self,
        expandParent: bool = False,
        fields: list[str] | None = None,
        activeOnly: bool = False,
        areasOnly: bool = False,
    ) -> CapacityAreaListResponse:
        raise NotImplementedError("Async method not yet implemented")

    async def get_capacity_area(self, label: str) -> CapacityArea:
        raise NotImplementedError("Async method not yet implemented")

    # endregion

    # region Capacity Categories

    async def get_capacity_categories(
        self, offset: int = 0, limit: int = 100
    ) -> CapacityCategoryListResponse:
        raise NotImplementedError("Async method not yet implemented")

    async def get_capacity_category(self, label: str) -> CapacityCategory:
        raise NotImplementedError("Async method not yet implemented")

    # endregion

    # region Forms

    async def get_forms(self, offset: int = 0, limit: int = 100):
        raise NotImplementedError("Async method not yet implemented")

    async def get_form(self, label: str):
        raise NotImplementedError("Async method not yet implemented")

    # endregion

    # region Inventory Types

    async def get_inventory_types(self) -> InventoryTypeListResponse:
        raise NotImplementedError("Async method not yet implemented")

    async def get_inventory_type(self, label: str) -> InventoryType:
        raise NotImplementedError("Async method not yet implemented")

    # endregion

    # region Languages

    async def get_languages(self, offset: int = 0, limit: int = 100):
        raise NotImplementedError("Async method not yet implemented")

    async def get_language(self, label: str):
        raise NotImplementedError("Async method not yet implemented")

    # endregion

    # region Link Templates

    async def get_link_templates(self, offset: int = 0, limit: int = 100):
        raise NotImplementedError("Async method not yet implemented")

    async def get_link_template(self, label: str):
        raise NotImplementedError("Async method not yet implemented")

    # endregion

    # region Map Layers

    async def get_map_layers(self, offset: int = 0, limit: int = 100):
        raise NotImplementedError("Async method not yet implemented")

    async def get_map_layer(self, label: str):
        raise NotImplementedError("Async method not yet implemented")

    # endregion

    # region Non-working Reasons

    async def get_non_working_reasons(self, offset: int = 0, limit: int = 100):
        raise NotImplementedError("Async method not yet implemented")

    async def get_non_working_reason(self, label: str):
        raise NotImplementedError("Async method not yet implemented")

    # endregion

    # region Organizations

    async def get_organizations(self) -> OrganizationListResponse:
        raise NotImplementedError("Async method not yet implemented")

    async def get_organization(self, label: str) -> Organization:
        raise NotImplementedError("Async method not yet implemented")

    # endregion

    # region Plugins

    async def import_plugin_file(self, plugin: Path):
        raise NotImplementedError("Async method not yet implemented")

    async def import_plugin(self, plugin: str):
        raise NotImplementedError("Async method not yet implemented")

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

    async def get_resource_types(self):
        raise NotImplementedError("Async method not yet implemented")

    # endregion

    # region Routing Profiles

    async def get_routing_profiles(
        self, offset: int = 0, limit: int = 100
    ) -> RoutingProfileList:
        raise NotImplementedError("Async method not yet implemented")

    async def get_routing_profile_plans(
        self, profile_label: str, offset: int = 0, limit: int = 100
    ) -> RoutingPlanList:
        raise NotImplementedError("Async method not yet implemented")

    async def export_routing_plan(
        self, profile_label: str, plan_label: str
    ) -> RoutingPlanData:
        raise NotImplementedError("Async method not yet implemented")

    async def export_plan_file(self, profile_label: str, plan_label: str) -> bytes:
        raise NotImplementedError("Async method not yet implemented")

    async def import_routing_plan(self, profile_label: str, plan_data: bytes):
        raise NotImplementedError("Async method not yet implemented")

    async def force_import_routing_plan(self, profile_label: str, plan_data: bytes):
        raise NotImplementedError("Async method not yet implemented")

    async def start_routing_plan(
        self,
        profile_label: str,
        plan_label: str,
        resource_external_id: str,
        date: str,
    ):
        raise NotImplementedError("Async method not yet implemented")

    # endregion

    # region Shifts

    async def get_shifts(self, offset: int = 0, limit: int = 100):
        raise NotImplementedError("Async method not yet implemented")

    async def get_shift(self, label: str):
        raise NotImplementedError("Async method not yet implemented")

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

    async def get_workskills(self, offset: int = 0, limit: int = 100):
        raise NotImplementedError("Async method not yet implemented")

    async def get_workskill(self, label: str):
        raise NotImplementedError("Async method not yet implemented")

    async def create_or_update_workskill(self, skill: Workskill):
        raise NotImplementedError("Async method not yet implemented")

    async def delete_workskill(self, label: str):
        raise NotImplementedError("Async method not yet implemented")

    async def get_workskill_conditions(self):
        raise NotImplementedError("Async method not yet implemented")

    async def replace_workskill_conditions(self, data: WorskillConditionList):
        raise NotImplementedError("Async method not yet implemented")

    async def get_workskill_groups(self) -> WorkSkillGroupListResponse:
        raise NotImplementedError("Async method not yet implemented")

    async def get_workskill_group(self, label: str) -> WorkSkillGroup:
        raise NotImplementedError("Async method not yet implemented")

    async def create_or_update_workskill_group(self, data: WorkSkillGroup):
        raise NotImplementedError("Async method not yet implemented")

    async def delete_workskill_group(self, label: str):
        raise NotImplementedError("Async method not yet implemented")

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
