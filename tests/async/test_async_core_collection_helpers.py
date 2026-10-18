"""The remaining async core collection helpers preserve paging and model types."""

from contextlib import asynccontextmanager
from datetime import date

import httpx
import pytest

from ofsc.async_client.core import AsyncOFSCore, _base as core_base
from ofsc.exceptions import OFSCApiError, OFSCAuthorizationError, OFSCNetworkError
from ofsc.models import Activity, OFSConfig, OFSResponseList, Property


@asynccontextmanager
async def core_with(handler):
    config = OFSConfig(clientID="fixture", companyName="fixture", secret="fixture", root="config-root", baseURL="https://fixture.invalid")
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        yield AsyncOFSCore(config, client)


async def collect(core, kind, **kwargs):
    if kind == "activities":
        return await core.get_all_activities(**kwargs)
    return await core.get_all_properties(**kwargs)


def item(kind, index):
    return {"activityId": index} if kind == "activities" else {"label": f"property-{index}", "name": "Fixture", "type": "string"}


async def test_collect_activities_preserves_filters_fields_and_actual_page_offsets():
    offsets = []
    fields, extra = ["activityId", "status"], ["status", "customField"]

    def handler(request):
        assert request.url.path == "/rest/ofscCore/v1/activities"
        assert request.url.params["resources"] == "config-root"
        assert request.url.params["includeChildren"] == "all"
        assert request.url.params["includeNonScheduled"] == "true"
        assert request.url.params["dateFrom"] == "2026-01-01"
        assert request.url.params["dateTo"] == "2026-01-02"
        assert request.url.params["fields"] == "activityId,status,customField"
        assert request.url.params["limit"] == "4"
        offset = int(request.url.params["offset"])
        offsets.append(offset)
        return httpx.Response(
            200,
            json={
                "items": [item("activities", 1), item("activities", 2)] if offset == 7 else [item("activities", 3)],
                "hasMore": offset == 7,
            },
        )

    async with core_with(handler) as core:
        result = await core.get_all_activities(
            date_from=date(2026, 1, 1),
            date_to=date(2026, 1, 2),
            activity_fields=fields,
            additional_fields=extra,
            initial_offset=7,
            limit=4,
            include_non_scheduled=True,
        )
    assert isinstance(result, OFSResponseList[Activity])
    assert [activity.activityId for activity in result.items] == [1, 2, 3]
    assert offsets == [7, 9]
    assert fields == ["activityId", "status"]
    assert extra == ["status", "customField"]


async def test_default_date_window_is_calculated_at_call_time_and_root_can_be_overridden(monkeypatch):
    class FixedDate(date):
        @classmethod
        def today(cls):
            return date(2026, 10, 13)

    monkeypatch.setattr(core_base, "date", FixedDate)

    def handler(request):
        assert request.url.params["dateFrom"] == "2026-10-06"
        assert request.url.params["dateTo"] == "2026-10-20"
        assert request.url.params["resources"] == "override-root"
        assert request.url.params["fields"] == "activityId,activityType,date,resourceId,status"
        assert request.url.params.get("includeNonScheduled", "false") == "false"
        return httpx.Response(200, json={"items": [], "hasMore": False})

    async with core_with(handler) as core:
        result = await core.get_all_activities(root="override-root")
    assert result.items == []


@pytest.mark.parametrize(
    "dates",
    [
        {"date_from": date(2026, 1, 1)},
        {"date_to": date(2026, 1, 2)},
        {"date_from": date(2026, 1, 3), "date_to": date(2026, 1, 2)},
    ],
)
async def test_invalid_date_ranges_fail_before_http(dates):
    def handler(request):
        pytest.fail("invalid date ranges must not send a request")

    async with core_with(handler) as core:
        with pytest.raises(ValueError):
            await core.get_all_activities(**dates)


async def test_collect_properties_uses_metadata_endpoint_and_typed_items():
    offsets = []

    def handler(request):
        assert request.url.path == "/rest/ofscMetadata/v1/properties"
        assert request.url.params["limit"] == "5"
        offset = int(request.url.params["offset"])
        offsets.append(offset)
        return httpx.Response(
            200,
            json={
                "items": [item("properties", 1), item("properties", 2)] if offset == 2 else [item("properties", 3)],
                "hasMore": offset == 2,
            },
        )

    async with core_with(handler) as core:
        result = await core.get_all_properties(initial_offset=2, limit=5)
    assert isinstance(result, OFSResponseList[Property])
    assert [prop.label for prop in result.items] == ["property-1", "property-2", "property-3"]
    assert offsets == [2, 4]


@pytest.mark.parametrize("kind", ["activities", "properties"])
async def test_empty_final_page_is_valid(kind):
    async with core_with(lambda request: httpx.Response(200, json={"items": [], "hasMore": False})) as core:
        assert (await collect(core, kind)).items == []


@pytest.mark.parametrize("kind", ["activities", "properties"])
@pytest.mark.parametrize("options", [{"initial_offset": -1}, {"limit": 0}, {"limit": -3}])
async def test_invalid_paging_fails_before_http(kind, options):
    def handler(request):
        pytest.fail("invalid paging must not send a request")

    async with core_with(handler) as core:
        with pytest.raises(ValueError):
            await collect(core, kind, **options)


@pytest.mark.parametrize("kind", ["activities", "properties"])
async def test_empty_page_with_more_data_cannot_loop(kind):
    calls = 0

    def handler(request):
        nonlocal calls
        calls += 1
        assert calls == 1
        return httpx.Response(200, json={"items": [], "hasMore": True})

    async with core_with(handler) as core:
        with pytest.raises(OFSCApiError):
            await collect(core, kind)
    assert calls == 1


@pytest.mark.parametrize("kind", ["activities", "properties"])
async def test_later_page_http_error_is_not_hidden_by_partial_results(kind):
    def handler(request):
        if request.url.params["offset"] == "0":
            return httpx.Response(200, json={"items": [item(kind, 1)], "hasMore": True})
        return httpx.Response(403, json={"status": "403", "detail": "fixture permission error"})

    async with core_with(handler) as core:
        with pytest.raises(OFSCAuthorizationError) as caught:
            await collect(core, kind)
    assert caught.value.detail == "fixture permission error"


@pytest.mark.parametrize("kind", ["activities", "properties"])
async def test_later_page_transport_error_keeps_its_cause(kind):
    original = httpx.ReadTimeout("fixture timeout")

    def handler(request):
        if request.url.params["offset"] == "0":
            return httpx.Response(200, json={"items": [item(kind, 1)], "hasMore": True})
        raise original

    async with core_with(handler) as core:
        with pytest.raises(OFSCNetworkError) as caught:
            await collect(core, kind)
    assert caught.value.__cause__ is original
