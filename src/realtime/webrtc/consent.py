"""
Optional hooks for compliance (e.g. recording / media consent before joining a room).

Wire :class:`AllowAllMediaConsent` or a custom check into
:class:`~fast_webrtc.signaling.WebRTCSignalingService` via ``before_peer_join``.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class BeforeMediaConsentCallback(Protocol):
    """
    Return ``True`` if *peer_id* may join *room_id* and use media (camera/mic/screen).

    Use for recording consent, terms acceptance, or parental gates — **before** SDP exchange.
    """

    def __call__(self, room_id: str, peer_id: str) -> bool: ...


class AllowAllMediaConsent:
    """Default: allow every join (no gating)."""

    def __call__(self, room_id: str, peer_id: str) -> bool:
        return True


class StaticDeniedPeers:
    """Deny specific ``(room_id, peer_id)`` pairs (e.g. blocklist)."""

    def __init__(self, denied: set[tuple[str, str]]) -> None:
        self._denied = set(denied)

    def __call__(self, room_id: str, peer_id: str) -> bool:
        return (room_id, peer_id) not in self._denied
