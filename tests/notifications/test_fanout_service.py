"""Tests for NotificationFanoutService."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from notifications.dto import (
    EmailNotificationTarget,
    NotificationFanoutRequest,
    PushNotificationTarget,
)
from notifications.fanout import LoggingEmailSender, NotificationFanoutService


def test_fanout_dispatch_email_only():
    email = AsyncMock()
    with patch("notifications.fanout.PushNotificationService") as mock_push_cls:
        mock_push_cls.return_value = MagicMock()
        svc = NotificationFanoutService(email_sender=email)
        req = NotificationFanoutRequest(
            title="T",
            body="B",
            email=EmailNotificationTarget(to=["u@x.com"]),
        )
        assert asyncio.run(svc.dispatch(req)) is True
    email.send_email.assert_awaited_once()


def test_fanout_dispatch_push_only():
    push = MagicMock()
    push.send_to_ios = AsyncMock()
    push.send_to_android = AsyncMock()
    with patch("notifications.fanout.PushNotificationService", return_value=push):
        svc = NotificationFanoutService(push=push)
        req = NotificationFanoutRequest(
            title="T",
            body="B",
            push=PushNotificationTarget(
                ios_device_tokens=["a"],
                android_registration_tokens=["b"],
            ),
        )
        assert asyncio.run(svc.dispatch(req)) is True
    push.send_to_ios.assert_awaited_once()
    push.send_to_android.assert_awaited_once()


def test_logging_email_sender():
    asyncio.run(
        LoggingEmailSender().send_email(
            to=["a@b.com"],
            subject="S",
            body_text="text",
            data={},
        )
    )


def test_fanout_dispatch_fcm_topic_only():
    push = MagicMock()
    push.send_to_ios = AsyncMock()
    push.send_to_android = AsyncMock()
    svc = NotificationFanoutService(push=push)
    req = NotificationFanoutRequest(
        title="T",
        body="B",
        push=PushNotificationTarget(fcm_topic="news"),
    )
    assert asyncio.run(svc.dispatch(req)) is True
    push.send_to_ios.assert_not_called()
    push.send_to_android.assert_awaited_once()
