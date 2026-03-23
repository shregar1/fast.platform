"""
fast_kafka – Kafka integration for FastMVC.
"""

from __future__ import annotations

from core.configuration.kafka import KafkaConfiguration
from core.dtos.kafka import KafkaConfigurationDTO, KafkaJsonEnvelope

from .consumer import KafkaConsumer
from .dlq import (
    DLQ_HEADER_ERROR,
    DLQ_HEADER_OFFSET,
    DLQ_HEADER_ORIGINAL_TOPIC,
    DLQ_HEADER_PARTITION,
    make_dlq_headers,
)
from .health import KafkaClusterHealth, describe_cluster_health
from .idempotent import DedupeStore, InMemoryDedupeStore, KafkaDedupeKeys
from .lag import ConsumerLagEntry, poll_consumer_lag
from .outbox import (
    POSTGRES_OUTBOX_DDL,
    OutboxMessage,
    publish_outbox_batch,
    run_outbox_publisher_loop,
)
from .producer import KafkaProducer
from .serde import serialize_avro_record, serialize_protobuf

__version__ = "0.3.0"

__all__ = [
    "DLQ_HEADER_ERROR",
    "DLQ_HEADER_OFFSET",
    "DLQ_HEADER_ORIGINAL_TOPIC",
    "DLQ_HEADER_PARTITION",
    "DedupeStore",
    "ConsumerLagEntry",
    "InMemoryDedupeStore",
    "KafkaClusterHealth",
    "KafkaConfiguration",
    "KafkaConsumer",
    "KafkaConfigurationDTO",
    "KafkaJsonEnvelope",
    "KafkaProducer",
    "OutboxMessage",
    "POSTGRES_OUTBOX_DDL",
    "__version__",
    "KafkaDedupeKeys",
    "describe_cluster_health",
    "make_dlq_headers",
    "poll_consumer_lag",
    "publish_outbox_batch",
    "run_outbox_publisher_loop",
    "serialize_avro_record",
    "serialize_protobuf",
]
