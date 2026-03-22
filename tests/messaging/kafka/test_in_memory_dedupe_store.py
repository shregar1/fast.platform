"""Tests for :class:`kafka.idempotent.InMemoryDedupeStore`."""
from tests.messaging.kafka.abstraction import IKafkaTests


import asyncio

import pytest

from kafka.idempotent import InMemoryDedupeStore


class TestInMemoryDedupeStore(IKafkaTests):
    def test_in_memory_dedupe_skip_after_success(self) -> None:
        async def run():
            store = InMemoryDedupeStore(max_keys=100)
            assert await store.should_skip("k1") is False
            await store.record_success("k1")
            assert await store.should_skip("k1") is True

        asyncio.run(run())

    def test_in_memory_dedupe_eviction(self) -> None:
        async def run():
            store = InMemoryDedupeStore(max_keys=2)
            await store.record_success("a")
            await store.record_success("b")
            await store.record_success("c")
            assert await store.should_skip("a") is False

        asyncio.run(run())

    def test_in_memory_dedupe_record_same_key_moves_lru(self) -> None:
        async def run():
            store = InMemoryDedupeStore(max_keys=100)
            await store.record_success("k")
            await store.record_success("k")
            assert await store.should_skip("k") is True

        asyncio.run(run())

    def test_in_memory_dedupe_invalid_max(self) -> None:
        with pytest.raises(ValueError):
            InMemoryDedupeStore(max_keys=0)
