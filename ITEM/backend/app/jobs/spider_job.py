# app/jobs/spider_job.py
import json
import sys
from datetime import datetime

from flask import current_app

from app import create_app, db
from app.models.spider_task import SpiderTask

from app.services.spider.client import WeiboClient, WeiboClientConfig
from app.services.spider.parser import WeiboParser
from app.services.spider.repository import MongoRepository, MongoRepositoryConfig
from app.services.spider.service import SpiderService


def build_spider_service() -> SpiderService:
    """构建爬虫服务实例 - 简化版(仅MongoDB)"""
    cfg = current_app.config

    # 客户端配置
    client = WeiboClient(
        WeiboClientConfig(
            cookie=cfg["WEIBO_COOKIE"],
            user_agent=cfg["WEIBO_USER_AGENT"],
        )
    )

    # 解析器
    parser = WeiboParser()

    # MongoDB存储
    current_app.logger.info(f"初始化MongoDB: {cfg['MONGO_URI']}/{cfg['MONGO_DATABASE']}")
    repo = MongoRepository(
        MongoRepositoryConfig(
            mongo_uri=cfg["MONGO_URI"],
            db_name=cfg["MONGO_DATABASE"]
        )
    )

    return SpiderService(client, parser, repo)


def main(task_id: str):
    """执行爬虫任务"""
    app = create_app()
    with app.app_context():
        task = SpiderTask.query.get(task_id)
        if not task:
            app.logger.error(f"任务不存在: {task_id}")
            return

        # 更新任务状态
        task.status = "RUNNING"
        task.started_at = datetime.utcnow()
        db.session.commit()

        try:
            app.logger.info(f"开始执行爬虫任务: {task_id}")
            
            # 读取任务参数
            spider_params = {}
            if task.params_json:
                try:
                    spider_params = json.loads(task.params_json)
                    app.logger.info(f"爬虫参数: {spider_params}")
                except json.JSONDecodeError as e:
                    app.logger.error(f"参数解析失败: {e}")
            
            # 构建并运行爬虫服务
            spider = build_spider_service()
            result = spider.run_spider(**spider_params)

            # 更新任务结果
            task.status = "SUCCESS" if result.get("success") else "FAILED"
            task.result_json = json.dumps(result, ensure_ascii=False)
            
            if not result.get("success"):
                task.error = result.get("message")
            
            app.logger.info(f"爬虫任务完成: {task_id}, 状态: {task.status}")
            
        except Exception as e:
            app.logger.exception(f"爬虫任务执行失败: {task_id}, 错误: {e}")
            task.status = "FAILED"
            task.error = str(e)
            
        finally:
            task.finished_at = datetime.utcnow()
            db.session.commit()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("缺少参数: task_id")
    
    task_id = sys.argv[1]
    main(task_id)