import json
import logging
from pathlib import Path

import pytest
from requests import Response

from ofsc import OFSC
from ofsc.common import FULL_RESPONSE, JSON_RESPONSE, TEXT_RESPONSE


@pytest.mark.debug
def test_get_token(instance, request_logging):
    logging.info("...302: Get Subscriptions using token")
    raw_response = instance.oauth2.get_token(response_type=FULL_RESPONSE)
    print(raw_response.content)
    assert raw_response.status_code == 200
    response = raw_response.json()
    assert "access_token" in response.keys()
    assert response["token_type"] == "bearer"
    assert response["expires_in"] == "3600"
