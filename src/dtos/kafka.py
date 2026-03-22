"""
DTOs for Kafka configuration settings.
"""

from .abstraction import IDTO

from typing import Any, List, Optional

from pydantic import Field


class KafkaConfigurationDTO(IDTO):
    """DTO for Kafka configuration."""

    enabled: bool = False
    bootstrap_servers: str = "localhost:9092"
    group_id: str = "fastmvc-worker"
    topics: List[str] = ["notifications"]
    enable_auto_commit: bool = True
    dlq_topic: Optional[str] = Field(
        default=None,
        description="Default dead-letter topic for producer helpers when no topic is passed explicitly.",
    )


class KafkaJsonEnvelope(IDTO):
    """
    Versioned JSON envelope for producer payloads (``Content-Type: application/json``).

    Use :meth:`fast_kafka.producer.KafkaProducer.send_json_envelope` or serialize with
    :meth:`to_json_bytes`.
    """

    schema_version: str = Field(default="1", description="Contract / schema version for consumers.")
    message_type: str = Field(..., description="Logical event or command name.")
    payload: dict[str, Any] = Field(default_factory=dict)
    metadata: Optional[dict[str, Any]] = Field(
        default=None,
        description="Optional tracing or correlation fields (ids, tenant, etc.).",
    )

    def to_json_bytes(self) -> bytes:
        """UTF-8 JSON bytes suitable for ``send`` / ``send_json_envelope``."""
        return self.model_dump_json(exclude_none=True).encode("utf-8")


def kafka_json_envelope_json_schema() -> dict[str, Any]:
    """JSON Schema for :class:`KafkaJsonEnvelope` (Pydantic v2 ``model_json_schema``)."""
    return KafkaJsonEnvelope.model_json_schema()
