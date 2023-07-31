import os
import sys
import unittest

sys.path.append(os.path.abspath("."))
import argparse
import json
import logging
import pprint
from datetime import date
from datetime import datetime as dt
from datetime import timedelta

from ofsc import FULL_RESPONSE, JSON_RESPONSE, OFSC


class ofscActivitiesTest(unittest.TestCase):
    def setUp(self):
        self.logger = logging.getLogger()
        self.pp = pprint.PrettyPrinter(indent=4)
        self.logger.setLevel(logging.DEBUG)
        # todo add credentials to test run
        logging.warning("Here {}".format(os.environ.get("OFSC_CLIENT_ID")))
        self.instance = OFSC(
            clientID=os.environ.get("OFSC_CLIENT_ID"),
            secret=os.environ.get("OFSC_CLIENT_SECRET"),
            companyName=os.environ.get("OFSC_COMPANY"),
        )
        response = self.instance.get_activity(3954794, response_type=JSON_RESPONSE)
        self.assertIsNotNone(response["date"])
        self.date = response["date"]

    # Test A.01 Get Activity Info (activity exists)
    def test_A01_get_activity(self):
        self.logger.info("...101: Get Activity Info (activity does exist)")
        raw_response = self.instance.get_activity(3951935)
        response = json.loads(raw_response)
        self.logger.debug(response)
        self.assertEqual(response["customerNumber"], "019895700")

    # Test A.02 Get Activity Info (activity does not exist)
    def test_A02_get_activity(self):
        instance = self.instance
        logger = self.logger
        logger.info("...102: Get Activity Info (activity does not exist)")
        raw_response = instance.get_activity(99999)
        response = json.loads(raw_response)

        logger.debug(response)
        self.assertEqual(response["status"], "404")

    # Test A.04 Move activity (between buckets, no error)
    def test_A04_move_activity_between_buckets_no_error(self):
        instance = self.instance
        logger = self.logger

        # Do a get resource to verify that the activity is in the right place
        response = instance.get_activity(4224010, response_type=FULL_RESPONSE)
        logger.debug(response.json())
        self.assertEqual(response.status_code, 200)
        original_resource = response.json()["resourceId"]

        logger.info("...104: Move activity (activity exists)")
        data = {"setResource": {"resourceId": "FLUSA"}}
        response = instance.move_activity(
            4224010, json.dumps(data), response_type=FULL_RESPONSE
        )
        self.assertEqual(response.status_code, 204)

        # Do a get resource to verify that the activity is in the right place
        response = instance.get_activity(4224010, response_type=FULL_RESPONSE)
        logger.debug(response.json())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["resourceId"], "FLUSA")

        # Return it to the previous place
        data["setResource"]["resourceId"] = original_resource
        response = instance.move_activity(
            4224010, json.dumps(data), response_type=FULL_RESPONSE
        )
        self.assertEqual(response.status_code, 204)


if __name__ == "__main__":
    unittest.main()
