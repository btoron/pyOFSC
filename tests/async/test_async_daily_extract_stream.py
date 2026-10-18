"""Daily extract streaming through the real httpx response lifecycle."""

import asyncio
import itertools
import json
from contextlib import asynccontextmanager

import httpx
import pytest

from ofsc.async_client import AsyncOFSC
from ofsc.exceptions import (
    OFSCApiError,
    OFSCAuthenticationError,
    OFSCAuthorizationError,
    OFSCNetworkError,
    OFSCNotFoundError,
    OFSCRateLimitError,
    OFSCServerError,
    OFSCValidationError,
)


class ProbeStream(httpx.AsyncByteStream):
    def __init__(self, chunks=(), read_error=None):
        self.chunks = chunks
        self.read_error = read_error
        self.yielded = 0
        self.closed = False

    async def __aiter__(self):
        for chunk in self.chunks:
            self.yielded += 1
            yield chunk
        if self.read_error is not None:
            raise self.read_error

    async def aclose(self):
        self.closed = True


@asynccontextmanager
async def stream_instance(source, status=200, enable_logging=False, handler=None):
    requests = []

    def handle(request):
        requests.append(request)
        if handler is not None:
            return handler(request)
        return httpx.Response(status, stream=source)

    async with AsyncOFSC(clientID="test", companyName="test", secret="test", enable_logging=enable_logging) as instance:
        # Preserve the public client's configured logging hooks while replacing
        # only its core transport. No tenant requests or credentials are used.
        async with httpx.AsyncClient(
            transport=httpx.MockTransport(handle),
            event_hooks=instance.core._client.event_hooks,
            trust_env=False,
        ) as transport:
            instance.core._client = transport
            yield instance, requests


@pytest.mark.parametrize("enable_logging", [False, True])
async def test_stream_is_lazy_even_with_logging_and_closes_on_early_exit(enable_logging):
    # An 80 MiB logical response allocates one reusable 8 KiB transport chunk.
    source = ProbeStream(itertools.repeat(b"x" * 8192, 10240))
    async with stream_instance(source, enable_logging=enable_logging) as (instance, requests):
        async with instance.core.get_daily_extract_file_stream("2024-01-15", "extract.zip") as chunks:
            assert source.yielded == 0
            assert not source.closed
            assert await anext(chunks) == b"x" * 8192
            assert source.yielded == 1
        assert source.closed
        assert not instance.core._client.is_closed
        (request,) = requests
        assert request.method == "GET"
        assert request.url.path == "/rest/ofscCore/v1/folders/dailyExtract/folders/2024-01-15/files/extract.zip"
        assert request.headers["Accept"] == "application/octet-stream"
        assert request.headers["Authorization"].startswith("Basic ")


async def test_stream_preserves_bytes_and_requested_chunk_boundaries():
    source = ProbeStream([b"abcd", b"efgh", b"ij"])
    async with stream_instance(source) as (instance, _):
        async with instance.core.get_daily_extract_file_stream("2024-01-15", "extract.zip", chunk_size=3) as stream:
            chunks = [chunk async for chunk in stream]
        assert chunks == [b"abc", b"def", b"ghi", b"j"]
        assert source.closed


async def test_empty_stream_is_closed():
    source = ProbeStream()
    async with stream_instance(source) as (instance, _):
        async with instance.core.get_daily_extract_file_stream("2024-01-15", "empty.zip") as stream:
            assert [chunk async for chunk in stream] == []
        assert source.closed


@pytest.mark.parametrize("chunk_size", [0, -1])
async def test_invalid_chunk_size_fails_before_request(chunk_size):
    async with stream_instance(ProbeStream()) as (instance, requests):
        with pytest.raises(ValueError, match="chunk_size"):
            async with instance.core.get_daily_extract_file_stream("2024-01-15", "extract.zip", chunk_size=chunk_size):
                pytest.fail("invalid size must not enter the download")
        assert requests == []


