"""Tests for :class:`identity.api_key.InMemoryHashedApiKeyStore`."""
from tests.sec.identity.abstraction import IIdentityTests


from identity.api_key import ApiKeyHashes, InMemoryHashedApiKeyStore


class TestInMemoryHashedApiKeyStore(IIdentityTests):
    def test_in_memory_store(self) -> None:
        store = InMemoryHashedApiKeyStore()
        k = "key-one"
        h = ApiKeyHashes.hash_api_key_sha256_hex("secret-one")
        store.register(k, h)
        assert store.verify("secret-one") == k
        assert store.verify("nope") is None
        store.remove(k)
        assert store.verify("secret-one") is None

    def test_in_memory_store_wrong_hash_length_skipped(self) -> None:
        store = InMemoryHashedApiKeyStore()
        store.register("k", "tooshort")
        assert store.verify("secret-one") is None
