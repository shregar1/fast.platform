"""Tests for :mod:`service.crypto`."""

from __future__ import annotations

import pytest

from fast_platform.core.errors import CryptoConfigurationError, ServiceUnavailableError
from fast_platform.core.service.crypto import (
    AesGcmCryptoService,
    CryptoService,
    HashingService,
    KeyRotationService,
)
from tests.core.service.abstraction import IServiceTests


class TestCryptoService(IServiceTests):
    """Represents the TestCryptoService class."""

    def test_secret_roundtrip(self) -> None:
        """Execute test_secret_roundtrip operation.

        Returns:
            The result of the operation.
        """
        svc = CryptoService(secret="unit-test-secret-32chars-min")
        plain = "sensitive-payload"
        ct = svc.encrypt(plain)
        assert ct != plain
        assert svc.decrypt(ct) == plain

    def test_fernet_key_roundtrip(self) -> None:
        """Execute test_fernet_key_roundtrip operation.

        Returns:
            The result of the operation.
        """
        key = CryptoService.generate_fernet_key()
        svc = CryptoService(fernet_key=key)
        plain = b"bytes-payload"
        ct = svc.encrypt(plain)
        assert svc.decrypt(ct) == plain.decode("utf-8")

    def test_safe_decrypt_invalid(self) -> None:
        """Execute test_safe_decrypt_invalid operation.

        Returns:
            The result of the operation.
        """
        svc = CryptoService(secret="another-stable-secret-for-tests")
        assert svc.safe_decrypt("not-valid-fernet-token!!!") is None

    def test_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Execute test_from_env operation.

        Args:
            monkeypatch: The monkeypatch parameter.

        Returns:
            The result of the operation.
        """
        monkeypatch.setenv("CRYPTO_SECRET_KEY", "env-derived-secret")
        svc = CryptoService.from_env()
        assert svc.decrypt(svc.encrypt("x")) == "x"

    def test_from_env_missing_raises(self) -> None:
        """Execute test_from_env_missing_raises operation.

        Returns:
            The result of the operation.
        """
        with pytest.raises(ServiceUnavailableError, match="NONEXISTENT_ENV_VAR_XYZ"):
            CryptoService.from_env("NONEXISTENT_ENV_VAR_XYZ")

    def test_constructor_validation(self) -> None:
        """Execute test_constructor_validation operation.

        Returns:
            The result of the operation.
        """
        with pytest.raises(CryptoConfigurationError, match="exactly one"):
            CryptoService()
        with pytest.raises(CryptoConfigurationError, match="exactly one"):
            CryptoService(secret="a", fernet_key=CryptoService.generate_fernet_key())


class TestHashingService(IServiceTests):
    """Represents the TestHashingService class."""

    def test_verify(self) -> None:
        """Execute test_verify operation.

        Returns:
            The result of the operation.
        """
        hs = HashingService(salt="testsalt")
        h = hs.hash("token")
        assert hs.verify("token", h)
        assert not hs.verify("other", h)


class TestKeyRotationService(IServiceTests):
    """Represents the TestKeyRotationService class."""

    def test_roundtrip(self) -> None:
        """Execute test_roundtrip operation.

        Returns:
            The result of the operation.
        """
        rot = KeyRotationService("password-for-field-encryption")
        ct = rot.encrypt("value")
        assert rot.decrypt(ct) == "value"


class TestAesGcmCryptoService(IServiceTests):
    """Represents the TestAesGcmCryptoService class."""

    def test_roundtrip(self) -> None:
        """Execute test_roundtrip operation.

        Returns:
            The result of the operation.
        """
        key = AesGcmCryptoService.generate_key(256)
        svc = AesGcmCryptoService(key)
        plain = b"binary-secret"
        ct = svc.encrypt(plain)
        assert svc.decrypt(ct) == plain

    def test_aad(self) -> None:
        """Execute test_aad operation.

        Returns:
            The result of the operation.
        """
        key = AesGcmCryptoService.generate_key(256)
        svc = AesGcmCryptoService(key)
        aad = b"ctx"
        ct = svc.encrypt(b"x", associated_data=aad)
        assert svc.decrypt(ct, associated_data=aad) == b"x"
