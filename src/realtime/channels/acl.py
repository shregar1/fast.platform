"""Channel ACL helpers: allow/deny WebSocket subscribe by ``user_id`` and channel id."""

from __future__ import annotations

from typing import Awaitable, Callable, Mapping, Protocol, Set, runtime_checkable

from starlette.exceptions import WebSocketException


@runtime_checkable
class ChannelACLPolicy(Protocol):
    """Represents the ChannelACLPolicy class."""

    async def may_subscribe(self, user_id: str, channel_id: str) -> bool:
        """Return True if *user_id* may subscribe to *channel_id*."""
        ...


class AllowAllChannelACL:
    """Default policy: any authenticated user may subscribe to any channel."""

    async def may_subscribe(self, user_id: str, channel_id: str) -> bool:
        """Execute may_subscribe operation.

        Args:
            user_id: The user_id parameter.
            channel_id: The channel_id parameter.

        Returns:
            The result of the operation.
        """
        return True


class StaticChannelACL:
    """Fixed mapping ``user_id`` → set of allowed ``channel_id`` strings."""

    def __init__(self, allowed: Mapping[str, Set[str]]) -> None:
        """Execute __init__ operation.

        Args:
            allowed: The allowed parameter.
        """
        self._allowed = {uid: set(channels) for uid, channels in allowed.items()}

    async def may_subscribe(self, user_id: str, channel_id: str) -> bool:
        """Execute may_subscribe operation.

        Args:
            user_id: The user_id parameter.
            channel_id: The channel_id parameter.

        Returns:
            The result of the operation.
        """
        allowed = self._allowed.get(user_id)
        if not allowed:
            return False
        return channel_id in allowed


def make_subscribe_acl_checker(
    policy: ChannelACLPolicy,
    *,
    user_id: str,
    denied_code: int = 1008,
    denied_reason: str = "channel not allowed",
) -> Callable[[str], Awaitable[None]]:
    """Build an async callable ``check(channel_id)`` that raises
    :class:`starlette.exceptions.WebSocketException` when subscribe is denied.

    Use before :meth:`~fast_channels.hub.ChannelsHub.connect`::

        check = make_subscribe_acl_checker(policy, user_id=current_user.id)
        await check(topic)
        await hub.connect(topic, websocket)
    """

    async def check(channel_id: str) -> None:
        """Execute check operation.

        Args:
            channel_id: The channel_id parameter.

        Returns:
            The result of the operation.
        """
        if not await policy.may_subscribe(user_id, channel_id):
            raise WebSocketException(code=denied_code, reason=denied_reason)

    return check
