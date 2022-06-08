import os
import sys
import unittest

sys.path.append(os.path.abspath("."))
import argparse
import json
import logging
import pprint

from ofsc import FULL_RESPONSE, OFSC


class ofscTest(unittest.TestCase):
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
        self.date = os.environ.get("OFSC_TEST_DATE")

    # Test M.P.01 Get Properties
    def test_get_properties(self):
        self.logger.info("...M.P.01 Get Properties")
        instance = self.instance
        logger = self.logger
        raw_response = instance.get_properties(response_type=FULL_RESPONSE)
        logging.debug(self.pp.pformat(raw_response.json()))
        response = raw_response.json()
        logger.debug(self.pp.pformat(response))
        self.assertIsNotNone(response["totalResults"])
        self.assertEqual(response["totalResults"], 453)  # 22.B
        self.assertEqual(response["items"][0]["label"], "ITEM_NUMBER")

    # Test C.P.10 Get File Property 01
    def test_get_file_property_01(self):
        self.logger.info("...C.P.01 Get File Property")
        instance = self.instance
        logger = self.logger
        raw_response = instance.get_file_property(
            activityId=3954865,
            label="csign",
            mediaType="*/*",
            response_type=FULL_RESPONSE,
        )
        logging.debug(self.pp.pformat(raw_response.json()))
        response = raw_response.json()
        logger.debug(self.pp.pformat(response))
        self.assertIsNotNone(response["mediaType"])
        self.assertEqual(response["mediaType"], "image/png")
        self.assertEqual(response["name"], "signature.png")

    # Test C.P.10 Get File Property 02
    def test_get_file_property_02(self):
        self.logger.info("...C.P.02 Get File Property content")
        instance = self.instance
        logger = self.logger
        metadata_response = instance.get_file_property(
            activityId=3954865,
            label="csign",
            mediaType="*/*",
            response_type=FULL_RESPONSE,
        )
        logging.debug(self.pp.pformat(metadata_response.json()))
        response = metadata_response.json()
        raw_response = instance.get_file_property(
            activityId=3954865,
            label="csign",
            mediaType="image/png",
            response_type=FULL_RESPONSE,
        )
        with open(os.path.join(os.getcwd(), response["name"]), "wb") as fd:
            fd.write(raw_response.content)
        self.assertEqual(response["name"], "signature.png")
        # TODO: Assert the size of the file


if __name__ == "__main__":
    unittest.main()
