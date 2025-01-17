from ofsc.common import FULL_RESPONSE
from ofsc.models import ResourceTypeListResponse


def test_get_resource_types_basic(instance, demo_data):
    metadata_response = instance.metadata.get_resource_types(
        response_type=FULL_RESPONSE
    )
    response = metadata_response.json()
    assert response["totalResults"] is not None
    assert response["totalResults"] >= demo_data.get("metadata").get(
        "expected_resource_types"
    )


def test_get_resource_types_obj(instance):
    response = instance.metadata.get_resource_types()
    assert isinstance(response, ResourceTypeListResponse)
    assert len(response.items) > 0
