from __future__ import annotations
"""Fernet (AES-128-CBC + HMAC) symmetric encryption.

Uses :class:`cryptography.fernet.Fernet` — token format is URL-safe base64.
"""

from .constants import FERNET_KEY_LENGTH_BYTES

import os
from typing import Optional, Union

from cryptography.fernet import Fernet, InvalidToken

from .abstraction import IEncryptionUtility


class FernetEncryption(IEncryptionUtility):
    """Encrypt/decrypt arbitrary bytes with a Fernet key."""

    def __init__(self, key: Union[str, bytes]) -> None:
        """Execute __init__ operation.

        Args:
            key: The key parameter.
        """
        if isinstance(key, str):
            key = key.encode("ascii")
        self._fernet = Fernet(key)

    @staticmethod
    def generate_key() -> bytes:
        """Return a new FERNET_KEY_LENGTH_BYTES-byte url-safe base64 key suitable for :class:`Fernet`."""
        return Fernet.generate_key()

    def encrypt(self, plaintext: bytes, *, associated_data: Optional[bytes] = None) -> bytes:
        """Execute encrypt operation.

        Args:
            plaintext: The plaintext parameter.
            associated_data: The associated_data parameter.

        Returns:
            The result of the operation.
        """
        _ = associated_data
        return self._fernet.encrypt(plaintext)

    def decrypt(self, ciphertext: bytes, *, associated_data: Optional[bytes] = None) -> bytes:
        """Execute decrypt operation.

        Args:
            ciphertext: The ciphertext parameter.
            associated_data: The associated_data parameter.

        Returns:
            The result of the operation.
        """
        _ = associated_data
        return self._fernet.decrypt(ciphertext)

    def decrypt_optional(self, ciphertext: bytes) -> bytes | None:
        """Decrypt or return ``None`` if the token is invalid or the key is wrong."""
        try:
            return self._fernet.decrypt(ciphertext)
        except InvalidToken:
            return None

    @staticmethod
    def random_key_string() -> str:
        """Human-storable Fernet key string (44 chars, url-safe base64)."""
        return Fernet.generate_key().decode("ascii")

    @staticmethod
    def encrypt_with_password(
        password: str,
        plaintext: bytes,
        *,
        salt: bytes | None = None,
        iterations: int = 100_000,
    ) -> tuple[bytes, bytes]:
        """Derive a Fernet key from *password* with PBKDF2-HMAC-SHA256 and encrypt.

        Returns ``(salt, fernet_ciphertext)`` — store *salt* alongside the ciphertext.
        """
        import base64

        from cryptography.hazmat.backends import default_backend
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

        salt = salt or os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=FERNET_KEY_LENGTH_BYTES,
            salt=salt,
            iterations=iterations,
            backend=default_backend(),
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode("utf-8")))
        return salt, Fernet(key).encrypt(plaintext)

    @staticmethod
    def decrypt_with_password(
        password: str,
        salt: bytes,
        ciphertext: bytes,
        *,
        iterations: int = 100_000,
    ) -> bytes:
        """Decrypt a blob produced by :meth:`encrypt_with_password`."""
        import base64

        from cryptography.hazmat.backends import default_backend
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=FERNET_KEY_LENGTH_BYTES,
            salt=salt,
            iterations=iterations,
            backend=default_backend(),
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode("utf-8")))
        return Fernet(key).decrypt(ciphertext)
