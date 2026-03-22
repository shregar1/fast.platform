"""
Multiple OIDC issuers during migrations: one JWKS URI per issuer string.
"""

from __future__ import annotations

from typing import Dict

from .jwks_cache import JWKSCache


class MultiIssuerJWKSCache:
    """
    Route ``iss`` values to the correct JWKS endpoint.

    Pass a map of issuer URL (must match JWT ``iss`` claim) to JWKS URI.
    """

    def __init__(
        self,
        issuer_to_jwks_uri: Dict[str, str],
        ttl_seconds: int = 3600,
    ) -> None:
        if not issuer_to_jwks_uri:
            raise ValueError("issuer_to_jwks_uri must not be empty")
        self._ttl = ttl_seconds
        self._caches: Dict[str, JWKSCache] = {
            iss: JWKSCache(uri, ttl_seconds=ttl_seconds) for iss, uri in issuer_to_jwks_uri.items()
        }

    def issuers(self) -> frozenset[str]:
        return frozenset(self._caches.keys())

    def has_issuer(self, issuer: str) -> bool:
        return issuer in self._caches

    async def get_jwks(self, issuer: str):
        if issuer not in self._caches:
            raise KeyError(issuer)
        return await self._caches[issuer].get_jwks()

    async def refresh_issuer(self, issuer: str):
        if issuer not in self._caches:
            raise KeyError(issuer)
        return await self._caches[issuer].refresh()
