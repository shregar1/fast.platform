"""Tests for WebRTC signaling service."""

from tests.realtime.webrtc.abstraction import IWebRTCTests
from fast_platform.realtime.webrtc.consent import StaticDeniedPeers
from fast_platform.realtime.webrtc.signaling import WebRTCSignalingService


class TestSignaling(IWebRTCTests):
    """Represents the TestSignaling class."""

    def test_join_room(self):
        """Execute test_join_room operation.

        Returns:
            The result of the operation.
        """
        svc = WebRTCSignalingService(max_peers_per_room=2)
        assert svc.join_room("r1", "p1") is True
        assert svc.join_room("r1", "p2") is True
        assert svc.join_room("r1", "p3") is False
        assert svc.list_peers("r1") == ["p1", "p2"]

    def test_join_room_idempotent(self):
        """Execute test_join_room_idempotent operation.

        Returns:
            The result of the operation.
        """
        svc = WebRTCSignalingService()
        assert svc.join_room("r1", "p1") is True
        assert svc.join_room("r1", "p1") is True
        assert svc.list_peers("r1") == ["p1"]

    def test_leave_room(self):
        """Execute test_leave_room operation.

        Returns:
            The result of the operation.
        """
        svc = WebRTCSignalingService()
        svc.join_room("r1", "p1")
        svc.join_room("r1", "p2")
        svc.leave_room("r1", "p1")
        assert svc.list_peers("r1") == ["p2"]
        svc.leave_room("r1", "p2")
        assert svc.list_peers("r1") == []

    def test_list_peers_exclude(self):
        """Execute test_list_peers_exclude operation.

        Returns:
            The result of the operation.
        """
        svc = WebRTCSignalingService()
        svc.join_room("r1", "p1")
        svc.join_room("r1", "p2")
        assert svc.list_peers("r1", exclude="p1") == ["p2"]

    def test_join_room_respects_before_peer_join(self):
        """Execute test_join_room_respects_before_peer_join operation.

        Returns:
            The result of the operation.
        """
        deny = StaticDeniedPeers({("r1", "bad")})
        svc = WebRTCSignalingService(before_peer_join=deny)
        assert svc.join_room("r1", "bad") is False
        assert svc.join_room("r1", "good") is True
        assert svc.list_peers("r1") == ["good"]
