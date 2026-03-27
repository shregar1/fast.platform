"""Tests for :class:`messaging.kafka.idempotent.InMemoryDedupeStore`."""

import asyncio

import pytest

from fast_platform.messaging.kafka.idempotent import InMemoryDedupeStore
from tests.messaging.kafka.abstraction import IKafkaTests


class TestInMemoryDedupeStore(IKafkaTests):
    """Represents the TestInMemoryDedupeStore class."""

    def test_in_memory_dedupe_skip_after_success(self) -> None:
        """Execute test_in_memory_dedupe_skip_after_success operation.

        Returns:
            The result of the operation.
        """

        async def run():
            """Execute run operation.

            Returns:
                The result of the operation.
            """
            store = InMemoryDedupeStore(max_keys=100)
            assert await store.should_skip("k1") is False
            await store.record_success("k1")
            assert await store.should_skip("k1") is True

        asyncio.run(run())

    def test_in_memory_dedupe_eviction(self) -> None:
        """Execute test_in_memory_dedupe_eviction operation.

        Returns:
            The result of the operation.
        """

        async def run():
            """Execute run operation.

            Returns:
                The result of the operation.
            """
            store = InMemoryDedupeStore(max_keys=2)
            await store.record_success("a")
            await store.record_success("b")
            await store.record_success("c")
            assert await store.should_skip("a") is False

        asyncio.run(run())

    def test_in_memory_dedupe_record_same_key_moves_lru(self) -> None:
        """Execute test_in_memory_dedupe_record_same_key_moves_lru operation.

        Returns:
            The result of the operation.
        """

        async def run():
            """Execute run operation.

            Returns:
                The result of the operation.
            """
            store = InMemoryDedupeStore(max_keys=100)
            await store.record_success("k")
            await store.record_success("k")
            assert await store.should_skip("k") is True

        asyncio.run(run())

    def test_in_memory_dedupe_invalid_max(self) -> None:
        """Execute test_in_memory_dedupe_invalid_max operation.

        Returns:
            The result of the operation.
        """
        with pytest.raises(ValueError):
            InMemoryDedupeStore(max_keys=0)
