"""Tests for :class:`sec.identity.api_key.ApiKeyHashes`."""

from sec.identity.api_key import ApiKeyHashes
from tests.sec.identity.abstraction import IIdentityTests


class TestApiKeyHashes(IIdentityTests):
    def test_hash_and_verify_round_trip(self) -> None:
        secret = "my-service-secret"
        hx = ApiKeyHashes.hash_api_key_sha256_hex(secret)
        assert len(hx) == 64
        assert ApiKeyHashes.verify_api_key_sha256_hex(secret, hx)
        assert ApiKeyHashes.verify_api_key_sha256_hex(secret, hx.upper())
        assert not ApiKeyHashes.verify_api_key_sha256_hex("wrong", hx)

    def test_verify_length_mismatch(self) -> None:
        assert not ApiKeyHashes.verify_api_key_sha256_hex("x", "abc")
