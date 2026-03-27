"""Tests for consent helpers."""

from tests.realtime.webrtc.abstraction import IWebRTCTests
from realtime.webrtc.consent import AllowAllMediaConsent, StaticDeniedPeers


class TestConsent(IWebRTCTests):
    """Represents the TestConsent class."""

    def test_allow_all_media_consent(self):
        """Execute test_allow_all_media_consent operation.

        Returns:
            The result of the operation.
        """
        assert AllowAllMediaConsent()("room", "peer") is True

    def test_static_denied_peers_blocks_pairs(self):
        """Execute test_static_denied_peers_blocks_pairs operation.

        Returns:
            The result of the operation.
        """
        gate = StaticDeniedPeers({("r1", "p1")})
        assert gate("r1", "p1") is False
        assert gate("r1", "p2") is True
