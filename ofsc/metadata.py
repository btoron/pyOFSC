import urllib
from pathlib import Path
from typing import Tuple
from urllib.parse import urljoin

import requests

from .common import FULL_RESPONSE, OBJ_RESPONSE, wrap_return
from .models import (
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
    OFSApi,
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


class OFSMetadata(OFSApi):
    # region Properties

    ## 202202 Properties and file properties

    @wrap_return(response_type=OBJ_RESPONSE, expected=[200])
    def get_properties(self, offset=0, limit=100):
        url = urljoin(self.baseUrl, "/rest/ofscMetadata/v1/properties")
        params = {"offset": offset, "limit": limit}
        response = requests.get(
            url,
            headers=self.headers,
            params=params,
        )
        return response

    # 202209 Get Property
    @wrap_return(response_type=OBJ_RESPONSE, expected=[200])
    def get_property(self, label: str):
        url = urljoin(self.baseUrl, f"/rest/ofscMetadata/v1/properties/{label}")
        response = requests.get(url, headers=self.headers)
        return response

    # 202209 Create Property
    @wrap_return(response_type=OBJ_RESPONSE, expected=[200])
    def create_or_replace_property(self, property: Property):
        url = urljoin(
            self.baseUrl, f"/rest/ofscMetadata/v1/properties/{property.label}"
        )
        response = requests.put(
            url, headers=self.headers, data=property.model_dump_json().encode("utf-8")
        )
        return response

    # 202412 Get Enumerated Property Values
    @wrap_return(response_type=OBJ_RESPONSE, expected=[200], model=EnumerationValueList)
    def get_enumeration_values(self, label: str, offset=0, limit=100):
        url = urljoin(
            self.baseUrl, f"/rest/ofscMetadata/v1/properties/{label}/enumerationList"
        )
        params = {
            "offset": offset,
            "limit": limit,
        }
        response = requests.get(
            url,
            headers=self.headers,
            params=params,
        )
        return response

    # 202503 Update or create Enumeration Value
    @wrap_return(response_type=OBJ_RESPONSE, expected=[200], model=EnumerationValueList)
    def create_or_update_enumeration_value(
        self, label: str, value: Tuple[EnumerationValue, ...]
    ):
        url = urljoin(
            self.baseUrl,
            f"/rest/ofscMetadata/v1/properties/{label}/enumerationList",
        )
        data = {"items": [item.model_dump() for item in value]}
        response = requests.put(url, headers=self.headers, json=data)
        return response

    # endregion

    # 202208 Skill management

    # 202208 Workzones
    @wrap_return(response_type=OBJ_RESPONSE, expected=[200], model=WorkzoneListResponse)
    def get_workzones(
        self,
        offset=0,
        limit=100,
    ):
        url = urljoin(self.baseUrl, "/rest/ofscMetadata/v1/workZones")
        params = {"offset": offset, "limit": limit}
        response = requests.get(
            url,
            headers=self.headers,
            params=params,
        )
        return response

    @wrap_return(response_type=OBJ_RESPONSE, expected=[200, 204], model=Workzone)
    def replace_workzone(
        self,
        workzone: Workzone,
        auto_resolve_conflicts: bool = False,
    ):
        url = urljoin(
            self.baseUrl,
            f"/rest/ofscMetadata/v1/workZones/{workzone.workZoneLabel}",
        )
        params = {}
        if auto_resolve_conflicts:
            params["autoResolveConflicts"] = "true"
        response = requests.put(
            url,
            headers=self.headers,
            data=workzone.model_dump_json(exclude_none=True),
            params=params if params else None,
        )
        return response

    # 202209 Resource Types
    @wrap_return(response_type=OBJ_RESPONSE, expected=[200])
    def get_resource_types(self):
        url = urljoin(self.baseUrl, "/rest/ofscMetadata/v1/resourceTypes")
        response = requests.get(url, headers=self.headers)
        return response

    # 202212 Import plugin
    @wrap_return(response_type=OBJ_RESPONSE, expected=[204])
    def import_plugin_file(self, plugin: Path):
        url = urljoin(
            self.baseUrl, "/rest/ofscMetadata/v1/plugins/custom-actions/import"
        )
        files = [("pluginFile", (plugin.name, plugin.read_text(), "text/xml"))]
        response = requests.post(url, headers=self.headers, files=files)
        return response

    # 202212 Import plugin
    @wrap_return(response_type=OBJ_RESPONSE, expected=[204])
    def import_plugin(self, plugin: str):
        url = urljoin(
            self.baseUrl, "/rest/ofscMetadata/v1/plugins/custom-actions/import"
        )
        files = [("pluginFile", ("noname.xml", plugin, "text/xml"))]
        response = requests.post(url, headers=self.headers, files=files)
        return response

    @wrap_return(response_type=OBJ_RESPONSE, expected=[200])
    def get_workskills(self, offset=0, limit=100, response_type=FULL_RESPONSE):
        url = urljoin(self.baseUrl, "/rest/ofscMetadata/v1/workSkills")
        params = {"offset": offset, "limit": limit}
        response = requests.get(
            url,
            headers=self.headers,
            params=params,
        )
        return response

    @wrap_return(response_type=OBJ_RESPONSE, expected=[200])
    def get_workskill(self, label: str, response_type=FULL_RESPONSE):
        url = urljoin(self.baseUrl, f"/rest/ofscMetadata/v1/workSkills/{label}")
        response = requests.get(
            url,
            headers=self.headers,
        )
        return response

    @wrap_return(response_type=OBJ_RESPONSE, expected=[200])
    def create_or_update_workskill(self, skill: Workskill, response_type=FULL_RESPONSE):
        url = urljoin(self.baseUrl, f"/rest/ofscMetadata/v1/workSkills/{skill.label}")
        response = requests.put(url, headers=self.headers, data=skill.model_dump_json())
        return response

    @wrap_return(response_type=OBJ_RESPONSE, expected=[204])
    def delete_workskill(self, label: str, response_type=FULL_RESPONSE):
        url = urljoin(self.baseUrl, f"/rest/ofscMetadata/v1/workSkills/{label}")
        response = requests.delete(url, headers=self.headers)
        return response

    # Workskill conditions
    @wrap_return(response_type=OBJ_RESPONSE, expected=[200])
    def get_workskill_conditions(self, response_type=FULL_RESPONSE):
        url = urljoin(self.baseUrl, "/rest/ofscMetadata/v1/workSkillConditions")
        response = requests.get(
            url,
            headers=self.headers,
        )
        return response

    @wrap_return(response_type=OBJ_RESPONSE, expected=[200])
    def replace_workskill_conditions(
        self, data: WorskillConditionList, response_type=FULL_RESPONSE
    ):
        url = urljoin(self.baseUrl, "/rest/ofscMetadata/v1/workSkillConditions")
        content = '{"items":' + data.model_dump_json(exclude_none=True) + "}"
        headers = self.headers
        headers["Content-Type"] = "application/json"
        response = requests.put(url, headers=headers, data=content)
        return response

    #####
    # Migration to OFS 2.0 model format

    # 202402 Metadata - Activity Type Groups
    @wrap_return(
        response_type=OBJ_RESPONSE, expected=[200], model=ActivityTypeGroupListResponse
    )
    def get_activity_type_groups(self, offset=0, limit=100):
        url = urljoin(self.baseUrl, "/rest/ofscMetadata/v1/activityTypeGroups")
        params = {"offset": offset, "limit": limit}
        response = requests.get(url, headers=self.headers, params=params)
        return response

    @wrap_return(response_type=OBJ_RESPONSE, expected=[200], model=ActivityTypeGroup)
    def get_activity_type_group(self, label):
        encoded_label = urllib.parse.quote_plus(label)
        url = urljoin(
            self.baseUrl,
            f"/rest/ofscMetadata/v1/activityTypeGroups/{encoded_label}",
        )
        response = requests.get(url, headers=self.headers)
        return response

    ## 202402 Activity Type
    @wrap_return(
        response_type=OBJ_RESPONSE, expected=[200], model=ActivityTypeListResponse
    )
    def get_activity_types(self, offset=0, limit=100):
        url = urljoin(self.baseUrl, "/rest/ofscMetadata/v1/activityTypes")
        params = {"offset": offset, "limit": limit}
        response = requests.get(url, headers=self.headers, params=params)
        return response

    @wrap_return(response_type=OBJ_RESPONSE, expected=[200])
    def get_activity_type(self, label):
        encoded_label = urllib.parse.quote_plus(label)
        url = urljoin(
            self.baseUrl, "/rest/ofscMetadata/v1/activityTypes/{}".format(encoded_label)
        )
        response = requests.get(url, headers=self.headers)
        return response

    # region Capacity Areas
    capacityAreasFields = [
        "label",
        "name",
        "type",
        "status",
        "parent.name",
        "parent.label",
    ]

    @wrap_return(
        response_type=OBJ_RESPONSE, expected=[200], model=CapacityAreaListResponse
    )
    def get_capacity_areas(
        self,
        expandParent: bool = False,
        fields: list[str] = ["label"],
        activeOnly: bool = False,
        areasOnly: bool = False,
    ):
        url = urljoin(self.baseUrl, "/rest/ofscMetadata/v1/capacityAreas")
        assert isinstance(fields, list)
        params = {
            "expand": None if not expandParent else "parent",
            "fields": (
                ",".join(fields) if fields else ",".join(self.capacityAreasFields)
            ),
            "status": None if not activeOnly else "active",
            "type": None if not areasOnly else "area",
        }
        response = requests.get(url, params=params, headers=self.headers)
        return response

    @wrap_return(response_type=OBJ_RESPONSE, expected=[200], model=CapacityArea)
    def get_capacity_area(self, label: str):
        encoded_label = urllib.parse.quote_plus(label)
        url = urljoin(
            self.baseUrl, f"/rest/ofscMetadata/v1/capacityAreas/{encoded_label}"
        )
        response = requests.get(url, headers=self.headers)
        return response

    # endregion

    # region 202402 Metadata - Capacity Categories
    @wrap_return(
        response_type=OBJ_RESPONSE, expected=[200], model=CapacityCategoryListResponse
    )
    def get_capacity_categories(self, offset=0, limit=100):
        url = urljoin(self.baseUrl, "/rest/ofscMetadata/v1/capacityCategories")
        params = {"offset": offset, "limit": limit}
        response = requests.get(url, headers=self.headers, params=params)
        return response

    @wrap_return(response_type=OBJ_RESPONSE, expected=[200], model=CapacityCategory)
    def get_capacity_category(self, label: str):
        encoded_label = urllib.parse.quote_plus(label)
        url = urljoin(
            self.baseUrl, f"/rest/ofscMetadata/v1/capacityCategories/{encoded_label}"
        )
        response = requests.get(url, headers=self.headers)
        return response

    # endregion

    # region 202405 Inventory Types
    @wrap_return(
        response_type=OBJ_RESPONSE, expected=[200], model=InventoryTypeListResponse
    )
    def get_inventory_types(self):
        url = urljoin(self.baseUrl, "/rest/ofscMetadata/v1/inventoryTypes")
        response = requests.get(url, headers=self.headers)
        return response

    @wrap_return(response_type=OBJ_RESPONSE, expected=[200], model=InventoryType)
    def get_inventory_type(self, label: str):
        encoded_label = urllib.parse.quote_plus(label)
        url = urljoin(
            self.baseUrl, f"/rest/ofscMetadata/v1/inventoryTypes/{encoded_label}"
        )
        response = requests.get(url, headers=self.headers)
        return response

    # endregion

    # region 202410 Metadata - Workskill Groups
    @wrap_return(
        response_type=OBJ_RESPONSE, expected=[200], model=WorkSkillGroupListResponse
    )
    def get_workskill_groups(self):
        url = urljoin(self.baseUrl, "/rest/ofscMetadata/v1/workSkillGroups")
        response = requests.get(url, headers=self.headers)
        return response

    @wrap_return(response_type=OBJ_RESPONSE, expected=[200], model=WorkSkillGroup)
    def get_workskill_group(self, label: str):
        url = urljoin(self.baseUrl, f"/rest/ofscMetadata/v1/workSkillGroups/{label}")
        response = requests.get(url, headers=self.headers)
        return response

    @wrap_return(response_type=OBJ_RESPONSE, expected=[200])
    def create_or_update_workskill_group(self, data: WorkSkillGroup):
        label = data.label
        url = urljoin(self.baseUrl, f"/rest/ofscMetadata/v1/workSkillGroups/{label}")
        response = requests.put(url, headers=self.headers, json=data.model_dump())
        return response

    @wrap_return(response_type=OBJ_RESPONSE, expected=[204])
    def delete_workskill_group(self, label: str):
        url = urljoin(self.baseUrl, f"/rest/ofscMetadata/v1/workSkillGroups/{label}")
        response = requests.delete(url, headers=self.headers)
        return response

    # endregion 202410 Metadata - Workskill Groups
    # region Applications
    @wrap_return(
        response_type=OBJ_RESPONSE, expected=[200], model=ApplicationListResponse
    )
    def get_applications(self):
        url = urljoin(self.baseUrl, "/rest/ofscMetadata/v1/applications")
        response = requests.get(url, headers=self.headers)
        return response

    @wrap_return(response_type=OBJ_RESPONSE, expected=[200], model=Application)
    def get_application(self, label: str):
        url = urljoin(self.baseUrl, f"/rest/ofscMetadata/v1/applications/{label}")
        response = requests.get(url, headers=self.headers)
        return response

    @wrap_return(response_type=OBJ_RESPONSE, expected=[200])
    def get_application_api_accesses(self, label: str):
        url = urljoin(
            self.baseUrl, f"/rest/ofscMetadata/v1/applications/{label}/apiAccess"
        )
        response = requests.get(url, headers=self.headers)
        return response

    @wrap_return(response_type=OBJ_RESPONSE, expected=[200])
    def get_application_api_access(self, label: str, accessId: str):
        url = urljoin(
            self.baseUrl,
            f"/rest/ofscMetadata/v1/applications/{label}/apiAccess/{accessId}",
        )
        response = requests.get(url, headers=self.headers)
        return response

    # endregion Applications
    # region Organizations
    @wrap_return(
        response_type=OBJ_RESPONSE, expected=[200], model=OrganizationListResponse
    )
    def get_organizations(self):
        url = urljoin(self.baseUrl, "/rest/ofscMetadata/v1/organizations")
        response = requests.get(url, headers=self.headers)
        return response

    @wrap_return(response_type=OBJ_RESPONSE, expected=[200], model=Organization)
    def get_organization(self, label: str):
        url = urljoin(self.baseUrl, f"/rest/ofscMetadata/v1/organizations/{label}")
        response = requests.get(url, headers=self.headers)
        return response

    # endregion Organizations

    # region 202510 Routing Profiles
    @wrap_return(response_type=OBJ_RESPONSE, expected=[200], model=RoutingProfileList)
    def get_routing_profiles(self, offset=0, limit=100):
        """Get all routing profiles

        A routing profile is a group of routing plans that enables assignment
        to multiple buckets without duplicating plans.

        Args:
            offset: Pagination offset (default: 0)
            limit: Maximum number of items to return (default: 100)

        Returns:
            RoutingProfileList: List of routing profiles with pagination info
        """
        url = urljoin(self.baseUrl, "/rest/ofscMetadata/v1/routingProfiles")
        params = {"offset": offset, "limit": limit}
        response = requests.get(url, headers=self.headers, params=params)
        return response

    @wrap_return(response_type=OBJ_RESPONSE, expected=[200], model=RoutingPlanList)
    def get_routing_profile_plans(self, profile_label: str, offset=0, limit=100):
        """Get routing plans for a specific profile

        Args:
            profile_label: Label of the routing profile
            offset: Pagination offset (default: 0)
            limit: Maximum number of items to return (default: 100)

        Returns:
            RoutingPlanList: List of routing plans with pagination info
        """
        encoded_label = urllib.parse.quote_plus(profile_label)
        url = urljoin(
            self.baseUrl, f"/rest/ofscMetadata/v1/routingProfiles/{encoded_label}/plans"
        )
        params = {"offset": offset, "limit": limit}
        response = requests.get(url, headers=self.headers, params=params)
        return response

    @wrap_return(response_type=OBJ_RESPONSE, expected=[200], model=RoutingPlanData)
    def export_routing_plan(self, profile_label: str, plan_label: str):
        """Export a routing plan

        Args:
            profile_label: Label of the routing profile
            plan_label: Label of the routing plan to export

        Returns:
            RoutingPlanData: Parsed routing plan configuration with all settings,
                            including activity groups, optimization parameters, and costs
        """
        encoded_profile = urllib.parse.quote_plus(profile_label)
        encoded_plan = urllib.parse.quote_plus(plan_label)
        url = urljoin(
            self.baseUrl,
            f"/rest/ofscMetadata/v1/routingProfiles/{encoded_profile}/plans/{encoded_plan}/custom-actions/export",
        )
        headers = self.headers.copy()
        headers["Accept"] = "application/octet-stream"
        response = requests.get(url, headers=headers)
        return response

    def export_plan_file(self, profile_label: str, plan_label: str) -> bytes:
        """Export routing plan as raw bytes ready for import

        This method exports a routing plan in the exact format needed for import operations.
        Unlike export_routing_plan which returns a Response object that can be parsed,
        this returns raw bytes that can be directly used with import_routing_plan or
        force_import_routing_plan.

        Args:
            profile_label: Label of the routing profile
            plan_label: Label of the routing plan to export

        Returns:
            bytes: Raw plan data ready for import/force_import operations

        Example:
            # Export and re-import a plan to a different profile
            plan_bytes = instance.metadata.export_plan_file("Profile1", "Plan1")
            response = instance.metadata.force_import_routing_plan(
                profile_label="Profile2",
                plan_data=plan_bytes
            )

        Note:
            The returned bytes contain the complete routing plan configuration
            including all settings, activity groups, and optimization parameters.
        """
        encoded_profile = urllib.parse.quote_plus(profile_label)
        encoded_plan = urllib.parse.quote_plus(plan_label)
        url = urljoin(
            self.baseUrl,
            f"/rest/ofscMetadata/v1/routingProfiles/{encoded_profile}/plans/{encoded_plan}/custom-actions/export",
        )
        headers = self.headers.copy()
        headers["Accept"] = "application/octet-stream"
        response = requests.get(url, headers=headers)
        return response.content

    @wrap_return(response_type=OBJ_RESPONSE, expected=[200, 409])
    def import_routing_plan(self, profile_label: str, plan_data: bytes):
        """Import a routing plan into a routing profile

        Imports a routing plan from exported plan data. If a plan with the same label
        already exists in the profile, this will return a 409 Conflict error indicating
        that force_import_routing_plan should be used instead.

        Args:
            profile_label: Label of the target routing profile
            plan_data: Raw plan data as bytes (from export_plan_file or export_routing_plan)

        Returns:
            Response object with status 200 on success, 409 if plan already exists

        Example:
            # Import a plan to a different profile
            plan_bytes = instance.metadata.export_plan_file("Profile1", "Plan1")
            response = instance.metadata.import_routing_plan(
                profile_label="Profile2",
                plan_data=plan_bytes,
                response_type=FULL_RESPONSE
            )

        Note:
            If the response is 409, the response will include "force": "required" in the JSON
            body, indicating that force_import_routing_plan should be used to overwrite.
        """
        encoded_label = urllib.parse.quote_plus(profile_label)
        url = urljoin(
            self.baseUrl,
            f"/rest/ofscMetadata/v1/routingProfiles/{encoded_label}/plans/custom-actions/import",
        )
        headers = self.headers.copy()
        headers["Content-Type"] = "application/octet-stream"
        response = requests.put(url, headers=headers, data=plan_data)
        return response

    @wrap_return(response_type=OBJ_RESPONSE, expected=[200])
    def force_import_routing_plan(self, profile_label: str, plan_data: bytes):
        """Force import a routing plan, overwriting if it already exists

        Imports a routing plan from exported plan data, overwriting any existing plan
        with the same label in the profile. This is useful for restoring backups or
        updating existing plans.

        Args:
            profile_label: Label of the target routing profile
            plan_data: Raw plan data as bytes (from export_plan_file or export_routing_plan)

        Returns:
            Response object with status 200 on success

        Example:
            # Export and restore a plan (backup/restore)
            plan_bytes = instance.metadata.export_plan_file("Profile1", "Plan1")
            response = instance.metadata.force_import_routing_plan(
                profile_label="Profile1",
                plan_data=plan_bytes,
                response_type=FULL_RESPONSE
            )

        Note:
            This will overwrite existing plans without warning. Use import_routing_plan
            first if you want to check for conflicts.
        """
        encoded_label = urllib.parse.quote_plus(profile_label)
        url = urljoin(
            self.baseUrl,
            f"/rest/ofscMetadata/v1/routingProfiles/{encoded_label}/plans/custom-actions/forceImport",
        )
        headers = self.headers.copy()
        headers["Content-Type"] = "application/octet-stream"
        response = requests.put(url, headers=headers, data=plan_data)
        return response

    @wrap_return(response_type=OBJ_RESPONSE, expected=[200, 202, 204])
    def start_routing_plan(
        self,
        profile_label: str,
        plan_label: str,
        resource_external_id: str,
        date: str,
    ):
        """Start a routing plan for a specific resource on a given date

        Triggers the execution of a routing plan for a specified resource and date.
        This initiates the routing optimization process.

        Args:
            profile_label: Label of the routing profile
            plan_label: Label of the routing plan to start
            resource_external_id: External ID of the resource to route
            date: Target date in YYYY-MM-DD format

        Returns:
            Response object with status 200, 202, or 204 on success

        Example:
            response = instance.metadata.start_routing_plan(
                profile_label="MaintenanceRoutingProfile",
                plan_label="Optimization",
                resource_external_id="TECH_001",
                date="2025-10-25",
                response_type=FULL_RESPONSE
            )

        Note:
            The resource must exist and be valid for the specified date.
            The date should be in YYYY-MM-DD format.
        """
        encoded_profile = urllib.parse.quote_plus(profile_label)
        encoded_plan = urllib.parse.quote_plus(plan_label)
        encoded_resource = urllib.parse.quote_plus(resource_external_id)

        url = urljoin(
            self.baseUrl,
            f"/rest/ofscMetadata/v1/routingProfiles/{encoded_profile}/plans/{encoded_plan}/"
            f"{encoded_resource}/{date}/custom-actions/start",
        )
        response = requests.post(url, headers=self.headers)
        return response

    # endregion Routing Profiles
