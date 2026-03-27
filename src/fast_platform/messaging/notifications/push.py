"""Push notification service for iOS and Android."""

from typing import Any, Dict, List, Optional

from loguru import logger

from ...core.configuration.notifications import NotificationsConfiguration


class PushNotificationService:
    """High-level push notification service."""

    def __init__(self) -> None:
        """Execute __init__ operation."""
        cfg = NotificationsConfiguration().get_config()
        self._apns = cfg.apns
        self._fcm = cfg.fcm

    @property
    def apns_enabled(self) -> bool:
        """Execute apns_enabled operation.

        Returns:
            The result of the operation.
        """
        return bool(self._apns.enabled)

    @property
    def fcm_enabled(self) -> bool:
        """Execute fcm_enabled operation.

        Returns:
            The result of the operation.
        """
        return bool(self._fcm.enabled)

    async def send_to_ios(
        self,
        device_tokens: List[str],
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Execute send_to_ios operation.

        Args:
            device_tokens: The device_tokens parameter.
            title: The title parameter.
            body: The body parameter.
            data: The data parameter.

        Returns:
            The result of the operation.
        """
        if not self.apns_enabled:
            logger.warning("APNS push attempted but APNS is disabled in config.")
            return
        logger.info(
            "Sending APNS notification",
            device_tokens=device_tokens,
            title=title,
            body=body,
            data=data or {},
        )

    async def send_to_android(
        self,
        registration_tokens: List[str],
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None,
        topic: Optional[str] = None,
    ) -> None:
        """Execute send_to_android operation.

        Args:
            registration_tokens: The registration_tokens parameter.
            title: The title parameter.
            body: The body parameter.
            data: The data parameter.
            topic: The topic parameter.

        Returns:
            The result of the operation.
        """
        if not self.fcm_enabled:
            logger.warning("FCM push attempted but FCM is disabled in config.")
            return
        logger.info(
            "Sending FCM notification",
            registration_tokens=registration_tokens,
            title=title,
            body=body,
            data=data or {},
            topic=topic,
        )
