"""
Generic presence / rooms service.

Can use in-memory (per-process) or Redis for distributed presence tracking.
Designed to work alongside the Channels hub and realtime providers.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple

from loguru import logger

try:
    import redis.asyncio as aioredis  # type: ignore[import]
except Exception:
    aioredis = None  # type: ignore[assignment]


@dataclass
class PresenceEntry:
    user_id: str
    last_seen: float


class InMemoryPresenceBackend:
    """In-memory presence backend for local/single-process use."""

    def __init__(self, ttl_seconds: int = 60) -> None:
        self._ttl_seconds = ttl_seconds
        self._rooms: Dict[str, Dict[str, PresenceEntry]] = {}

    async def mark_present(self, room_id: str, user_id: str) -> None:
        now = time.time()
        room = self._rooms.setdefault(room_id, {})
        room[user_id] = PresenceEntry(user_id=user_id, last_seen=now)
        logger.debug("User {} present in room {}", user_id, room_id)

    async def mark_absent(self, room_id: str, user_id: str) -> None:
        room = self._rooms.get(room_id)
        if not room:
            return
        room.pop(user_id, None)
        if not room:
            self._rooms.pop(room_id, None)
        logger.debug("User {} left room {}", user_id, room_id)

    async def list_present(self, room_id: str) -> List[str]:
        self._evict_expired()
        return list(self._rooms.get(room_id, {}).keys())

    async def list_rooms_for_user(self, user_id: str) -> List[str]:
        self._evict_expired()
        return [r for r, members in self._rooms.items() if user_id in members]

    def _evict_expired(self) -> None:
        now = time.time()
        to_delete: List[Tuple[str, str]] = []
        for room_id, members in self._rooms.items():
            for uid, entry in members.items():
                if now - entry.last_seen > self._ttl_seconds:
                    to_delete.append((room_id, uid))
        for room_id, uid in to_delete:
            members = self._rooms.get(room_id)
            if members:
                members.pop(uid, None)
                if not members:
                    self._rooms.pop(room_id, None)


class RedisPresenceBackend:
    """Redis-backed presence backend using sets and key expiry."""

    def __init__(self, client: "aioredis.Redis", ttl_seconds: int = 60) -> None:
        self._client = client
        self._ttl_seconds = ttl_seconds

    def _room_key(self, room_id: str) -> str:
        return f"presence:{room_id}"

    async def mark_present(self, room_id: str, user_id: str) -> None:
        key = self._room_key(room_id)
        await self._client.sadd(key, user_id)
        await self._client.expire(key, self._ttl_seconds)
        logger.debug("[Redis] User {} present in room {}", user_id, room_id)

    async def mark_absent(self, room_id: str, user_id: str) -> None:
        key = self._room_key(room_id)
        await self._client.srem(key, user_id)
        logger.debug("[Redis] User {} left room {}", user_id, room_id)

    async def list_present(self, room_id: str) -> List[str]:
        key = self._room_key(room_id)
        members: Set[bytes] = await self._client.smembers(key)
        return [m.decode("utf-8") for m in members]

    async def list_rooms_for_user(self, user_id: str) -> List[str]:
        logger.debug(
            "RedisPresenceBackend.list_rooms_for_user is not optimized; "
            "consider a reverse index in your project."
        )
        return []


class PresenceService:
    """High-level presence/rooms service delegating to a backend."""

    def __init__(self, backend: Optional[object] = None) -> None:
        self._backend = backend if backend is not None else InMemoryPresenceBackend()

    async def mark_present(self, room_id: str, user_id: str) -> None:
        await self._backend.mark_present(room_id, user_id)

    async def mark_absent(self, room_id: str, user_id: str) -> None:
        await self._backend.mark_absent(room_id, user_id)

    async def list_present(self, room_id: str) -> List[str]:
        return await self._backend.list_present(room_id)

    async def list_rooms_for_user(self, user_id: str) -> List[str]:
        return await self._backend.list_rooms_for_user(user_id)
