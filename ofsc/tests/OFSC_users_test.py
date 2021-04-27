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

    # Test C.U.01 Get Users
    def test_get_users(self):
        self.logger.info("...C.U.01 Get Users")
        instance = self.instance
        logger = self.logger
        raw_response = instance.get_users(response_type=FULL_RESPONSE)
        logging.debug(self.pp.pformat(raw_response.json()))
        response = raw_response.json()
        logger.debug(self.pp.pformat(response))
        self.assertIsNotNone(response['totalResults'])
        self.assertEqual(response['totalResults'], 306)
        self.assertEqual(response['items'][0]['login'], 'admin')  

    def test_get_user(self):
        self.logger.info("...C.U.02 Get Specific User")
        instance = self.instance
        logger = self.logger
        raw_response = instance.get_user(login="chris", response_type=FULL_RESPONSE)
        logging.debug(self.pp.pformat(raw_response.json()))
        response = raw_response.json()
        logger.debug(self.pp.pformat(response))
        self.assertEqual(raw_response.status_code, 200)
        self.assertIsNotNone(response['login'])
        self.assertEqual(response['login'], 'chris')
        self.assertEqual(response['resourceInternalIds'][0], 3000000)   


    def test_update_user(self):
        self.logger.info("...C.U.03 Get Specific User")
        instance = self.instance
        logger = self.logger
        raw_response = instance.get_user(login="chris", response_type=FULL_RESPONSE)
        logging.debug(self.pp.pformat(raw_response.json()))
        response = raw_response.json()
        logger.info(self.pp.pformat(response))
        self.assertEqual(raw_response.status_code, 200)
        self.assertIsNotNone(response['name'])
        self.assertEqual(response['name'], 'Chris')
        new_data = {}
        new_data['name']='Changed'
        raw_response = instance.update_user(login="chris", data=json.dumps(new_data), response_type=FULL_RESPONSE)
        logging.info(self.pp.pformat(raw_response.text))
        response = raw_response.json()
        self.assertEqual(raw_response.status_code, 200)
        self.assertIsNotNone(response['name'])
        self.assertEqual(response['name'], 'Changed')
        new_data = {}
        new_data['name']='Chris'
        raw_response = instance.update_user(login="chris", data=json.dumps(new_data), response_type=FULL_RESPONSE)
        logging.info(self.pp.pformat(raw_response.text))
        response = raw_response.json()
        self.assertEqual(raw_response.status_code, 200)
        self.assertIsNotNone(response['name'])
        self.assertEqual(response['name'], 'Chris')


if __name__ == '__main__':
    unittest.main()
