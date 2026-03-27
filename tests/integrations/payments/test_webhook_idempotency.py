"""Module test_webhook_idempotency.py."""

from __future__ import annotations

"""Tests for webhook idempotency store."""
import asyncio

import pytest

from integrations.payments.webhook_idempotency import InMemoryWebhookIdempotencyStore
from tests.integrations.payments.abstraction import IPaymentsTests


class TestWebhookIdempotency(IPaymentsTests):
    """Represents the TestWebhookIdempotency class."""

    @staticmethod
    async def _run_mark_processed_and_eviction() -> None:
        """Execute _run_mark_processed_and_eviction operation.

        Returns:
            The result of the operation.
        """
        store = InMemoryWebhookIdempotencyStore(max_keys=100)
        await store.mark_processed("evt-1")
        assert await store.is_duplicate("evt-1") is True
        await store.mark_processed("evt-1")
        small = InMemoryWebhookIdempotencyStore(max_keys=2)
        await small.mark_processed("a")
        await small.mark_processed("b")
        await small.mark_processed("c")

    def test_mark_processed_new_key_move_and_eviction(self) -> None:
        """Execute test_mark_processed_new_key_move_and_eviction operation.

        Returns:
            The result of the operation.
        """
        asyncio.run(TestWebhookIdempotency._run_mark_processed_and_eviction())

    def test_max_keys_rejects_zero(self) -> None:
        """Execute test_max_keys_rejects_zero operation.

        Returns:
            The result of the operation.
        """
        with pytest.raises(ValueError, match="max_keys"):
            InMemoryWebhookIdempotencyStore(max_keys=0)
