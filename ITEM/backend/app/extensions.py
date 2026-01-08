from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from pymongo import MongoClient
import logging
from logging.handlers import RotatingFileHandler
import os

# SQLAlchemy实例（MySQL）
db = SQLAlchemy()

# CORS实例
cors = CORS()

# MongoDB连接
mongo_client = None
mongo_db = None


def init_extensions(app):
    """初始化所有扩展"""
    
    # 初始化SQLAlchemy
    db.init_app(app)
    
    # 初始化CORS
    cors.init_app(app, resources={
        r"/api/*": {
            "origins": app.config['CORS_ORIGINS'],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "expose_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })
    
    # 初始化MongoDB
    init_mongo(app)
    
    # 初始化日志
    init_logging(app)


def init_mongo(app):
    """初始化MongoDB连接"""
    global mongo_client, mongo_db
    
    try:
        mongo_client = MongoClient(
            app.config['MONGO_URI'],
            serverSelectionTimeoutMS=5000
        )
        # 测试连接
        mongo_client.admin.command('ping')
        mongo_db = mongo_client[app.config['MONGO_DATABASE']]
        app.logger.info(f"MongoDB连接成功: {app.config['MONGO_URI']}")
    except Exception as e:
        app.logger.error(f"MongoDB连接失败: {e}")
        mongo_client = None
        mongo_db = None


def init_logging(app):
    """初始化日志配置"""
    
    if not app.debug:
        # 创建日志目录
        log_dir = os.path.dirname(app.config['LOG_FILE'])
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # 文件日志处理器
        file_handler = RotatingFileHandler(
            app.config['LOG_FILE'],
            maxBytes=10240000,  # 10MB
            backupCount=10,
            encoding='utf-8'
        )
        file_handler.setFormatter(logging.Formatter(
            '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
        ))
        file_handler.setLevel(getattr(logging, app.config['LOG_LEVEL']))
        
        app.logger.addHandler(file_handler)
        app.logger.setLevel(getattr(logging, app.config['LOG_LEVEL']))
        app.logger.info('应用启动')


def get_mongo_db():
    """获取MongoDB数据库实例"""
    return mongo_db


def close_mongo():
    """关闭MongoDB连接"""
    global mongo_client
    if mongo_client:
        mongo_client.close()