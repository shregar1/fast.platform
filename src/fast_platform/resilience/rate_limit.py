"""Rate limiting implementation."""

from typing import Optional, Callable, Any, Dict
from dataclasses import dataclass
from datetime import datetime, timedelta
from functools import wraps
import asyncio
import time


@dataclass
class RateLimitConfig:
    """Rate limit configuration."""

    requests_per_second: float = 10.0
    requests_per_minute: Optional[int] = None
    burst_size: int = 5

    # Key function for per-key rate limiting
    key_func: Optional[Callable] = None


class TokenBucket:
    """Token bucket rate limiter."""

    def __init__(self, rate: float, capacity: int):
        """Execute __init__ operation.

        Args:
            rate: The rate parameter.
            capacity: The capacity parameter.
        """
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last_update = time.time()
        self._lock = asyncio.Lock()

    async def acquire(self) -> bool:
        """Try to acquire a token."""
        async with self._lock:
            now = time.time()
            elapsed = now - self.last_update
            self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
            self.last_update = now

            if self.tokens >= 1:
                self.tokens -= 1
                return True
            return False

    async def wait_time(self) -> float:
        """Calculate wait time for next token."""
        async with self._lock:
            if self.tokens >= 1:
                return 0
            return (1 - self.tokens) / self.rate


class RateLimiter:
    """Rate limiter with token bucket algorithm."""

    def __init__(self, config: RateLimitConfig):
        """Execute __init__ operation.

        Args:
            config: The config parameter.
        """
        self.config = config
        self._buckets: Dict[str, TokenBucket] = {}
        self._default_bucket = TokenBucket(config.requests_per_second, config.burst_size)

    def _get_bucket(self, key: Optional[str] = None) -> TokenBucket:
        """Get or create token bucket."""
        if key is None:
            return self._default_bucket

        if key not in self._buckets:
            self._buckets[key] = TokenBucket(
                self.config.requests_per_second, self.config.burst_size
            )
        return self._buckets[key]

    async def limit(self, key: Optional[str] = None) -> bool:
        """Check if request is allowed.

        Returns True if allowed, False if rate limited
        """
        bucket = self._get_bucket(key)
        return await bucket.acquire()

    async def wait(self, key: Optional[str] = None) -> None:
        """Wait until request is allowed."""
        bucket = self._get_bucket(key)

        while not await bucket.acquire():
            wait_time = await bucket.wait_time()
            await asyncio.sleep(wait_time)


class RateLimitExceeded(Exception):
    """Raised when rate limit is exceeded."""

    pass


def rate_limit(
    requests_per_second: float = 10.0,
    burst_size: int = 5,
    key_func: Optional[Callable] = None,
    wait: bool = False,
):
    """Decorator to add rate limiting to a function.

    Args:
        requests_per_second: Rate limit
        burst_size: Burst capacity
        key_func: Function to extract key for per-key limiting
        wait: Whether to wait or raise exception

    """

    def decorator(func: Callable):
        """Execute decorator operation.

        Args:
            func: The func parameter.

        Returns:
            The result of the operation.
        """
        config = RateLimitConfig(
            requests_per_second=requests_per_second, burst_size=burst_size, key_func=key_func
        )
        limiter = RateLimiter(config)

        @wraps(func)
        async def wrapper(*args, **kwargs):
            """Execute wrapper operation.

            Returns:
                The result of the operation.
            """
            key = None
            if key_func:
                key = key_func(*args, **kwargs)

            if wait:
                await limiter.wait(key)
            else:
                if not await limiter.limit(key):
                    raise RateLimitExceeded(f"Rate limit exceeded: {requests_per_second}/s")

            return await func(*args, **kwargs)

        wrapper._rate_limiter = limiter
        return wrapper

    return decorator
