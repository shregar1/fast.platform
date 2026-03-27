"""Versioned event names and JSON Schema validation."""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

import jsonschema

SchemaDict = Dict[str, Any]


def parse_versioned_event_name(full: str) -> Tuple[str, int]:
    """Parse ``name@<int>`` into ``(name, version)``.

    Example: ``checkout.completed@2`` → ``("checkout.completed", 2)``.
    """
    if "@" not in full:
        raise ValueError("versioned event name required, e.g. 'purchase@1'")
    name, ver_s = full.rsplit("@", 1)
    if not name.strip():
        raise ValueError("empty event name before '@'")
    try:
        ver = int(ver_s)
    except ValueError as e:
        raise ValueError(f"invalid version segment: {ver_s!r}") from e
    return name, ver


class EventSchemaRegistry:
    """Register JSON Schemas per ``(event_base_name, version)``.

    Use versioned strings ``{name}@{version}`` in :meth:`IAnalyticsBackend.track` together with
    :class:`fast_analytics.validating_backend.ValidatingAnalyticsBackend`.
    """

    def __init__(self, *, require_registration: bool = False) -> None:
        """Execute __init__ operation.

        Args:
            require_registration: The require_registration parameter.
        """
        self._schemas: Dict[Tuple[str, int], SchemaDict] = {}
        self._require_registration = require_registration

    def register(self, event_base_name: str, version: int, schema: SchemaDict) -> None:
        """Register JSON Schema for ``event_base_name`` at ``version``."""
        self._schemas[(event_base_name, version)] = schema

    def register_versioned(self, versioned_name: str, schema: SchemaDict) -> None:
        """Register using a single ``name@version`` string."""
        base, ver = parse_versioned_event_name(versioned_name)
        self.register(base, ver, schema)

    def schema_for(self, event_base_name: str, version: int) -> Optional[SchemaDict]:
        """Execute schema_for operation.

        Args:
            event_base_name: The event_base_name parameter.
            version: The version parameter.

        Returns:
            The result of the operation.
        """
        return self._schemas.get((event_base_name, version))

    def validate_properties(
        self, versioned_event_name: str, properties: Optional[dict[str, Any]]
    ) -> None:
        """Validate ``properties`` against the registered schema for ``versioned_event_name``.

        Raises ``jsonschema.ValidationError`` on mismatch, ``ValueError`` if registration is missing
        when :attr:`require_registration` is true.
        """
        base, ver = parse_versioned_event_name(versioned_event_name)
        key = (base, ver)
        schema = self._schemas.get(key)
        if schema is None:
            if self._require_registration:
                raise ValueError(f"no schema registered for {versioned_event_name!r}")
            return
        jsonschema.validate(instance=properties or {}, schema=schema)
