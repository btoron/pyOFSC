import json
import logging

import pytest

from ofsc.common import FULL_RESPONSE


@pytest.fixture
def new_data(faker):
    return {
        "parentResourceId": "SUNRISE",
        "resourceType": "BK",
        "name": faker.name(),
        "language": "en",
        "timeZone": "Arizona",
        "externalId": faker.pystr(),
    }


def test_create_resource(instance, new_data, request_logging):
    raw_response = instance.core.create_resource(
        resourceId=new_data["externalId"],
        data=json.dumps(new_data),
        response_type=FULL_RESPONSE,
    )
    response = raw_response.json()
    assert raw_response.status_code < 299
    assert "resourceId" in response.keys()
    assert response["name"] == new_data["name"]


def test_create_resource_dict(instance, new_data, request_logging):
    raw_response = instance.core.create_resource(
        resourceId=new_data["externalId"],
        data=new_data,
        response_type=FULL_RESPONSE,
    )
    response = raw_response.json()
    assert raw_response.status_code >= 299


def test_create_resource_from_obj_dict(instance, new_data, request_logging):
    raw_response = instance.core.create_resource_from_obj(
        resourceId=new_data["externalId"],
        data=new_data,
        response_type=FULL_RESPONSE,
    )
    response = raw_response.json()
    assert raw_response.status_code == 200


def test_get_resource_no_expand(instance, demo_data):
    raw_response = instance.core.get_resource(55001, response_type=FULL_RESPONSE)
    assert raw_response.status_code == 200
    logging.debug(raw_response.json())
    response = raw_response.json()
    assert response["resourceInternalId"] == 5000001


def test_get_resource_expand(instance, demo_data):
    raw_response = instance.core.get_resource(
        55001, workSkills=True, workZones=True, response_type=FULL_RESPONSE
    )
    assert raw_response.status_code == 200
    response = raw_response.json()
    assert response["resourceInternalId"] == 5000001


def test_get_position_history(instance, demo_data, current_date):
    raw_response = instance.core.get_position_history(
        33001, date=current_date, response_type=FULL_RESPONSE
    )
    assert raw_response.status_code == 200
    response = raw_response.json()
    assert response["totalResults"] is not None
    assert response["totalResults"] > 200


def test_get_resource_route_nofields(instance, pp, demo_data, current_date):
    raw_response = instance.core.get_resource_route(
        33001, date=current_date, response_type=FULL_RESPONSE
    )
    logging.debug(pp.pformat(raw_response.json()))
    assert raw_response.status_code == 200
    logging.debug(pp.pformat(raw_response.json()))
    response = raw_response.json()
    assert response["totalResults"] == 13


def test_get_resource_route_twofields(instance, current_date, pp):
    raw_response = instance.core.get_resource_route(
        33001,
        date=current_date,
        activityFields="activityId,activityType",
        response_type=FULL_RESPONSE,
    )
    logging.debug(pp.pformat(raw_response.json()))
    assert raw_response.status_code == 200
    response = raw_response.json()
    assert response["totalResults"] == 13


def test_get_resource_descendants_noexpand(instance):
    raw_response = instance.core.get_resource_descendants(
        "FLUSA", response_type=FULL_RESPONSE
    )
    assert raw_response.status_code == 200
    response = raw_response.json()
    assert response["totalResults"] == 37


def test_get_resource_descendants_expand(instance):
    raw_response = instance.core.get_resource_descendants(
        "FLUSA",
        workSchedules=True,
        workZones=True,
        workSkills=True,
        response_type=FULL_RESPONSE,
    )
    assert raw_response.status_code == 200
    response = raw_response.json()
    assert response["totalResults"] == 37


def test_get_resource_descendants_noexpand_fields(instance, pp):
    raw_response = instance.core.get_resource_descendants(
        "FLUSA", resourceFields="resourceId,phone", response_type=FULL_RESPONSE
    )
    assert raw_response.status_code == 200
    response = raw_response.json()
    logging.debug(pp.pformat(response))
    assert response["totalResults"] == 37
