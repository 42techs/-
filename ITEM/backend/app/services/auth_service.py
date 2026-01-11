# app/services/auth_service.py
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import jwt
import os

from app.models.user import User
from app import db


@dataclass
class ServiceResult:
    success: bool
    message: str
    data: Dict[str, Any] = field(default_factory=dict)


class AuthService:
    """认证服务类（不做“参数不能为空”校验，交给前端）"""

    JWT_ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS = 24
    REFRESH_TOKEN_EXPIRE_DAYS = 7

    @staticmethod
    def _secret_key() -> str:
        key = os.environ.get("JWT_SECRET_KEY")
        if not key:
            raise RuntimeError("JWT_SECRET_KEY is not set")
        return key

    # ================= 注册 =================

    @staticmethod
    def register_user(username: str, email: str, password: str) -> ServiceResult:
        # 参数校验：避免 None 导致的 generate_password_hash/encode 错误
        if not username or not email or not password:
            return ServiceResult(False, "参数缺失：用户名、邮箱和密码均为必填项")

        try:
            if User.query.filter_by(username=username).first():
                return ServiceResult(False, "用户名已存在")

            if User.query.filter_by(email=email).first():
                return ServiceResult(False, "邮箱已被注册")

            user = User(username=username, email=email)
            user.set_password(password)

            db.session.add(user)
            db.session.commit()

            return ServiceResult(
                True,
                "注册成功",
                {
                    "user": user.to_dict(),
                    "access_token": AuthService._generate_access_token(user.id),
                    "refresh_token": AuthService._generate_refresh_token(user.id),
                },
            )

        except Exception as e:
            db.session.rollback()
            return ServiceResult(False, f"注册失败: {str(e)}")

    # ================= 登录 =================

    @staticmethod
    def authenticate_user(username: str, password: str) -> ServiceResult:
        # 参数校验
        if not username or not password:
            return ServiceResult(False, "参数缺失：用户名和密码为必填项")

        try:
            user = User.query.filter_by(username=username).first()

            # 统一失败信息，不区分原因（安全）
            if not user or not user.check_password(password):
                return ServiceResult(False, "用户名或密码错误")

            if not user.is_active:
                return ServiceResult(False, "账户已被禁用")

            user.last_login = datetime.now(timezone.utc)
            db.session.commit()

            return ServiceResult(
                True,
                "登录成功",
                {
                    "user": user.to_dict(),
                    "access_token": AuthService._generate_access_token(user.id),
                    "refresh_token": AuthService._generate_refresh_token(user.id),
                },
            )

        except Exception as e:
            db.session.rollback()
            return ServiceResult(False, f"登录失败: {str(e)}")

    # ================= 刷新 Token =================

    @staticmethod
    def refresh_access_token(refresh_token: str) -> ServiceResult:
        payload = AuthService._verify_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            return ServiceResult(False, "刷新令牌无效或已过期")

        user = User.query.get(payload.get("user_id"))
        if not user or not user.is_active:
            return ServiceResult(False, "用户不存在或已被禁用")

        return ServiceResult(
            True,
            "刷新成功",
            {"access_token": AuthService._generate_access_token(user.id)},
        )

    # ================= 修改密码 =================

    @staticmethod
    def change_password(user_id: int, current_password: str, new_password: str) -> ServiceResult:
        try:
            if not current_password or not new_password:
                return ServiceResult(False, "参数缺失：当前密码和新密码为必填项")
            user = User.query.get(user_id)
            if not user or not user.check_password(current_password):
                return ServiceResult(False, "当前密码错误")

            user.set_password(new_password)
            db.session.commit()
            return ServiceResult(True, "密码修改成功")

        except Exception as e:
            db.session.rollback()
            return ServiceResult(False, f"密码修改失败: {str(e)}")

    # ================= JWT =================

    @staticmethod
    def _generate_access_token(user_id: int) -> str:
        now = datetime.now(timezone.utc)
        payload = {
            "user_id": user_id,
            "type": "access",
            "iat": now,
            "exp": now + timedelta(hours=AuthService.ACCESS_TOKEN_EXPIRE_HOURS),
        }
        return jwt.encode(payload, AuthService._secret_key(), algorithm=AuthService.JWT_ALGORITHM)

    @staticmethod
    def _generate_refresh_token(user_id: int) -> str:
        now = datetime.now(timezone.utc)
        payload = {
            "user_id": user_id,
            "type": "refresh",
            "iat": now,
            "exp": now + timedelta(days=AuthService.REFRESH_TOKEN_EXPIRE_DAYS),
        }
        return jwt.encode(payload, AuthService._secret_key(), algorithm=AuthService.JWT_ALGORITHM)

    @staticmethod
    def _verify_token(token: str) -> Optional[dict]:
        try:
            return jwt.decode(
                token,
                AuthService._secret_key(),
                algorithms=[AuthService.JWT_ALGORITHM],
            )
        except jwt.InvalidTokenError:
            return None

    @staticmethod
    def verify_access_token(token: str):
        payload = AuthService._verify_token(token)
        if not payload or payload.get("type") != "access":
            return False, None

        user = User.query.get(payload.get("user_id"))
        if not user or not user.is_active:
            return False, None

        return True, user
