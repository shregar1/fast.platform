"""MongoDB connection configuration DTO."""

from __future__ import annotations

from typing import Optional

from .abstraction import IDTO


class MongoDBConfigurationDTO(IDTO):
    """Represents the MongoDBConfigurationDTO class."""

    host: str = "localhost"
    port: int = 27017
    user_name: str = ""
    password: str = ""
    database: str = ""
    connection_string: str = ""
    max_pool_size: int = 100
    min_pool_size: int = 0
    max_idle_time_seconds: Optional[float] = None
    connect_timeout_seconds: float = 20.0
    socket_timeout_seconds: Optional[float] = None
    server_selection_timeout_seconds: float = 30.0
    replica_set: str = ""
    tls: bool = False
    tls_allow_invalid_certificates: bool = False
    retry_writes: bool = True
    retry_reads: bool = True
    app_name: str = "FastMVC"
