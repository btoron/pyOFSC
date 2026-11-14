"""Mocked tests for resource custom actions (#119)."""

import json
from contextlib import asynccontextmanager
from datetime import date

import httpx
import pytest

from ofsc.async_client.core import AsyncOFSCore
from ofsc.exceptions import OFSCNetworkError, OFSCNotFoundError
from ofsc.models import (
    BulkUpdateResourceInventoriesResponse,
    FindMatchingResourcesResponse,
    FindNearbyActivitiesResponse,
    FindUrgentResourcesResponse,
    LastKnownPositionsResponse,
    OFSConfig,
    ResourcePosition,
    ResourcesInAreaResponse,
    SetPositionsResponse,
)

BASE = "/rest/ofscCore/v1/resources"


@asynccontextmanager
async def core_with(handler):
    config = OFSConfig(clientID="fixture", companyName="fixture", secret="fixture", baseURL="https://fixture.invalid")
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        yield AsyncOFSCore(config, client)


@pytest.mark.parametrize("method,segment", [("activate_route", "activate"), ("deactivate_route", "deactivate")])
@pytest.mark.parametrize("route_date", [date(2026, 1, 5), "2026-01-05"])
async def test_route_actions(method, segment, route_date):
    def handler(request):
        assert request.method == "POST"
        assert request.url.path == f"{BASE}/R1/routes/2026-01-05/custom-actions/{segment}"
        assert json.loads(request.content) == {"time": "2026-01-05 08:00:00"}
        return httpx.Response(204)

    async with core_with(handler) as core:
        assert await getattr(core, method)("R1", route_date, time="2026-01-05 08:00:00") is None


async def test_route_action_without_time_sends_no_body():
    def handler(request):
        assert not request.content
        return httpx.Response(204)

    async with core_with(handler) as core:
        assert await core.activate_route("R1", "2026-01-05") is None


async def test_find_nearby_activities():
    def handler(request):
        assert request.url.path == f"{BASE}/R1/findNearbyActivities"
        assert request.url.params["latitude"] == "10.5"
        assert request.url.params["longitude"] == "-3.0"
        assert request.url.params["fields"] == "activityId,city"
        assert request.url.params["limit"] == "5"
        return httpx.Response(200, json={"items": [{"activityId": 1}], "coordinates": {"latitude": 10.5, "longitude": -3.0}})

    async with core_with(handler) as core:
        r = await core.find_nearby_activities("R1", latitude=10.5, longitude=-3.0, fields=["activityId", "city"], limit=5)
    assert isinstance(r, FindNearbyActivitiesResponse)
    assert r.items[0]["activityId"] == 1
    assert r.coordinates is not None and r.coordinates.latitude == 10.5


async def test_bulk_update_resource_inventories():
    body = {"resources": [{"resourceId": "R1", "inventories": [{"inventoryType": "x"}]}]}

    def handler(request):
        assert request.method == "POST"
        assert request.url.path == f"{BASE}/custom-actions/bulkUpdateInventories"
        assert json.loads(request.content) == body
        return httpx.Response(200, json={"created": 1, "itemsFailed": 0, "results": [{"resourceId": "R1", "created": 1}]})

    async with core_with(handler) as core:
        r = await core.bulk_update_resource_inventories(data=body)
    assert isinstance(r, BulkUpdateResourceInventoriesResponse)
    assert r.results[0].resourceId == "R1"


async def test_find_matching_resources():
    def handler(request):
        assert request.url.path == f"{BASE}/custom-actions/findMatchingResources"
        assert json.loads(request.content) == {"activityId": 5, "date": "2026-01-05"}
        return httpx.Response(200, json={"totalResults": 1, "items": [{"resource": {"resourceId": "R1"}, "fitness": {"workZone": 1}}]})

    async with core_with(handler) as core:
        r = await core.find_matching_resources(data={"activityId": 5, "date": "2026-01-05"})
    assert isinstance(r, FindMatchingResourcesResponse)
    assert r.items[0].resource == {"resourceId": "R1"}


