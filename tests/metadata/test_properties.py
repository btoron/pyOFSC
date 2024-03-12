import logging

from ofsc import OFSC
from ofsc.common import FULL_RESPONSE
from ofsc.models import Property, Translation


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


def test_get_properties(instance, demo_data):
    logging.info("...Get properties")
    metadata_response = instance.metadata.get_properties(response_type=FULL_RESPONSE)
    expected_properties = demo_data.get("metadata").get("expected_properties")
    assert metadata_response.status_code == 200
    response = metadata_response.json()
    assert response["totalResults"]
    assert response["totalResults"] == expected_properties  # 22.D
    assert response["items"][0]["label"] == "ITEM_NUMBER"


def test_create_replace_property(instance: OFSC, request_logging, faker):
    logging.info("... Create property")
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
    property = Property.model_validate(response)
