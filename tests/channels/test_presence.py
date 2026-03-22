import asyncio
import time
from dataclasses import dataclass
from typing import Any, Dict, Set


class FakeRedisClient:
    """Tiny fake redis.asyncio client for PresenceBackend tests."""

    def __init__(self) -> None:
        self._data: Dict[str, Set[bytes]] = {}
        self._expirations: Dict[str, int] = {}

    async def sadd(self, key: str, value: str):
        self._data.setdefault(key, set()).add(value.encode("utf-8"))

    async def expire(self, key: str, ttl_seconds: int):
        self._expirations[key] = ttl_seconds

    async def srem(self, key: str, value: str):
        members = self._data.get(key, set())
        members.discard(value.encode("utf-8"))

    async def smembers(self, key: str):
        return self._data.get(key, set())


async def _collect(aiter):
    out = []
    async for x in aiter:
        out.append(x)
    return out


def test_inmemory_presence_mark_list_and_eviction():
    from channels.presence import InMemoryPresenceBackend

    backend = InMemoryPresenceBackend(ttl_seconds=60)

    # Deterministic time control.
    # Mark at t=1000, list_present at t=1050 (no eviction), then list_present at
    # t=1062 (>ttl) to force eviction.
    times = [1000.0, 1000.0, 1050.0, 1062.0]
    it = iter(times)
    original = time.time
    time.time = lambda: next(it)  # type: ignore[assignment]
    try:
        asyncio.run(backend.mark_present("room1", "u1"))
        asyncio.run(backend.mark_present("room1", "u2"))

        # Before eviction.
        present_before = asyncio.run(backend.list_present("room1"))
        assert set(present_before) == {"u1", "u2"}

        # Trigger eviction via list_present.
        present_after = asyncio.run(backend.list_present("room1"))
        assert present_after == []
    finally:
        time.time = original  # type: ignore[assignment]


def test_inmemory_mark_absent_noop_when_room_missing_or_empty():
    """Cover early return when ``room_id`` maps to a missing or empty room dict."""
    from channels.presence import InMemoryPresenceBackend

    backend = InMemoryPresenceBackend(ttl_seconds=60)
    # Unreachable via normal API: empty dict is falsy, so ``mark_absent`` returns immediately.
    backend._rooms["room1"] = {}  # type: ignore[attr-defined]
    asyncio.run(backend.mark_absent("room1", "u1"))
    assert asyncio.run(backend.list_present("room1")) == []

    asyncio.run(backend.mark_absent("unknown_room", "u1"))


def test_inmemory_presence_mark_absent_and_room_cleanup():
    from channels.presence import InMemoryPresenceBackend

    backend = InMemoryPresenceBackend(ttl_seconds=60)
    asyncio.run(backend.mark_present("room1", "u1"))
    asyncio.run(backend.mark_present("room1", "u2"))

    asyncio.run(backend.mark_absent("room1", "u1"))
    assert set(asyncio.run(backend.list_present("room1"))) == {"u2"}
    assert asyncio.run(backend.list_rooms_for_user("u1")) == []
    assert asyncio.run(backend.list_rooms_for_user("u2")) == ["room1"]

    # Last user leaving should delete the room.
    asyncio.run(backend.mark_absent("room1", "u2"))
    assert asyncio.run(backend.list_present("room1")) == []
    assert asyncio.run(backend.list_rooms_for_user("u2")) == []


def test_presence_service_delegates_to_backend():
    from channels.presence import PresenceService

    calls: dict[str, list[Any]] = {"present": [], "absent": [], "list_present": [], "list_rooms": []}

    class FakeBackend:
        async def mark_present(self, room_id: str, user_id: str) -> None:
            calls["present"].append((room_id, user_id))

        async def mark_absent(self, room_id: str, user_id: str) -> None:
            calls["absent"].append((room_id, user_id))

        async def list_present(self, room_id: str):
            calls["list_present"].append(room_id)
            return ["u1"]

        async def list_rooms_for_user(self, user_id: str):
            calls["list_rooms"].append(user_id)
            return ["room1"]

    svc = PresenceService(backend=FakeBackend())

    asyncio.run(svc.mark_present("room1", "u1"))
    asyncio.run(svc.mark_absent("room1", "u1"))
    assert asyncio.run(svc.list_present("room1")) == ["u1"]
    assert asyncio.run(svc.list_rooms_for_user("u1")) == ["room1"]

    assert calls["present"] == [("room1", "u1")]
    assert calls["absent"] == [("room1", "u1")]
    assert calls["list_present"] == ["room1"]
    assert calls["list_rooms"] == ["u1"]


def test_redis_presence_backend_mark_and_list():
    from channels.presence import RedisPresenceBackend

    client = FakeRedisClient()
    backend = RedisPresenceBackend(client=client, ttl_seconds=60)

    asyncio.run(backend.mark_present("room1", "u1"))
    asyncio.run(backend.mark_present("room1", "u2"))

    members = asyncio.run(backend.list_present("room1"))
    assert set(members) == {"u1", "u2"}

    asyncio.run(backend.mark_absent("room1", "u1"))
    members2 = asyncio.run(backend.list_present("room1"))
    assert set(members2) == {"u2"}

    # Non-optimized path should return [].
    assert asyncio.run(backend.list_rooms_for_user("u1")) == []

