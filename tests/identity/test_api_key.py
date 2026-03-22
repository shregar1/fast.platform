"""Tests for API key hashing and store."""

from fast_identity.api_key import (
    InMemoryHashedApiKeyStore,
    hash_api_key_sha256_hex,
    verify_api_key_sha256_hex,
)


def test_hash_and_verify_round_trip():
    secret = "my-service-secret"
    hx = hash_api_key_sha256_hex(secret)
    assert len(hx) == 64
    assert verify_api_key_sha256_hex(secret, hx)
    assert verify_api_key_sha256_hex(secret, hx.upper())
    assert not verify_api_key_sha256_hex("wrong", hx)


def test_verify_length_mismatch():
    assert not verify_api_key_sha256_hex("x", "abc")


def test_in_memory_store():
    store = InMemoryHashedApiKeyStore()
    k = "key-one"
    h = hash_api_key_sha256_hex("secret-one")
    store.register(k, h)
    assert store.verify("secret-one") == k
    assert store.verify("nope") is None
    store.remove(k)
    assert store.verify("secret-one") is None


def test_in_memory_store_wrong_hash_length_skipped():
    store = InMemoryHashedApiKeyStore()
    store.register("k", "tooshort")
    assert store.verify("secret-one") is None
