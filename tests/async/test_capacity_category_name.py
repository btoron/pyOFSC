"""Capacity categories may omit their display name in OFSC responses (#189)."""

from unittest.mock import AsyncMock, Mock

import pytest

from ofsc.async_client import AsyncOFSC
from ofsc.models import CapacityCategory


NAMELESS_CATEGORY = {
    "label": "BASIC",
    "active": True,
    "workSkills": [],
    "workSkillGroups": [],
    "timeSlots": [],
    "translations": [],
}


def _response(payload: dict) -> Mock:
    response = Mock()
    response.raise_for_status = Mock()
    response.json.return_value = payload
    return response


@pytest.mark.parametrize("name_field,expected", [({}, None), ({"name": None}, None), ({"name": "Basic Category"}, "Basic Category")])
def test_capacity_category_accepts_optional_name(name_field: dict, expected: str | None) -> None:
    category = CapacityCategory.model_validate({**NAMELESS_CATEGORY, **name_field})
    assert category.name == expected
    assert category.label == "BASIC"
    assert category.workSkills == []


@pytest.mark.asyncio
async def test_get_capacity_category_accepts_nameless_reply(mock_instance: AsyncOFSC) -> None:
    mock_instance.metadata._client.get = AsyncMock(return_value=_response(NAMELESS_CATEGORY.copy()))
    category = await mock_instance.metadata.get_capacity_category("BASIC")
    assert category.name is None
    assert category.label == "BASIC"


@pytest.mark.asyncio
async def test_nameless_category_does_not_reject_the_whole_page(mock_instance: AsyncOFSC) -> None:
    named = {**NAMELESS_CATEGORY, "label": "NAMED", "name": "Named Category"}
    page = {"items": [NAMELESS_CATEGORY.copy(), named], "totalResults": 2, "hasMore": False, "limit": 100, "offset": 0}
    mock_instance.metadata._client.get = AsyncMock(return_value=_response(page))
    categories = await mock_instance.metadata.get_capacity_categories()
    assert [category.label for category in categories.items] == ["BASIC", "NAMED"]
    assert [category.name for category in categories.items] == [None, "Named Category"]
    assert categories.totalResults == 2


@pytest.mark.asyncio
async def test_nameless_category_can_be_deactivated_and_read_back(mock_instance: AsyncOFSC) -> None:
    inactive = {**NAMELESS_CATEGORY, "active": False}
    mock_instance.metadata._client.put = AsyncMock(return_value=_response(inactive))
    category = CapacityCategory.model_validate(inactive)
    result = await mock_instance.metadata.create_or_replace_capacity_category(category)
    body = mock_instance.metadata._client.put.call_args.kwargs["json"]
    assert "name" not in body
    assert body["active"] is False
    assert result.name is None
    assert result.active is False
