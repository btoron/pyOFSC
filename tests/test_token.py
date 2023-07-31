import logging

from ofsc.common import FULL_RESPONSE


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
