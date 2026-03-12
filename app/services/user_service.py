"""
User Service
------------
Business logic for user CRUD operations.
"""

from typing import Tuple
from flask import current_app
from app.models.user import User
from app.extensions import db

# Fields the user is allowed to update via the API
UPDATABLE_FIELDS = {"first_name", "last_name", "username", "avatar_url"}


class UserService:

    @staticmethod
    def get_by_id(user_id: int) -> Tuple[User | None, str | None]:
        user = User.active().filter_by(id=user_id).first()
        if not user:
            return None, "User not found."
        return user, None

    @staticmethod
    def paginate(page: int = 1, per_page: int = 20) -> dict:
        """Return a paginated list of active users."""
        per_page = min(per_page, current_app.config["MAX_PAGE_SIZE"])

        pagination = (
            User.active()
            .order_by(User.created_at.desc())
            .paginate(page=page, per_page=per_page, error_out=False)
        )

        return {
            "users": [u.to_dict() for u in pagination.items],
            "total": pagination.total,
            "page": pagination.page,
            "per_page": pagination.per_page,
            "pages": pagination.pages,
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev,
        }

    @staticmethod
    def update(user_id: int, **kwargs) -> Tuple[User | None, str | None]:
        user = User.active().filter_by(id=user_id).first()
        if not user:
            return None, "User not found."

        # Only allow whitelisted fields
        safe_data = {k: v for k, v in kwargs.items() if k in UPDATABLE_FIELDS}

        # Check username uniqueness if changing it
        new_username = safe_data.get("username")
        if new_username and new_username != user.username:
            existing = User.find_by_username(new_username)
            if existing:
                return None, "Username already taken."

        try:
            user.update(**safe_data)
        except Exception as exc:
            db.session.rollback()
            return None, f"Update failed: {exc}"

        return user, None

    @staticmethod
    def delete(user_id: int) -> str | None:
        user = User.active().filter_by(id=user_id).first()
        if not user:
            return "User not found."

        try:
            user.soft_delete()
        except Exception as exc:
            db.session.rollback()
            return f"Delete failed: {exc}"

        return None
