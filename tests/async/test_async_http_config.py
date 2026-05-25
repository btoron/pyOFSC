"""Tests for HTTPClientConfig and its wiring into AsyncOFSC."""

import httpx
import pytest
from pydantic import ValidationError

from ofsc.async_client import AsyncOFSC, HTTPClientConfig


COMMON_KWARGS = dict(
    clientID="test_client",
    companyName="test_company",
    secret="test_secret",
)


def _pool(client: httpx.AsyncClient):
    """Return the underlying connection pool of an httpx.AsyncClient."""
    return client._transport._pool


class TestHTTPClientConfigModel:
    """The config model itself is library-neutral and validates inputs."""

    def test_defaults_preserve_today_behavior(self):
        cfg = HTTPClientConfig()
        assert cfg.max_concurrency is None
        assert cfg.timeout is None
        assert cfg.max_retries == 0
        assert cfg.proxy is None
        assert cfg.verify_ssl is True
        assert cfg.http2 is True
        assert cfg.follow_redirects is False
        assert cfg.trust_env is True

    def test_rejects_zero_max_concurrency(self):
        with pytest.raises(ValidationError):
            HTTPClientConfig(max_concurrency=0)

    def test_rejects_negative_max_concurrency(self):
        with pytest.raises(ValidationError):
            HTTPClientConfig(max_concurrency=-1)

    def test_rejects_zero_timeout(self):
        with pytest.raises(ValidationError):
            HTTPClientConfig(timeout=0)

    def test_rejects_negative_timeout(self):
        with pytest.raises(ValidationError):
            HTTPClientConfig(timeout=-1.0)

    def test_rejects_negative_max_retries(self):
        with pytest.raises(ValidationError):
            HTTPClientConfig(max_retries=-1)

    def test_is_frozen(self):
        cfg = HTTPClientConfig()
        with pytest.raises(ValidationError):
            cfg.max_concurrency = 5  # type: ignore[misc]


class TestAsyncOFSCDefaultClient:
    """Without http_config, AsyncOFSC must construct the same client as before."""

    @pytest.mark.asyncio
    async def test_no_http_config_keeps_http2_on(self):
        async with AsyncOFSC(**COMMON_KWARGS) as client:
            assert _pool(client._client)._http2 is True

    @pytest.mark.asyncio
    async def test_no_http_config_keeps_default_timeout(self):
        async with AsyncOFSC(**COMMON_KWARGS) as client:
            # httpx default is 5s — leave it untouched
            assert client._client.timeout == httpx.Timeout(5.0)

    @pytest.mark.asyncio
    async def test_no_http_config_no_custom_transport(self):
        async with AsyncOFSC(**COMMON_KWARGS) as client:
            # Default transport is created by AsyncClient itself, not us
            assert _pool(client._client)._retries == 0


class TestMaxConcurrencyWiring:
    """max_concurrency must reach the connection pool."""

    @pytest.mark.asyncio
    async def test_max_concurrency_sets_pool_limits(self):
        async with AsyncOFSC(
            **COMMON_KWARGS,
            http_config=HTTPClientConfig(max_concurrency=5),
        ) as client:
            pool = _pool(client._client)
            assert pool._max_connections == 5
            assert pool._max_keepalive_connections == 5


class TestTimeoutWiring:
    @pytest.mark.asyncio
    async def test_timeout_applied(self):
        async with AsyncOFSC(
            **COMMON_KWARGS,
            http_config=HTTPClientConfig(timeout=30.0),
        ) as client:
            t = client._client.timeout
            assert t.connect == 30.0
            assert t.read == 30.0
            assert t.write == 30.0
            assert t.pool == 30.0


class TestHttp2Toggle:
    @pytest.mark.asyncio
    async def test_http2_off(self):
        async with AsyncOFSC(
            **COMMON_KWARGS,
            http_config=HTTPClientConfig(http2=False),
        ) as client:
            assert _pool(client._client)._http2 is False

    @pytest.mark.asyncio
    async def test_http2_off_with_retries(self):
        """http2 must still be respected when retries create a custom transport."""
        async with AsyncOFSC(
            **COMMON_KWARGS,
            http_config=HTTPClientConfig(http2=False, max_retries=2),
        ) as client:
            assert _pool(client._client)._http2 is False


class TestRetriesWiring:
    @pytest.mark.asyncio
    async def test_retries_routed_via_custom_transport(self):
        async with AsyncOFSC(
            **COMMON_KWARGS,
            http_config=HTTPClientConfig(max_retries=3),
        ) as client:
            assert _pool(client._client)._retries == 3


class TestPassthroughFlags:
    @pytest.mark.asyncio
    async def test_follow_redirects(self):
        async with AsyncOFSC(
            **COMMON_KWARGS,
            http_config=HTTPClientConfig(follow_redirects=True),
        ) as client:
            assert client._client.follow_redirects is True

    @pytest.mark.asyncio
    async def test_trust_env(self):
        async with AsyncOFSC(
            **COMMON_KWARGS,
            http_config=HTTPClientConfig(trust_env=False),
        ) as client:
            assert client._client.trust_env is False
