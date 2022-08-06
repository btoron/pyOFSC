import logging

from ofsc.common import FULL_RESPONSE
from ofsc.models import SharingEnum, Workskill


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
