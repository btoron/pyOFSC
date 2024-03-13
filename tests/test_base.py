import logging

import requests

from ofsc.common import FULL_RESPONSE, JSON_RESPONSE, TEXT_RESPONSE
from ofsc.exceptions import OFSAPIException
from ofsc.models import (
    ActivityTypeGroup,
    ActivityTypeGroupList,
    ActivityTypeGroupListResponse,
)


def test_wrapper_generic(instance):
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


def test_wrapper_with_error(instance, pp):
    instance.core.config.auto_raise = False
    raw_response = instance.core.get_activity("123456", response_type=FULL_RESPONSE)
    assert isinstance(raw_response, requests.Response)
    assert raw_response.status_code == 404
    raw_response = instance.core.get_activity("123456", response_type=JSON_RESPONSE)
    assert isinstance(raw_response, dict)
    assert raw_response["status"] == "404"
    instance.core.config.auto_raise = True
    raw_response = instance.core.get_activity("123456", response_type=FULL_RESPONSE)
    assert isinstance(raw_response, requests.Response)
    assert raw_response.status_code == 404

    # Validate that the next line raises an exception
    try:
        instance.core.get_activity("123456", response_type=JSON_RESPONSE)
    except Exception as e:
        assert isinstance(e, OFSAPIException)
        # log exception fields
        assert e.status_code == 404


def test_wrapper_with_model_list(instance, demo_data):
    instance.core.config.auto_model = True
    raw_response = instance.metadata.get_activity_type_groups(
        response_type=FULL_RESPONSE
    )
    assert isinstance(raw_response, requests.Response)
    assert raw_response.status_code == 200

    json_response = instance.metadata.get_activity_type_groups()
    assert isinstance(json_response, ActivityTypeGroupListResponse)


def test_wrapper_with_model_single(instance):
    instance.core.config.auto_model = True
    raw_response = instance.metadata.get_activity_type_group("customer")
    assert isinstance(raw_response, ActivityTypeGroup)


def test_wrapper_without_model(instance):
    instance.auto_model = False
    raw_response = instance.metadata.get_activity_type_group("customer")
    assert isinstance(raw_response, dict)
    assert "label" in raw_response.keys()
    assert "name" in raw_response.keys()
