"""Async test fixtures."""

import os
from datetime import date, timedelta

import pytest
from dotenv import load_dotenv

from ofsc.async_client import AsyncOFSC
from ofsc.models import Activity


@pytest.fixture
async def async_instance():
    """Create an async OFSC instance for testing."""
    load_dotenv()
    async with AsyncOFSC(
        clientID=os.environ.get("OFSC_CLIENT_ID"),
        secret=os.environ.get("OFSC_CLIENT_SECRET"),
        companyName=os.environ.get("OFSC_COMPANY"),
        root=os.environ.get("OFSC_ROOT"),
    ) as instance:
        yield instance


@pytest.fixture
async def bucket_activity_type(async_instance):
    """Get a bucket-compatible activity type label for creating test activities."""
    activity_types = await async_instance.metadata.get_activity_types()
    activity_type = next(
        (
            at.label
            for at in activity_types
            if at.features and at.features.allowCreationInBuckets
        ),
        None,
    )
    assert activity_type is not None, "No bucket-compatible activity types available"
    return activity_type


@pytest.fixture
async def workzone_activity_type(async_instance):
    """Get an activity type label that has work zone support enabled."""
    activity_types = await async_instance.metadata.get_activity_types()
    label = next(
        (
            at.label
            for at in activity_types
            if at.features and at.features.supportOfWorkZones
        ),
        None,
    )
    if label is None:
        pytest.skip("No activity types with work zone support available")
    return label


@pytest.fixture
async def workzone_postal_code(async_instance):
    """Get a postal code from a workzone that has keys defined."""
    workzones = await async_instance.metadata.get_workzones()
    for wz in workzones:
        if wz.keys:
            return wz.keys[0]
    pytest.skip("No workzones with postal code keys available")


@pytest.fixture
async def fresh_activity(async_instance, bucket_activity_type):
    """Create a temporary future-dated activity, delete after test."""
    created = await async_instance.core.create_activity(
        Activity.model_validate(
            {
                "resourceId": "CAUSA",
                "date": (date.today() + timedelta(days=90)).isoformat(),
                "activityType": bucket_activity_type,
            }
        )
    )
    yield created
    await async_instance.core.delete_activity(created.activityId)


@pytest.fixture
async def serialized_inventory_type(async_instance):
    """Get a serialized inventory type label (nonSerialized=False)."""
    inv_types = await async_instance.metadata.get_inventory_types(limit=100)
    label = next(
        (it.label for it in inv_types.items if not it.non_serialized),
        None,
    )
    if label is None:
        pytest.skip("No serialized inventory types available")
    return label


@pytest.fixture
async def non_serialized_inventory_type(async_instance):
    """Get a non-serialized inventory type label (nonSerialized=True)."""
    inv_types = await async_instance.metadata.get_inventory_types(limit=100)
    label = next(
        (it.label for it in inv_types.items if it.non_serialized),
        None,
    )
    if label is None:
        pytest.skip("No non-serialized inventory types available")
    return label


@pytest.fixture
def resource_file_property_label():
    """File-type property label configured on resources."""
    return "tech_photo"


@pytest.fixture
async def fresh_activity_pair(async_instance, bucket_activity_type):
    """Create two temporary activities for link testing, delete both after."""
    act1 = await async_instance.core.create_activity(
        Activity.model_validate(
            {
                "resourceId": "CAUSA",
                "date": (date.today() + timedelta(days=90)).isoformat(),
                "activityType": bucket_activity_type,
            }
        )
    )
    act2 = await async_instance.core.create_activity(
        Activity.model_validate(
            {
                "resourceId": "CAUSA",
                "date": (date.today() + timedelta(days=90)).isoformat(),
                "activityType": bucket_activity_type,
            }
        )
    )
    yield act1, act2
    await async_instance.core.delete_activity(act1.activityId)
    await async_instance.core.delete_activity(act2.activityId)
