import logging

from ofsc.common import FULL_RESPONSE
from ofsc.models import OFSOAuthRequest


def test_get_token(instance_with_token):
    logging.info("...401: Get token")
    raw_response = instance_with_token.oauth2.get_token(response_type=FULL_RESPONSE)
    print(raw_response)
    assert raw_response.status_code == 200
    response = raw_response.json()
    assert "access_token" in response.keys()
    assert response["token_type"] == "bearer"
    assert response["expires_in"] == 3600


def test_cache_token(instance_with_token):
    logging.info("...402: Verify token cache")
    raw_response = instance_with_token.oauth2.get_token(response_type=FULL_RESPONSE)
    assert raw_response.status_code == 200
    response = raw_response.json()
    assert "access_token" in response.keys()
    first_token = response["access_token"]
    raw_response = instance_with_token.oauth2.get_token(response_type=FULL_RESPONSE)
    assert raw_response.status_code == 200
    response = raw_response.json()
    assert "access_token" in response.keys()
    assert first_token == response["access_token"]


def test_token_assertion(instance, assertion, request_logging):
    logging.info("...403: Get token with assertion")
    request = OFSOAuthRequest(
        assertion=assertion, grant_type="urn:ietf:params:oauth:grant-type:jwt-bearer"
    )
    raw_response = instance.oauth2.get_token(
        params=request, response_type=FULL_RESPONSE
    )
    assert raw_response.status_code == 200, raw_response.json()
    response = raw_response.json()
    assert "access_token" in response.keys()
    assert response["token_type"] == "bearer"
    assert response["expires_in"] == 3600
    assert False
