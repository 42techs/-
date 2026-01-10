from flask import Blueprint, request, g
from app.services.auth_service import AuthService
from app.utils.jwt_auth import token_required
from app.utils.responses import api_ok, api_error

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    result = AuthService.register_user(
        data.get("username"),
        data.get("email"),
        data.get("password"),
    )

    if not result.success:
        return api_error(result.message, status_code=400)

    return api_ok(result.data, message=result.message, status_code=201)


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    result = AuthService.authenticate_user(
        data.get("username"),
        data.get("password"),
    )

    if not result.success:
        return api_error(result.message, status_code=401)

    return api_ok(result.data, message=result.message)


@auth_bp.post("/refresh")
def refresh():
    data = request.get_json(silent=True) or {}
    result = AuthService.refresh_access_token(data.get("refresh_token"))

    if not result.success:
        return api_error(result.message, status_code=401)

    return api_ok(result.data, message=result.message)


@auth_bp.get("/profile")
@token_required
def profile():
    return api_ok({"user": g.current_user.to_dict()})


@auth_bp.post("/change-password")
@token_required
def change_password():
    data = request.get_json(silent=True) or {}
    result = AuthService.change_password(
        g.current_user.id,
        data.get("current_password"),
        data.get("new_password"),
    )

    if not result.success:
        return api_error(result.message)

    return api_ok(message=result.message)
