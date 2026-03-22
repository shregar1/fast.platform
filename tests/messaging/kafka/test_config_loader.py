"""Tests for Kafka configuration loader."""
from tests.messaging.kafka.abstraction import IKafkaTests


import json
from unittest.mock import mock_open, patch

class TestConfigLoader(IKafkaTests):

    def test_kafka_config_dto_defaults(self):
        from kafka.dto import KafkaConfigurationDTO
        d = KafkaConfigurationDTO()
        assert d.enabled is False
        assert d.bootstrap_servers == 'localhost:9092'
        assert d.group_id == 'fastmvc-worker'
        assert d.topics == ['notifications']
        assert d.dlq_topic is None

    def test_kafka_config_load_from_file(self):
        from kafka.config_loader import KafkaConfiguration
        KafkaConfiguration._instance = None
        data = {'enabled': True, 'bootstrap_servers': 'kafka:9092', 'topics': ['events']}
        m = mock_open(read_data=json.dumps(data))
        with patch('kafka.config_loader.open', m):
            with patch('kafka.config_loader.os.getenv', return_value=None):
                cfg = KafkaConfiguration()
        dto = cfg.get_config()
        assert dto.enabled is True
        assert dto.bootstrap_servers == 'kafka:9092'
        assert dto.topics == ['events']

    def test_kafka_config_file_not_found(self):
        from kafka.config_loader import KafkaConfiguration
        KafkaConfiguration._instance = None
        with patch('kafka.config_loader.open', side_effect=FileNotFoundError()):
            with patch('kafka.config_loader.os.getenv', return_value=None):
                cfg = KafkaConfiguration()
        dto = cfg.get_config()
        assert dto.enabled is False
        assert dto.bootstrap_servers == 'localhost:9092'

    def test_kafka_config_singleton(self):
        from kafka.config_loader import KafkaConfiguration
        KafkaConfiguration._instance = None
        with patch('kafka.config_loader.open', side_effect=FileNotFoundError()):
            with patch('kafka.config_loader.os.getenv', return_value=None):
                a = KafkaConfiguration()
                b = KafkaConfiguration()
        assert a is b

    def test_kafka_config_json_decode_error(self):
        from kafka.config_loader import KafkaConfiguration
        KafkaConfiguration._instance = None
        with patch('kafka.config_loader.open', mock_open(read_data='not-json')):
            with patch('kafka.config_loader.json.load', side_effect=json.JSONDecodeError('bad', 'doc', 0)):
                with patch('kafka.config_loader.os.getenv', return_value=None):
                    cfg = KafkaConfiguration()
        dto = cfg.get_config()
        assert dto.enabled is False
