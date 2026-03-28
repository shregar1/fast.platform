"""Phone number normalization and validation via optional ``phonenumbers``."""

from __future__ import annotations

import re
from typing import Optional

from ..optional_imports import OptionalImports
from .abstraction import IPhoneUtility


class PhoneUtility(IPhoneUtility):
    """Normalize and validate phone numbers.

    **Dependencies:** Uses standard regex helpers by default, but provides
    enhanced validation via ``phonenumbers`` if available.
    """

    @staticmethod
    def normalize_digits(value: str) -> str:
        """Strip all non-digit characters from the phone number."""
        return re.sub(r"\D", "", str(value))

    @staticmethod
    def is_likely_e164(value: str) -> bool:
        """Heuristic check for E.164 format (leading plus, 7-15 digits)."""
        pattern = re.compile(r"^\+[1-9]\d{6,14}$")
        return bool(pattern.match(str(value)))

    @staticmethod
    def validate_region(value: str, region: str = "US") -> bool:
        """Validate a phone number for a given region (ISO-3166).

        **Note:** Requires ``phonenumbers`` package. Returns False if missing.
        """
        _, pn = OptionalImports.optional_import("phonenumbers", "parse")
        if pn:
            try:
                num = pn(value, region)
                from phonenumbers import is_valid_number

                return is_valid_number(num)
            except Exception:
                return False
        return False

    @staticmethod
    def format_e164(value: str, region: str = "US") -> Optional[str]:
        """Convert a phone number to E.164 format (e.g. "+15551234567").

        **Note:** Requires ``phonenumbers`` package.
        Returns normalized digits with leading plus as fallback.
        """
        _, parse = OptionalImports.optional_import("phonenumbers", "parse")
        if parse:
            try:
                num = parse(value, region)
                from phonenumbers import PhoneNumberFormat, format_number, is_valid_number

                if is_valid_number(num):
                    return format_number(num, PhoneNumberFormat.E164)
            except Exception:
                pass

        # Manual fallback
        digits = PhoneUtility.normalize_digits(value)
        return f"+{digits}" if digits else None


__all__ = ["PhoneUtility", "IPhoneUtility"]
