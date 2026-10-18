"""Synchronous extract streaming lifecycle and real HTTP coverage."""

import io
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest.mock import Mock

import pytest
import requests

from ofsc.core import OFSCore
from ofsc.exceptions import OFSAPIException
from ofsc.models import OFSConfig


class TrackedBody(io.BytesIO):
    def __init__(self, body=b"abcdefgh"):
        super().__init__(body)
        self.read_sizes = []
        self.bytes_read = 0

    def read(self, size=-1):
        self.read_sizes.append(size)
        chunk = super().read(size)
        self.bytes_read += len(chunk)
        return chunk

    def release_conn(self):
        self.close()


class StreamingResponse(requests.Response):
    @property
    def content(self):
        if self.status_code == 200:
            pytest.fail("A successful streaming response must not buffer .content")
        return super().content


@pytest.fixture
def core():
    return OFSCore(OFSConfig(clientID="client", secret="secret", companyName="tenant", baseURL="https://example.test"))


def response(status=200, body=b"abcdefgh"):
    result = StreamingResponse()
    result.status_code = status
    result.url = "https://example.test/extract"
    result.raw = TrackedBody(body)
    result.close = Mock(wraps=result.close)
    return result


def install_response(monkeypatch, result):
    get = Mock(return_value=result)
    monkeypatch.setattr("ofsc.core.requests.get", get)
    return get


def test_stream_is_lazy_and_passes_path_headers_and_timeout(core, monkeypatch):
    result = response()
    get = install_response(monkeypatch, result)
    manager = core.get_daily_extract_file_stream("2026-01-15", "extract.zip", timeout=(5, 30))
    get.assert_not_called()

    with manager as stream:
        assert stream is result
        assert result.raw.bytes_read == 0
        assert list(stream.iter_content(chunk_size=3)) == [b"abc", b"def", b"gh"]

    get.assert_called_once_with(
        "https://example.test/rest/ofscCore/v1/folders/dailyExtract/folders/2026-01-15/files/extract.zip",
        headers={
            "Content-Type": "application/json;charset=UTF-8",
            "Authorization": "Basic Y2xpZW50QHRlbmFudDpzZWNyZXQ=",
            "Accept": "application/octet-stream",
        },
        stream=True,
        timeout=(5, 30),
    )
    result.close.assert_called_once()
    assert result.raw.closed


def test_default_timeout_preserves_requests_behavior(core, monkeypatch):
    result = response()
    get = install_response(monkeypatch, result)
    with core.get_daily_extract_file_stream("2026-01-15", "extract.zip"):
        pass
    assert get.call_args.kwargs["timeout"] is None
    assert result.raw.bytes_read == 0
    assert result.raw.closed


def test_partial_consumption_does_not_read_the_remaining_large_extract(core, monkeypatch):
    class LargeBody(TrackedBody):
        remaining = 80 * 1024 * 1024

        def read(self, size=-1):
            assert size > 0, "Unbounded reads defeat streaming"
            self.read_sizes.append(size)
            count = min(size, self.remaining)
            self.remaining -= count
            self.bytes_read += count
            return b"x" * count

    result = response()
    result.raw = LargeBody(b"")
    install_response(monkeypatch, result)
    with core.get_daily_extract_file_stream("2026-01-15", "extract.zip") as stream:
        assert next(stream.iter_content(chunk_size=8192)) == b"x" * 8192
    assert result.raw.read_sizes == [8192]
    assert result.raw.bytes_read == 8192
    assert result.raw.closed


def test_consumer_exception_closes_response(core, monkeypatch):
    result = response()
    install_response(monkeypatch, result)
    with pytest.raises(RuntimeError, match="consumer failed"):
        with core.get_daily_extract_file_stream("2026-01-15", "extract.zip") as stream:
            assert next(stream.iter_content(chunk_size=2)) == b"ab"
            raise RuntimeError("consumer failed")
    result.close.assert_called_once()
    assert result.raw.closed


def test_read_exception_closes_response(core, monkeypatch):
    result = response()
    result.raw.read = Mock(side_effect=requests.exceptions.ChunkedEncodingError("truncated download"))
    install_response(monkeypatch, result)
    with pytest.raises(requests.exceptions.ChunkedEncodingError, match="truncated download"):
        with core.get_daily_extract_file_stream("2026-01-15", "extract.zip") as stream:
            next(stream.iter_content(chunk_size=2))
    result.close.assert_called_once()
    assert result.raw.closed


