"""Backend wrapper that validates ``properties`` against :class:`~fast_analytics.schema_registry.EventSchemaRegistry`."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from .base import IAnalyticsBackend

if TYPE_CHECKING:
    from .schema_registry import EventSchemaRegistry


class ValidatingAnalyticsBackend(IAnalyticsBackend):
    """
    If ``event_name`` contains ``@`` (versioned), validate ``properties`` before forwarding.

    Non-versioned names are passed through unchanged (use for ad-hoc or internal events).
    """

    def __init__(self, inner: IAnalyticsBackend, registry: EventSchemaRegistry) -> None:
        self._inner = inner
        self._registry = registry

    def track(
        self,
        distinct_id: str,
        event_name: str,
        properties: Optional[dict[str, Any]] = None,
    ) -> None:
        if "@" in event_name:
            self._registry.validate_properties(event_name, properties)
        self._inner.track(distinct_id, event_name, properties)

    def identify(self, distinct_id: str, traits: Optional[dict[str, Any]] = None) -> None:
        self._inner.identify(distinct_id, traits)

    def delete_user(self, distinct_id: str) -> None:
        self._inner.delete_user(distinct_id)
