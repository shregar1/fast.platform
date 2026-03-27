"""Preference store + fan-out integration tests."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from fast_platform.core.dtos.notifications import EmailNotificationTarget, NotificationFanoutRequest

from fast_platform.messaging.notifications.fanout import NotificationFanoutService
from fast_platform.messaging.notifications.idempotency import InMemoryNotificationIdempotencyStore
from fast_platform.messaging.notifications.preferences import StaticMutedCategories
from tests.messaging.notifications.abstraction import INotificationTests


class TestPreferencesAndFanout(INotificationTests):
    """Represents the TestPreferencesAndFanout class."""

    def test_fanout_skips_muted_category(self):
        """Execute test_fanout_skips_muted_category operation.

        Returns:
            The result of the operation.
        """
        prefs = StaticMutedCategories({"u1": {"marketing"}})
        email = AsyncMock()
        with patch("fast_platform.messaging.notifications.fanout.PushNotificationService") as mock_push_cls:
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

    def test_fanout_idempotency_second_send_skipped(self):
        """Execute test_fanout_idempotency_second_send_skipped operation.

        Returns:
            The result of the operation.
        """
        store = InMemoryNotificationIdempotencyStore()
        email = AsyncMock()
        with patch("fast_platform.messaging.notifications.fanout.PushNotificationService") as mock_push_cls:
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

    def test_fanout_mute_checked_before_idempotency(self):
        """Muted users should not consume idempotency keys."""
        store = InMemoryNotificationIdempotencyStore()
        email = AsyncMock()
        prefs = StaticMutedCategories({"u1": {"alerts"}})
        with patch("fast_platform.messaging.notifications.fanout.PushNotificationService") as mock_push_cls:
            mock_push_cls.return_value = MagicMock()
            svc = NotificationFanoutService(
                email_sender=email, preference_store=prefs, idempotency_store=store
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
        req2 = NotificationFanoutRequest(
            title="T",
            body="B",
            email=EmailNotificationTarget(to=["u@x.com"]),
            user_id="u1",
            category="ok",
            template_id="t",
            dedupe_key="k",
        )
        with patch("fast_platform.messaging.notifications.fanout.PushNotificationService") as mock_push_cls:
            mock_push_cls.return_value = MagicMock()
            svc = NotificationFanoutService(
                email_sender=email, preference_store=prefs, idempotency_store=store
            )
            assert asyncio.run(svc.dispatch(req2)) is True
