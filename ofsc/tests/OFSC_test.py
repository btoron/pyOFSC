import unittest


import sys, os
sys.path.append(os.path.abspath('.'))
from ofsc.core import OFSC, FULL_RESPONSE
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
        self.instance = OFSC(clientID=os.environ.get('OFSC_CLIENT_ID'), secret=os.environ.get('OFSC_CLIENT_SECRET'), companyName=os.environ.get('OFSC_COMPANY'))

    # Test 1.01 Get Activity Info (activity exists)
    def test_get_activity_101(self):
        self.logger.info("...101: Get Activity Info (activity does exist)")
        raw_response = self.instance.get_activity(3951935)
        response = json.loads(raw_response)
        self.logger.debug(response)
        self.assertEqual(response['customerNumber'],'019895700')

    # Test 1.02 Get Activity Info (activity does not exist)
    def test_get_activity_102(self):
        instance = self.instance
        logger = self.logger
        logger.info("...102: Get Activity Info (activity does not exist)")
        raw_response = instance.get_activity(99999)
        response = json.loads(raw_response)

        logger.debug(response)
        self.assertEqual(response['status'],'404')

    # Test 2.01 Create subsciption (simple)
    def test_001_create_subscription(self):
        instance = self.instance
        logger = self.logger
        global created_subscription,pp
        data = {
            "events" : ["activityMoved"],
            "title"  : "Simple Subscription"
        }
        logger.info("...201: Create Subscription")
        raw_response = instance.create_subscription(json.dumps(data))
        response = json.loads(raw_response)
        logger.debug(self.pp.pformat(response))
        self.assertIsNotNone(response['subscriptionId'])
        created_subscription = response['subscriptionId']

    # Test 2.02 get subscription details
    def test_002_get_subscription_details(self):
        instance = self.instance
        logger = self.logger
        global created_subscription, created_time
        logger.info("...202: Get Subscription Details")
        raw_response = instance.get_subscription_details(created_subscription)
        response = json.loads(raw_response)
        logger.info(self.pp.pformat(response))
        self.assertEqual(response['subscriptionId'], created_subscription)
        created_time = response['createdTime']


    # Test 2.03 get subscriptions
    def test_003_get_subscriptions(self):
        instance = self.instance
        logger = self.logger
        global created_subscription
        logger.info("...203: Get Subscriptions")
        raw_response = instance.get_subscriptions()
        response = json.loads(raw_response)
        logger.info(self.pp.pformat(response))
        assert int(response['totalResults']) > 0
        found = False
        for items in response['items']:
            logger.debug(items['subscriptionId'])
            if items['subscriptionId'] == created_subscription:
                found = True
        self.assertTrue(found)

    def test_004_get_events(self):
        instance = self.instance
        logger = self.logger
        global created_subscription, pp, created_time
        params = {
            'subscriptionId' : created_subscription,
            'since' : created_time
        }
        logger.info("...210: Get Events")
        raw_response = instance.get_events(params)
        response = json.loads(raw_response)
        logger.info(self.pp.pformat(response))
        self.assertTrue(response['found'])
        nextPage = response['nextPage']
        params2 = {
            'page' : nextPage
        }
        raw_response = instance.get_events(params2)
        response = json.loads(raw_response)
        for item in response['items']:
            logger.info(self.pp.pformat(item['eventType']))
            if item['eventType'] == 'activityMoved':
                logger.info(self.pp.pformat(item))

    def test_201_get_resource_no_expand(self):
        instance = self.instance
        logger = self.logger
        raw_response = instance.get_resource(55001)
        response = json.loads(raw_response)
        self.assertEqual(response['resourceInternalId'], 5000001)

    def test_202_get_resource_expand(self):
        instance = self.instance
        logger = self.logger
        raw_response = instance.get_resource(55001, workSkills=True, workZones=True)
        response = json.loads(raw_response)
        self.assertEqual(response['resourceInternalId'], 5000001)

    def test_203_get_position_history(self):
        instance = self.instance
        logger = self.logger
        raw_response = instance.get_position_history(33001, date="2019-11-19")
        response = json.loads(raw_response)
        self.assertEqual(response['totalResults'], 222)

    def test_204_get_resource_route_nofields(self):
        instance = self.instance
        logger = self.logger
        raw_response = instance.get_resource_route(33001, date="2019-11-19")
        response = json.loads(raw_response)
        self.assertEqual(response['totalResults'], 13)

    def test_205_get_resource_route_twofields(self):
        instance = self.instance
        logger = self.logger
        raw_response = instance.get_resource_route(33001, date="2019-11-19", activityFields="activityId,activityType")
        response = json.loads(raw_response)
        #print(response)
        self.assertEqual(response['totalResults'], 13)

    def test_206_get_resource_descendants_noexpand(self):
        instance = self.instance
        logger = self.logger
        raw_response = instance.get_resource_descendants(55100)
        response = json.loads(raw_response)
        #print(response)
        self.assertEqual(response['totalResults'], 10)

    def test_207_get_resource_descendants_expand(self):
        instance = self.instance
        logger = self.logger
        raw_response = instance.get_resource_descendants(55100, workSchedules=True, workZones=True, workSkills=True)
        response = json.loads(raw_response)
        #print(response)
        self.assertEqual(response['totalResults'], 10)

    def test_208_get_resource_descendants_noexpand_fields(self):
        instance = self.instance
        logger = self.logger
        raw_response = instance.get_resource_descendants(55100, resourceFields="resourceId,phone", response_type=FULL_RESPONSE)
        # logging.debug(self.pp.pformat(raw_response.json()))
        response = raw_response.json()
        logger.info(self.pp.pformat(response))
        self.assertEqual(response['totalResults'], 10)


if __name__ == '__main__':
    unittest.main()
