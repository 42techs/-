# -*- coding: utf-8 -*-
# app/__init__.py
from flask import Flask, jsonify
from app.config import config
from app.extensions import init_extensions, db, close_mongo
import os


def create_app(config_name=None):
    """应用工厂函数"""
    
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    
    # 加载配置
    app.config.from_object(config[config_name])
    
    # 初始化扩展
    init_extensions(app)
    
    # 注册蓝图
    register_blueprints(app)
    
    # 注册错误处理器
    register_error_handlers(app)
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
    
    # 注册关闭钩子
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()
        close_mongo()
    
    return app


def register_blueprints(app):
    """注册所有蓝图"""
    
    from app.api.auth import auth_bp
    from app.api.spider import spider_bp
    from app.api.analysis import analysis_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(spider_bp, url_prefix='/api/spider')
    app.register_blueprint(analysis_bp, url_prefix='/api/analysis')
    
    # 健康检查接口
    @app.route('/api/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'message': '服务运行正常'
        })
    
    # 根路径
    @app.route('/')
    def index():
        return jsonify({
            'message': '微博数据分析系统 API',
            'version': '1.0.0',
            'endpoints': {
                'auth': '/api/auth',
                'spider': '/api/spider',
                'analysis': '/api/analysis',
                'health': '/api/health'
            }
        })


def register_error_handlers(app):
    """注册错误处理器"""
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'code': 404,
            'message': '请求的资源不存在'
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': '服务器内部错误'
        }), 500
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        app.logger.error(f'未处理的异常: {error}')
        return jsonify({
            'code': 500,
            'message': f'服务器错误: {str(error)}'
        }), 500