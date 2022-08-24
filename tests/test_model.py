import json
import logging
from dbm import dumb

import pytest
from ofsc.common import FULL_RESPONSE, JSON_RESPONSE, TEXT_RESPONSE
from ofsc.models import (
    Condition,
    SharingEnum,
    Translation,
    TranslationList,
    Workskill,
    WorkskillCondition,
    WorkskillList,
    WorskillConditionList,
)
from pydantic import ValidationError
from requests import Response


def test_translation_model_base():
    base = {"language": "en", "name": "Estimate", "languageISO": "en-US"}
    obj = Translation.parse_obj(base)
    assert obj.language == base["language"]
    assert obj.name == base["name"]


def test_translation_model_base_invalid():
    base = {"language": "xx", "name": "Estimate", "languageISO": "en-US"}
    with pytest.raises(ValidationError) as validation:
        obj = Translation.parse_obj(base)


def test_translationlist_model_base():
    base = [
        {"language": "en", "name": "Estimate", "languageISO": "en-US"},
        {"language": "es", "name": "Estimación"},
    ]
    objList = TranslationList.parse_obj(base)
    for idx, obj in enumerate(objList):
        assert obj.language == base[idx]["language"]
        assert obj.name == base[idx]["name"]


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
    obj = Workskill.parse_obj(base)
    assert obj.label == base["label"]
    assert obj.active == base["active"]
    assert obj.name == base["name"]
    assert obj.sharing == base["sharing"]
    assert obj.translations == TranslationList.parse_obj(base["translations"])


def test_workskilllist_connected(instance):
    metadata_response = instance.metadata.get_workskills(response_type=JSON_RESPONSE)
    logging.warning(json.dumps(metadata_response, indent=4))
    objList = WorkskillList.parse_obj(metadata_response["items"])
