"""Symmetric encryption and hashing helpers for application services."""

from __future__ import annotations

import base64
import hashlib
import hmac
import os
from typing import Optional, Union

from cryptography.exceptions import InvalidTag
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from ..errors import CryptoConfigurationError, ServiceUnavailableError


class CryptoService:
    """Fernet-based encrypt/decrypt with a shared secret or explicit Fernet key."""

    @staticmethod
    def _fernet_key_from_secret(secret: str) -> bytes:
        """Execute _fernet_key_from_secret operation.

        Args:
            secret: The secret parameter.

        Returns:
            The result of the operation.
        """
        salt = b"fastmvc.services.crypto.v1"
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=390_000)
        return base64.urlsafe_b64encode(kdf.derive(secret.encode("utf-8")))

    def __init__(
        self,
        *,
        secret: Optional[str] = None,
        fernet_key: Optional[Union[str, bytes]] = None,
    ) -> None:
        """Execute __init__ operation.

        Args:
            secret: The secret parameter.
            fernet_key: The fernet_key parameter.
        """
        if (secret is None) == (fernet_key is None):
            raise CryptoConfigurationError(
                "Provide exactly one of secret or fernet_key for CryptoService.",
            )
        if fernet_key is not None:
            key = fernet_key if isinstance(fernet_key, bytes) else fernet_key.encode("ascii")
        else:
            assert secret is not None
            key = CryptoService._fernet_key_from_secret(secret)
        self._fernet = Fernet(key)

    @staticmethod
    def generate_fernet_key() -> str:
        """Execute generate_fernet_key operation.

        Returns:
            The result of the operation.
        """
        return Fernet.generate_key().decode("ascii")

    @classmethod
    def from_env(cls, env_var: str = "CRYPTO_SECRET_KEY") -> CryptoService:
        """Execute from_env operation.

        Args:
            env_var: The env_var parameter.

        Returns:
            The result of the operation.
        """
        raw = os.environ.get(env_var)
        if not raw:
            raise ServiceUnavailableError(
                f"Environment variable {env_var} is not set.",
                responseKey="crypto.missing_env",
            )
        return cls(secret=raw)

    def encrypt(self, plain: Union[str, bytes]) -> str:
        """Execute encrypt operation.

        Args:
            plain: The plain parameter.

        Returns:
            The result of the operation.
        """
        data = plain if isinstance(plain, bytes) else plain.encode("utf-8")
        return self._fernet.encrypt(data).decode("ascii")

    def decrypt(self, token: str) -> str:
        """Execute decrypt operation.

        Args:
            token: The token parameter.

        Returns:
            The result of the operation.
        """
        return self._fernet.decrypt(token.encode("ascii")).decode("utf-8")

    def safe_decrypt(self, token: str) -> Optional[str]:
        """Execute safe_decrypt operation.

        Args:
            token: The token parameter.

        Returns:
            The result of the operation.
        """
        try:
            return self.decrypt(token)
        except (InvalidToken, ValueError):
            return None


class HashingService:
    """HMAC-SHA256 keyed hashing with a static salt."""

    def __init__(self, salt: str) -> None:
        """Execute __init__ operation.

        Args:
            salt: The salt parameter.
        """
        self._salt = salt.encode("utf-8")

    def hash(self, token: str) -> str:
        """Execute hash operation.

        Args:
            token: The token parameter.

        Returns:
            The result of the operation.
        """
        return hmac.new(self._salt, token.encode("utf-8"), hashlib.sha256).hexdigest()

    def verify(self, token: str, digest: str) -> bool:
        """Execute verify operation.

        Args:
            token: The token parameter.
            digest: The digest parameter.

        Returns:
            The result of the operation.
        """
        return hmac.compare_digest(self.hash(token), digest)


class KeyRotationService:
    """Encrypt short string values with a password-derived Fernet key (field-at-rest pattern)."""

    _SALT = b"fastmvc.keyrotation.v1"

    @staticmethod
    def _fernet_key_from_password(password: str, *, salt: bytes) -> bytes:
        """Execute _fernet_key_from_password operation.

        Args:
            password: The password parameter.
            salt: The salt parameter.

        Returns:
            The result of the operation.
        """
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=390_000)
        return base64.urlsafe_b64encode(kdf.derive(password.encode("utf-8")))

    def __init__(self, password: str) -> None:
        """Execute __init__ operation.

        Args:
            password: The password parameter.
        """
        key = KeyRotationService._fernet_key_from_password(password, salt=self._SALT)
        self._fernet = Fernet(key)

    def encrypt(self, value: str) -> str:
        """Execute encrypt operation.

        Args:
            value: The value parameter.

        Returns:
            The result of the operation.
        """
        return self._fernet.encrypt(value.encode("utf-8")).decode("ascii")

    def decrypt(self, token: str) -> str:
        """Execute decrypt operation.

        Args:
            token: The token parameter.

        Returns:
            The result of the operation.
        """
        return self._fernet.decrypt(token.encode("ascii")).decode("utf-8")


class AesGcmCryptoService:
    """AES-GCM for binary payloads with optional associated data."""

    def __init__(self, key: bytes) -> None:
        """Execute __init__ operation.

        Args:
            key: The key parameter.
        """
        if len(key) not in (16, 24, 32):
            raise CryptoConfigurationError("AES key must be 128, 192, or 256 bits.")
        self._aes = AESGCM(key)

    @staticmethod
    def generate_key(bits: int) -> bytes:
        """Execute generate_key operation.

        Args:
            bits: The bits parameter.

        Returns:
            The result of the operation.
        """
        if bits not in (128, 192, 256):
            raise CryptoConfigurationError("bits must be 128, 192, or 256.")
        return os.urandom(bits // 8)

    def encrypt(self, plain: bytes, *, associated_data: Optional[bytes] = None) -> bytes:
        """Execute encrypt operation.

        Args:
            plain: The plain parameter.
            associated_data: The associated_data parameter.

        Returns:
            The result of the operation.
        """
        nonce = os.urandom(12)
        ad = associated_data if associated_data is not None else None
        ct = self._aes.encrypt(nonce, plain, ad)
        return nonce + ct

    def decrypt(self, data: bytes, *, associated_data: Optional[bytes] = None) -> bytes:
        """Execute decrypt operation.

        Args:
            data: The data parameter.
            associated_data: The associated_data parameter.

        Returns:
            The result of the operation.
        """
        nonce, ct = data[:12], data[12:]
        ad = associated_data if associated_data is not None else None
        try:
            return self._aes.decrypt(nonce, ct, ad)
        except InvalidTag as exc:
            raise ValueError("decryption failed") from exc
