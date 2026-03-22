"""
Simple in-memory WebRTC signaling service.

Designed for small deployments and local development.
For production, consider replacing this with a distributed
signaling backend (Redis, Kafka, etc.).
"""

from __future__ import annotations

import time
from collections import defaultdict
from typing import TYPE_CHECKING, Dict, List, Optional, Protocol

from loguru import logger

if TYPE_CHECKING:
    from .consent import BeforeMediaConsentCallback


class SessionExpiredCallback(Protocol):
    def __call__(self, room_id: str, peer_id: str) -> None: ...


class WebRTCSignalingService:
    """
    Manages rooms and peers for WebRTC signaling.

    This implementation is intentionally simple and in-memory.

    * ``session_ttl_seconds`` — if set, peer memberships expire after this many seconds
      of wall-clock time (using :func:`time.monotonic` deadlines). Call
      :meth:`cleanup_expired_sessions` periodically or rely on lazy cleanup on
      :meth:`join_room`, :meth:`leave_room`, and :meth:`list_peers`.
    * ``on_session_expired`` — invoked when a peer is removed due to TTL (not when leaving voluntarily).
    * ``before_peer_join`` — if set, must return ``True`` for the peer to join (recording/consent gating).
    """

    def __init__(
        self,
        max_peers_per_room: int = 8,
        *,
        session_ttl_seconds: Optional[float] = None,
        on_session_expired: Optional[SessionExpiredCallback] = None,
        before_peer_join: Optional[BeforeMediaConsentCallback] = None,
    ) -> None:
        self._max_peers_per_room = max_peers_per_room
        self._session_ttl_seconds = session_ttl_seconds
        self._on_session_expired = on_session_expired
        self._before_peer_join = before_peer_join
        self._rooms: Dict[str, List[str]] = defaultdict(list)
        self._deadlines: Dict[tuple[str, str], float] = {}

    def join_room(self, room_id: str, peer_id: str) -> bool:
        if self._before_peer_join is not None and not self._before_peer_join(room_id, peer_id):
            logger.info(
                "Join denied by before_peer_join (consent / policy)",
                room_id=room_id,
                peer_id=peer_id,
            )
            return False
        self._cleanup_expired(room_id)
        peers = self._rooms[room_id]
        if peer_id in peers:
            self._touch_deadline(room_id, peer_id)
            return True
        if len(peers) >= self._max_peers_per_room:
            logger.warning(f"Room {room_id} is full (max {self._max_peers_per_room}).")
            return False
        peers.append(peer_id)
        self._touch_deadline(room_id, peer_id)
        logger.debug(f"Peer {peer_id} joined room {room_id}.")
        return True

    def leave_room(self, room_id: str, peer_id: str) -> None:
        self._cleanup_expired(room_id)
        peers = self._rooms.get(room_id, [])
        if peer_id in peers:
            peers.remove(peer_id)
            self._deadlines.pop((room_id, peer_id), None)
            logger.debug(f"Peer {peer_id} left room {room_id}.")
        if not peers and room_id in self._rooms:
            del self._rooms[room_id]

    def list_peers(self, room_id: str, exclude: str | None = None) -> List[str]:
        self._cleanup_expired(room_id)
        peers = list(self._rooms.get(room_id, []))
        if exclude and exclude in peers:
            peers.remove(exclude)
        return peers

    def cleanup_expired_sessions(self) -> int:
        """
        Scan all rooms and remove peers past TTL. Returns the number of peers removed.
        """
        removed = 0
        for room_id in list(self._rooms.keys()):
            before = len(self._rooms[room_id])
            self._cleanup_expired(room_id)
            after = len(self._rooms.get(room_id, []))
            removed += before - after
        return removed

    def _touch_deadline(self, room_id: str, peer_id: str) -> None:
        if self._session_ttl_seconds is None:
            return
        self._deadlines[(room_id, peer_id)] = time.monotonic() + float(self._session_ttl_seconds)

    def _cleanup_expired(self, room_id: str) -> None:
        if self._session_ttl_seconds is None:
            return
        now = time.monotonic()
        peers = self._rooms.get(room_id)
        if not peers:
            return
        to_remove: List[str] = []
        for peer_id in list(peers):
            key = (room_id, peer_id)
            deadline = self._deadlines.get(key)
            if deadline is not None and now > deadline:
                to_remove.append(peer_id)
        for peer_id in to_remove:
            peers.remove(peer_id)
            self._deadlines.pop((room_id, peer_id), None)
            if self._on_session_expired:
                self._on_session_expired(room_id, peer_id)
            logger.debug(f"Peer {peer_id} expired from room {room_id} (session TTL).")
        if not peers and room_id in self._rooms:
            del self._rooms[room_id]
