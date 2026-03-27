"""Unit tests for :class:`NotificationRetryPolicy` (no webhooks required)."""

from fast_platform.messaging.notifications.retry_policy import NotificationRetryPolicy
from tests.messaging.notifications.abstraction import INotificationTests


class TestRetryPolicyCore(INotificationTests):
    """Represents the TestRetryPolicyCore class."""

    def test_notification_retry_policy_defaults(self):
        """Execute test_notification_retry_policy_defaults operation.

        Returns:
            The result of the operation.
        """
        n = NotificationRetryPolicy()
        assert n.max_attempts == 3
        assert n.initial_delay_seconds == 1.0
        assert n.backoff_factor == 2.0
        assert n.jitter_ratio == 0.0
        assert {408, 429, 500, 502, 503} == n.retry_on_status
