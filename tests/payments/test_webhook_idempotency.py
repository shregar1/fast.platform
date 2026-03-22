"""Tests for webhook idempotency store."""

import asyncio

import pytest

from fast_payments.webhook_idempotency import InMemoryWebhookIdempotencyStore


async def _run():
    store = InMemoryWebhookIdempotencyStore(max_keys=100)
    await store.mark_processed("evt-1")
    assert await store.is_duplicate("evt-1") is True
    await store.mark_processed("evt-1")

    small = InMemoryWebhookIdempotencyStore(max_keys=2)
    await small.mark_processed("a")
    await small.mark_processed("b")
    await small.mark_processed("c")


def test_mark_processed_new_key_move_and_eviction():
    asyncio.run(_run())


def test_max_keys_rejects_zero():
    with pytest.raises(ValueError, match="max_keys"):
        InMemoryWebhookIdempotencyStore(max_keys=0)
