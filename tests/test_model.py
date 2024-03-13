import json
import logging
from dbm import dumb

import pytest
from pydantic import ValidationError
from requests import Response

from ofsc.common import FULL_RESPONSE, JSON_RESPONSE, TEXT_RESPONSE
from ofsc.models import (
    ActivityType,
    ActivityTypeGroup,
    ActivityTypeGroupList,
    ActivityTypeGroupListResponse,
    ActivityTypeList,
    Condition,
    SharingEnum,
    Translation,
    TranslationList,
    Workskill,
    WorkskillCondition,
    WorkskillList,
    WorskillConditionList,
)


def test_translation_model_base():
    base = {"language": "en", "name": "Estimate", "languageISO": "en-US"}
    obj = Translation.model_validate(base)
    assert obj.language == base["language"]
    assert obj.name == base["name"]


def test_translation_model_base_invalid():
    base = {"language": "xx", "Noname": "NoEstimate", "languageISO": "en-US"}
    with pytest.raises(ValidationError) as validation:
        obj = Translation.model_validate(base)


def test_translationlist_model_base():
    base = [
        {"language": "en", "name": "Estimate", "languageISO": "en-US"},
        {"language": "es", "name": "Estimación"},
    ]
    objList = TranslationList.model_validate(base)
    for idx, obj in enumerate(objList):
        assert type(obj) == Translation
        assert obj.language == base[idx]["language"]
        assert obj.name == base[idx]["name"]


def test_translationlist_model_json():
    base = [
        {"language": "en", "name": "Estimate", "languageISO": "en-US"},
        {"language": "es", "name": "Estimar"},
    ]
    objList = TranslationList.model_validate(base)
    assert json.loads(objList.model_dump_json())[0]["language"] == base[0]["language"]
    assert json.loads(objList.model_dump_json())[1]["name"] == base[1]["name"]


# Activity Type Groups
def test_activity_type_group_model_base():
    base = {
        "label": "customer",
        "name": "Customer",
        "activityTypes": [
            {"label": "4"},
            {"label": "5"},
            {"label": "6"},
            {"label": "7"},
            {"label": "8"},
            {"label": "installation"},
            {"label": "Testing"},
            {"label": "Multiday"},
            {"label": "SDI"},
        ],
        "translations": [
            {"language": "en", "name": "Customer", "languageISO": "en-US"},
            {"language": "es", "name": "Cliente", "languageISO": "es-ES"},
        ],
        "links": [
            {
                "rel": "canonical",
                "href": "https://<instance_name>.fs.ocs.oraclecloud.com/rest/ofscMetadata/v1/activityTypeGroups/customer",
            },
            {
                "rel": "describedby",
                "href": "https://<instance_name>.fs.ocs.oraclecloud.com/rest/ofscMetadata/v1/metadata-catalog/activityTypeGroups",
            },
        ],
    }
    obj = ActivityTypeGroup.model_validate(base)
    assert obj.label == base["label"]


def test_activity_type_model_base():
    base = {
        "label": "6",
        "name": "Phone Install/Upgrade",
        "active": True,
        "groupLabel": "customer",
        "defaultDuration": 48,
        "timeSlots": [
            {"label": "08-10"},
            {"label": "10-12"},
            {"label": "13-15"},
            {"label": "15-17"},
            {"label": "all-day"},
        ],
        "colors": {
            "pending": "FFDE00",
            "started": "5DBE3F",
            "suspended": "99FFFF",
            "cancelled": "80FF80",
            "notdone": "60CECE",
            "notOrdered": "FFCC99",
            "warning": "FFAAAA",
            "completed": "79B6EB",
        },
        "features": {
            "isTeamworkAvailable": False,
            "isSegmentingEnabled": False,
            "allowMoveBetweenResources": False,
            "allowCreationInBuckets": False,
            "allowReschedule": True,
            "supportOfNotOrderedActivities": True,
            "allowNonScheduled": True,
            "supportOfWorkZones": True,
            "supportOfWorkSkills": True,
            "supportOfTimeSlots": True,
            "supportOfInventory": True,
            "supportOfLinks": True,
            "supportOfPreferredResources": True,
            "allowMassActivities": True,
            "allowRepeatingActivities": True,
            "calculateTravel": True,
            "calculateActivityDurationUsingStatistics": True,
            "allowToSearch": True,
            "allowToCreateFromIncomingInterface": True,
            "enableDayBeforeTrigger": True,
            "enableReminderAndChangeTriggers": True,
            "enableNotStartedTrigger": True,
            "enableSwWarningTrigger": True,
            "calculateDeliveryWindow": True,
            "slaAndServiceWindowUseCustomerTimeZone": True,
            "supportOfRequiredInventory": True,
            "disableLocationTracking": False,
        },
        "translations": [
            {"language": "en", "name": "Phone Install/Upgrade", "languageISO": "en-US"},
            {
                "language": "es",
                "name": "Install/Upgrade: Telefono",
                "languageISO": "es-ES",
            },
        ],
        "links": [
            {
                "rel": "canonical",
                "href": "https://<instance_name>.fs.ocs.oraclecloud.com/rest/ofscMetadata/v1/activityTypes/6",
            },
            {
                "rel": "describedby",
                "href": "https://<instance_name>.fs.ocs.oraclecloud.com/rest/ofscMetadata/v1/metadata-catalog/activityTypes",
            },
        ],
    }
    obj = ActivityType.model_validate(base)
    assert obj.label == base["label"]


def test_workskill_model_base():
    base = {
        "label": "EST",
        "name": "Estimate",
        "active": True,
        "sharing": "maximal",
        "translations": [
            {"language": "en", "name": "Estimate", "languageISO": "en-US"}
        ],
        "links": [
            {
                "rel": "canonical",
                "href": "https://sunrise0511.etadirect.com/rest/ofscMetadata/v1/workSkills/EST",
            },
            {
                "rel": "describedby",
                "href": "https://sunrise0511.etadirect.com/rest/ofscMetadata/v1/metadata-catalog/workSkills",
            },
        ],
    }
    obj = Workskill.model_validate(base)
    assert obj.label == base["label"]
    assert obj.active == base["active"]
    assert obj.name == base["name"]
    assert obj.sharing == base["sharing"]
    assert obj.translations == TranslationList.model_validate(base["translations"])
    assert json.loads(obj.model_dump_json())["label"] == base["label"]


def test_workskilllist_connected(instance):
    metadata_response = instance.metadata.get_workskills(response_type=JSON_RESPONSE)
    logging.debug(json.dumps(metadata_response, indent=4))
    objList = WorkskillList.model_validate(metadata_response["items"])