async def test_find_urgent_resources():
    def handler(request):
        assert request.url.path == f"{BASE}/custom-actions/findResourcesForUrgentAssignment"
        assert json.loads(request.content)["activity"]["activityType"] == "install"
        return httpx.Response(200, json={"items": [{"nearestRoutingBucket": "B", "resourceDetails": {"resourceId": "R1"}}]})

    async with core_with(handler) as core:
        r = await core.find_urgent_resources(data={"activity": {"activityType": "install", "latitude": 1, "longitude": 2}})
    assert isinstance(r, FindUrgentResourcesResponse)
    assert r.items[0].nearestRoutingBucket == "B"


async def test_set_positions_accepts_models():
    def handler(request):
        assert request.url.path == f"{BASE}/custom-actions/setPositions"
        assert json.loads(request.content) == {"items": [{"resourceId": "R1", "time": "2026-01-05 08:00:00", "lat": 1.0, "lng": 2.0}]}
        return httpx.Response(200, json={"itemsProcessed": 1, "itemsFailed": 0})

    async with core_with(handler) as core:
        r = await core.set_positions([ResourcePosition(resourceId="R1", time="2026-01-05 08:00:00", lat=1.0, lng=2.0)])
    assert isinstance(r, SetPositionsResponse)
    assert r.itemsProcessed == 1


async def test_get_last_known_positions():
    def handler(request):
        assert request.url.path == f"{BASE}/custom-actions/lastKnownPositions"
        assert request.url.params["resources"] == "R1,R2"
        assert request.url.params["offset"] == "10"
        return httpx.Response(200, json={"items": [{"resourceId": "R1", "lat": 1, "lng": 2}], "hasMore": False})

    async with core_with(handler) as core:
        r = await core.get_last_known_positions(resources=["R1", "R2"], offset=10)
    assert isinstance(r, LastKnownPositionsResponse)
    assert r.items[0].lat == 1


async def test_get_resources_in_area():
    def handler(request):
        assert request.url.path == f"{BASE}/custom-actions/resourcesInArea"
        p = request.url.params
        assert (p["lat"], p["lng"], p["radius"], p["timeDiff"], p["offset"], p["limit"]) == ("1.5", "2.5", "500", "30", "0", "10")
        return httpx.Response(200, json={"items": [{"resourceId": "R1", "distance": 3}], "totalResults": 1})

    async with core_with(handler) as core:
        r = await core.get_resources_in_area(lat=1.5, lng=2.5, radius=500, time_diff=30, offset=0, limit=10)
    assert isinstance(r, ResourcesInAreaResponse)
    assert r.items[0].resourceId == "R1"


CALLS = [
    ("activate_route", ("R1", "2026-01-05"), {}),
    ("deactivate_route", ("R1", "2026-01-05"), {}),
    ("find_nearby_activities", ("R1",), {}),
    ("bulk_update_resource_inventories", (), {"data": {"resources": []}}),
    ("find_matching_resources", (), {"data": {}}),
    ("find_urgent_resources", (), {"data": {}}),
    ("set_positions", ([],), {}),
    ("get_last_known_positions", (), {}),
    ("get_resources_in_area", (), {"lat": 1, "lng": 2}),
]


@pytest.mark.parametrize("method,args,kwargs", CALLS)
async def test_404_maps_to_not_found(method, args, kwargs):
    async with core_with(lambda r: httpx.Response(404, json={"title": "nf"})) as core:
        with pytest.raises(OFSCNotFoundError):
            await getattr(core, method)(*args, **kwargs)


@pytest.mark.parametrize("method,args,kwargs", CALLS)
async def test_transport_error_maps_to_network_error(method, args, kwargs):
    def handler(request):
        raise httpx.ConnectError("boom")

    async with core_with(handler) as core:
        with pytest.raises(OFSCNetworkError):
            await getattr(core, method)(*args, **kwargs)
