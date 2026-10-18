"""Generic sync calls must deliver additionalHeaders to the HTTP endpoint."""

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

import pytest

from ofsc import OFSC


@pytest.fixture
def local_client():
    class EchoHandler(BaseHTTPRequestHandler):
        def do_POST(self):
            body = self.rfile.read(int(self.headers.get("Content-Length", "0")))
            payload = json.dumps(
                {
                    "path": self.path,
                    "headers": dict(self.headers),
                    "body": body.decode("utf-8"),
                }
            ).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), EchoHandler)
    thread = Thread(target=server.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True)
    thread.start()
    client = OFSC(
        clientID="fixture-client",
        companyName="fixture-company",
        secret="fixture-secret",
        baseUrl=f"http://127.0.0.1:{server.server_port}",
    )
    try:
        yield client
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
        assert not thread.is_alive()


@pytest.mark.parametrize(
    "extra",
    [
        {"Accept": "application/octet-stream"},
        {"Content-Type": "application/xml"},
        {"Authorization": "Bearer caller-fixture-token"},
        {"X-Fixture": "custom-header", "Accept": "text/plain"},
    ],
)
def test_call_delivers_additional_and_overridden_headers(local_client, extra):
    original = extra.copy()
    with local_client.core.call(
        method="POST",
        partialUrl="/rest/fixture",
        additionalHeaders=extra,
        params={"page": 2},
        data=b"fixture-body",
        timeout=5,
    ) as response:
        assert response.status_code == 200
        received = response.json()

    assert received["path"] == "/rest/fixture?page=2"
    assert received["body"] == "fixture-body"
    for name, value in extra.items():
        assert received["headers"][name] == value
    assert received["headers"]["Authorization"] == extra.get("Authorization", local_client.core.headers["Authorization"])
    assert received["headers"]["Content-Type"] == extra.get("Content-Type", "application/json;charset=UTF-8")
    assert extra == original


def test_custom_headers_do_not_leak_into_later_calls(local_client):
    with local_client.core.call(
        method="POST",
        partialUrl="/rest/fixture",
        additionalHeaders={"Accept": "application/octet-stream", "X-Fixture": "one-call"},
        timeout=5,
    ) as response:
        first = response.json()
    with local_client.core.call(method="POST", partialUrl="/rest/fixture", timeout=5) as response:
        second = response.json()
    assert first["headers"]["X-Fixture"] == "one-call"
    assert "X-Fixture" not in second["headers"]
    assert second["headers"]["Content-Type"] == "application/json;charset=UTF-8"
    assert second["headers"]["Authorization"] == local_client.core.headers["Authorization"]
    assert second["headers"]["Accept"] != "application/octet-stream"
