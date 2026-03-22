"""
Analytics / event tracking interface and factory.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Optional

from fast_core import AnalyticsConfiguration


class IAnalyticsBackend(ABC):
    """Interface for analytics/event tracking backends."""

    @abstractmethod
    def track(
        self,
        distinct_id: str,
        event_name: str,
        properties: Optional[dict[str, Any]] = None,
    ) -> None:
        """Track an event."""
        raise NotImplementedError

    @abstractmethod
    def identify(self, distinct_id: str, traits: Optional[dict[str, Any]] = None) -> None:
        """Identify a user."""
        raise NotImplementedError

    def delete_user(self, distinct_id: str) -> None:
        """
        Request downstream analytics to delete or anonymize this user (GDPR / right to erasure).

        Default is a no-op; HTTP and other backends may override to notify vendors.
        """
        return


def build_analytics_client() -> Optional[IAnalyticsBackend]:
    """
    Build an analytics client from AnalyticsConfiguration (config/analytics/config.json).
    Uses http_sink if enabled; otherwise no-op or optional Segment/PostHog/Mixpanel.
    """
    cfg = AnalyticsConfiguration().get_config()

    if getattr(cfg.http_sink, "enabled", False) and cfg.http_sink.endpoint:
        from .http_sink import HttpSinkAnalyticsBackend
        return HttpSinkAnalyticsBackend(
            endpoint=cfg.http_sink.endpoint,
            api_key=cfg.http_sink.api_key,
        )

    return None
