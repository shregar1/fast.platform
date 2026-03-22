"""Tests for fan-out DTOs and validation."""

import pytest
from notifications.dto import (
    EmailNotificationTarget,
    NotificationFanoutRequest,
    NotificationRetryPolicyDTO,
    PushNotificationTarget,
)

from notifications.retry_policy import NotificationRetryPolicy
from tests.messaging.notifications.abstraction import INotificationTests


class TestFanoutDto(INotificationTests):
    def test_fanout_request_email_only(self):
        req = NotificationFanoutRequest(
            title="Hi", body="Body", email=EmailNotificationTarget(to=["a@example.com"])
        )
        assert req.push is None

    def test_fanout_request_push_only(self):
        req = NotificationFanoutRequest(
            title="Hi", body="Body", push=PushNotificationTarget(ios_device_tokens=["t1"])
        )
        assert req.email is None

    def test_fanout_request_both_channels(self):
        req = NotificationFanoutRequest(
            title="Hi",
            body="Body",
            email=EmailNotificationTarget(to=["a@example.com"]),
            push=PushNotificationTarget(android_registration_tokens=["r1"]),
        )
        assert req.retry_policy is None

    def test_fanout_rejects_no_channel(self):
        with pytest.raises(ValueError, match="At least one"):
            NotificationFanoutRequest(title="x", body="y")

    def test_fanout_rejects_empty_push(self):
        with pytest.raises(ValueError, match="push is set"):
            NotificationFanoutRequest(title="x", body="y", push=PushNotificationTarget())

    def test_retry_policy_dto_roundtrip(self):
        dto = NotificationRetryPolicyDTO()
        dc = dto.to_dataclass()
        assert isinstance(dc, NotificationRetryPolicy)
        assert dc.max_attempts == 3
        back = NotificationRetryPolicyDTO.from_dataclass(dc)
        assert back.model_dump() == dto.model_dump()
