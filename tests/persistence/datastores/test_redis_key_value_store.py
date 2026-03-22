from __future__ import annotations
"""Tests for :class:`datastores.redis_kv.RedisKeyValueStore` (mocked redis)."""
from tests.persistence.datastores.abstraction import IDatastoresTests



from unittest.mock import MagicMock, patch

from datastores.redis_kv import RedisKeyValueStore


class TestRedisKeyValueStore(IDatastoresTests):
    @patch("datastores.redis_kv.redis.Redis")
    def test_connect_disconnect_roundtrip(self, mock_redis_cls: MagicMock) -> None:
        mock_client = MagicMock()
        mock_redis_cls.return_value = mock_client
        store = RedisKeyValueStore(host="127.0.0.1", port=6379, db=0)
        store.connect()
        mock_redis_cls.assert_called_once()
        store.disconnect()
        mock_client.close.assert_called_once()

    @patch("datastores.redis_kv.redis.Redis")
    def test_get_delegates_to_client(self, mock_redis_cls: MagicMock) -> None:
        mock_client = MagicMock()
        mock_client.get.return_value = b"v"
        mock_redis_cls.return_value = mock_client
        store = RedisKeyValueStore()
        store.connect()
        assert store.get("k") == b"v"
        mock_client.get.assert_called_once_with("k")
