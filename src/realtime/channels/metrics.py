"""Pluggable metrics for in-process channel hubs (subscribe / publish counters)."""

from __future__ import annotations

from collections import defaultdict
from typing import DefaultDict, Dict, Protocol, runtime_checkable


@runtime_checkable
class ChannelMetrics(Protocol):
    """Hook for observability (Prometheus, statsd, logging, etc.)."""

    def record_subscribe(self, topic: str) -> None:
        """A client joined ``topic``."""

    def record_unsubscribe(self, topic: str) -> None:
        """A client left ``topic``."""

    def record_publish(self, topic: str, *, recipient_count: int) -> None:
        """A message was dispatched to ``topic`` (``recipient_count`` targets)."""


class InMemoryChannelMetrics:
    """Simple counters suitable for tests and small apps.

    ``totals`` holds aggregate counts; ``by_topic`` holds per-topic breakdowns.
    """

    def __init__(self) -> None:
        """Execute __init__ operation."""
        self.subscribe_count: int = 0
        self.unsubscribe_count: int = 0
        self.publish_count: int = 0
        #: Sum of ``recipient_count`` across all ``record_publish`` calls (fan-out).
        self.recipient_fanout_total: int = 0
        self.by_topic: DefaultDict[str, Dict[str, int]] = defaultdict(
            lambda: {"subscribes": 0, "unsubscribes": 0, "publishes": 0}
        )

    def record_subscribe(self, topic: str) -> None:
        """Execute record_subscribe operation.

        Args:
            topic: The topic parameter.

        Returns:
            The result of the operation.
        """
        self.subscribe_count += 1
        self.by_topic[topic]["subscribes"] += 1

    def record_unsubscribe(self, topic: str) -> None:
        """Execute record_unsubscribe operation.

        Args:
            topic: The topic parameter.

        Returns:
            The result of the operation.
        """
        self.unsubscribe_count += 1
        self.by_topic[topic]["unsubscribes"] += 1

    def record_publish(self, topic: str, *, recipient_count: int) -> None:
        """Execute record_publish operation.

        Args:
            topic: The topic parameter.
            recipient_count: The recipient_count parameter.

        Returns:
            The result of the operation.
        """
        self.publish_count += 1
        self.recipient_fanout_total += recipient_count
        self.by_topic[topic]["publishes"] += 1
