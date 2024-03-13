import json
import logging
from pathlib import Path

from requests import Response

from ofsc import OFSC
from ofsc.common import FULL_RESPONSE, OBJ_RESPONSE, TEXT_RESPONSE
from ofsc.models import (
    ActivityType,
    ActivityTypeGroup,
    ActivityTypeGroupListResponse,
    ActivityTypeList,
    ActivityTypeListResponse,
    Condition,
    Property,
    SharingEnum,
    Translation,
    TranslationList,
    Workskill,
    WorkskillCondition,
    WorskillConditionList,
)


def test_activity_type_group_model(instance):
    instance.core.config.auto_model = True
    metadata_response = instance.metadata.get_activity_type_groups(
        response_type=OBJ_RESPONSE
    )
    assert isinstance(
        metadata_response, ActivityTypeGroupListResponse
    ), f"Response is {type(metadata_response)}"
    for item in metadata_response.items:
        assert isinstance(item, ActivityTypeGroup)


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


# Activity Types


def test_get_activity_types_auto_model_full(instance, demo_data, pp):
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


def test_get_activity_types_auto_model_obj(instance, demo_data, pp):
    instance.auto_model = True
    expected_activity_types = demo_data.get("metadata").get("expected_activity_types")
    response = instance.metadata.get_activity_types(offset=0, limit=30)
    logging.debug(pp.pformat(response))
    assert isinstance(response, ActivityTypeListResponse)

    assert response.items is not None
    assert len(response.items) == 30
    assert isinstance(response.items[0], ActivityType)
    assert response.totalResults == expected_activity_types
    assert response.items[28].label == "crew_assignment"
    assert response.items[12].label == "06"
    activityType = response.items[12]
    assert activityType.features is not None
    assert activityType.features.allowMoveBetweenResources == True


def test_get_activity_type_auto_model_full(instance, demo_data, pp):
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


def test_activity_types_no_model_list(instance):
    limit = 10
    instance.core.config.auto_model = False
    metadata_response = instance.metadata.get_activity_types(
        response_type=OBJ_RESPONSE, offset=0, limit=limit
    )
    assert isinstance(metadata_response, dict)
    logging.debug(json.dumps(metadata_response, indent=4))
    objList = ActivityTypeList.model_validate(metadata_response["items"])
    ## Iterate through the list and validate each item
    for idx, obj in enumerate(objList):
        assert type(obj) == ActivityType
        assert obj.label == metadata_response["items"][idx]["label"]
        new_obj = ActivityType.model_validate(
            instance.metadata.get_activity_type(
                label=obj.label, response_type=OBJ_RESPONSE
            )
        )
        assert new_obj.label == obj.label


def test_activity_type_no_model_simple(instance):
    instance.core.config.auto_model = False
    metadata_response = instance.metadata.get_activity_type(
        label="01", response_type=OBJ_RESPONSE
    )
    assert isinstance(metadata_response, dict)
    logging.debug(json.dumps(metadata_response, indent=4))
    obj = ActivityType.model_validate(metadata_response)
    assert obj.label == metadata_response["label"]
    assert obj.translations == TranslationList.model_validate(
        metadata_response["translations"]
    )
