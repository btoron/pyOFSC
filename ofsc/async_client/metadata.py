"""Async version of OFSMetadata API module."""

from pathlib import Path
from typing import Tuple

import httpx

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
    RoutingPlanData,
    RoutingPlanList,
    RoutingProfileList,
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

    # region Activity Type Groups

    async def get_activity_type_groups(
        self, offset: int = 0, limit: int = 100
    ) -> ActivityTypeGroupListResponse:
        raise NotImplementedError("Async method not yet implemented")

    async def get_activity_type_group(self, label: str) -> ActivityTypeGroup:
        raise NotImplementedError("Async method not yet implemented")

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
        fields: list[str] = None,
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

    async def get_properties(self, offset: int = 0, limit: int = 100):
        raise NotImplementedError("Async method not yet implemented")

    async def get_property(self, label: str):
        raise NotImplementedError("Async method not yet implemented")

    async def create_or_replace_property(self, property: Property):
        raise NotImplementedError("Async method not yet implemented")

    async def get_enumeration_values(
        self, label: str, offset: int = 0, limit: int = 100
    ) -> EnumerationValueList:
        raise NotImplementedError("Async method not yet implemented")

    async def create_or_update_enumeration_value(
        self, label: str, value: Tuple[EnumerationValue, ...]
    ) -> EnumerationValueList:
        raise NotImplementedError("Async method not yet implemented")

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

    async def get_time_slots(self, offset: int = 0, limit: int = 100):
        raise NotImplementedError("Async method not yet implemented")

    async def get_time_slot(self, label: str):
        raise NotImplementedError("Async method not yet implemented")

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
        """
        from urllib.parse import urljoin

        url = urljoin(self.baseUrl, "/rest/ofscMetadata/v1/workZones")
        params = {"offset": offset, "limit": limit}

        response = await self._client.get(url, headers=self.headers, params=params)
        response.raise_for_status()

        data = response.json()
        # Remove links if not in model
        if "links" in data and not hasattr(WorkzoneListResponse, "links"):
            del data["links"]

        return WorkzoneListResponse.model_validate(data)

    async def get_workzone(self, label: str) -> Workzone:
        """Get a single workzone by label.

        Args:
            label: The workzone label to retrieve

        Returns:
            Workzone: The workzone details
        """
        from urllib.parse import urljoin

        url = urljoin(self.baseUrl, f"/rest/ofscMetadata/v1/workZones/{label}")

        response = await self._client.get(url, headers=self.headers)
        response.raise_for_status()

        data = response.json()
        # Remove links if not in model
        if "links" in data and not hasattr(Workzone, "links"):
            del data["links"]

        return Workzone.model_validate(data)

    async def replace_workzone(
        self, workzone: Workzone, auto_resolve_conflicts: bool = False
    ) -> Workzone:
        raise NotImplementedError("Async method not yet implemented")

    # endregion
