"""
Auth Routes — /api/v1/auth
--------------------------
POST /register  → create account
POST /login     → issue access + refresh tokens
POST /refresh   → rotate access token
POST /logout    → revoke token (client-side)
GET  /me        → current user info
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt,
)
from app.services.auth_service import AuthService
from app.utils.responses import success, error
from app.utils.validators import validate_json

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/register")
@validate_json("email", "username", "password")
def register():
    """
    Register a new user.

    Body: { "email": str, "username": str, "password": str }
    """
    data = request.get_json()
    user, err = AuthService.register(
        email=data["email"],
        username=data["username"],
        password=data["password"],
        first_name=data.get("first_name"),
        last_name=data.get("last_name"),
    )

    if err:
        return error(err, 409)

    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    return success({
        "user": user.to_dict(),
        "access_token": access_token,
        "refresh_token": refresh_token,
    }, 201)


@auth_bp.post("/login")
@validate_json("email", "password")
def login():
    """
    Authenticate and return JWT tokens.

    Body: { "email": str, "password": str }
    """
    data = request.get_json()
    user, err = AuthService.login(email=data["email"], password=data["password"])

    if err:
        return error(err, 401)

    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    return success({
        "user": user.to_dict(),
        "access_token": access_token,
        "refresh_token": refresh_token,
    })


@auth_bp.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    """Issue a new access token using the refresh token."""
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return success({"access_token": access_token})


@auth_bp.get("/me")
@jwt_required()
def me():
    """Return the currently authenticated user."""
    user_id = get_jwt_identity()
    user, err = AuthService.get_user(user_id)
    if err:
        return error(err, 404)
    return success({"user": user.to_dict()})
