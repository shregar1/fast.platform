"""Backend wrapper that validates ``properties`` against :class:`~fast_analytics.schema_registry.EventSchemaRegistry`."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from .base import IAnalyticsBackend

if TYPE_CHECKING:
    from .schema_registry import EventSchemaRegistry


class ValidatingAnalyticsBackend(IAnalyticsBackend):
    """If ``event_name`` contains ``@`` (versioned), validate ``properties`` before forwarding.

    Non-versioned names are passed through unchanged (use for ad-hoc or internal events).
    """

    def __init__(self, inner: IAnalyticsBackend, registry: EventSchemaRegistry) -> None:
        """Execute __init__ operation.

        Args:
            inner: The inner parameter.
            registry: The registry parameter.
        """
        self._inner = inner
        self._registry = registry

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
        if "@" in event_name:
            self._registry.validate_properties(event_name, properties)
        self._inner.track(distinct_id, event_name, properties)

    def identify(self, distinct_id: str, traits: Optional[dict[str, Any]] = None) -> None:
        """Execute identify operation.

        Args:
            distinct_id: The distinct_id parameter.
            traits: The traits parameter.

        Returns:
            The result of the operation.
        """
        self._inner.identify(distinct_id, traits)

    def delete_user(self, distinct_id: str) -> None:
        """Execute delete_user operation.

        Args:
            distinct_id: The distinct_id parameter.

        Returns:
            The result of the operation.
        """
        self._inner.delete_user(distinct_id)
