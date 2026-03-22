"""PII scrubbing for analytics properties and traits."""

from __future__ import annotations

import re
from typing import Any, FrozenSet, Optional, Set

from .base import IAnalyticsBackend

_DEFAULT_DENY_KEYS: FrozenSet[str] = frozenset(
    {
        "password",
        "secret",
        "token",
        "authorization",
        "credit_card",
        "ssn",
        "api_key",
    }
)

_EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
_PHONE_RE = re.compile(r"\b\+?\d[\d\s().-]{8,}\d\b")


def _scrub_scalar_key(key: str, v: Any, *, redact_keys: Optional[Set[str]], deny: Set[str]) -> Any:
    lk = key.lower()
    if any(d in lk for d in deny):
        return "[REDACTED]"
    if "email" in lk and isinstance(v, str):
        return "[REDACTED]"
    if "phone" in lk and isinstance(v, str):
        return "[REDACTED]"
    if isinstance(v, str):
        if _EMAIL_RE.search(v) or _PHONE_RE.search(v):
            return "[REDACTED]"
        return v
    if isinstance(v, dict):
        return scrub_pii_properties(v, redact_keys=redact_keys)
    return v


def scrub_pii_properties(
    data: Optional[dict[str, Any]],
    *,
    redact_keys: Optional[Set[str]] = None,
) -> dict[str, Any]:
    """Return a copy with sensitive keys and email/phone-like content redacted."""
    if not data:
        return {}
    deny: Set[str] = set(_DEFAULT_DENY_KEYS) | (redact_keys or set())
    out: dict[str, Any] = {}
    for k, v in data.items():
        out[k] = _scrub_scalar_key(k, v, redact_keys=redact_keys, deny=deny)
    return out


class ScrubbingAnalyticsBackend(IAnalyticsBackend):
    """Wrap a backend and scrub ``properties`` / ``traits`` before send."""

    def __init__(self, inner: IAnalyticsBackend, *, redact_keys: Optional[Set[str]] = None) -> None:
        self._inner = inner
        self._redact_keys = redact_keys

    def track(
        self,
        distinct_id: str,
        event_name: str,
        properties: Optional[dict[str, Any]] = None,
    ) -> None:
        self._inner.track(
            distinct_id,
            event_name,
            scrub_pii_properties(properties, redact_keys=self._redact_keys),
        )

    def identify(self, distinct_id: str, traits: Optional[dict[str, Any]] = None) -> None:
        self._inner.identify(
            distinct_id,
            scrub_pii_properties(traits, redact_keys=self._redact_keys),
        )

    def delete_user(self, distinct_id: str) -> None:
        self._inner.delete_user(distinct_id)
