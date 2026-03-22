from __future__ import annotations

from tests.realtime.abstraction import IRealtimeSuite

"""Test-suite markers for ``webrtc`` (mirrors ``src/webrtc/``)."""


from abc import ABC


class IWebRTCTests(IRealtimeSuite, ABC):
    """Marker base for test classes covering :mod:`webrtc`."""

    __slots__ = ()


__all__ = ["IWebRTCTests"]
