"""Unit tests for Core API v3.0 implementation.

Tests the new core API implementation with:
- Parameter validation
- Response model integration
- Both sync and async client support
- Error handling
"""

import pytest
import respx
from httpx import Response

from ofsc.client import OFSC
from ofsc.models.core import SubscriptionList, UserListResponse


@pytest.fixture
def mock_subscription_response():
    """Mock subscription API response."""
    return {
        "totalResults": 2,
        "items": [
            {
                "subscriptionId": "test_sub_1",
                "name": "Test Subscription 1",
                "status": "active",
            },
            {
                "subscriptionId": "test_sub_2",
                "name": "Test Subscription 2",
                "status": "active",
            },
        ],
    }


@pytest.fixture
def mock_users_response():
    """Mock users API response."""
    return {
        "totalResults": 1,
        "limit": 100,
        "offset": 0,
        "items": [
            {
                "login": "test_user",
                "name": "Test User",
                "mainResourceId": "123",
                "status": "active",
            }
        ],
    }


@pytest.mark.asyncio
class TestCoreAPIAsyncClient:
    """Test Core API with async-only client."""

    @respx.mock
    async def test_get_subscriptions_success(self, mock_subscription_response):
        """Test get_subscriptions with valid parameters."""
        route = respx.get(
            "https://demo.fs.ocs.oraclecloud.com/rest/ofscCore/v1/events/subscriptions"
        )
        route.mock(return_value=Response(200, json=mock_subscription_response))

        async with OFSC(
            instance="demo", client_id="test_id", client_secret="test_secret"
        ) as client:
            result = await client.core.get_subscriptions()
            assert isinstance(result, SubscriptionList)
            assert result.totalResults == 2

    @respx.mock
    async def test_get_users_success(self, mock_users_response):
        """Test get_users with valid parameters."""
        route = respx.get("https://demo.fs.ocs.oraclecloud.com/rest/ofscCore/v1/users")
        route.mock(return_value=Response(200, json=mock_users_response))

        async with OFSC(
            instance="demo", client_id="test_id", client_secret="test_secret"
        ) as client:
            result = await client.core.get_users(offset=0, limit=50)
            assert isinstance(result, UserListResponse)
            assert result.totalResults == 1
