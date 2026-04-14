from typing import Final

RABBITMQ_BACKEND: Final[str] = "rabbitmq"
KAFKA_BACKEND: Final[str] = "kafka"
SQS_BACKEND: Final[str] = "sqs"
NATS_BACKEND: Final[str] = "nats"
MAX_DLQ_ERROR_LENGTH: Final[int] = 8000
MAX_DLQ_ATTRIBUTE_ERROR_LENGTH: Final[int] = 4000
