"""DTOs for push notification configuration (iOS/Android) and multi-channel fan-out."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, List, Optional

from pydantic import Field, model_validator

from .abstraction import IDTO

if TYPE_CHECKING:
    from fast_platform.messaging.notifications.retry_policy import NotificationRetryPolicy


class APNSConfigDTO(IDTO):
    """Apple Push Notification Service configuration."""

    enabled: bool = False
    key_id: Optional[str] = None
    team_id: Optional[str] = None
    bundle_id: Optional[str] = None
    private_key_path: Optional[str] = None
    use_sandbox: bool = True


class FCMConfigDTO(IDTO):
    """Firebase Cloud Messaging configuration."""

    enabled: bool = False
    server_key: Optional[str] = None
    project_id: Optional[str] = None
    default_topics: List[str] = []


class PushConfigurationDTO(IDTO):
    """Complete push notification configuration DTO."""

    apns: APNSConfigDTO = APNSConfigDTO()
    fcm: FCMConfigDTO = FCMConfigDTO()


class NotificationRetryPolicyDTO(IDTO):
    """JSON-friendly retry policy with the same fields/defaults as
    :class:`~fast_webhooks.delivery.RetryPolicy` and
    :class:`~fast_notifications.retry_policy.NotificationRetryPolicy`.
    """

    max_attempts: int = 3
    initial_delay_seconds: float = 1.0
    backoff_factor: float = 2.0
    jitter_ratio: float = 0.0
    retry_on_status: set[int] = Field(default_factory=lambda: {408, 429, 500, 502, 503})

    def to_dataclass(self) -> Any:
        """Execute to_dataclass operation.

        Returns:
            The result of the operation.
        """
        from fast_platform.messaging.notifications.retry_policy import NotificationRetryPolicy

        return NotificationRetryPolicy(
            max_attempts=self.max_attempts,
            initial_delay_seconds=self.initial_delay_seconds,
            backoff_factor=self.backoff_factor,
            jitter_ratio=self.jitter_ratio,
            retry_on_status=set(self.retry_on_status),
        )

    @classmethod
    def from_dataclass(cls, policy: Any) -> NotificationRetryPolicyDTO:
        """Execute from_dataclass operation.

        Args:
            policy: The policy parameter.

        Returns:
            The result of the operation.
        """
        return cls(
            max_attempts=policy.max_attempts,
            initial_delay_seconds=policy.initial_delay_seconds,
            backoff_factor=policy.backoff_factor,
            jitter_ratio=policy.jitter_ratio,
            retry_on_status=set(policy.retry_on_status),
        )


class EmailNotificationTarget(IDTO):
    """SMTP-style recipients for one fan-out request."""

    to: List[str] = Field(..., min_length=1)
    subject: Optional[str] = None


class PushNotificationTarget(IDTO):
    """Mobile tokens / topic for one fan-out request."""

    ios_device_tokens: List[str] = Field(default_factory=list)
    android_registration_tokens: List[str] = Field(default_factory=list)
    fcm_topic: Optional[str] = None


class NotificationFanoutRequest(IDTO):
    """Single DTO for email + push: set ``email``, ``push``, or both.
    Optional ``retry_policy`` carries the same retry shape as webhooks for downstream HTTP/SMTP clients.

    Optional ``user_id`` / ``template_id`` / ``dedupe_key`` enable idempotent fan-out;
    ``category`` pairs with :class:`~fast_notifications.preferences.INotificationPreferenceStore`.
    """

    title: str
    body: str
    data: dict[str, Any] = Field(default_factory=dict)
    email: Optional[EmailNotificationTarget] = None
    push: Optional[PushNotificationTarget] = None
    retry_policy: Optional[NotificationRetryPolicyDTO] = None
    user_id: Optional[str] = None
    template_id: Optional[str] = None
    dedupe_key: Optional[str] = None
    category: Optional[str] = None

    @model_validator(mode="after")
    def _validate_channels(self) -> NotificationFanoutRequest:
        """Execute _validate_channels operation.

        Returns:
            The result of the operation.
        """
        if self.email is None and self.push is None:
            raise ValueError("At least one of email or push must be set")
        if self.push is not None:
            p = self.push
            if not (p.ios_device_tokens or p.android_registration_tokens or p.fcm_topic):
                raise ValueError(
                    "When push is set, specify ios_device_tokens, android_registration_tokens, or fcm_topic"
                )
        return self
