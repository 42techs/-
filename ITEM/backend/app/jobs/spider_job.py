import json
import sys
from datetime import datetime

from flask import current_app

from app import create_app, db
from app.models.spider_task import SpiderTask

from app.services.spider.client import WeiboClient, WeiboClientConfig
from app.services.spider.parser import WeiboParser
from app.services.spider.publisher import KafkaPublisher, KafkaPublisherConfig, NullPublisher
from app.services.spider.repository import MongoRepository, MongoRepositoryConfig
from app.services.spider.service import SpiderService


def build_spider_service() -> SpiderService:
    """构建爬虫服务实例 - 修复Kafka配置问题"""
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

    # Kafka发布器 - 根据配置决定是否启用
    if cfg.get('KAFKA_ENABLED', False):
        publisher = KafkaPublisher(
            KafkaPublisherConfig(
                bootstrap_servers=cfg["KAFKA_BOOTSTRAP"]
            )
        )
    else:
        # 使用空发布器(不发送到Kafka)
        publisher = NullPublisher()

    # MongoDB存储 - 添加db_name参数
    repo = MongoRepository(
        MongoRepositoryConfig(
            mongo_uri=cfg["MONGO_URI"],
            db_name=cfg["MONGO_DATABASE"]
        )
    )

    return SpiderService(client, parser, publisher, repo)


def main(task_id: str):
    """执行爬虫任务"""
    app = create_app()
    with app.app_context():
        task = SpiderTask.query.get(task_id)
        if not task:
            app.logger.error(f"任务不存在: {task_id}")
            return

        # 更新任务状态为运行中
        task.status = "RUNNING"
        task.started_at = datetime.utcnow()
        db.session.commit()

        try:
            app.logger.info(f"开始执行爬虫任务: {task_id}")
            
            # 构建并运行爬虫服务
            spider = build_spider_service()
            result = spider.run_spider()

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