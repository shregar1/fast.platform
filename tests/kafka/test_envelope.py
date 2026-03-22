"""Tests for JSON envelope DTO and schema helper."""

from fast_kafka.dto import KafkaJsonEnvelope, kafka_json_envelope_json_schema


def test_kafka_json_envelope_roundtrip():
    env = KafkaJsonEnvelope(message_type="UserCreated", payload={"id": "1"}, metadata={"trace": "x"})
    raw = env.to_json_bytes()
    assert b"UserCreated" in raw
    assert b'"trace"' in raw


def test_kafka_json_envelope_json_schema():
    schema = kafka_json_envelope_json_schema()
    assert schema.get("type") == "object"
    assert "message_type" in schema.get("properties", {})
