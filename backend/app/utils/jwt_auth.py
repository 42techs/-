# -*- coding: utf-8 -*-
# app/utils/jwt_auth.py
from functools import wraps
from flask import request, g, current_app
from app.services.auth_service import AuthService
from app.utils.responses import api_error


def token_required(f):
    """JWT Token验证装饰器"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        # 获取Authorization头
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header:
            return api_error('缺少认证令牌', status_code=401)
        
        if not auth_header.startswith('Bearer '):
            return api_error('认证令牌格式错误', status_code=401)
        
        # 提取token
        try:
            token = auth_header.split(' ', 1)[1]
        except IndexError:
            return api_error('认证令牌格式错误', status_code=401)
        
        # 验证token
        ok, user = AuthService.verify_access_token(token)
        if not ok:
            return api_error('认证令牌无效或已过期', status_code=401)
        
        # 将用户信息存入g对象
        g.current_user = user
        
        return f(*args, **kwargs)
    
    return wrapper


def optional_token(f):
    """可选的Token验证装饰器（用于某些接口可以匿名访问，但登录后有更多功能）"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        
        if auth_header and auth_header.startswith('Bearer '):
            try:
                token = auth_header.split(' ', 1)[1]
                ok, user = AuthService.verify_access_token(token)
                if ok:
                    g.current_user = user
                else:
                    g.current_user = None
            except Exception:
                g.current_user = None
        else:
            g.current_user = None
        
        return f(*args, **kwargs)
    
    return wrapper