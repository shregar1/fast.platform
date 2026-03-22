from __future__ import annotations
from tests.messaging.abstraction import IMessagingSuite
"""Test-suite markers for ``queues`` (mirrors ``src/queues/``)."""


from abc import ABC



class IQueueTests(IMessagingSuite, ABC):
    """Marker base for test classes covering :mod:`queues`."""

    __slots__ = ()


__all__ = ["IQueueTests"]
