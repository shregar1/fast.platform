"""Tests for fast_queues."""

from from fast_platform.services.queues import QueueMessage

from fast_queues import (
    DEFAULT_DLQ_SUFFIX,
    ENVELOPE_VERSION_KEY,
    IQueueBackend,
    QueueBroker,
    QueueMessageEnvelope,
    QueuesConfiguration,
    QueuesConfigurationDTO,
    dlq_name,
    is_dlq_name,
    prepare_dlq_message,
    primary_queue_from_dlq,
)
from fast_queues.dlq import (
    primary_queue_from_quarantine,
    prepare_quarantine_message,
    quarantine_name,
)
from fast_queues.envelope import should_quarantine as should_quarantine_fn


def test_imports():
    assert QueueBroker is not None
    assert QueuesConfiguration is not None
    assert dlq_name("q") == "q" + DEFAULT_DLQ_SUFFIX
    assert dlq_name("q" + DEFAULT_DLQ_SUFFIX) == "q" + DEFAULT_DLQ_SUFFIX
    assert quarantine_name("q" + DEFAULT_DLQ_SUFFIX + ".quarantine") == (
        "q" + DEFAULT_DLQ_SUFFIX + ".quarantine"
    )
    assert primary_queue_from_quarantine("plain") == "plain"
    assert ENVELOPE_VERSION_KEY == "envelope_version"
    assert QueueMessageEnvelope(payload={}).envelope_version == 1
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

    env = QueueMessageEnvelope(payload={"k": 1}, last_error="e")
    d = env.to_dict()
    assert d["last_error"] == "e"
    e2 = QueueMessageEnvelope.from_dict({"payload": None, "last_error": 42})
    assert e2.payload == {}
    assert e2.last_error == "42"
    assert not QueueMessageEnvelope(failure_count=0).should_quarantine(0)
    assert not should_quarantine_fn(5, 0)

    import fast_queues as fq

    assert fq.__version__ == "0.3.0"
