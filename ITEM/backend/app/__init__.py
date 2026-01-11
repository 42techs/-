from flask import Flask, jsonify, g
from app.config import config
from app.extensions import init_extensions, db, close_mongo
import os


def create_app(config_name=None):
    """应用工厂函数 - 优化版本"""
    
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    
    # 加载配置
    app.config.from_object(config[config_name])
    
    # 配置热重载设置 (解决Windows套接字错误的关键)
    configure_hot_reload(app, config_name)
    
    # 初始化扩展
    init_extensions(app)
    
    # 注册蓝图
    register_blueprints(app)
    
    # 注册错误处理器
    register_error_handlers(app)
    
    # 注册上下文处理器
    register_context_processors(app)
    
    # 初始化数据库 (可选跳过，用于测试)
    initialize_database(app)
    
    # 注册关闭钩子
    register_teardown_handlers(app)
    
    return app


def configure_hot_reload(app, config_name):
    """配置热重载相关设置 - 专门解决Windows套接字错误"""
    is_development = config_name == 'development'
    
    # 在Windows开发环境下调整热重载配置
    if is_development and os.name == 'nt':  # nt 表示 Windows 系统
        app.config['TEMPLATES_AUTO_RELOAD'] = True
        # 建议在Windows开发环境下禁用reloader或设置为False
        # 这能有效解决 [WinError 10038] 套接字错误
        app.config['USE_RELOADER'] = os.getenv('USE_RELOADER', 'false').lower() == 'true'
        
    app.logger.info(f"运行环境: {config_name}, 热重载: {app.config.get('USE_RELOADER', '未设置')}")


def register_blueprints(app):
    """注册所有蓝图"""
    
    from app.api.auth import auth_bp
    from app.api.spider import spider_bp
    from app.api.analysis import analysis_bp
    
    # 注册API蓝图
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(spider_bp, url_prefix='/api/spider')
    app.register_blueprint(analysis_bp, url_prefix='/api/analysis')
    
    # 健康检查接口
    @app.route('/api/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'message': '服务运行正常',
            'environment': app.config.get('ENV', 'development')
        })
    
    # 根路径 - API信息
    @app.route('/')
    def index():
        return jsonify({
            'message': '微博数据分析系统 API',
            'version': '1.0.0',
            'environment': app.config.get('ENV', 'development'),
            'endpoints': {
                'auth': '/api/auth',
                'spider': '/api/spider', 
                'analysis': '/api/analysis',
                'health': '/api/health'
            }
        })


def register_error_handlers(app):
    """注册错误处理器"""
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'code': 400,
            'success': False,
            'message': '请求参数错误'
        }), 400
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'code': 404,
            'success': False,
            'message': '请求的资源不存在'
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        # 确保数据库会话回滚
        if hasattr(g, 'db_session'):
            g.db_session.rollback()
        return jsonify({
            'code': 500,
            'success': False, 
            'message': '服务器内部错误'
        }), 500


def register_context_processors(app):
    """注册上下文处理器"""
    
    @app.before_request
    def before_request():
        """在每个请求开始前执行"""
        # 可以在这里添加请求前的初始化逻辑
        g.db_session = db.session
        
    @app.context_processor
    def inject_environment():
        """向模板注入环境变量"""
        return {
            'environment': app.config.get('ENV', 'development')
        }


def initialize_database(app):
    """初始化数据库表"""
    if os.getenv('SKIP_DB_INIT'):
        app.logger.info("跳过数据库初始化")
        return
        
    try:
        with app.app_context():
            # 创建所有表
            db.create_all()
            app.logger.info("数据库表初始化成功")
            
            # 可以在这里添加初始数据
            if os.getenv('INIT_SAMPLE_DATA'):
                init_sample_data(app)
                
    except Exception as e:
        app.logger.warning(f"数据库初始化警告: {e}")
        # 不要在这里抛出异常，允许应用继续启动


def register_teardown_handlers(app):
    """注册资源清理处理器"""
    
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        """在应用上下文结束时清理资源"""
        try:
            # 清理SQLAlchemy会话
            if hasattr(g, 'db_session'):
                g.db_session.remove()
                
            # 关闭MongoDB连接
            close_mongo()
            
        except Exception as e:
            app.logger.error(f"资源清理错误: {e}")


def init_sample_data(app):
    """初始化示例数据（可选）"""
    try:
        from app.models.user import User
        
        # 检查是否已存在示例用户
        if not User.query.filter_by(username='admin').first():
            admin_user = User(
                username='admin',
                email='admin@weiboanalysis.com'
            )
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            db.session.commit()
            app.logger.info("示例用户创建成功")
            
    except Exception as e:
        app.logger.error(f"初始化示例数据失败: {e}")
        db.session.rollback()


# 主程序入口
if __name__ == '__main__':
    app = create_app()
    
    # 获取配置
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    
    # Windows环境下的特殊处理
    use_reloader = debug
    if os.name == 'nt' and debug:
        use_reloader = os.getenv('USE_RELOADER', 'false').lower() == 'true'
    
    print(f"""
    ╔══════════════════════════════════════════╗
    ║        微博数据分析系统 API Server       ║  
    ╠══════════════════════════════════════════╣
    ║   地址: http://{host}:{port}           ║
    ║   环境: {os.getenv('FLASK_ENV', 'development')}                    ║
    ║   调试模式: {'开启' if debug else '关闭'}                     ║
    ║   热重载: {'开启' if use_reloader else '关闭'}                    ║
    ╚══════════════════════════════════════════╝
    """)
    
    # 启动服务器
    app.run(
        host=host,
        port=port, 
        debug=debug,
        use_reloader=use_reloader,  # 关键配置
        threaded=True
    )