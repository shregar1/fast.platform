"""Resolve per-queue job timeouts from ``JobsConfiguration.queue_timeouts``."""

from __future__ import annotations

from typing import Dict, Optional

from from fast_platform import JobsConfiguration


def get_queue_timeouts() -> Dict[str, int]:
    """Return the ``queue_name -> seconds`` map from config (copy)."""
    cfg = JobsConfiguration().get_config()
    return dict(cfg.queue_timeouts or {})


def resolve_job_timeout_seconds(
    queue_name: str,
    *,
    explicit: Optional[int] = None,
    queue_timeouts: Optional[Dict[str, int]] = None,
) -> Optional[int]:
    """
    Return timeout in seconds: ``explicit`` if set, else ``queue_timeouts[queue]``,
    else ``queue_timeouts[\"default\"]``.

    If ``queue_timeouts`` is ``None``, uses ``JobsConfiguration.queue_timeouts``.

    Returns ``None`` when no mapping applies and no explicit ``explicit`` value.
    ``explicit`` is always clamped to at least ``1`` when provided.
    """
    if explicit is not None:
        return max(1, int(explicit))
    timeouts = queue_timeouts if queue_timeouts is not None else get_queue_timeouts()
    if not timeouts:
        return None
    if queue_name in timeouts:
        return max(1, int(timeouts[queue_name]))
    if "default" in timeouts:
        return max(1, int(timeouts["default"]))
    return None
