"""Async resource methods mixin for OFSCore API."""

from datetime import date
from typing import Any, Protocol
from urllib.parse import quote_plus, urljoin

import httpx

from ...exceptions import OFSCNetworkError
from ...models import Inventory, InventoryListResponse
from ...models.resources import (
    AssignedLocationsResponse,
    CalendarView,
    CalendarsListResponse,
    Location,
    LocationListResponse,
    PositionHistoryResponse,
    Resource,
    ResourceAssistantsResponse,
    ResourceCreate,
    ResourceListResponse,
    ResourcePlansResponse,
    ResourceRouteResponse,
    ResourceUsersListResponse,
    ResourceWorkScheduleItem,
    ResourceWorkScheduleResponse,
    ResourceWorkskillAssignment,
    ResourceWorkskillListResponse,
    ResourceWorkzoneAssignment,
    ResourceWorkzoneListResponse,
)


class _CoreBaseProtocol(Protocol):
    """Type stub declaring what AsyncOFSCoreResourcesMixin expects from its base class."""

    _client: httpx.AsyncClient

    @property
    def baseUrl(self) -> str: ...

    @property
    def headers(self) -> dict: ...

    def _handle_http_error(
        self, e: httpx.HTTPStatusError, context: str = ""
    ) -> None: ...

    def _build_expand_param(
        self,
        inventories: bool,
        workskills: bool,
        workzones: bool,
        workschedules: bool,
    ) -> str | None: ...


