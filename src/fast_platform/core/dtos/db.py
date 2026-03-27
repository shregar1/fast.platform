"""Database connection / pool configuration DTO."""

from __future__ import annotations

from typing import Optional

from .abstraction import IDTO


class DBConfigurationDTO(IDTO):
    """Represents the DBConfigurationDTO class."""

    user_name: str = ""
    password: str = ""
    host: str = ""
    port: int = 5432
    database: str = ""
    connection_string: str = ""
    async_connection_string: str = ""
    pool_size: int = 5
    max_overflow: int = 10
    pool_timeout: float = 30.0
    pool_recycle: Optional[int] = None
    pool_pre_ping: bool = True
    connection_name: str = ""
    statement_timeout_seconds: Optional[float] = None
    read_replica_connection_string: str = ""
    read_replica_host: str = ""
    read_replica_port: Optional[int] = None
