"""
Users Routes — /api/v1/users
-----------------------------
GET    /          → list users (admin only)
GET    /:id       → get user by id
PATCH  /:id       → update user (owner or admin)
DELETE /:id       → soft-delete user (owner or admin)
"""

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.user_service import UserService
from app.utils.responses import success, error
from app.utils.decorators import admin_required, owner_or_admin

users_bp = Blueprint("users", __name__)


@users_bp.get("/")
@jwt_required()
@admin_required
def list_users():
    """
    List all users with pagination.
    Query params: page (int), per_page (int)
    """
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    result = UserService.paginate(page=page, per_page=per_page)
    return success(result)


@users_bp.get("/<int:user_id>")
@jwt_required()
def get_user(user_id: int):
    """Fetch a single user by ID."""
    user, err = UserService.get_by_id(user_id)
    if err:
        return error(err, 404)
    return success({"user": user.to_dict()})


@users_bp.patch("/<int:user_id>")
@jwt_required()
@owner_or_admin
def update_user(user_id: int):
    """
    Update a user's profile fields.
    Only the account owner or an admin may update.
    """
    data = request.get_json() or {}
    user, err = UserService.update(user_id, **data)
    if err:
        return error(err, 400)
    return success({"user": user.to_dict()})


@users_bp.delete("/<int:user_id>")
@jwt_required()
@owner_or_admin
def delete_user(user_id: int):
    """Soft-delete a user account."""
    err = UserService.delete(user_id)
    if err:
        return error(err, 400)
    return success({"message": "User deleted successfully"})
