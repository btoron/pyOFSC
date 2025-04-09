import json
import logging
from datetime import date, timedelta

import pytest

from ofsc.common import FULL_RESPONSE, OBJ_RESPONSE
from ofsc.models import (
    AssignedLocation,
    AssignedLocationsResponse,
    CalendarView,
    CalendarViewItem,
    CalendarViewShift,
    Location,
    LocationListResponse,
    ResourceUsersListResponse,
    ResourceWorkScheduleItem,
    ResourceWorkScheduleResponse,
)


@pytest.fixture
def new_data(faker):
    return {
        "parentResourceId": "SUNRISE",
        "resourceType": "BK",
        "name": faker.name(),
        "language": "en",
        "timeZone": "Arizona",
        "externalId": faker.pystr(),
    }


def test_create_resource(instance, new_data, request_logging):
    raw_response = instance.core.create_resource(
        resourceId=new_data["externalId"],
        data=json.dumps(new_data),
        response_type=FULL_RESPONSE,
    )
    response = raw_response.json()
    assert raw_response.status_code < 299
    assert "resourceId" in response.keys()
    assert response["name"] == new_data["name"]


def test_create_resource_dict(instance, new_data, request_logging):
    raw_response = instance.core.create_resource(
        resourceId=new_data["externalId"],
        data=new_data,
        response_type=FULL_RESPONSE,
    )
    response = raw_response.json()
    assert raw_response.status_code >= 299


def test_create_resource_from_obj_dict(instance, new_data, request_logging):
    raw_response = instance.core.create_resource_from_obj(
        resourceId=new_data["externalId"],
        data=new_data,
        response_type=FULL_RESPONSE,
    )
    response = raw_response.json()
    assert raw_response.status_code == 200


def test_get_resource_no_expand(instance, demo_data):
    raw_response = instance.core.get_resource(55001, response_type=FULL_RESPONSE)
    assert raw_response.status_code == 200
    logging.debug(raw_response.json())
    response = raw_response.json()
    assert response["resourceInternalId"] == 5000001


def test_get_resource_expand(instance, demo_data):
    raw_response = instance.core.get_resource(
        55001, workSkills=True, workZones=True, response_type=FULL_RESPONSE
    )
    assert raw_response.status_code == 200
    response = raw_response.json()
    assert response["resourceInternalId"] == 5000001


def test_get_position_history(instance, demo_data, current_date):
    raw_response = instance.core.get_position_history(
        33001, date=current_date, response_type=FULL_RESPONSE
    )
    assert raw_response.status_code == 200
    response = raw_response.json()
    assert response["totalResults"] is not None
    assert response["totalResults"] > 200


def test_get_resource_route_nofields(instance, pp, demo_data, current_date):
    raw_response = instance.core.get_resource_route(
        33001, date=current_date, response_type=FULL_RESPONSE
    )
    logging.debug(pp.pformat(raw_response.json()))
    assert raw_response.status_code == 200
    logging.debug(pp.pformat(raw_response.json()))
    response = raw_response.json()
    assert response["totalResults"] == 13


def test_get_resource_route_twofields(instance, current_date, pp):
    raw_response = instance.core.get_resource_route(
        33001,
        date=current_date,
        activityFields="activityId,activityType",
        response_type=FULL_RESPONSE,
    )
    logging.debug(pp.pformat(raw_response.json()))
    assert raw_response.status_code == 200
    response = raw_response.json()
    assert response["totalResults"] == 13


def test_get_resource_descendants_noexpand(instance):
    raw_response = instance.core.get_resource_descendants(
        "FLUSA", response_type=FULL_RESPONSE
    )
    assert raw_response.status_code == 200
    response = raw_response.json()
    assert response["totalResults"] == 37


def test_get_resource_descendants_expand(instance):
    raw_response = instance.core.get_resource_descendants(
        "FLUSA",
        workSchedules=True,
        workZones=True,
        workSkills=True,
        response_type=FULL_RESPONSE,
    )
    assert raw_response.status_code == 200
    response = raw_response.json()
    assert response["totalResults"] == 37


def test_get_resource_descendants_noexpand_fields(instance, pp):
    raw_response = instance.core.get_resource_descendants(
        "FLUSA", resourceFields="resourceId,phone", response_type=FULL_RESPONSE
    )
    assert raw_response.status_code == 200
    response = raw_response.json()
    logging.debug(pp.pformat(response))
    assert response["totalResults"] == 37


def test_update_resource(instance, demo_data, request_logging):
    raw_response = instance.core.update_resource(
        "FLUSA", data={"name": "FLUSA-1"}, response_type=FULL_RESPONSE
    )
    assert raw_response.status_code == 200
    response = raw_response.json()
    assert response["name"] == "FLUSA-1"
    raw_response = instance.core.update_resource(
        "FLUSA", data={"name": "FLUSA"}, response_type=FULL_RESPONSE
    )


