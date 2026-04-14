from typing import Final

POSTGRESQL_DRIVER: Final[str] = "postgresql"
DEFAULT_SQLITE_URL_PREFIX: Final[str] = "sqlite:///"
INCOMPLETE_DB_CONFIG_ERROR: Final[str] = (
    "Database configuration is incomplete. Set user_name, password, host, port, database, and connection_string."
)
