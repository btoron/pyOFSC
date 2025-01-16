from ofsc.common import OBJ_RESPONSE
from ofsc.models import InventoryType, InventoryTypeListResponse


def test_inventory_types_model(instance):
    instance.core.config.auto_model = True
    metadata_response = instance.metadata.get_inventory_types(
        response_type=OBJ_RESPONSE
    )
    assert isinstance(
        metadata_response, InventoryTypeListResponse
    ), f"Response is {type(metadata_response)}"
    for item in metadata_response.items:
        assert isinstance(item, InventoryType)


def test_inventory_types_demo(instance, demo_data):
    metadata_response = instance.metadata.get_inventory_types(
        response_type=OBJ_RESPONSE
    )
    assert metadata_response.items, "No inventory types found"
    assert metadata_response.totalResults > 0, "No inventory types found"
    assert len(metadata_response.items) >= demo_data.get("metadata").get(
        "expected_inventory_types"
    ).get(
        "count"
    ), f"Expected {demo_data.get('metadata').get('expected_inventory_types').get('count')} inventory types, got {len(metadata_response.items)}"


def test_inventory_types_create_replace(instance, demo_data, request_logging):
    data = demo_data.get("metadata").get("expected_inventory_types").get("demo")
    inv_type = instance.metadata.get_inventory_type(
        data.get("label"), response_type=OBJ_RESPONSE
    )
    assert isinstance(inv_type, InventoryType)
    assert inv_type.label == data.get("label")
