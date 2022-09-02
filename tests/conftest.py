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
    logging.warning("Here {}".format(os.environ.get("OFSC_CLIENT_ID")))
    instance = OFSC(
        clientID=os.environ.get("OFSC_CLIENT_ID"),
        secret=os.environ.get("OFSC_CLIENT_SECRET"),
        companyName=os.environ.get("OFSC_COMPANY"),
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
