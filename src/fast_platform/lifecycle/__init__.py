"""
FastMVC Lifecycle Module

Graceful shutdown, startup hooks, and lifecycle management.
"""

from .shutdown import (
    on_shutdown,
    on_startup,
    ShutdownManager,
    StartupManager,
)
from .signals import (
    handle_signals,
    SignalHandler,
)

__all__ = [
    "on_shutdown",
    "on_startup",
    "ShutdownManager",
    "StartupManager",
    "handle_signals",
    "SignalHandler",
]
