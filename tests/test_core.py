import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import ClassVar
from unittest.mock import patch

import pytest

from espncricinfo import _core


class _FlakyHandler(BaseHTTPRequestHandler):
    """Answer each path with the next status in ``plan``, then 200 JSON."""

    plan: ClassVar[dict[str, list[int]]] = {}
    hits: ClassVar[dict[str, int]] = {}

    def do_GET(self):
        self.hits[self.path] = self.hits.get(self.path, 0) + 1
        statuses = self.plan.get(self.path, [])
        status = statuses.pop(0) if statuses else 200
        body = json.dumps({"path": self.path}).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


@pytest.fixture
def server():
    _FlakyHandler.plan, _FlakyHandler.hits = {}, {}
    httpd = HTTPServer(("127.0.0.1", 0), _FlakyHandler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{httpd.server_port}"
    httpd.shutdown()
    httpd.server_close()


def test_transient_503_is_retried(server):
    _FlakyHandler.plan["/team"] = [503, 503]
    with patch.object(_core._RETRY, "backoff_factor", 0):
        data = _core.get_json(f"{server}/team", LookupError)
    assert data == {"path": "/team"}
    assert _FlakyHandler.hits["/team"] == 3


def test_404_is_not_retried(server):
    _FlakyHandler.plan["/missing"] = [404]
    with pytest.raises(LookupError, match="Not found"):
        _core.get_json(f"{server}/missing", LookupError)
    assert _FlakyHandler.hits["/missing"] == 1


def test_persistent_503_raises_after_retries(server):
    _FlakyHandler.plan["/down"] = [503] * 10
    with (
        patch.object(_core._RETRY, "backoff_factor", 0),
        pytest.raises(_core.requests.HTTPError),
    ):
        _core.get_json(f"{server}/down", LookupError)
    assert _FlakyHandler.hits["/down"] == 4


def test_http_get_sends_timeout_and_default_headers():
    with patch.object(_core._SESSION, "get") as get:
        _core.http_get("http://example.invalid/x")
    get.assert_called_once_with(
        "http://example.invalid/x", headers=_core.HEADERS, timeout=_core.TIMEOUT
    )
