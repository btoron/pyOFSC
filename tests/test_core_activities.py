import logging
from datetime import date, timedelta

import pytest

from ofsc.common import FULL_RESPONSE


def test_search_activities_001(instance):
    logging.info("...101: Search Activities (activity exists)")
    params = {
        "searchInField": "customerPhone",
        "searchForValue": "555760757294",
        "dateFrom": "2021-01-01",
        "dateTo": "2099-01-01",
    }
    response = instance.core.search_activities(params, response_type=FULL_RESPONSE)
    logging.info(response.json())
    assert response.status_code == 200
    assert response.json()["totalResults"] == 2  # 202206 Modified in demo 22B


# test A.06 Get Activities
def test_get_activities_no_offset(instance, current_date, demo_data, request_logging):
    logging.info("...102: Get activities (no offset)")
    start = date.fromisoformat(current_date) - timedelta(days=5)
    end = start + timedelta(days=20)
    logging.info(f"{start} {end}")
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

    # TODO: Due to the nature of the get_activities this assert may fail

    assert data["items"][10] == {
        "activityId": expected_id,
        "resourceId": expected_postalcode,
    }


def test_get_activities_offset(instance, current_date, demo_data, request_logging):
    logging.info("...103: Get activities (offset)")
    start = date.fromisoformat(current_date) - timedelta(days=5)
    end = start + timedelta(days=20)
    logging.info(f"{start} {end}")
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

    # TODO: Due to the nature of the get_activities this assert may fail

    assert data["items"][0] == {
        "activityId": expected_id,
        "resourceId": expected_postalcode,
    }
