import json

import pytest
from pydantic import ValidationError

from ofsc.models import (
    ActivityType,
    ActivityTypeGroup,
    CapacityArea,
    CapacityAreaListResponse,
    CapacityCategoryListResponse,
    ItemList,
    SubscriptionConfig,
    SubscriptionConfigItem,
    SubscriptionListResponse,
    Translation,
    TranslationList,
    Workskill,
)


def test_translation_model_base():
    base = {"language": "en", "name": "Estimate", "languageISO": "en-US"}
    obj = Translation.model_validate(base)
    assert obj.language == base["language"]
    assert obj.name == base["name"]


def test_translation_model_base_invalid():
    base = {"language": "xx", "Noname": "NoEstimate", "languageISO": "en-US"}
    with pytest.raises(ValidationError):
        Translation.model_validate(base)


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

    CapacityAreaListResponse.model_validate(base)


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
# region Subscriptions

subscription_config_item = {
    "events": ["activityUpdated"],
    "filterExpression": "not (activityType in ['IN','TC','BR']) and (event.user != 'ics_integ') and customerName != ''",
}


def test_subscription_config_item_model_base():
    obj = SubscriptionConfigItem.model_validate(subscription_config_item)
    assert obj.events == subscription_config_item["events"]
    assert obj.filterExpression == subscription_config_item["filterExpression"]


subscription_config = [
    {
        "events": ["activityUpdated"],
        "filterExpression": "not (activityType in ['IN','TC','BR']) and (event.user != 'ics_integ') and customerName != ''",
    },
    {
        "events": ["activityCompleted"],
        "fields": ["firstManualOperationUser", "endTime"],
    },
]


def test_subscription_config_model_base():
    obj = SubscriptionConfig.model_validate(subscription_config)
    assert obj[0].events == subscription_config[0]["events"]
    assert obj[1].fields == subscription_config[1]["fields"]


subscription_list = {
    "items": [
        {
            "subscriptionId": "356a192b7913b04c54574d18c28d46e6395428ab",
            "subscriptionTitle": "My first subscription",
            "applicationId": "middleware1",
            "createdTime": "2017-05-04 07:39:19",
            "expirationTime": "2017-05-05 17:39:19",
            "subscriptionConfig": [
                {
                    "events": ["activityUpdated"],
                    "filterExpression": "not (activityType in ['IN','TC','BR']) and (event.user != 'ics_integ') and customerName != ''",
                }
            ],
        },
        {
            "subscriptionId": "da4b9237bacccdf19c0760cab7aec4a8359010b0",
            "subscriptionTitle": "My second subscription",
            "applicationId": "middleware1",
            "createdTime": "2017-05-04 07:39:19",
            "expirationTime": "2017-05-05 17:39:19",
            "subscriptionConfig": [
                {
                    "events": ["activityCompleted"],
                    "fields": ["firstManualOperationUser", "endTime"],
                }
            ],
        },
    ]
}


def test_subscription_model_list():
    objList = SubscriptionListResponse.model_validate(subscription_list)
    assert (
        objList.items[0].subscriptionId
        == subscription_list["items"][0]["subscriptionId"]
    )
    assert (
        objList.items[0].subscriptionTitle
        == subscription_list["items"][0]["subscriptionTitle"]
    )
    assert (
        objList.items[0].applicationId == subscription_list["items"][0]["applicationId"]
    )
    assert objList.items[0].createdTime == subscription_list["items"][0]["createdTime"]
    assert (
        objList.items[0].expirationTime
        == subscription_list["items"][0]["expirationTime"]
    )
    assert (
        objList.items[0].subscriptionConfig[0].events
        == subscription_list["items"][0]["subscriptionConfig"][0]["events"]
    )
    assert (
        objList.items[1].subscriptionId
        == subscription_list["items"][1]["subscriptionId"]
    )
    assert (
        objList.items[1].subscriptionTitle
        == subscription_list["items"][1]["subscriptionTitle"]
    )
    assert (
        objList.items[1].applicationId == subscription_list["items"][1]["applicationId"]
    )
    assert objList.items[1].createdTime == subscription_list["items"][1]["createdTime"]
    assert (
        objList.items[1].expirationTime
        == subscription_list["items"][1]["expirationTime"]
    )
    assert (
        objList.items[1].subscriptionConfig[0].events
        == subscription_list["items"][1]["subscriptionConfig"][0]["events"]
    )
    assert (
        objList.items[1].subscriptionConfig[0].fields
        == subscription_list["items"][1]["subscriptionConfig"][0]["fields"]
    )
