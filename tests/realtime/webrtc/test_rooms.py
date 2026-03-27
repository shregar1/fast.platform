"""Tests for in-memory room registry."""

import pytest

from tests.realtime.webrtc.abstraction import IWebRTCTests
from fast_platform.realtime.webrtc.rooms import InMemoryRoomRegistry


class TestRooms(IWebRTCTests):
    """Represents the TestRooms class."""

    def test_registry_join_leave_and_capacity(self):
        """Execute test_registry_join_leave_and_capacity operation.

        Returns:
            The result of the operation.
        """
        reg = InMemoryRoomRegistry(max_participants_per_room=2)
        assert reg.join("r1", "p1", display_name="A") is True
        assert reg.join("r1", "p2") is True
        assert reg.join("r1", "p3") is False
        assert len(reg.list_participants("r1")) == 2
        reg.leave("r1", "p1")
        assert reg.join("r1", "p3") is True

    def test_registry_idempotent_join_updates_display_name(self):
        """Execute test_registry_idempotent_join_updates_display_name operation.

        Returns:
            The result of the operation.
        """
        reg = InMemoryRoomRegistry()
        assert reg.join("r1", "p1", display_name="Old") is True
        assert reg.join("r1", "p1", display_name="New") is True
        p = reg.list_participants("r1")[0]
        assert p.display_name == "New"

    def test_registry_room_ids(self):
        """Execute test_registry_room_ids operation.

        Returns:
            The result of the operation.
        """
        reg = InMemoryRoomRegistry()
        reg.join("a", "p1")
        reg.join("b", "p2")
        assert set(reg.room_ids()) == {"a", "b"}
        reg.leave("a", "p1")
        assert "a" not in reg.room_ids()

    def test_registry_rejects_zero_capacity(self):
        """Execute test_registry_rejects_zero_capacity operation.

        Returns:
            The result of the operation.
        """
        with pytest.raises(ValueError):
            InMemoryRoomRegistry(max_participants_per_room=0)

    def test_get_room_list_participants_leave_when_missing(self):
        """Execute test_get_room_list_participants_leave_when_missing operation.

        Returns:
            The result of the operation.
        """
        reg = InMemoryRoomRegistry()
        assert reg.get_room("nope") is None
        assert reg.list_participants("nope") == []
        reg.leave("nope", "p1")

    def test_rejoin_updates_metadata(self):
        """Execute test_rejoin_updates_metadata operation.

        Returns:
            The result of the operation.
        """
        reg = InMemoryRoomRegistry()
        assert reg.join("r1", "p1", metadata={"a": 1}) is True
        assert reg.join("r1", "p1", metadata={"b": 2}) is True
        p = reg.list_participants("r1")[0]
        assert p.metadata == {"a": 1, "b": 2}
