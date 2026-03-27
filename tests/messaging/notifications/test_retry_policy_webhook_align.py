"""Alignment tests with :mod:`webhooks` (optional dependency in dev/CI)."""

import pytest

pytest.importorskip("webhooks")

from fast_platform.messaging.notifications import NotificationRetryPolicy, as_webhook_retry_policy
from tests.messaging.notifications.abstraction import INotificationTests


class TestRetryPolicyWebhookAlign(INotificationTests):
    """Represents the TestRetryPolicyWebhookAlign class."""

    def test_notification_retry_policy_defaults_match_webhooks(self):
        """Execute test_notification_retry_policy_defaults_match_webhooks operation.

        Returns:
            The result of the operation.
        """
        from messaging.webhooks.delivery import RetryPolicy as W

        n = NotificationRetryPolicy()
        w = W()
        assert n.max_attempts == w.max_attempts
        assert n.initial_delay_seconds == w.initial_delay_seconds
        assert n.backoff_factor == w.backoff_factor
        assert n.jitter_ratio == w.jitter_ratio
        assert n.retry_on_status == w.retry_on_status

    def test_from_webhook_retry_policy(self):
        """Execute test_from_webhook_retry_policy operation.

        Returns:
            The result of the operation.
        """
        from messaging.webhooks.delivery import RetryPolicy as W

        w = W(max_attempts=5, jitter_ratio=0.1)
        n = NotificationRetryPolicy.from_webhook_retry_policy(w)
        assert n.max_attempts == 5
        assert n.jitter_ratio == 0.1

    def test_as_webhook_retry_policy_roundtrip(self):
        """Execute test_as_webhook_retry_policy_roundtrip operation.

        Returns:
            The result of the operation.
        """
        n = NotificationRetryPolicy(max_attempts=2)
        w = as_webhook_retry_policy(n)
        assert w.max_attempts == 2
