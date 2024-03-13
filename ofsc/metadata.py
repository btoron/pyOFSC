import base64
import json
import logging
import urllib
from pathlib import Path
from typing import List
from urllib.parse import urljoin

import requests

from .common import FULL_RESPONSE, JSON_RESPONSE, TEXT_RESPONSE, wrap_return
from .models import (
    ActivityTypeGroup,
    ActivityTypeGroupList,
    ActivityTypeGroupListResponse,
    ActivityTypeListResponse,
    OFSApi,
    OFSConfig,
    Property,
    Workskill,
    WorkskillCondition,
    WorskillConditionList,
)


class OFSMetadata(OFSApi):

    capacityAreasFields = "label,name,type,status,parent.name,parent.label"
    additionalCapacityFields = [
        "parentLabel",
        "configuration.isTimeSlotBase",
        "configuration.byCapacityCategory",
        "configuration.byDay",
        "configuration.byTimeSlot",
        "configuration.isAllowCloseOnWorkzoneLevel",
        "configuration.definitionLevel.day",
        "configuration.definitionLevel.timeSlot",
        "configuration.definitionLevel.capacityCategory",
    ]
    capacityHeaders = capacityAreasFields.split(",") + additionalCapacityFields

    @wrap_return(response_type=JSON_RESPONSE, expected=[200])
    def get_capacity_areas(
        self,
        expand="parent",
        fields=capacityAreasFields,
        status="active",
        queryType="area",
    ):
        url = urljoin(self.baseUrl, "/rest/ofscMetadata/v1/capacityAreas")
        params = {}
        params["expand"] = expand
        params["fields"] = fields
        params["status"] = status
        params["type"] = queryType
        response = requests.get(url, params=params, headers=self.headers)
        return response

    @wrap_return(response_type=JSON_RESPONSE, expected=[200])
    def get_capacity_area(self, label: str):
        encoded_label = urllib.parse.quote_plus(label)
        url = urljoin(
            self.baseUrl, "/rest/ofscMetadata/v1/capacityAreas/{}".format(encoded_label)
        )
        response = requests.get(url, headers=self.headers)
        return response

    ## 202202 Properties and file properties

    @wrap_return(response_type=JSON_RESPONSE, expected=[200])
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
    @wrap_return(response_type=JSON_RESPONSE, expected=[200])
    def get_property(self, label: str):
        url = urljoin(self.baseUrl, f"/rest/ofscMetadata/v1/properties/{label}")
        response = requests.get(url, headers=self.headers)
        return response

    # 202209 Create Property
    @wrap_return(response_type=JSON_RESPONSE, expected=[200])
    def create_or_replace_property(self, property: Property):
        url = urljoin(
            self.baseUrl, f"/rest/ofscMetadata/v1/properties/{property.label}"
        )
        response = requests.put(url, headers=self.headers, data=property.json())
        return response

    # 202208 Skill management

    # 202208 Workzones
    @wrap_return(response_type=JSON_RESPONSE, expected=[200])
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
    @wrap_return(response_type=JSON_RESPONSE, expected=[200])
    def get_resource_types(self):
        url = urljoin(self.baseUrl, "/rest/ofscMetadata/v1/resourceTypes")
        response = requests.get(url, headers=self.headers)
        return response

    # 202212 Import plugin
    @wrap_return(response_type=JSON_RESPONSE, expected=[204])
    def import_plugin_file(self, plugin: Path):
        url = urljoin(
            self.baseUrl, f"/rest/ofscMetadata/v1/plugins/custom-actions/import"
        )
        files = [("pluginFile", (plugin.name, plugin.read_text(), "text/xml"))]
        response = requests.post(url, headers=self.headers, files=files)
        return response

    # 202212 Import plugin
    @wrap_return(response_type=JSON_RESPONSE, expected=[204])
    def import_plugin(self, plugin: str):
        url = urljoin(
            self.baseUrl, f"/rest/ofscMetadata/v1/plugins/custom-actions/import"
        )
        files = [("pluginFile", ("noname.xml", plugin, "text/xml"))]
        response = requests.post(url, headers=self.headers, files=files)
        return response

    @wrap_return(response_type=JSON_RESPONSE, expected=[200])
    def get_workskills(self, offset=0, limit=100, response_type=FULL_RESPONSE):
        url = urljoin(self.baseUrl, "/rest/ofscMetadata/v1/workSkills")
        params = {"offset": offset, "limit": limit}
        response = requests.get(
            url,
            headers=self.headers,
            params=params,
        )
        return response

    @wrap_return(response_type=JSON_RESPONSE, expected=[200])
    def get_workskill(self, label: str, response_type=FULL_RESPONSE):
        url = urljoin(self.baseUrl, f"/rest/ofscMetadata/v1/workSkills/{label}")
        response = requests.get(
            url,
            headers=self.headers,
        )
        return response

    @wrap_return(response_type=JSON_RESPONSE, expected=[200])
    def create_or_update_workskill(self, skill: Workskill, response_type=FULL_RESPONSE):
        url = urljoin(self.baseUrl, f"/rest/ofscMetadata/v1/workSkills/{skill.label}")
        response = requests.put(url, headers=self.headers, data=skill.model_dump_json())
        return response

    @wrap_return(response_type=JSON_RESPONSE, expected=[204])
    def delete_workskill(self, label: str, response_type=FULL_RESPONSE):
        url = urljoin(self.baseUrl, f"/rest/ofscMetadata/v1/workSkills/{label}")
        response = requests.delete(url, headers=self.headers)
        return response

    # Workskill conditions
    @wrap_return(response_type=JSON_RESPONSE, expected=[200])
    def get_workskill_conditions(self, response_type=FULL_RESPONSE):
        url = urljoin(self.baseUrl, f"/rest/ofscMetadata/v1/workSkillConditions")
        response = requests.get(
            url,
            headers=self.headers,
        )
        return response

    @wrap_return(response_type=JSON_RESPONSE, expected=[200])
    def replace_workskill_conditions(
        self, data: WorskillConditionList, response_type=FULL_RESPONSE
    ):
        url = urljoin(self.baseUrl, f"/rest/ofscMetadata/v1/workSkillConditions")
        content = '{"items":' + data.model_dump_json(exclude_none=True) + "}"
        headers = self.headers
        headers["Content-Type"] = "application/json"
        response = requests.put(url, headers=headers, data=content)
        return response

    #####
    # Migration to OFS 2.0 model format

    # 202402 Metadata - Activity Type Groups
    @wrap_return(
        response_type=JSON_RESPONSE, expected=[200], model=ActivityTypeGroupListResponse
    )
    def get_activity_type_groups(self, offset=0, limit=100):
        url = urljoin(self.baseUrl, "/rest/ofscMetadata/v1/activityTypeGroups")
        params = {"offset": offset, "limit": limit}
        response = requests.get(url, headers=self.headers, params=params)
        return response

    @wrap_return(response_type=JSON_RESPONSE, expected=[200], model=ActivityTypeGroup)
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
        response_type=JSON_RESPONSE, expected=[200], model=ActivityTypeListResponse
    )
    def get_activity_types(self, offset=0, limit=100):
        url = urljoin(self.baseUrl, "/rest/ofscMetadata/v1/activityTypes")
        params = {"offset": offset, "limit": limit}
        response = requests.get(url, headers=self.headers, params=params)
        return response

    @wrap_return(response_type=JSON_RESPONSE, expected=[200])
    def get_activity_type(self, label):
        encoded_label = urllib.parse.quote_plus(label)
        url = urljoin(
            self.baseUrl, "/rest/ofscMetadata/v1/activityTypes/{}".format(encoded_label)
        )
        response = requests.get(url, headers=self.headers)
        return response
