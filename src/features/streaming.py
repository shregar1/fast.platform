"""
Optional real-time adapters: poll snapshot file changes or SSE-friendly chunks.

These are intentionally lightweight (no LaunchDarkly streaming SDK).
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any, AsyncIterator, Dict, Optional

from .snapshot import load_snapshot_from_path


async def poll_snapshot_changes(
    path: str | Path,
    *,
    interval_seconds: float = 5.0,
) -> AsyncIterator[Dict[str, Any]]:
    """
    Async iterator that yields the parsed snapshot JSON whenever the file's mtime changes.

    First yield happens after the first successful read. Suitable for long-poll or SSE loops
    that rebuild a :class:`~fast_feature_flags.snapshot.SnapshotFeatureFlagsClient` in-process.
    """
    p = Path(path)
    last_mtime: Optional[float] = None
    while True:
        try:
            st = p.stat()
            m = st.st_mtime
            if last_mtime is None or m != last_mtime:
                last_mtime = m
                yield load_snapshot_from_path(p)
        except OSError:
            pass
        await asyncio.sleep(max(0.1, float(interval_seconds)))


def format_sse_event(data: Any, *, event: str = "snapshot", event_id: Optional[str] = None) -> str:
    """
    Format one Server-Sent Events frame (``event:`` / ``id:`` / ``data:``).

    ``data`` is JSON-encoded if not a string.
    """
    if not isinstance(data, str):
        payload = json.dumps(data, default=str, ensure_ascii=False)
    else:
        payload = data
    lines = []
    if event:
        lines.append(f"event: {event}")
    if event_id:
        lines.append(f"id: {event_id}")
    for line in payload.split("\n"):
        lines.append(f"data: {line}")
    lines.append("")
    lines.append("")
    return "\n".join(lines)


async def snapshot_sse_generator(path: str | Path, *, interval_seconds: float = 5.0) -> AsyncIterator[bytes]:
    """Async generator of UTF-8 SSE chunks for ``StreamingResponse`` (polls ``poll_snapshot_changes``)."""
    async for doc in poll_snapshot_changes(path, interval_seconds=interval_seconds):
        yield format_sse_event(doc).encode("utf-8")
