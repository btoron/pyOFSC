import pytest

from ofsc.common import FULL_RESPONSE
from ofsc.models import Workzone, WorkzoneListResponse


def test_get_workzones(instance):
    metadata_response = instance.metadata.get_workzones(
        offset=0, limit=1000, response_type=FULL_RESPONSE
    )
    response = metadata_response.json()
    assert response["totalResults"] is not None
    assert response["totalResults"] == 18  # 22.B
    assert response["items"][0]["workZoneLabel"] == "ALTAMONTE_SPRINGS"
    assert response["items"][1]["workZoneName"] == "CASSELBERRY"


def test_get_workzones_with_model(instance):
    """Test that get_workzones returns WorkzoneListResponse when using model parameter"""
    workzones = instance.metadata.get_workzones(offset=0, limit=100)

    # Verify type validation
    assert isinstance(workzones, WorkzoneListResponse)
    assert hasattr(workzones, "items")
    assert hasattr(workzones, "totalResults")
    assert isinstance(workzones.items, list)

    # Verify items are Workzone instances
    if len(workzones.items) > 0:
        assert isinstance(workzones.items[0], Workzone)
        assert hasattr(workzones.items[0], "workZoneLabel")
        assert hasattr(workzones.items[0], "workZoneName")


def test_get_workzone(instance):
    """Test getting a single workzone by label"""
    # First get a list of workzones to get a valid label
    workzones = instance.metadata.get_workzones(offset=0, limit=1)

    if len(workzones.items) == 0:
        pytest.skip("No workzones available to test")

    # Get the label of the first workzone
    label = workzones.items[0].workZoneLabel

    # Get the specific workzone
    workzone = instance.metadata.get_workzone(label)

    # Verify type validation
    assert isinstance(workzone, Workzone)
    assert workzone.workZoneLabel == label
    assert hasattr(workzone, "workZoneName")
    assert hasattr(workzone, "status")
    assert hasattr(workzone, "travelArea")


def test_get_workzone_with_response_type(instance):
    """Test getting a single workzone using FULL_RESPONSE"""
    # Get a valid label first
    workzones = instance.metadata.get_workzones(offset=0, limit=1)

    if len(workzones.items) == 0:
        pytest.skip("No workzones available to test")

    label = workzones.items[0].workZoneLabel

    # Get with FULL_RESPONSE
    response = instance.metadata.get_workzone(label, response_type=FULL_RESPONSE)

    assert response.status_code == 200
    workzone_data = response.json()
    assert workzone_data["workZoneLabel"] == label
    assert "workZoneName" in workzone_data
    assert "status" in workzone_data


@pytest.mark.uses_real_data
def test_replace_workzone(instance, faker):
    """Test replacing an existing workzone"""
    # First, get an existing workzone
    get_response = instance.metadata.get_workzones(
        offset=0, limit=1, response_type=FULL_RESPONSE
    )
    assert get_response.status_code == 200
    workzones = get_response.json()["items"]

    if not workzones:
        pytest.skip("No workzones available to test")

    # Get the first workzone and store original data
    original_workzone = Workzone.model_validate(workzones[0])

    # Modify the workzone
    modified_workzone = original_workzone.model_copy()
    modified_workzone.workZoneName = f"TEST_{faker.city()}"

    # Replace the workzone
    replace_response = instance.metadata.replace_workzone(
        modified_workzone, response_type=FULL_RESPONSE
    )
    assert replace_response.status_code in [200, 204], replace_response.json()

    # Restore original workzone
    restore_response = instance.metadata.replace_workzone(
        original_workzone, response_type=FULL_RESPONSE
    )
    assert restore_response.status_code in [200, 204]


@pytest.mark.uses_real_data
def test_replace_workzone_with_auto_resolve_conflicts(instance, faker):
    """Test replacing a workzone with auto_resolve_conflicts parameter"""
    # Get an existing workzone
    get_response = instance.metadata.get_workzones(
        offset=0, limit=1, response_type=FULL_RESPONSE
    )
    assert get_response.status_code == 200
    workzones = get_response.json()["items"]

    if not workzones:
        pytest.skip("No workzones available to test")

    # Get the first workzone and store original data
    original_workzone = Workzone.model_validate(workzones[0])

    # Modify the workzone
    modified_workzone = original_workzone.model_copy()
    modified_workzone.workZoneName = f"TEST_AUTO_{faker.city()}"

    # Replace with auto_resolve_conflicts
    replace_response = instance.metadata.replace_workzone(
        modified_workzone, auto_resolve_conflicts=True, response_type=FULL_RESPONSE
    )
    assert replace_response.status_code in [200, 204], replace_response.json()

    # Restore original workzone
    restore_response = instance.metadata.replace_workzone(
        original_workzone, response_type=FULL_RESPONSE
    )
    assert restore_response.status_code in [200, 204]


def test_replace_workzone_model_validation():
    """Test Workzone model with new fields"""
    # Test with all fields
    workzone = Workzone(
        workZoneLabel="TEST_ZONE",
        workZoneName="Test Zone Name",
        status="active",
        travelArea="sunrise_enterprise",
        keys=["KEY1", "KEY2"],
        shapes=["12345", "67890"],
        organization="ORG_LABEL",
    )
    assert workzone.workZoneLabel == "TEST_ZONE"
    assert workzone.shapes == ["12345", "67890"]
    assert workzone.organization == "ORG_LABEL"

    # Test with minimal fields
    minimal_workzone = Workzone(
        workZoneLabel="MINIMAL",
        workZoneName="Minimal Zone",
        status="inactive",
        travelArea="sunrise_enterprise",
    )
    assert minimal_workzone.keys is None
    assert minimal_workzone.shapes is None
    assert minimal_workzone.organization is None


@pytest.mark.uses_real_data
def test_replace_workzone_with_model(instance, faker):
    """Test that replace_workzone returns Workzone when using model parameter and status is 200"""
    # Get existing workzones using the model
    workzones = instance.metadata.get_workzones(offset=0, limit=1)

    if len(workzones.items) == 0:
        pytest.skip("No workzones available to test")

    # Get the first workzone and store original data
    original_workzone = workzones.items[0]

    # Modify the workzone
    modified_workzone = original_workzone.model_copy()
    modified_workzone.workZoneName = f"TEST_{faker.city()}"

    # Replace the workzone (without response_type to use model)
    result = instance.metadata.replace_workzone(modified_workzone)

    # Verify type validation if we got a 200 response (some APIs return 204)
    if result is not None:
        assert isinstance(result, Workzone)
        assert hasattr(result, "workZoneLabel")
        assert hasattr(result, "workZoneName")

    # Restore original workzone
    instance.metadata.replace_workzone(original_workzone)
