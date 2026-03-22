from __future__ import annotations

from tests.messaging.abstraction import IMessagingSuite

"""Test-suite markers for ``notifications`` (mirrors ``src/notifications/``)."""


from abc import ABC


class INotificationTests(IMessagingSuite, ABC):
    """Marker base for test classes covering :mod:`notifications`."""

    __slots__ = ()


__all__ = ["INotificationTests"]
