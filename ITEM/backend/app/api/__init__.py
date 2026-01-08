from .auth import auth_bp
from .spider import spider_bp
from .analysis import analysis_bp

# 所有蓝图列表
all_blueprints = [auth_bp, spider_bp, analysis_bp]