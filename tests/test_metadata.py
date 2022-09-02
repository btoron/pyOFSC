import json
import logging

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
from requests import Response


def test_get_workskills(instance):
    logging.info("...Get all skills")
    metadata_response = instance.metadata.get_workskills(response_type=FULL_RESPONSE)
    response = metadata_response.json()
    assert response["totalResults"] is not None
    assert response["totalResults"] == 6  # 22.B
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


def test_create_workskill(instance):
    logging.info("...create one skill")
    skill = Workskill(label="TEST", name="test", sharing=SharingEnum.maximal)
    logging.warning(skill.json())
    metadata_response = instance.metadata.create_or_update_workskill(
        skill=skill, response_type=FULL_RESPONSE
    )
    response = metadata_response.json()
    assert response["label"] == skill.label
    assert response["name"] == skill.name
    # Cleaning up
    instance.metadata.delete_workskill(label=skill.label, response_type=FULL_RESPONSE)


def test_delete_workskill(instance):
    logging.info("...delete one skill")
    skill = Workskill(label="TEST", name="test", sharing=SharingEnum.maximal)
    logging.warning(skill.json())
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


def test_get_workskill_conditions(instance, pp):
    logging.info("... get workskill conditions")
    metadata_response = instance.metadata.get_workskill_conditions(
        response_type=FULL_RESPONSE
    )
    response = metadata_response.json()
    assert metadata_response.status_code == 200
    logging.debug(pp.pformat(response))
    assert response["totalResults"] is not None
    assert response["totalResults"] == 7
    for item in response["items"]:
        logging.debug(pp.pformat(item))
        ws_item = WorkskillCondition.parse_obj(item)
        logging.debug(pp.pformat(ws_item))
        assert ws_item.label == item["label"]
        for condition in ws_item.conditions:
            assert type(condition) == Condition


def test_replace_workskill_conditions(instance, pp):
    logging.info("... replace workskill conditions")
    response = instance.metadata.get_workskill_conditions(response_type=JSON_RESPONSE)
    assert response["totalResults"] is not None
    assert response["totalResults"] == 7
    ws_list = WorskillConditionList.parse_obj(response["items"])
    metadata_response = instance.metadata.replace_workskill_conditions(ws_list)
    logging.debug(pp.pformat(metadata_response.text))
    assert metadata_response.status_code == 200
    assert response["totalResults"] is not None
    assert response["totalResults"] == 7


def test_get_workzones(instance):
    logging.info("...Get all workzones")
    metadata_response = instance.metadata.get_workzones(
        offset=0, limit=1000, response_type=FULL_RESPONSE
    )
    response = metadata_response.json()
    assert response["totalResults"] is not None
    assert response["totalResults"] == 18  # 22.B
    assert response["items"][0]["workZoneLabel"] == "ALTAMONTE SPRINGS"
    assert response["items"][1]["workZoneName"] == "CASSELBERRY"


def test_get_resource_types(instance):
    logging.info("...Get all Resource Types")
    metadata_response = instance.metadata.get_resource_types(
        response_type=FULL_RESPONSE
    )
    response = metadata_response.json()
    logging.warning(response["items"])
    assert response["totalResults"] is not None
    assert response["totalResults"] == 10  # 22.B


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


def test_create_replace_property(instance: OFSC, request_logging, faker):
    logging.info("... Create property")
    property = Property.parse_obj(
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
    property = Property.parse_obj(response)
