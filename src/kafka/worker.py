"""
Example Kafka worker process.

Usage:
    python -m fast_kafka.worker
"""

import asyncio

from loguru import logger

from .consumer import KafkaConsumer


async def handle_message(topic: str, value: bytes) -> None:
    logger.info("Kafka message received", topic=topic, value=value.decode("utf-8", "ignore"))


async def main() -> None:
    consumer = KafkaConsumer()
    await consumer.start()
    try:
        await consumer.loop(handle_message)
    finally:
        await consumer.stop()


def run() -> None:
    asyncio.run(main())


if __name__ == "__main__":
    run()
