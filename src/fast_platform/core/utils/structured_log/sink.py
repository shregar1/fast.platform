"""Protocol for structured log sinks (stdout, loguru, etc.)."""

from __future__ import annotations

from typing import Any, Mapping, Protocol, runtime_checkable

__all__ = ["StructuredLogSink"]


@runtime_checkable
class StructuredLogSink(Protocol):
    """Protocol for adapters (stdout, loguru, etc.)."""

    def emit(self, record: Mapping[str, Any]) -> None:
        """Deliver a structured record (e.g. write JSON line)."""
        ...
