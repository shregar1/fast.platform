"""Tests for consent helpers."""

from fast_webrtc.consent import AllowAllMediaConsent, StaticDeniedPeers


def test_allow_all_media_consent():
    assert AllowAllMediaConsent()("room", "peer") is True


def test_static_denied_peers_blocks_pairs():
    gate = StaticDeniedPeers({("r1", "p1")})
    assert gate("r1", "p1") is False
    assert gate("r1", "p2") is True
