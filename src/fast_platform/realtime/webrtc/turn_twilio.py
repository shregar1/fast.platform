"""Mint short-lived TURN credentials via Twilio's **Tokens** API (STUN + TURN ``ice_servers``).

Uses only the standard library (``urllib``). Credentials are created server-side; never ship
Twilio auth tokens to browsers.

Twilio docs: https://www.twilio.com/docs/stun-turn/api — ``POST .../Accounts/{AccountSid}/Tokens.json``.
"""

from __future__ import annotations

import base64
import json
from typing import Any
from urllib import error as urlerror
from urllib import parse as urlparse
from urllib import request as urlrequest


def twilio_tokens_url(account_sid: str) -> str:
    """``POST`` target for creating a Network Traversal token (ICE servers)."""
    return f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Tokens.json"


def _normalize_ice_entry(raw: dict[str, Any]) -> dict[str, Any]:
    """Map one Twilio ``ice_servers`` element to browser ``RTCIceServer`` JSON."""
    urls = raw.get("urls") or raw.get("url")
    if urls is None:
        raise ValueError("Twilio ICE entry missing urls/url")
    out: dict[str, Any] = {"urls": urls}
    if raw.get("username") is not None:
        out["username"] = raw["username"]
    if raw.get("credential") is not None:
        out["credential"] = raw["credential"]
    return out


def fetch_twilio_turn_ice_servers(
    account_sid: str,
    auth_token: str,
    *,
    ttl_seconds: int = 86_400,
    timeout_seconds: float = 10.0,
) -> list[dict[str, Any]]:
    """POST to Twilio and return ``RTCIceServer``-shaped dicts (``urls``, optional ``username`` / ``credential``).

    Raises ``RuntimeError`` on HTTP errors or malformed JSON.

    * *account_sid* / *auth_token* — Twilio API credentials (HTTP Basic).
    * *ttl_seconds* — credential lifetime (Twilio default 24h; keep as short as practical).
    """
    url = twilio_tokens_url(account_sid)
    basic = base64.b64encode(f"{account_sid}:{auth_token}".encode()).decode("ascii")
    body = urlparse.urlencode({"Ttl": str(int(ttl_seconds))}).encode()
    req = urlrequest.Request(
        url,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Basic {basic}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )
    try:
        with urlrequest.urlopen(req, timeout=timeout_seconds) as resp:  # noqa: S310
            payload = json.loads(resp.read().decode())
    except urlerror.HTTPError as exc:
        raise RuntimeError(
            f"Twilio Tokens HTTP {exc.code}: {exc.read().decode(errors='replace')}"
        ) from exc
    except urlerror.URLError as exc:
        raise RuntimeError(f"Twilio Tokens request failed: {exc}") from exc

    ice = payload.get("ice_servers")
    if not isinstance(ice, list):
        raise RuntimeError("Twilio Tokens response missing ice_servers list")
    return [_normalize_ice_entry(x) for x in ice if isinstance(x, dict)]
