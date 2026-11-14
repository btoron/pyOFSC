"""Mocked tests for service requests (#127)."""

import json
from contextlib import asynccontextmanager
from datetime import date

import httpx
import pytest

from ofsc.async_client.core import AsyncOFSCore
from ofsc.exceptions import OFSCNetworkError, OFSCNotFoundError
from ofsc.models import OFSConfig, ServiceRequest, ServiceRequestCreate

BASE = "/rest/ofscCore/v1/serviceRequests"


@asynccontextmanager
async def core_with(handler):
    config = OFSConfig(clientID="fixture", companyName="fixture", secret="fixture", baseURL="https://fixture.invalid")
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        yield AsyncOFSCore(config, client)


async def test_create_service_request_model():
    def handler(request):
        assert request.method == "POST"
        assert request.url.path == BASE
        assert json.loads(request.content) == {"activityId": 5, "date": "2026-01-05", "requestType": "t", "custom": "x"}
        return httpx.Response(201, json={"requestId": 9, "activityId": 5, "created": "2026-01-05 10:00:00", "custom": "x"})

    async with core_with(handler) as core:
        result = await core.create_service_request(
            ServiceRequestCreate.model_validate({"activityId": 5, "date": date(2026, 1, 5), "requestType": "t", "custom": "x"})
        )
    assert isinstance(result, ServiceRequest)
    assert result.requestId == 9
    assert result.model_extra == {"custom": "x"}


async def test_create_service_request_dict():
    def handler(request):
        assert json.loads(request.content) == {"resourceId": "R1"}
        return httpx.Response(201, json={"requestId": 1, "resourceId": "R1"})

    async with core_with(handler) as core:
        assert (await core.create_service_request({"resourceId": "R1"})).resourceId == "R1"


async def test_get_service_request():
    def handler(request):
        assert request.method == "GET"
        assert request.url.path == f"{BASE}/9"
        return httpx.Response(200, json={"requestId": 9, "resourceInternalId": 3, "inventoryId": 4})

    async with core_with(handler) as core:
        result = await core.get_service_request(9)
    assert result.resourceInternalId == 3 and result.inventoryId == 4


async def test_get_service_request_property():
    def handler(request):
        assert request.url.path == f"{BASE}/9/my_file"
        assert request.headers["Accept"] == "image/png"
        return httpx.Response(200, content=b"\x89PNG")

    async with core_with(handler) as core:
        assert await core.get_service_request_property(9, "my_file", media_type="image/png") == b"\x89PNG"


async def test_get_service_request_property_default_accept():
    def handler(request):
        assert request.headers["Accept"] == "application/octet-stream"
        return httpx.Response(200, content=b"x")

    async with core_with(handler) as core:
        assert await core.get_service_request_property(9, "f") == b"x"


@pytest.mark.parametrize("call", ["get", "create", "prop"])
async def test_not_found(call):
    def handler(request):
        return httpx.Response(404, json={"type": "t", "title": "Not Found", "status": "404", "detail": "no"})

    async with core_with(handler) as core:
        with pytest.raises(OFSCNotFoundError):
            if call == "get":
                await core.get_service_request(1)
            elif call == "create":
                await core.create_service_request({"activityId": 1})
            else:
                await core.get_service_request_property(1, "f")


@pytest.mark.parametrize("call", ["get", "create", "prop"])
async def test_network_error(call):
    def handler(request):
        raise httpx.ConnectError("boom")

    async with core_with(handler) as core:
        with pytest.raises(OFSCNetworkError):
            if call == "get":
                await core.get_service_request(1)
            elif call == "create":
                await core.create_service_request({"activityId": 1})
            else:
                await core.get_service_request_property(1, "f")
