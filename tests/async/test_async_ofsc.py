"""Tests for AsyncOFSC class."""

import pytest

from ofsc.async_client import AsyncOFSC


class TestAsyncOFSCContextManager:
    """Test AsyncOFSC context manager behavior."""

    @pytest.mark.asyncio
    async def test_context_manager_creates_client(self):
        """Test that entering context manager creates the client and sub-modules."""
        async with AsyncOFSC(
            clientID="test_client",
            companyName="test_company",
            secret="test_secret",
        ) as client:
            assert client._client is not None
            assert client._core is not None
            assert client._metadata is not None
            assert client._capacity is not None
            assert client._oauth is not None

    @pytest.mark.asyncio
    async def test_context_manager_closes_client(self):
        """Test that exiting context manager closes the client."""
        client = AsyncOFSC(
            clientID="test_client",
            companyName="test_company",
            secret="test_secret",
        )
        async with client:
            http_client = client._client
            assert http_client is not None

        # After exiting, client should be None
        assert client._client is None

    @pytest.mark.asyncio
    async def test_properties_accessible_in_context(self):
        """Test that properties are accessible inside context manager."""
        async with AsyncOFSC(
            clientID="test_client",
            companyName="test_company",
            secret="test_secret",
        ) as client:
            # These should not raise
            _ = client.core
            _ = client.metadata
            _ = client.capacity
            _ = client.oauth2
            _ = client.auto_model

    def test_properties_raise_outside_context(self):
        """Test that accessing properties outside context raises RuntimeError."""
        client = AsyncOFSC(
            clientID="test_client",
            companyName="test_company",
            secret="test_secret",
        )

        with pytest.raises(RuntimeError, match="must be used as async context manager"):
            _ = client.core

        with pytest.raises(RuntimeError, match="must be used as async context manager"):
            _ = client.metadata

        with pytest.raises(RuntimeError, match="must be used as async context manager"):
            _ = client.capacity

        with pytest.raises(RuntimeError, match="must be used as async context manager"):
            _ = client.oauth2


class TestAsyncOFSCConfiguration:
    """Test AsyncOFSC configuration."""

    @pytest.mark.asyncio
    async def test_constructor_signature_matches_sync(self):
        """Test that AsyncOFSC has the same constructor signature as OFSC."""
        # Test with all parameters
        async with AsyncOFSC(
            clientID="test_client",
            companyName="test_company",
            secret="test_secret",
            root="test_root",
            baseUrl="https://custom.url.com",
            useToken=False,
            enable_auto_raise=True,
            enable_auto_model=True,
        ) as client:
            assert client._config.clientID == "test_client"
            assert client._config.companyName == "test_company"
            assert client._config.secret == "test_secret"
            assert client._config.root == "test_root"
            assert client._config.baseURL == "https://custom.url.com"
            assert client._config.useToken is False
            assert client._config.auto_raise is True
            assert client._config.auto_model is True

    @pytest.mark.asyncio
    async def test_default_base_url(self):
        """Test that default base URL is constructed from company name."""
        async with AsyncOFSC(
            clientID="test_client",
            companyName="mycompany",
            secret="test_secret",
        ) as client:
            assert client._config.baseURL == "https://mycompany.fs.ocs.oraclecloud.com"

    @pytest.mark.asyncio
    async def test_auto_model_setter(self):
        """Test that auto_model setter propagates to sub-modules."""
        async with AsyncOFSC(
            clientID="test_client",
            companyName="test_company",
            secret="test_secret",
            enable_auto_model=True,
        ) as client:
            assert client.auto_model is True
            assert client.core.config.auto_model is True

            client.auto_model = False
            assert client.auto_model is False
            assert client.core.config.auto_model is False
            assert client.metadata.config.auto_model is False
            assert client.capacity.config.auto_model is False
            assert client.oauth2.config.auto_model is False

    @pytest.mark.asyncio
    async def test_str_representation(self):
        """Test string representation of AsyncOFSC."""
        async with AsyncOFSC(
            clientID="test_client",
            companyName="mycompany",
            secret="test_secret",
        ) as client:
            assert "AsyncOFSC" in str(client)
            assert "mycompany" in str(client)


class TestAsyncOFSCoreStubs:
    """Test that AsyncOFSCore methods raise NotImplementedError."""

    @pytest.mark.asyncio
    async def test_get_activities_not_implemented(self):
        async with AsyncOFSC(
            clientID="test", companyName="test", secret="test"
        ) as client:
            with pytest.raises(NotImplementedError):
                await client.core.get_activities({})

    @pytest.mark.asyncio
    async def test_get_resource_not_implemented(self):
        async with AsyncOFSC(
            clientID="test", companyName="test", secret="test"
        ) as client:
            with pytest.raises(NotImplementedError):
                await client.core.get_resource("resource_id")


class TestAsyncOFSMetadataStubs:
    """Test that AsyncOFSMetadata methods raise NotImplementedError."""

    @pytest.mark.asyncio
    async def test_get_workzones_not_implemented(self):
        async with AsyncOFSC(
            clientID="test", companyName="test", secret="test"
        ) as client:
            with pytest.raises(NotImplementedError):
                await client.metadata.get_workzones()

    @pytest.mark.asyncio
    async def test_get_properties_not_implemented(self):
        async with AsyncOFSC(
            clientID="test", companyName="test", secret="test"
        ) as client:
            with pytest.raises(NotImplementedError):
                await client.metadata.get_properties()


class TestAsyncOFSCapacityStubs:
    """Test that AsyncOFSCapacity methods raise NotImplementedError."""

    @pytest.mark.asyncio
    async def test_get_available_capacity_not_implemented(self):
        async with AsyncOFSC(
            clientID="test", companyName="test", secret="test"
        ) as client:
            with pytest.raises(NotImplementedError):
                await client.capacity.getAvailableCapacity(dates=["2025-01-01"])

    @pytest.mark.asyncio
    async def test_get_quota_not_implemented(self):
        async with AsyncOFSC(
            clientID="test", companyName="test", secret="test"
        ) as client:
            with pytest.raises(NotImplementedError):
                await client.capacity.getQuota(dates=["2025-01-01"])


class TestAsyncOFSOauth2Stubs:
    """Test that AsyncOFSOauth2 methods raise NotImplementedError."""

    @pytest.mark.asyncio
    async def test_get_token_not_implemented(self):
        async with AsyncOFSC(
            clientID="test", companyName="test", secret="test"
        ) as client:
            with pytest.raises(NotImplementedError):
                await client.oauth2.get_token()
