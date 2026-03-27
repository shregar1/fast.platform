"""Tests for :class:`messaging.kafka.idempotent.KafkaDedupeKeys`."""

from messaging.kafka.idempotent import KafkaDedupeKeys
from tests.messaging.kafka.abstraction import IKafkaTests


class TestKafkaDedupeKeys(IKafkaTests):
    """Represents the TestKafkaDedupeKeys class."""

    def test_default_dedupe_key_stable(self) -> None:
        """Execute test_default_dedupe_key_stable operation.

        Returns:
            The result of the operation.
        """
        assert KafkaDedupeKeys.default_dedupe_key(b"a") == KafkaDedupeKeys.default_dedupe_key(b"a")
        assert KafkaDedupeKeys.default_dedupe_key(b"a") != KafkaDedupeKeys.default_dedupe_key(b"b")
