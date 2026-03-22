"""Schema registry, buffer/replay, GDPR hook, PII, rate limit."""

from __future__ import annotations

from typing import Any, List, Optional
from unittest.mock import MagicMock, patch

import pytest
import jsonschema

from analytics.buffer import BufferedAnalyticsBackend
from analytics.http_sink import HttpSinkAnalyticsBackend
from analytics.pii import ScrubbingAnalyticsBackend, scrub_pii_properties
from analytics.rate_limit import RateLimitedAnalyticsBackend
from analytics.schema_registry import EventSchemaRegistry, parse_versioned_event_name
from analytics.validating_backend import ValidatingAnalyticsBackend


def test_parse_versioned_event_name_ok() -> None:
    assert parse_versioned_event_name("purchase@1") == ("purchase", 1)
    assert parse_versioned_event_name("checkout.completed@2") == ("checkout.completed", 2)


def test_parse_versioned_event_name_errors() -> None:
    with pytest.raises(ValueError, match="versioned"):
        parse_versioned_event_name("nover")
    with pytest.raises(ValueError, match="empty"):
        parse_versioned_event_name("@1")
    with pytest.raises(ValueError, match="invalid version"):
        parse_versioned_event_name("e@x")


def test_registry_validate_properties() -> None:
    reg = EventSchemaRegistry()
    reg.register("purchase", 1, {
        "type": "object",
        "properties": {"amount": {"type": "number"}},
        "required": ["amount"],
    })
    reg.validate_properties("purchase@1", {"amount": 1.0})
    with pytest.raises(jsonschema.ValidationError):
        reg.validate_properties("purchase@1", {})


def test_registry_require_registration() -> None:
    reg = EventSchemaRegistry(require_registration=True)
    with pytest.raises(ValueError, match="no schema"):
        reg.validate_properties("missing@1", {})


class _MemBackend:
    name = "mem"

    def __init__(self) -> None:
        self.tracks: List[tuple[str, str, Optional[dict[str, Any]]]] = []
        self.identifies: List[tuple[str, Optional[dict[str, Any]]]] = []
        self.deletes: List[str] = []

    def track(self, distinct_id: str, event_name: str, properties: Optional[dict[str, Any]] = None) -> None:
        self.tracks.append((distinct_id, event_name, properties))

    def identify(self, distinct_id: str, traits: Optional[dict[str, Any]] = None) -> None:
        self.identifies.append((distinct_id, traits))

    def delete_user(self, distinct_id: str) -> None:
        self.deletes.append(distinct_id)


def test_validating_backend_versioned() -> None:
    reg = EventSchemaRegistry()
    reg.register("x", 1, {"type": "object", "properties": {"a": {"type": "string"}}, "required": ["a"]})
    mem = _MemBackend()
    v = ValidatingAnalyticsBackend(mem, reg)
    v.track("u", "x@1", {"a": "ok"})
    assert len(mem.tracks) == 1
    with pytest.raises(jsonschema.ValidationError):
        v.track("u", "x@1", {})


def test_validating_backend_unversioned_passthrough() -> None:
    reg = EventSchemaRegistry(require_registration=True)
    mem = _MemBackend()
    v = ValidatingAnalyticsBackend(mem, reg)
    v.track("u", "http.request", {"path": "/"})
    assert mem.tracks == [("u", "http.request", {"path": "/"})]


def test_buffer_dry_run_and_replay() -> None:
    mem = _MemBackend()
    buf = BufferedAnalyticsBackend(inner=None, dry_run=True)
    buf.track("u1", "e@1", {"k": 1})
    buf.identify("u1", {"name": "x"})
    buf.delete_user("u1")
    assert len(mem.tracks) == 0
    assert len(buf.list_buffered()) == 3
    buf.replay(mem)
    assert len(mem.tracks) == 1
    assert mem.identifies == [("u1", {"name": "x"})]
    assert mem.deletes == ["u1"]
    assert buf.list_buffered() == []


def test_buffer_forward_when_not_dry_run() -> None:
    mem = _MemBackend()
    buf = BufferedAnalyticsBackend(inner=mem, dry_run=False)
    buf.track("u", "evt", None)
    assert len(mem.tracks) == 1
    assert len(buf.list_buffered()) == 1


def test_buffer_replay_requires_target() -> None:
    buf = BufferedAnalyticsBackend(inner=None, dry_run=True)
    buf.track("u", "e", {})
    with pytest.raises(ValueError, match="replay requires"):
        buf.replay(None)


def test_scrub_pii() -> None:
    d = scrub_pii_properties({"email": "a@b.com", "password": "x", "ok": 1})
    assert d["password"] == "[REDACTED]"
    assert "EMAIL" in d["email"] or d["email"] != "a@b.com"


def test_scrubbing_backend_delegates_delete() -> None:
    mem = _MemBackend()
    s = ScrubbingAnalyticsBackend(mem)
    s.delete_user("uid")
    assert mem.deletes == ["uid"]


def test_rate_limit_allows_delete_without_cap() -> None:
    mem = _MemBackend()
    rl = RateLimitedAnalyticsBackend(mem, max_events_per_user_per_minute=0)
    for _ in range(5):
        rl.delete_user("u")
    assert len(mem.deletes) == 5


@patch("urllib.request.urlopen")
def test_http_sink_delete_user(mock_urlopen: MagicMock) -> None:
    from urllib.request import Request

    mock_urlopen.return_value.read = MagicMock(return_value=b"")
    b = HttpSinkAnalyticsBackend("http://example.com/collect", api_key="k")
    b.delete_user("user-9")
    assert mock_urlopen.called
    req = mock_urlopen.call_args[0][0]
    assert isinstance(req, Request)
    assert req.get_full_url() == "http://example.com/collect/forget"
