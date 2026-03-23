"""
AES symmetric encryption (AES-GCM — authenticated).

Format for :meth:`AesGcmEncryption.encrypt` output: ``nonce (12 bytes) || ciphertext``,
where *ciphertext* includes the GCM authentication tag (as produced by ``AESGCM``).
"""

from __future__ import annotations

import os
from typing import Optional

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from .abstraction import IEncryptionUtility

_NONCE_LEN = 12


class AesGcmEncryption(IEncryptionUtility):
    """
    AES-GCM with a random 12-byte nonce per encryption.

    *key* must be 16, 24, or 32 bytes (AES-128 / AES-192 / AES-256).
    """

    def __init__(self, key: bytes) -> None:
        self._key = key
        if len(key) not in (16, 24, 32):
            raise ValueError("AES key must be 16, 24, or 32 bytes")
        self._aes = AESGCM(key)

    @staticmethod
    def generate_key(bits: int = 256) -> bytes:
        """Return a random key: *bits* must be 128, 192, or 256."""

        if bits not in (128, 192, 256):
            raise ValueError("bits must be 128, 192, or 256")
        return os.urandom(bits // 8)

    def encrypt(self, plaintext: bytes, *, associated_data: Optional[bytes] = None) -> bytes:
        nonce = os.urandom(_NONCE_LEN)
        ct = self._aes.encrypt(nonce, plaintext, associated_data)
        return nonce + ct

    def decrypt(self, ciphertext: bytes, *, associated_data: Optional[bytes] = None) -> bytes:
        if len(ciphertext) < _NONCE_LEN:
            raise ValueError("ciphertext too short")
        nonce, ct = ciphertext[:_NONCE_LEN], ciphertext[_NONCE_LEN:]
        return self._aes.decrypt(nonce, ct, associated_data)
