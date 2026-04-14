"""Pusher real-time notification provider client."""

from ...core.constants import DEFAULT_TIMEOUT_SECONDS
from typing import Any, Callable


class PusherChannel:
    """Pusher channel representation."""

    def __init__(self, name: str):
        self.name = name


class PusherClient:
    """Pusher client for real-time notifications."""

    def __init__(
        self,
        app_id: str,
        key: str,
        secret: str,
        cluster: str = "mt1",
    ):
        """Initialize Pusher client.
        
        Args:
            app_id: Pusher app ID
            key: Pusher key
            secret: Pusher secret
            cluster: Pusher cluster
        """
        self.app_id = app_id
        self.key = key
        self.secret = secret
        self.cluster = cluster

    async def trigger(
        self,
        channel: str,
        event: str,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """Trigger event on channel."""
        raise NotImplementedError("Install pusher to use PusherClient")

    def bind(self, event: str, callback: Callable) -> None:
        """Bind to event."""
        raise NotImplementedError("Install pusher to use PusherClient")


__all__ = ["PusherChannel", "PusherClient"]
