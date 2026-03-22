"""
fast_identity – Identity provider abstractions and builders for FastMVC.
"""

from fast_core import IdentityProvidersConfiguration, IdentityProvidersConfigurationDTO

from .api_key import (
    InMemoryHashedApiKeyStore,
    hash_api_key_sha256_hex,
    verify_api_key_sha256_hex,
)
from .claims_normalize import (
    NormalizedClaims,
    normalize_roles,
    normalize_scopes,
    normalize_token_claims,
    parse_acr_claim,
    parse_amr_claim,
)
from .jwks_cache import JWKSCache
from .multi_issuer_jwks import MultiIssuerJWKSCache
from .providers import (
    IdentityUserProfile,
    IIdentityProvider,
    build_identity_providers,
)

__version__ = "0.3.0"

__all__ = [
    "IdentityUserProfile",
    "IIdentityProvider",
    "IdentityProvidersConfiguration",
    "IdentityProvidersConfigurationDTO",
    "InMemoryHashedApiKeyStore",
    "JWKSCache",
    "MultiIssuerJWKSCache",
    "NormalizedClaims",
    "build_identity_providers",
    "hash_api_key_sha256_hex",
    "normalize_roles",
    "normalize_scopes",
    "normalize_token_claims",
    "parse_acr_claim",
    "parse_amr_claim",
    "verify_api_key_sha256_hex",
]
