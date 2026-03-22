"""Tests for optional Protobuf / Avro serde helpers."""
from tests.messaging.kafka.abstraction import IKafkaTests

import importlib.util
import pytest

class TestSerde(IKafkaTests):

    def test_serialize_protobuf_duck_typing(self):
        from kafka.serde import serialize_protobuf

        class Msg:

            def SerializeToString(self):
                return b'bin'
        assert serialize_protobuf(Msg()) == b'bin'

    def test_serialize_protobuf_rejects_plain_object(self):
        from kafka.serde import serialize_protobuf
        with pytest.raises(TypeError):
            serialize_protobuf(object())

    def test_serialize_avro_when_fastavro_installed(self):
        from kafka.serde import serialize_avro_record
        try:
            import fastavro
        except ImportError:
            pytest.skip('fastavro not installed')
        schema = {'type': 'record', 'name': 'Ev', 'namespace': 'test', 'fields': [{'name': 'x', 'type': 'int'}]}
        raw = serialize_avro_record({'x': 7}, schema)
        assert isinstance(raw, bytes)
        assert len(raw) > 0

    def test_serialize_avro_import_error_message(self):
        if importlib.util.find_spec('fastavro') is not None:
            pytest.skip('fastavro is installed')
        from kafka.serde import serialize_avro_record
        with pytest.raises(RuntimeError, match='fastavro'):
            serialize_avro_record({'x': 1}, {'type': 'record', 'name': 'E', 'fields': []})
