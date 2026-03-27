"""Response sanitization for the API.

Removes internal identifiers from response payloads so the frontend never
receives raw `id` or `*_id` fields; use `urn` (and `*_urn`) for resource
identification instead.

Used by:
- BaseResponseDTO.model_dump(): sanitizes the `data` payload before serialization.

Request validation and sanitization (inbound) are handled by EnhancedBaseModel
and SecurityValidators; see docs/SECURITY.md for the full picture.
"""

from __future__ import annotations

from typing import Any

from .abstraction import ISanitization

__all__ = ["SanitizationJsonUtility"]


class SanitizationJsonUtility(ISanitization):
    """Remove internal ``id`` / ``*_id`` keys from API response dicts (recursive)."""

    @staticmethod
    def sanitize_for_api(data: dict) -> dict:
        """Remove `id` and any key ending with `_id` from a dict so API responses
        never expose internal IDs to the frontend. Callers should ensure `urn`
        (and optionally `*_urn`) are present where needed.
        """
        if not isinstance(data, dict):
            return data

        return {
            k: SanitizationJsonUtility._sanitize_value(v)
            for k, v in data.items()
            if k != "id" and not k.endswith("_id")
        }

    @staticmethod
    def _sanitize_value(value: Any) -> Any:
        """Recursively sanitize nested dicts and lists of dicts."""
        if isinstance(value, dict):
            return SanitizationJsonUtility.sanitize_for_api(value)

        if isinstance(value, list):
            return [SanitizationJsonUtility._sanitize_value(item) for item in value]

        return value
