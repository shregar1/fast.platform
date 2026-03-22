"""Identity / OAuth providers configuration DTO."""

from __future__ import annotations

from .abstraction import IDTO

from pydantic import ConfigDict, Field

from .oauth_provider import OAuthProviderDTO


class IdentityProvidersConfigurationDTO(IDTO):
    model_config = ConfigDict(extra="ignore")
    google: OAuthProviderDTO = Field(default_factory=OAuthProviderDTO)
    github: OAuthProviderDTO = Field(default_factory=OAuthProviderDTO)
    microsoft: OAuthProviderDTO = Field(default_factory=OAuthProviderDTO)
