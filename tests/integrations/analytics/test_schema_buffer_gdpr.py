"""Module test_schema_buffer_gdpr.py."""

from __future__ import annotations

"""Schema registry, buffer/replay, GDPR hook, PII, rate limit."""
from typing import Any, List, Optional
from unittest.mock import MagicMock, patch

import jsonschema
import pytest

from integrations.analytics.buffer import BufferedAnalyticsBackend
from integrations.analytics.http_sink import HttpSinkAnalyticsBackend
from integrations.analytics.pii import ScrubbingAnalyticsBackend, scrub_pii_properties
from integrations.analytics.rate_limit import RateLimitedAnalyticsBackend
from integrations.analytics.schema_registry import EventSchemaRegistry, parse_versioned_event_name
from integrations.analytics.validating_backend import ValidatingAnalyticsBackend
from tests.integrations.analytics.abstraction import IAnalyticsTests


class _MemBackend:
    """Represents the _MemBackend class."""

    name = "mem"

    def __init__(self) -> None:
        """Execute __init__ operation."""
        self.tracks: List[tuple[str, str, Optional[dict[str, Any]]]] = []
        self.identifies: List[tuple[str, Optional[dict[str, Any]]]] = []
        self.deletes: List[str] = []

    def track(
        self, distinct_id: str, event_name: str, properties: Optional[dict[str, Any]] = None
    ) -> None:
        """Execute track operation.

        Args:
            distinct_id: The distinct_id parameter.
            event_name: The event_name parameter.
            properties: The properties parameter.

        Returns:
            The result of the operation.
        """
        self.tracks.append((distinct_id, event_name, properties))

    def identify(self, distinct_id: str, traits: Optional[dict[str, Any]] = None) -> None:
        """Execute identify operation.

        Args:
            distinct_id: The distinct_id parameter.
            traits: The traits parameter.

        Returns:
            The result of the operation.
        """
        self.identifies.append((distinct_id, traits))

    def delete_user(self, distinct_id: str) -> None:
        """Execute delete_user operation.

        Args:
            distinct_id: The distinct_id parameter.

        Returns:
            The result of the operation.
        """
        self.deletes.append(distinct_id)


class TestSchemaBufferGdpr(IAnalyticsTests):
    """Represents the TestSchemaBufferGdpr class."""

    def test_parse_versioned_event_name_ok(self) -> None:
        """Execute test_parse_versioned_event_name_ok operation.

        Returns:
            The result of the operation.
        """
        assert parse_versioned_event_name("purchase@1") == ("purchase", 1)
        assert parse_versioned_event_name("checkout.completed@2") == ("checkout.completed", 2)

    def test_parse_versioned_event_name_errors(self) -> None:
        """Execute test_parse_versioned_event_name_errors operation.

        Returns:
            The result of the operation.
        """
        with pytest.raises(ValueError, match="versioned"):
            parse_versioned_event_name("nover")
        with pytest.raises(ValueError, match="empty"):
            parse_versioned_event_name("@1")
        with pytest.raises(ValueError, match="invalid version"):
            parse_versioned_event_name("e@x")

    def test_registry_validate_properties(self) -> None:
        """Execute test_registry_validate_properties operation.

        Returns:
            The result of the operation.
        """
        reg = EventSchemaRegistry()
        reg.register(
            "purchase",
            1,
            {
                "type": "object",
                "properties": {"amount": {"type": "number"}},
                "required": ["amount"],
            },
        )
        reg.validate_properties("purchase@1", {"amount": 1.0})
        with pytest.raises(jsonschema.ValidationError):
            reg.validate_properties("purchase@1", {})

    def test_registry_require_registration(self) -> None:
        """Execute test_registry_require_registration operation.

        Returns:
            The result of the operation.
        """
        reg = EventSchemaRegistry(require_registration=True)
        with pytest.raises(ValueError, match="no schema"):
            reg.validate_properties("missing@1", {})

    def test_validating_backend_versioned(self) -> None:
        """Execute test_validating_backend_versioned operation.

        Returns:
            The result of the operation.
        """
        reg = EventSchemaRegistry()
        reg.register(
            "x", 1, {"type": "object", "properties": {"a": {"type": "string"}}, "required": ["a"]}
        )
        mem = _MemBackend()
        v = ValidatingAnalyticsBackend(mem, reg)
        v.track("u", "x@1", {"a": "ok"})
        assert len(mem.tracks) == 1
        with pytest.raises(jsonschema.ValidationError):
            v.track("u", "x@1", {})

    def test_validating_backend_unversioned_passthrough(self) -> None:
        """Execute test_validating_backend_unversioned_passthrough operation.

        Returns:
            The result of the operation.
        """
        reg = EventSchemaRegistry(require_registration=True)
        mem = _MemBackend()
        v = ValidatingAnalyticsBackend(mem, reg)
        v.track("u", "http.request", {"path": "/"})
        assert mem.tracks == [("u", "http.request", {"path": "/"})]

    def test_buffer_dry_run_and_replay(self) -> None:
        """Execute test_buffer_dry_run_and_replay operation.

        Returns:
            The result of the operation.
        """
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

    def test_buffer_forward_when_not_dry_run(self) -> None:
        """Execute test_buffer_forward_when_not_dry_run operation.

        Returns:
            The result of the operation.
        """
        mem = _MemBackend()
        buf = BufferedAnalyticsBackend(inner=mem, dry_run=False)
        buf.track("u", "evt", None)
        assert len(mem.tracks) == 1
        assert len(buf.list_buffered()) == 1

    def test_buffer_replay_requires_target(self) -> None:
        """Execute test_buffer_replay_requires_target operation.

        Returns:
            The result of the operation.
        """
        buf = BufferedAnalyticsBackend(inner=None, dry_run=True)
        buf.track("u", "e", {})
        with pytest.raises(ValueError, match="replay requires"):
            buf.replay(None)

    def test_scrub_pii(self) -> None:
        """Execute test_scrub_pii operation.

        Returns:
            The result of the operation.
        """
        d = scrub_pii_properties({"email": "a@b.com", "password": "x", "ok": 1})
        assert d["password"] == "[REDACTED]"
        assert "EMAIL" in d["email"] or d["email"] != "a@b.com"

    def test_scrubbing_backend_delegates_delete(self) -> None:
        """Execute test_scrubbing_backend_delegates_delete operation.

        Returns:
            The result of the operation.
        """
        mem = _MemBackend()
        s = ScrubbingAnalyticsBackend(mem)
        s.delete_user("uid")
        assert mem.deletes == ["uid"]

    def test_rate_limit_allows_delete_without_cap(self) -> None:
        """Execute test_rate_limit_allows_delete_without_cap operation.

        Returns:
            The result of the operation.
        """
        mem = _MemBackend()
        rl = RateLimitedAnalyticsBackend(mem, max_events_per_user_per_minute=0)
        for _ in range(5):
            rl.delete_user("u")
        assert len(mem.deletes) == 5

    @patch("urllib.request.urlopen")
    def test_http_sink_delete_user(self, mock_urlopen: MagicMock) -> None:
        """Execute test_http_sink_delete_user operation.

        Args:
            mock_urlopen: The mock_urlopen parameter.

        Returns:
            The result of the operation.
        """
        from urllib.request import Request

        mock_urlopen.return_value.read = MagicMock(return_value=b"")
        b = HttpSinkAnalyticsBackend("http://example.com/collect", api_key="k")
        b.delete_user("user-9")
        assert mock_urlopen.called
        req = mock_urlopen.call_args[0][0]
        assert isinstance(req, Request)
        assert req.get_full_url() == "http://example.com/collect/forget"
