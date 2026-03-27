"""Optional binary serialization helpers (Protobuf / Avro) alongside JSON envelopes.

Install extras: ``pip install fast_kafka[protobuf]`` or ``fast_kafka[avro]``.
"""

from __future__ import annotations

from typing import Any


def serialize_protobuf(message: Any) -> bytes:
    """Serialize a ``google.protobuf.Message`` (or any object with ``SerializeToString()``).

    Requires the ``protobuf`` package when using generated stubs.
    """
    ser = getattr(message, "SerializeToString", None)
    if ser is None:
        raise TypeError("message must provide SerializeToString()")
    return ser()


def serialize_avro_record(record: dict[str, Any], schema: dict[str, Any]) -> bytes:
    """Encode *record* with *schema* using ``fastavro`` schemaless writer.

    Install: ``pip install fast_kafka[avro]`` (pulls ``fastavro``).
    """
    try:
        import fastavro  # type: ignore[import-untyped]
    except ImportError as exc:
        raise RuntimeError(
            "fastavro is required for Avro serialization; install with: pip install fast_kafka[avro]"
        ) from exc
    from io import BytesIO

    parsed = fastavro.parse_schema(schema)
    buf = BytesIO()
    fastavro.schemaless_writer(buf, parsed, record)
    return buf.getvalue()
