import pytest

from ofsc.common import FULL_RESPONSE
from ofsc.models import Workzone, WorkzoneListResponse


def test_get_workzones_basic(instance):
    metadata_response = instance.metadata.get_workzones(
        offset=0, limit=1000, response_type=FULL_RESPONSE
    )
    response = metadata_response.json()
    assert response["totalResults"] is not None
    assert response["totalResults"] == 18  # 22.B
    assert response["items"][0]["workZoneLabel"] == "ALTAMONTE_SPRINGS"
    assert response["items"][1]["workZoneName"] == "CASSELBERRY"


def test_get_workzones_obj(instance):
    response = instance.metadata.get_workzones()
    assert isinstance(response, WorkzoneListResponse)
    assert len(response.items) > 0


def test_get_workzone(instance):
    # First get list to find a valid label
    response = instance.metadata.get_workzones()
    if len(response.items) == 0:
        pytest.skip("No workzones available to test with")

    # Get first workzone's label
    label = response.items[0].workZoneLabel

    # Test getting single workzone
    response = instance.metadata.get_workzone(label)
    assert isinstance(response, Workzone)
    assert response.workZoneLabel == label


def test_get_workzone_invalid(instance):
    with pytest.raises(Exception):
        instance.metadata.get_workzone("INVALID_WORKZONE")
