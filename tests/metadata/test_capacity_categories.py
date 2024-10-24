from ofsc.models import CapacityCategory, CapacityCategoryListResponse


def test_get_capacity_categories_model_no_parameters(instance, pp, demo_data):
    capacity_categories = demo_data.get("metadata").get("expected_capacity_categories")
    metadata_response = instance.metadata.get_capacity_categories()
    assert isinstance(
        metadata_response, CapacityCategoryListResponse
    ), f"Expected a CapacityCategoryListResponse received {type(metadata_response)}"
    assert len(metadata_response.items) == len(
        capacity_categories.keys()
    ), f"Expected {len(capacity_categories.keys())} received {metadata_response.totalResults}"
    assert metadata_response.hasMore is False
    assert metadata_response.totalResults == len(capacity_categories.keys())
    for category in metadata_response.items:
        assert isinstance(category, CapacityCategory)
        assert category.label in capacity_categories.keys()


def test_get_capacity_category(instance, pp, demo_data):
    capacity_categories = demo_data.get("metadata").get("expected_capacity_categories")
    for category in capacity_categories.keys():
        metadata_response = instance.metadata.get_capacity_category(category)
        assert isinstance(
            metadata_response, CapacityCategory
        ), f"Expected a CapacityCategory received {type(metadata_response)}"
        assert metadata_response.label == category
        assert metadata_response.name == capacity_categories[category].get("name")
