"""Tests for JSON envelope DTO and schema helper."""

from core.dtos.kafka import KafkaJsonEnvelope

from tests.messaging.kafka.abstraction import IKafkaTests


class TestEnvelope(IKafkaTests):
    """Represents the TestEnvelope class."""

    def test_kafka_json_envelope_roundtrip(self):
        """Execute test_kafka_json_envelope_roundtrip operation.

        Returns:
            The result of the operation.
        """
        env = KafkaJsonEnvelope(
            message_type="UserCreated", payload={"id": "1"}, metadata={"trace": "x"}
        )
        raw = env.to_json_bytes()
        assert b"UserCreated" in raw
        assert b'"trace"' in raw

    def test_kafka_json_envelope_json_schema(self):
        """Execute test_kafka_json_envelope_json_schema operation.

        Returns:
            The result of the operation.
        """
        schema = KafkaJsonEnvelope.envelope_json_schema()
        assert schema.get("type") == "object"
        assert "message_type" in schema.get("properties", {})
