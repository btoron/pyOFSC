import pytest

from ofsc.models import ActivityType, ActivityTypeListResponse


def test_get_activity_types(instance):
    """Test getting list of activity types"""
    response = instance.metadata.get_activity_types()
    assert isinstance(response, ActivityTypeListResponse)
    assert response.items is not None
    if len(response.items) > 0:
        assert isinstance(response.items[0], ActivityType)


def test_get_activity_type(instance):
    """Test getting a single activity type"""
    # First get list to find a valid label
    response = instance.metadata.get_activity_types()
    if len(response.items) == 0:
        pytest.skip("No activity types available to test with")

    # Get first activity type's label
    label = response.items[0].label

    # Test getting single activity type
    activity_type = instance.metadata.get_activity_type(label)
    assert isinstance(activity_type, ActivityType)
    assert activity_type.label == label
    assert activity_type.name is not None
    assert isinstance(activity_type.active, bool)
    assert isinstance(activity_type.defaultDuration, int)


def test_get_activity_type_invalid_label(instance):
    """Test getting an activity type with invalid label"""
    with pytest.raises(Exception):  # Replace with specific exception if known
        instance.metadata.get_activity_type("invalid_label_123456789")
