"""Activity types may omit their display name in OFSC responses (#208)."""

from unittest.mock import AsyncMock, Mock

import pytest

from ofsc.async_client import AsyncOFSC
from ofsc.models import ActivityType


NAMELESS_ACTIVITY_TYPE = {
    "label": "PTO",
    "active": True,
    "defaultDuration": 60,
    "groupLabel": "internal",
    "translations": [],
}


def _response(payload: dict) -> Mock:
    response = Mock()
    response.raise_for_status = Mock()
    response.json.return_value = payload
    return response


@pytest.mark.parametrize("name_field,expected", [({}, None), ({"name": None}, None), ({"name": "Paid Time Off"}, "Paid Time Off")])
def test_activity_type_accepts_optional_name(name_field: dict, expected: str | None) -> None:
    activity_type = ActivityType.model_validate({**NAMELESS_ACTIVITY_TYPE, **name_field})
    assert activity_type.name == expected
    assert activity_type.label == "PTO"
    assert activity_type.groupLabel == "internal"


def test_activity_type_accepts_missing_group_label() -> None:
    payload = {key: value for key, value in NAMELESS_ACTIVITY_TYPE.items() if key != "groupLabel"}
    activity_type = ActivityType.model_validate(payload)
    assert activity_type.groupLabel is None


@pytest.mark.asyncio
async def test_get_activity_type_accepts_nameless_reply(mock_instance: AsyncOFSC) -> None:
    mock_instance.metadata._client.get = AsyncMock(return_value=_response(NAMELESS_ACTIVITY_TYPE.copy()))
    activity_type = await mock_instance.metadata.get_activity_type("PTO")
    assert activity_type.name is None
    assert activity_type.label == "PTO"


@pytest.mark.asyncio
async def test_nameless_activity_type_does_not_reject_the_whole_page(mock_instance: AsyncOFSC) -> None:
    named = {**NAMELESS_ACTIVITY_TYPE, "label": "INSTALL", "name": "Installation"}
    page = {"items": [named, NAMELESS_ACTIVITY_TYPE.copy()], "totalResults": 2, "hasMore": False, "limit": 100, "offset": 0}
    mock_instance.metadata._client.get = AsyncMock(return_value=_response(page))
    activity_types = await mock_instance.metadata.get_activity_types()
    assert [activity_type.label for activity_type in activity_types.items] == ["INSTALL", "PTO"]
    assert [activity_type.name for activity_type in activity_types.items] == ["Installation", None]
    assert activity_types.totalResults == 2


@pytest.mark.asyncio
async def test_nameless_activity_type_is_written_without_a_name(mock_instance: AsyncOFSC) -> None:
    inactive = {**NAMELESS_ACTIVITY_TYPE, "active": False}
    mock_instance.metadata._client.put = AsyncMock(return_value=_response(inactive))
    activity_type = ActivityType.model_validate(inactive)
    result = await mock_instance.metadata.create_or_replace_activity_type(activity_type)
    body = mock_instance.metadata._client.put.call_args.kwargs["json"]
    assert "name" not in body
    assert body["active"] is False
    assert result.name is None
    assert result.active is False
