"""Tests for DLQ header helpers."""

from fast_platform.messaging.kafka.dlq import (
    DLQ_HEADER_ERROR,
    DLQ_HEADER_OFFSET,
    DLQ_HEADER_ORIGINAL_TOPIC,
    DLQ_HEADER_PARTITION,
    make_dlq_headers,
)
from tests.messaging.kafka.abstraction import IKafkaTests


class TestDlq(IKafkaTests):
    """Represents the TestDlq class."""

    def test_make_dlq_headers_minimal(self):
        """Execute test_make_dlq_headers_minimal operation.

        Returns:
            The result of the operation.
        """
        h = make_dlq_headers(original_topic="orders", error="timeout")
        names = [x[0] for x in h]
        assert DLQ_HEADER_ORIGINAL_TOPIC in names
        assert DLQ_HEADER_ERROR in names
        assert dict(h)[DLQ_HEADER_ORIGINAL_TOPIC] == b"orders"
        assert dict(h)[DLQ_HEADER_ERROR] == b"timeout"

    def test_make_dlq_headers_with_coords_and_extra(self):
        """Execute test_make_dlq_headers_with_coords_and_extra operation.

        Returns:
            The result of the operation.
        """
        h = make_dlq_headers(
            original_topic="t", error="e", partition=3, offset=99, extra=[("x-trace-id", b"abc")]
        )
        d = dict(h)
        assert d[DLQ_HEADER_PARTITION] == b"3"
        assert d[DLQ_HEADER_OFFSET] == b"99"
        assert d["x-trace-id"] == b"abc"
