"""
Simple Validation Helpers for FastMVC

Lightweight validation before Pydantic models.

Usage:
    from core.validation import validate, validate_json, ValidationError
    
    # Simple validation
    @validate({
        "email": "required|email",
        "age": "required|integer|min:18|max:120"
    })
    async def create_user(data: dict):
        # data is validated here
        return {"message": "User created"}
    
    # Manual validation
    errors = validate_data({
        "email": "test@example.com",
        "age": 25
    }, {
        "email": "required|email",
        "age": "required|integer|min:18"
    })
    
    if errors:
        raise ValidationError(errors)
    
    # Individual rules
    from core.validation import rules
    
    rules.email("test@example.com")  # True
    rules.email("invalid")           # False
    
    rules.min_length("hello", 3)     # True
    rules.min_length("hi", 3)        # False

Available Rules:
    - required      - Field must be present and not empty
    - email         - Valid email format
    - url           - Valid URL format
    - integer       - Integer value
    - number        - Numeric value (int or float)
    - boolean       - Boolean value
    - string        - String value
    - min:n         - Minimum length (strings) or value (numbers)
    - max:n         - Maximum length (strings) or value (numbers)
    - between:n,m   - Between n and m (inclusive)
    - regex:pattern - Match regex pattern
    - in:a,b,c      - Value in list
    - uuid          - Valid UUID format
    - json          - Valid JSON string
    - alpha         - Alphabetic characters only
    - alphanumeric  - Alphanumeric characters only
    - slug          - URL-friendly slug format
    - phone         - Phone number format
"""

import re
import json
from typing import Any, Callable, Dict, List, Optional, Union
from functools import wraps


