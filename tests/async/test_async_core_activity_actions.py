"""Mocked tests for activity custom actions and whereIsMyTech (#123)."""

import json
from contextlib import asynccontextmanager

import httpx
import pytest

from ofsc.async_client.core import AsyncOFSCore
from ofsc.exceptions import OFSCNetworkError, OFSCNotFoundError
from ofsc.models import (
    Activity,
    ActivityActionRequest,
    DelayActivityRequest,
    OFSConfig,
    ReopenActivityRequest,
    SetPositionInRoute,
    StartPreworkRequest,
    WhereIsMyTechResponse,
)


@asynccontextmanager
async def core_with(handler):
    config = OFSConfig(clientID="fixture", companyName="fixture", secret="fixture", baseURL="https://fixture.invalid")
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        yield AsyncOFSCore(config, client)


ACTIONS = [
    ("start_prework", "startPrework"),
    ("reopen_activity", "reopen"),
    ("delay_activity", "delay"),
    ("cancel_activity", "cancel"),
    ("start_activity", "start"),
    ("enroute_activity", "enroute"),
    ("stop_travel", "stopTravel"),
    ("suspend_activity", "suspend"),
    ("complete_activity", "complete"),
    ("notdone_activity", "notDone"),
]


@pytest.mark.parametrize("method,segment", [a for a in ACTIONS if a[0] != "reopen_activity"])
async def test_action_without_body_returns_activity(method, segment):
    def handler(request):
        assert request.method == "POST"
        assert request.url.path == f"/rest/ofscCore/v1/activities/42/custom-actions/{segment}"
        assert not request.content
        return httpx.Response(200, json={"activityId": 42, "status": "started"})

    async with core_with(handler) as core:
        result = await getattr(core, method)(42)
    assert isinstance(result, Activity)
    assert result.activityId == 42


@pytest.mark.parametrize(
    "method,body",
    [
        ("start_prework", {"time": "2026-01-01 10:00:00"}),
        ("reopen_activity", {"setPositionInRoute": {"position": "first"}}),
        ("delay_activity", {"delayMinutes": 15}),
        ("cancel_activity", {"time": "2026-01-01 10:00:00", "multidayActivityStatus": "cancelled"}),
        ("start_activity", {"time": "2026-01-01 10:00:00"}),
        ("suspend_activity", {"time": "2026-01-01 10:00:00"}),
        ("complete_activity", {"multidayTimeToComplete": 0}),
        ("notdone_activity", {"time": "2026-01-01 10:00:00"}),
    ],
)
async def test_action_dict_body_is_sent(method, body):
    def handler(request):
        assert json.loads(request.content) == body
        return httpx.Response(200, json={"activityId": 7})

    async with core_with(handler) as core:
        result = await getattr(core, method)(7, body)
    assert result.activityId == 7


async def test_model_bodies_omit_none():
    seen = []

    def handler(request):
        seen.append(json.loads(request.content))
        return httpx.Response(200, json={"activityId": 1})

    async with core_with(handler) as core:
        await core.delay_activity(1, DelayActivityRequest(delayUntilTime="2026-01-01 10:00:00"))
        await core.complete_activity(1, ActivityActionRequest(time="2026-01-01 10:00:00"))
        await core.reopen_activity(1, ReopenActivityRequest(setPositionInRoute=SetPositionInRoute(position="last")))
        await core.start_prework(1, StartPreworkRequest(time="2026-01-01 10:00:00"))
    assert seen == [
        {"delayUntilTime": "2026-01-01 10:00:00"},
        {"time": "2026-01-01 10:00:00"},
        {"setPositionInRoute": {"position": "last"}},
        {"time": "2026-01-01 10:00:00"},
    ]


async def test_action_404_maps_to_typed_error():
    async with core_with(lambda r: httpx.Response(404, json={"detail": "nope"})) as core:
        with pytest.raises(OFSCNotFoundError):
            await core.cancel_activity(1)


async def test_action_transport_error_maps_to_network_error():
    def handler(request):
        raise httpx.ConnectError("boom")

    async with core_with(handler) as core:
        with pytest.raises(OFSCNetworkError):
            await core.enroute_activity(1)


async def test_where_is_my_tech_sends_query_and_returns_model():
    def handler(request):
        assert request.method == "GET"
        assert request.url.path == "/rest/ofscCore/v1/whereIsMyTech"
        q = request.url.params
        assert q["activityId"] == "42"
        assert q["includeAvatarImageData"] == "true"
        assert q["resourceFields"] == "name,phone"
        assert q["activityFields"] == "address"
        assert q["hideResourceLocationTime"] == "5"
        return httpx.Response(
            200,
            json={
                "status": "onTheWay",
                "resourceDetails": {"name": "Tech", "avatar": {"filename": "a.png"}},
                "coordinates": {"time": "2026-01-01T10:00:00Z", "latitude": 1.5, "longitude": 2.5},
                "activityDetails": {"activityId": 42, "startTime": "2026-01-01 10:00:00", "timeZoneDiff": -180},
            },
        )

    async with core_with(handler) as core:
        result = await core.where_is_my_tech(
            42,
            include_avatar_image_data=True,
            resource_fields=["name", "phone"],
            activity_fields=["address"],
            hide_resource_location_time=5,
        )
    assert isinstance(result, WhereIsMyTechResponse)
    assert result.status == "onTheWay"
    assert result.coordinates is not None and result.coordinates.latitude == 1.5
    assert result.activityDetails is not None and result.activityDetails.activityId == 42
    assert result.resourceDetails is not None and result.resourceDetails.name == "Tech"


async def test_where_is_my_tech_minimal_query():
    def handler(request):
        assert dict(request.url.params) == {"activityId": "3"}
        return httpx.Response(200, json={"status": "notAssigned"})

    async with core_with(handler) as core:
        result = await core.where_is_my_tech(3)
    assert result.status == "notAssigned"
    assert result.coordinates is None
