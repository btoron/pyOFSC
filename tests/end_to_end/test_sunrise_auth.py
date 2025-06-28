import asyncio
import os

import pytest

from ofsc.client import OFSC
from ofsc.models.core import SubscriptionList, User, UserListResponse


@pytest.mark.live
class TestSunriseAuthentication:
    """Live authentication tests using OFSC client classes."""

    @pytest.fixture
    def live_credentials(self):
        """Get live credentials from environment variables."""
        instance = os.getenv("OFSC_INSTANCE")
        client_id = os.getenv("OFSC_CLIENT_ID")
        client_secret = os.getenv("OFSC_CLIENT_SECRET")

        if not all([instance, client_id, client_secret]):
            pytest.skip(
                "Live credentials not available. Set OFSC_INSTANCE, OFSC_CLIENT_ID, OFSC_CLIENT_SECRET"
            )

        return {
            "instance": instance,
            "client_id": client_id,
            "client_secret": client_secret,
        }

    @pytest.fixture
    def async_client_basic_auth(self, live_credentials):
        """Async OFSC client with Basic Auth for live testing."""
        return OFSC(
            instance=live_credentials["instance"],
            client_id=live_credentials["client_id"],
            client_secret=live_credentials["client_secret"],
            use_token=False,  # Use Basic Auth
        )

    def test_async_client(self, async_client_basic_auth: OFSC):
        async def test_async_client_basic_auth(async_client_basic_auth):
            async with async_client_basic_auth as client:
                # Test if the client can fetch subscriptions
                subscription_response: SubscriptionList = (
                    await client.core.get_subscriptions()
                )
                # Optionally, print the first subscriptio for debugging
                assert subscription_response.totalResults >= 0
                response: UserListResponse = await client.core.get_users()
                assert response.totalResults == 100
                for user in response.users:
                    assert isinstance(user, User)

        asyncio.run(test_async_client_basic_auth(async_client_basic_auth))
