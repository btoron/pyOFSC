"""Everyday recurrences may omit recurEvery in OFSC responses (#218)."""

from datetime import date
from unittest.mock import AsyncMock, Mock

import pytest
from pydantic import ValidationError

from ofsc.async_client import AsyncOFSC
from ofsc.models import Recurrence, RecurrenceType, ResourceWorkScheduleItem


EVERYDAY_SCHEDULE = {
    "recordType": "schedule",
    "scheduleLabel": "SCH_5X8_0800",
    "startDate": "2026-10-01",
    "recurrence": {"recurrenceType": "everyday"},
}


def _response(payload: dict) -> Mock:
    response = Mock()
    response.raise_for_status = Mock()
    response.json.return_value = payload
    return response


def test_everyday_recurrence_accepts_missing_recur_every() -> None:
    recurrence = Recurrence.model_validate({"recurrenceType": "everyday"})
    assert recurrence.recurrenceType == RecurrenceType.everyday
    assert recurrence.recurEvery is None


def test_recur_every_keeps_its_range_when_present() -> None:
    assert Recurrence.model_validate({"recurrenceType": "daily", "recurEvery": 2}).recurEvery == 2
    with pytest.raises(ValidationError):
        Recurrence.model_validate({"recurrenceType": "daily", "recurEvery": 0})


def test_default_item_recurrence_is_unchanged() -> None:
    item = ResourceWorkScheduleItem.model_validate({"recordType": "schedule"})
    assert item.recurrence == Recurrence(recurEvery=1, recurrenceType=RecurrenceType.daily)


@pytest.mark.asyncio
async def test_everyday_item_does_not_reject_the_whole_response(mock_instance: AsyncOFSC) -> None:
    daily = {**EVERYDAY_SCHEDULE, "scheduleLabel": "SCH_DAILY", "recurrence": {"recurrenceType": "daily", "recurEvery": 1}}
    page = {"items": [daily, EVERYDAY_SCHEDULE.copy()], "totalResults": 2}
    mock_instance.core._client.get = AsyncMock(return_value=_response(page))
    schedules = await mock_instance.core.get_resource_workschedules("RES_1", date(2026, 10, 1))
    assert [item.scheduleLabel for item in schedules.items] == ["SCH_DAILY", "SCH_5X8_0800"]
    assert schedules.items[1].recurrence is not None
    assert schedules.items[1].recurrence.recurrenceType == RecurrenceType.everyday
    assert schedules.items[1].recurrence.recurEvery is None


@pytest.mark.asyncio
async def test_everyday_item_is_written_without_recur_every(mock_instance: AsyncOFSC) -> None:
    mock_instance.core._client.post = AsyncMock(return_value=_response({"items": [EVERYDAY_SCHEDULE.copy()], "totalResults": 1}))
    item = ResourceWorkScheduleItem.model_validate(EVERYDAY_SCHEDULE)
    await mock_instance.core.set_resource_workschedules("RES_1", item)
    body = mock_instance.core._client.post.call_args.kwargs["json"]
    assert body["recurrence"] == {"recurrenceType": RecurrenceType.everyday}
