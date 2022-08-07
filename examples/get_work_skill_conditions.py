#!python
import argparse
import pprint
from logging import basicConfig, debug, info, warning
from typing import List

import ofsc
from ofsc import FULL_RESPONSE, JSON_RESPONSE, OFSC
from ofsc.models import WorkskillCondition
from openpyxl import Workbook

from config import Config


def init_script():
    global args, instance, pp
    pp = pprint.PrettyPrinter(indent=4)
    parser = argparse.ArgumentParser(description="Extract users from OFSC instance")
    parser.add_argument(
        "--verbose",
        type=int,
        choices={0, 1, 2, 3},
        default=1,
        help="Additional messages. 0 is None, 3 is detailed debug",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="output.xlsx",
        help="Excel sheet to update",
    )
    args = parser.parse_args()

    # create logger
    basicConfig(level=40 - 10 * int(args.verbose))
    instance = OFSC(
        clientID=Config.OFSC_CLIENT_ID,
        secret=Config.OFSC_CLIENT_SECRET,
        companyName=Config.OFSC_COMPANY,
        baseUrl=Config.OFSC_BASE_URL,
    )
    info(f"Creating connection for {Config.OFSC_COMPANY} {Config.OFSC_CLIENT_ID}")
    return instance


def get_workskill_list():
    response = instance.metadata.get_workskill_conditions(response_type=JSON_RESPONSE)
    ws_list = [WorkskillCondition.parse_obj(item) for item in response["items"]]
    return ws_list


def write_xls(filename: str, wsc_list: List[WorkskillCondition]):
    wb = Workbook()
    ws_conditions = wb.create_sheet("Workskill Conditions")
    ws_rules = wb.create_sheet("Workskill Conditions Rules")
    condition_field_names = None
    rules_field_names = ["condition_id"]
    for condition in wsc_list:
        if condition_field_names is None:
            condition_field_names = list(
                condition.dict(exclude={"conditions", "dependencies"}).keys()
            )
            print(f"Condition Fields: {condition_field_names}")
            ws_conditions.append(condition_field_names)
        data = list(condition.dict(exclude={"conditions", "dependencies"}).values())
        ws_conditions.append(data)
        for rule in condition.conditions:
            if len(rules_field_names) == 1:
                rules_field_names += [str(field) for field in rule.dict().keys()]
                print(f"Rules Fields: {rules_field_names}")
                ws_rules.append(rules_field_names)
            data = [condition.internalId] + [
                str(field) for field in rule.dict().values()
            ]
            ws_rules.append(data)

    wb.save(filename)
    return None


init_script()
wsc_list = get_workskill_list()
write_xls(args.output, wsc_list)
