from ofsc import FULL_RESPONSE
from ofsc.models import TimeSlotListResponse


def test_get_timeslots_basic(instance):
    response = instance.metadata.get_timeslots(response_type=FULL_RESPONSE)
    assert response.status_code == 200
    assert response.json() is not None


def test_get_timeslots_objlist(instance):
    response = instance.metadata.get_timeslots()
    assert isinstance(response, TimeSlotListResponse)
