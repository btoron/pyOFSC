import json
import logging
from datetime import date
from urllib.parse import urljoin

import requests

from .common import FULL_RESPONSE, OBJ_RESPONSE, wrap_return
from .models import (
    BulkUpdateRequest,
    CalendarView,
    OFSApi,
    ResourceUsersListResponse,
    ResourceWorkScheduleItem,
    ResourceWorkScheduleResponse,
)


class OFSCore(OFSApi):
    # OFSC Function Library
    @wrap_return(response_type=OBJ_RESPONSE, expected=[200])
    def get_activities(self, params):
        url = urljoin(self.baseUrl, "/rest/ofscCore/v1/activities")
        response = requests.get(url, headers=self.headers, params=params)
        return response

    @wrap_return(response_type=OBJ_RESPONSE, expected=[200])
    def get_activity(self, activity_id):
        url = urljoin(
            self.baseUrl, "/rest/ofscCore/v1/activities/{}".format(activity_id)
        )
        response = requests.get(url, headers=self.headers)
        return response

    @wrap_return(response_type=OBJ_RESPONSE, expected=[200])
    def update_activity(self, activity_id, data):
        url = urljoin(
            self.baseUrl, "/rest/ofscCore/v1/activities/{}".format(activity_id)
        )
        response = requests.patch(url, headers=self.headers, data=data)
        return response

    # 202107 Added ssearch
    @wrap_return(response_type=OBJ_RESPONSE, expected=[200])
    def search_activities(self, params):
        url = urljoin(
            self.baseUrl, "/rest/ofscCore/v1/activities/custom-actions/search"
        )
        response = requests.get(url, headers=self.headers, params=params)
        return response

    @wrap_return(response_type=OBJ_RESPONSE, expected=[200])
    def move_activity(self, activity_id, data):
        url = urljoin(
            self.baseUrl,
            f"/rest/ofscCore/v1/activities/{activity_id}/custom-actions/move",
        )
        response = requests.post(url, headers=self.headers, data=data)
        return response

    @wrap_return(response_type=OBJ_RESPONSE, expected=[200])
    def get_events(self, params):
        url = urljoin(self.baseUrl, "/rest/ofscCore/v1/events")
        response = requests.get(
            url,
            headers=self.headers,
            params=params,
        )
        return response

    # region Resource Management
    @wrap_return(response_type=OBJ_RESPONSE, expected=[200])
    def get_resource(
        self,
        resource_id,
        inventories=False,
        workSkills=False,
        workZones=False,
        workSchedules=False,
    ):
        url = urljoin(
            self.baseUrl, "/rest/ofscCore/v1/resources/{}".format(str(resource_id))
        )
        data = {}
        expand = ""
        if inventories:
            expand = "inventories"
        if workSkills:
            if len(expand) > 0:
                expand = "{},workSkills".format(expand)
            else:
                expand = "workSkills"
        if workZones:
            if len(expand) > 0:
                expand = "{},workZones".format(expand)
            else:
                expand = "workZones"
        if workSchedules:
            if len(expand) > 0:
                expand = "{},workSchedules".format(expand)
            else:
                expand = "workSchedules"

        if len(expand) > 0:
            data["expand"] = expand

        response = requests.get(url, params=data, headers=self.headers)
        return response

    # 202209 Resource Types
    @wrap_return(response_type=OBJ_RESPONSE, expected=[200])
    def create_resource(self, resourceId, data):
        url = urljoin(self.baseUrl, f"/rest/ofscCore/v1/resources/{resourceId}")
        logging.debug(f"OFSC.Create_Resource: {data} {type(data)}")
        response = requests.put(url, headers=self.headers, data=data)
        return response

    @wrap_return(response_type=OBJ_RESPONSE, expected=[200])
    def create_resource_from_obj(self, resourceId, data):
        url = urljoin(self.baseUrl, f"/rest/ofscCore/v1/resources/{resourceId}")
        logging.debug(f"OFSC.Create_Resource: {data} {type(data)}")
        response = requests.put(url, headers=self.headers, data=json.dumps(data))
        return response

    @wrap_return(response_type=OBJ_RESPONSE, expected=[200])
    def update_resource(
        self, resourceId, data: dict, identify_by_internal_id: bool = False
    ):
        url = urljoin(self.baseUrl, f"/rest/ofscCore/v1/resources/{resourceId}")
        if identify_by_internal_id:
            # add a query parameter to identify the resource by internal id
            url += "?identifyResourceBy=resourceInternalId"
        logging.debug(f"OFSC.Update_Resource: {data} {type(data)}")
        response = requests.patch(url, headers=self.headers, data=json.dumps(data))
        return response

    @wrap_return(response_type=OBJ_RESPONSE, expected=[200])
    def get_position_history(self, resource_id, date):
        url = urljoin(
            self.baseUrl,
            "/rest/ofscCore/v1/resources/{}/positionHistory".format(str(resource_id)),
        )
        params = {}
        params["date"] = date
        response = requests.get(url, params=params, headers=self.headers)
        return response

    @wrap_return(response_type=OBJ_RESPONSE, expected=[200])
    def get_resource_route(
        self, resource_id, date, activityFields=None, offset=0, limit=100
    ):
        url = urljoin(
            self.baseUrl,
            "/rest/ofscCore/v1/resources/{}/routes/{}".format(str(resource_id), date),
        )
        params = {}
        if activityFields is not None:
            params["activityFields"] = activityFields
        response = requests.get(url, params=params, headers=self.headers)
        return response

    @wrap_return(response_type=OBJ_RESPONSE, expected=[200])
    def get_resource_descendants(
        self,
        resource_id,
        resourceFields=None,
        offset=0,
        limit=100,
        inventories=False,
        workSkills=False,
        workZones=False,
        workSchedules=False,
    ):
        url = urljoin(
            self.baseUrl,
            "/rest/ofscCore/v1/resources/{}/descendants".format(str(resource_id)),
        )
        # Calculate expand
        params = {}
        expand = ""
        if inventories:
            expand = "inventories"
        if workSkills:
            if len(expand) > 0:
                expand = "{},workSkills".format(expand)
            else:
                expand = "workSkills"
        if workZones:
            if len(expand) > 0:
                expand = "{},workZones".format(expand)
            else:
                expand = "workZones"
        if workSchedules:
            if len(expand) > 0:
                expand = "{},workSchedules".format(expand)
            else:
                expand = "workSchedules"

        if len(expand) > 0:
            params["expand"] = expand

        if resourceFields is not None:
            params["fields"] = resourceFields
        params["limit"] = limit
        params["offset"] = offset
        logging.debug(json.dumps(params, indent=2))

        response = requests.get(url, params=params, headers=self.headers)
        return response

    @wrap_return(
        response_type=OBJ_RESPONSE, expected=[200], model=ResourceUsersListResponse
    )
    def get_resource_users(self, resource_id):
        url = urljoin(
            self.baseUrl,
            f"/rest/ofscCore/v1/resources/{str(resource_id)}/users",
        )
        response = requests.get(url, headers=self.headers)
        return response

    @wrap_return(response_type=OBJ_RESPONSE, expected=[200])
    def set_resource_users(self, *, resource_id, users: tuple[str]):
        data = {
            "items": [{"login": user} for user in users],
        }
        url = urljoin(
            self.baseUrl,
            f"/rest/ofscCore/v1/resources/{str(resource_id)}/users",
        )
        response = requests.put(url, headers=self.headers, data=json.dumps(data))
        return response

    @wrap_return(response_type=OBJ_RESPONSE, expected=[204])
    def delete_resource_users(self, resource_id):
        url = urljoin(
            self.baseUrl,
            f"/rest/ofscCore/v1/resources/{str(resource_id)}/users",
        )
        response = requests.delete(url, headers=self.headers)
        return response

    @wrap_return(
        response_type=OBJ_RESPONSE, expected=[200], model=ResourceWorkScheduleResponse
    )
    def get_resource_workschedules(self, resource_id, actualDate: date):
        url = urljoin(
            self.baseUrl,
            f"/rest/ofscCore/v1/resources/{str(resource_id)}/workSchedules?actualDate={actualDate.isoformat()}",
        )
        response = requests.get(url, headers=self.headers)
        return response

    @wrap_return(
        response_type=OBJ_RESPONSE, expected=[200], model=ResourceWorkScheduleResponse
    )
    def set_resource_workschedules(self, resource_id, data: ResourceWorkScheduleItem):
        url = urljoin(
            self.baseUrl,
            f"/rest/ofscCore/v1/resources/{str(resource_id)}/workSchedules",
        )
        response = requests.post(
            url,
            headers=self.headers,
            data=data.model_dump_json(exclude_none=True),
        )
        return response

    @wrap_return(response_type=OBJ_RESPONSE, expected=[200], model=CalendarView)
    def get_resource_calendar(self, resource_id: str, dateFrom: date, dateTo: date):
        url = urljoin(
            self.baseUrl,
            f"/rest/ofscCore/v1/resources/{str(resource_id)}/workSchedules/calendarView",
        )
        params = {}
        params["dateFrom"] = dateFrom.strftime("%Y-%m-%d")
        params["dateTo"] = dateTo.strftime("%Y-%m-%d")
        response = requests.get(url, headers=self.headers, params=params)
        return response

    @wrap_return(response_type=OBJ_RESPONSE, expected=[200])
    def get_resource_inventories(self, resource_id):
        url = urljoin(
            self.baseUrl,
            f"/rest/ofscCore/v1/resources/{str(resource_id)}/inventories",
        )
        response = requests.get(url, headers=self.headers)
        return response

    @wrap_return(response_type=OBJ_RESPONSE, expected=[200])
    def get_resource_assigned_locations(self, resource_id):
        url = urljoin(
            self.baseUrl,
            f"/rest/ofscCore/v1/resources/{str(resource_id)}/assignedLocations",
        )
        response = requests.get(url, headers=self.headers)
        return response

    @wrap_return(response_type=OBJ_RESPONSE, expected=[200])
    def get_resource_workzones(self, resource_id):
        url = urljoin(
            self.baseUrl,
            f"/rest/ofscCore/v1/resources/{str(resource_id)}/workZones",
        )
        response = requests.get(url, headers=self.headers)
        return response

    @wrap_return(response_type=OBJ_RESPONSE, expected=[200])
    def get_resource_workskills(self, resource_id):
        url = urljoin(
            self.baseUrl,
            f"/rest/ofscCore/v1/resources/{str(resource_id)}/workSkills",
        )
        response = requests.get(url, headers=self.headers)
        return response

    @wrap_return(response_type=OBJ_RESPONSE, expected=[200])
    def bulk_update_resource_workzones(self, *, data):
        url = urljoin(
            self.baseUrl,
            "/rest/ofscCore/v1/resources/custom-actions/bulkUpdateWorkZones",
        )
        response = requests.post(url, headers=self.headers, data=data)
        return response

    @wrap_return(response_type=OBJ_RESPONSE, expected=[200])
    def bulk_update_resource_workskills(self, *, data):
        url = urljoin(
            self.baseUrl,
            "/rest/ofscCore/v1/resources/custom-actions/bulkUpdateWorkSkills",
        )
        response = requests.post(url, headers=self.headers, data=data)
        return response

    @wrap_return(response_type=OBJ_RESPONSE, expected=[200])
    def bulk_update_resource_workschedules(self, *, data):
        url = urljoin(
            self.baseUrl,
            "/rest/ofscCore/v1/resources/custom-actions/bulkUpdateWorkSchedules",
        )
        response = requests.post(url, headers=self.headers, data=data)
        return response

    # endregion
    # region User Management

    @wrap_return(response_type=OBJ_RESPONSE, expected=[200])
    def get_users(self, offset=0, limit=100):
        url = urljoin(self.baseUrl, "/rest/ofscCore/v1/users")
        params = {}
        params["offset"] = offset
        params["limit"] = limit
        response = requests.get(url, params, headers=self.headers)
        return response

    @wrap_return(response_type=OBJ_RESPONSE, expected=[200])
    def get_user(self, login):
        url = urljoin(self.baseUrl, "/rest/ofscCore/v1/users/{}".format(login))
        response = requests.get(url, headers=self.headers)
        return response

    @wrap_return(response_type=OBJ_RESPONSE, expected=[200])
    def update_user(self, login, data):
        url = urljoin(self.baseUrl, "/rest/ofscCore/v1/users/{}".format(login))
        response = requests.patch(url, headers=self.headers, data=data)
        return response

    ##202106
    @wrap_return(response_type=OBJ_RESPONSE, expected=[200])
    def create_user(self, login, data):
        url = urljoin(self.baseUrl, f"/rest/ofscCore/v1/users/{login}")
        response = requests.put(url, headers=self.headers, data=data)
        return response

    ##202106

    @wrap_return(response_type=OBJ_RESPONSE, expected=[200])
    def delete_user(self, login):
        url = urljoin(self.baseUrl, f"/rest/ofscCore/v1/users/{login}")
        response = requests.delete(url, headers=self.headers)
        return response

    # endregion
    # region Daily Extract
    ##202105 Daily Extract - NOT TESTED
    @wrap_return(response_type=OBJ_RESPONSE, expected=[200])
    def get_daily_extract_dates(self):
        url = urljoin(self.baseUrl, "/rest/ofscCore/v1/folders/dailyExtract/folders/")
        response = requests.get(url, headers=self.headers)
        return response

    ##202105 Daily Extract - NOT TESTED
    @wrap_return(response_type=OBJ_RESPONSE, expected=[200])
    def get_daily_extract_files(self, date):
        url = urljoin(
            self.baseUrl,
            "/rest/ofscCore/v1/folders/dailyExtract/folders/{}/files".format(date),
        )
        response = requests.get(url, headers=self.headers)
        return response

    ##202105 Daily Extract - NOT TESTED
    @wrap_return(response_type=OBJ_RESPONSE, expected=[200])
    def get_daily_extract_file(self, date, filename):
        url = urljoin(
            self.baseUrl,
            "/rest/ofscCore/v1/folders/dailyExtract/folders/{}/files/{}".format(
                date, filename
            ),
        )
        response = requests.get(url, headers=self.headers)
        return response

    # endregion
    ## 202202 Helper functions
    def get_all_activities(
        self, root, date_from, date_to, activity_fields, initial_offset=0, limit=5000
    ):
        items = []
        hasMore = True
        offset = initial_offset
        while hasMore:
            request_params = {
                "dateFrom": date_from,
                "dateTo": date_to,
                "resources": root,
                "includeChildren": "all",
                # "includeNonScheduled": "true",
                # "q":"status=='notdone'",
                "fields": activity_fields,
                "offset": offset,
                "limit": limit,
            }
            logging.info(request_params)
            response = self.get_activities(
                response_type=FULL_RESPONSE, params=request_params
            )
            response_body = response.json()
            if "items" in response_body.keys():
                response_count = len(response_body["items"])
                items.extend(response_body["items"])
            else:
                response_count = 0
            if "hasMore" in response_body.keys():
                hasMore = response_body["hasMore"]
                logging.info(
                    "{},{},{}".format(offset, response_count, response.elapsed)
                )
            else:
                hasMore = False
                logging.info(
                    "{},{},{}".format(offset, response_count, response.elapsed)
                )
            offset = offset + response_count
        return items

    def get_all_properties(self, initial_offset=0, limit=100):
        items = []
        hasMore = True
        offset = initial_offset
        while hasMore:
            response = self.get_properties(
                offset=offset, limit=limit, response_type=FULL_RESPONSE
            )
            response_body = response.json()
            if "items" in response_body.keys():
                response_count = len(response_body["items"])
                items.extend(response_body["items"])
            else:
                response_count = 0
            if "hasMore" in response_body.keys():
                hasMore = response_body["hasMore"]
                logging.info(
                    "{},{},{}".format(offset, response_count, response.elapsed)
                )
            else:
                hasMore = False
                logging.info(
                    "{},{},{}".format(offset, response_count, response.elapsed)
                )
            offset = offset + response_count
        return items

    ###
    # 1. Subscriptions Management. Using wrapper
    ###
    @wrap_return(response_type=OBJ_RESPONSE, expected=[200])
    def get_subscriptions(self):
        url = urljoin(self.baseUrl, "/rest/ofscCore/v1/events/subscriptions")
        response = requests.get(url, headers=self.headers)
        return response

    @wrap_return(response_type=OBJ_RESPONSE, expected=[200])
    def create_subscription(self, data):
        url = urljoin(self.baseUrl, "/rest/ofscCore/v1/events/subscriptions")
        response = requests.post(url, headers=self.headers, data=data)
        return response

    @wrap_return(response_type=OBJ_RESPONSE, expected=[204])
    def delete_subscription(self, subscription_id):
        url = urljoin(
            self.baseUrl, f"/rest/ofscCore/v1/events/subscriptions/{subscription_id}"
        )
        response = requests.delete(url, headers=self.headers)
        return response

    @wrap_return(response_type=OBJ_RESPONSE, expected=[200])
    def get_subscription_details(self, subscription_id):
        url = urljoin(
            self.baseUrl,
            "/rest/ofscCore/v1/events/subscriptions/{}".format(str(subscription_id)),
        )
        response = requests.get(url, headers=self.headers)
        return response

    ###
    # 2. Core / Activities
    ###

    @wrap_return(response_type=OBJ_RESPONSE, expected=[200])
    def bulk_update(self, data: BulkUpdateRequest):
        url = urljoin(
            self.baseUrl,
            "/rest/ofscCore/v1/activities/custom-actions/bulkUpdate",
        )
        response = requests.post(url, headers=self.headers, data=data.model_dump_json())
        return response

    @wrap_return(response_type=OBJ_RESPONSE, expected=[200])
    def get_file_property(
        self,
        activityId,
        label,
        mediaType="application/octet-stream",
    ):
        url = urljoin(
            self.baseUrl,
            f"/rest/ofscCore/v1/activities/{activityId}/{label}",
        )
        headers = self.headers
        headers["Accept"] = mediaType
        response = requests.get(
            url,
            headers=headers,
        )
        return response
        headers["Accept"] = mediaType
        response = requests.get(
            url,
            headers=headers,
        )
        return response
