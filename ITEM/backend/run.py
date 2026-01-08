import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()




from app import create_app

# 创建应用实例
app = create_app()

if __name__ == '__main__':
    # 获取配置
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"""
    ╔══════════════════════════════════════════╗
    ║   微博数据分析系统 API Server          ║
    ╠══════════════════════════════════════════╣
    ║   地址: http://{host}:{port}           ║
    ║   环境: {os.getenv('FLASK_ENV', 'development')}                    ║
    ║   调试模式: {'开启' if debug else '关闭'}                     ║
    ╚══════════════════════════════════════════╝
    """)
    
    # 启动服务器
    app.run(
        host=host,
        port=port,
        debug=debug,
        threaded=True
    )