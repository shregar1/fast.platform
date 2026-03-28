"""Validation errors (:class:`ValidationError`)."""

from __future__ import annotations

from typing import Dict, List


class ValidationError(Exception):
    """Exception raised when validation fails."""

    def __init__(self, errors: Dict[str, List[str]]):
        """Execute __init__ operation.

        Args:
            errors: The errors parameter (mapping of field name to list of error messages).
        """
        self.errors = errors
        self.message = self._format_errors(errors)
        super().__init__(self.message)

    def _format_errors(self, errors: Dict[str, List[str]]) -> str:
        """Execute _format_errors operation.

        Args:
            errors: The errors parameter.

        Returns:
            The formatted error message string.
        """
        messages = []
        for field, field_errors in errors.items():
            for error in field_errors:
                messages.append(f"{field}: {error}")
        return "; ".join(messages)

    def to_dict(self) -> dict:
        """Convert to dictionary for API responses."""
        return {"error": "Validation failed", "errors": self.errors}
