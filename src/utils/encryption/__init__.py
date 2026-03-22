"""
Generic symmetric encryption helpers (Fernet, AES-GCM).

Prefer :class:`FernetEncryption` for simple string/blob storage; use
:class:`AesGcmEncryption` when you need AES directly or associated authenticated data (AAD).

Depends on the ``cryptography`` package (already a fast-platform dependency).
"""

from .abstraction import IEncryptionUtility
from .aes import AesGcmEncryption
from .fernet import FernetEncryption

__all__ = [
    "AesGcmEncryption",
    "FernetEncryption",
    "IEncryptionUtility",
]
