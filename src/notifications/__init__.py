"""
fast_notifications – Notifications extension for FastMVC.
"""

from __future__ import annotations

from .digest import DigestBuffer, DigestItem, build_digest_fanout_request
from .dto import (
    APNSConfigDTO,
    EmailNotificationTarget,
    FCMConfigDTO,
    NotificationFanoutRequest,
    NotificationRetryPolicyDTO,
    PushConfigurationDTO,
    PushNotificationTarget,
)
from .fanout import EmailSender, LoggingEmailSender, NotificationFanoutService
from .idempotency import (
    InMemoryNotificationIdempotencyStore,
    NotificationIdempotencyStore,
    RedisNotificationIdempotencyStore,
    make_idempotency_key,
)
from .preferences import (
    AllowAllNotificationPreferences,
    INotificationPreferenceStore,
    StaticMutedCategories,
)
from .push import PushNotificationService
from .retry_policy import NotificationRetryPolicy
from .service import Notification, NotificationsService
from .templating import render_jinja_string
from .webhook_retry_compat import as_webhook_retry_policy

__version__ = "0.3.0"

__all__ = [
    "APNSConfigDTO",
    "AllowAllNotificationPreferences",
    "DigestBuffer",
    "DigestItem",
    "EmailNotificationTarget",
    "EmailSender",
    "FCMConfigDTO",
    "INotificationPreferenceStore",
    "InMemoryNotificationIdempotencyStore",
    "LoggingEmailSender",
    "Notification",
    "NotificationFanoutRequest",
    "NotificationIdempotencyStore",
    "NotificationRetryPolicy",
    "NotificationRetryPolicyDTO",
    "NotificationFanoutService",
    "NotificationsService",
    "PushConfigurationDTO",
    "PushNotificationService",
    "PushNotificationTarget",
    "RedisNotificationIdempotencyStore",
    "StaticMutedCategories",
    "__version__",
    "as_webhook_retry_policy",
    "build_digest_fanout_request",
    "make_idempotency_key",
    "render_jinja_string",
]
