"""Shared cryptographic digests and Fernet key material (no I/O).

Centralizes patterns that were duplicated across ``security``, ``service``,
``identity``, ``kafka``, and :mod:`utils.idempotency`.
"""

from __future__ import annotations

import base64
import hashlib

from .abstraction import IDigestsUtility

__all__ = ["Digests", "IDigestsUtility"]


class Digests(IDigestsUtility):
    """SHA-256 and Fernet key derivation helpers."""

    @staticmethod
    def sha256_hex_utf8(text: str) -> str:
        """Lowercase hex SHA-256 of UTF-8 encoded *text*."""
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    @staticmethod
    def sha256_hex_bytes(data: bytes) -> str:
        """Lowercase hex SHA-256 of raw *data*."""
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def fernet_key_bytes_from_utf8_secret(secret: str) -> bytes:
        """Derive a 32-byte URL-safe key suitable for :class:`cryptography.fernet.Fernet`.

        Uses SHA-256 over UTF-8 *secret*, then base64-url encoding — same scheme as
        :mod:`security.llm_provider_keys` and :class:`service.crypto.CryptoService`
        (secret-based mode).
        """
        return base64.urlsafe_b64encode(hashlib.sha256(secret.encode("utf-8")).digest())
