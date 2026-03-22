"""Tests for push notification service."""

import asyncio
from unittest.mock import MagicMock, patch


@patch("fast_notifications.push.PushConfiguration")
def test_push_service_apns_disabled(mock_cfg_cls):
    from fast_notifications.push import PushNotificationService
    mock_cfg = MagicMock()
    mock_cfg.get_config.return_value = MagicMock(
        apns=MagicMock(enabled=False),
        fcm=MagicMock(enabled=False),
    )
    mock_cfg_cls.return_value = mock_cfg
    svc = PushNotificationService()
    assert svc.apns_enabled is False
    assert svc.fcm_enabled is False
    asyncio.run(svc.send_to_ios(["token"], "t", "b"))  # no-op when disabled


@patch("fast_notifications.push.PushConfiguration")
def test_push_service_apns_enabled(mock_cfg_cls):
    from fast_notifications.push import PushNotificationService
    mock_cfg = MagicMock()
    mock_cfg.get_config.return_value = MagicMock(
        apns=MagicMock(enabled=True),
        fcm=MagicMock(enabled=False),
    )
    mock_cfg_cls.return_value = mock_cfg
    svc = PushNotificationService()
    assert svc.apns_enabled is True
    asyncio.run(svc.send_to_ios(["t1"], "Title", "Body"))
    asyncio.run(svc.send_to_android(["r1"], "T", "B"))
