"""Smoke test package import."""

import sec.identity as i

from tests.sec.identity.abstraction import IIdentityTests


class TestIdentityPackageImports(IIdentityTests):
    def test_import(self) -> None:
        assert i.build_identity_providers is not None
        assert i.IIdentityProvider is not None
        assert i.IdentityUserProfile is not None
        assert i.IdentityProvidersConfiguration is not None
        assert i.JWKSCache is not None
        assert i.MultiIssuerJWKSCache is not None
        assert i.NormalizedClaims is not None
        assert i.normalize_token_claims is not None
        assert i.ApiKeyHashes is not None
        assert i.__version__ == "0.3.0"
