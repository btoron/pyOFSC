from ofsc import OFSC
from ofsc.common import FULL_RESPONSE
from ofsc.models import Application, ApplicationListResponse


def test_get_applications_basic(instance: OFSC):
    raw_response = instance.metadata.get_applications(response_type=FULL_RESPONSE)
    assert raw_response is not None
    assert raw_response.status_code == 200
    response = raw_response.json()
    assert response["items"] is not None
    assert (
        len(response["items"]) > 0
    ), f"Received {[i['label'] for i in response['items']]}"
    applications = {app["label"]: app for app in response["items"]}
    assert instance._config.clientID in applications.keys()


def test_get_applications_obj(instance: OFSC):
    response = instance.metadata.get_applications()
    assert response is not None
    assert isinstance(response, ApplicationListResponse)
    assert len(response.items) > 0
    applications = {app.label: app for app in response.items}
    assert instance._config.clientID in applications.keys()


def test_get_application_basic(instance: OFSC):
    raw_response = instance.metadata.get_application(
        instance._config.clientID, response_type=FULL_RESPONSE
    )
    assert raw_response is not None
    assert raw_response.status_code == 200
    response = raw_response.json()
    assert response["label"] == instance._config.clientID
    application_obj = Application.model_validate(response)
    assert application_obj is not None


def test_get_application_obj(instance: OFSC):
    response = instance.metadata.get_application(instance._config.clientID)
    assert isinstance(response, Application)
    assert response.label == instance._config.clientID


def test_get_application_api_accesses_basic(instance: OFSC):
    raw_response = instance.metadata.get_application_api_accesses(
        instance._config.clientID, response_type=FULL_RESPONSE
    )
    assert raw_response is not None
    assert raw_response.status_code == 200
    response = raw_response.json()
    assert response["items"] is not None
    assert len(response["items"]) > 0
    accesses = {access["label"]: access for access in response["items"]}
    assert accesses is not None


def test_get_application_api_access_basic(instance: OFSC):
    raw_response = instance.metadata.get_application_api_access(
        instance._config.clientID, "metadataAPI", response_type=FULL_RESPONSE
    )
    assert raw_response is not None
    assert raw_response.status_code == 200
    response = raw_response.json()
    assert response["label"] == "metadataAPI"
