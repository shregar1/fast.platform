"""Module test_dlq.py."""

from __future__ import annotations

"""Tests for DLQ and quarantine helpers."""
from fast_platform.messaging.queues.broker import QueueMessage
from fast_platform.messaging.queues.dlq import (
    DEFAULT_QUARANTINE_SUFFIX,
    dlq_name,
    is_dlq_name,
    is_quarantine_name,
    prepare_dlq_message,
    prepare_quarantine_message,
    primary_queue_from_dlq,
    primary_queue_from_quarantine,
    quarantine_name,
)
from tests.messaging.queues.abstraction import IQueueTests


class TestDlq(IQueueTests):
    """Represents the TestDlq class."""

    def test_dlq_naming(self) -> None:
        """Execute test_dlq_naming operation.

        Returns:
            The result of the operation.
        """
        assert dlq_name("orders") == "orders.dlq"
        assert is_dlq_name("orders.dlq")
        assert not is_dlq_name("orders")
        assert primary_queue_from_dlq("orders.dlq") == "orders"
        assert primary_queue_from_dlq("plain") == "plain"

    def test_quarantine_naming(self) -> None:
        """Execute test_quarantine_naming operation.

        Returns:
            The result of the operation.
        """
        assert quarantine_name("orders") == "orders" + DEFAULT_QUARANTINE_SUFFIX
        assert is_quarantine_name("orders.quarantine")
        assert primary_queue_from_quarantine("orders.quarantine") == "orders"
        assert quarantine_name("orders.dlq") == "orders.quarantine"

    def test_prepare_quarantine(self) -> None:
        """Execute test_prepare_quarantine operation.

        Returns:
            The result of the operation.
        """
        msg = QueueMessage(body=b'{"x":1}', attributes={"trace": "t1"})
        body, attrs = prepare_quarantine_message(
            "orders",
            msg,
            failure_count=5,
            max_failures=5,
            last_error="timeout",
            extra_metadata={"request_id": "r1"},
        )
        assert body
        assert attrs["x-fastmvc-failure-count"] == "5"
        assert "fast_quarantine" in body.decode()

    def test_prepare_dlq(self) -> None:
        """Execute test_prepare_dlq operation.

        Returns:
            The result of the operation.
        """
        body, attrs = prepare_dlq_message("q", QueueMessage(body=b""), reason="x")
        assert body
        assert attrs["x-fastmvc-dlq-reason"] == "x"
