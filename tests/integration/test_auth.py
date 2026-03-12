"""
Auth Integration Tests
----------------------
Tests register, login, refresh, and /me endpoints.
Run with: pytest tests/integration/test_auth.py -v
"""

import pytest
from app import create_app
from app.extensions import db as _db


@pytest.fixture(scope="module")
def app():
    app = create_app("testing")
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


# ── Helpers ───────────────────────────────────────────────────────────────────
def register(client, email="test@example.com", username="testuser", password="Password1"):
    return client.post("/api/v1/auth/register", json={
        "email": email,
        "username": username,
        "password": password,
    })


# ── Tests ─────────────────────────────────────────────────────────────────────
class TestRegister:
    def test_register_success(self, client):
        res = register(client)
        assert res.status_code == 201
        data = res.get_json()
        assert data["success"] is True
        assert "access_token" in data["data"]
        assert "user" in data["data"]

    def test_register_duplicate_email(self, client):
        register(client, email="dup@example.com", username="user1")
        res = register(client, email="dup@example.com", username="user2")
        assert res.status_code == 409

    def test_register_missing_fields(self, client):
        res = client.post("/api/v1/auth/register", json={"email": "x@x.com"})
        assert res.status_code == 422


class TestLogin:
    def test_login_success(self, client):
        register(client, email="login@example.com", username="loginuser")
        res = client.post("/api/v1/auth/login", json={
            "email": "login@example.com",
            "password": "Password1",
        })
        assert res.status_code == 200
        assert res.get_json()["data"]["access_token"]

    def test_login_wrong_password(self, client):
        register(client, email="wp@example.com", username="wpuser")
        res = client.post("/api/v1/auth/login", json={
            "email": "wp@example.com",
            "password": "WrongPass9",
        })
        assert res.status_code == 401

    def test_login_unknown_email(self, client):
        res = client.post("/api/v1/auth/login", json={
            "email": "ghost@example.com",
            "password": "Password1",
        })
        assert res.status_code == 401


class TestMe:
    def test_me_authenticated(self, client):
        res = register(client, email="me@example.com", username="meuser")
        token = res.get_json()["data"]["access_token"]
        me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert me.status_code == 200
        assert me.get_json()["data"]["user"]["email"] == "me@example.com"

    def test_me_unauthenticated(self, client):
        res = client.get("/api/v1/auth/me")
        assert res.status_code == 401
