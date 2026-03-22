"""
Batch digest buffer: accumulate items per user/category and flush on a schedule.

Pair with cron, APScheduler, or a Celery beat task (see package README).
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, DefaultDict, Dict, List, Optional, Tuple

from .dto import EmailNotificationTarget, NotificationFanoutRequest, PushNotificationTarget


@dataclass
class DigestItem:
    """One notification line inside a digest."""

    title: str
    body: str
    data: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class DigestBuffer:
    """
    In-memory accumulator keyed by ``(user_id, category)``.

    Not durable — use for single-process demos or back with Redis in your app if needed.
    """

    def __init__(self) -> None:
        self._buf: DefaultDict[Tuple[str, str], List[DigestItem]] = defaultdict(list)

    def add(self, user_id: str, category: str, item: DigestItem) -> None:
        self._buf[(user_id, category)].append(item)

    def take_and_clear(self, user_id: str, category: str) -> List[DigestItem]:
        """Pop all items for the bucket and remove it."""
        key = (user_id, category)
        items = self._buf.pop(key, [])
        return items

    def drain_all(self) -> Dict[Tuple[str, str], List[DigestItem]]:
        """Take every bucket and clear the buffer (e.g. end-of-window sweep)."""
        out = dict(self._buf)
        self._buf.clear()
        return out

    def bucket_count(self) -> int:
        return len(self._buf)


def build_digest_fanout_request(
    *,
    items: List[DigestItem],
    digest_title: str = "Your notification digest",
    email: Optional[EmailNotificationTarget] = None,
    push: Optional[PushNotificationTarget] = None,
    category: Optional[str] = None,
    user_id: Optional[str] = None,
) -> NotificationFanoutRequest:
    """
    Build a single :class:`~fast_notifications.dto.NotificationFanoutRequest` from buffered rows.

    * *items* — non-empty list of digest lines (titles/bodies merged into one message).
    * At least one of *email* or *push* must be set (same rules as core DTO).
    """
    if not items:
        raise ValueError("items must be non-empty")
    lines = []
    for it in items:
        lines.append(f"• {it.title}: {it.body}")
    body = "\n".join(lines)
    extra: dict[str, Any] = {"digest_count": len(items)}
    if category:
        extra["category"] = category
    return NotificationFanoutRequest(
        title=digest_title,
        body=body,
        data=extra,
        email=email,
        push=push,
        user_id=user_id,
        category=category,
    )
