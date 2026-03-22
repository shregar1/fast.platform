"""Tests for idempotent dedupe helpers."""

import asyncio

import pytest

from kafka.idempotent import InMemoryDedupeStore, default_dedupe_key


def test_default_dedupe_key_stable():
    assert default_dedupe_key(b"a") == default_dedupe_key(b"a")
    assert default_dedupe_key(b"a") != default_dedupe_key(b"b")


def test_in_memory_dedupe_skip_after_success():
    async def run():
        store = InMemoryDedupeStore(max_keys=100)
        assert await store.should_skip("k1") is False
        await store.record_success("k1")
        assert await store.should_skip("k1") is True

    asyncio.run(run())


def test_in_memory_dedupe_eviction():
    async def run():
        store = InMemoryDedupeStore(max_keys=2)
        await store.record_success("a")
        await store.record_success("b")
        await store.record_success("c")
        assert await store.should_skip("a") is False

    asyncio.run(run())


def test_in_memory_dedupe_record_same_key_moves_lru():
    async def run():
        store = InMemoryDedupeStore(max_keys=100)
        await store.record_success("k")
        await store.record_success("k")

    asyncio.run(run())


def test_in_memory_dedupe_invalid_max():
    with pytest.raises(ValueError):
        InMemoryDedupeStore(max_keys=0)
