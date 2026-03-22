from __future__ import annotations
from tests.messaging.abstraction import IMessagingSuite
"""Test-suite markers for ``jobs`` (mirrors ``src/jobs/``)."""


from abc import ABC



class IJobTests(IMessagingSuite, ABC):
    """Marker base for test classes covering :mod:`jobs`."""

    __slots__ = ()


__all__ = ["IJobTests"]