class ValidationError(Exception):
    """Exception raised when validation fails."""
    
    def __init__(self, errors: Dict[str, List[str]]):
        self.errors = errors
        self.message = self._format_errors(errors)
        super().__init__(self.message)
    
    def _format_errors(self, errors: Dict[str, List[str]]) -> str:
        messages = []
        for field, field_errors in errors.items():
            for error in field_errors:
                messages.append(f"{field}: {error}")
        return "; ".join(messages)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for API responses."""
        return {
            "error": "Validation failed",
            "errors": self.errors
        }


class RuleEngine:
    """Validation rule engine."""
    
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
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, value))
    
    @staticmethod
    def url(value: Any) -> bool:
        """Check if value is valid URL."""
        if not isinstance(value, str):
            return False
        pattern = r'^https?://[^\s/$.?#].[^\s]*$'
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
            return value.lower() in ('true', 'false', '1', '0', 'yes', 'no')
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
        pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
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
        pattern = r'^[a-z0-9]+(?:-[a-z0-9]+)*$'
        return bool(re.match(pattern, value))
    
    @staticmethod
    def phone(value: Any) -> bool:
        """Check if value is valid phone number."""
        if not isinstance(value, str):
            return False
        # Simple international phone validation
        pattern = r'^[\+]?[1-9][\d\s\-\(\)]{8,}$'
        return bool(re.match(pattern, value))


# Global rule engine instance
rules = RuleEngine()


def parse_rule(rule_string: str) -> tuple:
    """
    Parse a rule string into rule name and parameters.
    
    Examples:
        "min:18" -> ("min", [18])
        "between:18,65" -> ("between", [18, 65])
        "required" -> ("required", [])
    """
    if ":" in rule_string:
        name, params = rule_string.split(":", 1)
        params = [p.strip() for p in params.split(",")]
        
        # Convert numeric parameters
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


def validate_field(value: Any, rules_string: str) -> List[str]:
    """
    Validate a single field against rule string.
    
    Args:
        value: Value to validate
        rules_string: Pipe-separated rules (e.g., "required|email|min:5")
    
    Returns:
        List of error messages (empty if valid)
    """
    errors = []
    rule_list = [r.strip() for r in rules_string.split("|")]
    
    for rule_str in rule_list:
        if not rule_str:
            continue
        
        rule_name, params = parse_rule(rule_str)
        
        # Skip other rules if value is empty and not required
        if rule_name != "required" and not RuleEngine.required(value):
            continue
        
        # Get validation method
        method = getattr(rules, rule_name, None)
        if not method:
            errors.append(f"Unknown rule: {rule_name}")
            continue
        
        # Validate
        try:
            if params:
                is_valid = method(value, *params)
            else:
                is_valid = method(value)
            
            if not is_valid:
                # Generate error message
                if params:
                    errors.append(f"Failed {rule_name} validation ({', '.join(map(str, params))})")
                else:
                    errors.append(f"Failed {rule_name} validation")
        except Exception as e:
            errors.append(f"Validation error: {e}")
    
    return errors


def validate_data(data: dict, rules: dict) -> Dict[str, List[str]]:
    """
    Validate data against rules.
    
    Args:
        data: Dictionary of data to validate
        rules: Dictionary of field -> rule strings
    
    Returns:
        Dictionary of field -> error messages (empty if all valid)
    
    Example:
        errors = validate_data(
            {"email": "test@example.com", "age": 25},
            {"email": "required|email", "age": "required|integer|min:18"}
        )
        if errors:
            print(errors)  # {"age": ["Failed integer validation"]}
    """
    errors = {}
    
    for field, field_rules in rules.items():
        value = data.get(field)
        field_errors = validate_field(value, field_rules)
        
        if field_errors:
            errors[field] = field_errors
    
    return errors


def validate(rules: dict):
    """
    Decorator to validate request data.
    
    Usage:
        @validate({
            "email": "required|email",
            "password": "required|min:8"
        })
        async def create_user(request):
            data = await request.json()
            # Data is validated here
            return {"message": "Created"}
    
    Args:
        rules: Dictionary of field -> validation rules
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Try to extract data from various sources
            data = None
            
            # Check for request object in args
            for arg in args:
                if hasattr(arg, 'json'):
                    try:
                        data = await arg.json()
                    except:
                        pass
                    break
                elif hasattr(arg, 'body'):
                    try:
                        import json
                        body = await arg.body()
                        data = json.loads(body)
                    except:
                        pass
                    break
                elif isinstance(arg, dict):
                    data = arg
                    break
            
            # Check kwargs
            if data is None:
                data = kwargs.get('data') or kwargs.get('body') or kwargs.get('request')
            
            if data is None:
                raise ValidationError({"_general": ["Could not extract data for validation"]})
            
            # Validate
            errors = validate_data(data, rules)
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
                data = kwargs.get('data') or kwargs.get('body')
            
            if data is None:
                raise ValidationError({"_general": ["Could not extract data for validation"]})
            
            errors = validate_data(data, rules)
            if errors:
                raise ValidationError(errors)
            
            return func(*args, **kwargs)
        
        import inspect
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator


# FastAPI-specific validation decorator
def validate_json(rules: dict):
    """
    Decorator for FastAPI endpoints that validates JSON body.
    
    Usage:
        from fastapi import FastAPI, Request
        
        app = FastAPI()
        
        @app.post("/users")
        @validate_json({
            "email": "required|email",
            "age": "required|integer|min:18"
        })
        async def create_user(request: Request):
            data = await request.json()
            return {"message": f"Created user with email {data['email']}"}
    """
    return validate(rules)


# Helper for quick validation
def quick_validate(data: dict, **field_rules) -> Optional[List[str]]:
    """
    Quick validation for simple cases.
    
    Usage:
        errors = quick_validate(
            {"email": "test@example.com"},
            email="required|email"
        )
        if errors:
            print(errors)
    
    Returns:
        List of error strings or None if valid
    """
    errors = validate_data(data, field_rules)
    
    if not errors:
        return None
    
    # Flatten errors to list
    flat_errors = []
    for field, field_errors in errors.items():
        for error in field_errors:
            flat_errors.append(f"{field}: {error}")
    
    return flat_errors
