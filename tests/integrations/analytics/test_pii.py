from __future__ import annotations

"""PII scrubbing."""
from typing import Any, Optional

from analytics.base import IAnalyticsBackend
from analytics.pii import ScrubbingAnalyticsBackend, scrub_pii_properties
from tests.integrations.analytics.abstraction import IAnalyticsTests


class MemBackend(IAnalyticsBackend):
    def __init__(self) -> None:
        self.last_props: Optional[dict[str, Any]] = None

    def track(
        self, distinct_id: str, event_name: str, properties: Optional[dict[str, Any]] = None
    ) -> None:
        self.last_props = dict(properties or {})

    def identify(self, distinct_id: str, traits: Optional[dict[str, Any]] = None) -> None:
        self.last_traits = dict(traits or {})


class TestPii(IAnalyticsTests):
    def test_scrub_keys_and_patterns(self) -> None:
        d = scrub_pii_properties(
            {
                "email": "x@y.com",
                "safe": "ok",
                "nested": {"phone": "555-123-4567"},
                "blob": "contact me at a@b.co",
            }
        )
        assert d["email"] == "[REDACTED]"
        assert d["safe"] == "ok"
        assert d["nested"]["phone"] == "[REDACTED]"
        assert d["blob"] == "[REDACTED]"

    def test_scrubbing_backend(self) -> None:
        inner = MemBackend()
        b = ScrubbingAnalyticsBackend(inner)
        b.track("u", "e", {"email": "secret@x.com", "k": 1})
        assert inner.last_props is not None
        assert inner.last_props["email"] == "[REDACTED]"
        assert inner.last_props["k"] == 1
