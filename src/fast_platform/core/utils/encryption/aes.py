from __future__ import annotations
"""AES symmetric encryption (AES-GCM — authenticated).

Format for :meth:`AesGcmEncryption.encrypt` output: ``nonce (AES_GCM_NONCE_LENGTH bytes) || ciphertext``,
where *ciphertext* includes the GCM authentication tag (as produced by ``AESGCM``).
"""

from .constants import AES_256_KEY_LENGTH_BYTES, AES_GCM_NONCE_LENGTH

import os
from typing import Optional

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from .abstraction import IEncryptionUtility

_NONCE_LEN = AES_GCM_NONCE_LENGTH


class AesGcmEncryption(IEncryptionUtility):
    """AES-GCM with a random AES_GCM_NONCE_LENGTH-byte nonce per encryption.

    *key* must be 16, 24, or AES_256_KEY_LENGTH_BYTES bytes (AES-128 / AES-192 / AES-256).
    """

    def __init__(self, key: bytes) -> None:
        """Execute __init__ operation.

        Args:
            key: The key parameter.
        """
        self._key = key
        if len(key) not in (16, 24, AES_256_KEY_LENGTH_BYTES):
            raise ValueError(f"AES key must be 16, 24, or {AES_256_KEY_LENGTH_BYTES} bytes")
        self._aes = AESGCM(key)

    @staticmethod
    def generate_key(bits: int = 256) -> bytes:
        """Return a random key: *bits* must be 128, 192, or 256."""
        if bits not in (128, 192, 256):
            raise ValueError("bits must be 128, 192, or 256")
        return os.urandom(bits // 8)

    def encrypt(self, plaintext: bytes, *, associated_data: Optional[bytes] = None) -> bytes:
        """Execute encrypt operation.

        Args:
            plaintext: The plaintext parameter.
            associated_data: The associated_data parameter.

        Returns:
            The result of the operation.
        """
        nonce = os.urandom(_NONCE_LEN)
        ct = self._aes.encrypt(nonce, plaintext, associated_data)
        return nonce + ct

    def decrypt(self, ciphertext: bytes, *, associated_data: Optional[bytes] = None) -> bytes:
        """Execute decrypt operation.

        Args:
            ciphertext: The ciphertext parameter.
            associated_data: The associated_data parameter.

        Returns:
            The result of the operation.
        """
        if len(ciphertext) < _NONCE_LEN:
            raise ValueError("ciphertext too short")
        nonce, ct = ciphertext[:_NONCE_LEN], ciphertext[_NONCE_LEN:]
        return self._aes.decrypt(nonce, ct, associated_data)
