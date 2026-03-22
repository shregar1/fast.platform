"""S3-compatible storage subsection."""

from __future__ import annotations

from .abstraction import IDTO

from pydantic import ConfigDict


class S3StorageDTO(IDTO):
    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    bucket: str = ""
    region: str = ""
    access_key_id: str = ""
    secret_access_key: str = ""
