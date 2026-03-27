"""Tests for claim normalization."""

from fast_platform.sec.identity.claims_normalize import (
    NormalizedClaims,
    normalize_roles,
    normalize_scopes,
    normalize_token_claims,
    parse_acr_claim,
    parse_amr_claim,
)
from tests.sec.identity.abstraction import IIdentityTests


class TestClaimsNormalize(IIdentityTests):
    """Represents the TestClaimsNormalize class."""

    def test_normalize_roles_keycloak_style(self):
        """Execute test_normalize_roles_keycloak_style operation.

        Returns:
            The result of the operation.
        """
        claims = {
            "realm_access": {"roles": ["admin", "user"]},
            "resource_access": {"client": {"roles": ["api"]}},
            "roles": ["direct"],
        }
        r = normalize_roles(claims)
        assert r == frozenset({"admin", "user", "api", "direct"})

    def test_normalize_scopes(self):
        """Execute test_normalize_scopes operation.

        Returns:
            The result of the operation.
        """
        assert normalize_scopes({"scope": "a b c"}) == frozenset({"a", "b", "c"})
        assert normalize_scopes({"scp": ["x", "y"]}) == frozenset({"x", "y"})

    def test_parse_amr_acr(self):
        """Execute test_parse_amr_acr operation.

        Returns:
            The result of the operation.
        """
        assert parse_amr_claim(None) == frozenset()
        assert parse_amr_claim(["pwd", "otp"]) == frozenset({"pwd", "otp"})
        assert parse_amr_claim("pwd mfa") == frozenset({"pwd", "mfa"})
        assert parse_acr_claim(None) is None
        assert parse_acr_claim("urn:mace:incommon:iap:silver") == "urn:mace:incommon:iap:silver"

    def test_normalize_token_claims_mfa(self):
        """Execute test_normalize_token_claims_mfa operation.

        Returns:
            The result of the operation.
        """
        claims = {
            "sub": "user-1",
            "iss": "https://idp/",
            "aud": "my-api",
            "realm_access": {"roles": ["r1"]},
            "scope": "api.read",
            "amr": ["pwd", "otp"],
            "acr": "silver",
        }
        n = normalize_token_claims(claims)
        assert isinstance(n, NormalizedClaims)
        assert n.subject == "user-1"
        assert n.issuer == "https://idp/"
        assert n.audience == "my-api"
        assert "r1" in n.roles
        assert "api.read" in n.scopes
        assert n.amr == frozenset({"pwd", "otp"})
        assert n.acr == "silver"

    def test_aud_list_tuple(self):
        """Execute test_aud_list_tuple operation.

        Returns:
            The result of the operation.
        """
        n = normalize_token_claims({"sub": "x", "aud": ["a", "b"]})
        assert n.audience == ("a", "b")

    def test_aud_single_element_list(self):
        """Execute test_aud_single_element_list operation.

        Returns:
            The result of the operation.
        """
        n = normalize_token_claims({"sub": "x", "aud": ["only"]})
        assert n.audience == "only"

    def test_parse_amr_non_sequence(self):
        """Execute test_parse_amr_non_sequence operation.

        Returns:
            The result of the operation.
        """
        assert parse_amr_claim(42) == frozenset({"42"})
