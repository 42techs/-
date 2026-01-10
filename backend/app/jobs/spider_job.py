import json
import sys
from datetime import datetime

from flask import current_app

from app import create_app, db
from app.models.spider_task import SpiderTask

from app.services.spider.client import WeiboClient, WeiboClientConfig
from app.services.spider.parser import WeiboParser
from app.services.spider.publisher import KafkaPublisher, KafkaPublisherConfig
from app.services.spider.repository import MongoRepository, MongoRepositoryConfig
from app.services.spider.service import SpiderService


def build_spider_service() -> SpiderService:
    cfg = current_app.config

    client = WeiboClient(
        WeiboClientConfig(
            cookie=cfg["WEIBO_COOKIE"],
            user_agent=cfg["WEIBO_USER_AGENT"],
        )
    )

    parser = WeiboParser()

    publisher = KafkaPublisher(
        KafkaPublisherConfig(
            bootstrap_servers=cfg["KAFKA_BOOTSTRAP"]
        )
    )

    repo = MongoRepository(
        MongoRepositoryConfig(
            mongo_uri=cfg["MONGO_URI"]
        )
    )

    return SpiderService(client, parser, publisher, repo)


def main(task_id: str):
    app = create_app()
    with app.app_context():
        task = SpiderTask.query.get(task_id)
        if not task:
            return

        task.status = "RUNNING"
        task.started_at = datetime.utcnow()
        db.session.commit()

        try:
            spider = build_spider_service()
            result = spider.run_spider()

            task.status = "SUCCESS" if result.get("success") else "FAILED"
            task.result_json = json.dumps(result, ensure_ascii=False)
            if not result.get("success"):
                task.error = result.get("message")
        except Exception as e:
            task.status = "FAILED"
            task.error = str(e)
        finally:
            task.finished_at = datetime.utcnow()
            db.session.commit()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("missing task_id")
    main(sys.argv[1])
