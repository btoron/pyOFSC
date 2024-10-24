#!python
import argparse
import logging

from config import Config

import ofsc
from ofsc import FULL_RESPONSE, OBJ_RESPONSE, OFSC


def init_script():
    # Parse arguments
    global args, instance
    parser = argparse.ArgumentParser(description="Extract users from OFSC instance")
    parser.add_argument(
        "--verbose",
        type=int,
        choices={0, 1, 2, 3},
        default=1,
        help="Additional messages. 0 is None, 3 is detailed debug",
    )
    args = parser.parse_args()

    # create logger
    logging.basicConfig(level=40 - 10 * int(args.verbose))
    instance = OFSC(
        clientID=Config.OFSC_CLIENT_ID,
        secret=Config.OFSC_CLIENT_SECRET,
        companyName=Config.OFSC_COMPANY,
        baseUrl=Config.OFSC_BASE_URL,
    )
    logging.info(
        "Creating instance connection for {} {}".format(
            Config.OFSC_COMPANY, Config.OFSC_CLIENT_ID
        )
    )
    return instance


def get_users(instance):
    response = instance.core.get_users(offset=0, limit=100, response_type=OBJ_RESPONSE)
    total_results = response["totalResults"]
    offset = response["offset"]
    final_items_list = response["items"]
    while offset + 100 < total_results:
        print(
            "Still pending users Total Results : {} - Offset : {} - List size {}".format(
                total_results, offset, len(final_items_list)
            )
        )
        offset = offset + 100
        response_json = instance.core.get_users(
            offset=offset, response_type=OBJ_RESPONSE
        )
        total_results = response_json["totalResults"]
        items = response_json["items"]
        final_items_list.extend(items)
        offset = response_json["offset"]
    return final_items_list


myInstance = init_script()

users = get_users(myInstance)

for user in users:
    print(f"{user['login']},{user['name']},{user['userType']}")
