"""Tests for WebRTC signaling service."""
from tests.realtime.webrtc.abstraction import IWebRTCTests

from webrtc.consent import StaticDeniedPeers
from webrtc.signaling import WebRTCSignalingService

class TestSignaling(IWebRTCTests):

    def test_join_room(self):
        svc = WebRTCSignalingService(max_peers_per_room=2)
        assert svc.join_room('r1', 'p1') is True
        assert svc.join_room('r1', 'p2') is True
        assert svc.join_room('r1', 'p3') is False
        assert svc.list_peers('r1') == ['p1', 'p2']

    def test_join_room_idempotent(self):
        svc = WebRTCSignalingService()
        assert svc.join_room('r1', 'p1') is True
        assert svc.join_room('r1', 'p1') is True
        assert svc.list_peers('r1') == ['p1']

    def test_leave_room(self):
        svc = WebRTCSignalingService()
        svc.join_room('r1', 'p1')
        svc.join_room('r1', 'p2')
        svc.leave_room('r1', 'p1')
        assert svc.list_peers('r1') == ['p2']
        svc.leave_room('r1', 'p2')
        assert svc.list_peers('r1') == []

    def test_list_peers_exclude(self):
        svc = WebRTCSignalingService()
        svc.join_room('r1', 'p1')
        svc.join_room('r1', 'p2')
        assert svc.list_peers('r1', exclude='p1') == ['p2']

    def test_join_room_respects_before_peer_join(self):
        deny = StaticDeniedPeers({('r1', 'bad')})
        svc = WebRTCSignalingService(before_peer_join=deny)
        assert svc.join_room('r1', 'bad') is False
        assert svc.join_room('r1', 'good') is True
        assert svc.list_peers('r1') == ['good']
