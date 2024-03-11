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
    logging.info("...Get all skills")
    metadata_response = instance.metadata.get_workskills(response_type=FULL_RESPONSE)
    response = metadata_response.json()
    expected_workskills = demo_data.get("metadata").get("expected_workskills")
    assert response["totalResults"] is not None
    assert response["totalResults"] == expected_workskills  # 22.B
    assert response["items"][0]["label"] == "EST"
    assert response["items"][1]["name"] == "Residential"


def test_get_workskill(instance):
    logging.info("...Get one skill")
    metadata_response = instance.metadata.get_workskill(
        label="RES", response_type=FULL_RESPONSE
    )
    response = metadata_response.json()
    assert response["label"] == "RES"
    assert response["name"] == "Residential"


def test_create_workskill(instance, pp):
    logging.info("...create one skill")
    skill = Workskill(label="TEST", name="test", sharing=SharingEnum.maximal)
    logging.warning(f"TEST.Create WorkSkill: IN: {skill.model_dump_json()}")
    metadata_response = instance.metadata.create_or_update_workskill(
        skill=skill, response_type=FULL_RESPONSE
    )
    response = metadata_response.json()
    logging.info(pp.pformat(response))
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
    logging.info("... get workskill conditions")
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
    logging.info("... replace workskill conditions")
    response = instance.metadata.get_workskill_conditions(response_type=JSON_RESPONSE)
    expected_workskill_conditions = demo_data.get("metadata").get(
        "expected_workskill_conditions"
    )
    assert response["totalResults"] is not None
    assert response["totalResults"] == expected_workskill_conditions
    ws_list = WorskillConditionList.model_validate(response["items"])
    metadata_response = instance.metadata.replace_workskill_conditions(ws_list)
    logging.debug(pp.pformat(metadata_response.text))
    assert metadata_response.status_code == 200
    assert response["totalResults"] is not None
    assert response["totalResults"] == expected_workskill_conditions


def test_get_workzones(instance):
    logging.info("...Get all workzones")
    metadata_response = instance.metadata.get_workzones(
        offset=0, limit=1000, response_type=FULL_RESPONSE
    )
    response = metadata_response.json()
    assert response["totalResults"] is not None
    assert response["totalResults"] == 18  # 22.B
    assert response["items"][0]["workZoneLabel"] == "ALTAMONTE_SPRINGS"
    assert response["items"][1]["workZoneName"] == "CASSELBERRY"


def test_get_resource_types(instance, demo_data):
    logging.info("...Get all Resource Types")
    metadata_response = instance.metadata.get_resource_types(
        response_type=FULL_RESPONSE
    )
    response = metadata_response.json()
    assert response["totalResults"] is not None
    assert response["totalResults"] == demo_data.get("metadata").get(
        "expected_resource_types"
    )


def test_get_property(instance):
    logging.info("...Get property info")
    metadata_response = instance.metadata.get_property(
        "XA_CASE_ACCOUNT", response_type=FULL_RESPONSE
    )
    assert metadata_response.status_code == 200
    response = metadata_response.json()
    logging.info(response)
    assert response["label"] == "XA_CASE_ACCOUNT"
    assert response["type"] == "string"
    assert response["entity"] == "activity"
    property = Property.parse_obj(response)


def test_get_properties(instance, demo_data):
    logging.info("...Get properties")
    metadata_response = instance.metadata.get_properties(response_type=FULL_RESPONSE)
    expected_properties = demo_data.get("metadata").get("expected_properties")
    assert metadata_response.status_code == 200
    response = metadata_response.json()
    assert response["totalResults"]
    assert response["totalResults"] == expected_properties  # 22.D
    assert response["items"][0]["label"] == "ITEM_NUMBER"


def test_create_replace_property(instance: OFSC, request_logging, faker):
    logging.info("... Create property")
    property = Property.model_validate(
        {
            "label": faker.pystr(),
            "type": "string",
            "entity": "activity",
            "name": faker.pystr(),
            "translations": [],
            "gui": "text",
        }
    )
    property.translations.__root__.append(Translation(name=property.name))
    metadata_response = instance.metadata.create_or_replace_property(
        property, response_type=FULL_RESPONSE
    )
    logging.warning(metadata_response.json())
    assert metadata_response.status_code < 299, metadata_response.json()

    metadata_response = instance.metadata.get_property(
        property.label, response_type=FULL_RESPONSE
    )
    assert metadata_response.status_code < 299
    response = metadata_response.json()
    assert response["name"] == property.name
    assert response["type"] == property.type
    assert response["entity"] == property.entity
    property = Property.model_validate(response)


def test_import_plugin_file(instance: OFSC):
    logging.info("... Import plugin via file")
    metadata_response = instance.metadata.import_plugin_file(Path("tests/test.xml"))
    assert metadata_response.status_code == 204


def test_import_plugin(instance: OFSC):
    logging.info("... Import plugin")
    metadata_response = instance.metadata.import_plugin(
        Path("tests/test.xml").read_text()
    )
    assert metadata_response.status_code == 204