def test_update_resource_external_id(instance, demo_data, request_logging):
    raw_response = instance.core.update_resource(
        "8100308",
        data={"resourceId": "FLUSA-1"},
        identify_by_internal_id=True,
        response_type=FULL_RESPONSE,
    )
    assert raw_response.status_code == 200
    response = raw_response.json()
    assert response["resourceId"] == "FLUSA-1"
    # Do a get to the resource
    raw_response = instance.core.get_resource("FLUSA-1", response_type=FULL_RESPONSE)
    assert raw_response.status_code == 200
    response = raw_response.json()
    assert response["resourceId"] == "FLUSA-1"
    # reset
    raw_response = instance.core.update_resource(
        "8100308",
        data={"resourceId": "FLUSA"},
        identify_by_internal_id=True,
        response_type=FULL_RESPONSE,
    )
    assert raw_response.status_code == 200
    response = raw_response.json()
    assert response["resourceId"] == "FLUSA"
    # Do a get to the resource
    raw_response = instance.core.get_resource("FLUSA", response_type=FULL_RESPONSE)
    assert raw_response.status_code == 200
    response = raw_response.json()
    assert response["resourceId"] == "FLUSA"


def test_get_resource_users_base(instance, demo_data):
    raw_response = instance.core.get_resource_users(
        "55001", response_type=FULL_RESPONSE
    )
    assert raw_response.status_code == 200
    response = raw_response.json()
    assert response["totalResults"] == 1
    assert response["items"][0]["login"] == "walter.ambriz"


def test_get_resource_users_obj(instance, demo_data):
    response = instance.core.get_resource_users("55001", response_type=OBJ_RESPONSE)
    assert isinstance(response, ResourceUsersListResponse)
    assert response.totalResults == 1
    assert response.users[0] == "walter.ambriz"


def test_set_resource_users(instance, demo_data):
    initial_data = instance.core.get_resource_users("33001", response_type=OBJ_RESPONSE)
    assert initial_data.totalResults == 1
    assert initial_data.users[0] == "william.arndt"

    raw_response = instance.core.set_resource_users(
        resource_id="33001",
        users=["william.arndt", "terri.basile"],
        response_type=FULL_RESPONSE,
    )
    assert raw_response.status_code == 200
    response = raw_response.json()
    assert response["items"][0]["login"] == "william.arndt"
    logging.warning(initial_data.users)
    new_response = instance.core.set_resource_users(
        resource_id="33001", users=initial_data.users, response_type=FULL_RESPONSE
    )
    assert new_response.status_code == 200
    logging.warning(new_response.json())
    assert False


def test_reset_resource_users(instance, demo_data):
    instance.core.delete_resource_users(resource_id="100000490999044")
    raw_response = instance.core.set_resource_users(
        resource_id="100000490999044",
        users=["chris.conner"],
        response_type=FULL_RESPONSE,
    )
    assert raw_response.status_code == 200, raw_response.json()
    response = raw_response.json()
    assert response["items"][0]["login"] == "chris.conner"
    assert len(response["items"]) == 1
    raw_response = instance.core.get_resource_users(
        "100000490999044", response_type=FULL_RESPONSE
    )
    assert raw_response.status_code == 200
    response = raw_response.json()
    assert response["totalResults"] == 1


def test_reset2_resource_users(instance, demo_data):
    raw_response = instance.core.set_resource_users(
        resource_id="33001", users=["william.arndt"], response_type=FULL_RESPONSE
    )
    assert raw_response.status_code == 200, raw_response.json()
    response = raw_response.json()
    assert response["items"][0]["login"] == "william.arndt"
    assert len(response["items"]) == 1
    raw_response = instance.core.get_resource_users(
        "33001", response_type=FULL_RESPONSE
    )
    assert raw_response.status_code == 200
    response = raw_response.json()
    assert response["totalResults"] == 1
    assert response["items"][0]["login"] == "william.arndt"


def test_delete_resource_users(instance, demo_data):
    initial_data = instance.core.get_resource_users("33001", response_type=OBJ_RESPONSE)
    assert initial_data.totalResults == 1
    assert initial_data.users[0] == "william.arndt"

    raw_response = instance.core.delete_resource_users(
        resource_id="33001",
        response_type=FULL_RESPONSE,
    )
    assert raw_response.status_code == 204
    modified_data = instance.core.get_resource_users(
        "33001", response_type=OBJ_RESPONSE
    )
    assert modified_data.totalResults == 0
    instance.core.set_resource_users(resource_id="33001", users=initial_data.users)


def test_add_resource_users(instance, demo_data):
    raw_response = instance.core.set_resource_users(
        resource_id="33001",
        users=["william.arndt", "admin"],
        response_type=FULL_RESPONSE,
    )
    assert raw_response.status_code == 200, raw_response.json()
    response = raw_response.json()
    assert len(response["items"]) == 2
    assert response["items"][0]["login"] == "william.arndt"
    assert response["items"][1]["login"] == "admin"


