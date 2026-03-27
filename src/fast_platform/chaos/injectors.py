"""Failure Injectors for Chaos Engineering."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import asyncio
import random
import time


class InjectionHandle:
    """Handle for an injected failure."""

    def __init__(self, injector: "FailureInjector", rollback_fn, cleanup_fn):
        """Execute __init__ operation.

        Args:
            injector: The injector parameter.
            rollback_fn: The rollback_fn parameter.
            cleanup_fn: The cleanup_fn parameter.
        """
        self.injector = injector
        self._rollback = rollback_fn
        self._cleanup = cleanup_fn

    async def rollback(self) -> None:
        """Execute rollback operation.

        Returns:
            The result of the operation.
        """
        await self._rollback()

    async def cleanup(self) -> None:
        """Execute cleanup operation.

        Returns:
            The result of the operation.
        """
        await self._cleanup()


class FailureInjector(ABC):
    """Base class for failure injectors."""

    @abstractmethod
    async def inject(
        self, target: str, probability: float, parameters: Dict[str, Any], blast_radius: float
    ) -> InjectionHandle:
        """Inject the failure."""
        pass


class LatencyInjector(FailureInjector):
    """Inject latency spikes."""

    _active_delays: Dict[str, bool] = {}

    async def inject(
        self, target: str, probability: float, parameters: Dict[str, Any], blast_radius: float
    ) -> InjectionHandle:
        """Execute inject operation.

        Args:
            target: The target parameter.
            probability: The probability parameter.
            parameters: The parameters parameter.
            blast_radius: The blast_radius parameter.

        Returns:
            The result of the operation.
        """
        min_latency = parameters.get("min_ms", 100)
        max_latency = parameters.get("max_ms", 5000)

        key = f"{target}_latency"
        self._active_delays[key] = True

        async def rollback():
            """Execute rollback operation.

            Returns:
                The result of the operation.
            """
            self._active_delays[key] = False

        async def cleanup():
            """Execute cleanup operation.

            Returns:
                The result of the operation.
            """
            self._active_delays.pop(key, None)

        return InjectionHandle(self, rollback, cleanup)

    @classmethod
    def should_delay(cls, target: str) -> tuple:
        """Check if request should be delayed."""
        key = f"{target}_latency"
        if cls._active_delays.get(key):
            return True, random.randint(100, 5000)
        return False, 0


class ExceptionInjector(FailureInjector):
    """Inject random exceptions."""

    _active_exceptions: Dict[str, bool] = {}

    async def inject(
        self, target: str, probability: float, parameters: Dict[str, Any], blast_radius: float
    ) -> InjectionHandle:
        """Execute inject operation.

        Args:
            target: The target parameter.
            probability: The probability parameter.
            parameters: The parameters parameter.
            blast_radius: The blast_radius parameter.

        Returns:
            The result of the operation.
        """
        exception_types = parameters.get(
            "exceptions", [ValueError, RuntimeError, ConnectionError, TimeoutError]
        )

        key = f"{target}_exception"
        self._active_exceptions[key] = True

        async def rollback():
            """Execute rollback operation.

            Returns:
                The result of the operation.
            """
            self._active_exceptions[key] = False

        async def cleanup():
            """Execute cleanup operation.

            Returns:
                The result of the operation.
            """
            self._active_exceptions.pop(key, None)

        return InjectionHandle(self, rollback, cleanup)

    @classmethod
    def should_raise(cls, target: str) -> bool:
        """Check if request should raise exception."""
        key = f"{target}_exception"
        return cls._active_exceptions.get(key, False)


class DatabaseFailureInjector(FailureInjector):
    """Inject database failures."""

    _active_failures: Dict[str, Dict[str, Any]] = {}

    async def inject(
        self, target: str, probability: float, parameters: Dict[str, Any], blast_radius: float
    ) -> InjectionHandle:
        """Execute inject operation.

        Args:
            target: The target parameter.
            probability: The probability parameter.
            parameters: The parameters parameter.
            blast_radius: The blast_radius parameter.

        Returns:
            The result of the operation.
        """
        failure_mode = parameters.get("mode", "random_disconnect")

        key = f"{target}_db"
        self._active_failures[key] = {
            "mode": failure_mode,
            "probability": probability * blast_radius,
        }

        async def rollback():
            """Execute rollback operation.

            Returns:
                The result of the operation.
            """
            self._active_failures.pop(key, None)

        async def cleanup():
            """Execute cleanup operation.

            Returns:
                The result of the operation.
            """
            pass

        return InjectionHandle(self, rollback, cleanup)

    @classmethod
    def get_failure(cls, target: str) -> Optional[Dict[str, Any]]:
        """Get active failure config for target."""
        key = f"{target}_db"
        return cls._active_failures.get(key)


class NetworkFailureInjector(FailureInjector):
    """Inject network failures."""

    _active_failures: Dict[str, Dict[str, Any]] = {}

    async def inject(
        self, target: str, probability: float, parameters: Dict[str, Any], blast_radius: float
    ) -> InjectionHandle:
        """Execute inject operation.

        Args:
            target: The target parameter.
            probability: The probability parameter.
            parameters: The parameters parameter.
            blast_radius: The blast_radius parameter.

        Returns:
            The result of the operation.
        """
        key = f"{target}_network"
        self._active_failures[key] = {
            "probability": probability * blast_radius,
            "mode": parameters.get("mode", "timeout"),
        }

        async def rollback():
            """Execute rollback operation.

            Returns:
                The result of the operation.
            """
            self._active_failures.pop(key, None)

        async def cleanup():
            """Execute cleanup operation.

            Returns:
                The result of the operation.
            """
            pass

        return InjectionHandle(self, rollback, cleanup)


class FailureInjectorFactory:
    """Factory for creating failure injectors."""

    from .core import FailureType

    _injectors: Dict[FailureType, type] = {}

    @classmethod
    def register(cls, failure_type: FailureType, injector_class: type) -> None:
        """Execute register operation.

        Args:
            failure_type: The failure_type parameter.
            injector_class: The injector_class parameter.

        Returns:
            The result of the operation.
        """
        cls._injectors[failure_type] = injector_class

    @classmethod
    def create(cls, failure_type: FailureType) -> FailureInjector:
        """Execute create operation.

        Args:
            failure_type: The failure_type parameter.

        Returns:
            The result of the operation.
        """
        injector_class = cls._injectors.get(failure_type)
        if not injector_class:
            raise ValueError(f"Unknown failure type: {failure_type}")
        return injector_class()


# Register default injectors
default_injectors = [
    ("LATENCY_SPIKE", LatencyInjector),
    ("LATENCY_DEGRADATION", LatencyInjector),
    ("EXCEPTION_INJECTION", ExceptionInjector),
    ("DB_CONNECTION_DROP", DatabaseFailureInjector),
]

# Import FailureType here to avoid circular imports
from .core import FailureType

for name, injector_class in default_injectors:
    FailureInjectorFactory.register(FailureType[name], injector_class)
