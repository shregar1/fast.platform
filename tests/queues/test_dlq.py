"""Tests for DLQ and quarantine helpers."""

from fast_core.services.queues import QueueMessage

from fast_queues.dlq import (
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


def test_dlq_naming():
    assert dlq_name("orders") == "orders.dlq"
    assert is_dlq_name("orders.dlq")
    assert not is_dlq_name("orders")
    assert primary_queue_from_dlq("orders.dlq") == "orders"
    assert primary_queue_from_dlq("plain") == "plain"


def test_quarantine_naming():
    assert quarantine_name("orders") == "orders" + DEFAULT_QUARANTINE_SUFFIX
    assert is_quarantine_name("orders.quarantine")
    assert primary_queue_from_quarantine("orders.quarantine") == "orders"
    # DLQ input is normalized to primary before appending quarantine
    assert quarantine_name("orders.dlq") == "orders.quarantine"


def test_prepare_quarantine():
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


def test_prepare_dlq():
    body, attrs = prepare_dlq_message("q", QueueMessage(body=b""), reason="x")
    assert body
    assert attrs["x-fastmvc-dlq-reason"] == "x"
