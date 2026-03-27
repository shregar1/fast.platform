"""fast_db – DB extension for FastMVC.

Provides SQLAlchemy engine/session from fast_platform DB config,
FastAPI DBDependency, table name constants, and get_database_url for Alembic.
"""

from .async_dependency import AsyncDBDependency
from .async_engine import (
    async_connect_args_for_url,
    async_database_url_from_config,
    async_read_replica_url_from_config,
    check_database_async,
    create_and_set_async_session_factory,
    create_async_session_factory,
    get_async_engine,
    get_async_engine_instance,
    get_async_read_engine,
    get_async_read_engine_instance,
    get_async_session_factory,
    set_global_async_engine,
    set_global_async_read_engine,
    set_global_async_session_factory,
    sync_url_to_async_url,
)
from .dependency import DBDependency
from .engine import (
    check_database,
    create_and_set_session,
    create_session_factory,
    get_db_session,
    get_engine,
    set_global_engine,
    set_global_session,
    sync_connect_args_for_url,
)
from .migration_lock import (
    DEFAULT_MIGRATION_LOCK_KEY1,
    DEFAULT_MIGRATION_LOCK_KEY2,
    advisory_migration_lock,
    try_advisory_migration_lock,
)
from .replica import (
    ReadDBDependency,
    create_and_set_read_session,
    create_read_session_factory,
    get_read_db_session,
    get_read_engine,
    get_read_engine_instance,
    read_replica_url_from_config,
    set_global_read_engine,
    set_global_read_session,
)
from .table import Table
from .url import get_database_url

__version__ = "0.1.0"

__all__ = [
    "__version__",
    "DEFAULT_MIGRATION_LOCK_KEY1",
    "DEFAULT_MIGRATION_LOCK_KEY2",
    "AsyncDBDependency",
    "DBDependency",
    "ReadDBDependency",
    "Table",
    "advisory_migration_lock",
    "async_connect_args_for_url",
    "async_database_url_from_config",
    "async_read_replica_url_from_config",
    "check_database",
    "check_database_async",
    "create_and_set_async_session_factory",
    "create_and_set_read_session",
    "create_and_set_session",
    "create_async_session_factory",
    "create_read_session_factory",
    "create_session_factory",
    "get_database_url",
    "get_db_session",
    "get_async_engine",
    "get_async_engine_instance",
    "get_async_read_engine",
    "get_async_read_engine_instance",
    "get_async_session_factory",
    "get_engine",
    "get_read_db_session",
    "get_read_engine",
    "get_read_engine_instance",
    "read_replica_url_from_config",
    "set_global_async_engine",
    "set_global_async_read_engine",
    "set_global_async_session_factory",
    "set_global_engine",
    "set_global_read_engine",
    "set_global_read_session",
    "set_global_session",
    "sync_connect_args_for_url",
    "sync_url_to_async_url",
    "try_advisory_migration_lock",
]
