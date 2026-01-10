from flask import Blueprint, jsonify, current_app, request, g
from app.utils.jwt_auth import token_required
from app.utils.responses import api_ok, api_error
from app.models.spider_task import SpiderTask
from app import db
import uuid
from datetime import datetime
import subprocess
import sys
import os

from app.services.spider.client import WeiboClient, WeiboClientConfig
from app.services.spider.parser import WeiboParser
from app.services.spider.publisher import KafkaPublisher, KafkaPublisherConfig
from app.services.spider.repository import MongoRepository, MongoRepositoryConfig
from app.services.spider.service import SpiderService

spider_bp = Blueprint('spider', __name__)


def build_spider_service() -> SpiderService:
    """构建爬虫服务实例"""
    cfg = current_app.config
    
    # 客户端配置
    client = WeiboClient(
        WeiboClientConfig(
            cookie=cfg['WEIBO_COOKIE'],
            user_agent=cfg['WEIBO_USER_AGENT'],
        )
    )
    
    # 解析器
    parser = WeiboParser()
    
    # Kafka发布器（如果启用）
    publisher = None
    if cfg.get('KAFKA_ENABLED', False):
        publisher = KafkaPublisher(
            KafkaPublisherConfig(
                bootstrap_servers=cfg['KAFKA_BOOTSTRAP']
            )
        )
    else:
        # 使用空发布器（不发送到Kafka）
        from app.services.spider.publisher import NullPublisher
        publisher = NullPublisher()
    
    # MongoDB存储
    repo = MongoRepository(
        MongoRepositoryConfig(
            mongo_uri=cfg['MONGO_URI'],
            db_name=cfg['MONGO_DATABASE']
        )
    )
    
    return SpiderService(client, parser, publisher, repo)


@spider_bp.route('/start', methods=['POST'])
@token_required
def start_spider():
    """启动爬虫任务"""
    
    # 检查Cookie配置
    if not current_app.config.get('WEIBO_COOKIE'):
        return api_error('未配置微博Cookie，无法启动爬虫', status_code=400)
    
    # 获取当前用户ID
    user_id = g.current_user.id
    current_app.logger.info(f'用户 {user_id} 请求启动爬虫任务')
    
    # 检查当前用户是否有正在运行的任务
    running_task = SpiderTask.query.filter_by(
        user_id=user_id,
        status='RUNNING'
    ).first()
    
    if running_task:
        return api_error(
            '您已有爬虫任务正在运行',
            data={'task_id': running_task.id}
        )
    
    try:
        # 创建任务记录
        task_id = str(uuid.uuid4())
        task = SpiderTask(
            id=task_id,
            user_id=user_id,  # 设置用户ID
            status='PENDING',
            created_at=datetime.utcnow()
        )
        db.session.add(task)
        db.session.commit()
        
        current_app.logger.info(f'任务创建成功: {task_id}, 用户: {user_id}')
        
        # 异步执行爬虫任务（使用subprocess）
        script_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'app', 'jobs', 'spider_job.py'
        )
        
        # 后台执行：使用模块方式运行并把工作目录设为项目根（确保可以导入 `app` 包）
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        subprocess.Popen(
            [sys.executable, '-m', 'app.jobs.spider_job', task_id],
            cwd=project_root,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        
        current_app.logger.info(f'后台进程已启动: {task_id}')
        
        return api_ok(
            data={
                'task_id': task_id,
                'status': 'PENDING',
                'message': '爬虫任务已启动'
            },
            message='爬虫任务创建成功',
            status_code=201
        )
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'启动爬虫失败: {e}', exc_info=True)
        return api_error(f'启动爬虫失败: {str(e)}', status_code=500)


@spider_bp.route('/tasks', methods=['GET'])
@token_required
def get_tasks():
    """获取任务列表（仅当前用户）"""
    
    try:
        user_id = g.current_user.id
        
        # 分页参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status', None, type=str)
        
        # 构建查询 - 只查询当前用户的任务
        query = SpiderTask.query.filter_by(user_id=user_id)
        if status:
            query = query.filter_by(status=status)
        
        # 分页查询
        pagination = query.order_by(SpiderTask.created_at.desc()).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        tasks = [{
            'id': task.id,
            'user_id': task.user_id,
            'status': task.status,
            'created_at': task.created_at.isoformat() if task.created_at else None,
            'started_at': task.started_at.isoformat() if task.started_at else None,
            'finished_at': task.finished_at.isoformat() if task.finished_at else None,
            'error': task.error
        } for task in pagination.items]
        
        return api_ok(data={
            'tasks': tasks,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        })
        
    except Exception as e:
        current_app.logger.error(f'获取任务列表失败: {e}')
        return api_error(f'获取任务列表失败: {str(e)}', status_code=500)


