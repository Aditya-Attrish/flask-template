"""
User Model Unit Tests
---------------------
Tests password hashing, to_dict(), soft-delete, and helpers.
Run with: pytest tests/unit/test_user_model.py -v
"""

import pytest
from app import create_app
from app.extensions import db as _db
from app.models.user import User


@pytest.fixture(scope="module")
def app():
    app = create_app("testing")
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture(autouse=True)
def clean_db(app):
    """Wipe users table before each test."""
    with app.app_context():
        _db.session.query(User).delete()
        _db.session.commit()
    yield


def make_user(email="u@test.com", username="testuser", password="Secret1"):
    u = User(email=email, username=username)
    u.password = password
    u.save()
    return u


class TestPasswordHashing:
    def test_password_is_hashed(self, app):
        with app.app_context():
            u = make_user()
            assert u._password_hash != "Secret1"

    def test_correct_password_validates(self, app):
        with app.app_context():
            u = make_user()
            assert u.check_password("Secret1") is True

    def test_wrong_password_fails(self, app):
        with app.app_context():
            u = make_user()
            assert u.check_password("Wrong123") is False

    def test_password_write_only(self, app):
        with app.app_context():
            u = make_user()
            with pytest.raises(AttributeError):
                _ = u.password


class TestToDict:
    def test_excludes_password_hash(self, app):
        with app.app_context():
            u = make_user()
            d = u.to_dict()
            assert "password_hash" not in d
            assert "email" in d

    def test_contains_expected_fields(self, app):
        with app.app_context():
            u = make_user()
            d = u.to_dict()
            assert "id" in d
            assert "created_at" in d


class TestSoftDelete:
    def test_soft_delete_sets_deleted_at(self, app):
        with app.app_context():
            u = make_user()
            assert u.is_deleted is False
            u.soft_delete()
            assert u.is_deleted is True
            assert u.deleted_at is not None

    def test_active_query_excludes_deleted(self, app):
        with app.app_context():
            u = make_user()
            u.soft_delete()
            active = User.active().all()
            assert u not in active
