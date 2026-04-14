from typing import Final

POSTGRESQL_DRIVER: Final[str] = "postgresql"
POSTGRESQL_ASYNCPG_DRIVER: Final[str] = "postgresql+asyncpg"
DEFAULT_SQLITE_URL_PREFIX: Final[str] = "sqlite:///"
DEFAULT_SQLITE_AIOSQLITE_PREFIX: Final[str] = "sqlite+aiosqlite:///"
DEFAULT_SQLITE_AIOSQLITE_SCHEME: Final[str] = "sqlite+aiosqlite://"
INCOMPLETE_DB_CONFIG_ERROR: Final[str] = (
    "Database configuration is incomplete. Set user_name, password, host, port, database, and connection_string."
)