@spider_bp.route('/tasks/<task_id>', methods=['GET'])
@token_required
def get_task(task_id):
    """获取任务详情（仅限自己的任务）"""
    
    try:
        user_id = g.current_user.id
        
        task = SpiderTask.query.filter_by(id=task_id, user_id=user_id).first()
        if not task:
            return api_error('任务不存在或无权访问', status_code=404)
        
        import json
        result_data = None
        if task.result_json:
            try:
                result_data = json.loads(task.result_json)
            except:
                result_data = task.result_json
        
        return api_ok(data={
            'id': task.id,
            'user_id': task.user_id,
            'status': task.status,
            'created_at': task.created_at.isoformat() if task.created_at else None,
            'started_at': task.started_at.isoformat() if task.started_at else None,
            'finished_at': task.finished_at.isoformat() if task.finished_at else None,
            'result': result_data,
            'error': task.error
        })
        
    except Exception as e:
        current_app.logger.error(f'获取任务详情失败: {e}')
        return api_error(f'获取任务详情失败: {str(e)}', status_code=500)


@spider_bp.route('/status', methods=['GET'])
@token_required
def get_status():
    """获取爬虫状态（当前用户的统计）"""
    
    try:
        user_id = g.current_user.id
        
        # 统计任务状态 - 仅当前用户
        total = SpiderTask.query.filter_by(user_id=user_id).count()
        running = SpiderTask.query.filter_by(user_id=user_id, status='RUNNING').count()
        success = SpiderTask.query.filter_by(user_id=user_id, status='SUCCESS').count()
        failed = SpiderTask.query.filter_by(user_id=user_id, status='FAILED').count()
        pending = SpiderTask.query.filter_by(user_id=user_id, status='PENDING').count()
        
        # 最近一次任务
        last_task = SpiderTask.query.filter_by(user_id=user_id).order_by(
            SpiderTask.created_at.desc()
        ).first()
        
        last_task_info = None
        if last_task:
            last_task_info = {
                'id': last_task.id,
                'status': last_task.status,
                'created_at': last_task.created_at.isoformat() if last_task.created_at else None,
                'finished_at': last_task.finished_at.isoformat() if last_task.finished_at else None
            }
        
        return api_ok(data={
            'statistics': {
                'total': total,
                'running': running,
                'success': success,
                'failed': failed,
                'pending': pending
            },
            'last_task': last_task_info,
            'is_running': running > 0,
            'config': {
                'cookie_configured': bool(current_app.config.get('WEIBO_COOKIE')),
                'kafka_enabled': current_app.config.get('KAFKA_ENABLED', False)
            }
        })
        
    except Exception as e:
        current_app.logger.error(f'获取爬虫状态失败: {e}')
        return api_error(f'获取爬虫状态失败: {str(e)}', status_code=500)


@spider_bp.route('/test', methods=['GET'])
@token_required
def test_spider():
    """测试爬虫服务（不实际爬取数据）"""
    
    try:
        # 检查配置
        checks = {
            'cookie_configured': bool(current_app.config.get('WEIBO_COOKIE')),
            'mongo_connected': False,
            'kafka_enabled': current_app.config.get('KAFKA_ENABLED', False),
            'kafka_connected': False
        }
        
        # 测试MongoDB连接
        try:
            from app.extensions import get_mongo_db
            mongo_db = get_mongo_db()
            if mongo_db:
                mongo_db.list_collection_names()
                checks['mongo_connected'] = True
        except Exception as e:
            current_app.logger.error(f'MongoDB连接测试失败: {e}')
        
        # 测试Kafka连接
        if checks['kafka_enabled']:
            try:
                publisher = KafkaPublisher(
                    KafkaPublisherConfig(
                        bootstrap_servers=current_app.config['KAFKA_BOOTSTRAP']
                    )
                )
                try:
                    producer = getattr(publisher, 'producer', None)
                    if producer and getattr(producer, 'bootstrap_connected', lambda: False)():
                        checks['kafka_connected'] = True
                    else:
                        checks['kafka_connected'] = False
                except Exception as e:
                    current_app.logger.error(f'Kafka bootstrap 检查失败: {e}')
                    checks['kafka_connected'] = False
                finally:
                    publisher.close()
            except Exception as e:
                current_app.logger.error(f'Kafka连接测试失败: {e}')
        
        all_ok = all([
            checks['cookie_configured'],
            checks['mongo_connected']
        ])
        
        return api_ok(data={
            'checks': checks,
            'ready': all_ok,
            'message': '所有检查通过' if all_ok else '部分检查未通过'
        })
        
    except Exception as e:
        current_app.logger.error(f'测试爬虫服务失败: {e}')
        return api_error(f'测试失败: {str(e)}', status_code=500)