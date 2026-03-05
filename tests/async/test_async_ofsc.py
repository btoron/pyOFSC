"""Tests for AsyncOFSC class."""

import logging

import httpx
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


class TestAsyncOFSCLogging:
    """Test AsyncOFSC event hook logging."""

    @pytest.mark.asyncio
    async def test_logging_disabled_by_default(self):
        """Test that logging is disabled by default."""
        client = AsyncOFSC(
            clientID="test_client",
            companyName="test_company",
            secret="test_secret",
        )
        assert client._enable_logging is False

    @pytest.mark.asyncio
    async def test_logging_enabled_creates_event_hooks(self):
        """Test that enabling logging configures httpx event hooks."""
        async with AsyncOFSC(
            clientID="test_client",
            companyName="test_company",
            secret="test_secret",
            enable_logging=True,
        ) as client:
            assert len(client._client.event_hooks["request"]) == 1
            assert len(client._client.event_hooks["response"]) == 1

    @pytest.mark.asyncio
    async def test_logging_disabled_no_event_hooks(self):
        """Test that disabling logging results in no custom event hooks."""
        async with AsyncOFSC(
            clientID="test_client",
            companyName="test_company",
            secret="test_secret",
            enable_logging=False,
        ) as client:
            assert len(client._client.event_hooks["request"]) == 0
            assert len(client._client.event_hooks["response"]) == 0

    @pytest.mark.asyncio
    async def test_request_hook_logs_at_debug(self, caplog):
        """Test that request hook logs at DEBUG level."""
        async with AsyncOFSC(
            clientID="test_client",
            companyName="test_company",
            secret="test_secret",
            enable_logging=True,
        ) as client:
            hook = client._client.event_hooks["request"][0]
            request = client._client.build_request("GET", "https://example.com/test")
            with caplog.at_level(logging.DEBUG, logger="ofsc.async_client"):
                await hook(request)
            assert "Request: GET https://example.com/test" in caplog.text

    @pytest.mark.asyncio
    async def test_response_hook_logs_at_debug(self, caplog):
        """Test that response hook logs at DEBUG level for successful responses."""
        async with AsyncOFSC(
            clientID="test_client",
            companyName="test_company",
            secret="test_secret",
            enable_logging=True,
        ) as client:
            hook = client._client.event_hooks["response"][0]
            request = client._client.build_request("GET", "https://example.com/test")
            response = httpx.Response(200, request=request)
            with caplog.at_level(logging.DEBUG, logger="ofsc.async_client"):
                await hook(response)
            assert "Response: GET https://example.com/test 200" in caplog.text

    @pytest.mark.asyncio
    async def test_response_hook_warns_on_http_error(self, caplog):
        """Test that response hook logs a WARNING for 4xx/5xx status codes."""
        async with AsyncOFSC(
            clientID="test_client",
            companyName="test_company",
            secret="test_secret",
            enable_logging=True,
        ) as client:
            hook = client._client.event_hooks["response"][0]
            request = client._client.build_request("GET", "https://example.com/test")
            response = httpx.Response(404, request=request)
            with caplog.at_level(logging.DEBUG, logger="ofsc.async_client"):
                await hook(response)
            assert "HTTP error: GET https://example.com/test 404" in caplog.text
            warning_records = [r for r in caplog.records if r.levelno == logging.WARNING]
            assert len(warning_records) == 1


class TestAsyncOFSMetadataStubs:
    """Test that AsyncOFSMetadata stub methods raise NotImplementedError."""

    # Note: get_properties is now implemented, see test_async_properties.py
    pass


class TestAsyncOFSCapacityStubs:
    """Test that AsyncOFSCapacity methods are implemented (not stubs)."""

    # Note: get_available_capacity and get_quota are now implemented,
    # see tests/async/test_async_capacity.py
    pass


class TestAsyncOFSOauth2Stubs:
    """Test that AsyncOFSOauth2 methods are implemented (not stubs)."""

    # Note: get_token is now implemented, see tests/async/test_async_oauth.py
    pass
