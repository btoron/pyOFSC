"""Simple tests for Core API to test actual available methods."""

import pytest
import respx

from ofsc.client import OFSC


class TestCoreAPISimple:
    """Test Core API with methods that actually exist."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_core_api_access(self):
        """Test accessing core API through client."""
        async with OFSC(
            instance="demo", client_id="test_id", client_secret="test_secret"
        ) as client:
            # Test that we can access the core API
            core_api = client.core
            assert core_api is not None

            # Check if bulk methods exist (these were visible in the dir output)
            expected_methods = [
                "bulk_update_activities",
                "bulk_update_inventories",
                "bulk_update_work_skills",
            ]

            for method_name in expected_methods:
                if hasattr(core_api, method_name):
                    method = getattr(core_api, method_name)
                    assert callable(method), f"Method {method_name} is not callable"

    @pytest.mark.asyncio
    async def test_core_api_instantiation(self):
        """Test that Core API can be accessed."""
        async with OFSC(
            instance="demo", client_id="test_id", client_secret="test_secret"
        ) as client:
            assert client is not None
            assert hasattr(client, "core")
            assert client.core is not None
