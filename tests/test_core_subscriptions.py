import json
import logging

from ofsc.common import FULL_RESPONSE


def test_get_subscriptions(instance):
    logging.info("...301: Get Subscriptions")
    raw_response = instance.core.get_subscriptions(response_type=FULL_RESPONSE)
    assert raw_response.status_code == 200
    response = raw_response.json()
    assert "totalResults" in response.keys()


def test_get_subscriptions_with_token(instance_with_token):
    logging.info("...302: Get Subscriptions using token")
    raw_response = instance_with_token.core.get_subscriptions(
        response_type=FULL_RESPONSE
    )
    assert raw_response.status_code == 200
    response = raw_response.json()
    assert "totalResults" in response.keys()


def test_create_delete_subscription(instance):
    data = {"events": ["activityMoved"], "title": "Simple Subscription"}
    logging.info("...303: Create Subscription")
    raw_response = instance.core.create_subscription(
        json.dumps(data), response_type=FULL_RESPONSE
    )
    assert raw_response.status_code == 200
    response = raw_response.json()
    assert "subscriptionId" in response.keys()
    id = response["subscriptionId"]

    logging.info("...304: Subscription details")
    raw_response = instance.core.get_subscription_details(
        id, response_type=FULL_RESPONSE
    )
    assert raw_response.status_code == 200
    response = raw_response.json()
    assert "subscriptionId" in response.keys()
    assert response["subscriptionId"] == id
    assert response["events"] == data["events"]

    logging.info("...305: Delete Subscription")
    response = instance.core.delete_subscription(id, response_type=FULL_RESPONSE)
    assert response.status_code == 204
