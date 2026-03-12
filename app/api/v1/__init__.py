"""
API v1 Blueprint
----------------
All v1 routes are registered here and exposed under /api/v1/
"""

from flask import Blueprint

api_v1_bp = Blueprint("api_v1", __name__)

# Import routes so they are registered on the blueprint
from . import health          # noqa: E402, F401
from .auth import auth_bp     # noqa: E402, F401
from .users import users_bp   # noqa: E402, F401

api_v1_bp.register_blueprint(auth_bp, url_prefix="/auth")
api_v1_bp.register_blueprint(users_bp, url_prefix="/users")
