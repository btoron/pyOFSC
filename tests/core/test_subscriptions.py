import json
import logging
import time

from ofsc.common import FULL_RESPONSE


def test_get_subscriptions(instance):
    raw_response = instance.core.get_subscriptions(response_type=FULL_RESPONSE)
    assert raw_response.status_code == 200
    response = raw_response.json()
    assert "totalResults" in response.keys()


def test_get_subscriptions_with_token(instance_with_token):
    raw_response = instance_with_token.core.get_subscriptions(
        response_type=FULL_RESPONSE
    )
    assert raw_response.status_code == 200
    response = raw_response.json()
    assert "totalResults" in response.keys()


def test_create_delete_subscription(instance):
    data = {"events": ["activityMoved"], "title": "Simple Subscription"}
    raw_response = instance.core.create_subscription(
        json.dumps(data), response_type=FULL_RESPONSE
    )
    assert raw_response.status_code == 200
    response = raw_response.json()
    assert "subscriptionId" in response.keys()
    id = response["subscriptionId"]

    raw_response = instance.core.get_subscription_details(
        id, response_type=FULL_RESPONSE
    )
    assert raw_response.status_code == 200
    response = raw_response.json()
    assert "subscriptionId" in response.keys()
    assert response["subscriptionId"] == id
    assert response["events"] == data["events"]

    response = instance.core.delete_subscription(id, response_type=FULL_RESPONSE)
    assert response.status_code == 204


def test_get_events(instance, pp, demo_data, clear_subscriptions):
    move_data = demo_data.get("events")

    # Creating subscription
    data = {"events": ["activityMoved"], "title": "Simple Subscription"}
    raw_response = instance.core.create_subscription(
        json.dumps(data), response_type=FULL_RESPONSE
    )
    assert raw_response.status_code == 200
    response = raw_response.json()
    assert "subscriptionId" in response.keys()
    id = response["subscriptionId"]

    # Get creation time
    params = {"subscriptionId": id}
    raw_response = instance.core.get_subscription_details(
        id, response_type=FULL_RESPONSE
    )
    response = raw_response.json()
    assert "subscriptionId" in response.keys()
    assert response["subscriptionId"] == id
    created_time = response["createdTime"]
    logging.info(response)

    # Moving activity
    data = {"setResource": {"resourceId": move_data["move_to"]}}
    raw_response = instance.core.move_activity(
        move_data["move_id"], json.dumps(data), response_type=FULL_RESPONSE
    )
    assert raw_response.status_code == 204, raw_response.json()

    params = {
        "subscriptionId": id,
        "since": created_time,
    }
    current_page = ""
    raw_response = instance.core.get_events(params)
    response = json.loads(raw_response)
    assert response["found"]
    next_page = response["nextPage"]
    events = []
    time.sleep(3)
    while next_page != current_page:
        logging.info(f"Current page: {current_page}, Next page: {next_page}")
        current_page = next_page
        params2 = {"subscriptionId": id, "page": next_page}
        raw_response = instance.core.get_events(params2, response_type=FULL_RESPONSE)
        response = raw_response.json()
        if response["items"]:
            events.extend(response["items"])
        next_page = response["nextPage"]
        logging.info(
            f"Current page: {current_page}, Next page: {next_page}, {response}"
        )
    assert len(events) >= 1
    for item in events:
        if item["eventType"] == "activityMoved":
            assert item["activityDetails"]["activityId"] == move_data["move_id"]

    # Moving activity back
    data = {"setResource": {"resourceId": move_data["move_from"]}}
    raw_response = instance.core.move_activity(
        move_data["move_id"], json.dumps(data), response_type=FULL_RESPONSE
    )
    assert raw_response.status_code == 204, raw_response.json()

    # Deleting subscription
    response = instance.core.delete_subscription(id, response_type=FULL_RESPONSE)
    assert response.status_code == 204
