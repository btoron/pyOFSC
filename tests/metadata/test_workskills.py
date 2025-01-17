from ofsc.common import FULL_RESPONSE, OBJ_RESPONSE
from ofsc.models import (
    Condition,
    SharingEnum,
    Workskill,
    WorkskillCondition,
    WorkskillConditionList,
    WorkskillConditionListResponse,
    WorkskillListResponse,
)


def test_get_workskills_basic(instance, demo_data):
    metadata_response = instance.metadata.get_workskills(response_type=FULL_RESPONSE)
    response = metadata_response.json()
    expected_workskills = demo_data.get("metadata").get("expected_workskills")
    assert response["totalResults"] is not None
    assert response["totalResults"] >= expected_workskills
    assert response["items"][0]["label"] == "EST"
    assert response["items"][1]["name"] == "Residential"


def test_get_workskills_obj(instance):
    response = instance.metadata.get_workskills()
    assert isinstance(response, WorkskillListResponse)
    assert len(response.items) > 0


def test_get_workskill_basic(instance):
    response = instance.metadata.get_workskill("COM", response_type=FULL_RESPONSE)
    assert response.status_code == 200
    data = response.json()
    assert data["label"] == "COM"


def test_get_workskill_obj(instance):
    response = instance.metadata.get_workskill("COM")
    assert isinstance(response, Workskill)
    assert response.label == "COM"


def test_create_workskill(instance, pp):
    skill = Workskill(label="TESTWSKILL", name="test", sharing=SharingEnum.maximal)
    metadata_response = instance.metadata.create_or_update_workskill(
        skill=skill, response_type=FULL_RESPONSE
    )
    response = metadata_response.json()
    assert metadata_response.status_code < 299, response
    assert response["label"] == skill.label
    assert response["name"] == skill.name
    # Check if it is created
    metadata_response = instance.metadata.get_workskill(
        label=skill.label, response_type=FULL_RESPONSE
    )
    assert metadata_response.status_code == 200
    # Cleaning up
    instance.metadata.delete_workskill(label=skill.label, response_type=FULL_RESPONSE)


def test_delete_workskill(instance):
    skill = Workskill(label="TESTWSKILL", name="test", sharing=SharingEnum.maximal)
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
    # Check if it is deleted
    metadata_response = instance.metadata.get_workskill(
        label=skill.label, response_type=FULL_RESPONSE
    )
    assert metadata_response.status_code == 404


def test_get_workskill_conditions_basic(instance, pp, demo_data):
    metadata_response = instance.metadata.get_workskill_conditions(
        response_type=FULL_RESPONSE
    )
    expected_workskill_conditions = demo_data.get("metadata").get(
        "expected_workskill_conditions"
    )
    response = metadata_response.json()
    assert metadata_response.status_code == 200
    assert response["totalResults"] is not None
    assert response["totalResults"] >= expected_workskill_conditions
    for item in response["items"]:
        ws_item = WorkskillCondition.model_validate(item)
        assert ws_item.label == item["label"]
        for condition in ws_item.conditions:
            assert isinstance(condition, Condition)


def test_get_workskill_conditions_obj(instance):
    response = instance.metadata.get_workskill_conditions()
    assert isinstance(response, WorkskillConditionListResponse)
    assert len(response.items) > 0


def test_replace_workskill_conditions(instance, pp, demo_data):
    response = instance.metadata.get_workskill_conditions(response_type=OBJ_RESPONSE)
    expected_workskill_conditions = demo_data.get("metadata").get(
        "expected_workskill_conditions"
    )
    assert response.totalResults is not None
    assert response.totalResults >= expected_workskill_conditions
    current_count = response.totalResults
    ws_list = WorkskillConditionList.model_validate(response.items)
    metadata_response = instance.metadata.replace_workskill_conditions(
        ws_list, response_type=FULL_RESPONSE
    )
    assert metadata_response.status_code == 200
    assert response.totalResults >= expected_workskill_conditions
    assert response.totalResults >= current_count
