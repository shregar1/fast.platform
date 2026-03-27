"""S3-compatible storage subsection."""

from __future__ import annotations

from pydantic import ConfigDict

from .abstraction import IDTO


class S3StorageDTO(IDTO):
    """Represents the S3StorageDTO class."""

    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    bucket: str = ""
    region: str = ""
    access_key_id: str = ""
    secret_access_key: str = ""
