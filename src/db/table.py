"""
Database table name constants.

Use these instead of string literals for __tablename__ to avoid typos and
centralize renames.
"""

from typing import Final


class Table:
    """Database table name constants."""

    USER: Final[str] = "user"
    """Table name for user accounts and authentication data."""
