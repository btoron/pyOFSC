import unittest


import sys, os
sys.path.append(os.path.abspath('.'))
from ofsc import OFSC, FULL_RESPONSE
import logging
import json
import argparse


import pprint


class ofscTest(unittest.TestCase):

    def setUp(self):
        self.logger = logging.getLogger()
        self.pp = pprint.PrettyPrinter(indent=4)
        self.logger.setLevel(logging.DEBUG)
        #todo add credentials to test run
        logging.warning("Here {}".format(os.environ.get('OFSC_CLIENT_ID')))
        self.instance = OFSC(clientID=os.environ.get('OFSC_CLIENT_ID'), secret=os.environ.get('OFSC_CLIENT_SECRET'), companyName=os.environ.get('OFSC_COMPANY'))
        self.date = os.environ.get('OFSC_TEST_DATE')

    # Test R.0.1
    def test_R01_get_resource_route_nofields(self):
        instance = self.instance
        logger = self.logger
        raw_response = instance.get_resource_route(33001, date=self.date, response_type=FULL_RESPONSE)
        logging.debug(self.pp.pformat(raw_response.json()))
        response = raw_response.json()
        self.assertEqual(response['totalResults'], 13)

    def test_R02_get_resource_route_twofields(self):
        instance = self.instance
        logger = self.logger
        raw_response = instance.get_resource_route(33001, date=self.date, activityFields="activityId,activityType")
        response = json.loads(raw_response)
        #print(response)
        self.assertEqual(response['totalResults'], 13)

    def test_R03_get_resource_descendants_noexpand(self):
        instance = self.instance
        logger = self.logger
        raw_response = instance.get_resource_descendants("FLUSA")
        response = json.loads(raw_response)
        #print(response)
        self.assertEqual(response['totalResults'], 37)

    def test_R04_get_resource_descendants_expand(self):
        instance = self.instance
        logger = self.logger
        raw_response = instance.get_resource_descendants("FLUSA", workSchedules=True, workZones=True, workSkills=True)
        response = json.loads(raw_response)
        #print(response)
        self.assertEqual(response['totalResults'], 37)

    def test_R05_get_resource_descendants_noexpand_fields(self):
        instance = self.instance
        logger = self.logger
        raw_response = instance.get_resource_descendants("FLUSA", resourceFields="resourceId,phone", response_type=FULL_RESPONSE)
        # logging.debug(self.pp.pformat(raw_response.json()))
        response = raw_response.json()
        logger.info(self.pp.pformat(response))
        self.assertEqual(response['totalResults'], 37)

    def test_R07_create_resource(self):
        self.logger.info("...R.07  Create Resource (not existent)")
        instance = self.instance
        logger = self.logger
        new_data = {
            "parentResourceId": "SUNRISE",
            "resourceType": "BK",
            "name" : "Test Name",
            "language": "en",
            "timeZone": "Arizona"
        }
        raw_response = instance.create_resource(resourceId="test_resource", data=json.dumps(new_data), response_type=FULL_RESPONSE)
        logging.debug(self.pp.pformat(raw_response.json()))
        response = raw_response.json()
        logger.info(self.pp.pformat(response))
        self.assertEqual(raw_response.status_code, 201)
        self.assertIsNotNone(response['externalId'])
        self.assertEqual(response['name'], 'Test Name')
        
if __name__ == '__main__':
    unittest.main()
