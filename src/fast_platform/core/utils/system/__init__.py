from __future__ import annotations
"""System environment, platform, and resource utilities."""

from ...constants import BYTES_PER_KB

import os
import platform
import sys
from typing import Optional, Any

from .abstraction import ISystemUtility


class SystemUtility(ISystemUtility):
    """Stateless helpers for OS-level and environment queries."""

    @staticmethod
    def get_env_bool(name: str, default: bool = False) -> bool:
        """True if the environment variable *name* is "true", "1", "yes", or "on" (case-insensitive)."""
        val = os.getenv(name)
        if val is None:
            return default
        return val.lower() in ("true", "1", "yes", "on")

    @staticmethod
    def get_env_int(name: str, default: Optional[int] = None) -> Optional[int]:
        """Return environment variable *name* cast as int, else *default*."""
        val = os.getenv(name)
        if val is None:
            return default
        try:
            return int(val)
        except ValueError:
            return default

    @staticmethod
    def is_linux() -> bool:
        """True if current OS is Linux."""
        return sys.platform.startswith("linux")

    @staticmethod
    def is_windows() -> bool:
        """True if current OS is Windows."""
        return sys.platform.startswith("win") or sys.platform == "cygwin"

    @staticmethod
    def is_macos() -> bool:
        """True if current OS is macOS."""
        return sys.platform == "darwin"

    @staticmethod
    def get_python_version() -> str:
        """Return the running Python version as a string (major.minor.patch)."""
        return platform.python_version()

    @staticmethod
    def get_memory_usage_mb() -> float:
        """Return process resident memory in MB (approximate).

        **Note:** Requires Linux/macOS. Returns 0.0 on Windows unless psutil is added.
        """
        try:
            import resource

            res = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            if SystemUtility.is_macos():
                return float(res) / (BYTES_PER_KB * BYTES_PER_KB)  # macOS is bytes
            return float(res) / BYTES_PER_KB  # Linux is kb
        except (ImportError, AttributeError):
            return 0.0


__all__ = ["SystemUtility", "ISystemUtility"]
