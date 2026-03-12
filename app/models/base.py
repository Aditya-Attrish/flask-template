"""
Base Model
----------
Abstract SQLAlchemy model providing common columns and helper methods
inherited by all domain models.
"""

from datetime import datetime, timezone
from typing import Any
from app.extensions import db


class TimestampMixin:
    """Adds created_at / updated_at columns to any model."""

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class SoftDeleteMixin:
    """Adds soft-delete support (marks row as deleted without removing it)."""

    deleted_at = db.Column(db.DateTime(timezone=True), nullable=True, default=None)

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    def soft_delete(self) -> None:
        self.deleted_at = datetime.now(timezone.utc)
        db.session.commit()

    @classmethod
    def active(cls):
        """Return a query filtered to non-deleted records."""
        return cls.query.filter(cls.deleted_at.is_(None))


class BaseModel(TimestampMixin, db.Model):
    """
    Abstract base model. All project models should inherit from this class.

    Provides:
    - Integer primary key
    - created_at / updated_at timestamps
    - to_dict() serialization helper
    - save() / delete() convenience methods
    """

    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    def save(self) -> "BaseModel":
        """Persist (insert or update) this instance to the database."""
        db.session.add(self)
        db.session.commit()
        return self

    def delete(self) -> None:
        """Hard-delete this instance from the database."""
        db.session.delete(self)
        db.session.commit()

    def to_dict(self, exclude: list[str] | None = None) -> dict[str, Any]:
        """
        Serialize model columns to a plain dictionary.

        Args:
            exclude: List of column names to omit from the output.

        Returns:
            Dictionary of column_name -> value pairs.
        """
        exclude = exclude or []
        result = {}
        for column in self.__table__.columns:
            if column.name not in exclude:
                value = getattr(self, column.name)
                if isinstance(value, datetime):
                    value = value.isoformat()
                result[column.name] = value
        return result

    def update(self, **kwargs) -> "BaseModel":
        """Update multiple attributes and commit."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        db.session.commit()
        return self

    @classmethod
    def get_by_id(cls, record_id: int) -> "BaseModel | None":
        """Fetch a single record by primary key."""
        return cls.query.get(record_id)

    @classmethod
    def get_all(cls) -> list["BaseModel"]:
        """Return all records for this model."""
        return cls.query.all()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}>"
