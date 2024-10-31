import argparse
import csv
import logging
import pprint

from config import Config
from flatten_dict import flatten

from ofsc import FULL_RESPONSE, OFSC

capacityAreasFields = "label,name,type,status,parent.name,parent.label"


def init_script():
    # Parse arguments
    global args

    # TODO : add custom_fields argument
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", type=int, choices={0, 1, 2, 3}, default=1)
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--root", type=str, default=Config.OFSC_ROOT)
    parser.add_argument("--output", type=str, default="output.csv")
    args = parser.parse_args()

    # create logger
    global logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.info("Starting execution: {}".format(args.verbose))
    # create console handler and set level to debug
    ch = logging.StreamHandler()
    # create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    # add formatter to ch
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logger.setLevel(40 - 10 * int(args.verbose))
    logger.info("Log level is {}".format(args.verbose))

    global instance
    instance = OFSC(
        clientID=Config.OFSC_CLIENT_ID,
        secret=Config.OFSC_CLIENT_SECRET,
        companyName=Config.OFSC_COMPANY,
    )
    logger.info(
        "Creating instance connection for {} {}".format(
            Config.OFSC_COMPANY, Config.OFSC_CLIENT_ID
        )
    )


def connectivity_test():
    logger.info("TEST 000: connectivity")
    response = instance.core.get_subscriptions(response_type=FULL_RESPONSE)
    logger.debug(pprint.pformat(response.text))
    logger.info("{}...Elapsed Time: {}".format(response.status_code, response.elapsed))
    return response.elapsed


def get_capacity_info():
    result = instance.metadata.get_capacity_areas()
    response = result.json()
    if "items" in response.keys():
        response_count = len(response["items"])
        original_items = response["items"]
        items = []
        # Reduce structure and get extra info
        for area in original_items:
            logger.info("Retrieving {}".format(area))
            result = instance.metadata.get_capacity_area(area["label"])
            item = result.json()
            logger.info(item)
            for definitionLevel in item["configuration"]["definitionLevel"]:
                item["configuration.definitionLevel.{}".format(definitionLevel)] = True
            new_item = flatten(item, reducer="dot")
            logger.debug(pprint.pformat(new_item))
            items.append(new_item)
    else:
        print(response)
    return items


additionalFields = [
    "parentLabel",
    "configuration.isTimeSlotBase",
    "configuration.byCapacityCategory",
    "configuration.byDay",
    "configuration.byTimeSlot",
    "configuration.isAllowCloseOnWorkzoneLevel",
    "configuration.definitionLevel.day",
    "configuration.definitionLevel.timeSlot",
    "configuration.definitionLevel.capacityCategory",
]
app = pprint.PrettyPrinter(indent=4)


def write_csv(items, header_fields, filename):
    logger.info("First element: {}".format(items[0]))
    logger.info(pprint.pformat(items[0]))
    headers = header_fields.split(",") + additionalFields
    print(additionalFields)
    print(headers)
    try:
        with open(filename, "w") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers, extrasaction="ignore")
            writer.writeheader()
            for data in items:
                writer.writerow(data)
    except IOError:
        print("I/O error")


fields = capacityAreasFields
init_script()
write_csv(get_capacity_info(), header_fields=fields, filename=args.output)
