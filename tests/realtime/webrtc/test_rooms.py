"""Tests for in-memory room registry."""
from tests.realtime.webrtc.abstraction import IWebRTCTests

import pytest
from webrtc.rooms import InMemoryRoomRegistry

class TestRooms(IWebRTCTests):

    def test_registry_join_leave_and_capacity(self):
        reg = InMemoryRoomRegistry(max_participants_per_room=2)
        assert reg.join('r1', 'p1', display_name='A') is True
        assert reg.join('r1', 'p2') is True
        assert reg.join('r1', 'p3') is False
        assert len(reg.list_participants('r1')) == 2
        reg.leave('r1', 'p1')
        assert reg.join('r1', 'p3') is True

    def test_registry_idempotent_join_updates_display_name(self):
        reg = InMemoryRoomRegistry()
        assert reg.join('r1', 'p1', display_name='Old') is True
        assert reg.join('r1', 'p1', display_name='New') is True
        p = reg.list_participants('r1')[0]
        assert p.display_name == 'New'

    def test_registry_room_ids(self):
        reg = InMemoryRoomRegistry()
        reg.join('a', 'p1')
        reg.join('b', 'p2')
        assert set(reg.room_ids()) == {'a', 'b'}
        reg.leave('a', 'p1')
        assert 'a' not in reg.room_ids()

    def test_registry_rejects_zero_capacity(self):
        with pytest.raises(ValueError):
            InMemoryRoomRegistry(max_participants_per_room=0)

    def test_get_room_list_participants_leave_when_missing(self):
        reg = InMemoryRoomRegistry()
        assert reg.get_room('nope') is None
        assert reg.list_participants('nope') == []
        reg.leave('nope', 'p1')

    def test_rejoin_updates_metadata(self):
        reg = InMemoryRoomRegistry()
        assert reg.join('r1', 'p1', metadata={'a': 1}) is True
        assert reg.join('r1', 'p1', metadata={'b': 2}) is True
        p = reg.list_participants('r1')[0]
        assert p.metadata == {'a': 1, 'b': 2}
