import logging

from ofsc import OFSC
from ofsc.common import FULL_RESPONSE
from ofsc.models import (
    EnumerationValue,
    EnumerationValueList,
    Property,
    Translation,
    TranslationList,
)


def test_get_property(instance):
    metadata_response = instance.metadata.get_property(
        "XA_CASE_ACCOUNT", response_type=FULL_RESPONSE
    )
    assert metadata_response.status_code == 200
    response = metadata_response.json()
    logging.debug(response)
    assert response["label"] == "XA_CASE_ACCOUNT"
    assert response["type"] == "string"
    assert response["entity"] == "activity"
    property = Property.model_validate(response)


def test_get_properties(instance, demo_data):
    metadata_response = instance.metadata.get_properties(response_type=FULL_RESPONSE)
    expected_properties = demo_data.get("metadata").get("expected_properties")
    assert metadata_response.status_code == 200
    response = metadata_response.json()
    assert response["totalResults"]
    assert response["totalResults"] == expected_properties  # 22.D
    assert response["items"][0]["label"] == "ITEM_NUMBER"


def test_create_replace_property(instance: OFSC, faker):
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
    en_name = Translation(name=property.name)
    property.translations = TranslationList([en_name])
    metadata_response = instance.metadata.create_or_replace_property(
        property, response_type=FULL_RESPONSE
    )
    logging.debug(metadata_response.json())
    assert metadata_response.status_code < 299, metadata_response.json()

    metadata_response = instance.metadata.get_property(
        property.label, response_type=FULL_RESPONSE
    )
    assert metadata_response.status_code < 299
    response = metadata_response.json()
    assert response["name"] == property.name
    assert response["type"] == property.type
    assert response["entity"] == property.entity
    assert response.get("translations")[0]["name"] == property.translations[0].name
    property = Property.model_validate(response)


def test_create_replace_property_noansi(instance: OFSC, request_logging, faker):
    property = Property.model_validate(
        {
            "label": faker.pystr(),
            "type": "string",
            "entity": "activity",
            "name": "césped",
            "translations": [],
            "gui": "text",
        }
    )
    en_name = Translation(name=property.name)
    property.translations = TranslationList([en_name])
    metadata_response = instance.metadata.create_or_replace_property(
        property, response_type=FULL_RESPONSE
    )
    logging.debug(metadata_response.json())
    assert metadata_response.status_code < 299, metadata_response.json()

    metadata_response = instance.metadata.get_property(
        property.label, response_type=FULL_RESPONSE
    )
    assert metadata_response.status_code < 299
    response = metadata_response.json()
    assert response["name"] == property.name
    assert response["type"] == property.type
    assert response["entity"] == property.entity
    assert response.get("translations")[0]["name"] == property.translations[0].name
    property = Property.model_validate(response)


def test_get_enumeration_values_full(instance: OFSC):
    metadata_response = instance.metadata.get_enumeration_values(
        "complete_code", response_type=FULL_RESPONSE
    )
    assert metadata_response.status_code == 200
    response = metadata_response.json()
    assert response["totalResults"]


def test_get_enumeration_values_obj(instance: OFSC):
    response = instance.metadata.get_enumeration_values("complete_code")
    assert isinstance(response, EnumerationValueList)
    for value in response.items:
        assert isinstance(value, EnumerationValue)
        assert value.map.get("en") is not None
