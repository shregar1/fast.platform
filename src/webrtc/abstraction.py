"""webrtc package abstractions."""

from __future__ import annotations

from abc import ABC


class IWebRTC(ABC):
    """Marker base for concrete types in the ``webrtc`` package."""

    __slots__ = ()


__all__ = ["IWebRTC"]
