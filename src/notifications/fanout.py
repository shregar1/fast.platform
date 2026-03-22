"""
Multi-provider fan-out: one :class:`~fast_notifications.dto.NotificationFanoutRequest`
to email (pluggable) and push (APNS/FCM via :class:`~fast_notifications.push.PushNotificationService`).
"""

from __future__ import annotations

from typing import Optional, Protocol

from loguru import logger

from .dto import NotificationFanoutRequest
from .idempotency import NotificationIdempotencyStore, make_idempotency_key
from .preferences import INotificationPreferenceStore, AllowAllNotificationPreferences
from .push import PushNotificationService


class EmailSender(Protocol):
    """Pluggable email transport (SMTP, SES, SendGrid, etc.)."""

    async def send_email(
        self,
        *,
        to: list[str],
        subject: str,
        body_text: str,
        data: dict,
    ) -> None:
        ...


class LoggingEmailSender:
    """Default implementation that logs only (suitable for dev/tests)."""

    async def send_email(
        self,
        *,
        to: list[str],
        subject: str,
        body_text: str,
        data: dict,
    ) -> None:
        logger.info(
            "Email notification (logging backend)",
            to=to,
            subject=subject,
            body_preview=body_text[:200],
            data_keys=list(data.keys()),
        )


class NotificationFanoutService:
    """
    Dispatches a :class:`~fast_notifications.dto.NotificationFanoutRequest` to
    configured email and push backends.

    Optional **preference store** skips muted categories; optional **idempotency store**
    dedupes on ``(user_id, template_id, dedupe_key)`` within ``idempotency_ttl_seconds``.
    """

    def __init__(
        self,
        *,
        push: Optional[PushNotificationService] = None,
        email_sender: Optional[EmailSender] = None,
        preference_store: Optional[INotificationPreferenceStore] = None,
        idempotency_store: Optional[NotificationIdempotencyStore] = None,
        idempotency_ttl_seconds: int = 86_400,
    ) -> None:
        self._push = push or PushNotificationService()
        self._email = email_sender or LoggingEmailSender()
        self._prefs = preference_store or AllowAllNotificationPreferences()
        self._idempotency = idempotency_store
        self._idempotency_ttl = idempotency_ttl_seconds

    async def dispatch(self, req: NotificationFanoutRequest) -> bool:
        """
        Deliver to configured channels. Returns ``False`` if skipped (muted category or duplicate idempotency key).
        """
        if req.user_id and req.category:
            if await self._prefs.is_category_muted(req.user_id, req.category):
                logger.info(
                    "Skipping fan-out (muted category)",
                    user_id=req.user_id,
                    category=req.category,
                )
                return False

        if (
            self._idempotency is not None
            and req.user_id
            and req.template_id
            and req.dedupe_key
        ):
            key = make_idempotency_key(req.user_id, req.template_id, req.dedupe_key)
            if not await self._idempotency.try_acquire(key, ttl_seconds=self._idempotency_ttl):
                logger.info(
                    "Skipping fan-out (idempotent duplicate)",
                    user_id=req.user_id,
                    template_id=req.template_id,
                )
                return False

        subject = req.title
        if req.email is not None:
            em = req.email
            subj = em.subject or subject
            await self._email.send_email(
                to=list(em.to),
                subject=subj,
                body_text=req.body,
                data={**req.data, "title": req.title},
            )

        if req.push is not None:
            pu = req.push
            merged = {**req.data, "title": req.title}
            if pu.ios_device_tokens:
                await self._push.send_to_ios(
                    list(pu.ios_device_tokens),
                    req.title,
                    req.body,
                    merged,
                )
            if pu.android_registration_tokens or pu.fcm_topic:
                await self._push.send_to_android(
                    list(pu.android_registration_tokens),
                    req.title,
                    req.body,
                    merged,
                    topic=pu.fcm_topic,
                )
        return True
