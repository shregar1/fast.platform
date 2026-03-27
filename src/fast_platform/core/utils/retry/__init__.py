"""Async retry/backoff utilities."""

from __future__ import annotations

import asyncio
import random
from typing import Awaitable, Callable, Tuple, TypeVar

from .abstraction import IAsyncRetryUtility

T = TypeVar("T")

__all__ = ["AsyncRetry", "IAsyncRetryUtility"]


class AsyncRetry(IAsyncRetryUtility):
    """Retry async callables with exponential backoff + jitter."""

    @staticmethod
    async def retry_async(
        fn: Callable[[], Awaitable[T]],
        *,
        retries: int = 3,
        base_delay: float = 0.5,
        max_delay: float = 10.0,
        jitter: float = 0.2,
        exceptions: Tuple[type[BaseException], ...] = (Exception,),
    ) -> T:
        """Retry an async function with exponential backoff + jitter."""
        if retries < 0:
            raise ValueError("retries must be >= 0")
        if base_delay < 0:
            raise ValueError("base_delay must be >= 0")
        if max_delay < base_delay:
            raise ValueError("max_delay must be >= base_delay")
        if jitter < 0:
            raise ValueError("jitter must be >= 0")

        attempt = 0
        while True:
            try:
                return await fn()
            except exceptions:
                if attempt >= retries:
                    raise

                delay = min(max_delay, base_delay * (2**attempt))

                if jitter > 0 and delay > 0:
                    delta = delay * jitter
                    delay = delay + random.uniform(-delta, delta)
                    delay = max(0.0, delay)

                await asyncio.sleep(delay)
                attempt += 1
