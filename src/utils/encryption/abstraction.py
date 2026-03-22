"""Encryption utility contracts for :mod:`utils.encryption`."""

from __future__ import annotations

from abc import abstractmethod
from typing import Optional

from ..abstraction import IUtility


class IEncryptionUtility(IUtility):
    """
    Symmetric encrypt/decrypt helpers (Fernet, AES-GCM, etc.).

    Implementations that do not support AAD ignore ``associated_data``.
    """

    @abstractmethod
    def encrypt(self, plaintext: bytes, *, associated_data: Optional[bytes] = None) -> bytes:
        """Encrypt *plaintext*; pass *associated_data* when the backend supports AEAD."""

    @abstractmethod
    def decrypt(self, ciphertext: bytes, *, associated_data: Optional[bytes] = None) -> bytes:
        """Decrypt *ciphertext*; *associated_data* must match :meth:`encrypt` when used."""


__all__ = ["IEncryptionUtility"]