@pytest.mark.parametrize("error", [requests.ConnectionError("connection failed"), requests.ConnectTimeout("connection timed out")])
def test_connection_errors_propagate(core, monkeypatch, error):
    get = Mock(side_effect=error)
    monkeypatch.setattr("ofsc.core.requests.get", get)
    with pytest.raises(type(error), match=str(error)):
        with core.get_daily_extract_file_stream("2026-01-15", "extract.zip"):
            pytest.fail("Failed requests must not yield a response")


@pytest.mark.parametrize("status", [404, 503])
def test_ofsc_errors_raise_existing_exception_and_close(core, monkeypatch, status):
    body = json.dumps({"type": "error", "title": "Extract unavailable", "status": status, "detail": "Try another date"}).encode()
    result = response(status, body)
    install_response(monkeypatch, result)
    with pytest.raises(OFSAPIException) as error:
        with core.get_daily_extract_file_stream("2026-01-15", "extract.zip"):
            pytest.fail("HTTP errors must not yield a downloadable extract")
    assert error.value.status_code == status
    assert error.value.title == "Extract unavailable"
    assert error.value.detail == "Try another date"
    result.close.assert_called_once()
    assert result.raw.closed


@pytest.mark.parametrize("body", [b"<html>upstream unavailable</html>", b"[]"])
def test_non_ofsc_error_bodies_raise_http_error_and_close(core, monkeypatch, body):
    result = response(502, body)
    install_response(monkeypatch, result)
    with pytest.raises(requests.HTTPError) as error:
        with core.get_daily_extract_file_stream("2026-01-15", "extract.zip"):
            pytest.fail("HTTP errors must not yield a downloadable extract")
    assert error.value.response is result
    result.close.assert_called_once()
    assert result.raw.closed


@pytest.mark.parametrize("body", [b'{"status":404,"title":"Missing"}', b"not JSON"])
def test_auto_raise_false_yields_raw_error_response_without_reading(core, monkeypatch, body):
    core.config.auto_raise = False
    result = response(404, body)
    install_response(monkeypatch, result)
    with core.get_daily_extract_file_stream("2026-01-15", "extract.zip") as stream:
        assert stream.status_code == 404
        assert result.raw.bytes_read == 0
    assert result.raw.closed


def test_unexpected_success_status_is_not_silently_downloaded(core, monkeypatch):
    result = response(204, b"")
    install_response(monkeypatch, result)
    with pytest.raises(requests.HTTPError, match="204"):
        with core.get_daily_extract_file_stream("2026-01-15", "extract.zip"):
            pytest.fail("Daily extract downloads require HTTP 200")
    assert result.raw.closed


def test_buffered_api_still_returns_bytes(core, monkeypatch):
    result = requests.Response()
    result.status_code = 200
    result._content = b"buffered extract"
    get = install_response(monkeypatch, result)
    assert core.get_daily_extract_file("2026-01-15", "extract.zip") == b"buffered extract"
    assert "stream" not in get.call_args.kwargs


@pytest.mark.parametrize("use_token", [False, True])
def test_real_http_partial_read_does_not_wait_for_remaining_body(core, monkeypatch, use_token):
    release = threading.Event()
    observed = {}

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            observed["path"] = self.path
            observed["authorization"] = self.headers.get("Authorization")
            observed["accept"] = self.headers.get("Accept")
            self.send_response(200)
            self.send_header("Content-Length", "16")
            self.send_header("Content-Type", "application/octet-stream")
            self.end_headers()
            self.wfile.write(b"abcdefgh")
            self.wfile.flush()
            release.wait(5)
            try:
                self.wfile.write(b"ijklmnop")
            except (BrokenPipeError, ConnectionResetError):
                pass

        def log_message(self, *_args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()
    core.config.baseURL = f"http://127.0.0.1:{server.server_port}"
    core.config.useToken = use_token
    token = requests.Response()
    token._content = b'{"access_token":"test-token"}'
    monkeypatch.setattr(core, "token", Mock(return_value=token))
    try:
        with core.get_daily_extract_file_stream("2026-01-15", "extract.zip", timeout=2) as stream:
            assert stream._content is False
            assert next(stream.iter_content(chunk_size=4)) == b"abcd"
            assert not release.is_set()
            assert observed["path"] == "/rest/ofscCore/v1/folders/dailyExtract/folders/2026-01-15/files/extract.zip"
            assert observed["authorization"] == ("Bearer test-token" if use_token else "Basic Y2xpZW50QHRlbmFudDpzZWNyZXQ=")
            assert observed["accept"] == "application/octet-stream"
        assert stream.raw.closed
    finally:
        release.set()
        server.shutdown()
        server.server_close()
        worker.join(timeout=5)
