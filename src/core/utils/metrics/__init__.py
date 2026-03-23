"""
Lightweight in-process metrics (no Prometheus client required).

Use for tests, smoke dashboards, or adapters that push to OTLP/Prometheus later.
"""

from __future__ import annotations

from .abstraction import IMetricsUtility
from .counter import Counter
from .histogram import Histogram
from .registry import MetricsRegistry

__all__ = ["Counter", "Histogram", "IMetricsUtility", "MetricsRegistry"]
