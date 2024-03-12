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


def test_get_workskills(instance, demo_data):
    metadata_response = instance.metadata.get_workskills(response_type=FULL_RESPONSE)
    response = metadata_response.json()
    expected_workskills = demo_data.get("metadata").get("expected_workskills")
    assert response["totalResults"] is not None
    assert response["totalResults"] == expected_workskills  # 22.B
    assert response["items"][0]["label"] == "EST"
    assert response["items"][1]["name"] == "Residential"


def test_get_workskill(instance):
    metadata_response = instance.metadata.get_workskill(
        label="RES", response_type=FULL_RESPONSE
    )
    response = metadata_response.json()
    assert response["label"] == "RES"
    assert response["name"] == "Residential"


def test_create_workskill(instance, pp):
    skill = Workskill(label="TEST", name="test", sharing=SharingEnum.maximal)
    metadata_response = instance.metadata.create_or_update_workskill(
        skill=skill, response_type=FULL_RESPONSE
    )
    response = metadata_response.json()
    logging.debug(pp.pformat(response))
    assert metadata_response.status_code < 299, response
    assert response["label"] == skill.label
    assert response["name"] == skill.name
    # Cleaning up
    instance.metadata.delete_workskill(label=skill.label, response_type=FULL_RESPONSE)


def test_delete_workskill(instance):
    skill = Workskill(label="TEST", name="test", sharing=SharingEnum.maximal)
    metadata_response = instance.metadata.create_or_update_workskill(
        skill=skill, response_type=FULL_RESPONSE
    )
    response = metadata_response.json()
    assert response["label"] == skill.label
    assert response["name"] == skill.name
    # Now delete
    metadata_response = instance.metadata.delete_workskill(
        label=skill.label, response_type=FULL_RESPONSE
    )
    assert metadata_response.status_code == 204


def test_get_workskill_conditions(instance, pp, demo_data):
    metadata_response = instance.metadata.get_workskill_conditions(
        response_type=FULL_RESPONSE
    )
    expected_workskill_conditions = demo_data.get("metadata").get(
        "expected_workskill_conditions"
    )
    response = metadata_response.json()
    assert metadata_response.status_code == 200
    logging.debug(pp.pformat(response))
    assert response["totalResults"] is not None
    assert response["totalResults"] == expected_workskill_conditions
    for item in response["items"]:
        logging.debug(pp.pformat(item))
        ws_item = WorkskillCondition.model_validate(item)
        logging.debug(pp.pformat(ws_item))
        assert ws_item.label == item["label"]
        for condition in ws_item.conditions:
            assert type(condition) == Condition


def test_replace_workskill_conditions(instance, pp, demo_data):
    response = instance.metadata.get_workskill_conditions(response_type=JSON_RESPONSE)
    expected_workskill_conditions = demo_data.get("metadata").get(
        "expected_workskill_conditions"
    )
    assert response["totalResults"] is not None
    assert response["totalResults"] == expected_workskill_conditions
    ws_list = WorskillConditionList.model_validate(response["items"])
    metadata_response = instance.metadata.replace_workskill_conditions(
        ws_list, response_type=FULL_RESPONSE
    )
    logging.debug(pp.pformat(metadata_response.text))
    assert metadata_response.status_code == 200
    assert response["totalResults"] is not None
    assert response["totalResults"] == expected_workskill_conditions


def test_get_workzones(instance):
    metadata_response = instance.metadata.get_workzones(
        offset=0, limit=1000, response_type=FULL_RESPONSE
    )
    response = metadata_response.json()
    assert response["totalResults"] is not None
    assert response["totalResults"] == 18  # 22.B
    assert response["items"][0]["workZoneLabel"] == "ALTAMONTE_SPRINGS"
    assert response["items"][1]["workZoneName"] == "CASSELBERRY"


def test_get_resource_types(instance, demo_data):
    metadata_response = instance.metadata.get_resource_types(
        response_type=FULL_RESPONSE
    )
    response = metadata_response.json()
    assert response["totalResults"] is not None
    assert response["totalResults"] == demo_data.get("metadata").get(
        "expected_resource_types"
    )


def test_import_plugin_file(instance: OFSC):
    metadata_response = instance.metadata.import_plugin_file(
        Path("tests/test.xml"), response_type=FULL_RESPONSE
    )
    assert metadata_response.status_code == 204


def test_import_plugin(instance: OFSC):
    metadata_response = instance.metadata.import_plugin(
        Path("tests/test.xml").read_text(), response_type=FULL_RESPONSE
    )
    assert metadata_response.status_code == 204
