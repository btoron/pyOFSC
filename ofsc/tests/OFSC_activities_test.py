import unittest


import sys, os
sys.path.append(os.path.abspath('.'))
from ofsc import OFSC, FULL_RESPONSE
import logging
import json
import argparse


import pprint


class ofscActivitiesTest(unittest.TestCase):

    def setUp(self):
        self.logger = logging.getLogger()
        self.pp = pprint.PrettyPrinter(indent=4)
        self.logger.setLevel(logging.DEBUG)
        #todo add credentials to test run
        logging.warning("Here {}".format(os.environ.get('OFSC_CLIENT_ID')))
        self.instance = OFSC(clientID=os.environ.get('OFSC_CLIENT_ID'), secret=os.environ.get('OFSC_CLIENT_SECRET'), companyName=os.environ.get('OFSC_COMPANY'))
        self.date = os.environ.get('OFSC_TEST_DATE')

    # Test A.01 Get Activity Info (activity exists)
    def test_A01_get_activity(self):
        self.logger.info("...101: Get Activity Info (activity does exist)")
        raw_response = self.instance.get_activity(3951935)
        response = json.loads(raw_response)
        self.logger.debug(response)
        self.assertEqual(response['customerNumber'],'019895700')

    # Test A.02 Get Activity Info (activity does not exist)
    def test_A02_get_activity(self):
        instance = self.instance
        logger = self.logger
        logger.info("...102: Get Activity Info (activity does not exist)")
        raw_response = instance.get_activity(99999)
        response = json.loads(raw_response)

        logger.debug(response)
        self.assertEqual(response['status'],'404') 

    # Test A.03 Search Activities (activity exists)
    def test_A03_search_activities(self):
        instance = self.instance
        logger = self.logger
        logger.info("...103: Search Activities (activity exists)")
        params = {
            "searchInField" : "customerNumber",
            "searchForValue": '019895700',
            "dateFrom": "2021-01-01",
            "dateTo" : "2099-01-01"
        }
        response = instance.search_activities(params, response_type=FULL_RESPONSE)
        logger.debug(response.json())
        self.assertEqual(response.status_code,200) 
        self.assertEqual(response.json()["totalResults"],8) 

    # Test A.04 Move activity (between buckets, no error)
    def test_A04_move_activity_between_buckets_no_error(self):
        instance = self.instance
        logger = self.logger

        # Do a get resource to verify that the activity is in the right place
        response = instance.get_activity(4224010, response_type=FULL_RESPONSE)
        logger.debug(response.json())
        self.assertEqual(response.status_code,200)
        original_resource = response.json()["resourceId"]

        logger.info("...104: Move activity (activity exists)")
        data = {
                "setResource" : {
                    "resourceId": "FLUSA"
                }
            }
        response = instance.move_activity(4224010, json.dumps(data), response_type=FULL_RESPONSE)
        self.assertEqual(response.status_code,204)

        # Do a get resource to verify that the activity is in the right place
        response = instance.get_activity(4224010, response_type=FULL_RESPONSE)
        logger.debug(response.json())
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json()["resourceId"],"FLUSA") 

        # Return it to the previous place
        data["setResource"]["resourceId"] = original_resource
        response = instance.move_activity(4224010, json.dumps(data), response_type=FULL_RESPONSE)
        self.assertEqual(response.status_code,204)

if __name__ == '__main__':
    unittest.main()
