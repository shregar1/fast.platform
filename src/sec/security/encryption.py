"""Field-Level Encryption.

Provides encryption for sensitive data fields in your models.
"""

import base64
import hashlib
import hmac
import os
from dataclasses import dataclass
from typing import Any, Optional, Union

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


@dataclass
class EncryptedValue:
    """Container for encrypted data."""

    ciphertext: str
    algorithm: str = "fernet"
    key_id: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        """Execute to_dict operation.

        Returns:
            The result of the operation.
        """
        return {
            "ciphertext": self.ciphertext,
            "algorithm": self.algorithm,
            "key_id": self.key_id,
        }


class FieldEncryption:
    """Field-level encryption utility.

    Uses Fernet symmetric encryption for secure field encryption.
    """

    def __init__(
        self,
        key: Optional[str] = None,
        key_bytes: Optional[bytes] = None,
        salt: Optional[bytes] = None,
    ) -> None:
        """Execute __init__ operation.

        Args:
            key: The key parameter.
            key_bytes: The key_bytes parameter.
            salt: The salt parameter.
        """
        if key_bytes:
            self._fernet = Fernet(base64.urlsafe_b64encode(key_bytes))
        elif key:
            salt = salt or os.urandom(16)
            self._salt = salt
            derived_key = self._derive_key(key, salt)
            self._fernet = Fernet(derived_key)
        else:
            self._fernet = Fernet(Fernet.generate_key())

    @staticmethod
    def _derive_key(password: str, salt: bytes) -> bytes:
        """Derive encryption key from password using PBKDF2."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend(),
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))

    @staticmethod
    def generate_key() -> str:
        """Generate a new encryption key."""
        return Fernet.generate_key().decode()

    def encrypt(self, plaintext: Union[str, bytes]) -> str:
        """Encrypt data; returns base64-encoded ciphertext."""
        if isinstance(plaintext, str):
            plaintext = plaintext.encode()
        ciphertext = self._fernet.encrypt(plaintext)
        return ciphertext.decode()

    def decrypt(self, ciphertext: Union[str, bytes]) -> str:
        """Decrypt data."""
        if isinstance(ciphertext, str):
            ciphertext = ciphertext.encode()
        plaintext = self._fernet.decrypt(ciphertext)
        return plaintext.decode()

    def encrypt_dict(
        self,
        data: dict[str, Any],
        fields: list[str],
    ) -> dict[str, Any]:
        """Encrypt specific fields in a dictionary."""
        result = data.copy()
        for field in fields:
            if field in result and result[field] is not None:
                result[field] = self.encrypt(str(result[field]))
        return result

    def decrypt_dict(
        self,
        data: dict[str, Any],
        fields: list[str],
    ) -> dict[str, Any]:
        """Decrypt specific fields in a dictionary."""
        result = data.copy()
        for field in fields:
            if field in result and result[field] is not None:
                result[field] = self.decrypt(result[field])
        return result


class KeyRotation:
    """Key rotation manager for field encryption.

    Supports encrypting with current key while decrypting
    with multiple keys during rotation period.
    """

    def __init__(
        self,
        current_key: str,
        previous_keys: Optional[list[str]] = None,
    ) -> None:
        """Execute __init__ operation.

        Args:
            current_key: The current_key parameter.
            previous_keys: The previous_keys parameter.
        """
        self._current = FieldEncryption(key=current_key)
        self._previous = [FieldEncryption(key=k) for k in (previous_keys or [])]

    def encrypt(self, plaintext: Union[str, bytes]) -> str:
        """Encrypt with current key."""
        return self._current.encrypt(plaintext)

    def decrypt(self, ciphertext: Union[str, bytes]) -> str:
        """Decrypt with current or previous keys."""
        try:
            return self._current.decrypt(ciphertext)
        except Exception:
            pass

        for encryptor in self._previous:
            try:
                return encryptor.decrypt(ciphertext)
            except Exception:
                continue

        raise ValueError("Could not decrypt with any available key")

    def re_encrypt(self, ciphertext: Union[str, bytes]) -> str:
        """Re-encrypt data with current key."""
        plaintext = self.decrypt(ciphertext)
        return self.encrypt(plaintext)


class HashingUtility:
    """Utility for hashing sensitive data (one-way).

    Use for data that needs to be compared but not retrieved
    (e.g., lookup tokens, fingerprints).

    Extra keyword arguments (e.g. urn, user_urn) are accepted for
    compatibility with framework utilities and ignored.
    """

    def __init__(
        self,
        salt: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Execute __init__ operation.

        Args:
            salt: The salt parameter.
        """
        _ = kwargs
        self._salt = (salt or "").encode()

    def hash(self, data: Union[str, bytes]) -> str:
        """Create SHA-256 hash of data."""
        if isinstance(data, str):
            data = data.encode()
        salted = self._salt + data
        return hashlib.sha256(salted).hexdigest()

    def hash_with_pepper(
        self,
        data: Union[str, bytes],
        pepper: str,
    ) -> str:
        """Create hash with additional pepper."""
        if isinstance(data, str):
            data = data.encode()
        peppered = self._salt + data + pepper.encode()
        return hashlib.sha256(peppered).hexdigest()

    def verify(self, data: Union[str, bytes], hash_value: str) -> bool:
        """Verify data against hash."""
        computed = self.hash(data)
        return hmac.compare_digest(computed, hash_value)
