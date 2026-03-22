"""Tests for session TTL and cleanup hooks."""

import time

from tests.realtime.webrtc.abstraction import IWebRTCTests
from webrtc.signaling import WebRTCSignalingService


class TestSignalingTtl(IWebRTCTests):
    def test_no_ttl_backward_compatible(self):
        svc = WebRTCSignalingService(max_peers_per_room=2)
        assert svc.join_room("r", "p")
        time.sleep(0.05)
        assert svc.list_peers("r") == ["p"]

    def test_ttl_removes_peer_on_list(self):
        svc = WebRTCSignalingService(session_ttl_seconds=0.05)
        assert svc.join_room("r", "p")
        time.sleep(0.12)
        assert svc.list_peers("r") == []

    def test_ttl_callback_on_cleanup(self):
        events: list[tuple[str, str]] = []

        def on_expired(room_id: str, peer_id: str) -> None:
            events.append((room_id, peer_id))

        svc = WebRTCSignalingService(session_ttl_seconds=0.05, on_session_expired=on_expired)
        svc.join_room("r", "p")
        time.sleep(0.12)
        n = svc.cleanup_expired_sessions()
        assert n == 1
        assert events == [("r", "p")]

    def test_cleanup_expired_sessions_idempotent(self):
        svc = WebRTCSignalingService()
        assert svc.cleanup_expired_sessions() == 0
