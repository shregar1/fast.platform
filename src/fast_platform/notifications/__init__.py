"""fast_notifications – Multi-channel notifications (email, SMS, push) for FastMVC."""

from fast_platform.messaging.notifications import (
    APNSConfigDTO,
    DigestBuffer,
    DigestItem,
    EmailNotificationTarget,
    FCMConfigDTO,
    INotificationPreferenceStore,
    Notification,
    NotificationFanoutRequest,
    NotificationRetryPolicy,
    NotificationRetryPolicyDTO,
    NotificationsService,
    PushConfigurationDTO,
    PushNotificationService,
    PushNotificationTarget,
    as_webhook_retry_policy,
    build_digest_fanout_request,
    make_idempotency_key,
    render_jinja_string,
)

__version__ = "0.3.0"

__all__ = [
    "APNSConfigDTO",
    "DigestBuffer",
    "DigestItem",
    "EmailNotificationTarget",
    "FCMConfigDTO",
    "INotificationPreferenceStore",
    "Notification",
    "NotificationFanoutRequest",
    "NotificationRetryPolicy",
    "NotificationRetryPolicyDTO",
    "NotificationsService",
    "PushConfigurationDTO",
    "PushNotificationService",
    "PushNotificationTarget",
    "as_webhook_retry_policy",
    "build_digest_fanout_request",
    "make_idempotency_key",
    "render_jinja_string",
]
