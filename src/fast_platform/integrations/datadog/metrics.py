"""Datadog metrics reporting."""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from functools import wraps
import time


@dataclass
class MetricPoint:
    """A metric data point."""

    name: str
    value: float
    timestamp: float
    tags: List[str]
    metric_type: str = "gauge"


class MetricsReporter:
    """Metrics reporter for Datadog."""

    def __init__(self, client: "DatadogClient", prefix: Optional[str] = None):
        """Execute __init__ operation.

        Args:
            client: The client parameter.
            prefix: The prefix parameter.
        """
        self.client = client
        self.prefix = prefix or "fastmvc"
        self._buffer: List[MetricPoint] = []
        self._buffer_size = 100

    def _full_metric_name(self, name: str) -> str:
        """Get full metric name with prefix."""
        return f"{self.prefix}.{name}"

    async def gauge(self, name: str, value: float, tags: Optional[List[str]] = None) -> bool:
        """Send a gauge metric."""
        return await self.client.send_metric(self._full_metric_name(name), value, tags, "gauge")

    async def count(self, name: str, value: int = 1, tags: Optional[List[str]] = None) -> bool:
        """Send a count metric."""
        return await self.client.send_metric(
            self._full_metric_name(name), float(value), tags, "count"
        )

    async def histogram(self, name: str, value: float, tags: Optional[List[str]] = None) -> bool:
        """Send a histogram metric."""
        return await self.client.send_metric(self._full_metric_name(name), value, tags, "histogram")

    async def timing(self, name: str, value_ms: float, tags: Optional[List[str]] = None) -> bool:
        """Send a timing metric."""
        return await self.client.send_metric(self._full_metric_name(name), value_ms, tags, "timer")

    def buffer(self, point: MetricPoint) -> None:
        """Buffer a metric point for batch sending."""
        self._buffer.append(point)

        if len(self._buffer) >= self._buffer_size:
            # Trigger flush in background
            import asyncio

            asyncio.create_task(self.flush())

    async def flush(self) -> None:
        """Flush buffered metrics."""
        if not self._buffer:
            return

        # Take current buffer
        batch = self._buffer[:]
        self._buffer.clear()

        # Send all metrics
        for point in batch:
            await self.client.send_metric(
                self._full_metric_name(point.name), point.value, point.tags, point.metric_type
            )


def metric(
    name: Optional[str] = None, metric_type: str = "gauge", tags: Optional[List[str]] = None
):
    """Decorator to send function metrics to Datadog.

    Args:
        name: Metric name (defaults to function name)
        metric_type: Type of metric
        tags: Additional tags

    """

    def decorator(func):
        """Execute decorator operation.

        Args:
            func: The func parameter.

        Returns:
            The result of the operation.
        """
        metric_name = name or f"function.{func.__name__}"
        base_tags = tags or []

        @wraps(func)
        async def wrapper(*args, **kwargs):
            """Execute wrapper operation.

            Returns:
                The result of the operation.
            """
            start = time.time()

            try:
                result = await func(*args, **kwargs)
                status = "success"
                return result
            except Exception:
                status = "error"
                raise
            finally:
                elapsed = (time.time() - start) * 1000

                # Send metrics
                # Note: Would need a global reporter instance
                # reporter.timing(f"{metric_name}.duration", elapsed, base_tags + [f"status:{status}"])
                # reporter.count(f"{metric_name}.calls", 1, base_tags + [f"status:{status}"])

        return wrapper

    return decorator
