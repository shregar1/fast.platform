from __future__ import annotations

"""Integration smoke tests for ``queues`` exports."""
from queues import (
    DEFAULT_DLQ_SUFFIX,
    ENVELOPE_VERSION_KEY,
    IQueueBackend,
    QueueBroker,
    QueueMessageEnvelope,
    QueuesConfiguration,
    QueuesConfigurationDTO,
    dlq_name,
    prepare_dlq_message,
)
from queues.broker import QueueMessage
from queues.dlq import (
    prepare_quarantine_message,
    primary_queue_from_quarantine,
    quarantine_name,
)
from queues.envelope import should_quarantine as should_quarantine_fn
from tests.messaging.queues.abstraction import IQueueTests


class TestInit(IQueueTests):
    def test_core_symbols_non_none(self) -> None:
        assert QueueBroker is not None
        assert QueuesConfiguration is not None
        assert IQueueBackend is not None
        assert QueuesConfigurationDTO is not None

    def test_dlq_naming_helpers(self) -> None:
        assert dlq_name("q") == "q" + DEFAULT_DLQ_SUFFIX
        assert dlq_name("q" + DEFAULT_DLQ_SUFFIX) == "q" + DEFAULT_DLQ_SUFFIX
        assert (
            quarantine_name("q" + DEFAULT_DLQ_SUFFIX + ".quarantine")
            == "q" + DEFAULT_DLQ_SUFFIX + ".quarantine"
        )
        assert primary_queue_from_quarantine("plain") == "plain"

    def test_envelope_version_constant(self) -> None:
        assert ENVELOPE_VERSION_KEY == "envelope_version"
        assert QueueMessageEnvelope(payload={}).envelope_version == 1

    def test_prepare_dlq_and_quarantine(self) -> None:
        assert prepare_dlq_message("q", QueueMessage(body=b""), reason="x")[0]
        raw, attrs = prepare_dlq_message(
            "q",
            QueueMessage(body=b"x", attributes={"a": "1"}),
            reason="bad",
            error="boom",
        )
        assert b"boom" in raw
        assert "x-fastmvc-dlq-error" in attrs
        body_q, _ = prepare_quarantine_message(
            "q",
            QueueMessage(body=b"y"),
            failure_count=3,
            max_failures=3,
            last_error="oops",
            extra_metadata={"trace": "t1"},
        )
        assert b"oops" in body_q

    def test_envelope_serialization_and_quarantine_rules(self) -> None:
        env = QueueMessageEnvelope(payload={"k": 1}, last_error="e")
        d = env.to_dict()
        assert d["last_error"] == "e"
        e2 = QueueMessageEnvelope.from_dict({"payload": None, "last_error": 42})
        assert e2.payload == {}
        assert e2.last_error == "42"
        assert not QueueMessageEnvelope(failure_count=0).should_quarantine(0)
        assert not should_quarantine_fn(5, 0)

    def test_package_version(self) -> None:
        import queues as q

        assert q.__version__ == "0.3.0"
