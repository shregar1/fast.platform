"""Tests for NotificationFanoutService."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from fast_platform.core.dtos.notifications import (
    EmailNotificationTarget,
    NotificationFanoutRequest,
    PushNotificationTarget,
)

from fast_platform.messaging.notifications.fanout import LoggingEmailSender, NotificationFanoutService
from tests.messaging.notifications.abstraction import INotificationTests


class TestFanoutService(INotificationTests):
    """Represents the TestFanoutService class."""

    def test_fanout_dispatch_email_only(self):
        """Execute test_fanout_dispatch_email_only operation.

        Returns:
            The result of the operation.
        """
        email = AsyncMock()
        with patch("fast_platform.messaging.notifications.fanout.PushNotificationService") as mock_push_cls:
            mock_push_cls.return_value = MagicMock()
            svc = NotificationFanoutService(email_sender=email)
            req = NotificationFanoutRequest(
                title="T", body="B", email=EmailNotificationTarget(to=["u@x.com"])
            )
            assert asyncio.run(svc.dispatch(req)) is True
        email.send_email.assert_awaited_once()

    def test_fanout_dispatch_push_only(self):
        """Execute test_fanout_dispatch_push_only operation.

        Returns:
            The result of the operation.
        """
        push = MagicMock()
        push.send_to_ios = AsyncMock()
        push.send_to_android = AsyncMock()
        with patch("fast_platform.messaging.notifications.fanout.PushNotificationService", return_value=push):
            svc = NotificationFanoutService(push=push)
            req = NotificationFanoutRequest(
                title="T",
                body="B",
                push=PushNotificationTarget(
                    ios_device_tokens=["a"], android_registration_tokens=["b"]
                ),
            )
            assert asyncio.run(svc.dispatch(req)) is True
        push.send_to_ios.assert_awaited_once()
        push.send_to_android.assert_awaited_once()

    def test_logging_email_sender(self):
        """Execute test_logging_email_sender operation.

        Returns:
            The result of the operation.
        """
        asyncio.run(
            LoggingEmailSender().send_email(to=["a@b.com"], subject="S", body_text="text", data={})
        )

    def test_fanout_dispatch_fcm_topic_only(self):
        """Execute test_fanout_dispatch_fcm_topic_only operation.

        Returns:
            The result of the operation.
        """
        push = MagicMock()
        push.send_to_ios = AsyncMock()
        push.send_to_android = AsyncMock()
        svc = NotificationFanoutService(push=push)
        req = NotificationFanoutRequest(
            title="T", body="B", push=PushNotificationTarget(fcm_topic="news")
        )
        assert asyncio.run(svc.dispatch(req)) is True
        push.send_to_ios.assert_not_called()
        push.send_to_android.assert_awaited_once()
