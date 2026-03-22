"""
TTL cache for OIDC JWKS documents (JSON Web Key Sets).

Requires ``httpx`` — install ``fast_identity[oauth]``.
"""

from __future__ import annotations

import time
from typing import Any, Dict

try:
    import httpx
except Exception:  # pragma: no cover - optional
    httpx = None  # type: ignore


class JWKSCache:
    """
    Fetch and cache JWKS from a fixed URI with TTL.

    Thread-safe enough for typical async single-threaded event loop usage;
    concurrent refreshes may duplicate fetches briefly.
    """

    def __init__(self, jwks_uri: str, ttl_seconds: int = 3600) -> None:
        self._jwks_uri = jwks_uri
        self._ttl = max(0, int(ttl_seconds))
        self._keys: Dict[str, Any] | None = None
        self._expires_at: float = 0.0

    @property
    def jwks_uri(self) -> str:
        return self._jwks_uri

    def _stale(self) -> bool:
        return self._keys is None or time.monotonic() >= self._expires_at

    async def _fetch(self) -> Dict[str, Any]:
        if httpx is None:
            raise RuntimeError("httpx is required for JWKS. Install fast_identity[oauth].")
        async with httpx.AsyncClient() as client:
            resp = await client.get(self._jwks_uri, headers={"Accept": "application/json"}, timeout=15.0)
            resp.raise_for_status()
            data = resp.json()
        if not isinstance(data, dict):
            raise ValueError("JWKS response must be a JSON object")
        return data

    async def get_jwks(self) -> Dict[str, Any]:
        """Return cached JWKS, fetching when missing or expired."""
        if not self._stale():
            assert self._keys is not None
            return self._keys
        keys = await self._fetch()
        self._keys = keys
        self._expires_at = time.monotonic() + float(self._ttl)
        return keys

    async def refresh(self) -> Dict[str, Any]:
        """Force a fetch and refresh the TTL."""
        keys = await self._fetch()
        self._keys = keys
        self._expires_at = time.monotonic() + float(self._ttl)
        return keys
