"""Module test_envelope.py."""

from __future__ import annotations

"""Tests for :class:`messaging.queues.envelope.QueueMessageEnvelope`."""
import pytest

from fast_platform.messaging.queues.envelope import (
    ENVELOPE_VERSION_KEY,
    PRIORITY_KEY,
    QueueMessageEnvelope,
    should_quarantine,
)
from tests.messaging.queues.abstraction import IQueueTests


class TestEnvelope(IQueueTests):
    """Represents the TestEnvelope class."""

    def test_round_trip(self) -> None:
        """Execute test_round_trip operation.

        Returns:
            The result of the operation.
        """
        e = QueueMessageEnvelope(payload={"job": "x"}, priority=5, delay_seconds=30)
        raw = e.to_json_bytes()
        e2 = QueueMessageEnvelope.from_json_bytes(raw)
        assert e2.payload == {"job": "x"}
        assert e2.priority == 5
        assert e2.delay_seconds == 30

    def test_with_processing_failure_and_quarantine(self) -> None:
        """Execute test_with_processing_failure_and_quarantine operation.

        Returns:
            The result of the operation.
        """
        e = QueueMessageEnvelope(payload={})
        e2 = e.with_processing_failure("boom")
        assert e2.failure_count == 1
        assert e2.last_error == "boom"
        assert e2.should_quarantine(3) is False
        e3 = e2.with_processing_failure("again").with_processing_failure("third")
        assert e3.failure_count == 3
        assert e3.should_quarantine(3) is True

    def test_should_quarantine_function(self) -> None:
        """Execute test_should_quarantine_function operation.

        Returns:
            The result of the operation.
        """
        assert should_quarantine(2, 2) is True
        assert should_quarantine(1, 3) is False
        assert should_quarantine(0, 1) is False

    def test_from_dict_invalid(self) -> None:
        """Execute test_from_dict_invalid operation.

        Returns:
            The result of the operation.
        """
        with pytest.raises(ValueError):
            QueueMessageEnvelope.from_dict([])
        with pytest.raises(ValueError):
            QueueMessageEnvelope.from_dict({"payload": []})

    def test_to_dict_keys(self) -> None:
        """Execute test_to_dict_keys operation.

        Returns:
            The result of the operation.
        """
        d = QueueMessageEnvelope(payload={"a": 1}, priority=2).to_dict()
        assert d[ENVELOPE_VERSION_KEY] == 1
        assert d[PRIORITY_KEY] == 2
