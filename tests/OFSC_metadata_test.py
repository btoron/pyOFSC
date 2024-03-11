import os
import sys
import unittest

from ofsc.models import SharingEnum, Workskill

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


if __name__ == "__main__":
    unittest.main()
