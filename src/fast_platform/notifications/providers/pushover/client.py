"""Pushover API client."""

from typing import Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum


class Priority(Enum):
    """Pushover priority levels."""

    LOWEST = -2
    LOW = -1
    NORMAL = 0
    HIGH = 1
    EMERGENCY = 2


@dataclass
class PushoverResponse:
    """Pushover API response."""

    status: int
    request: str
    errors: list


class PushoverClient:
    """Pushover API client for mobile push notifications."""

    def __init__(self, app_token: str):
        """Execute __init__ operation.

        Args:
            app_token: The app_token parameter.
        """
        self.app_token = app_token
        self.base_url = "https://api.pushover.net/1"

    async def send_message(
        self,
        user_key: str,
        message: str,
        title: Optional[str] = None,
        priority: Priority = Priority.NORMAL,
        url: Optional[str] = None,
        url_title: Optional[str] = None,
        sound: Optional[str] = None,
        device: Optional[str] = None,
        html: bool = False,
        timestamp: Optional[int] = None,
        retry: Optional[int] = None,  # For emergency priority
        expire: Optional[int] = None,  # For emergency priority
    ) -> PushoverResponse:
        """Send a push notification.

        Args:
            user_key: User/group key
            message: Message body (max 1024 chars)
            title: Message title (max 250 chars)
            priority: Message priority
            url: Supplementary URL
            url_title: Title for URL
            sound: Notification sound
            device: Device name to send to
            html: Enable HTML formatting
            timestamp: Unix timestamp
            retry: Retry interval for emergency (seconds)
            expire: Expiration for emergency (seconds)

        """
        import aiohttp

        url_endpoint = f"{self.base_url}/messages.json"

        payload = {
            "token": self.app_token,
            "user": user_key,
            "message": message[:1024],
            "priority": priority.value,
        }

        if title:
            payload["title"] = title[:250]
        if url:
            payload["url"] = url
        if url_title:
            payload["url_title"] = url_title
        if sound:
            payload["sound"] = sound
        if device:
            payload["device"] = device
        if html:
            payload["html"] = "1"
        if timestamp:
            payload["timestamp"] = timestamp
        if priority == Priority.EMERGENCY:
            if retry:
                payload["retry"] = retry
            if expire:
                payload["expire"] = expire

        async with aiohttp.ClientSession() as session:
            async with session.post(url_endpoint, data=payload) as response:
                data = await response.json()

                return PushoverResponse(
                    status=data.get("status", 0),
                    request=data.get("request", ""),
                    errors=data.get("errors", []),
                )

    async def send_to_group(
        self,
        group_key: str,
        message: str,
        title: Optional[str] = None,
        priority: Priority = Priority.NORMAL,
    ) -> PushoverResponse:
        """Send to a Pushover group."""
        return await self.send_message(
            user_key=group_key, message=message, title=title, priority=priority
        )

    async def send_emergency(
        self,
        user_key: str,
        message: str,
        title: str,
        retry: int = 60,  # Retry every 60 seconds
        expire: int = 3600,  # Expire after 1 hour
    ) -> PushoverResponse:
        """Send emergency priority notification."""
        return await self.send_message(
            user_key=user_key,
            message=message,
            title=title,
            priority=Priority.EMERGENCY,
            retry=retry,
            expire=expire,
        )

    async def validate_user(self, user_key: str) -> bool:
        """Validate a user key."""
        import aiohttp

        url = f"{self.base_url}/users/validate.json"

        payload = {"token": self.app_token, "user": user_key}

        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=payload) as response:
                data = await response.json()
                return data.get("status") == 1

    async def get_sounds(self) -> Dict[str, str]:
        """Get available notification sounds."""
        import aiohttp

        url = f"{self.base_url}/sounds.json"

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params={"token": self.app_token}) as response:
                data = await response.json()
                return data.get("sounds", {})

    async def cancel_emergency(self, receipt: str) -> bool:
        """Cancel an emergency notification."""
        import aiohttp

        url = f"{self.base_url}/receipts/{receipt}/cancel.json"

        payload = {"token": self.app_token}

        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=payload) as response:
                data = await response.json()
                return data.get("status") == 1
