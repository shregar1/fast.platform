"""
Server-initiated WebSocket ping and stale-connection sweep for :class:`~fast_channels.hub.ChannelsHub`.
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .hub import ChannelsHub


async def run_heartbeat_loop(
    hub: "ChannelsHub",
    *,
    interval_seconds: float = 30.0,
    stale_after_seconds: float = 90.0,
    ping_payload: str = '{"type":"ping"}',
    stop_event: Optional[asyncio.Event] = None,
) -> None:
    """
    Periodically send *ping_payload* to every topic and disconnect subscribers
    that have not had :meth:`~fast_channels.hub.ChannelsHub.record_pong` called
    within *stale_after_seconds*.

    Run as a background task; cancel the task or set *stop_event* to stop cleanly.
    """
    evt = stop_event if stop_event is not None else asyncio.Event()

    while not evt.is_set():
        try:
            await asyncio.wait_for(evt.wait(), timeout=interval_seconds)
        except asyncio.TimeoutError:
            pass
        if evt.is_set():
            break
        for topic in hub.topic_names():
            await hub.send_ping(topic, ping_payload)
            hub.sweep_stale_connections(topic, stale_after_seconds=stale_after_seconds)
