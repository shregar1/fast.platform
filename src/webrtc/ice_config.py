"""
ICE server lists from :class:`dtos.realtime.RealtimeConfigurationDTO`.

Also provides helpers to map legacy flat STUN/TURN URL lists from :class:`~webrtc.dto.WebRTCConfigurationDTO`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from dtos import RealtimeConfigurationDTO

    from .dto import WebRTCConfigurationDTO


def rtc_ice_servers_for_client(cfg: RealtimeConfigurationDTO) -> list[dict[str, Any]]:
    """
    Build a JSON-serializable list of ``RTCIceServer``-shaped dicts for browser clients.

    When ``cfg.webrtc.enabled`` is false, returns an empty list.
    """
    w = cfg.webrtc
    if not w.enabled:
        return []
    return [
        {k: v for k, v in s.model_dump(exclude_none=True).items() if v != ""} for s in w.ice_servers
    ]


def ice_servers_from_legacy_webrtc_dto(dto: WebRTCConfigurationDTO) -> list[dict[str, Any]]:
    """
    Map ``stun_servers`` / ``turn_servers`` URL strings to minimal ``{"urls": ...}`` entries.

    Prefer :func:`rtc_ice_servers_for_client` with :class:`RealtimeConfigurationDTO` when possible.
    """
    out: list[dict[str, Any]] = []
    for u in dto.stun_servers:
        out.append({"urls": u})
    for u in dto.turn_servers:
        out.append({"urls": u})
    return out
