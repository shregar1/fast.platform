from __future__ import annotations
from tests.realtime.abstraction import IRealtimeSuite
"""Test-suite markers for ``channels`` (mirrors ``src/channels/``)."""


from abc import ABC



class IChannelTests(IRealtimeSuite, ABC):
    """Marker base for test classes covering :mod:`channels`."""

    __slots__ = ()


__all__ = ["IChannelTests"]
