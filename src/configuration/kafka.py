"""
Kafka configuration loader.

Reads from config/kafka/config.json (or FASTMVC_KAFKA_CONFIG_PATH).
"""

import json
import os
from typing import Optional

from loguru import logger

from dtos.kafka import KafkaConfigurationDTO


class KafkaConfiguration:
    """Configuration manager for Kafka settings."""

    _instance: Optional["KafkaConfiguration"] = None

    def __new__(cls) -> "KafkaConfiguration":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.config = {}
            cls._instance.load_config()
        return cls._instance

    def load_config(self) -> None:
        path = os.getenv("FASTMVC_KAFKA_CONFIG_PATH")
        if not path:
            base = os.getenv("FASTMVC_CONFIG_BASE")
            path = (
                os.path.join(base, "kafka", "config.json") if base else "config/kafka/config.json"
            )
        try:
            with open(path) as f:
                self.config = json.load(f)
            logger.debug("Kafka config loaded successfully.")
        except FileNotFoundError:
            logger.debug("Kafka config file not found.")
            self.config = {}
        except json.JSONDecodeError:
            logger.debug("Error decoding Kafka config file.")
            self.config = {}

    def get_config(self) -> KafkaConfigurationDTO:
        return KafkaConfigurationDTO(
            enabled=self.config.get("enabled", False),
            bootstrap_servers=self.config.get("bootstrap_servers", "localhost:9092"),
            group_id=self.config.get("group_id", "fastmvc-worker"),
            topics=self.config.get("topics", ["notifications"]),
            enable_auto_commit=self.config.get("enable_auto_commit", True),
            dlq_topic=self.config.get("dlq_topic"),
        )
