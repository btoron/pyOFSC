import logging

from ofsc.common import FULL_RESPONSE


def test_get_subscriptions(instance):
    logging.info("...301: Get Subscriptions")
    raw_response = instance.core.get_subscriptions(response_type=FULL_RESPONSE)
    assert raw_response.status_code == 200
    response = raw_response.json()
    assert "totalResults" in response.keys()
    assert response["totalResults"] == 0


def test_get_subscriptions_with_token(instance_with_token):
    logging.info("...302: Get Subscriptions using token")
    raw_response = instance_with_token.core.get_subscriptions(
        response_type=FULL_RESPONSE
    )
    assert raw_response.status_code == 200
    response = raw_response.json()
    assert "totalResults" in response.keys()
    assert response["totalResults"] == 0
