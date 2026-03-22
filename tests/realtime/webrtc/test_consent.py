"""Tests for consent helpers."""
from tests.realtime.webrtc.abstraction import IWebRTCTests

from webrtc.consent import AllowAllMediaConsent, StaticDeniedPeers

class TestConsent(IWebRTCTests):

    def test_allow_all_media_consent(self):
        assert AllowAllMediaConsent()('room', 'peer') is True

    def test_static_denied_peers_blocks_pairs(self):
        gate = StaticDeniedPeers({('r1', 'p1')})
        assert gate('r1', 'p1') is False
        assert gate('r1', 'p2') is True
