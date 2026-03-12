"""
User Model
----------
Core user entity with password hashing and JWT token helpers.
"""

import bcrypt
from app.extensions import db
from .base import BaseModel, SoftDeleteMixin


class User(SoftDeleteMixin, BaseModel):
    """
    Application user.

    Relationships (add as your app grows):
        - orders: db.relationship("Order", back_populates="user")
        - profile: db.relationship("Profile", uselist=False, back_populates="user")
    """

    __tablename__ = "users"

    # ── Identity ──────────────────────────────────────────────────────────────
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    _password_hash = db.Column("password_hash", db.String(255), nullable=False)

    # ── Profile ───────────────────────────────────────────────────────────────
    first_name = db.Column(db.String(80), nullable=True)
    last_name = db.Column(db.String(80), nullable=True)
    avatar_url = db.Column(db.String(500), nullable=True)

    # ── Access Control ────────────────────────────────────────────────────────
    role = db.Column(
        db.Enum("admin", "moderator", "user", name="user_roles"),
        nullable=False,
        default="user",
    )
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    is_verified = db.Column(db.Boolean, nullable=False, default=False)

    # ── Security ──────────────────────────────────────────────────────────────
    last_login_at = db.Column(db.DateTime(timezone=True), nullable=True)

    # ── Password ──────────────────────────────────────────────────────────────
    @property
    def password(self):
        raise AttributeError("Password is write-only.")

    @password.setter
    def password(self, plain_text: str) -> None:
        self._password_hash = bcrypt.hashpw(
            plain_text.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

    def check_password(self, plain_text: str) -> bool:
        """Return True if the supplied password matches the stored hash."""
        return bcrypt.checkpw(
            plain_text.encode("utf-8"),
            self._password_hash.encode("utf-8"),
        )

    # ── Helpers ───────────────────────────────────────────────────────────────
    @property
    def full_name(self) -> str:
        parts = filter(None, [self.first_name, self.last_name])
        return " ".join(parts) or self.username

    def to_dict(self, exclude=None):
        """Override to always exclude the password hash."""
        excluded = list(exclude or []) + ["password_hash"]
        return super().to_dict(exclude=excluded)

    @classmethod
    def find_by_email(cls, email: str) -> "User | None":
        return cls.query.filter_by(email=email.lower().strip()).first()

    @classmethod
    def find_by_username(cls, username: str) -> "User | None":
        return cls.query.filter_by(username=username.strip()).first()
