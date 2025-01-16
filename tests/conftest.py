import logging
import os
import pprint
from collections import ChainMap
from datetime import datetime, timedelta
from http.client import HTTPConnection  # py3
from pathlib import Path

import jwt
import pytest
from dotenv import load_dotenv

from ofsc import FULL_RESPONSE, OFSC


@pytest.fixture(scope="module")
def instance() -> OFSC:
    # load .env file
    load_dotenv()
    # todo add credentials to test run
    instance = OFSC(
        clientID=os.environ.get("OFSC_CLIENT_ID"),
        secret=os.environ.get("OFSC_CLIENT_SECRET"),
        companyName=os.environ.get("OFSC_COMPANY"),
        root=os.environ.get("OFSC_ROOT"),
    )
    return instance


@pytest.fixture(scope="module")
def assertion() -> str:
    payload = {}
    payload["sub"] = "admin"
    payload["iss"] = (
        "/C=US/ST=Florida/L=Miami/O=MyOrg/CN=JohnSmith/emailAddress=test@example.com"
    )
    payload["iat"] = datetime.now()
    payload["exp"] = datetime.now() + timedelta(minutes=6000)
    payload["aud"] = (
        f'ofsc:{os.environ.get("OFSC_COMPANY")}:{os.environ.get("OFSC_CLIENT_ID")}'
    )
    payload["scope"] = "/REST"
    key = Path("tests/keys/ofsc.key").read_text()
    return jwt.encode(payload, key, algorithm="RS256")


@pytest.fixture(scope="module")
def instance_with_token():
    # load .env file
    load_dotenv()
    # todo add credentials to test run
    instance = OFSC(
        clientID=os.environ.get("OFSC_CLIENT_ID"),
        secret=os.environ.get("OFSC_CLIENT_SECRET"),
        companyName=os.environ.get("OFSC_COMPANY"),
        root=os.environ.get("OFSC_ROOT"),
        useToken=True,
    )
    return instance


@pytest.fixture(scope="module")
def clear_subscriptions(instance):
    response = instance.core.get_subscriptions(response_type=FULL_RESPONSE)
    if response.status_code == 200 and response.json()["totalResults"] > 0:
        for subscription in response.json()["items"]:
            logging.info(subscription)
            instance.core.delete_subscription(subscription["subscriptionId"])
    yield
    response = instance.core.get_subscriptions(response_type=FULL_RESPONSE)
    if response.status_code == 200 and response.json()["totalResults"] > 0:
        for subscription in response.json()["items"]:
            instance.core.delete_subscription(subscription["subscriptionId"])


@pytest.fixture
def current_date():
    return os.environ.get("OFSC_TEST_DATE")


@pytest.fixture
def pp():
    pp = pprint.PrettyPrinter(indent=4)
    return pp


@pytest.fixture
def request_logging():
    log = logging.getLogger("urllib3")
    log.setLevel(logging.DEBUG)

    # logging from urllib3 to console
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    log.addHandler(ch)

    # print statements from `http.client.HTTPConnection` to console/stdout
    HTTPConnection.debuglevel = 1


@pytest.fixture
def demo_data():
    # TODO: find a better way to change based on demo date
    demo_data = {
        "23B Service Update 1": {
            "get_all_activities": {
                "bucket_id": "CAUSA",
                "expected_id": 3960470,
                "expected_items": 758,
                "expected_postalcode": "55001",
            }
        },
        "24A WMP 02 Demo_Services.E360.Supremo.Chapter8.ESM . 2024-03-01 22:20": {
            "get_all_activities": {
                "bucket_id": "CAUSA",
                "expected_id": 3960470,
                "expected_items": 698,
                "expected_postalcode": "55001",
            },
            "metadata": {
                "expected_workskills": 7,
                "expected_workskill_conditions": 8,
                "expected_resource_types": 10,
                "expected_properties": 463,
                "expected_activity_type_groups": 5,
                "expected_activity_types": 35,
                "expected_activity_types_customer": 25,
                "expected_capacity_areas": [
                    {
                        "label": "CAUSA",
                        "status": "active",
                        "type": "area",
                        "parentLabel": "SUNRISE",
                    },
                    {
                        "label": "FLUSA",
                        "status": "active",
                        "type": "area",
                        "parentLabel": "SUNRISE",
                    },
                    {
                        "label": "South Florida",
                        "status": "active",
                        "type": "area",
                        "parentLabel": "FLUSA",
                    },
                    {"label": "SUNRISE", "status": "active", "type": "group"},
                    {
                        "label": "routing_old",
                        "status": "inactive",
                        "type": "area",
                        "parentLabel": "FLUSA",
                    },
                ],
                "expected_capacity_categories": {
                    "EST": {"label": "EST", "name": "Estimate"},
                    "RES": {"label": "RES", "name": "Residential"},
                    "COM": {"label": "COM", "name": "Commercial"},
                },
                "expected_inventory_types": {
                    "count": 23,
                    "demo": {
                        "label": "FIT5000",
                        "status": "active",
                    },
                },
            },
            "get_file_property": {
                "activity_id": 3954799,  # Note: manual addition
            },
            "get_users": {
                "totalResults": 322,
            },
            "events": {"move_from": "FLUSA", "move_to": "CAUSA", "move_id": 4224268},
        },
    }
    # return a ChainMap of the demo_data elements, sorting them by the keys
    return ChainMap(*demo_data.values())
