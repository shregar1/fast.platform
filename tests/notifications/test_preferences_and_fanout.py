"""Preference store + fan-out integration tests."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from fast_notifications.dto import EmailNotificationTarget, NotificationFanoutRequest
from fast_notifications.fanout import NotificationFanoutService
from fast_notifications.idempotency import InMemoryNotificationIdempotencyStore
from fast_notifications.preferences import StaticMutedCategories


def test_fanout_skips_muted_category():
    prefs = StaticMutedCategories({"u1": {"marketing"}})
    email = AsyncMock()
    with patch("fast_notifications.fanout.PushNotificationService") as mock_push_cls:
        mock_push_cls.return_value = MagicMock()
        svc = NotificationFanoutService(email_sender=email, preference_store=prefs)
        req = NotificationFanoutRequest(
            title="T",
            body="B",
            email=EmailNotificationTarget(to=["u@x.com"]),
            user_id="u1",
            category="marketing",
        )
        assert asyncio.run(svc.dispatch(req)) is False
    email.send_email.assert_not_called()


def test_fanout_idempotency_second_send_skipped():
    store = InMemoryNotificationIdempotencyStore()
    email = AsyncMock()
    with patch("fast_notifications.fanout.PushNotificationService") as mock_push_cls:
        mock_push_cls.return_value = MagicMock()
        svc = NotificationFanoutService(email_sender=email, idempotency_store=store)
        req = NotificationFanoutRequest(
            title="T",
            body="B",
            email=EmailNotificationTarget(to=["u@x.com"]),
            user_id="u1",
            template_id="welcome",
            dedupe_key="evt-1",
        )
        assert asyncio.run(svc.dispatch(req)) is True
        assert asyncio.run(svc.dispatch(req)) is False
    assert email.send_email.await_count == 1


def test_fanout_mute_checked_before_idempotency():
    """Muted users should not consume idempotency keys."""
    store = InMemoryNotificationIdempotencyStore()
    email = AsyncMock()
    prefs = StaticMutedCategories({"u1": {"alerts"}})
    with patch("fast_notifications.fanout.PushNotificationService") as mock_push_cls:
        mock_push_cls.return_value = MagicMock()
        svc = NotificationFanoutService(
            email_sender=email,
            preference_store=prefs,
            idempotency_store=store,
        )
        req = NotificationFanoutRequest(
            title="T",
            body="B",
            email=EmailNotificationTarget(to=["u@x.com"]),
            user_id="u1",
            category="alerts",
            template_id="t",
            dedupe_key="k",
        )
        assert asyncio.run(svc.dispatch(req)) is False
    email.send_email.assert_not_called()

    # Same key should still be acquirable for a non-muted send (different category / user).
    req2 = NotificationFanoutRequest(
        title="T",
        body="B",
        email=EmailNotificationTarget(to=["u@x.com"]),
        user_id="u1",
        category="ok",
        template_id="t",
        dedupe_key="k",
    )
    with patch("fast_notifications.fanout.PushNotificationService") as mock_push_cls:
        mock_push_cls.return_value = MagicMock()
        svc = NotificationFanoutService(
            email_sender=email,
            preference_store=prefs,
            idempotency_store=store,
        )
        assert asyncio.run(svc.dispatch(req2)) is True
