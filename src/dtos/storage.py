"""Object / blob storage configuration DTO."""

from __future__ import annotations

from .abstraction import IDTO

from pydantic import ConfigDict, Field

from .s3_storage import S3StorageDTO


class StorageConfigurationDTO(IDTO):
    model_config = ConfigDict(extra="ignore")
    default_backend: str = "local"
    s3: S3StorageDTO = Field(default_factory=S3StorageDTO)
