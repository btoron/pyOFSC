from ofsc.common import FULL_RESPONSE, OBJ_RESPONSE
from ofsc.models import TranslationList, WorkSkillAssignmentsList, WorkSkillGroup

_workskill_group = {
    "label": "TEST",
    "name": "Just a test",
    "assignToResource": True,
    "addToCapacityCategory": True,
    "active": True,
    "workSkills": [
        {"label": "COM", "ratio": 100},
        {"label": "EST", "ratio": 50},
        {"label": "installer", "ratio": 20},
    ],
    "translations": [
        {"language": "en", "name": "Just a test", "languageISO": "en-US"},
        {
            "language": "es",
            "name": "Prueba de un grupo de habilidades",
            "languageISO": "es-ES",
        },
    ],
    "links": [
        {
            "rel": "canonical",
            "href": "https://sunrise0511.fs.ocs.oraclecloud.com/rest/ofscMetadata/v1/workSkillGroups/TEST",
        },
        {
            "rel": "describedby",
            "href": "https://sunrise0511.fs.ocs.oraclecloud.com/rest/ofscMetadata/v1/metadata-catalog/workSkillGroups",
        },
    ],
}


def test_workskill_group_model_base():
    obj = WorkSkillGroup.model_validate(_workskill_group)
    assert obj.label == _workskill_group["label"]
    assert obj.name == _workskill_group["name"]
    assert obj.assignToResource == _workskill_group["assignToResource"]
    assert obj.addToCapacityCategory == _workskill_group["addToCapacityCategory"]
    assert obj.active == _workskill_group["active"]
    assert obj.workSkills == WorkSkillAssignmentsList.model_validate(
        _workskill_group["workSkills"]
    )
    assert obj.translations == TranslationList.model_validate(
        _workskill_group["translations"]
    )


def test_get_workskill_group_full(instance):
    metadata_response = instance.metadata.get_workskill_group(
        label="TESTGROUP", response_type=FULL_RESPONSE
    )
    response = metadata_response.json()
    assert response["label"] == "TESTGROUP"
    assert response["name"] == "Just a test"
    group = WorkSkillGroup.model_validate(response)
    assert group.label == "TESTGROUP"


def test_get_workskill_group_obj(instance):
    response = instance.metadata.get_workskill_group(
        label="TESTGROUP", response_type=OBJ_RESPONSE
    )
    assert isinstance(response, WorkSkillGroup)
    assert response.label == "TESTGROUP"
    assert response.name == "Just a test"


def test_get_workskill_groups_base(instance):
    metadata_response = instance.metadata.get_workskill_groups(
        response_type=FULL_RESPONSE
    )
    response = metadata_response.json()
    assert response["totalResults"] > 0
    assert response["totalResults"] == len(response["items"])
    for item in response["items"]:
        assert item["label"] is not None
        assert item["name"] is not None
        assert item["workSkills"] is not None
        assert item["translations"] is not None
        group = WorkSkillGroup.model_validate(item)
        assert group.label == item["label"]
        assert group.name == item["name"]
        assert group.workSkills == WorkSkillAssignmentsList.model_validate(
            item["workSkills"]
        )
        assert group.translations == TranslationList.model_validate(
            item["translations"]
        )


def test_workskill_groups_obj(instance):
    response = instance.metadata.get_workskill_groups(response_type=OBJ_RESPONSE)
    assert response.totalResults > 0
    assert len(response.items) == response.totalResults
    for item in response.items:
        assert isinstance(item, WorkSkillGroup)


def test_create_or_update_workskill_group(instance):
    group = WorkSkillGroup(
        label="TESTGROUP2",
        name="Just a test",
        assignToResource=True,
        addToCapacityCategory=True,
        active=True,
        workSkills=[
            {"label": "COM", "ratio": 100},
            {"label": "EST", "ratio": 50},
            {"label": "installer", "ratio": 20},
        ],
        translations=[
            {"language": "en", "name": "Just a test", "languageISO": "en-US"},
            {
                "language": "es",
                "name": "Prueba de un grupo de habilidades",
                "languageISO": "es-ES",
            },
        ],
    )
    response = instance.metadata.create_or_update_workskill_group(group)
    assert response.status_code == 201
    assert response.json() == _workskill_group
    assert response.json()["label"] == "TESTGROUP2"
