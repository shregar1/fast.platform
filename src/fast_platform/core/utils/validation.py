from __future__ import annotations
"""Validation Utility for FastPlatform.

Concrete implementation of validation helpers (rules, decorators, and data validation)
inheriting from IUtility.
"""

from ..constants import VALIDATION_EXTRACTION_ERROR, MAX_KEYS_VALIDATION_ERROR

import re
import json
import inspect
from typing import Any, Callable, Dict, List, Optional, Union
from functools import wraps

from ..errors.validationerror import ValidationError
from .abstraction import IUtility


class ValidationUtility(IUtility):
    """Validation utility providing rules, data validation, and decorators."""

    # --- Rule Engine (Internal static methods) ---

    @staticmethod
    def required(value: Any) -> bool:
        """Check if value is present and not empty."""
        if value is None:
            return False
        if isinstance(value, str) and not value.strip():
            return False
        if isinstance(value, (list, dict)) and len(value) == 0:
            return False
        return True

    @staticmethod
    def email(value: Any) -> bool:
        """Check if value is valid email."""
        if not isinstance(value, str):
            return False
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, value))

    @staticmethod
    def url(value: Any) -> bool:
        """Check if value is valid URL."""
        if not isinstance(value, str):
            return False
        pattern = r"^https?://[^\s/$.?#].[^\s]*$"
        return bool(re.match(pattern, value, re.IGNORECASE))

    @staticmethod
    def integer(value: Any) -> bool:
        """Check if value is integer."""
        if isinstance(value, int) and not isinstance(value, bool):
            return True
        if isinstance(value, str):
            try:
                int(value)
                return True
            except ValueError:
                return False
        return False

    @staticmethod
    def number(value: Any) -> bool:
        """Check if value is numeric."""
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return True
        if isinstance(value, str):
            try:
                float(value)
                return True
            except ValueError:
                return False
        return False

    @staticmethod
    def boolean(value: Any) -> bool:
        """Check if value is boolean."""
        if isinstance(value, bool):
            return True
        if isinstance(value, str):
            return value.lower() in ("true", "false", "1", "0", "yes", "no")
        return False

    @staticmethod
    def string(value: Any) -> bool:
        """Check if value is string."""
        return isinstance(value, str)

    @staticmethod
    def min(value: Any, threshold: Union[int, float]) -> bool:
        """Check if value >= threshold."""
        if isinstance(value, (int, float)):
            return value >= threshold
        if isinstance(value, str):
            return len(value) >= threshold
        if isinstance(value, (list, dict)):
            return len(value) >= threshold
        return False

    @staticmethod
    def max(value: Any, threshold: Union[int, float]) -> bool:
        """Check if value <= threshold."""
        if isinstance(value, (int, float)):
            return value <= threshold
        if isinstance(value, str):
            return len(value) <= threshold
        if isinstance(value, (list, dict)):
            return len(value) <= threshold
        return False

    @staticmethod
    def between(value: Any, min_val: Union[int, float], max_val: Union[int, float]) -> bool:
        """Check if value is between min and max."""
        if isinstance(value, (int, float)):
            return min_val <= value <= max_val
        if isinstance(value, str):
            return min_val <= len(value) <= max_val
        return False

    @staticmethod
    def regex(value: Any, pattern: str) -> bool:
        """Check if value matches regex pattern."""
        if not isinstance(value, str):
            return False
        return bool(re.match(pattern, value))

    @staticmethod
    def in_list(value: Any, allowed: List[Any]) -> bool:
        """Check if value is in allowed list."""
        return value in allowed

    @staticmethod
    def uuid(value: Any) -> bool:
        """Check if value is valid UUID."""
        if not isinstance(value, str):
            return False
        pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
        return bool(re.match(pattern, value, re.IGNORECASE))

    @staticmethod
    def is_json(value: Any) -> bool:
        """Check if value is valid JSON string."""
        if not isinstance(value, str):
            return False
        try:
            json.loads(value)
            return True
        except json.JSONDecodeError:
            return False

    @staticmethod
    def alpha(value: Any) -> bool:
        """Check if value contains only alphabetic characters."""
        if not isinstance(value, str):
            return False
        return value.isalpha()

    @staticmethod
    def alphanumeric(value: Any) -> bool:
        """Check if value contains only alphanumeric characters."""
        if not isinstance(value, str):
            return False
        return value.isalnum()

    @staticmethod
    def slug(value: Any) -> bool:
        """Check if value is valid URL slug."""
        if not isinstance(value, str):
            return False
        pattern = r"^[a-z0-9]+(?:-[a-z0-9]+)*$"
        return bool(re.match(pattern, value))

    @staticmethod
    def phone(value: Any) -> bool:
        """Check if value is valid phone number."""
        if not isinstance(value, str):
            return False
        pattern = r"^[\+]?[1-9][\d\s\-\(\)]{8,}$"
        return bool(re.match(pattern, value))

    # --- Logic Helpers ---

    @classmethod
    def parse_rule(cls, rule_string: str) -> tuple[str, list]:
        """Parse a rule string into rule name and parameters."""
        if ":" in rule_string:
            name, params = rule_string.split(":", 1)
            params = [p.strip() for p in params.split(",")]

            converted_params = []
            for p in params:
                try:
                    if "." in p:
                        converted_params.append(float(p))
                    else:
                        converted_params.append(int(p))
                except ValueError:
                    converted_params.append(p)

            return name, converted_params

        return rule_string, []

    @classmethod
    def validate_field(cls, value: Any, rules_string: str) -> List[str]:
        """Validate a single field against rule string."""
        errors = []
        rule_list = [r.strip() for r in rules_string.split("|")]

        for rule_str in rule_list:
            if not rule_str:
                continue

            rule_name, params = cls.parse_rule(rule_str)

            if rule_name != "required" and not cls.required(value):
                continue

            method = getattr(cls, rule_name, None)
            if not method:
                errors.append(f"Unknown rule: {rule_name}")
                continue

            try:
                is_valid = method(value, *params) if params else method(value)
                if not is_valid:
                    if params:
                        errors.append(f"Failed {rule_name} validation ({', '.join(map(str, params))})")
                    else:
                        errors.append(f"Failed {rule_name} validation")
            except Exception as e:
                errors.append(f"Validation error: {e}")

        return errors

    @classmethod
    def validate_data(cls, data: dict, rules: dict) -> Dict[str, List[str]]:
        """Validate data against rules dictionary."""
        errors = {}
        for field, field_rules in rules.items():
            value = data.get(field)
            field_errors = cls.validate_field(value, field_rules)
            if field_errors:
                errors[field] = field_errors
        return errors

    @classmethod
    def quick_validate(cls, data: dict, **field_rules) -> Optional[List[str]]:
        """Quick validation for simple cases returning flattened list of errors."""
        errors = cls.validate_data(data, field_rules)
        if not errors:
            return None

        flat_errors = []
        for field, field_errors in errors.items():
            for error in field_errors:
                flat_errors.append(f"{field}: {error}")
        return flat_errors

    # --- Decorators ---

    @classmethod
    def validate(cls, rules: dict):
        """Decorator to validate request data."""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                data = None
                for arg in args:
                    if hasattr(arg, "json"):
                        try:
                            data = await arg.json()
                        except:
                            pass
                        break
                    elif hasattr(arg, "body"):
                        try:
                            body = await arg.body()
                            data = json.loads(body)
                        except:
                            pass
                        break
                    elif isinstance(arg, dict):
                        data = arg
                        break

                if data is None:
                    data = kwargs.get("data") or kwargs.get("body") or kwargs.get("request")

                if data is None:
                    raise ValidationError({"_general": ["Could not extract data for validation"]})

                errors = cls.validate_data(data, rules)
                if errors:
                    raise ValidationError(errors)

                return await func(*args, **kwargs)

            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                data = None
                for arg in args:
                    if isinstance(arg, dict):
                        data = arg
                        break

                if data is None:
                    data = kwargs.get("data") or kwargs.get("body")

                if data is None:
                    raise ValidationError({"_general": ["Could not extract data for validation"]})

                errors = cls.validate_data(data, rules)
                if errors:
                    raise ValidationError(errors)

                return func(*args, **kwargs)

            if inspect.iscoroutinefunction(func):
                return async_wrapper
            return sync_wrapper

        return decorator

    @classmethod
    def validate_json(cls, rules: dict):
        """Decorator for FastAPI endpoints that validates JSON body."""
        return cls.validate(rules)


# --- Backward Compatible Aliases ---

# Regional/Global instance for easy access
rules = ValidationUtility  # All methods are static or class methods

validate = ValidationUtility.validate
validate_json = ValidationUtility.validate_json
validate_data = ValidationUtility.validate_data
validate_field = ValidationUtility.validate_field
quick_validate = ValidationUtility.quick_validate
parse_rule = ValidationUtility.parse_rule
RuleEngine = ValidationUtility
