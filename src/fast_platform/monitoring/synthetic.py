"""Synthetic monitoring (uptime checks)."""

from typing import Callable, Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import asyncio
import time


class CheckStatus(Enum):
    """Check status."""

    PASS = "pass"
    FAIL = "fail"
    DEGRADED = "degraded"


@dataclass
class CheckResult:
    """Synthetic check result."""

    name: str
    status: CheckStatus
    response_time_ms: float
    timestamp: datetime
    message: Optional[str] = None
    details: Dict[str, Any] = None
    region: str = "default"


class SyntheticCheck:
    """A synthetic check."""

    def __init__(
        self,
        name: str,
        handler: Callable,
        interval: str = "1m",
        regions: List[str] = None,
        timeout: float = 30.0,
    ):
        """Execute __init__ operation.

        Args:
            name: The name parameter.
            handler: The handler parameter.
            interval: The interval parameter.
            regions: The regions parameter.
            timeout: The timeout parameter.
        """
        self.name = name
        self.handler = handler
        self.interval = self._parse_interval(interval)
        self.regions = regions or ["default"]
        self.timeout = timeout
        self._task: Optional[asyncio.Task] = None
        self._running = False
        self._history: List[CheckResult] = []
        self._max_history = 1000

    def _parse_interval(self, interval: str) -> float:
        """Parse interval string to seconds."""
        units = {"s": 1, "m": 60, "h": 3600}

        for unit, seconds in units.items():
            if interval.endswith(unit):
                return float(interval[:-1]) * seconds

        return float(interval)

    async def run(self) -> CheckResult:
        """Run the check once."""
        start = time.time()

        try:
            result = await asyncio.wait_for(self.handler(), timeout=self.timeout)
            elapsed = (time.time() - start) * 1000

            if isinstance(result, dict):
                status = CheckStatus.PASS if result.get("status") != "fail" else CheckStatus.FAIL
                message = result.get("message")
                details = result.get("details", {})
            else:
                status = CheckStatus.PASS if result else CheckStatus.FAIL
                message = None
                details = {}

            check_result = CheckResult(
                name=self.name,
                status=status,
                response_time_ms=elapsed,
                timestamp=datetime.utcnow(),
                message=message,
                details=details,
            )

        except asyncio.TimeoutError:
            check_result = CheckResult(
                name=self.name,
                status=CheckStatus.FAIL,
                response_time_ms=self.timeout * 1000,
                timestamp=datetime.utcnow(),
                message=f"Timeout after {self.timeout}s",
            )
        except Exception as e:
            check_result = CheckResult(
                name=self.name,
                status=CheckStatus.FAIL,
                response_time_ms=(time.time() - start) * 1000,
                timestamp=datetime.utcnow(),
                message=str(e),
            )

        # Store history
        self._history.append(check_result)
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history :]

        return check_result

    async def start(self) -> None:
        """Start continuous monitoring."""
        self._running = True
        self._task = asyncio.create_task(self._run_loop())

    async def stop(self) -> None:
        """Stop monitoring."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def _run_loop(self) -> None:
        """Run check loop."""
        while self._running:
            await self.run()
            await asyncio.sleep(self.interval)

    def get_uptime(self, hours: int = 24) -> float:
        """Calculate uptime percentage."""
        cutoff = datetime.utcnow().timestamp() - (hours * 3600)
        recent = [r for r in self._history if r.timestamp.timestamp() > cutoff]

        if not recent:
            return 100.0

        passes = sum(1 for r in recent if r.status == CheckStatus.PASS)
        return (passes / len(recent)) * 100


class SyntheticMonitor:
    """Synthetic monitoring manager."""

    _checks: Dict[str, SyntheticCheck] = {}

    @classmethod
    def register(cls, check: SyntheticCheck) -> None:
        """Register a check."""
        cls._checks[check.name] = check

    @classmethod
    async def start_all(cls) -> None:
        """Start all checks."""
        for check in cls._checks.values():
            await check.start()

    @classmethod
    async def stop_all(cls) -> None:
        """Stop all checks."""
        for check in cls._checks.values():
            await check.stop()

    @classmethod
    def get_status(cls) -> Dict[str, Any]:
        """Get overall status."""
        return {
            name: {
                "status": check._history[-1].status.value if check._history else "unknown",
                "uptime_24h": check.get_uptime(24),
                "last_check": check._history[-1].timestamp.isoformat() if check._history else None,
            }
            for name, check in cls._checks.items()
        }


def synthetic_check(
    name: Optional[str] = None,
    interval: str = "1m",
    regions: List[str] = None,
    timeout: float = 30.0,
):
    """Decorator to create a synthetic check.

    Args:
        name: Check name
        interval: Check interval (e.g., "1m", "5m", "1h")
        regions: Regions to check from
        timeout: Request timeout

    """

    def decorator(func: Callable):
        """Execute decorator operation.

        Args:
            func: The func parameter.

        Returns:
            The result of the operation.
        """
        check_name = name or func.__name__

        check = SyntheticCheck(
            name=check_name, handler=func, interval=interval, regions=regions, timeout=timeout
        )

        SyntheticMonitor.register(check)

        return func

    return decorator
