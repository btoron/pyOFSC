import os
import sys
import unittest

from ofsc.ofsc_proxy import JSON_RESPONSE

sys.path.append(os.path.abspath("."))
import argparse
import json
import logging
import pprint

from ofsc import FULL_RESPONSE, OFSC


class ofscTest(unittest.TestCase):
    aid = 4224010

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

    def create_subscription(self):
        instance = self.instance
        logger = self.logger
        data = {"events": ["activityMoved"], "title": "Simple Subscription"}
        logger.info("...201: Create Subscription")
        raw_response = instance.create_subscription(
            json.dumps(data), response_type=FULL_RESPONSE
        )
        self.assertEqual(raw_response.status_code, 200)
        response = raw_response.json()
        logger.debug(self.pp.pformat(response))
        self.assertIsNotNone(response["subscriptionId"])
        return response

    def delete_subscription(self, id):
        instance = self.instance
        logger = self.logger
        logger.info("...202: Delete Subscription")
        response = instance.delete_subscription(id, response_type=FULL_RESPONSE)
        self.assertEqual(response.status_code, 204)
        return response

    def move_activity_between_buckets_no_error(self):
        instance = self.instance
        logger = self.logger

        # Do a get resource to verify that the activity is in the right place
        response = instance.get_activity(self.aid, response_type=FULL_RESPONSE)
        self.assertEqual(response.status_code, 200)
        original_resource = response.json()["resourceId"]

        logger.info("...104: Move activity (activity exists)")
        data = {"setResource": {"resourceId": "FLUSA"}}
        response = instance.move_activity(
            4224010, json.dumps(data), response_type=FULL_RESPONSE
        )
        self.assertEqual(response.status_code, 204)

        # Do a get resource to verify that the activity is in the right place
        response = instance.get_activity(self.aid, response_type=FULL_RESPONSE)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["resourceId"], "FLUSA")

        # Return it to the previous place
        data["setResource"]["resourceId"] = original_resource
        response = instance.move_activity(
            4224010, json.dumps(data), response_type=FULL_RESPONSE
        )
        self.assertEqual(response.status_code, 204)
        logger.info("...104: Move activity back")

    # Test 2.01 Create subsciption (simple)
    def test_001_create_delete_subscription(self):
        logger = self.logger
        global pp
        response = self.create_subscription()
        self.assertIsNotNone(response["subscriptionId"])
        result = self.delete_subscription(response["subscriptionId"])
        self.assertEqual(result.status_code, 204)

    # Test 2.02 get subscription details
    def test_002_get_subscription_details(self):
        instance = self.instance
        logger = self.logger

        logger.info("...202: Get Subscription Details")
        created_subscription = self.create_subscription()
        raw_response = instance.get_subscription_details(
            created_subscription["subscriptionId"], response_type=FULL_RESPONSE
        )
        response = raw_response.json()
        logger.info(self.pp.pformat(response))
        self.assertEqual(
            response["subscriptionId"], created_subscription["subscriptionId"]
        )
        self.delete_subscription(response["subscriptionId"])

    # Test 2.03 get subscriptions
    def test_003_get_subscriptions(self):
        instance = self.instance
        logger = self.logger
        global created_subscription
        logger.info("...203: Get Subscriptions")
        raw_response = instance.get_subscriptions()
        response = json.loads(raw_response)
        logger.info(self.pp.pformat(response))
        assert "totalResults" in response.keys()

    def test_004_get_events(self):

        instance = self.instance
        logger = self.logger
        global pp, created_time
        created_subscription = self.create_subscription()
        details = instance.get_subscription_details(
            created_subscription["subscriptionId"], response_type=JSON_RESPONSE
        )
        # Moving activity
        self.move_activity_between_buckets_no_error()
        params = {
            "subscriptionId": details["subscriptionId"],
            "since": details["createdTime"],
        }
        logger.info("...210: Get Events")
        current_page = ""
        raw_response = instance.get_events(params)
        response = json.loads(raw_response)
        logger.info(self.pp.pformat(response))
        self.assertTrue(response["found"])
        next_page = response["nextPage"]
        events = []
        while next_page != current_page:
            current_page = next_page
            params2 = {"subscriptionId": details["subscriptionId"], "page": next_page}
            raw_response = instance.get_events(params2, response_type=FULL_RESPONSE)
            response = raw_response.json()
            if response["items"]:
                events.extend(response["items"])
            next_page = response["nextPage"]
        self.assertGreaterEqual(len(events), 2)
        for item in events:
            logger.info(self.pp.pformat(item))
            if item["eventType"] == "activityMoved":
                self.assertEqual(item["activityDetails"]["activityId"], self.aid)
        self.delete_subscription(details["subscriptionId"])

    def test_201_get_resource_no_expand(self):
        instance = self.instance
        logger = self.logger
        raw_response = instance.get_resource(55001)
        response = json.loads(raw_response)
        self.assertEqual(response["resourceInternalId"], 5000001)

    def test_202_get_resource_expand(self):
        instance = self.instance
        logger = self.logger
        raw_response = instance.get_resource(55001, workSkills=True, workZones=True)
        response = json.loads(raw_response)
        self.assertEqual(response["resourceInternalId"], 5000001)

    def test_203_get_position_history(self):
        instance = self.instance
        logger = self.logger
        raw_response = instance.get_position_history(33001, date=self.date)
        response = json.loads(raw_response)
        self.assertIsNotNone(response["totalResults"])
        self.assertTrue(response["totalResults"] > 200)

    # Capacity tests
    def test_301_get_capacity_areas_simple(self):
        instance = self.instance
        logger = self.logger
        raw_response = instance.get_capacity_areas(response_type=FULL_RESPONSE)
        logging.debug(self.pp.pformat(raw_response.json()))
        response = raw_response.json()
        logger.info(self.pp.pformat(response))
        self.assertIsNotNone(response["items"])
        self.assertEqual(len(response["items"]), 2)
        self.assertEqual(response["items"][0]["label"], "CAUSA")

    def test_302_get_capacity_area(self):
        instance = self.instance
        logger = self.logger
        raw_response = instance.get_capacity_area("FLUSA", response_type=FULL_RESPONSE)
        logging.debug(self.pp.pformat(raw_response.json()))
        response = raw_response.json()
        logger.info(self.pp.pformat(response))
        self.assertIsNotNone(response["label"])
        self.assertEqual(response["label"], "FLUSA")
        self.assertIsNotNone(response["configuration"])
        self.assertIsNotNone(response["parentLabel"])
        self.assertEqual(response["parentLabel"], "SUNRISE")

    def test_311_get_activity_type_groups(self):
        instance = self.instance
        logger = self.logger
        raw_response = instance.get_activity_type_groups(response_type=FULL_RESPONSE)
        logging.debug(self.pp.pformat(raw_response.json()))
        response = raw_response.json()
        logger.info(self.pp.pformat(response))
        self.assertIsNotNone(response["items"])
        self.assertEqual(len(response["items"]), 5)
        self.assertEqual(response["totalResults"], 5)
        self.assertEqual(response["items"][0]["label"], "customer")

    def test_312_get_activity_type_group(self):
        instance = self.instance
        logger = self.logger
        raw_response = instance.get_activity_type_group(
            "customer", response_type=FULL_RESPONSE
        )
        logging.debug(self.pp.pformat(raw_response.json()))
        response = raw_response.json()
        self.assertEqual(raw_response.status_code, 200)
        logger.info(self.pp.pformat(response))
        self.assertIsNotNone(response["label"])
        self.assertEqual(response["label"], "customer")
        self.assertIsNotNone(response["activityTypes"])
        self.assertEqual(len(response["activityTypes"]), 24)
        self.assertEqual(response["activityTypes"][20]["label"], "hvac_emergency")

    def test_313_get_activity_types(self):
        instance = self.instance
        logger = self.logger
        raw_response = instance.get_activity_types(response_type=FULL_RESPONSE)
        logging.debug(self.pp.pformat(raw_response.json()))
        response = raw_response.json()
        self.assertEqual(raw_response.status_code, 200)
        logger.info(self.pp.pformat(response))
        self.assertIsNotNone(response["items"])
        self.assertEqual(len(response["items"]), 34)
        self.assertEqual(response["totalResults"], 34)
        self.assertEqual(response["items"][28]["label"], "crew_assignment")
        self.assertEqual(response["items"][12]["label"], "06")
        activityType = response["items"][12]
        self.assertIsNotNone(activityType["features"])
        self.assertEqual(len(activityType["features"]), 27)
        self.assertEqual(activityType["features"]["allowMoveBetweenResources"], True)

    def test_313_get_activity_type(self):
        instance = self.instance
        logger = self.logger
        raw_response = instance.get_activity_type(
            "ac_installation", response_type=FULL_RESPONSE
        )
        logging.debug(self.pp.pformat(raw_response.json()))
        response = raw_response.json()
        self.assertEqual(raw_response.status_code, 200)
        logger.info(self.pp.pformat(response))
        self.assertIsNotNone(response["label"])
        self.assertEqual(response["label"], "ac_installation")
        self.assertIsNotNone(response["features"])
        self.assertEqual(len(response["features"]), 27)
        self.assertEqual(response["features"]["allowMoveBetweenResources"], True)


if __name__ == "__main__":
    unittest.main()