class AsyncOFSCoreResourcesMixin:
    """Mixin providing async resource-related methods for AsyncOFSCore.

    Requires _client, baseUrl, headers, and _handle_http_error from base class.
    """

    # region Resources

    def _build_expand_param(
        self: _CoreBaseProtocol,
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
        self: _CoreBaseProtocol,
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

    async def get_calendars(
        self: _CoreBaseProtocol,
        resources: list[str],
        date_from: date,
        date_to: date,
    ) -> CalendarsListResponse:
        """Get calendars for the specified resources and date range.

        Args:
            resources: List of resource IDs to get calendars for.
            date_from: Start date of the range.
            date_to: End date of the range.

        Returns:
            CalendarsListResponse: List of calendars.

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        url = urljoin(self.baseUrl, "/rest/ofscCore/v1/calendars")
        params = {
            "resources": ",".join(resources),
            "dateFrom": date_from.isoformat(),
            "dateTo": date_to.isoformat(),
        }

        try:
            response = await self._client.get(url, headers=self.headers, params=params)
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
        self: _CoreBaseProtocol, resource_id: str, position_date: date
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
        self: _CoreBaseProtocol,
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
        self: _CoreBaseProtocol, resource_id: str, date_from: date, date_to: date
    ) -> ResourceAssistantsResponse:
        """Get assistant resources for a date range.

        Args:
            resource_id: The resource ID.
            date_from: Start date of the range.
            date_to: End date of the range.

        Returns:
            ResourceAssistantsResponse: List of assistant resources.

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        url = urljoin(
            self.baseUrl, f"/rest/ofscCore/v1/resources/{resource_id}/assistants"
        )
        params = {"dateFrom": date_from.isoformat(), "dateTo": date_to.isoformat()}

        try:
            response = await self._client.get(url, headers=self.headers, params=params)
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
        self: _CoreBaseProtocol, resource_id: str, date_from: date, date_to: date
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
        self: _CoreBaseProtocol, resource_id: str, offset: int = 0, limit: int = 100
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
        self: _CoreBaseProtocol,
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

        params: dict[str, Any] = {"offset": offset, "limit": limit}
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

    async def get_resource_inventories(
        self: _CoreBaseProtocol, resource_id: str
    ) -> InventoryListResponse:
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
        self: _CoreBaseProtocol, resource_id: str, location_id: int
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

    async def get_resource_locations(
        self: _CoreBaseProtocol, resource_id: str
    ) -> LocationListResponse:
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

    async def get_resource_plans(
        self: _CoreBaseProtocol, resource_id: str, date_from: date, date_to: date
    ) -> ResourcePlansResponse:
        """Get routing plans for a resource for a date range.

        Args:
            resource_id: The resource ID.
            date_from: Start date for retrieving plans.
            date_to: End date for retrieving plans.

        Returns:
            ResourcePlansResponse: List of resource routing plans.

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        url = urljoin(self.baseUrl, f"/rest/ofscCore/v1/resources/{resource_id}/plans")
        params = {"dateFrom": date_from.isoformat(), "dateTo": date_to.isoformat()}

        try:
            response = await self._client.get(url, headers=self.headers, params=params)
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
        self: _CoreBaseProtocol,
        resource_id: str,
        route_date: date,
        offset: int = 0,
        limit: int = 100,
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

    async def get_resource_users(
        self: _CoreBaseProtocol, resource_id: str
    ) -> ResourceUsersListResponse:
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
        self: _CoreBaseProtocol, resource_id: str, actual_date: date
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
        self: _CoreBaseProtocol, resource_id: str
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
        self: _CoreBaseProtocol, resource_id: str
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
        self: _CoreBaseProtocol,
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

        params: dict[str, Any] = {"offset": offset, "limit": limit}
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

    # region Write / Delete Operations

    async def create_resource(
        self: _CoreBaseProtocol,
        resource_id: str,
        data: "ResourceCreate | Resource | dict",
    ) -> Resource:
        """Create or replace a resource (PUT — idempotent).

        Args:
            resource_id: Resource identifier
            data: Resource data as Resource model or dict

        Returns:
            Resource: Created/updated resource details

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCValidationError: If data is invalid (400/422)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        if isinstance(data, ResourceCreate):
            body = data.model_dump(exclude_none=True)
        elif isinstance(data, dict):
            body = ResourceCreate.model_validate(data).model_dump(exclude_none=True)
        else:
            # Resource or other BaseModel — validate required create fields
            body = ResourceCreate.model_validate(
                data.model_dump(exclude_none=True)
            ).model_dump(exclude_none=True)

        url = urljoin(self.baseUrl, f"/rest/ofscCore/v1/resources/{resource_id}")

        try:
            response = await self._client.put(url, headers=self.headers, json=body)
            response.raise_for_status()
            return Resource.model_validate(response.json())
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, f"Failed to create resource '{resource_id}'")
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def create_resource_from_obj(
        self: _CoreBaseProtocol, resource_id: str, data: dict
    ) -> Resource:
        """Create or replace a resource from a dict (PUT — idempotent).

        Args:
            resource_id: Resource identifier
            data: Resource data as plain dict

        Returns:
            Resource: Created/updated resource details

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCValidationError: If data is invalid (400/422)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        url = urljoin(self.baseUrl, f"/rest/ofscCore/v1/resources/{resource_id}")

        try:
            response = await self._client.put(url, headers=self.headers, json=data)
            response.raise_for_status()
            return Resource.model_validate(response.json())
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e, f"Failed to create resource '{resource_id}' from dict"
            )
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def update_resource(
        self: _CoreBaseProtocol,
        resource_id: str,
        data: dict,
        identify_by_internal_id: bool = False,
    ) -> Resource:
        """Partially update a resource (PATCH).

        Args:
            resource_id: Resource identifier
            data: Partial resource data to update
            identify_by_internal_id: If True, identify resource by internal ID

        Returns:
            Resource: Updated resource details

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCNotFoundError: If resource not found (404)
            OFSCValidationError: If data is invalid (400/422)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        url = urljoin(self.baseUrl, f"/rest/ofscCore/v1/resources/{resource_id}")
        params = (
            {"identifyResourceBy": "resourceInternalId"}
            if identify_by_internal_id
            else None
        )

        try:
            response = await self._client.patch(
                url, headers=self.headers, json=data, params=params
            )
            response.raise_for_status()
            return Resource.model_validate(response.json())
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, f"Failed to update resource '{resource_id}'")
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def set_resource_users(
        self: _CoreBaseProtocol,
        *,
        resource_id: str,
        users: tuple[str, ...] | list[str],
    ) -> ResourceUsersListResponse:
        """Set (replace) users assigned to a resource (PUT).

        Args:
            resource_id: Resource identifier
            users: Sequence of user login names to assign

        Returns:
            ResourceUsersListResponse: Updated list of assigned users

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCNotFoundError: If resource not found (404)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        url = urljoin(self.baseUrl, f"/rest/ofscCore/v1/resources/{resource_id}/users")
        body = {"items": [{"login": user} for user in users]}

        try:
            response = await self._client.put(url, headers=self.headers, json=body)
            response.raise_for_status()
            data = response.json()
            if "links" in data:
                del data["links"]
            return ResourceUsersListResponse.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e, f"Failed to set users for resource '{resource_id}'"
            )
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def delete_resource_users(self: _CoreBaseProtocol, resource_id: str) -> None:
        """Remove all users from a resource (DELETE).

        Args:
            resource_id: Resource identifier

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCNotFoundError: If resource not found (404)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        url = urljoin(self.baseUrl, f"/rest/ofscCore/v1/resources/{resource_id}/users")

        try:
            response = await self._client.delete(url, headers=self.headers)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e, f"Failed to delete users for resource '{resource_id}'"
            )
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def set_resource_workschedules(
        self: _CoreBaseProtocol,
        resource_id: str,
        data: "ResourceWorkScheduleItem | dict",
    ) -> ResourceWorkScheduleResponse:
        """Add/update work schedule for a resource (POST).

        Args:
            resource_id: Resource identifier
            data: Work schedule item as model or dict

        Returns:
            ResourceWorkScheduleResponse: Updated work schedule

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCNotFoundError: If resource not found (404)
            OFSCValidationError: If data is invalid (400/422)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        url = urljoin(
            self.baseUrl, f"/rest/ofscCore/v1/resources/{resource_id}/workSchedules"
        )
        if isinstance(data, dict):
            body = data
        else:
            body = data.model_dump(exclude_none=True)

        try:
            response = await self._client.post(url, headers=self.headers, json=body)
            response.raise_for_status()
            resp_data = response.json()
            if "links" in resp_data:
                del resp_data["links"]
            return ResourceWorkScheduleResponse.model_validate(resp_data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e, f"Failed to set workschedules for resource '{resource_id}'"
            )
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def bulk_update_resource_workzones(
        self: _CoreBaseProtocol, *, data: dict
    ) -> dict:
        """Bulk update work zones for multiple resources (POST).

        Args:
            data: Bulk update payload

        Returns:
            dict: API response

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCValidationError: If data is invalid (400/422)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        url = urljoin(
            self.baseUrl,
            "/rest/ofscCore/v1/resources/custom-actions/bulkUpdateWorkZones",
        )

        try:
            response = await self._client.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, "Failed to bulk update resource workzones")
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def bulk_update_resource_workskills(
        self: _CoreBaseProtocol, *, data: dict
    ) -> dict:
        """Bulk update work skills for multiple resources (POST).

        Args:
            data: Bulk update payload

        Returns:
            dict: API response

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCValidationError: If data is invalid (400/422)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        url = urljoin(
            self.baseUrl,
            "/rest/ofscCore/v1/resources/custom-actions/bulkUpdateWorkSkills",
        )

        try:
            response = await self._client.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, "Failed to bulk update resource workskills")
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def bulk_update_resource_workschedules(
        self: _CoreBaseProtocol, *, data: dict
    ) -> dict:
        """Bulk update work schedules for multiple resources (POST).

        Args:
            data: Bulk update payload

        Returns:
            dict: API response

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCValidationError: If data is invalid (400/422)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        url = urljoin(
            self.baseUrl,
            "/rest/ofscCore/v1/resources/custom-actions/bulkUpdateWorkSchedules",
        )

        try:
            response = await self._client.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, "Failed to bulk update resource workschedules")
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def create_resource_location(
        self: _CoreBaseProtocol, resource_id: str, *, location: "Location | dict"
    ) -> Location:
        """Create a new location for a resource (POST — returns 201).

        Args:
            resource_id: Resource identifier
            location: Location data as Location model or dict

        Returns:
            Location: Created location details

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCNotFoundError: If resource not found (404)
            OFSCValidationError: If data is invalid (400/422)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        url = urljoin(
            self.baseUrl, f"/rest/ofscCore/v1/resources/{resource_id}/locations"
        )
        if isinstance(location, dict):
            body = location
        else:
            body = location.model_dump(
                exclude={"locationId"}, exclude_unset=True, exclude_none=True
            )

        try:
            response = await self._client.post(url, headers=self.headers, json=body)
            response.raise_for_status()
            return Location.model_validate(response.json())
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e, f"Failed to create location for resource '{resource_id}'"
            )
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def delete_resource_location(
        self: _CoreBaseProtocol, resource_id: str, location_id: int
    ) -> None:
        """Delete a location from a resource (DELETE — returns 204).

        Args:
            resource_id: Resource identifier
            location_id: Location ID to delete

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCNotFoundError: If resource or location not found (404)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        url = urljoin(
            self.baseUrl,
            f"/rest/ofscCore/v1/resources/{resource_id}/locations/{location_id}",
        )

        try:
            response = await self._client.delete(url, headers=self.headers)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e,
                f"Failed to delete location {location_id} for resource '{resource_id}'",
            )
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def set_assigned_locations(
        self: _CoreBaseProtocol,
        resource_id: str,
        data: "AssignedLocationsResponse | dict",
    ) -> AssignedLocationsResponse:
        """Set (replace) assigned locations for a resource (PUT).

        Args:
            resource_id: Resource identifier
            data: Assigned locations data as model or dict

        Returns:
            AssignedLocationsResponse: Updated assigned locations

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCNotFoundError: If resource not found (404)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        url = urljoin(
            self.baseUrl,
            f"/rest/ofscCore/v1/resources/{resource_id}/assignedLocations",
        )
        if isinstance(data, dict):
            body = data
        else:
            body = data.model_dump(exclude_none=True, exclude_unset=True)

        try:
            response = await self._client.put(url, headers=self.headers, json=body)
            response.raise_for_status()
            return AssignedLocationsResponse.model_validate(response.json())
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e, f"Failed to set assigned locations for resource '{resource_id}'"
            )
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def create_resource_inventory(
        self: _CoreBaseProtocol,
        resource_id: str,
        inventory_data: "Inventory | dict",
    ) -> Inventory:
        """Create an inventory item for a resource (POST).

        Args:
            resource_id: Resource identifier
            inventory_data: Inventory data as model or dict

        Returns:
            Inventory: Created inventory item

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCNotFoundError: If resource not found (404)
            OFSCValidationError: If data is invalid (400/422)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        url = urljoin(
            self.baseUrl, f"/rest/ofscCore/v1/resources/{resource_id}/inventories"
        )
        if isinstance(inventory_data, dict):
            body = inventory_data
        else:
            body = inventory_data.model_dump(exclude_none=True)

        try:
            response = await self._client.post(url, headers=self.headers, json=body)
            response.raise_for_status()
            return Inventory.model_validate(response.json())
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e, f"Failed to create inventory for resource '{resource_id}'"
            )
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def install_resource_inventory(
        self: _CoreBaseProtocol, resource_id: str, inventory_id: int
    ) -> Inventory:
        """Install an inventory item for a resource (POST custom-action).

        Args:
            resource_id: Resource identifier
            inventory_id: Inventory ID to install

        Returns:
            Inventory: Updated inventory item

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCNotFoundError: If resource or inventory not found (404)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        url = urljoin(
            self.baseUrl,
            f"/rest/ofscCore/v1/resources/{resource_id}/inventories/{inventory_id}/custom-actions/install",
        )

        try:
            response = await self._client.post(url, headers=self.headers)
            response.raise_for_status()
            return Inventory.model_validate(response.json())
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e,
                f"Failed to install inventory {inventory_id} for resource '{resource_id}'",
            )
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def set_resource_workskills(
        self: _CoreBaseProtocol,
        resource_id: str,
        workskills: "list[ResourceWorkskillAssignment | dict]",
    ) -> ResourceWorkskillListResponse:
        """Set (replace) work skills for a resource (POST).

        Args:
            resource_id: Resource identifier
            workskills: List of work skill assignments as models or dicts

        Returns:
            ResourceWorkskillListResponse: Updated work skill assignments

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCNotFoundError: If resource not found (404)
            OFSCValidationError: If data is invalid (400/422)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        url = urljoin(
            self.baseUrl, f"/rest/ofscCore/v1/resources/{resource_id}/workSkills"
        )
        items = []
        for ws in workskills:
            if isinstance(ws, dict):
                items.append(ws)
            else:
                items.append(ws.model_dump(exclude_none=True))
        body = {"items": items}

        try:
            response = await self._client.post(url, headers=self.headers, json=body)
            response.raise_for_status()
            data = response.json()
            if "links" in data:
                del data["links"]
            return ResourceWorkskillListResponse.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e, f"Failed to set workskills for resource '{resource_id}'"
            )
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def delete_resource_workskill(
        self: _CoreBaseProtocol, resource_id: str, workskill: str
    ) -> None:
        """Delete a specific work skill from a resource (DELETE — returns 204).

        Args:
            resource_id: Resource identifier
            workskill: Work skill label to remove

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCNotFoundError: If resource or workskill not found (404)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        url = urljoin(
            self.baseUrl,
            f"/rest/ofscCore/v1/resources/{resource_id}/workSkills/{workskill}",
        )

        try:
            response = await self._client.delete(url, headers=self.headers)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e,
                f"Failed to delete workskill '{workskill}' from resource '{resource_id}'",
            )
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def set_resource_workzones(
        self: _CoreBaseProtocol,
        resource_id: str,
        workzones: "list[ResourceWorkzoneAssignment | dict]",
    ) -> ResourceWorkzoneListResponse:
        """Set (replace) work zones for a resource (POST).

        Args:
            resource_id: Resource identifier
            workzones: List of work zone assignments as models or dicts

        Returns:
            ResourceWorkzoneListResponse: Updated work zone assignments

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCNotFoundError: If resource not found (404)
            OFSCValidationError: If data is invalid (400/422)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        url = urljoin(
            self.baseUrl, f"/rest/ofscCore/v1/resources/{resource_id}/workZones"
        )
        items = []
        for wz in workzones:
            if isinstance(wz, dict):
                items.append(wz)
            else:
                items.append(wz.model_dump(exclude_none=True))
        body = {"items": items}

        try:
            response = await self._client.post(url, headers=self.headers, json=body)
            response.raise_for_status()
            data = response.json()
            if "links" in data:
                del data["links"]
            return ResourceWorkzoneListResponse.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e, f"Failed to set workzones for resource '{resource_id}'"
            )
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def delete_resource_workzone(
        self: _CoreBaseProtocol, resource_id: str, workzone_item_id: int
    ) -> None:
        """Delete a specific work zone from a resource (DELETE — returns 204).

        Args:
            resource_id: Resource identifier
            workzone_item_id: Work zone item ID to remove

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCNotFoundError: If resource or workzone not found (404)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        url = urljoin(
            self.baseUrl,
            f"/rest/ofscCore/v1/resources/{resource_id}/workZones/{workzone_item_id}",
        )

        try:
            response = await self._client.delete(url, headers=self.headers)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e,
                f"Failed to delete workzone {workzone_item_id} from resource '{resource_id}'",
            )
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def delete_resource_workschedule(
        self: _CoreBaseProtocol, resource_id: str, schedule_item_id: int
    ) -> None:
        """Delete a specific work schedule item from a resource (DELETE — returns 204).

        Args:
            resource_id: Resource identifier
            schedule_item_id: Schedule item ID to remove

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCNotFoundError: If resource or schedule item not found (404)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        url = urljoin(
            self.baseUrl,
            f"/rest/ofscCore/v1/resources/{resource_id}/workSchedules/{schedule_item_id}",
        )

        try:
            response = await self._client.delete(url, headers=self.headers)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e,
                f"Failed to delete workschedule {schedule_item_id} from resource '{resource_id}'",
            )
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def update_resource_location(
        self: _CoreBaseProtocol,
        resource_id: str,
        location_id: int,
        data: dict,
    ) -> Location:
        """Partially update a location for a resource (PATCH).

        Args:
            resource_id: Resource identifier
            location_id: Location ID to update
            data: Partial location data to update

        Returns:
            Location: Updated location details

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCNotFoundError: If resource or location not found (404)
            OFSCValidationError: If data is invalid (400/422)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        url = urljoin(
            self.baseUrl,
            f"/rest/ofscCore/v1/resources/{resource_id}/locations/{location_id}",
        )

        try:
            response = await self._client.patch(url, headers=self.headers, json=data)
            response.raise_for_status()
            return Location.model_validate(response.json())
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e,
                f"Failed to update location {location_id} for resource '{resource_id}'",
            )
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    # endregion

    # endregion

    # region File Properties

    async def get_resource_file_property(
        self: _CoreBaseProtocol,
        resource_id: str,
        property_label: str,
        media_type: str = "application/octet-stream",
    ) -> bytes:
        """Get a binary file property for a resource.

        Args:
            resource_id: Resource identifier
            property_label: Property label (e.g., 'csign')
            media_type: Expected MIME type (default: application/octet-stream)

        Returns:
            bytes: Binary content of the property

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCNotFoundError: If resource or property not found (404)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        encoded_resource_id = quote_plus(resource_id)
        encoded_label = quote_plus(property_label)
        url = urljoin(
            self.baseUrl,
            f"/rest/ofscCore/v1/resources/{encoded_resource_id}/{encoded_label}",
        )
        headers = {**self.headers, "Accept": media_type}

        try:
            response = await self._client.get(url, headers=headers)
            response.raise_for_status()
            return response.content
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e,
                f"Failed to get property '{property_label}' for resource '{resource_id}'",
            )
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def set_resource_file_property(
        self: _CoreBaseProtocol,
        resource_id: str,
        property_label: str,
        content: bytes,
        filename: str,
        content_type: str = "application/octet-stream",
    ) -> None:
        """Upload a binary file property for a resource.

        Args:
            resource_id: Resource identifier
            property_label: Property label (e.g., 'csign')
            content: Binary content to upload
            filename: Filename for the Content-Disposition header
            content_type: MIME type of the content (default: application/octet-stream)

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCNotFoundError: If resource not found (404)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        encoded_resource_id = quote_plus(resource_id)
        encoded_label = quote_plus(property_label)
        url = urljoin(
            self.baseUrl,
            f"/rest/ofscCore/v1/resources/{encoded_resource_id}/{encoded_label}",
        )
        base_headers = {k: v for k, v in self.headers.items() if k != "Content-Type"}
        headers = {
            **base_headers,
            "Content-Type": content_type,
            "Content-Disposition": f'attachment; filename="{filename}"',
        }

        try:
            response = await self._client.put(url, headers=headers, content=content)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e,
                f"Failed to set property '{property_label}' for resource '{resource_id}'",
            )
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def delete_resource_file_property(
        self: _CoreBaseProtocol,
        resource_id: str,
        property_label: str,
    ) -> None:
        """Delete a binary file property for a resource.

        Args:
            resource_id: Resource identifier
            property_label: Property label to delete

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCNotFoundError: If resource or property not found (404)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        encoded_resource_id = quote_plus(resource_id)
        encoded_label = quote_plus(property_label)
        url = urljoin(
            self.baseUrl,
            f"/rest/ofscCore/v1/resources/{encoded_resource_id}/{encoded_label}",
        )

        try:
            response = await self._client.delete(url, headers=self.headers)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e,
                f"Failed to delete property '{property_label}' for resource '{resource_id}'",
            )
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    # endregion
