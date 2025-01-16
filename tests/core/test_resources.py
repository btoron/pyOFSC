import json
import logging

import pytest

from ofsc.common import FULL_RESPONSE, OBJ_RESPONSE
from ofsc.models import ResourceUsersListResponse


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


def test_update_resource(instance, demo_data, request_logging):
    raw_response = instance.core.update_resource(
        "FLUSA", data={"name": "FLUSA-1"}, response_type=FULL_RESPONSE
    )
    assert raw_response.status_code == 200
    response = raw_response.json()
    assert response["name"] == "FLUSA-1"
    raw_response = instance.core.update_resource(
        "FLUSA", data={"name": "FLUSA"}, response_type=FULL_RESPONSE
    )


def test_update_resource_external_id(instance, demo_data, request_logging):
    raw_response = instance.core.update_resource(
        "8100308",
        data={"resourceId": "FLUSA-1"},
        identify_by_internal_id=True,
        response_type=FULL_RESPONSE,
    )
    assert raw_response.status_code == 200
    response = raw_response.json()
    assert response["resourceId"] == "FLUSA-1"
    # Do a get to the resource
    raw_response = instance.core.get_resource("FLUSA-1", response_type=FULL_RESPONSE)
    assert raw_response.status_code == 200
    response = raw_response.json()
    assert response["resourceId"] == "FLUSA-1"
    # reset
    raw_response = instance.core.update_resource(
        "8100308",
        data={"resourceId": "FLUSA"},
        identify_by_internal_id=True,
        response_type=FULL_RESPONSE,
    )
    assert raw_response.status_code == 200
    response = raw_response.json()
    assert response["resourceId"] == "FLUSA"
    # Do a get to the resource
    raw_response = instance.core.get_resource("FLUSA", response_type=FULL_RESPONSE)
    assert raw_response.status_code == 200
    response = raw_response.json()
    assert response["resourceId"] == "FLUSA"


def test_get_resource_users_base(instance, demo_data):
    raw_response = instance.core.get_resource_users(
        "55001", response_type=FULL_RESPONSE
    )
    assert raw_response.status_code == 200
    response = raw_response.json()
    assert response["totalResults"] == 1
    assert response["items"][0]["login"] == "walter.ambriz"


def test_get_resource_users_obj(instance, demo_data):
    response = instance.core.get_resource_users("55001", response_type=OBJ_RESPONSE)
    assert isinstance(response, ResourceUsersListResponse)
    assert response.totalResults == 1
    assert response.users[0] == "walter.ambriz"


def test_set_resource_users(instance, demo_data):
    initial_data = instance.core.get_resource_users("33001", response_type=OBJ_RESPONSE)
    assert initial_data.totalResults == 1
    assert initial_data.users[0] == "william.arndt"

    raw_response = instance.core.set_resource_users(
        resource_id="33001",
        users=["william.arndt", "terri.basile"],
        response_type=FULL_RESPONSE,
    )
    assert raw_response.status_code == 200
    response = raw_response.json()
    assert response["items"][0]["login"] == "william.arndt"
    logging.warning(initial_data.users)
    new_response = instance.core.set_resource_users(
        resource_id="33001", users=initial_data.users, response_type=FULL_RESPONSE
    )
    assert new_response.status_code == 200
    logging.warning(new_response.json())
    assert False


def test_reset_resource_users(instance, demo_data):
    instance.core.delete_resource_users(resource_id="100000490999044")
    raw_response = instance.core.set_resource_users(
        resource_id="100000490999044",
        users=["chris.conner"],
        response_type=FULL_RESPONSE,
    )
    assert raw_response.status_code == 200, raw_response.json()
    response = raw_response.json()
    assert response["items"][0]["login"] == "chris.conner"
    assert len(response["items"]) == 1
    raw_response = instance.core.get_resource_users(
        "100000490999044", response_type=FULL_RESPONSE
    )
    assert raw_response.status_code == 200
    response = raw_response.json()
    assert response["totalResults"] == 1


def test_reset2_resource_users(instance, demo_data):
    raw_response = instance.core.set_resource_users(
        resource_id="33001", users=["william.arndt"], response_type=FULL_RESPONSE
    )
    assert raw_response.status_code == 200, raw_response.json()
    response = raw_response.json()
    assert response["items"][0]["login"] == "william.arndt"
    assert len(response["items"]) == 1
    raw_response = instance.core.get_resource_users(
        "33001", response_type=FULL_RESPONSE
    )
    assert raw_response.status_code == 200
    response = raw_response.json()
    assert response["totalResults"] == 1
    assert response["items"][0]["login"] == "william.arndt"


def test_delete_resource_users(instance, demo_data):
    initial_data = instance.core.get_resource_users("33001", response_type=OBJ_RESPONSE)
    assert initial_data.totalResults == 1
    assert initial_data.users[0] == "william.arndt"

    raw_response = instance.core.delete_resource_users(
        resource_id="33001",
        response_type=FULL_RESPONSE,
    )
    assert raw_response.status_code == 204
    modified_data = instance.core.get_resource_users(
        "33001", response_type=OBJ_RESPONSE
    )
    assert modified_data.totalResults == 0
    instance.core.set_resource_users(resource_id="33001", users=initial_data.users)


def test_add_resource_users(instance, demo_data):
    raw_response = instance.core.set_resource_users(
        resource_id="33001",
        users=["william.arndt", "admin"],
        response_type=FULL_RESPONSE,
    )
    assert raw_response.status_code == 200, raw_response.json()
    response = raw_response.json()
    assert len(response["items"]) == 2
    assert response["items"][0]["login"] == "william.arndt"
    assert response["items"][1]["login"] == "admin"
