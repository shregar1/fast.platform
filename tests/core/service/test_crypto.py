"""Tests for :mod:`service.crypto`."""

from __future__ import annotations

import pytest

from core.errors import CryptoConfigurationError, ServiceUnavailableError
from core.service.crypto import (
    AesGcmCryptoService,
    CryptoService,
    HashingService,
    KeyRotationService,
)
from tests.core.service.abstraction import IServiceTests


class TestCryptoService(IServiceTests):
    def test_secret_roundtrip(self) -> None:
        svc = CryptoService(secret="unit-test-secret-32chars-min")
        plain = "sensitive-payload"
        ct = svc.encrypt(plain)
        assert ct != plain
        assert svc.decrypt(ct) == plain

    def test_fernet_key_roundtrip(self) -> None:
        key = CryptoService.generate_fernet_key()
        svc = CryptoService(fernet_key=key)
        plain = b"bytes-payload"
        ct = svc.encrypt(plain)
        assert svc.decrypt(ct) == plain.decode("utf-8")

    def test_safe_decrypt_invalid(self) -> None:
        svc = CryptoService(secret="another-stable-secret-for-tests")
        assert svc.safe_decrypt("not-valid-fernet-token!!!") is None

    def test_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("CRYPTO_SECRET_KEY", "env-derived-secret")
        svc = CryptoService.from_env()
        assert svc.decrypt(svc.encrypt("x")) == "x"

    def test_from_env_missing_raises(self) -> None:
        with pytest.raises(ServiceUnavailableError, match="NONEXISTENT_ENV_VAR_XYZ"):
            CryptoService.from_env("NONEXISTENT_ENV_VAR_XYZ")

    def test_constructor_validation(self) -> None:
        with pytest.raises(CryptoConfigurationError, match="exactly one"):
            CryptoService()
        with pytest.raises(CryptoConfigurationError, match="exactly one"):
            CryptoService(secret="a", fernet_key=CryptoService.generate_fernet_key())


class TestHashingService(IServiceTests):
    def test_verify(self) -> None:
        hs = HashingService(salt="testsalt")
        h = hs.hash("token")
        assert hs.verify("token", h)
        assert not hs.verify("other", h)


class TestKeyRotationService(IServiceTests):
    def test_roundtrip(self) -> None:
        rot = KeyRotationService("password-for-field-encryption")
        ct = rot.encrypt("value")
        assert rot.decrypt(ct) == "value"


class TestAesGcmCryptoService(IServiceTests):
    def test_roundtrip(self) -> None:
        key = AesGcmCryptoService.generate_key(256)
        svc = AesGcmCryptoService(key)
        plain = b"binary-secret"
        ct = svc.encrypt(plain)
        assert svc.decrypt(ct) == plain

    def test_aad(self) -> None:
        key = AesGcmCryptoService.generate_key(256)
        svc = AesGcmCryptoService(key)
        aad = b"ctx"
        ct = svc.encrypt(b"x", associated_data=aad)
        assert svc.decrypt(ct, associated_data=aad) == b"x"
