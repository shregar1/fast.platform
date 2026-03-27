"""Tests for :class:`sec.identity.api_key.ApiKeyHashes`."""

from sec.identity.api_key import ApiKeyHashes
from tests.sec.identity.abstraction import IIdentityTests


class TestApiKeyHashes(IIdentityTests):
    """Represents the TestApiKeyHashes class."""

    def test_hash_and_verify_round_trip(self) -> None:
        """Execute test_hash_and_verify_round_trip operation.

        Returns:
            The result of the operation.
        """
        secret = "my-service-secret"
        hx = ApiKeyHashes.hash_api_key_sha256_hex(secret)
        assert len(hx) == 64
        assert ApiKeyHashes.verify_api_key_sha256_hex(secret, hx)
        assert ApiKeyHashes.verify_api_key_sha256_hex(secret, hx.upper())
        assert not ApiKeyHashes.verify_api_key_sha256_hex("wrong", hx)

    def test_verify_length_mismatch(self) -> None:
        """Execute test_verify_length_mismatch operation.

        Returns:
            The result of the operation.
        """
        assert not ApiKeyHashes.verify_api_key_sha256_hex("x", "abc")
