"""
Retry policy shape aligned with ``fast_webhooks.delivery.RetryPolicy`` (same fields/defaults).

Use :mod:`fast_notifications.webhook_retry_compat` for conversion to/from webhook types.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Collection, Protocol, Set


class _RetryPolicyLike(Protocol):
    max_attempts: int
    initial_delay_seconds: float
    backoff_factor: float
    jitter_ratio: float
    retry_on_status: Collection[int]


@dataclass
class NotificationRetryPolicy:
    """
    Mirrors ``fast_webhooks.delivery.RetryPolicy`` so notification pipelines can share
    retry configuration with webhook delivery or serialize the same shape in config.
    """

    max_attempts: int = 3
    initial_delay_seconds: float = 1.0
    backoff_factor: float = 2.0
    #: If > 0, each sleep is multiplied by ``uniform(1 - jitter_ratio, 1 + jitter_ratio)``.
    jitter_ratio: float = 0.0
    retry_on_status: Set[int] = field(default_factory=lambda: {408, 429, 500, 502, 503})

    @classmethod
    def from_webhook_retry_policy(cls, policy: _RetryPolicyLike) -> "NotificationRetryPolicy":
        """Build from any object with the same fields (e.g. ``fast_webhooks`` ``RetryPolicy``)."""
        return cls(
            max_attempts=policy.max_attempts,
            initial_delay_seconds=policy.initial_delay_seconds,
            backoff_factor=policy.backoff_factor,
            jitter_ratio=policy.jitter_ratio,
            retry_on_status=set(policy.retry_on_status),
        )
