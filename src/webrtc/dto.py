"""
DTO for WebRTC signaling configuration settings.
"""

from typing import List

from pydantic import BaseModel


class WebRTCConfigurationDTO(BaseModel):
    """
    DTO for WebRTC configuration.

    Fields:
        enabled (bool): Whether WebRTC signaling APIs are enabled.
        stun_servers (list[str]): STUN server URLs.
        turn_servers (list[str]): TURN server URLs.
        max_peers_per_room (int): Maximum peers allowed in a single room.
    """

    enabled: bool = False
    stun_servers: List[str] = []
    turn_servers: List[str] = []
    max_peers_per_room: int = 8
