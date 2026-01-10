import os
from datetime import timedelta

from dotenv import load_dotenv
# 加载环境变量
load_dotenv()

class Config:
    """基础配置类"""
    
    # Flask基础配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    JSON_AS_ASCII = False  
    
    # MySQL配置（用户认证）
    MYSQL_HOST = os.getenv('MYSQL_HOST', '127.0.0.1')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', '3306'))
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'password')
    MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'weibo_auth')
    
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@"
        f"{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}?charset=utf8mb4"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    # MongoDB配置（爬虫数据）
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://127.0.0.1:27017')
    MONGO_DATABASE = os.getenv('MONGO_DATABASE', 'weibo_db')

    # JWT配置
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', '24')))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=int(os.getenv('JWT_REFRESH_TOKEN_EXPIRES', '7')))

    # Kafka配置：支持更多真值表示，保留向后兼容的变量名
    _KAFKA_ENABLED = os.getenv('KAFKA_ENABLED', 'true') or 'false'
    KAFKA_ENABLED = str(_KAFKA_ENABLED).strip().lower() in ('1', 'true', 'yes', 'on')
    KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
    # 兼容旧名称
    KAFKA_BOOTSTRAP = KAFKA_BOOTSTRAP_SERVERS
    
    # 微博爬虫配置
    WEIBO_COOKIE = os.getenv('WEIBO_COOKIE', '')
    WEIBO_USER_AGENT = os.getenv(
        'WEIBO_USER_AGENT',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    )
    
    # CORS配置：解析逗号分隔并过滤空项
    _CORS_RAW = os.getenv('CORS_ORIGINS', '*')
    if isinstance(_CORS_RAW, str):
        CORS_ORIGINS = [o.strip() for o in _CORS_RAW.split(',') if o.strip()]
        if not CORS_ORIGINS:
            CORS_ORIGINS = ['*']
    else:
        CORS_ORIGINS = ['*']
    
    # 日志配置
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/app.log')


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    SQLALCHEMY_ECHO = False


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    SQLALCHEMY_ECHO = False


class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


# 配置字典
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}