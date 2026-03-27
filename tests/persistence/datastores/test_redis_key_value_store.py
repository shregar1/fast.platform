"""Module test_redis_key_value_store.py."""

from __future__ import annotations

"""Tests for :class:`persistence.datastores.redis_kv.RedisKeyValueStore` (mocked redis)."""
from unittest.mock import MagicMock, patch

from persistence.datastores.redis_kv import RedisKeyValueStore
from tests.persistence.datastores.abstraction import IDatastoresTests


class TestRedisKeyValueStore(IDatastoresTests):
    """Represents the TestRedisKeyValueStore class."""

    @patch("persistence.datastores.redis_kv.redis.Redis")
    def test_connect_disconnect_roundtrip(self, mock_redis_cls: MagicMock) -> None:
        """Execute test_connect_disconnect_roundtrip operation.

        Args:
            mock_redis_cls: The mock_redis_cls parameter.

        Returns:
            The result of the operation.
        """
        mock_client = MagicMock()
        mock_redis_cls.return_value = mock_client
        store = RedisKeyValueStore(host="127.0.0.1", port=6379, db=0)
        store.connect()
        mock_redis_cls.assert_called_once()
        store.disconnect()
        mock_client.close.assert_called_once()

    @patch("persistence.datastores.redis_kv.redis.Redis")
    def test_get_delegates_to_client(self, mock_redis_cls: MagicMock) -> None:
        """Execute test_get_delegates_to_client operation.

        Args:
            mock_redis_cls: The mock_redis_cls parameter.

        Returns:
            The result of the operation.
        """
        mock_client = MagicMock()
        mock_client.get.return_value = b"v"
        mock_redis_cls.return_value = mock_client
        store = RedisKeyValueStore()
        store.connect()
        assert store.get("k") == b"v"
        mock_client.get.assert_called_once_with("k")
