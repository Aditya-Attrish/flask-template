"""
Validators
----------
Reusable input validation helpers.
"""

import re
from functools import wraps
from flask import request
from app.utils.responses import error

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$")
USERNAME_REGEX = re.compile(r"^[a-zA-Z0-9_]{3,30}$")


def validate_json(*required_fields):
    """Ensure JSON body is present and contains all required fields."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            data = request.get_json(silent=True)
            if not data:
                return error("Request body must be valid JSON.", 400)
            missing = [f for f in required_fields if not data.get(f)]
            if missing:
                return error(f"Missing required fields: {', '.join(missing)}", 422)
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def is_valid_email(email: str) -> bool:
    return bool(EMAIL_REGEX.match(email))


def is_valid_username(username: str) -> bool:
    return bool(USERNAME_REGEX.match(username))


def is_strong_password(password: str) -> bool:
    """Minimum 8 chars, 1 uppercase, 1 digit."""
    return (
        len(password) >= 8
        and any(c.isupper() for c in password)
        and any(c.isdigit() for c in password)
    )