def test_get_calendar_view_basic(instance, demo_data):
    raw_response = instance.core.get_resource_calendar(
        "33001",
        dateFrom=date.today(),
        dateTo=date.today() + timedelta(days=30),
        response_type=FULL_RESPONSE,
    )
    assert raw_response.status_code == 200
    response = raw_response.json()
    assert isinstance(response, dict)
    # Delete the links
    del response["links"]
    assert len(response) == 31
    for day in response:
        assert isinstance(response[day], dict)
        for label, record in response[day].items():
            assert isinstance(label, str)
            assert label in ["regular", "on-call"]
            data = CalendarViewItem.model_validate(record)


def test_get_calendar_view_object(instance, demo_data):
    response: CalendarView = instance.core.get_resource_calendar(
        "33008",
        dateFrom=date.today(),
        dateTo=date.today() + timedelta(days=30),
        response_type=OBJ_RESPONSE,
    )
    assert isinstance(response, CalendarView)
    for day, shift in response.root.items():
        assert isinstance(day, str)
        assert isinstance(response[day], CalendarViewShift)
        if shift.regular is not None:
            assert isinstance(shift.regular, CalendarViewItem)
        if shift.on_call is not None:
            assert isinstance(shift.on_call, CalendarViewItem)


def test_get_resource_workschedules_base(instance):
    raw_response = instance.core.get_resource_workschedules(
        "33003", actualDate=date.today(), response_type=FULL_RESPONSE
    )
    assert raw_response.status_code == 200


def test_get_resource_workschedules_obj(instance):
    response = instance.core.get_resource_workschedules(
        "33003", actualDate=date.today(), response_type=OBJ_RESPONSE
    )
    assert isinstance(response, ResourceWorkScheduleResponse)
    for item in response.items:
        assert isinstance(item, ResourceWorkScheduleItem)


def test_set_resource_workschedules_obj(instance, request_logging):
    schedule = ResourceWorkScheduleItem(shiftLabel="9-18", recordType="shift")
    response = instance.core.set_resource_workschedules(
        "33003",
        data=schedule,
        response_type=FULL_RESPONSE,
    )
    assert response.status_code == 200, f"Error: {response.json()}"


def test_get_resource_locations_base(instance):
    raw_response = instance.core.get_resource_locations(
        "FLUSA", response_type=FULL_RESPONSE
    )
    assert raw_response.status_code == 200
    response = raw_response.json()
    assert response["totalResults"] == 1
    assert response["items"][0]["postalCode"] == "32817"


def test_get_resource_locations_obj(instance):
    response = instance.core.get_resource_locations("FLUSA", response_type=OBJ_RESPONSE)
    assert isinstance(response, LocationListResponse)
    for item in response.items:
        assert isinstance(item, Location)


def test_create_resource_location_basic(instance, request_logging):
    location = Location(
        address="3232 Coral Way",
        city="Miami",
        state="FL",
        postalCode="33145",
        label="HOME",
    )
    raw_response = instance.core.create_resource_location(
        "FLUSA", location=location, response_type=FULL_RESPONSE
    )
    assert raw_response.status_code == 201, raw_response.json()
    response = raw_response.json()
    assert [
        response[key] == location.model_dump()[key]
        for key in location.model_dump(
            exclude_defaults=True, exclude_none=True, exclude_unset=True
        ).keys()
    ]
    assert response["locationId"] is not None
    # Reset the location
    raw_response = instance.core.delete_resource_location(
        "FLUSA", location_id=response["locationId"], response_type=FULL_RESPONSE
    )
    assert raw_response.status_code == 204


def test_create_resource_location_obj(instance, request_logging):
    location = Location(
        address="3232 Coral Way",
        city="Miami",
        state="FL",
        postalCode="33145",
        label="HOME",
    )
    response = instance.core.create_resource_location("FLUSA", location=location)
    assert isinstance(response, Location)
    # Reset the location
    instance.core.delete_resource_location(
        "FLUSA", location_id=response.locationId, response_type=FULL_RESPONSE
    )


def test_get_assigned_locations_basic(instance):
    raw_response = instance.core.get_assigned_locations(
        "33003", response_type=FULL_RESPONSE
    )
    assert raw_response.status_code == 200
    response = raw_response.json()
    assert isinstance(response, dict)


def test_get_assigned_locations_obj(instance):
    response = instance.core.get_assigned_locations("33003", response_type=OBJ_RESPONSE)
    assert isinstance(response, AssignedLocationsResponse)


def test_set_assigned_locations_obj(instance):
    location = Location(
        address="3232 Coral Way",
        city="Miami",
        state="FL",
        postalCode="33145",
        label="HOME",
    )
    # Create the location in the resource 33008
    created_location = instance.core.create_resource_location(
        "33008", location=location
    )
    assert isinstance(created_location, Location)

    # Set the assigned location only for mondays
    assigned_location = AssignedLocationsResponse(
        mon=AssignedLocation(start=created_location.locationId, end=None)
    )

    response = instance.core.set_assigned_locations(
        "33008",
        data=assigned_location,
    )
    # reset
    instance.core.delete_resource_location(
        "33008", location_id=created_location.locationId
    )
