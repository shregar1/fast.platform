"""Single OAuth2 identity provider subsection."""

from __future__ import annotations

from .abstraction import IDTO

from typing import List

from pydantic import ConfigDict, Field


class OAuthProviderDTO(IDTO):
    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    client_id: str = ""
    client_secret: str = ""
    auth_url: str = ""
    token_url: str = ""
    userinfo_url: str = ""
    redirect_uri: str = ""
    scopes: List[str] = Field(default_factory=list)
