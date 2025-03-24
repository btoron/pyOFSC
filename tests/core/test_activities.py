import logging
import os
from datetime import date, timedelta

from ofsc.common import FULL_RESPONSE
from ofsc.models import BulkUpdateRequest, BulkUpdateResponse


def test_get_activity(instance):
    raw_response = instance.core.get_activity(3951935, response_type=FULL_RESPONSE)
    response = raw_response.json()
    logging.debug(response)
    assert response["customerNumber"] == "019895700"


def test_get_all_activities(instance):
    response = instance.core.get_all_activities()
    assert len(response) > 0


def test_get_all_activities_with_date_range(instance):
    response = instance.core.get_all_activities(
        date_from=None,
        date_to=None,
        include_non_scheduled=True,
    )
    assert len(response) > 0


def test_get_activity_error(instance):
    raw_response = instance.core.get_activity(99999, response_type=FULL_RESPONSE)
    assert raw_response.status_code == 404


def test_search_activities_001(instance):
    params = {
        "searchInField": "customerPhone",
        "searchForValue": "555760757294",
        "dateFrom": "2021-01-01",
        "dateTo": "2099-01-01",
    }
    response = instance.core.search_activities(params, response_type=FULL_RESPONSE)
    logging.debug(response.json())
    assert response.status_code == 200
    assert response.json()["totalResults"] == 2  # 202206 Modified in demo 22B


def test_get_activities_no_offset(instance, current_date, demo_data, request_logging):
    start = date.fromisoformat(current_date) - timedelta(days=5)
    end = start + timedelta(days=20)
    logging.debug(f"{start} {end}")
    params = {
        "dateFrom": start.strftime("%Y-%m-%d"),
        "dateTo": end.strftime("%Y-%m-%d"),
        "resources": demo_data.get("get_all_activities").get("bucket_id"),
        "includeChildren": "all",
        "fields": "activityId,resourceId",
        "offset": 0,
        "limit": 5000,
    }
    response = instance.core.get_activities(params, response_type=FULL_RESPONSE)
    assert response.status_code == 200
    data = response.json()
    assert "hasMore" not in data.keys()
    assert "items" in data.keys()
    expected_items = demo_data.get("get_all_activities").get("expected_items")
    expected_id = demo_data.get("get_all_activities").get("expected_id")
    expected_postalcode = demo_data.get("get_all_activities").get("expected_postalcode")
    assert len(data["items"]) == expected_items

    assert data["items"][10] == {
        "activityId": expected_id,
        "resourceId": expected_postalcode,
    }


def test_get_activities_offset(instance, current_date, demo_data, request_logging):
    start = date.fromisoformat(current_date) - timedelta(days=5)
    end = start + timedelta(days=20)
    logging.debug(f"{start} {end}")
    params = {
        "dateFrom": start.strftime("%Y-%m-%d"),
        "dateTo": end.strftime("%Y-%m-%d"),
        "resources": demo_data.get("get_all_activities").get("bucket_id"),
        "includeChildren": "all",
        "fields": "activityId,resourceId",
        "offset": 10,
        "limit": 100,
    }
    response = instance.core.get_activities(params, response_type=FULL_RESPONSE)
    assert response.status_code == 200
    data = response.json()
    assert "hasMore" in data.keys()
    assert "items" in data.keys()
    expected_id = demo_data.get("get_all_activities").get("expected_id")
    expected_postalcode = demo_data.get("get_all_activities").get("expected_postalcode")
    assert len(data["items"]) == params["limit"]

    assert data["items"][0] == {
        "activityId": expected_id,
        "resourceId": expected_postalcode,
    }


def test_model_bulk_update_simple(instance, request_logging):
    data = {
        "updateParameters": {
            "identifyActivityBy": "apptNumber",
            "ifInFinalStatusThen": "doNothing",
        },
        "activities": [
            {
                "apptNumber": "XS3453456",
                "resourceId": "CAUSA",
                "date": "2023-08-09",
                "activityType": "09",
                "timeZone": "America/New_York",
                "language": "en-US",
                "inventories": {
                    "items": [
                        {
                            "inventoryType": "RG6BLK",
                            "inventory_model": "Z222",
                            "quantity": 10,
                        },
                        {
                            "inventoryType": "RG6BLK",
                            "inventory_model": "X333",
                            "quantity": 5,
                        },
                    ]
                },
                "requiredInventories": {
                    "items": [
                        {"inventoryType": "NS", "model": "A22", "quantity": 10},
                        {"inventoryType": "NS", "model": "B22", "quantity": 10},
                    ]
                },
                "linkedActivities": {
                    "items": [
                        {
                            "fromActivity": {
                                "apptNumber": "A0001",
                                "linkType": "start-after",
                            }
                        },
                        {
                            "toActivity": {
                                "apptNumber": "B0002",
                                "linkType": "start-after",
                            }
                        },
                    ]
                },
                "resourcePreferences": {
                    "items": [
                        {
                            "resourceId": "testActivityCustomAcQYNWZCUYYP",
                            "preferenceType": "preferred",
                        },
                        {
                            "resourceId": "testActivityCustomAcCKIVJZFSSB",
                            "preferenceType": "preferred",
                        },
                    ]
                },
            }
        ],
    }
    input = BulkUpdateRequest.model_validate(data)
    raw_response = instance.core.bulk_update(input, response_type=FULL_RESPONSE)
    assert raw_response.status_code == 200
    response = raw_response.json()
    output = BulkUpdateResponse.model_validate(response)


def test_get_file_property_01(instance, pp, demo_data):
    activity_id = demo_data.get("get_file_property").get("activity_id")
    # Get all properties from the activity
    raw_response = instance.core.get_activity(activity_id, response_type=FULL_RESPONSE)
    assert raw_response.status_code == 200, raw_response.json()
    response = raw_response.json()
    # verify that the file is there
    assert response.get("csign") is not None
    assert response.get("csign").get("links") is not None
    logging.info(pp.pformat(response.get("csign").get("links")[0].get("href")))
    raw_response = instance.core.get_file_property(
        activityId=activity_id,
        label="csign",
        mediaType="*/*",
        response_type=FULL_RESPONSE,
    )
    assert raw_response.status_code == 200, raw_response.json()
    logging.info(pp.pformat(raw_response.json()))
    response = raw_response.json()
    logging.info(pp.pformat(response))
    assert response["mediaType"] is not None
    assert response["mediaType"] == "image/png"
    assert response["name"] == "signature.png"


def test_get_file_property_02(instance, pp, demo_data):
    logging.info("...C.P.02 Get File Property content")
    activity_id = demo_data.get("get_file_property").get("activity_id")
    metadata_response = instance.core.get_file_property(
        activityId=activity_id,
        label="csign",
        mediaType="*/*",
        response_type=FULL_RESPONSE,
    )
    logging.debug(pp.pformat(metadata_response.json()))
    response = metadata_response.json()
    raw_response = instance.core.get_file_property(
        activityId=activity_id,
        label="csign",
        mediaType="image/png",
        response_type=FULL_RESPONSE,
    )
    with open(os.path.join(os.getcwd(), response["name"]), "wb") as fd:
        fd.write(raw_response.content)
    assert response["name"] == "signature.png"
