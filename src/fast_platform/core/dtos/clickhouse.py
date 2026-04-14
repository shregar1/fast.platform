"""ClickHouse configuration DTO."""

from __future__ import annotations

from ..constants import DEFAULT_HOST
from typing import Optional

from .abstraction import IDTO


class ClickHouseConfigurationDTO(IDTO):
    """Represents the ClickHouseConfigurationDTO class."""

    host: str = DEFAULT_HOST
    port: int = 8123
    user_name: str = "default"
    password: str = ""
    database: str = "default"
    secure: bool = False
    verify: bool = True
    connect_timeout_seconds: float = 10.0
    send_receive_timeout_seconds: float = 300.0
    use_http: bool = True
    compression: Optional[str] = None
