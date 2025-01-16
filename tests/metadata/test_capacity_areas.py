import logging

from ofsc.common import FULL_RESPONSE
from ofsc.models import CapacityAreaListResponse


# Capacity tests
def test_get_capacity_areas_no_model_simple(instance, pp, demo_data):
    capacity_areas = demo_data.get("metadata").get("expected_capacity_areas")
    raw_response = instance.metadata.get_capacity_areas(response_type=FULL_RESPONSE)
    assert raw_response.status_code == 200
    logging.debug(pp.pformat(raw_response.json()))
    response = raw_response.json()
    logging.debug(pp.pformat(response))
    assert response["items"] is not None
    assert len(response["items"]) == len(
        capacity_areas
    ), f"Received {[i['label'] for i in response['items']]}"
    assert response["items"][0]["label"] == "CAUSA"


def test_get_capacity_areas_model_no_parameters(instance, pp, demo_data):
    capacity_areas = demo_data.get("metadata").get("expected_capacity_areas")
    metadata_response = instance.metadata.get_capacity_areas()
    assert isinstance(
        metadata_response, CapacityAreaListResponse
    ), f"Expected a CapacityAreaListResponse received {type(metadata_response)}"
    assert len(metadata_response.items) == len(capacity_areas)
    assert metadata_response.hasMore is False
    assert metadata_response.totalResults == len(capacity_areas)


def test_get_capacity_areas_model_with_parameters(instance, pp, demo_data):
    capacity_areas = demo_data.get("metadata").get("expected_capacity_areas")
    metadata_response = instance.metadata.get_capacity_areas(
        activeOnly=False,
        areasOnly=True,
        expandParent=True,
        fields=["label", "status", "parent.label"],
    )
    assert isinstance(
        metadata_response, CapacityAreaListResponse
    ), f"Expected a CapacityAreaListResponse received {type(metadata_response)}"
    expected_result = len([area for area in capacity_areas if area["type"] == "area"])
    assert len(metadata_response.items) == expected_result
    assert metadata_response.hasMore is False
    assert metadata_response.totalResults == expected_result

    metadata_response = instance.metadata.get_capacity_areas(
        activeOnly=False,
        areasOnly=True,
        expandParent=False,
        fields=["label", "status", "parent.label"],
    )
    assert isinstance(
        metadata_response, CapacityAreaListResponse
    ), f"Expected a CapacityAreaListResponse received {type(metadata_response)}"
    expected_result = len([area for area in capacity_areas if area["type"] == "area"])
    assert len(metadata_response.items) == expected_result
    assert metadata_response.hasMore is False
    assert metadata_response.totalResults == expected_result

    metadata_response = instance.metadata.get_capacity_areas(
        activeOnly=True,
        areasOnly=True,
        expandParent=False,
        fields=["label", "status", "parent.label"],
    )
    assert isinstance(
        metadata_response, CapacityAreaListResponse
    ), f"Expected a CapacityAreaListResponse received {type(metadata_response)}"
    expected_result = len(
        [
            area
            for area in capacity_areas
            if (area["type"] == "area" and area["status"] == "active")
        ]
    )
    assert len(metadata_response.items) == expected_result
    assert metadata_response.hasMore is False
    assert metadata_response.totalResults == expected_result


def test_get_capacity_area_no_model(instance, pp):
    raw_response = instance.metadata.get_capacity_area(
        "CAUSA", response_type=FULL_RESPONSE
    )
    assert raw_response.status_code == 200
    logging.debug(pp.pformat(raw_response.json()))
    response = raw_response.json()
    logging.debug(pp.pformat(response))
    assert response["label"] is not None
    assert response["label"] == "CAUSA"
    assert response["configuration"] is not None
    assert response["parentLabel"] is not None
    assert response["parentLabel"] == "SUNRISE"


def test_get_capacity_area_model(instance, pp, demo_data):
    metadata_response = instance.metadata.get_capacity_area("CAUSA")
    assert metadata_response.label == "CAUSA"
    assert metadata_response.configuration is not None
    assert metadata_response.parentLabel is not None
    assert metadata_response.parentLabel == "SUNRISE"
    assert metadata_response.status == "active"
    assert metadata_response.type == "area"
