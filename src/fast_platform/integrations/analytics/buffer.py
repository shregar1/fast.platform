"""Buffer analytics calls for dry-run / dev and replay to a real backend."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Optional

from .base import IAnalyticsBackend

Record = Dict[str, Any]


class BufferedAnalyticsBackend(IAnalyticsBackend):
    """Record ``track`` / ``identify`` / ``delete_user`` calls.

    * ``dry_run=True`` (default): do not forward to ``inner``.
    * ``dry_run=False``: forward to ``inner`` immediately and still append to the buffer.

    Use :meth:`list_buffered` to inspect, :meth:`replay` to flush to another backend, :meth:`clear` to drop.
    """

    def __init__(self, inner: Optional[IAnalyticsBackend] = None, *, dry_run: bool = True) -> None:
        """Execute __init__ operation.

        Args:
            inner: The inner parameter.
            dry_run: The dry_run parameter.
        """
        self._inner = inner
        self._dry_run = dry_run
        self._buffer: List[Record] = []

    @property
    def buffer(self) -> List[Record]:
        """Mutable list of recorded operations (same objects as :meth:`list_buffered`)."""
        return self._buffer

    def track(
        self,
        distinct_id: str,
        event_name: str,
        properties: Optional[dict[str, Any]] = None,
    ) -> None:
        """Execute track operation.

        Args:
            distinct_id: The distinct_id parameter.
            event_name: The event_name parameter.
            properties: The properties parameter.

        Returns:
            The result of the operation.
        """
        rec: Record = {
            "op": "track",
            "distinct_id": distinct_id,
            "event": event_name,
            "properties": deepcopy(properties) if properties else {},
        }
        self._buffer.append(rec)
        if not self._dry_run and self._inner is not None:
            self._inner.track(distinct_id, event_name, properties)

    def identify(self, distinct_id: str, traits: Optional[dict[str, Any]] = None) -> None:
        """Execute identify operation.

        Args:
            distinct_id: The distinct_id parameter.
            traits: The traits parameter.

        Returns:
            The result of the operation.
        """
        rec: Record = {
            "op": "identify",
            "distinct_id": distinct_id,
            "traits": deepcopy(traits) if traits else {},
        }
        self._buffer.append(rec)
        if not self._dry_run and self._inner is not None:
            self._inner.identify(distinct_id, traits)

    def delete_user(self, distinct_id: str) -> None:
        """Execute delete_user operation.

        Args:
            distinct_id: The distinct_id parameter.

        Returns:
            The result of the operation.
        """
        rec: Record = {"op": "delete_user", "distinct_id": distinct_id}
        self._buffer.append(rec)
        if not self._dry_run and self._inner is not None:
            self._inner.delete_user(distinct_id)

    def list_buffered(self) -> List[Record]:
        """Copy of buffered records (for inspection or persistence)."""
        return [deepcopy(r) for r in self._buffer]

    def replay(self, target: Optional[IAnalyticsBackend] = None) -> None:
        """Send buffered operations to ``target`` (or the constructor ``inner``) and clear the buffer."""
        t = target or self._inner
        if t is None:
            raise ValueError("replay requires a target backend or constructor inner=")
        for rec in self._buffer:
            op = rec["op"]
            if op == "track":
                t.track(rec["distinct_id"], rec["event"], rec.get("properties"))
            elif op == "identify":
                t.identify(rec["distinct_id"], rec.get("traits"))
            elif op == "delete_user":
                t.delete_user(rec["distinct_id"])
        self._buffer.clear()

    def clear(self) -> None:
        """Drop buffered records without sending."""
        self._buffer.clear()
