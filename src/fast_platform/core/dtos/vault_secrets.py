"""Vault secrets subsection."""

from __future__ import annotations

from ..constants import DEFAULT_HOST
from pydantic import ConfigDict

from .abstraction import IDTO


class VaultSecretsDTO(IDTO):
    """Represents the VaultSecretsDTO class."""

    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    url: str = ""
    token: str = ""
    mount_point: str = "secret"
