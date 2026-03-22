"""
Versioned JSON envelope for ``QueueMessage.body`` with optional priority,
visibility delay, and poison-message (retry) metadata.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, replace
from typing import Any, Dict, Optional

ENVELOPE_VERSION_KEY = "envelope_version"
PAYLOAD_KEY = "payload"
PRIORITY_KEY = "priority"
DELAY_SECONDS_KEY = "delay_seconds"
FAILURE_COUNT_KEY = "failure_count"
LAST_ERROR_KEY = "last_error"


@dataclass
class QueueMessageEnvelope:
    """
    Structured payload for queue bodies.

    - **priority** — optional integer; higher values are processed first when workers
      sort by priority (backend-specific; see README).
    - **delay_seconds** — optional delay before the message becomes visible /
      deliverable (scheduled visibility).
    - **failure_count** / **last_error** — updated by workers when handling fails;
      use with :func:`should_quarantine` after ``N`` attempts.
    """

    envelope_version: int = 1
    payload: Dict[str, Any] = field(default_factory=dict)
    priority: Optional[int] = None
    delay_seconds: Optional[int] = None
    failure_count: int = 0
    last_error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        out: Dict[str, Any] = {
            ENVELOPE_VERSION_KEY: self.envelope_version,
            PAYLOAD_KEY: self.payload,
            FAILURE_COUNT_KEY: self.failure_count,
        }
        if self.priority is not None:
            out[PRIORITY_KEY] = self.priority
        if self.delay_seconds is not None:
            out[DELAY_SECONDS_KEY] = self.delay_seconds
        if self.last_error is not None:
            out[LAST_ERROR_KEY] = self.last_error
        return out

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> QueueMessageEnvelope:
        if not isinstance(data, dict):
            raise ValueError("envelope root must be a JSON object")
        ver = int(data.get(ENVELOPE_VERSION_KEY, 1))
        payload = data.get(PAYLOAD_KEY)
        if payload is None:
            payload = {}
        if not isinstance(payload, dict):
            raise ValueError("payload must be an object")
        priority = data.get(PRIORITY_KEY)
        if priority is not None:
            priority = int(priority)
        delay = data.get(DELAY_SECONDS_KEY)
        if delay is not None:
            delay = int(delay)
        fc = int(data.get(FAILURE_COUNT_KEY, 0))
        le = data.get(LAST_ERROR_KEY)
        if le is not None:
            le = str(le)
        return cls(
            envelope_version=ver,
            payload=payload,
            priority=priority,
            delay_seconds=delay,
            failure_count=fc,
            last_error=le,
        )

    def to_json_bytes(self) -> bytes:
        return json.dumps(self.to_dict(), separators=(",", ":"), ensure_ascii=False).encode("utf-8")

    @classmethod
    def from_json_bytes(cls, raw: bytes) -> QueueMessageEnvelope:
        data = json.loads(raw.decode("utf-8"))
        return cls.from_dict(data)

    def with_processing_failure(self, error: str) -> QueueMessageEnvelope:
        """Increment ``failure_count`` and set ``last_error`` (immutable copy)."""
        return replace(
            self,
            failure_count=self.failure_count + 1,
            last_error=error[:8000] if error else None,
        )

    def should_quarantine(self, max_failures: int) -> bool:
        """
        Return True when ``failure_count`` has reached ``max_failures``.

        Typical use: after each failed attempt, call ``with_processing_failure``;
        if ``should_quarantine(N)``, route to the quarantine queue instead of retry/DLQ.
        """
        if max_failures < 1:
            return False
        return self.failure_count >= max_failures


def should_quarantine(failure_count: int, max_failures: int) -> bool:
    """Stateless check: quarantine when ``failure_count >= max_failures`` (``max_failures >= 1``)."""
    if max_failures < 1:
        return False
    return failure_count >= max_failures
