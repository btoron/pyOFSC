import logging

import requests

from ofsc.common import FULL_RESPONSE, JSON_RESPONSE, TEXT_RESPONSE


def test_wrapper(instance):
    logging.info("...301: Testing wrapper")
    raw_response = instance.core.get_subscriptions(response_type=FULL_RESPONSE)
    assert isinstance(raw_response, requests.Response)
    assert raw_response.status_code == 200
    response = raw_response.json()
    assert "totalResults" in response.keys()
    json_response = instance.core.get_subscriptions(response_type=JSON_RESPONSE)
    assert isinstance(json_response, dict)
    assert "totalResults" in json_response.keys()
    text_response = instance.core.get_subscriptions(response_type=TEXT_RESPONSE)
    assert isinstance(text_response, str)
    default_response = instance.core.get_subscriptions()
    assert isinstance(default_response, dict)
