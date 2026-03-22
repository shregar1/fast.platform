"""Preference store + fan-out integration tests."""
from tests.messaging.notifications.abstraction import INotificationTests

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from notifications.dto import EmailNotificationTarget, NotificationFanoutRequest
from notifications.fanout import NotificationFanoutService
from notifications.idempotency import InMemoryNotificationIdempotencyStore
from notifications.preferences import StaticMutedCategories

class TestPreferencesAndFanout(INotificationTests):

    def test_fanout_skips_muted_category(self):
        prefs = StaticMutedCategories({'u1': {'marketing'}})
        email = AsyncMock()
        with patch('notifications.fanout.PushNotificationService') as mock_push_cls:
            mock_push_cls.return_value = MagicMock()
            svc = NotificationFanoutService(email_sender=email, preference_store=prefs)
            req = NotificationFanoutRequest(title='T', body='B', email=EmailNotificationTarget(to=['u@x.com']), user_id='u1', category='marketing')
            assert asyncio.run(svc.dispatch(req)) is False
        email.send_email.assert_not_called()

    def test_fanout_idempotency_second_send_skipped(self):
        store = InMemoryNotificationIdempotencyStore()
        email = AsyncMock()
        with patch('notifications.fanout.PushNotificationService') as mock_push_cls:
            mock_push_cls.return_value = MagicMock()
            svc = NotificationFanoutService(email_sender=email, idempotency_store=store)
            req = NotificationFanoutRequest(title='T', body='B', email=EmailNotificationTarget(to=['u@x.com']), user_id='u1', template_id='welcome', dedupe_key='evt-1')
            assert asyncio.run(svc.dispatch(req)) is True
            assert asyncio.run(svc.dispatch(req)) is False
        assert email.send_email.await_count == 1

    def test_fanout_mute_checked_before_idempotency(self):
        """Muted users should not consume idempotency keys."""
        store = InMemoryNotificationIdempotencyStore()
        email = AsyncMock()
        prefs = StaticMutedCategories({'u1': {'alerts'}})
        with patch('notifications.fanout.PushNotificationService') as mock_push_cls:
            mock_push_cls.return_value = MagicMock()
            svc = NotificationFanoutService(email_sender=email, preference_store=prefs, idempotency_store=store)
            req = NotificationFanoutRequest(title='T', body='B', email=EmailNotificationTarget(to=['u@x.com']), user_id='u1', category='alerts', template_id='t', dedupe_key='k')
            assert asyncio.run(svc.dispatch(req)) is False
        email.send_email.assert_not_called()
        req2 = NotificationFanoutRequest(title='T', body='B', email=EmailNotificationTarget(to=['u@x.com']), user_id='u1', category='ok', template_id='t', dedupe_key='k')
        with patch('notifications.fanout.PushNotificationService') as mock_push_cls:
            mock_push_cls.return_value = MagicMock()
            svc = NotificationFanoutService(email_sender=email, preference_store=prefs, idempotency_store=store)
            assert asyncio.run(svc.dispatch(req2)) is True