@pytest.mark.parametrize(
    "status, expected",
    [
        (400, OFSCValidationError),
        (401, OFSCAuthenticationError),
        (403, OFSCAuthorizationError),
        (404, OFSCNotFoundError),
        (429, OFSCRateLimitError),
        (500, OFSCServerError),
        (302, OFSCApiError),
    ],
)
async def test_http_error_body_is_read_for_existing_typed_errors(status, expected):
    error_data = {"type": "fixture-error", "title": "Download failed", "detail": "Fixture failure"}
    source = ProbeStream([json.dumps(error_data).encode()])
    async with stream_instance(source, status=status) as (instance, _):
        with pytest.raises(expected) as caught:
            async with instance.core.get_daily_extract_file_stream("2024-01-15", "extract.zip"):
                pytest.fail("an HTTP error must not expose a file stream")
        assert caught.value.status_code == status
        assert caught.value.detail == "Fixture failure"
        assert caught.value.title == "Download failed"
        assert caught.value.error_type == "fixture-error"
        assert source.closed


async def test_non_json_http_error_preserves_response_text():
    source = ProbeStream([b"service unavailable"])
    async with stream_instance(source, status=503) as (instance, _):
        with pytest.raises(OFSCServerError, match="service unavailable"):
            async with instance.core.get_daily_extract_file_stream("2024-01-15", "extract.zip"):
                pytest.fail("an HTTP error must not expose a file stream")
        assert source.closed


async def test_connection_error_is_translated():
    error = httpx.ConnectError("cannot connect")

    def fail(_request):
        raise error

    async with stream_instance(ProbeStream(), handler=fail) as (instance, _):
        with pytest.raises(OFSCNetworkError, match="cannot connect") as caught:
            async with instance.core.get_daily_extract_file_stream("2024-01-15", "extract.zip"):
                pytest.fail("a connection error must not expose a stream")
        assert caught.value.__cause__ is error


async def test_midstream_read_error_is_translated_and_closed():
    error = httpx.ReadError("connection lost")
    source = ProbeStream([b"first"], read_error=error)
    async with stream_instance(source) as (instance, _):
        with pytest.raises(OFSCNetworkError, match="connection lost") as caught:
            async with instance.core.get_daily_extract_file_stream("2024-01-15", "extract.zip", chunk_size=5) as chunks:
                assert await anext(chunks) == b"first"
                await anext(chunks)
        assert caught.value.__cause__ is error
        assert source.closed


async def test_error_response_read_failure_is_translated_and_closed():
    source = ProbeStream(read_error=httpx.ReadError("error body interrupted"))
    async with stream_instance(source, status=404) as (instance, _):
        with pytest.raises(OFSCNetworkError, match="error body interrupted"):
            async with instance.core.get_daily_extract_file_stream("2024-01-15", "extract.zip"):
                pytest.fail("an interrupted error response must not expose a stream")
        assert source.closed


async def test_consumer_transport_error_is_preserved_and_stream_closed():
    error = httpx.ReadError("consumer upload failed")
    source = ProbeStream([b"first", b"second"])
    async with stream_instance(source) as (instance, _):
        with pytest.raises(httpx.ReadError) as caught:
            async with instance.core.get_daily_extract_file_stream("2024-01-15", "extract.zip"):
                raise error
        assert caught.value is error
        assert source.closed


async def test_cancelling_iteration_closes_the_response():
    class WaitingStream(ProbeStream):
        def __init__(self):
            super().__init__()
            self.started = asyncio.Event()

        async def __aiter__(self):
            self.started.set()
            await asyncio.Event().wait()
            yield b"unreachable"

    source = WaitingStream()
    async with stream_instance(source) as (instance, _):

        async def download():
            async with instance.core.get_daily_extract_file_stream("2024-01-15", "extract.zip") as stream:
                async for _ in stream:
                    pass

        task = asyncio.create_task(download())
        try:
            await asyncio.wait_for(source.started.wait(), timeout=2)
        finally:
            task.cancel()
            with pytest.raises(asyncio.CancelledError):
                await task
        assert source.closed
