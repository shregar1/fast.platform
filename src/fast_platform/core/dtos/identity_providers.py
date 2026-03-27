"""Identity / OAuth providers configuration DTO."""

from __future__ import annotations

from pydantic import ConfigDict, Field

from .abstraction import IDTO
from .oauth_provider import OAuthProviderDTO


class IdentityProvidersConfigurationDTO(IDTO):
    """Represents the IdentityProvidersConfigurationDTO class."""

    model_config = ConfigDict(extra="ignore")
    google: OAuthProviderDTO = Field(default_factory=OAuthProviderDTO)
    github: OAuthProviderDTO = Field(default_factory=OAuthProviderDTO)
    microsoft: OAuthProviderDTO = Field(default_factory=OAuthProviderDTO)
