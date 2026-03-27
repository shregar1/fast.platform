"""Health check implementations."""

from typing import Dict, Any, List, Optional, Callable, Awaitable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import asyncio
import time


class HealthStatus(Enum):
    """Health status levels."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthResult:
    """Result of a health check."""

    name: str
    status: HealthStatus
    response_time_ms: float
    message: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Execute to_dict operation.

        Returns:
            The result of the operation.
        """
        return {
            "name": self.name,
            "status": self.status.value,
            "response_time_ms": self.response_time_ms,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
        }


class HealthCheck:
    """Health check registry and runner."""

    _checks: Dict[str, List[Callable]] = {"health": [], "ready": [], "live": [], "startup": []}

    @classmethod
    def register(cls, check_type: str, func: Callable[[], Awaitable[Dict[str, Any]]]) -> None:
        """Register a health check."""
        if check_type not in cls._checks:
            cls._checks[check_type] = []
        cls._checks[check_type].append(func)

    @classmethod
    async def run_checks(cls, check_type: str, timeout: float = 5.0) -> List[HealthResult]:
        """Run all checks of a type."""
        checks = cls._checks.get(check_type, [])
        results = []

        for check in checks:
            start = time.time()
            try:
                result = await asyncio.wait_for(check(), timeout=timeout)
                response_time = (time.time() - start) * 1000

                status = HealthStatus.HEALTHY
                if result.get("status") == "unhealthy":
                    status = HealthStatus.UNHEALTHY
                elif result.get("status") == "degraded":
                    status = HealthStatus.DEGRADED

                results.append(
                    HealthResult(
                        name=check.__name__,
                        status=status,
                        response_time_ms=response_time,
                        message=result.get("message"),
                        details=result.get("details", {}),
                    )
                )

            except asyncio.TimeoutError:
                results.append(
                    HealthResult(
                        name=check.__name__,
                        status=HealthStatus.UNHEALTHY,
                        response_time_ms=timeout * 1000,
                        message=f"Check timed out after {timeout}s",
                    )
                )
            except Exception as e:
                results.append(
                    HealthResult(
                        name=check.__name__,
                        status=HealthStatus.UNHEALTHY,
                        response_time_ms=(time.time() - start) * 1000,
                        message=str(e),
                    )
                )

        return results

    @classmethod
    async def is_healthy(cls) -> bool:
        """Check if all health checks pass."""
        results = await cls.run_checks("health")
        return all(r.status == HealthStatus.HEALTHY for r in results)

    @classmethod
    async def is_ready(cls) -> bool:
        """Check if service is ready."""
        results = await cls.run_checks("ready")
        return all(r.status in (HealthStatus.HEALTHY, HealthStatus.DEGRADED) for r in results)

    @classmethod
    async def is_alive(cls) -> bool:
        """Check if service is alive."""
        results = await cls.run_checks("live")
        return all(r.status != HealthStatus.UNHEALTHY for r in results)

    @classmethod
    def get_overall_status(cls, results: List[HealthResult]) -> HealthStatus:
        """Get overall health status from results."""
        if any(r.status == HealthStatus.UNHEALTHY for r in results):
            return HealthStatus.UNHEALTHY
        if any(r.status == HealthStatus.DEGRADED for r in results):
            return HealthStatus.DEGRADED
        if all(r.status == HealthStatus.HEALTHY for r in results):
            return HealthStatus.HEALTHY
        return HealthStatus.UNKNOWN


def health_check(func: Callable) -> Callable:
    """Decorator for general health checks."""
    HealthCheck.register("health", func)
    return func


def readiness_probe(func: Callable) -> Callable:
    """Decorator for Kubernetes readiness probes."""
    HealthCheck.register("ready", func)
    return func


def liveness_probe(func: Callable) -> Callable:
    """Decorator for Kubernetes liveness probes."""
    HealthCheck.register("live", func)
    return func


def startup_probe(func: Callable) -> Callable:
    """Decorator for Kubernetes startup probes."""
    HealthCheck.register("startup", func)
    return func


# Built-in health checks


@health_check
async def check_memory() -> Dict[str, Any]:
    """Check memory usage."""
    import psutil

    memory = psutil.virtual_memory()
    used_percent = memory.percent

    if used_percent > 90:
        return {
            "status": "unhealthy",
            "message": f"Memory usage critical: {used_percent}%",
            "details": {"used_percent": used_percent},
        }
    elif used_percent > 75:
        return {
            "status": "degraded",
            "message": f"Memory usage high: {used_percent}%",
            "details": {"used_percent": used_percent},
        }

    return {"status": "healthy", "details": {"used_percent": used_percent}}


@health_check
async def check_disk() -> Dict[str, Any]:
    """Check disk usage."""
    import psutil

    disk = psutil.disk_usage("/")
    used_percent = (disk.used / disk.total) * 100

    if used_percent > 90:
        return {
            "status": "unhealthy",
            "message": f"Disk usage critical: {used_percent:.1f}%",
            "details": {"used_percent": used_percent},
        }

    return {"status": "healthy", "details": {"used_percent": used_percent}}
