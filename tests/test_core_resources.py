import json
import logging

from ofsc.common import FULL_RESPONSE


def test_create_resource(instance, faker, request_logging):
    new_data = {
        "parentResourceId": "SUNRISE",
        "resourceType": "BK",
        "name": faker.name(),
        "language": "en",
        "timeZone": "Arizona",
        "externalId": faker.pystr(),
    }
    raw_response = instance.core.create_resource(
        resourceId=new_data["externalId"],
        data=json.dumps(new_data),
        response_type=FULL_RESPONSE,
    )
    response = raw_response.json()
    assert raw_response.status_code < 299
    assert "resourceId" in response.keys()
    assert response["name"] == new_data["name"]


def test_create_resource_dict(instance, faker, request_logging):
    new_data = {
        "parentResourceId": "SUNRISE",
        "resourceType": "BK",
        "name": faker.name(),
        "language": "en",
        "timeZone": "Arizona",
        "externalId": faker.pystr(),
    }
    raw_response = instance.core.create_resource(
        resourceId=new_data["externalId"],
        data=new_data,
        response_type=FULL_RESPONSE,
    )
    response = raw_response.json()
    assert raw_response.status_code >= 299


def test_create_resource_from_obj_dict(instance, faker, request_logging):
    new_data = {
        "parentResourceId": "SUNRISE",
        "resourceType": "BK",
        "name": faker.name(),
        "language": "en",
        "timeZone": "Arizona",
        "externalId": faker.pystr(),
    }
    raw_response = instance.core.create_resource_from_obj(
        resourceId=new_data["externalId"],
        data=new_data,
        response_type=FULL_RESPONSE,
    )
    response = raw_response.json()
    assert raw_response.status_code == 200
