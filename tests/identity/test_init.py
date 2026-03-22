"""Smoke test package import."""

import identity as i


def test_import():
    assert i.build_identity_providers is not None
    assert i.IIdentityProvider is not None
    assert i.IdentityUserProfile is not None
    assert i.IdentityProvidersConfiguration is not None
    assert i.JWKSCache is not None
    assert i.MultiIssuerJWKSCache is not None
    assert i.NormalizedClaims is not None
    assert i.normalize_token_claims is not None
    assert i.hash_api_key_sha256_hex is not None
    assert i.__version__ == "0.3.0"
