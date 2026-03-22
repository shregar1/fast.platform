"""
Redis key-value store implementation.

Thin wrapper around `redis.Redis` implementing the generic `IKeyValueStore`
interface so it can be swapped or mocked in tests.
"""

from typing import Any, Optional

import redis
from loguru import logger

from .interfaces import IKeyValueStore


class RedisKeyValueStore(IKeyValueStore):
    """
    Redis-backed key-value store.

    The connection parameters are passed in explicitly so callers are free
    to load them from environment variables, configuration DTOs, or any
    other source.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        password: Optional[str] = None,
        db: int = 0,
    ) -> None:
        self._host = host
        self._port = port
        self._password = password
        self._db = db
        self._client: Optional[redis.Redis] = None

    @property
    def client(self) -> redis.Redis:
        if self._client is None:
            raise RuntimeError("RedisKeyValueStore is not connected.")
        return self._client

    def connect(self) -> None:
        self._client = redis.Redis(
            host=self._host,
            port=self._port,
            password=self._password,
            db=self._db,
        )
        logger.info(
            "Connected RedisKeyValueStore",
            host=self._host,
            port=self._port,
            db=self._db,
        )

    def disconnect(self) -> None:
        if self._client is not None:
            try:
                self._client.close()
            except Exception:
                # Older redis-py may not have close(); ignore.
                pass
            self._client = None
            logger.info("Disconnected RedisKeyValueStore")

    def get(self, key: str) -> Any:
        value = self.client.get(key)
        return value

    def set(self, key: str, value: Any, **kwargs: Any) -> None:
        self.client.set(key, value, **kwargs)

    def delete(self, key: str) -> None:
        self.client.delete(key)

    def exists(self, key: str) -> bool:
        return bool(self.client.exists(key))

    def increment(self, key: str, amount: int = 1) -> int:
        return int(self.client.incr(key, amount))

    def expire(self, key: str, ttl_seconds: int) -> None:
        self.client.expire(key, ttl_seconds)


