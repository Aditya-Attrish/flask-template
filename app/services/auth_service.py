"""
Auth Service
------------
Business logic for authentication: registration, login, token validation.
Keeps route handlers thin and logic testable.
"""

from datetime import datetime, timezone
from typing import Tuple
from app.models.user import User
from app.extensions import db


class AuthService:

    @staticmethod
    def register(
        email: str,
        username: str,
        password: str,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> Tuple[User | None, str | None]:
        """
        Create a new user account.

        Returns:
            (User, None) on success
            (None, error_message) on failure
        """
        if User.find_by_email(email):
            return None, "Email already registered."

        if User.find_by_username(username):
            return None, "Username already taken."

        user = User(
            email=email.lower().strip(),
            username=username.strip(),
            first_name=first_name,
            last_name=last_name,
        )
        user.password = password  # triggers bcrypt hashing

        try:
            user.save()
        except Exception as exc:
            db.session.rollback()
            return None, f"Could not create account: {exc}"

        return user, None

    @staticmethod
    def login(email: str, password: str) -> Tuple[User | None, str | None]:
        """
        Authenticate a user.

        Returns:
            (User, None) on success
            (None, error_message) on failure
        """
        user = User.find_by_email(email)

        if not user or not user.check_password(password):
            return None, "Invalid email or password."

        if not user.is_active:
            return None, "Account is disabled. Contact support."

        if user.is_deleted:
            return None, "Account not found."

        # Record login timestamp
        user.last_login_at = datetime.now(timezone.utc)
        db.session.commit()

        return user, None

    @staticmethod
    def get_user(user_id: str | int) -> Tuple[User | None, str | None]:
        """Fetch a user by their JWT identity (user_id string)."""
        user = User.get_by_id(int(user_id))
        if not user or user.is_deleted:
            return None, "User not found."
        return user, None
