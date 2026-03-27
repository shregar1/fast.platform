"""Service-to-service API key helpers: SHA-256 hex digest and constant-time verify.

Not JWT — use alongside bearer tokens for machine clients.
"""

from __future__ import annotations

import hmac
from typing import Dict, Optional

from core.utils.digests import Digests


class ApiKeyHashes:
    """SHA-256 hex digest and verification for raw API key strings."""

    @staticmethod
    def hash_api_key_sha256_hex(api_key: str) -> str:
        """Return lowercase hex SHA-256 of the raw secret string."""
        return Digests.sha256_hex_utf8(api_key)

    @staticmethod
    def verify_api_key_sha256_hex(api_key: str, expected_hex_hash: str) -> bool:
        """Constant-time compare of SHA-256 hex digest (case-insensitive hex)."""
        got = ApiKeyHashes.hash_api_key_sha256_hex(api_key)
        exp = expected_hex_hash.strip().lower()
        if len(exp) != len(got):
            return False
        return hmac.compare_digest(got, exp)


class InMemoryHashedApiKeyStore:
    """Register pre-hashed keys (e.g. from env/DB) and verify presented secrets.

    ``register`` stores ``key_id -> hex_hash``; ``verify`` tries the incoming
    secret against every registered hash (suitable for a small set of service keys).
    """

    def __init__(self) -> None:
        """Execute __init__ operation."""
        self._by_id: Dict[str, str] = {}

    def register(self, key_id: str, hex_hash: str) -> None:
        """Execute register operation.

        Args:
            key_id: The key_id parameter.
            hex_hash: The hex_hash parameter.

        Returns:
            The result of the operation.
        """
        self._by_id[key_id] = hex_hash.strip().lower()

    def remove(self, key_id: str) -> None:
        """Execute remove operation.

        Args:
            key_id: The key_id parameter.

        Returns:
            The result of the operation.
        """
        self._by_id.pop(key_id, None)

    def verify(self, api_key: str) -> Optional[str]:
        """If ``api_key`` matches a registered hash, return that key's ``key_id``;
        otherwise ``None``.
        """
        if not self._by_id:
            return None
        digest = ApiKeyHashes.hash_api_key_sha256_hex(api_key)
        for kid, hx in self._by_id.items():
            if len(hx) != len(digest):
                continue
            if hmac.compare_digest(digest, hx):
                return kid
        return None
