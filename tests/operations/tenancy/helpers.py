"""Shared helpers for tenancy tests (not a test module)."""

from __future__ import annotations

from starlette.requests import Request


def make_request(host: str, path: str = "/", extra_headers: dict | None = None) -> Request:
    """Execute make_request operation.

    Args:
        host: The host parameter.
        path: The path parameter.
        extra_headers: The extra_headers parameter.

    Returns:
        The result of the operation.
    """
    h = {"host": host}
    if extra_headers:
        h.update(extra_headers)
    hdrs = [(k.lower().encode("latin-1"), str(v).encode("latin-1")) for k, v in h.items()]
    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "GET",
        "path": path,
        "raw_path": path.encode("utf-8"),
        "root_path": "",
        "scheme": "http",
        "query_string": b"",
        "headers": hdrs,
        "client": ("127.0.0.1", 12345),
        "server": ("testserver", 80),
    }
    return Request(scope)
