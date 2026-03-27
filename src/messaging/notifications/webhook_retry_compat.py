"""Optional bridge to ``fast_webhooks.delivery.RetryPolicy``.

Keeps :mod:`fast_notifications.retry_policy` free of ``fast_webhooks`` imports at module load.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .retry_policy import NotificationRetryPolicy


def as_webhook_retry_policy(policy: "NotificationRetryPolicy") -> Any:
    """Convert to :class:`fast_webhooks.delivery.RetryPolicy` for ``deliver_webhook`` and friends.

    Requires the ``fastmvc-webhooks`` package.
    """
    try:
        from messaging.webhooks.delivery import RetryPolicy as WebhookRetryPolicy
    except ImportError as exc:  # pragma: no cover - exercised when webhooks missing
        raise ImportError(
            "fastmvc-webhooks is required for as_webhook_retry_policy(); "
            "install it or copy fields manually."
        ) from exc
    return WebhookRetryPolicy(
        max_attempts=policy.max_attempts,
        initial_delay_seconds=policy.initial_delay_seconds,
        backoff_factor=policy.backoff_factor,
        jitter_ratio=policy.jitter_ratio,
        retry_on_status=set(policy.retry_on_status),
    )
