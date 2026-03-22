"""Tests for optional Protobuf / Avro serde helpers."""

import importlib.util

import pytest


def test_serialize_protobuf_duck_typing():
    from fast_kafka.serde import serialize_protobuf

    class Msg:
        def SerializeToString(self):
            return b"bin"

    assert serialize_protobuf(Msg()) == b"bin"


def test_serialize_protobuf_rejects_plain_object():
    from fast_kafka.serde import serialize_protobuf

    with pytest.raises(TypeError):
        serialize_protobuf(object())


def test_serialize_avro_when_fastavro_installed():
    from fast_kafka.serde import serialize_avro_record

    try:
        import fastavro  # noqa: F401
    except ImportError:
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


def test_serialize_avro_import_error_message():
    if importlib.util.find_spec("fastavro") is not None:
        pytest.skip("fastavro is installed")

    from fast_kafka.serde import serialize_avro_record

    with pytest.raises(RuntimeError, match="fastavro"):
        serialize_avro_record({"x": 1}, {"type": "record", "name": "E", "fields": []})
