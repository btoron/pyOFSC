from ofsc.common import FULL_RESPONSE
from ofsc.models import Organization, OrganizationListResponse


def test_get_organizations_basic(instance):
    response = instance.metadata.get_organizations(response_type=FULL_RESPONSE)
    assert response.status_code == 200
    response = response.json()
    assert response["totalResults"]
    assert response["items"] is not None
    assert len(response["items"]) > 0
    for item in response["items"]:
        assert isinstance(item, dict)
        assert "label" in item
        assert "name" in item
        assert "translations" in item
        assert "type" in item


def test_get_organization_basic(instance):
    response = instance.metadata.get_organization(
        "default", response_type=FULL_RESPONSE
    )
    assert response.status_code == 200
    response = response.json()
    assert response["label"] == "default"


def test_get_organization_obj(instance):
    response = instance.metadata.get_organization("default")
    assert isinstance(response, Organization)
    assert response.label == "default"
    assert response.translations is not None
    assert response.type is not None


def test_get_organization_list_obj(instance):
    response = instance.metadata.get_organizations()
    assert isinstance(response, OrganizationListResponse)
    assert response.items is not None
    assert len(response.items) > 0
    for item in response.items:
        assert isinstance(item, Organization)
