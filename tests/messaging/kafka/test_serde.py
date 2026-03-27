"""Tests for optional Protobuf / Avro serde helpers."""

import importlib.util

import pytest

from tests.messaging.kafka.abstraction import IKafkaTests


class TestSerde(IKafkaTests):
    """Represents the TestSerde class."""

    def test_serialize_protobuf_duck_typing(self):
        """Execute test_serialize_protobuf_duck_typing operation.

        Returns:
            The result of the operation.
        """
        from fast_platform.messaging.kafka.serde import serialize_protobuf

        class Msg:
            """Represents the Msg class."""

            def SerializeToString(self):
                """Execute SerializeToString operation.

                Returns:
                    The result of the operation.
                """
                return b"bin"

        assert serialize_protobuf(Msg()) == b"bin"

    def test_serialize_protobuf_rejects_plain_object(self):
        """Execute test_serialize_protobuf_rejects_plain_object operation.

        Returns:
            The result of the operation.
        """
        from fast_platform.messaging.kafka.serde import serialize_protobuf

        with pytest.raises(TypeError):
            serialize_protobuf(object())

    def test_serialize_avro_when_fastavro_installed(self):
        """Execute test_serialize_avro_when_fastavro_installed operation.

        Returns:
            The result of the operation.
        """
        from fast_platform.messaging.kafka.serde import serialize_avro_record

        if importlib.util.find_spec("fastavro") is None:
            pytest.skip("fastavro not installed")
        schema = {
            "type": "record",
            "name": "Ev",
            "namespace": "test",
            "fields": [{"name": "x", "type": "int"}],
        }
        raw = serialize_avro_record({"x": 7}, schema)
        assert isinstance(raw, bytes)
        assert len(raw) > 0

    def test_serialize_avro_import_error_message(self):
        """Execute test_serialize_avro_import_error_message operation.

        Returns:
            The result of the operation.
        """
        if importlib.util.find_spec("fastavro") is not None:
            pytest.skip("fastavro is installed")
        from fast_platform.messaging.kafka.serde import serialize_avro_record

        with pytest.raises(RuntimeError, match="fastavro"):
            serialize_avro_record({"x": 1}, {"type": "record", "name": "E", "fields": []})
