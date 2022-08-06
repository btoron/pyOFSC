import logging
import os

import pytest
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
