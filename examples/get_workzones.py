#!python
import argparse
import logging
import pprint
from logging import basicConfig, info

from config import Config
from openpyxl import Workbook

from ofsc import OBJ_RESPONSE, OFSC
from ofsc.models import WorkzoneList


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


def get_workzone_list():
    response = instance.metadata.get_workzones(response_type=OBJ_RESPONSE)
    return WorkzoneList.model_validate(response["items"])


def write_xls(filename: str, wz_list: WorkzoneList):
    def convert(data):
        match data:
            case None:
                return data
            case str():
                return data
            case bool():
                return data
            case int():
                return data
            case _:
                return str(data)

    wb = Workbook()
    ws_workzones = wb.active
    ws_workzones.title = "Workzones"
    workzone_field_names = None
    for zone in wz_list:
        logging.warning(f"ZONE: {zone} {type(zone)}")
        if workzone_field_names is None:
            workzone_field_names = list(zone.dict().keys())
            print(f"Zone: Workzone Fields: {workzone_field_names}")
            ws_workzones.append(workzone_field_names)
        data = [convert(value) for value in zone.dict().values()]
        ws_workzones.append(data)
    wb.save(filename)
    return None


init_script()
wsc_list = get_workzone_list()
write_xls(args.output, wsc_list)
