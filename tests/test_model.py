import json
import logging
from dbm import dumb

import pytest
from pydantic import ValidationError
from requests import Response

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
