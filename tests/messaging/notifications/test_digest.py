"""Tests for digest buffer and fan-out builder."""
from tests.messaging.notifications.abstraction import INotificationTests

import pytest
from notifications.digest import DigestBuffer, DigestItem, build_digest_fanout_request
from notifications.dto import EmailNotificationTarget, PushNotificationTarget

class TestDigest(INotificationTests):

    def test_digest_buffer_add_take_and_clear(self):
        buf = DigestBuffer()
        buf.add('u1', 'news', DigestItem(title='A', body='1'))
        buf.add('u1', 'news', DigestItem(title='B', body='2'))
        assert buf.bucket_count() == 1
        items = buf.take_and_clear('u1', 'news')
        assert len(items) == 2
        assert buf.take_and_clear('u1', 'news') == []

    def test_digest_buffer_drain_all(self):
        buf = DigestBuffer()
        buf.add('u1', 'a', DigestItem(title='x', body='y'))
        buf.add('u2', 'b', DigestItem(title='p', body='q'))
        all_buckets = buf.drain_all()
        assert len(all_buckets) == 2
        assert buf.bucket_count() == 0

    def test_build_digest_fanout_request(self):
        req = build_digest_fanout_request(items=[DigestItem(title='One', body='a'), DigestItem(title='Two', body='b')], digest_title='Daily', email=EmailNotificationTarget(to=['a@b.com']), user_id='u1', category='news')
        assert req.title == 'Daily'
        assert 'One' in req.body
        assert req.data.get('digest_count') == 2
        assert req.user_id == 'u1'
        assert req.category == 'news'

    def test_build_digest_requires_channel(self):
        with pytest.raises(ValueError, match='At least one'):
            build_digest_fanout_request(items=[DigestItem(title='x', body='y')])

    def test_build_digest_push_only(self):
        req = build_digest_fanout_request(items=[DigestItem(title='x', body='y')], push=PushNotificationTarget(ios_device_tokens=['t']))
        assert req.push is not None
