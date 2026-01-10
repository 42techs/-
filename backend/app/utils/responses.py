# -*- coding: utf-8 -*-
# app/utils/responses.py
from flask import jsonify


def api_ok(data=None, message='操作成功', status_code=200):
    """成功响应"""
    return jsonify({
        'code': 0,
        'success': True,
        'message': message,
        'data': data if data is not None else {}
    }), status_code


def api_error(message, code=1, status_code=400, data=None):
    """错误响应"""
    return jsonify({
        'code': code,
        'success': False,
        'message': message,
        'data': data if data is not None else {}
    }), status_code