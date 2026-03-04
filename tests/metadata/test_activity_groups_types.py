import json
import logging
from pathlib import Path

import pytest
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
    WorkskillConditionList,
)


@pytest.mark.uses_real_data
def test_activity_type_group_model(instance):
    instance.core.config.auto_model = True
    metadata_response = instance.metadata.get_activity_type_groups(
        response_type=OBJ_RESPONSE
    )
    assert isinstance(metadata_response, ActivityTypeGroupListResponse), (
        f"Response is {type(metadata_response)}"
    )
    for item in metadata_response.items:
        assert isinstance(item, ActivityTypeGroup)


@pytest.mark.uses_real_data
def test_get_activity_type_groups(instance, pp, demo_data):
    raw_response = instance.metadata.get_activity_type_groups(
        response_type=FULL_RESPONSE
    )
    assert raw_response.status_code == 200
    logging.debug(pp.pformat(raw_response.json()))
    response = raw_response.json()
    logging.debug(pp.pformat(response))
    assert response["items"] is not None
    assert len(response["items"]) >= 1
    assert response["totalResults"] >= 1


@pytest.mark.uses_real_data
def test_get_activity_type_group(instance, demo_data, pp):
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
    assert len(response["activityTypes"]) >= 1


# Activity Types


@pytest.mark.uses_real_data
def test_get_activity_types_auto_model_full(instance, demo_data, pp):
    raw_response = instance.metadata.get_activity_types(response_type=FULL_RESPONSE)
    logging.debug(pp.pformat(raw_response.json()))
    response = raw_response.json()
    assert raw_response.status_code == 200
    logging.debug(pp.pformat(response))
    assert response["items"] is not None
    assert len(response["items"]) >= 1
    assert response["totalResults"] >= 1


@pytest.mark.uses_real_data
def test_get_activity_types_auto_model_obj(instance, demo_data, pp):
    instance.auto_model = True
    response = instance.metadata.get_activity_types(offset=0, limit=30)
    logging.debug(pp.pformat(response))
    assert isinstance(response, ActivityTypeListResponse)

    assert response.items is not None
    assert len(response.items) >= 1
    assert isinstance(response.items[0], ActivityType)
    assert response.totalResults >= 1


@pytest.mark.uses_real_data
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


@pytest.mark.uses_real_data
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


@pytest.mark.uses_real_data
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
