"""
Custom Decorators
-----------------
Reusable decorators for authorization and request validation.
"""

from functools import wraps
from flask import request
from flask_jwt_extended import get_jwt_identity
from app.utils.responses import error


def admin_required(fn):
    """
    Require that the current JWT user has the 'admin' role.
    Must be used AFTER @jwt_required().
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        from app.models.user import User
        user_id = get_jwt_identity()
        user = User.get_by_id(int(user_id))
        if not user or user.role != "admin":
            return error("Admin access required.", 403)
        return fn(*args, **kwargs)
    return wrapper


def owner_or_admin(fn):
    """
    Allow access if the JWT user is the resource owner OR has the admin role.
    The route must have a `user_id` URL parameter.
    Must be used AFTER @jwt_required().
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        from app.models.user import User
        current_id = int(get_jwt_identity())
        resource_user_id = kwargs.get("user_id")

        if current_id != resource_user_id:
            user = User.get_by_id(current_id)
            if not user or user.role != "admin":
                return error("Access denied.", 403)

        return fn(*args, **kwargs)
    return wrapper


def validate_json(*required_fields):
    """
    Decorator that ensures the request has a JSON body with required fields.

    Usage:
        @validate_json("email", "password")
        def login(): ...
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            data = request.get_json(silent=True)
            if not data:
                return error("Request body must be valid JSON.", 400)
            missing = [f for f in required_fields if f not in data or data[f] == ""]
            if missing:
                return error(f"Missing required fields: {', '.join(missing)}", 422)
            return fn(*args, **kwargs)
        return wrapper
    return decorator
