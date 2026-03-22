"""Tests for :class:`kafka.idempotent.KafkaDedupeKeys`."""
from tests.messaging.kafka.abstraction import IKafkaTests


from kafka.idempotent import KafkaDedupeKeys


class TestKafkaDedupeKeys(IKafkaTests):
    def test_default_dedupe_key_stable(self) -> None:
        assert KafkaDedupeKeys.default_dedupe_key(b"a") == KafkaDedupeKeys.default_dedupe_key(b"a")
        assert KafkaDedupeKeys.default_dedupe_key(b"a") != KafkaDedupeKeys.default_dedupe_key(b"b")
