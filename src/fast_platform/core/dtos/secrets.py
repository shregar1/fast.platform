"""Secrets backends configuration DTO."""

from __future__ import annotations

from pydantic import ConfigDict, Field

from .abstraction import IDTO
from .aws_secrets import AwsSecretsDTO
from .gcp_secrets import GcpSecretsDTO
from .vault_secrets import VaultSecretsDTO


class SecretsConfigurationDTO(IDTO):
    """Represents the SecretsConfigurationDTO class."""

    model_config = ConfigDict(extra="ignore")
    vault: VaultSecretsDTO = Field(default_factory=VaultSecretsDTO)
    aws: AwsSecretsDTO = Field(default_factory=AwsSecretsDTO)
    gcp: GcpSecretsDTO = Field(default_factory=GcpSecretsDTO)
