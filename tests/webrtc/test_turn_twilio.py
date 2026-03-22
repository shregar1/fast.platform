"""Tests for Twilio TURN credential minting (mocked HTTP)."""

import io
import json
from unittest.mock import patch
from urllib.error import HTTPError, URLError

import pytest

from fast_webrtc.turn_twilio import fetch_twilio_turn_ice_servers, twilio_tokens_url


def test_twilio_tokens_url_contains_account():
    assert "ACtest" in twilio_tokens_url("ACtest")
    assert "Tokens.json" in twilio_tokens_url("ACtest")


@patch("fast_webrtc.turn_twilio.urlrequest.urlopen")
def test_fetch_twilio_turn_ice_servers_parses_response(mock_urlopen):
    payload = {
        "ice_servers": [
            {"urls": "stun:global.stun.twilio.com:3478"},
            {
                "urls": "turn:global.turn.twilio.com:3478?transport=udp",
                "username": "u",
                "credential": "p",
            },
        ]
    }

    class _Resp:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def read(self):
            return json.dumps(payload).encode()

    mock_urlopen.return_value = _Resp()

    out = fetch_twilio_turn_ice_servers("ACxxx", "token", ttl_seconds=3600)
    assert len(out) == 2
    assert out[0]["urls"] == "stun:global.stun.twilio.com:3478"
    assert out[1]["username"] == "u"
    assert out[1]["credential"] == "p"
    mock_urlopen.assert_called_once()


@patch("fast_webrtc.turn_twilio.urlrequest.urlopen")
def test_fetch_twilio_raises_on_bad_json(mock_urlopen):
    class _Resp:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def read(self):
            return b"{}"

    mock_urlopen.return_value = _Resp()

    with pytest.raises(RuntimeError, match="ice_servers"):
        fetch_twilio_turn_ice_servers("ACx", "t")


@patch("fast_webrtc.turn_twilio.urlrequest.urlopen")
def test_normalize_rejects_missing_urls(mock_urlopen):
    class _Resp:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def read(self):
            return json.dumps({"ice_servers": [{}]}).encode()

    mock_urlopen.return_value = _Resp()

    with pytest.raises(ValueError, match="urls"):
        fetch_twilio_turn_ice_servers("ACx", "t")


@patch("fast_webrtc.turn_twilio.urlrequest.urlopen")
def test_fetch_twilio_turn_http_error(mock_urlopen):
    fp = io.BytesIO(b"auth failed")
    mock_urlopen.side_effect = HTTPError(
        "https://api.twilio.com/x", 401, "Unauthorized", {}, fp
    )
    with pytest.raises(RuntimeError, match="HTTP 401"):
        fetch_twilio_turn_ice_servers("ACx", "t")


@patch("fast_webrtc.turn_twilio.urlrequest.urlopen")
def test_fetch_twilio_turn_url_error(mock_urlopen):
    mock_urlopen.side_effect = URLError("network down")
    with pytest.raises(RuntimeError, match="request failed"):
        fetch_twilio_turn_ice_servers("ACx", "t")
