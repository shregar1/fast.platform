from __future__ import annotations

"""Tests for :class:`messaging.queues.envelope.QueueMessageEnvelope`."""
import pytest

from messaging.queues.envelope import (
    ENVELOPE_VERSION_KEY,
    PRIORITY_KEY,
    QueueMessageEnvelope,
    should_quarantine,
)
from tests.messaging.queues.abstraction import IQueueTests


class TestEnvelope(IQueueTests):
    def test_round_trip(self) -> None:
        e = QueueMessageEnvelope(payload={"job": "x"}, priority=5, delay_seconds=30)
        raw = e.to_json_bytes()
        e2 = QueueMessageEnvelope.from_json_bytes(raw)
        assert e2.payload == {"job": "x"}
        assert e2.priority == 5
        assert e2.delay_seconds == 30

    def test_with_processing_failure_and_quarantine(self) -> None:
        e = QueueMessageEnvelope(payload={})
        e2 = e.with_processing_failure("boom")
        assert e2.failure_count == 1
        assert e2.last_error == "boom"
        assert e2.should_quarantine(3) is False
        e3 = e2.with_processing_failure("again").with_processing_failure("third")
        assert e3.failure_count == 3
        assert e3.should_quarantine(3) is True

    def test_should_quarantine_function(self) -> None:
        assert should_quarantine(2, 2) is True
        assert should_quarantine(1, 3) is False
        assert should_quarantine(0, 1) is False

    def test_from_dict_invalid(self) -> None:
        with pytest.raises(ValueError):
            QueueMessageEnvelope.from_dict([])
        with pytest.raises(ValueError):
            QueueMessageEnvelope.from_dict({"payload": []})

    def test_to_dict_keys(self) -> None:
        d = QueueMessageEnvelope(payload={"a": 1}, priority=2).to_dict()
        assert d[ENVELOPE_VERSION_KEY] == 1
        assert d[PRIORITY_KEY] == 2
