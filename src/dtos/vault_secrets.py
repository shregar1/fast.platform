"""Vault secrets subsection."""

from __future__ import annotations

from .abstraction import IDTO

from pydantic import ConfigDict


class VaultSecretsDTO(IDTO):
    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    url: str = ""
    token: str = ""
    mount_point: str = "secret"
