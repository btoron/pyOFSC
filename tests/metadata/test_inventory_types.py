import pytest

from ofsc.common import OBJ_RESPONSE
from ofsc.models import InventoryType, InventoryTypeListResponse


@pytest.mark.uses_real_data
def test_inventory_types_model(instance):
    instance.core.config.auto_model = True
    metadata_response = instance.metadata.get_inventory_types(
        response_type=OBJ_RESPONSE
    )
    assert isinstance(metadata_response, InventoryTypeListResponse), (
        f"Response is {type(metadata_response)}"
    )
    for item in metadata_response.items:
        assert isinstance(item, InventoryType)


@pytest.mark.uses_real_data
def test_inventory_types_demo(instance, demo_data):
    metadata_response = instance.metadata.get_inventory_types(
        response_type=OBJ_RESPONSE
    )
    assert metadata_response.items, "No inventory types found"
    assert metadata_response.totalResults > 0, "No inventory types found"
    assert len(metadata_response.items) >= demo_data.get("metadata").get(
        "expected_inventory_types"
    ).get("count"), (
        f"Expected {demo_data.get('metadata').get('expected_inventory_types').get('count')} inventory types, got {len(metadata_response.items)}"
    )


@pytest.mark.uses_real_data
def test_inventory_types_create_replace(instance, request_logging):
    metadata_response = instance.metadata.get_inventory_types(
        response_type=OBJ_RESPONSE
    )
    assert metadata_response.items, "No inventory types available"
    label = metadata_response.items[0].label

    inv_type = instance.metadata.get_inventory_type(label, response_type=OBJ_RESPONSE)
    assert isinstance(inv_type, InventoryType)
    assert inv_type.label == label
