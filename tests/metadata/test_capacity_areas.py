import logging

import pytest

from ofsc.common import FULL_RESPONSE


# Capacity tests
def test_get_capacity_areas_simple(instance, pp, demo_data):
    capacity_areas = demo_data.get("metadata").get("expected_capacity_areas")
    raw_response = instance.metadata.get_capacity_areas(response_type=FULL_RESPONSE)
    assert raw_response.status_code == 200
    logging.debug(pp.pformat(raw_response.json()))
    response = raw_response.json()
    logging.debug(pp.pformat(response))
    assert response["items"] is not None
    assert len(response["items"]) == len(capacity_areas)
    assert response["items"][0]["label"] == "CAUSA"


def test_get_capacity_area(instance, pp):
    raw_response = instance.metadata.get_capacity_area(
        "FLUSA", response_type=FULL_RESPONSE
    )
    assert raw_response.status_code == 200
    logging.debug(pp.pformat(raw_response.json()))
    response = raw_response.json()
    logging.debug(pp.pformat(response))
    assert response["label"] is not None
    assert response["label"] == "FLUSA"
    assert response["configuration"] is not None
    assert response["parentLabel"] is not None
    assert response["parentLabel"] == "SUNRISE"
