import json
import logging
from pathlib import Path

from requests import Response

from ofsc import OFSC
from ofsc.common import FULL_RESPONSE, JSON_RESPONSE, TEXT_RESPONSE
from ofsc.models import (
    Condition,
    Property,
    SharingEnum,
    Translation,
    TranslationList,
    Workskill,
    WorkskillCondition,
    WorskillConditionList,
)


def test_get_activity_type_groups(instance, pp, demo_data):
    expected_activity_type_groups = demo_data.get("metadata").get(
        "expected_activity_type_groups"
    )
    raw_response = instance.metadata.get_activity_type_groups(
        response_type=FULL_RESPONSE
    )
    assert raw_response.status_code == 200
    logging.debug(pp.pformat(raw_response.json()))
    response = raw_response.json()
    logging.debug(pp.pformat(response))
    assert response["items"] is not None
    assert len(response["items"]) == expected_activity_type_groups
    assert response["totalResults"] == expected_activity_type_groups
    assert response["items"][0]["label"] == "customer"


def test_get_activity_type_group(instance, demo_data, pp):
    expected_activity_types = demo_data.get("metadata").get(
        "expected_activity_types_customer"
    )
    raw_response = instance.metadata.get_activity_type_group(
        "customer", response_type=FULL_RESPONSE
    )
    logging.debug(pp.pformat(raw_response.json()))
    response = raw_response.json()
    assert raw_response.status_code == 200
    logging.debug(pp.pformat(response))
    assert response["label"] is not None
    assert response["label"] == "customer"
    assert response["activityTypes"] is not None
    assert len(response["activityTypes"]) == expected_activity_types
    assert response["activityTypes"][20]["label"] == "fitness_emergency"


def test_get_activity_types(instance, demo_data, pp):
    expected_activity_types = demo_data.get("metadata").get("expected_activity_types")
    raw_response = instance.metadata.get_activity_types(response_type=FULL_RESPONSE)
    logging.debug(pp.pformat(raw_response.json()))
    response = raw_response.json()
    assert raw_response.status_code == 200
    logging.debug(pp.pformat(response))
    assert response["items"] is not None
    assert len(response["items"]) == expected_activity_types
    assert response["totalResults"] == expected_activity_types
    assert response["items"][28]["label"] == "crew_assignment"
    assert response["items"][12]["label"] == "06"
    activityType = response["items"][12]
    assert activityType["features"] is not None
    assert len(activityType["features"]) == 27
    assert activityType["features"]["allowMoveBetweenResources"] == True


def test_get_activity_type(instance, demo_data, pp):
    raw_response = instance.metadata.get_activity_type(
        "fitness_emergency", response_type=FULL_RESPONSE
    )
    logging.debug(pp.pformat(raw_response.json()))
    response = raw_response.json()
    assert raw_response.status_code == 200
    logging.debug(pp.pformat(response))
    assert response["label"] is not None
    assert response["label"] == "fitness_emergency"
    assert response["features"] is not None
    assert len(response["features"]) == 27
    assert response["features"]["allowMoveBetweenResources"] == True
