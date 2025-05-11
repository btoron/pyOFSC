import json
import logging

import pytest
from pydantic import ValidationError

from ofsc.common import OBJ_RESPONSE
from ofsc.models import (
    ActivityType,
    ActivityTypeGroup,
    CapacityArea,
    CapacityAreaListResponse,
    CapacityCategoryListResponse,
    DailyExtractFiles,
    DailyExtractFolders,
    DailyExtractItem,
    DailyExtractItemList,
    ItemList,
    Translation,
    TranslationList,
    Workskill,
    WorkskillList,
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
        assert isinstance(obj, Translation)
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


def test_translation_map():
    base = [
        {"language": "en", "name": "Estimate", "languageISO": "en-US"},
        {"language": "es", "name": "Estimar"},
    ]
    ## Map the list into a dictionary with the language as the key
    objMap = TranslationList.model_validate(base).map()
    assert objMap.get("en").name == "Estimate"


# region Activity Type Groups
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


# endregion

# region Capacity Areas


def test_capacity_area_model_base():
    base = {
        "label": "CapacityArea",
        "name": "Capacity Area",
        "type": "area",
        "status": "active",
        "workZones": {
            "href": "https://<instance_name>.fs.ocs.oraclecloud.com/rest/ofscMetadata/v1/capacityAreas/CapacityArea/workZones"
        },
        "organizations": {
            "href": "https://<instance_name>.fs.ocs.oraclecloud.com/rest/ofscMetadata/v1/capacityAreas/CapacityArea/organizations"
        },
        "capacityCategories": {
            "href": "https://<instance_name>.fs.ocs.oraclecloud.com/rest/ofscMetadata/v1/capacityAreas/CapacityArea/capacityCategories"
        },
        "timeIntervals": {
            "href": "https://<instance_name>.fs.ocs.oraclecloud.com/rest/ofscMetadata/v1/capacityAreas/CapacityArea/timeIntervals"
        },
        "timeSlots": {
            "href": "https://<instance_name>.fs.ocs.oraclecloud.com/rest/ofscMetadata/v1/capacityAreas/CapacityArea/timeSlots"
        },
        "parentLabel": "66000",
        "configuration": {
            "definitionLevel": ["day"],
            "isAllowCloseOnWorkzoneLevel": False,
            "byDay": "percentIncludeOtherActivities",
            "byCapacityCategory": "minutes",
            "byTimeSlot": "minutes",
            "isTimeSlotBase": False,
        },
    }
    obj = CapacityArea.model_validate(base)
    assert obj.label == base["label"]


def test_capacity_area_list_model_base():
    base = {
        "items": [
            {
                "label": "22",
                "name": "Sunrise Enterprise",
                "type": "group",
                "status": "active",
            },
            {
                "label": "ASIA",
                "name": "Asia",
                "type": "area",
                "status": "active",
                "parent": {"label": "22"},
            },
            {
                "label": "EUROPE",
                "name": "Europe",
                "type": "area",
                "status": "active",
                "parent": {"label": "22"},
            },
            {
                "label": "66000",
                "name": "Newfoundland",
                "type": "group",
                "status": "active",
                "parent": {"label": "22"},
            },
            {
                "label": "CapacityArea",
                "name": "Capacity Area",
                "type": "area",
                "status": "active",
                "parent": {"label": "66000"},
            },
            {
                "label": "routing",
                "name": "Planning",
                "type": "area",
                "status": "active",
                "parent": {"label": "22"},
            },
            {
                "label": "S??o Jos??",
                "name": "S??o Jos?? dos Campos",
                "type": "area",
                "status": "active",
                "parent": {"label": "22"},
            },
            {
                "label": "Texasin",
                "name": "Texas inventories",
                "type": "group",
                "status": "active",
                "parent": {"label": "22"},
            },
            {
                "label": "routing_bucket_T",
                "name": "Texas City",
                "type": "area",
                "status": "active",
                "parent": {"label": "Texasin"},
            },
        ]
    }

    obj = CapacityAreaListResponse.model_validate(base)


# endregion
# region Workskills
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
    metadata_response = instance.metadata.get_workskills(response_type=OBJ_RESPONSE)
    logging.debug(json.dumps(metadata_response, indent=4))
    objList = WorkskillList.model_validate(metadata_response["items"])


# endregion
# region Capacity Categories
capacityCategoryList = {
    "hasMore": True,
    "totalResults": 8,
    "limit": 1,
    "offset": 2,
    "items": [
        {
            "label": "UP",
            "name": "Upgrade",
            "active": True,
            "workSkills": [{"label": "UP", "ratio": 1, "startDate": "2000-01-01"}],
            "workSkillGroups": [],
            "timeSlots": [
                {"label": "08-10"},
                {"label": "10-12"},
                {"label": "13-15"},
                {"label": "15-17"},
            ],
            "translations": [
                {"language": "en", "name": "Upgrade", "languageISO": "en-US"},
                {"language": "es", "name": "Upgrade", "languageISO": "es-ES"},
                {"language": "fr", "name": "Upgrade", "languageISO": "fr-FR"},
                {"language": "nl", "name": "Upgrade", "languageISO": "nl-NL"},
                {"language": "de", "name": "Upgrade", "languageISO": "de-DE"},
                {"language": "ro", "name": "Upgrade", "languageISO": "ro-RO"},
                {
                    "language": "ru",
                    "name": "????????????????????????",
                    "languageISO": "ru-RU",
                },
                {"language": "br", "name": "Upgrade", "languageISO": "pt-BR"},
            ],
            "links": [
                {
                    "rel": "canonical",
                    "href": "https://<instance_name>.fs.ocs.oraclecloud.com/rest/ofscMetadata/v1/capacityCategories/UP",
                },
                {
                    "rel": "describedby",
                    "href": "https://<instance_name>.fs.ocs.oraclecloud.com/rest/ofscMetadata/v1/metadata-catalog/capacityCategories",
                },
            ],
        }
    ],
    "links": [
        {
            "rel": "canonical",
            "href": "https://<instance_name>.fs.ocs.oraclecloud.com/rest/ofscMetadata/v1/capacityCategories?limit=1&offset=2",
        },
        {
            "rel": "prev",
            "href": "https://<instance_name>.fs.ocs.oraclecloud.com/rest/ofscMetadata/v1/capacityCategories?offset=1",
        },
        {
            "rel": "next",
            "href": "https://<instance_name>.fs.ocs.oraclecloud.com/rest/ofscMetadata/v1/capacityCategories?offset=3",
        },
        {
            "rel": "describedby",
            "href": "https://<instance_name>.fs.ocs.oraclecloud.com/rest/ofscMetadata/v1/metadata-catalog/capacityCategories",
        },
    ],
}


def test_capacity_category_model_list():
    objList = CapacityCategoryListResponse.model_validate(capacityCategoryList)
    assert objList.hasMore == capacityCategoryList["hasMore"]
    assert objList.totalResults == capacityCategoryList["totalResults"]
    assert objList.limit == capacityCategoryList["limit"]
    assert objList.offset == capacityCategoryList["offset"]
    assert len(objList.items) == len(capacityCategoryList["items"])
    assert objList.links == capacityCategoryList["links"]
    for idx, item in enumerate(objList.items):
        assert item.label == capacityCategoryList["items"][idx]["label"]
        assert item.name == capacityCategoryList["items"][idx]["name"]
        assert item.active == capacityCategoryList["items"][idx]["active"]
        assert item.timeSlots == ItemList.model_validate(
            capacityCategoryList["items"][idx]["timeSlots"]
        )
        assert item.translations == TranslationList.model_validate(
            capacityCategoryList["items"][idx]["translations"]
        )
        assert item.links == capacityCategoryList["items"][idx]["links"]
        # assert item.workSkills == capacityCategoryList["items"][idx]["workSkills"]
        assert item.workSkillGroups == ItemList.model_validate(
            capacityCategoryList["items"][idx]["workSkillGroups"]
        )


# endregion


def test_daily_extract_subfolders():
    """
    Test the daily extract subfolders
    """
    base = {
        "name": "folders",
        "folders": {
            "items": [
                {
                    "name": "2015-07-01",
                    "links": [
                        {
                            "rel": "canonical",
                            "href": "https://instance.fs.ocs.oraclecloud.com/rest/ofscCore/v1/folders/dailyExtract/folders/2015-07-01",
                        }
                    ],
                },
                {
                    "name": "2015-07-02",
                    "links": [
                        {
                            "rel": "canonical",
                            "href": "https://instance.fs.ocs.oraclecloud.com/rest/ofscCore/v1/folders/dailyExtract/folders/2015-07-02",
                        }
                    ],
                },
            ],
            "links": [
                {
                    "rel": "canonical",
                    "href": "https://instance.fs.ocs.oraclecloud.com/rest/ofscCore/v1/folders/dailyExtract/folders",
                }
            ],
        },
        "links": [
            {
                "rel": "canonical",
                "href": "https://instance.fs.ocs.oraclecloud.com/rest/ofscCore/v1/folders/dailyExtract/folders",
            },
            {
                "rel": "describedby",
                "href": "https://instance.fs.ocs.oraclecloud.com/rest/ofscCore/v1/metadata-catalog/folders",
            },
        ],
    }
    obj = DailyExtractFolders.model_validate(base)
    assert obj.name == base["name"]
    assert isinstance(obj.folders, DailyExtractItemList)
    assert isinstance(obj.folders.items[0], DailyExtractItem)
    assert obj.folders.items[0].name == base["folders"]["items"][0]["name"]


def test_daily_extract_files():
    base = {
        "name": "files",
        "files": {
            "items": [
                {
                    "name": "activity-data.tar.gz",
                    "bytes": 3943529,
                    "mediaType": "application/octet-stream",
                    "links": [
                        {
                            "rel": "canonical",
                            "href": "https://test.fs.ocs.oraclecloud.com/rest/ofscCore/v1/folders/dailyExtract/folders/2015-07-02/files/activity-data.tar.gz",
                        }
                    ],
                },
                {
                    "name": "inventory-data.tar.gz",
                    "bytes": 32727812,
                    "mediaType": "application/octet-stream",
                    "links": [
                        {
                            "rel": "canonical",
                            "href": "https://test.fs.ocs.oraclecloud.com/rest/ofscCore/v1/folders/dailyExtract/folders/2015-07-02/files/inventory-data.tar.gz",
                        }
                    ],
                },
            ]
        },
        "links": [
            {
                "rel": "canonical",
                "href": "https://test.fs.ocs.oraclecloud.com/rest/ofscCore/v1/folders/dailyExtract/folders/2015-07-02/files",
            },
            {
                "rel": "describedby",
                "href": "https://test.fs.ocs.oraclecloud.com/rest/ofscCore/v1/metadata-catalog/folders",
            },
        ],
    }
    obj = DailyExtractFiles.model_validate(base)
    assert obj.name == base["name"]
    assert isinstance(obj.files, DailyExtractItemList)
    assert isinstance(obj.files.items[0], DailyExtractItem)
    assert obj.files.items[0].name == base["files"]["items"][0]["name"]
    assert obj.files.items[0].bytes == base["files"]["items"][0]["bytes"]
    assert obj.files.items[0].mediaType == base["files"]["items"][0]["mediaType"]
