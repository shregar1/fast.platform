"""Example Kafka worker process.

Usage:
    python -m fast_kafka.worker
"""

import asyncio

from loguru import logger

from .consumer import KafkaConsumer


async def handle_message(topic: str, value: bytes) -> None:
    """Execute handle_message operation.

    Args:
        topic: The topic parameter.
        value: The value parameter.

    Returns:
        The result of the operation.
    """
    logger.info("Kafka message received", topic=topic, value=value.decode("utf-8", "ignore"))


async def main() -> None:
    """Execute main operation.

    Returns:
        The result of the operation.
    """
    consumer = KafkaConsumer()
    await consumer.start()
    try:
        await consumer.loop(handle_message)
    finally:
        await consumer.stop()


def run() -> None:
    """Execute run operation.

    Returns:
        The result of the operation.
    """
    asyncio.run(main())


if __name__ == "__main__":
    run()
