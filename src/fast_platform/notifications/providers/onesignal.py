"""OneSignal push notification provider client."""

from enum import Enum
from typing import Any


class DeviceType(Enum):
    """OneSignal device types."""
    IOS = 0
    ANDROID = 1
    AMAZON = 2
    WINDOWS_PHONE = 3
    CHROME_APP = 4
    CHROME_WEB = 5
    SAFARI = 7
    FIREFOX = 8
    MACOS = 9


class OneSignalError(Exception):
    """OneSignal API error."""
    pass


class OneSignalNotification:
    """OneSignal notification data class."""

    def __init__(
        self,
        title: str,
        message: str,
        data: dict[str, Any] | None = None,
        included_segments: list[str] | None = None,
        include_player_ids: list[str] | None = None,
    ):
        self.title = title
        self.message = message
        self.data = data
        self.included_segments = included_segments
        self.include_player_ids = include_player_ids


class OneSignalClient:
    """OneSignal API client for push notifications."""

    def __init__(self, app_id: str, api_key: str):
        """Initialize OneSignal client.
        
        Args:
            app_id: OneSignal app ID
            api_key: OneSignal REST API key
        """
        self.app_id = app_id
        self.api_key = api_key

    async def send_push(
        self,
        player_ids: list[str],
        title: str,
        message: str,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Send push notification."""
        raise NotImplementedError("Install aiohttp to use OneSignalClient")

    async def send_to_segments(
        self,
        segments: list[str],
        title: str,
        message: str,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Send push to segments."""
        raise NotImplementedError("Install aiohttp to use OneSignalClient")


__all__ = [
    "DeviceType",
    "OneSignalClient",
    "OneSignalError",
    "OneSignalNotification",
]
