"""Signal handling for graceful shutdown."""

import signal
import asyncio
import logging
from typing import Optional, Callable

from .shutdown import ShutdownManager

logger = logging.getLogger(__name__)


class SignalHandler:
    """Handles OS signals for graceful shutdown."""

    def __init__(
        self,
        shutdown_callback: Optional[Callable] = None,
        signals: tuple = (signal.SIGTERM, signal.SIGINT),
    ):
        """Execute __init__ operation.

        Args:
            shutdown_callback: The shutdown_callback parameter.
            signals: The signals parameter.
        """
        self.shutdown_callback = shutdown_callback or ShutdownManager.shutdown
        self.signals = signals
        self._original_handlers: dict = {}

    def setup(self) -> None:
        """Setup signal handlers."""
        for sig in self.signals:
            try:
                self._original_handlers[sig] = signal.getsignal(sig)
                signal.signal(sig, self._handle_signal)
                logger.debug(f"Registered handler for {sig.name}")
            except ValueError:
                # Signal not supported on this platform
                pass

    def _handle_signal(self, sig, frame):
        """Handle received signal."""
        logger.info(f"Received signal {sig}")

        # Create task for async shutdown
        loop = asyncio.get_event_loop()
        loop.create_task(self._async_shutdown())

    async def _async_shutdown(self):
        """Async shutdown handler."""
        try:
            await self.shutdown_callback()
        except Exception as e:
            logger.exception(f"Error during shutdown: {e}")
        finally:
            # Exit the process
            import sys

            sys.exit(0)

    def restore(self) -> None:
        """Restore original signal handlers."""
        for sig, handler in self._original_handlers.items():
            signal.signal(sig, handler)
        self._original_handlers.clear()


def handle_signals(
    shutdown_callback: Optional[Callable] = None, setup: bool = True
) -> SignalHandler:
    """Setup signal handling for graceful shutdown.

    Args:
        shutdown_callback: Optional custom shutdown callback
        setup: Whether to setup handlers immediately

    Returns:
        SignalHandler instance

    """
    handler = SignalHandler(shutdown_callback)
    if setup:
        handler.setup()
    return handler
