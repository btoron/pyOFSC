"""Async version of OFSMetadata API module."""

from collections.abc import AsyncGenerator
from pathlib import Path
from typing import Tuple
from urllib.parse import quote_plus, urljoin

import httpx

from ..exceptions import OFSCNetworkError
from ._base import AsyncClientBase
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
    CapacityAreaCapacityCategoriesResponse,
    CapacityAreaChildrenResponse,
    CapacityAreaListResponse,
    CapacityAreaOrganizationsResponse,
    CapacityAreaTimeIntervalsResponse,
    CapacityAreaTimeSlotsResponse,
    CapacityAreaWorkZonesResponse,
    CapacityAreaWorkZonesV1Response,
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
    PopulateStatusResponse,
    NonWorkingReason,
    NonWorkingReasonListResponse,
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
    ShiftUpdate,
    TimeSlot,
    TimeSlotListResponse,
    Workskill,
    WorkskillListResponse,
    WorkskillGroup,
    WorkskillGroupListResponse,
    WorkskillConditionList,
    Workzone,
    WorkzoneListResponse,
    WorkZoneKeyResponse,
)


class AsyncOFSMetadata(AsyncClientBase):
    """Async version of OFSMetadata API module."""

    # region Activity Type Groups

    async def get_activity_type_groups(self, offset: int = 0, limit: int = 100) -> ActivityTypeGroupListResponse:
        """Get activity type groups with pagination.

        :param offset: Starting record number (default 0)
        :type offset: int
        :param limit: Maximum number of activity type groups to return (default 100)
        :type limit: int
        :return: List of activity type groups with pagination info
        :rtype: ActivityTypeGroupListResponse
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        return await self._get_paginated_list(
            "/rest/ofscMetadata/v1/activityTypeGroups",
            ActivityTypeGroupListResponse,
            "Failed to get activity type groups",
            offset,
            limit,
        )

    async def get_activity_type_group(self, label: str) -> ActivityTypeGroup:
        """Get a single activity type group by label.

        :param label: The activity type group label to retrieve
        :type label: str
        :return: The activity type group details
        :rtype: ActivityTypeGroup
        :raises OFSCNotFoundError: If activity type group not found (404)
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        return await self._get_single_item(
            "/rest/ofscMetadata/v1/activityTypeGroups/{label}",
            label,
            ActivityTypeGroup,
            f"Failed to get activity type group '{label}'",
        )

    async def create_or_replace_activity_type_group(self, data: ActivityTypeGroup) -> ActivityTypeGroup:
        """Create or replace an activity type group.

        :param data: The activity type group to create or replace
        :type data: ActivityTypeGroup
        :return: The created or replaced activity type group
        :rtype: ActivityTypeGroup
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCValidationError: If validation fails (400, 422)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        encoded_label = quote_plus(data.label)
        return await self._put_item(
            f"/rest/ofscMetadata/v1/activityTypeGroups/{encoded_label}",
            data,
            ActivityTypeGroup,
            f"Failed to create/replace activity type group '{data.label}'",
        )

    # endregion

    # region Activity Types

    async def get_activity_types(self, offset: int = 0, limit: int = 100) -> ActivityTypeListResponse:
        """Get activity types with pagination.

        :param offset: Starting record number (default 0)
        :type offset: int
        :param limit: Maximum number of activity types to return (default 100)
        :type limit: int
        :return: List of activity types with pagination info
        :rtype: ActivityTypeListResponse
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        return await self._get_paginated_list(
            "/rest/ofscMetadata/v1/activityTypes",
            ActivityTypeListResponse,
            "Failed to get activity types",
            offset,
            limit,
        )

    async def get_activity_type(self, label: str) -> ActivityType:
        """Get a single activity type by label.

        :param label: The activity type label to retrieve
        :type label: str
        :return: The activity type details
        :rtype: ActivityType
        :raises OFSCNotFoundError: If activity type not found (404)
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        return await self._get_single_item(
            "/rest/ofscMetadata/v1/activityTypes/{label}",
            label,
            ActivityType,
            f"Failed to get activity type '{label}'",
        )

    async def create_or_replace_activity_type(self, data: ActivityType) -> ActivityType:
        """Create or replace an activity type.

        :param data: The activity type to create or replace
        :type data: ActivityType
        :return: The created or replaced activity type
        :rtype: ActivityType
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCValidationError: If validation fails (400, 422)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        encoded_label = quote_plus(data.label)
        return await self._put_item(
            f"/rest/ofscMetadata/v1/activityTypes/{encoded_label}",
            data,
            ActivityType,
            f"Failed to create/replace activity type '{data.label}'",
        )

    # endregion

    # region Applications

    async def get_applications(self) -> ApplicationListResponse:
        """Get all applications.

        :return: List of applications
        :rtype: ApplicationListResponse
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        return await self._get_all_items(
            "/rest/ofscMetadata/v1/applications",
            ApplicationListResponse,
            "Failed to get applications",
        )

    async def get_application(self, label: str) -> Application:
        """Get a single application by label.

        :param label: The application label to retrieve
        :type label: str
        :return: The application details
        :rtype: Application
        :raises OFSCNotFoundError: If application not found (404)
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        return await self._get_single_item(
            "/rest/ofscMetadata/v1/applications/{label}",
            label,
            Application,
            f"Failed to get application '{label}'",
        )

    async def get_application_api_accesses(self, label: str) -> ApplicationApiAccessListResponse:
        """Get all API accesses for an application.

        :param label: The application label
        :type label: str
        :return: List of API accesses
        :rtype: ApplicationApiAccessListResponse
        :raises OFSCNotFoundError: If application not found (404)
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        encoded_label = quote_plus(label)
        url = urljoin(
            self.baseUrl,
            f"/rest/ofscMetadata/v1/applications/{encoded_label}/apiAccess",
        )

        try:
            response = await self._client.get(url, headers=self.headers)
            response.raise_for_status()
            data = self._clean_response(response.json())
            return ApplicationApiAccessListResponse.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, f"Failed to get API accesses for application '{label}'")
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def get_application_api_access(self, label: str, access_id: str) -> ApplicationApiAccess:
        """Get a single API access for an application.

        :param label: The application label
        :type label: str
        :param access_id: The API access ID (e.g., "capacityAPI", "coreAPI")
        :type access_id: str
        :return: The API access details
        :rtype: ApplicationApiAccess
        :raises OFSCNotFoundError: If application or API access not found (404)
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        from ..models import parse_application_api_access

        encoded_label = quote_plus(label)
        encoded_access_id = quote_plus(access_id)
        url = urljoin(
            self.baseUrl,
            f"/rest/ofscMetadata/v1/applications/{encoded_label}/apiAccess/{encoded_access_id}",
        )

        try:
            response = await self._client.get(url, headers=self.headers)
            response.raise_for_status()
            data = self._clean_response(response.json())
            return parse_application_api_access(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e,
                f"Failed to get API access '{access_id}' for application '{label}'",
            )
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def create_or_replace_application(self, data: Application) -> Application:
        """Create or replace an application.

        :param data: The application to create or replace
        :type data: Application
        :return: The created or replaced application
        :rtype: Application
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCValidationError: If validation fails (400, 422)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        encoded_label = quote_plus(data.label)
        return await self._put_item(
            f"/rest/ofscMetadata/v1/applications/{encoded_label}",
            data,
            Application,
            f"Failed to create/replace application '{data.label}'",
        )

    async def update_application_api_access(self, label: str, api_label: str, data: dict) -> ApplicationApiAccess:
        """Update API access settings for an application.

        :param label: The application label
        :type label: str
        :param api_label: The API access label (e.g., "coreAPI", "capacityAPI")
        :type api_label: str
        :param data: Partial API access data to update
        :type data: dict
        :return: The updated API access
        :rtype: ApplicationApiAccess
        :raises OFSCNotFoundError: If application or API access not found (404)
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        from ..models import parse_application_api_access

        encoded_label = quote_plus(label)
        encoded_api_label = quote_plus(api_label)
        url = urljoin(
            self.baseUrl,
            f"/rest/ofscMetadata/v1/applications/{encoded_label}/apiAccess/{encoded_api_label}",
        )

        try:
            response = await self._client.patch(url, headers=self.headers, json=data)
            response.raise_for_status()
            result = self._clean_response(response.json())
            return parse_application_api_access(result)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e,
                f"Failed to update API access '{api_label}' for application '{label}'",
            )
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def generate_application_client_secret(self, label: str) -> dict:
        """Generate a new client secret for an application.

        :param label: The application label
        :type label: str
        :return: Response containing the new client secret
        :rtype: dict
        :raises OFSCNotFoundError: If application not found (404)
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        encoded_label = quote_plus(label)
        url = urljoin(
            self.baseUrl,
            f"/rest/ofscMetadata/v1/applications/{encoded_label}/custom-actions/generateClientSecret",
        )

        try:
            response = await self._client.post(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, f"Failed to generate client secret for application '{label}'")
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

        :param expandParent: If True, expands parent area details
        :type expandParent: bool
        :param fields: List of fields to return (default: all fields)
        :type fields: list[str] | None
        :param activeOnly: If True, return only active areas
        :type activeOnly: bool
        :param areasOnly: If True, return only areas (not categories)
        :type areasOnly: bool
        :return: List of capacity areas
        :rtype: CapacityAreaListResponse
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
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
            response = await self._client.get(url, headers=self.headers, params=params if params else None)
            response.raise_for_status()
            data = self._clean_response(response.json())
            return CapacityAreaListResponse.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, "Failed to get capacity areas")
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def get_capacity_area(self, label: str) -> CapacityArea:
        """Get a single capacity area by label.

        :param label: The capacity area label to retrieve
        :type label: str
        :return: The capacity area details
        :rtype: CapacityArea
        :raises OFSCNotFoundError: If capacity area not found (404)
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        return await self._get_single_item(
            "/rest/ofscMetadata/v1/capacityAreas/{label}",
            label,
            CapacityArea,
            f"Failed to get capacity area '{label}'",
        )

    async def get_capacity_area_capacity_categories(self, label: str) -> CapacityAreaCapacityCategoriesResponse:
        """Get capacity categories for a capacity area (ME012G).

        :param label: The capacity area label
        :type label: str
        :return: List of capacity categories for the area
        :rtype: CapacityAreaCapacityCategoriesResponse
        :raises OFSCNotFoundError: If capacity area not found (404)
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        encoded_label = quote_plus(label)
        return await self._get_all_items(
            f"/rest/ofscMetadata/v1/capacityAreas/{encoded_label}/capacityCategories",
            CapacityAreaCapacityCategoriesResponse,
            f"Failed to get capacity categories for area '{label}'",
        )

    async def get_capacity_area_workzones(self, label: str) -> CapacityAreaWorkZonesResponse:
        """Get workzones for a capacity area using v2 API (ME013G).

        :param label: The capacity area label
        :type label: str
        :return: List of workzones for the area
        :rtype: CapacityAreaWorkZonesResponse
        :raises OFSCNotFoundError: If capacity area not found (404)
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        encoded_label = quote_plus(label)
        return await self._get_all_items(
            f"/rest/ofscMetadata/v2/capacityAreas/{encoded_label}/workZones",
            CapacityAreaWorkZonesResponse,
            f"Failed to get workzones for capacity area '{label}'",
        )

    async def get_capacity_area_workzones_v1(self, label: str) -> CapacityAreaWorkZonesV1Response:
        """Get workzones for a capacity area using v1 API (ME014G).

        .. deprecated::
            Use get_capacity_area_workzones() (v2) instead, which returns richer data.

        :param label: The capacity area label
        :type label: str
        :return: List of workzone labels for the area
        :rtype: CapacityAreaWorkZonesV1Response
        :raises OFSCNotFoundError: If capacity area not found (404)
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        encoded_label = quote_plus(label)
        return await self._get_all_items(
            f"/rest/ofscMetadata/v1/capacityAreas/{encoded_label}/workZones",
            CapacityAreaWorkZonesV1Response,
            f"Failed to get workzones (v1) for capacity area '{label}'",
        )

    async def get_capacity_area_time_slots(self, label: str) -> CapacityAreaTimeSlotsResponse:
        """Get time slots for a capacity area (ME015G).

        :param label: The capacity area label
        :type label: str
        :return: List of time slots for the area
        :rtype: CapacityAreaTimeSlotsResponse
        :raises OFSCNotFoundError: If capacity area not found (404)
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        encoded_label = quote_plus(label)
        return await self._get_all_items(
            f"/rest/ofscMetadata/v1/capacityAreas/{encoded_label}/timeSlots",
            CapacityAreaTimeSlotsResponse,
            f"Failed to get time slots for capacity area '{label}'",
        )

    async def get_capacity_area_time_intervals(self, label: str) -> CapacityAreaTimeIntervalsResponse:
        """Get time intervals for a capacity area (ME016G).

        :param label: The capacity area label
        :type label: str
        :return: List of time intervals for the area
        :rtype: CapacityAreaTimeIntervalsResponse
        :raises OFSCNotFoundError: If capacity area not found (404)
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        encoded_label = quote_plus(label)
        return await self._get_all_items(
            f"/rest/ofscMetadata/v1/capacityAreas/{encoded_label}/timeIntervals",
            CapacityAreaTimeIntervalsResponse,
            f"Failed to get time intervals for capacity area '{label}'",
        )

    async def get_capacity_area_organizations(self, label: str) -> CapacityAreaOrganizationsResponse:
        """Get organizations for a capacity area (ME017G).

        :param label: The capacity area label
        :type label: str
        :return: List of organizations for the area
        :rtype: CapacityAreaOrganizationsResponse
        :raises OFSCNotFoundError: If capacity area not found (404)
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        encoded_label = quote_plus(label)
        return await self._get_all_items(
            f"/rest/ofscMetadata/v1/capacityAreas/{encoded_label}/organizations",
            CapacityAreaOrganizationsResponse,
            f"Failed to get organizations for capacity area '{label}'",
        )

    async def get_capacity_area_children(
        self,
        label: str,
        status: str | None = None,
        fields: list[str] | None = None,
        expand: str | None = None,
        type: str | None = None,
    ) -> CapacityAreaChildrenResponse:
        """Get child capacity areas for a capacity area (ME018G).

        :param label: The capacity area label
        :type label: str
        :param status: Filter by status (e.g. 'active', 'inactive')
        :type status: str | None
        :param fields: List of fields to return
        :type fields: list[str] | None
        :param expand: Comma-separated list of fields to expand
        :type expand: str | None
        :param type: Filter by type (e.g. 'area')
        :type type: str | None
        :return: List of child capacity areas
        :rtype: CapacityAreaChildrenResponse
        :raises OFSCNotFoundError: If capacity area not found (404)
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        encoded_label = quote_plus(label)
        url = urljoin(
            self.baseUrl,
            f"/rest/ofscMetadata/v1/capacityAreas/{encoded_label}/children",
        )

        params = {}
        if status is not None:
            params["status"] = status
        if fields is not None:
            params["fields"] = ",".join(fields)
        if expand is not None:
            params["expand"] = expand
        if type is not None:
            params["type"] = type

        try:
            response = await self._client.get(url, headers=self.headers, params=params if params else None)
            response.raise_for_status()
            data = self._clean_response(response.json())
            return CapacityAreaChildrenResponse.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, f"Failed to get children for capacity area '{label}'")
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    # endregion

    # region Capacity Categories

    async def get_capacity_categories(self, offset: int = 0, limit: int = 100) -> CapacityCategoryListResponse:
        """Get all capacity categories with pagination.

        :param offset: Starting record number (default 0)
        :type offset: int
        :param limit: Maximum number to return (default 100)
        :type limit: int
        :return: List of capacity categories
        :rtype: CapacityCategoryListResponse
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        return await self._get_paginated_list(
            "/rest/ofscMetadata/v1/capacityCategories",
            CapacityCategoryListResponse,
            "Failed to get capacity categories",
            offset,
            limit,
        )

    async def get_capacity_category(self, label: str) -> CapacityCategory:
        """Get a single capacity category by label.

        :param label: The capacity category label to retrieve
        :type label: str
        :return: The capacity category details
        :rtype: CapacityCategory
        :raises OFSCNotFoundError: If capacity category not found (404)
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        return await self._get_single_item(
            "/rest/ofscMetadata/v1/capacityCategories/{label}",
            label,
            CapacityCategory,
            f"Failed to get capacity category '{label}'",
        )

    async def create_or_replace_capacity_category(self, data: CapacityCategory) -> CapacityCategory:
        """Create or replace a capacity category.

        :param data: The capacity category to create or replace
        :type data: CapacityCategory
        :return: The created or replaced capacity category
        :rtype: CapacityCategory
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCValidationError: If validation fails (400, 422)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        encoded_label = quote_plus(data.label)
        return await self._put_item(
            f"/rest/ofscMetadata/v1/capacityCategories/{encoded_label}",
            data,
            CapacityCategory,
            f"Failed to create/replace capacity category '{data.label}'",
        )

    async def delete_capacity_category(self, label: str) -> None:
        """Delete a capacity category.

        :param label: The capacity category label to delete
        :type label: str
        :raises OFSCNotFoundError: If capacity category not found (404)
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        return await self._delete_item(
            "/rest/ofscMetadata/v1/capacityCategories/{label}",
            label,
            f"Failed to delete capacity category '{label}'",
        )

    # endregion

    # region Forms

    async def get_forms(self, offset: int = 0, limit: int = 100) -> FormListResponse:
        """Get all forms with pagination.

        :param offset: Starting record number (default 0)
        :type offset: int
        :param limit: Maximum number to return (default 100)
        :type limit: int
        :return: List of forms
        :rtype: FormListResponse
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        return await self._get_paginated_list(
            "/rest/ofscMetadata/v1/forms",
            FormListResponse,
            "Failed to get forms",
            offset,
            limit,
        )

    async def get_form(self, label: str) -> Form:
        """Get a single form by label.

        :param label: The form label to retrieve
        :type label: str
        :return: The form details
        :rtype: Form
        :raises OFSCNotFoundError: If form not found (404)
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        return await self._get_single_item(
            "/rest/ofscMetadata/v1/forms/{label}",
            label,
            Form,
            f"Failed to get form '{label}'",
        )

    async def create_or_replace_form(self, data: Form) -> Form:
        """Create or replace a form.

        :param data: The form to create or replace
        :type data: Form
        :return: The created or replaced form
        :rtype: Form
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCValidationError: If validation fails (400, 422)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        encoded_label = quote_plus(data.label)
        return await self._put_item(
            f"/rest/ofscMetadata/v1/forms/{encoded_label}",
            data,
            Form,
            f"Failed to create/replace form '{data.label}'",
        )

    async def delete_form(self, label: str) -> None:
        """Delete a form.

        :param label: The form label to delete
        :type label: str
        :raises OFSCNotFoundError: If form not found (404)
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        return await self._delete_item(
            "/rest/ofscMetadata/v1/forms/{label}",
            label,
            f"Failed to delete form '{label}'",
        )

    # endregion

    # region Inventory Types

    async def get_inventory_types(self, offset: int = 0, limit: int = 100) -> InventoryTypeListResponse:
        """Get inventory types with pagination.

        :param offset: Starting record number (default 0)
        :type offset: int
        :param limit: Maximum number to return (default 100)
        :type limit: int
        :return: List with pagination info
        :rtype: InventoryTypeListResponse
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        return await self._get_paginated_list(
            "/rest/ofscMetadata/v1/inventoryTypes",
            InventoryTypeListResponse,
            "Failed to get inventory types",
            offset,
            limit,
        )

    async def get_inventory_type(self, label: str) -> InventoryType:
        """Get a single inventory type by label.

        :param label: The inventory type label
        :type label: str
        :return: The inventory type details
        :rtype: InventoryType
        :raises OFSCNotFoundError: If inventory type not found (404)
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        return await self._get_single_item(
            "/rest/ofscMetadata/v1/inventoryTypes/{label}",
            label,
            InventoryType,
            f"Failed to get inventory type '{label}'",
        )

    async def create_or_replace_inventory_type(self, data: InventoryType) -> InventoryType:
        """Create or replace an inventory type.

        :param data: The inventory type to create or replace
        :type data: InventoryType
        :return: The created or replaced inventory type
        :rtype: InventoryType
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCValidationError: If validation fails (400, 422)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        encoded_label = quote_plus(data.label)
        return await self._put_item(
            f"/rest/ofscMetadata/v1/inventoryTypes/{encoded_label}",
            data,
            InventoryType,
            f"Failed to create/replace inventory type '{data.label}'",
        )

    # endregion

    # region Languages

    async def get_languages(self, offset: int = 0, limit: int = 100) -> LanguageListResponse:
        """Get languages with pagination.

        :param offset: Starting record number (default 0)
        :type offset: int
        :param limit: Maximum number to return (default 100)
        :type limit: int
        :return: List with pagination info
        :rtype: LanguageListResponse
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        return await self._get_paginated_list(
            "/rest/ofscMetadata/v1/languages",
            LanguageListResponse,
            "Failed to get languages",
            offset,
            limit,
        )

    async def get_language(self, label: str) -> Language:
        raise NotImplementedError(f"Async get_language({label!r}) not yet implemented")

    # endregion

    # region Link Templates

    async def get_link_templates(self, offset: int = 0, limit: int = 100) -> LinkTemplateListResponse:
        """Get link templates with pagination.

        :param offset: Starting record number (default 0)
        :type offset: int
        :param limit: Maximum number to return (default 100)
        :type limit: int
        :return: List with pagination info
        :rtype: LinkTemplateListResponse
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        return await self._get_paginated_list(
            "/rest/ofscMetadata/v1/linkTemplates",
            LinkTemplateListResponse,
            "Failed to get link templates",
            offset,
            limit,
        )

    async def get_link_template(self, label: str) -> LinkTemplate:
        """Get a single link template by label.

        :param label: The link template label
        :type label: str
        :return: The link template details
        :rtype: LinkTemplate
        :raises OFSCNotFoundError: If link template not found (404)
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        return await self._get_single_item(
            "/rest/ofscMetadata/v1/linkTemplates/{label}",
            label,
            LinkTemplate,
            f"Failed to get link template '{label}'",
        )

    async def create_link_template(self, data: LinkTemplate) -> LinkTemplate:
        """Create a new link template.

        :param data: The link template to create
        :type data: LinkTemplate
        :return: The created link template
        :rtype: LinkTemplate
        :raises OFSCConflictError: If link template already exists (409)
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCValidationError: If validation fails (400, 422)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        return await self._post_item(
            "/rest/ofscMetadata/v1/linkTemplates",
            data,
            LinkTemplate,
            "Failed to create link template",
        )

    async def update_link_template(self, data: LinkTemplate) -> LinkTemplate:
        """Update a link template (partial update).

        :param data: The link template with updated fields
        :type data: LinkTemplate
        :return: The updated link template
        :rtype: LinkTemplate
        :raises OFSCNotFoundError: If link template not found (404)
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCValidationError: If validation fails (400, 422)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        encoded_label = quote_plus(data.label)
        return await self._patch_item(
            f"/rest/ofscMetadata/v1/linkTemplates/{encoded_label}",
            data,
            LinkTemplate,
            f"Failed to update link template '{data.label}'",
        )

    # endregion

    # region Map Layers

    async def get_map_layers(self, offset: int = 0, limit: int = 100) -> MapLayerListResponse:
        """Get all map layers with pagination.

        :param offset: Starting record number (default 0)
        :type offset: int
        :param limit: Maximum number to return (default 100)
        :type limit: int
        :return: List of map layers
        :rtype: MapLayerListResponse
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        return await self._get_paginated_list(
            "/rest/ofscMetadata/v1/mapLayers",
            MapLayerListResponse,
            "Failed to get map layers",
            offset,
            limit,
        )

    async def get_map_layer(self, label: str) -> MapLayer:
        """Get a single map layer by label.

        :param label: The map layer label to retrieve
        :type label: str
        :return: The map layer details
        :rtype: MapLayer
        :raises OFSCNotFoundError: If map layer not found (404)
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        return await self._get_single_item(
            "/rest/ofscMetadata/v1/mapLayers/{label}",
            label,
            MapLayer,
            f"Failed to get map layer '{label}'",
        )

    async def create_or_replace_map_layer(self, data: MapLayer) -> MapLayer:
        """Create or replace a map layer.

        :param data: The map layer to create or replace
        :type data: MapLayer
        :return: The created or replaced map layer
        :rtype: MapLayer
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCValidationError: If validation fails (400, 422)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        encoded_label = quote_plus(data.label)
        return await self._put_item(
            f"/rest/ofscMetadata/v1/mapLayers/{encoded_label}",
            data,
            MapLayer,
            f"Failed to create/replace map layer '{data.label}'",
        )

    async def create_map_layer(self, data: MapLayer) -> MapLayer:
        """Create a new map layer.

        :param data: The map layer to create
        :type data: MapLayer
        :return: The created map layer
        :rtype: MapLayer
        :raises OFSCConflictError: If map layer already exists (409)
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCValidationError: If validation fails (400, 422)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        return await self._post_item(
            "/rest/ofscMetadata/v1/mapLayers",
            data,
            MapLayer,
            "Failed to create map layer",
        )

    async def populate_map_layers(self, data: bytes | Path) -> None:
        """Populate map layers from a file upload.

        :param data: File content as bytes or path to file
        :type data: bytes | Path
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCValidationError: If file is invalid (400, 422)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        url = urljoin(
            self.baseUrl,
            "/rest/ofscMetadata/v1/mapLayers/custom-actions/populateLayers",
        )

        if isinstance(data, Path):
            file_content = data.read_bytes()
            filename = data.name
        else:
            file_content = data
            filename = "mapLayers.csv"

        try:
            files = {"file": (filename, file_content, "application/octet-stream")}
            response = await self._client.post(url, headers=self.headers, files=files)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, "Failed to populate map layers")
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def get_populate_map_layers_status(self, download_id: int) -> PopulateStatusResponse:
        """Get the status of a populate map layers operation (ME030G).

        :param download_id: The download ID returned by the populate operation
        :type download_id: int
        :return: Status of the populate operation
        :rtype: PopulateStatusResponse
        :raises OFSCNotFoundError: If download ID not found (404)
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        url = urljoin(
            self.baseUrl,
            f"/rest/ofscMetadata/v1/mapLayers/custom-actions/populateLayers/{download_id}",
        )

        try:
            response = await self._client.get(url, headers=self.headers)
            response.raise_for_status()
            data = self._clean_response(response.json())
            return PopulateStatusResponse.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e,
                f"Failed to get populate map layers status for download_id={download_id}",
            )
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    # endregion

    # region Non-working Reasons

    async def get_non_working_reasons(self, offset: int = 0, limit: int = 100) -> NonWorkingReasonListResponse:
        """Get non-working reasons with pagination.

        :param offset: Starting record number (default 0)
        :type offset: int
        :param limit: Maximum number of non-working reasons to return (default 100)
        :type limit: int
        :return: List of non-working reasons with pagination info
        :rtype: NonWorkingReasonListResponse
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        return await self._get_paginated_list(
            "/rest/ofscMetadata/v1/nonWorkingReasons",
            NonWorkingReasonListResponse,
            "Failed to get non-working reasons",
            offset,
            limit,
        )

    async def get_non_working_reason(self, label: str) -> NonWorkingReason:
        """Get a single non-working reason by label.

        Note:
            The Oracle Field Service API does not support retrieving individual
            non-working reasons by label. This method raises NotImplementedError.
            Use get_non_working_reasons() and filter the results instead.

        :param label: The non-working reason label to retrieve
        :type label: str
        :raises NotImplementedError: This operation is not supported by the API
        """
        raise NotImplementedError(
            f"Oracle Field Service API does not support retrieving individual non-working reasons by label ({label!r}). "
            "Use get_non_working_reasons() and filter the results instead."
        )

    # endregion

    # region Organizations

    async def get_organizations(self) -> OrganizationListResponse:
        """Get all organizations.

        :return: List of organizations
        :rtype: OrganizationListResponse
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        return await self._get_all_items(
            "/rest/ofscMetadata/v1/organizations",
            OrganizationListResponse,
            "Failed to get organizations",
        )

    async def get_organization(self, label: str) -> Organization:
        """Get a single organization by label.

        :param label: The organization label
        :type label: str
        :return: The organization details
        :rtype: Organization
        :raises OFSCNotFoundError: If organization not found (404)
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        return await self._get_single_item(
            "/rest/ofscMetadata/v1/organizations/{label}",
            label,
            Organization,
            f"Failed to get organization '{label}'",
        )

    # endregion

    # region Plugins

    async def import_plugin_file(self, plugin: Path) -> None:
        """Import a plugin from a file.

        :param plugin: Path to the plugin XML file
        :type plugin: Path
        :return: None on success (204 No Content)
        :rtype: None
        :raises OFSCValidationError: If plugin XML is invalid (400)
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        url = urljoin(self.baseUrl, "/rest/ofscMetadata/v1/plugins/custom-actions/import")

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

        :param plugin: Plugin XML content as string
        :type plugin: str
        :return: None on success (204 No Content)
        :rtype: None
        :raises OFSCValidationError: If plugin XML is invalid (400)
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        url = urljoin(self.baseUrl, "/rest/ofscMetadata/v1/plugins/custom-actions/import")

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

    async def install_plugin(self, plugin_label: str) -> dict:
        """Install a plugin by label.

        :param plugin_label: The plugin label to install
        :type plugin_label: str
        :return: Response from the install action
        :rtype: dict
        :raises OFSCNotFoundError: If plugin not found (404)
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        encoded_label = quote_plus(plugin_label)
        url = urljoin(
            self.baseUrl,
            f"/rest/ofscMetadata/v1/plugins/{encoded_label}/custom-actions/install",
        )

        try:
            response = await self._client.post(url, headers=self.headers)
            response.raise_for_status()
            if response.status_code == 204 or not response.content:
                return {}
            return response.json()
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, f"Failed to install plugin '{plugin_label}'")
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    # endregion

    # region Properties

    async def get_properties(self, offset: int = 0, limit: int = 100) -> PropertyListResponse:
        """Get properties with pagination.

        :param offset: Starting record number (default 0)
        :type offset: int
        :param limit: Maximum number of properties to return (default 100)
        :type limit: int
        :return: List of properties with pagination info
        :rtype: PropertyListResponse
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        return await self._get_paginated_list(
            "/rest/ofscMetadata/v1/properties",
            PropertyListResponse,
            "Failed to get properties",
            offset,
            limit,
        )

    async def get_property(self, label: str) -> Property:
        """Get a single property by label.

        :param label: The property label to retrieve
        :type label: str
        :return: The property details
        :rtype: Property
        :raises OFSCNotFoundError: If property not found (404)
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        return await self._get_single_item(
            "/rest/ofscMetadata/v1/properties/{label}",
            label,
            Property,
            f"Failed to get property '{label}'",
        )

    async def create_or_replace_property(self, property: Property) -> Property:
        """Create or replace a property.

        :param property: The property object to create or replace
        :type property: Property
        :return: The created or updated property
        :rtype: Property
        :raises OFSCValidationError: If validation fails (400)
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        encoded_label = quote_plus(property.label)
        return await self._put_item(
            f"/rest/ofscMetadata/v1/properties/{encoded_label}",
            property,
            Property,
            f"Failed to create or replace property '{property.label}'",
        )

    async def update_property(self, property: Property) -> Property:
        """Update a property (partial update).

        :param property: The property with updated fields
        :type property: Property
        :return: The updated property
        :rtype: Property
        :raises OFSCNotFoundError: If property not found (404)
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCValidationError: If validation fails (400, 422)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        encoded_label = quote_plus(property.label)
        return await self._patch_item(
            f"/rest/ofscMetadata/v1/properties/{encoded_label}",
            property,
            Property,
            f"Failed to update property '{property.label}'",
        )

    async def get_enumeration_values(self, label: str, offset: int = 0, limit: int = 100) -> EnumerationValueList:
        """Get enumeration values for a property.

        :param label: The property label
        :type label: str
        :param offset: Starting record number (default 0)
        :type offset: int
        :param limit: Maximum number of values to return (default 100)
        :type limit: int
        :return: List of enumeration values with pagination info
        :rtype: EnumerationValueList
        :raises OFSCNotFoundError: If property not found (404)
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        return await self._get_paginated_list(
            f"/rest/ofscMetadata/v1/properties/{label}/enumerationList",
            EnumerationValueList,
            f"Failed to get enumeration values for property '{label}'",
            offset,
            limit,
        )

    async def create_or_update_enumeration_value(self, label: str, value: Tuple[EnumerationValue, ...]) -> EnumerationValueList:
        """Create or update enumeration values for a property.

        :param label: The property label
        :type label: str
        :param value: Tuple of EnumerationValue objects to create or update
        :type value: Tuple[EnumerationValue, ...]
        :return: Updated list of enumeration values
        :rtype: EnumerationValueList
        :raises OFSCNotFoundError: If property not found (404)
        :raises OFSCValidationError: If validation fails (400)
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        url = urljoin(
            self.baseUrl,
            f"/rest/ofscMetadata/v1/properties/{label}/enumerationList",
        )
        data = {"items": [item.model_dump(mode="json") for item in value]}

        try:
            response = await self._client.put(url, headers=self.headers, json=data)
            response.raise_for_status()
            response_data = self._clean_response(response.json())
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

        :return: List of resource types
        :rtype: ResourceTypeListResponse
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        return await self._get_all_items(
            "/rest/ofscMetadata/v1/resourceTypes",
            ResourceTypeListResponse,
            "Failed to get resource types",
        )

    # endregion

    # region Routing Profiles

    async def get_routing_profiles(self, offset: int = 0, limit: int = 100) -> RoutingProfileList:
        """Get all routing profiles with pagination.

        :param offset: Starting record number (default 0)
        :type offset: int
        :param limit: Maximum number to return (default 100)
        :type limit: int
        :return: List of routing profiles with pagination info
        :rtype: RoutingProfileList
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        return await self._get_paginated_list(
            "/rest/ofscMetadata/v1/routingProfiles",
            RoutingProfileList,
            "Failed to get routing profiles",
            offset,
            limit,
        )

    async def get_routing_profile_plans(self, profile_label: str, offset: int = 0, limit: int = 100) -> RoutingPlanList:
        """Get all routing plans for a routing profile.

        :param profile_label: Routing profile label
        :type profile_label: str
        :param offset: Starting record number (default 0)
        :type offset: int
        :param limit: Maximum number to return (default 100)
        :type limit: int
        :return: List of routing plans with pagination info
        :rtype: RoutingPlanList
        :raises OFSCNotFoundError: If routing profile not found (404)
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        encoded_label = quote_plus(profile_label)
        return await self._get_paginated_list(
            f"/rest/ofscMetadata/v1/routingProfiles/{encoded_label}/plans",
            RoutingPlanList,
            f"Failed to get routing plans for profile '{profile_label}'",
            offset,
            limit,
        )

    async def export_routing_plan(self, profile_label: str, plan_label: str) -> RoutingPlanData:
        """Export a routing plan.

        :param profile_label: Routing profile label
        :type profile_label: str
        :param plan_label: Routing plan label
        :type plan_label: str
        :return: Complete routing plan configuration
        :rtype: RoutingPlanData
        :raises OFSCNotFoundError: If routing profile or plan not found (404)
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
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
            data = self._clean_response(response.json())
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

        :param profile_label: Routing profile label
        :type profile_label: str
        :param plan_label: Routing plan label
        :type plan_label: str
        :return: Raw binary content of the routing plan file
        :rtype: bytes
        :raises OFSCNotFoundError: If routing profile or plan not found (404)
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
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

        :param profile_label: Routing profile label
        :type profile_label: str
        :param plan_data: Binary plan data to import
        :type plan_data: bytes
        :return: Success returns None
        :rtype: None
        :raises OFSCNotFoundError: If routing profile not found (404)
        :raises OFSCConflictError: If plan already exists (409)
        :raises OFSCValidationError: If validation fails (400)
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
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
            self._handle_http_error(e, f"Failed to import routing plan to profile '{profile_label}'")
            raise  # This will never execute, but satisfies type checker
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def force_import_routing_plan(self, profile_label: str, plan_data: bytes) -> None:
        """Force import a routing plan (overwrite if exists).

        :param profile_label: Routing profile label
        :type profile_label: str
        :param plan_data: Binary plan data to import
        :type plan_data: bytes
        :return: Success returns None
        :rtype: None
        :raises OFSCNotFoundError: If routing profile not found (404)
        :raises OFSCValidationError: If validation fails (400)
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
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
            self._handle_http_error(e, f"Failed to force import routing plan to profile '{profile_label}'")
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

        :param profile_label: Routing profile label
        :type profile_label: str
        :param plan_label: Routing plan label
        :type plan_label: str
        :param resource_external_id: External ID of the resource
        :type resource_external_id: str
        :param date: Date in format YYYY-MM-DD
        :type date: str
        :return: None
        :rtype: None
        :raises OFSCNotFoundError: If routing profile, plan, or resource not found (404)
        :raises OFSCValidationError: If validation fails (400)
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
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

        :param offset: Starting record number (default 0)
        :type offset: int
        :param limit: Maximum number to return (default 100)
        :type limit: int
        :return: List of shifts
        :rtype: ShiftListResponse
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        return await self._get_paginated_list(
            "/rest/ofscMetadata/v1/shifts",
            ShiftListResponse,
            "Failed to get shifts",
            offset,
            limit,
        )

    async def get_shift(self, label: str) -> Shift:
        """Get a single shift by label.

        :param label: The shift label to retrieve
        :type label: str
        :return: The shift details
        :rtype: Shift
        :raises OFSCNotFoundError: If shift not found (404)
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        return await self._get_single_item(
            "/rest/ofscMetadata/v1/shifts/{label}",
            label,
            Shift,
            f"Failed to get shift '{label}'",
        )

    async def create_or_replace_shift(self, data: Shift | ShiftUpdate) -> Shift:
        """Create or replace a shift.

        :param data: The shift to create or replace
        :type data: Shift
        :return: The created or replaced shift
        :rtype: Shift
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCValidationError: If validation fails (400, 422)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        encoded_label = quote_plus(data.label)
        url = urljoin(self.baseUrl, f"/rest/ofscMetadata/v1/shifts/{encoded_label}")

        try:
            response = await self._client.put(
                url,
                headers=self.headers,
                json=data.model_dump(exclude_none=True, mode="json"),
            )
            response.raise_for_status()
            result = self._clean_response(response.json())
            return Shift.model_validate(result)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, f"Failed to create/replace shift '{data.label}'")
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def delete_shift(self, label: str) -> None:
        """Delete a shift.

        :param label: The shift label to delete
        :type label: str
        :raises OFSCNotFoundError: If shift not found (404)
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        return await self._delete_item(
            "/rest/ofscMetadata/v1/shifts/{label}",
            label,
            f"Failed to delete shift '{label}'",
        )

    # endregion

    # region Time Slots

    async def get_time_slots(self, offset: int = 0, limit: int = 100) -> TimeSlotListResponse:
        """Get time slots with pagination.

        :param offset: Starting record number (default 0)
        :type offset: int
        :param limit: Maximum number of time slots to return (default 100)
        :type limit: int
        :return: List of time slots with pagination info
        :rtype: TimeSlotListResponse
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        return await self._get_paginated_list(
            "/rest/ofscMetadata/v1/timeSlots",
            TimeSlotListResponse,
            "Failed to get time slots",
            offset,
            limit,
        )

    async def get_time_slot(self, label: str) -> TimeSlot:
        """Get a single time slot by label.

        Note:
            The Oracle Field Service API does not support retrieving individual
            time slots by label. This method raises NotImplementedError.
            Use get_time_slots() and filter the results instead.

        :param label: The time slot label to retrieve
        :type label: str
        :return: The time slot details
        :rtype: TimeSlot
        :raises NotImplementedError: This operation is not supported by the Oracle API
        """
        raise NotImplementedError(
            f"Oracle Field Service API does not support retrieving individual time slots by label ({label!r}). "
            "Use get_time_slots() and filter the results instead."
        )

    # endregion

    # region Work Skills

    async def get_workskills(self, offset: int = 0, limit: int = 100) -> WorkskillListResponse:
        """Get all work skills with pagination.

        :param offset: Starting record number (default 0)
        :type offset: int
        :param limit: Maximum number to return (default 100)
        :type limit: int
        :return: List of work skills with pagination info
        :rtype: WorkskillListResponse
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        return await self._get_paginated_list(
            "/rest/ofscMetadata/v1/workSkills",
            WorkskillListResponse,
            "Failed to get work skills",
            offset,
            limit,
        )

    async def get_workskill(self, label: str) -> Workskill:
        """Get a single work skill by label.

        :param label: The work skill label to retrieve
        :type label: str
        :return: The work skill details
        :rtype: Workskill
        :raises OFSCNotFoundError: If work skill not found (404)
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        return await self._get_single_item(
            "/rest/ofscMetadata/v1/workSkills/{label}",
            label,
            Workskill,
            f"Failed to get work skill '{label}'",
        )

    async def create_or_update_workskill(self, skill: Workskill) -> Workskill:
        """Create or update a work skill.

        :param skill: The work skill to create or update
        :type skill: Workskill
        :return: The created or updated work skill
        :rtype: Workskill
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCValidationError: If validation fails (400, 422)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        encoded_label = quote_plus(skill.label)
        return await self._put_item(
            f"/rest/ofscMetadata/v1/workSkills/{encoded_label}",
            skill,
            Workskill,
            f"Failed to create/update work skill '{skill.label}'",
        )

    async def delete_workskill(self, label: str) -> None:
        """Delete a work skill.

        :param label: The work skill label to delete
        :type label: str
        :raises OFSCNotFoundError: If work skill not found (404)
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        return await self._delete_item(
            "/rest/ofscMetadata/v1/workSkills/{label}",
            label,
            f"Failed to delete work skill '{label}'",
        )

    async def get_workskill_conditions(self) -> WorkskillConditionList:
        """Get all work skill conditions.

        :return: List of work skill conditions
        :rtype: WorkskillConditionList
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
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

    async def replace_workskill_conditions(self, data: WorkskillConditionList) -> WorkskillConditionList:
        """Replace all work skill conditions.

        Note: Conditions not provided in the request are removed from the system.

        :param data: List of work skill conditions to replace all existing ones
        :type data: WorkskillConditionList
        :return: The updated list of work skill conditions
        :rtype: WorkskillConditionList
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCValidationError: If validation fails (400, 422)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        url = urljoin(self.baseUrl, "/rest/ofscMetadata/v1/workSkillConditions")
        body = {"items": [item.model_dump(exclude_none=True, mode="json") for item in data]}

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

        :return: List of work skill groups with pagination info
        :rtype: WorkskillGroupListResponse
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        return await self._get_all_items(
            "/rest/ofscMetadata/v1/workSkillGroups",
            WorkskillGroupListResponse,
            "Failed to get work skill groups",
        )

    async def get_workskill_group(self, label: str) -> WorkskillGroup:
        """Get a single work skill group by label.

        :param label: The work skill group label to retrieve
        :type label: str
        :return: The work skill group details
        :rtype: WorkskillGroup
        :raises OFSCNotFoundError: If work skill group not found (404)
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        return await self._get_single_item(
            "/rest/ofscMetadata/v1/workSkillGroups/{label}",
            label,
            WorkskillGroup,
            f"Failed to get work skill group '{label}'",
        )

    async def create_or_update_workskill_group(self, data: WorkskillGroup) -> WorkskillGroup:
        """Create or update a work skill group.

        :param data: The work skill group to create or update
        :type data: WorkskillGroup
        :return: The created or updated work skill group
        :rtype: WorkskillGroup
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCValidationError: If validation fails (400, 422)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        encoded_label = quote_plus(data.label)
        return await self._put_item(
            f"/rest/ofscMetadata/v1/workSkillGroups/{encoded_label}",
            data,
            WorkskillGroup,
            f"Failed to create/update work skill group '{data.label}'",
        )

    async def delete_workskill_group(self, label: str) -> None:
        """Delete a work skill group.

        :param label: The work skill group label to delete
        :type label: str
        :raises OFSCNotFoundError: If work skill group not found (404)
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        return await self._delete_item(
            "/rest/ofscMetadata/v1/workSkillGroups/{label}",
            label,
            f"Failed to delete work skill group '{label}'",
        )

    # endregion

    # region Work Zones

    async def get_workzones(self, offset: int = 0, limit: int = 100) -> WorkzoneListResponse:
        """Get workzones with pagination.

        :param offset: Starting record number (default 0)
        :type offset: int
        :param limit: Maximum number of workzones to return (default 100)
        :type limit: int
        :return: List of workzones with pagination info
        :rtype: WorkzoneListResponse
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        return await self._get_paginated_list(
            "/rest/ofscMetadata/v1/workZones",
            WorkzoneListResponse,
            "Failed to get workzones",
            offset,
            limit,
        )

    async def get_workzone(self, label: str) -> Workzone:
        """Get a single workzone by label.

        :param label: The workzone label to retrieve
        :type label: str
        :return: The workzone details
        :rtype: Workzone
        :raises OFSCNotFoundError: If workzone not found (404)
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        return await self._get_single_item(
            "/rest/ofscMetadata/v1/workZones/{label}",
            label,
            Workzone,
            f"Failed to get workzone '{label}'",
        )

    async def get_all_workzones(self, limit: int = 100) -> AsyncGenerator[Workzone, None]:
        """Async generator that yields all workzones one by one, fetching pages on demand.

        :param limit: Maximum number of workzones to fetch per page (default 100)
        :type limit: int
        :return: Async generator yielding individual Workzone objects
        :rtype: AsyncGenerator[Workzone, None]
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        offset = 0
        has_more = True

        while has_more:
            response = await self.get_workzones(offset=offset, limit=limit)
            for workzone in response.items:
                yield workzone
            has_more = response.hasMore or False
            offset += len(response.items)
            if len(response.items) == 0:
                break

    async def create_workzone(self, workzone: Workzone) -> Workzone:
        """Create a new workzone.

        :param workzone: The workzone object to create
        :type workzone: Workzone
        :return: The created workzone
        :rtype: Workzone
        :raises OFSCConflictError: If the workzone already exists (409)
        :raises OFSCValidationError: If validation fails (400)
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        return await self._post_item(
            "/rest/ofscMetadata/v1/workZones",
            workzone,
            Workzone,
            f"Failed to create workzone '{workzone.workZoneLabel}'",
        )

    async def replace_workzone(self, workzone: Workzone, auto_resolve_conflicts: bool = False) -> Workzone | None:
        """Replace an existing workzone.

        :param workzone: The workzone object with updated data
        :type workzone: Workzone
        :param auto_resolve_conflicts: If True, automatically resolve conflicts (default False)
        :type auto_resolve_conflicts: bool
        :return: The updated workzone if status is 200, None if status is 204
        :rtype: Workzone | None
        :raises OFSCNotFoundError: If workzone not found (404)
        :raises OFSCConflictError: If there are conflicts (409)
        :raises OFSCValidationError: If validation fails (400)
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
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

            data = self._clean_response(response.json())
            return Workzone.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, f"Failed to replace workzone '{workzone.workZoneLabel}'")
            raise  # This will never execute, but satisfies type checker
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def replace_workzones(self, data: list[Workzone]) -> WorkzoneListResponse:
        """Bulk replace all workzones.

        Note: Workzones not provided in the request are removed from the system.

        :param data: List of workzones to replace all existing ones
        :type data: list[Workzone]
        :return: The updated list of workzones
        :rtype: WorkzoneListResponse
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCValidationError: If validation fails (400, 422)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        url = urljoin(self.baseUrl, "/rest/ofscMetadata/v1/workZones")
        body = {"items": [item.model_dump(exclude_none=True, mode="json") for item in data]}

        try:
            response = await self._client.put(url, headers=self.headers, json=body)
            response.raise_for_status()
            response_data = self._clean_response(response.json())
            return WorkzoneListResponse.model_validate(response_data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, "Failed to replace workzones")
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def update_workzones(self, data: list[Workzone]) -> WorkzoneListResponse:
        """Bulk partial update of workzones.

        :param data: List of workzones with fields to update
        :type data: list[Workzone]
        :return: The updated list of workzones
        :rtype: WorkzoneListResponse
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCValidationError: If validation fails (400, 422)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        url = urljoin(self.baseUrl, "/rest/ofscMetadata/v1/workZones")
        body = {"items": [item.model_dump(exclude_none=True, mode="json") for item in data]}

        try:
            response = await self._client.patch(url, headers=self.headers, json=body)
            response.raise_for_status()
            response_data = self._clean_response(response.json())
            return WorkzoneListResponse.model_validate(response_data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, "Failed to update workzones")
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def populate_workzone_shapes(self, data: bytes | Path) -> None:
        """Populate workzone shapes from a file upload.

        :param data: File content as bytes or path to file
        :type data: bytes | Path
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCValidationError: If file is invalid (400, 422)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        url = urljoin(
            self.baseUrl,
            "/rest/ofscMetadata/v1/workZones/custom-actions/populateShapes",
        )

        if isinstance(data, Path):
            file_content = data.read_bytes()
            filename = data.name
        else:
            file_content = data
            filename = "workzoneShapes.csv"

        try:
            files = {"file": (filename, file_content, "application/octet-stream")}
            response = await self._client.post(url, headers=self.headers, files=files)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, "Failed to populate workzone shapes")
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def get_populate_workzone_shapes_status(self, download_id: int) -> PopulateStatusResponse:
        """Get the status of a populate workzone shapes operation (ME057G).

        :param download_id: The download ID returned by the populate operation
        :type download_id: int
        :return: Status of the populate operation
        :rtype: PopulateStatusResponse
        :raises OFSCNotFoundError: If download ID not found (404)
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        url = urljoin(
            self.baseUrl,
            f"/rest/ofscMetadata/v1/workZones/custom-actions/populateShapes/{download_id}",
        )

        try:
            response = await self._client.get(url, headers=self.headers)
            response.raise_for_status()
            data = self._clean_response(response.json())
            return PopulateStatusResponse.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e,
                f"Failed to get populate workzone shapes status for download_id={download_id}",
            )
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def get_workzone_key(self) -> WorkZoneKeyResponse:
        """Get the workzone key configuration (ME059G).

        :return: The workzone key with current and optional pending elements
        :rtype: WorkZoneKeyResponse
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        return await self._get_all_items(
            "/rest/ofscMetadata/v1/workZoneKey",
            WorkZoneKeyResponse,
            "Failed to get workzone key",
        )

    # endregion
