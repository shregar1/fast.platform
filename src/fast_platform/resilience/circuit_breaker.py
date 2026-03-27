"""Circuit breaker pattern implementation."""

from typing import Optional, Callable, Any, Type, List
from dataclasses import dataclass
from enum import Enum, auto
from functools import wraps
import time
import asyncio
import logging

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states."""

    CLOSED = auto()  # Normal operation
    OPEN = auto()  # Failing, reject calls
    HALF_OPEN = auto()  # Testing if service recovered


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration."""

    failure_threshold: int = 5
    recovery_timeout: float = 30.0
    half_open_max_calls: int = 3
    success_threshold: int = 2

    # Exceptions that should count as failures
    expected_exceptions: tuple = (Exception,)

    # Exceptions that should be ignored
    ignored_exceptions: tuple = ()


class CircuitBreaker:
    """Circuit breaker implementation.

    Prevents cascading failures by stopping calls to failing services.
    """

    def __init__(self, name: str, config: Optional[CircuitBreakerConfig] = None):
        """Execute __init__ operation.

        Args:
            name: The name parameter.
            config: The config parameter.
        """
        self.name = name
        self.config = config or CircuitBreakerConfig()

        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: Optional[float] = None
        self._half_open_calls = 0
        self._lock = asyncio.Lock()

    @property
    def state(self) -> CircuitState:
        """Execute state operation.

        Returns:
            The result of the operation.
        """
        return self._state

    @property
    def is_open(self) -> bool:
        """Execute is_open operation.

        Returns:
            The result of the operation.
        """
        return self._state == CircuitState.OPEN

    @property
    def is_closed(self) -> bool:
        """Execute is_closed operation.

        Returns:
            The result of the operation.
        """
        return self._state == CircuitState.CLOSED

    @property
    def is_half_open(self) -> bool:
        """Execute is_half_open operation.

        Returns:
            The result of the operation.
        """
        return self._state == CircuitState.HALF_OPEN

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Call a function through the circuit breaker."""
        async with self._lock:
            await self._update_state()

            if self._state == CircuitState.OPEN:
                raise CircuitBreakerOpen(f"Circuit {self.name} is OPEN")

            if self._state == CircuitState.HALF_OPEN:
                if self._half_open_calls >= self.config.half_open_max_calls:
                    raise CircuitBreakerOpen(f"Circuit {self.name} HALF_OPEN limit reached")
                self._half_open_calls += 1

        # Execute the call
        try:
            result = await func(*args, **kwargs)
            await self._on_success()
            return result
        except Exception as e:
            if self._should_count_as_failure(e):
                await self._on_failure()
            raise

    async def _update_state(self) -> None:
        """Update circuit state based on time."""
        if self._state == CircuitState.OPEN:
            if self._last_failure_time:
                elapsed = time.time() - self._last_failure_time
                if elapsed >= self.config.recovery_timeout:
                    logger.info(f"Circuit {self.name} moving to HALF_OPEN")
                    self._state = CircuitState.HALF_OPEN
                    self._half_open_calls = 0
                    self._success_count = 0

    async def _on_success(self) -> None:
        """Handle successful call."""
        async with self._lock:
            if self._state == CircuitState.HALF_OPEN:
                self._success_count += 1
                if self._success_count >= self.config.success_threshold:
                    logger.info(f"Circuit {self.name} closing")
                    self._state = CircuitState.CLOSED
                    self._failure_count = 0
                    self._half_open_calls = 0
            elif self._state == CircuitState.CLOSED:
                self._failure_count = 0

    async def _on_failure(self) -> None:
        """Handle failed call."""
        async with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.time()

            if self._state == CircuitState.HALF_OPEN:
                logger.warning(f"Circuit {self.name} opening (half-open failure)")
                self._state = CircuitState.OPEN
            elif self._state == CircuitState.CLOSED:
                if self._failure_count >= self.config.failure_threshold:
                    logger.warning(f"Circuit {self.name} opening")
                    self._state = CircuitState.OPEN

    def _should_count_as_failure(self, exception: Exception) -> bool:
        """Check if exception should count as failure."""
        if isinstance(exception, self.config.ignored_exceptions):
            return False
        return isinstance(exception, self.config.expected_exceptions)

    def get_metrics(self) -> dict:
        """Get circuit breaker metrics."""
        return {
            "name": self.name,
            "state": self._state.name,
            "failure_count": self._failure_count,
            "success_count": self._success_count,
            "last_failure_time": self._last_failure_time,
        }


class CircuitBreakerOpen(Exception):
    """Raised when circuit breaker is open."""

    pass


# Global registry of circuit breakers
_circuit_breakers: dict = {}


def get_circuit_breaker(name: str) -> Optional[CircuitBreaker]:
    """Get a circuit breaker by name."""
    return _circuit_breakers.get(name)


def circuit_breaker(
    name: Optional[str] = None,
    failure_threshold: int = 5,
    recovery_timeout: float = 30.0,
    expected_exceptions: tuple = (Exception,),
    fallback: Optional[Callable] = None,
):
    """Decorator to add circuit breaker to a function.

    Args:
        name: Circuit breaker name
        failure_threshold: Failures before opening
        recovery_timeout: Seconds before trying again
        expected_exceptions: Exceptions that count as failures
        fallback: Optional fallback function

    """

    def decorator(func: Callable):
        """Execute decorator operation.

        Args:
            func: The func parameter.

        Returns:
            The result of the operation.
        """
        cb_name = name or func.__name__

        config = CircuitBreakerConfig(
            failure_threshold=failure_threshold,
            recovery_timeout=recovery_timeout,
            expected_exceptions=expected_exceptions,
        )

        cb = CircuitBreaker(cb_name, config)
        _circuit_breakers[cb_name] = cb

        @wraps(func)
        async def wrapper(*args, **kwargs):
            """Execute wrapper operation.

            Returns:
                The result of the operation.
            """
            try:
                return await cb.call(func, *args, **kwargs)
            except CircuitBreakerOpen:
                if fallback:
                    return await fallback(*args, **kwargs)
                raise

        wrapper._circuit_breaker = cb
        return wrapper

    return decorator
