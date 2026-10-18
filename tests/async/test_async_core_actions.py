"""Transport contracts for the three implemented core operation stubs (#151)."""

import json
from contextlib import asynccontextmanager

import httpx
import pytest

from ofsc.async_client.core import AsyncOFSCore
from ofsc.exceptions import (
    OFSCAuthenticationError,
    OFSCAuthorizationError,
    OFSCConflictError,
    OFSCNetworkError,
    OFSCNotFoundError,
    OFSCRateLimitError,
    OFSCServerError,
    OFSCValidationError,
)
from ofsc.models import (
    ActivityListResponse,
    BulkUpdateActivityItem,
    BulkUpdateParameters,
    BulkUpdateRequest,
    BulkUpdateResponse,
    OFSConfig,
)


@asynccontextmanager
async def core_with(handler):
    config = OFSConfig(clientID="fixture", companyName="fixture", secret="fixture", baseURL="https://fixture.invalid")
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        yield AsyncOFSCore(config, client)


def bulk_request():
    return BulkUpdateRequest(
        activities=[
            BulkUpdateActivityItem(activityId=None, activityType="install", resourceId="fixture", customerName=None),
            BulkUpdateActivityItem(activityId=42, customerNumber="customer-2"),
        ],
        updateParameters=BulkUpdateParameters(identifyActivityBy="activityId"),
    )


async def invoke(core, operation):
    if operation == "search":
        return await core.search_activities({"searchInField": "customerName", "searchForValue": "fixture", "includeNonScheduled": "true"})
    if operation == "move":
        return await core.move_activity(42, {"setDate": {"date": None}})
    return await core.bulk_update(bulk_request())


async def test_search_sends_query_and_returns_typed_items():
    params = {
        "searchInField": "customerName",
        "searchForValue": "fixture & value",
        "dateFrom": "2026-10-13",
        "dateTo": "2026-10-14",
        "offset": 7,
        "limit": 20,
    }
    original = params.copy()

    def handler(request):
        assert request.method == "GET"
        assert request.url.path == "/rest/ofscCore/v1/activities/custom-actions/search"
        assert request.url.params["searchForValue"] == "fixture & value"
        assert request.url.params["offset"] == "7"
        assert request.url.params["limit"] == "20"
        assert request.headers["Authorization"].startswith("Basic ")
        return httpx.Response(
            200,
            json={
                "items": [{"activityId": 42, "resourceId": "fixture", "status": "pending"}],
                "totalResults": 1,
                "offset": 7,
                "limit": 20,
                "hasMore": False,
                "links": [{"rel": "canonical", "href": str(request.url)}],
            },
        )

    async with core_with(handler) as core:
        result = await core.search_activities(params)
    assert isinstance(result, ActivityListResponse)
    assert result.items[0].activityId == 42
    assert result.offset == 7
    assert result.totalResults == 1
    assert params == original


async def test_search_empty_result_is_valid():
    async with core_with(lambda request: httpx.Response(200, json={"items": [], "totalResults": 0})) as core:
        result = await core.search_activities({"includeNonScheduled": "true"})
    assert result.items == []
    assert result.totalResults == 0


@pytest.mark.parametrize(
    "payload",
    [
        {"setDate": {"date": None}},
        {"setDate": {"date": "2026-10-14"}, "setResource": {"resourceId": "fixture-2"}, "setPositionInRoute": {"position": "first"}},
    ],
)
async def test_move_preserves_actions_and_accepts_empty_204(payload):
    original = json.dumps(payload, sort_keys=True)

    def handler(request):
        assert request.method == "POST"
        assert request.url.path == "/rest/ofscCore/v1/activities/42/custom-actions/move"
        assert request.headers["Content-Type"].startswith("application/json")
        assert json.loads(request.content) == payload
        return httpx.Response(204)

    async with core_with(handler) as core:
        assert await core.move_activity(42, payload) is None
    assert json.dumps(payload, sort_keys=True) == original


async def test_bulk_preserves_explicit_nulls_omits_unset_fields_and_returns_each_result():
    data = bulk_request()
    original = data.model_dump()

    def handler(request):
        assert request.method == "POST"
        assert request.url.path == "/rest/ofscCore/v1/activities/custom-actions/bulkUpdate"
        assert json.loads(request.content) == {
            "activities": [
                {"activityId": None, "activityType": "install", "resourceId": "fixture", "customerName": None},
                {"activityId": 42, "customerNumber": "customer-2"},
            ],
            "updateParameters": {"identifyActivityBy": "activityId"},
        }
        return httpx.Response(
            200,
            json={
                "results": [
                    {"activityKeys": {"activityId": 99}, "operationsPerformed": ["create"], "warnings": [{"message": "fixture warning"}]},
                    {
                        "activityKeys": {"activityId": 42},
                        "operationsFailed": ["update"],
                        "errors": [{"operation": "update", "errorDetail": "fixture conflict"}],
                    },
                ]
            },
        )

    async with core_with(handler) as core:
        result = await core.bulk_update(data)
    assert isinstance(result, BulkUpdateResponse)
    assert result.results[0].activityKeys.activityId == 99
    assert result.results[0].warnings[0].message == "fixture warning"
    assert result.results[1].errors[0].errorDetail == "fixture conflict"
    assert result.results[1].operationsFailed == ["update"]
    assert data.model_dump() == original


@pytest.mark.parametrize("operation", ["search", "move", "bulk"])
@pytest.mark.parametrize(
    ("status", "exception"),
    [
        (400, OFSCValidationError),
        (401, OFSCAuthenticationError),
        (403, OFSCAuthorizationError),
        (404, OFSCNotFoundError),
        (409, OFSCConflictError),
        (429, OFSCRateLimitError),
        (500, OFSCServerError),
    ],
)
async def test_http_errors_retain_typed_status_and_detail(operation, status, exception):
    def handler(request):
        return httpx.Response(status, json={"type": "fixture-error", "title": "Fixture error", "status": str(status), "detail": "fixture detail"})

    async with core_with(handler) as core:
        with pytest.raises(exception) as caught:
            await invoke(core, operation)
    assert caught.value.status_code == status
    assert caught.value.detail == "fixture detail"


@pytest.mark.parametrize("operation", ["search", "move", "bulk"])
@pytest.mark.parametrize("exception", [httpx.ConnectError, httpx.ReadTimeout])
async def test_transport_errors_keep_their_cause(operation, exception):
    original = exception("fixture transport failure")

    def handler(request):
        raise original

    async with core_with(handler) as core:
        with pytest.raises(OFSCNetworkError) as caught:
            await invoke(core, operation)
    assert caught.value.__cause__ is original
