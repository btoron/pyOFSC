import json
import logging

from ofsc.common import FULL_RESPONSE


def test_get_users(instance, demo_data, pp):
    raw_response = instance.core.get_users(response_type=FULL_RESPONSE)
    logging.debug(pp.pformat(raw_response.json()))
    response = raw_response.json()
    logging.debug(pp.pformat(response))
    assert response["totalResults"] is not None
    assert response["totalResults"] == demo_data.get("get_users").get("totalResults")
    assert response["items"][0]["login"] == "admin"


def test_get_user(instance, demo_data, pp):
    raw_response = instance.core.get_user(login="chris", response_type=FULL_RESPONSE)
    logging.debug(pp.pformat(raw_response.json()))
    response = raw_response.json()
    logging.debug(pp.pformat(response))
    assert raw_response.status_code == 200
    assert response["login"] is not None
    assert response["login"] == "chris"
    assert response["resourceInternalIds"][0] == 3000000


def test_update_user(instance, demo_data, pp):
    raw_response = instance.core.get_user(login="chris", response_type=FULL_RESPONSE)
    assert raw_response.status_code == 200
    response = raw_response.json()
    assert response["name"] is not None
    assert response["name"] == "Chris"
    new_data = {}
    new_data["name"] = "Changed"
    raw_response = instance.core.update_user(
        login="chris", data=json.dumps(new_data), response_type=FULL_RESPONSE
    )
    assert raw_response.status_code == 200
    response = raw_response.json()
    assert response["name"] is not None
    assert response["name"] == "Changed"
    new_data = {}
    new_data["name"] = "Chris"
    raw_response = instance.core.update_user(
        login="chris", data=json.dumps(new_data), response_type=FULL_RESPONSE
    )
    assert raw_response.status_code == 200
    response = raw_response.json()
    assert response["name"] is not None
    assert response["name"] == "Chris"


def test_create_user(instance, demo_data, pp):
    new_data = {
        "name": "Test Name",
        "mainResourceId": "44042",
        "language": "en",
        "timeZone": "Arizona",
        "userType": "technician",
        "password": "123123123121212Abc!",
        "resources": ["44008", "44035", "44042"],
    }
    raw_response = instance.core.create_user(
        login="test_user", data=json.dumps(new_data), response_type=FULL_RESPONSE
    )
    assert raw_response.status_code == 200, raw_response.json()
    logging.debug(pp.pformat(raw_response.json()))
    response = raw_response.json()
    logging.debug(pp.pformat(response))

    assert response["name"] is not None
    assert response["name"] == "Test Name"

    raw_response = instance.core.delete_user(
        login="test_user", response_type=FULL_RESPONSE
    )
    assert raw_response.status_code == 200
    logging.debug(pp.pformat(raw_response.json()))
