from ofsc.common import FULL_RESPONSE


def test_get_resource_types(instance, demo_data):
    metadata_response = instance.metadata.get_resource_types(
        response_type=FULL_RESPONSE
    )
    response = metadata_response.json()
    assert response["totalResults"] is not None
    assert response["totalResults"] >= demo_data.get("metadata").get(
        "expected_resource_types"
    )
