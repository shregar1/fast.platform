"""Tests for Kafka configuration loader."""

import json
from unittest.mock import mock_open, patch

from tests.messaging.kafka.abstraction import IKafkaTests


class TestConfigLoader(IKafkaTests):
    """Represents the TestConfigLoader class."""

    def test_kafka_config_dto_defaults(self):
        """Execute test_kafka_config_dto_defaults operation.

        Returns:
            The result of the operation.
        """
        from core.dtos.kafka import KafkaConfigurationDTO

        d = KafkaConfigurationDTO()
        assert d.enabled is False
        assert d.bootstrap_servers == "localhost:9092"
        assert d.group_id == "fastmvc-worker"
        assert d.topics == ["notifications"]
        assert d.dlq_topic is None

    def test_kafka_config_load_from_file(self):
        """Execute test_kafka_config_load_from_file operation.

        Returns:
            The result of the operation.
        """
        from core.configuration.kafka import KafkaConfiguration

        KafkaConfiguration._instance = None
        data = {"enabled": True, "bootstrap_servers": "kafka:9092", "topics": ["events"]}
        m = mock_open(read_data=json.dumps(data))
        with patch("fast_platform.core.configuration.kafka.open", m):
            with patch("fast_platform.core.configuration.kafka.os.getenv", return_value=None):
                cfg = KafkaConfiguration()
        dto = cfg.get_config()
        assert dto.enabled is True
        assert dto.bootstrap_servers == "kafka:9092"
        assert dto.topics == ["events"]

    def test_kafka_config_file_not_found(self):
        """Execute test_kafka_config_file_not_found operation.

        Returns:
            The result of the operation.
        """
        from core.configuration.kafka import KafkaConfiguration

        KafkaConfiguration._instance = None
        with patch("fast_platform.core.configuration.kafka.open", side_effect=FileNotFoundError()):
            with patch("fast_platform.core.configuration.kafka.os.getenv", return_value=None):
                cfg = KafkaConfiguration()
        dto = cfg.get_config()
        assert dto.enabled is False
        assert dto.bootstrap_servers == "localhost:9092"

    def test_kafka_config_singleton(self):
        """Execute test_kafka_config_singleton operation.

        Returns:
            The result of the operation.
        """
        from core.configuration.kafka import KafkaConfiguration

        KafkaConfiguration._instance = None
        with patch("fast_platform.core.configuration.kafka.open", side_effect=FileNotFoundError()):
            with patch("fast_platform.core.configuration.kafka.os.getenv", return_value=None):
                a = KafkaConfiguration()
                b = KafkaConfiguration()
        assert a is b

    def test_kafka_config_json_decode_error(self):
        """Execute test_kafka_config_json_decode_error operation.

        Returns:
            The result of the operation.
        """
        from core.configuration.kafka import KafkaConfiguration

        KafkaConfiguration._instance = None
        with patch("fast_platform.core.configuration.kafka.open", mock_open(read_data="not-json")):
            with patch(
                "fast_platform.core.configuration.kafka.json.load",
                side_effect=json.JSONDecodeError("bad", "doc", 0),
            ):
                with patch("fast_platform.core.configuration.kafka.os.getenv", return_value=None):
                    cfg = KafkaConfiguration()
        dto = cfg.get_config()
        assert dto.enabled is False
