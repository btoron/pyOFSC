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
    Workskill,
    WorkSkillGroup,
    WorkSkillGroupListResponse,
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
    @wrap_return(response_type=OBJ_RESPONSE, expected=[200])
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
