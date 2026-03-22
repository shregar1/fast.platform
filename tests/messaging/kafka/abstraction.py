from __future__ import annotations

from tests.messaging.abstraction import IMessagingSuite

"""Test-suite markers for ``kafka`` (mirrors ``src/kafka/``)."""


from abc import ABC


class IKafkaTests(IMessagingSuite, ABC):
    """Marker base for test classes covering :mod:`kafka`."""

    __slots__ = ()


__all__ = ["IKafkaTests"]
