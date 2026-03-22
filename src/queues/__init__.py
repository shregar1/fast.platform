"""
fast_queues – Queue backends (RabbitMQ, SQS, Azure Service Bus, NATS) for FastMVC.
"""

from from fast_platform import QueuesConfiguration, QueuesConfigurationDTO

from from fast_platform.services.queues import (
    IQueueBackend,
    QueueBroker,
    QueueMessage,
)

from .dlq import (
    DEFAULT_DLQ_SUFFIX,
    DEFAULT_QUARANTINE_SUFFIX,
    dlq_name,
    is_dlq_name,
    is_quarantine_name,
    prepare_dlq_message,
    prepare_quarantine_message,
    primary_queue_from_dlq,
    primary_queue_from_quarantine,
    quarantine_name,
)
from .envelope import (
    DELAY_SECONDS_KEY,
    ENVELOPE_VERSION_KEY,
    FAILURE_COUNT_KEY,
    LAST_ERROR_KEY,
    PAYLOAD_KEY,
    PRIORITY_KEY,
    QueueMessageEnvelope,
    should_quarantine,
)

__version__ = "0.3.0"

__all__ = [
    "DEFAULT_DLQ_SUFFIX",
    "DEFAULT_QUARANTINE_SUFFIX",
    "DELAY_SECONDS_KEY",
    "ENVELOPE_VERSION_KEY",
    "FAILURE_COUNT_KEY",
    "IQueueBackend",
    "LAST_ERROR_KEY",
    "PAYLOAD_KEY",
    "PRIORITY_KEY",
    "QueueBroker",
    "QueueMessage",
    "QueueMessageEnvelope",
    "QueuesConfiguration",
    "QueuesConfigurationDTO",
    "dlq_name",
    "is_dlq_name",
    "is_quarantine_name",
    "prepare_dlq_message",
    "prepare_quarantine_message",
    "primary_queue_from_dlq",
    "primary_queue_from_quarantine",
    "quarantine_name",
    "should_quarantine",
]
