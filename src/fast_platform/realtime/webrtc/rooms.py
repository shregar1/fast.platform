"""Optional in-memory room / participant registry for small apps.

This is **app-level** metadata (names, roles). Pair with
:class:`~fast_webrtc.signaling.WebRTCSignalingService` for SDP routing peers.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from loguru import logger


@dataclass
class Participant:
    """A participant in a room."""

    peer_id: str
    display_name: str = ""
    joined_at: float = field(default_factory=time.monotonic)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Room:
    """Room metadata and participant map keyed by ``peer_id``."""

    room_id: str
    created_at: float = field(default_factory=time.monotonic)
    participants: dict[str, Participant] = field(default_factory=dict)


class InMemoryRoomRegistry:
    """In-memory registry: create rooms, add/remove participants, bounded capacity.

    Not distributed; suitable for demos and single-node deployments.
    """

    def __init__(self, max_participants_per_room: int = 8) -> None:
        """Execute __init__ operation.

        Args:
            max_participants_per_room: The max_participants_per_room parameter.
        """
        if max_participants_per_room < 1:
            raise ValueError("max_participants_per_room must be >= 1")
        self._max = max_participants_per_room
        self._rooms: Dict[str, Room] = {}

    def get_or_create_room(self, room_id: str) -> Room:
        """Execute get_or_create_room operation.

        Args:
            room_id: The room_id parameter.

        Returns:
            The result of the operation.
        """
        if room_id not in self._rooms:
            self._rooms[room_id] = Room(room_id=room_id)
            logger.debug("Created room {}", room_id)
        return self._rooms[room_id]

    def get_room(self, room_id: str) -> Optional[Room]:
        """Execute get_room operation.

        Args:
            room_id: The room_id parameter.

        Returns:
            The result of the operation.
        """
        return self._rooms.get(room_id)

    def join(
        self,
        room_id: str,
        peer_id: str,
        *,
        display_name: str = "",
        metadata: Optional[dict[str, Any]] = None,
    ) -> bool:
        """Execute join operation.

        Args:
            room_id: The room_id parameter.
            peer_id: The peer_id parameter.
            display_name: The display_name parameter.
            metadata: The metadata parameter.

        Returns:
            The result of the operation.
        """
        room = self.get_or_create_room(room_id)
        if peer_id in room.participants:
            p = room.participants[peer_id]
            p.display_name = display_name or p.display_name
            if metadata:
                p.metadata.update(metadata)
            return True
        if len(room.participants) >= self._max:
            logger.warning("Room {} full (max {})", room_id, self._max)
            return False
        room.participants[peer_id] = Participant(
            peer_id=peer_id,
            display_name=display_name,
            metadata=dict(metadata or {}),
        )
        logger.debug("Participant {} joined room {}", peer_id, room_id)
        return True

    def leave(self, room_id: str, peer_id: str) -> None:
        """Execute leave operation.

        Args:
            room_id: The room_id parameter.
            peer_id: The peer_id parameter.

        Returns:
            The result of the operation.
        """
        room = self._rooms.get(room_id)
        if not room:
            return
        room.participants.pop(peer_id, None)
        if not room.participants:
            del self._rooms[room_id]
            logger.debug("Removed empty room {}", room_id)

    def list_participants(self, room_id: str) -> List[Participant]:
        """Execute list_participants operation.

        Args:
            room_id: The room_id parameter.

        Returns:
            The result of the operation.
        """
        room = self._rooms.get(room_id)
        if not room:
            return []
        return list(room.participants.values())

    def room_ids(self) -> List[str]:
        """Execute room_ids operation.

        Returns:
            The result of the operation.
        """
        return list(self._rooms.keys())
