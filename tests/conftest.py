import logging
import os
import pprint
from http.client import HTTPConnection  # py3

import pytest
import requests
from faker import Faker

from ofsc import OFSC


@pytest.fixture(scope="module")
def instance():
    # todo add credentials to test run
    instance = OFSC(
        clientID=os.environ.get("OFSC_CLIENT_ID"),
        secret=os.environ.get("OFSC_CLIENT_SECRET"),
        companyName=os.environ.get("OFSC_COMPANY"),
        root=os.environ.get("OFSC_ROOT"),
    )
    return instance


@pytest.fixture(scope="module")
def instance_with_token():
    # todo add credentials to test run
    instance = OFSC(
        clientID=os.environ.get("OFSC_CLIENT_ID"),
        secret=os.environ.get("OFSC_CLIENT_SECRET"),
        companyName=os.environ.get("OFSC_COMPANY"),
        root=os.environ.get("OFSC_ROOT"),
        useToken=True,
    )
    return instance


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
            },
            "get_file_property": {
                "activity_id": 3954799,  # Note: manual addition
            },
            "get_users": {
                "totalResults": 322,
            },
        },
    }
    return demo_data[
        "24A WMP 02 Demo_Services.E360.Supremo.Chapter8.ESM . 2024-03-01 22:20"
    ]
