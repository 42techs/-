# app/services/spider/service.py
from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from .client import WeiboClient
from .parser import WeiboParser
from .publisher import KafkaPublisher
from .repository import MongoRepository

logger = logging.getLogger(__name__)


@dataclass
class SpiderTopics:
    arctype: str = "weibo_arctype"
    article: str = "weibo_article"
    comment: str = "weibo_comment"


@dataclass
class SpiderStats:
    arctype_count: int = 0
    article_count: int = 0
    comment_count: int = 0
    failed_count: int = 0


class SpiderService:
    """
    只负责编排：
    - client 拉数据
    - parser 解析
    - publisher 发 kafka
    - repo 写 mongo
    """

    def __init__(
        self,
        client: WeiboClient,
        parser: WeiboParser,
        publisher: KafkaPublisher,
        repo: MongoRepository,
        topics: SpiderTopics = SpiderTopics(),
    ):
        self.client = client
        self.parser = parser
        self.publisher = publisher
        self.repo = repo
        self.topics = topics
        self.stats = SpiderStats()

        # 缓存：建议改成外部存储（Redis/Mongo），这里先保留“任务内缓存”
        self.article_seen: set[str] = set()
        self.arctypes: List[Dict[str, Any]] = []

    def crawl_arctype(self) -> Tuple[bool, List[Dict[str, Any]]]:
        url = "https://weibo.com/ajax/feed/allGroups"
        json_data = self.client.get_json(url, params={})
        if not json_data:
            self.stats.failed_count += 1
            return False, []

        arctypes = self.parser.parse_arctypes(json_data)
        if not arctypes:
            self.stats.failed_count += 1
            return False, []

        out: List[Dict[str, Any]] = []
        for a in arctypes:
            ok_k = self.publisher.send(self.topics.arctype, key=a["gid"], value=a)
            ok_m = self.repo.upsert("arctype", a, id_field="gid", id_prefix="arctype")
            if ok_k and ok_m:
                out.append(a)
                self.stats.arctype_count += 1
            else:
                self.stats.failed_count += 1

        self.arctypes = out
        return True, out

    def crawl_articles(self) -> Tuple[bool, List[Dict[str, Any]]]:
        if not self.arctypes:
            return False, []

        url = "https://weibo.com/ajax/feed/hottimeline"
        all_articles: List[Dict[str, Any]] = []

        for arctype in self.arctypes:
            time.sleep(1)
            params = {
                "group_id": arctype["gid"],
                "containerid": arctype["containerid"],
                "extparam": "discover|new_feed",
            }

            json_data = self.client.get_json(url, params=params)
            if not json_data:
                self.stats.failed_count += 1
                continue

            articles = self.parser.parse_articles(json_data, arctype_title=arctype["title"])
            for art in articles:
                if art["id"] in self.article_seen:
                    continue
                self.article_seen.add(art["id"])

                # 分区：可选（拿不到就交给 Kafka）
                partition = None
                if art.get("author_id"):
                    partition = self.publisher.partition_for_key(self.topics.article, art["author_id"])

                ok_k = self.publisher.send(self.topics.article, key=art["id"], value=art, partition=partition)
                ok_m = self.repo.upsert("article", art, id_field="id", id_prefix="article")

                if ok_k and ok_m:
                    all_articles.append(art)
                    self.stats.article_count += 1
                else:
                    self.stats.failed_count += 1

        return True, all_articles

    def crawl_comments(self, articles: List[Dict[str, Any]]) -> Tuple[bool, int]:
        if not articles:
            return False, 0

        url = "https://weibo.com/ajax/statuses/buildComments"
        total = 0

        for art in articles:
            time.sleep(1)
            params = {"id": art["id"], "is_show_bulletin": 2}
            json_data = self.client.get_json(url, params=params)
            if not json_data:
                self.stats.failed_count += 1
                continue

            comments = self.parser.parse_comments(
                json_data,
                article_id=art["id"],
                author_id=art.get("author_id", ""),
            )

            for c in comments:
                partition = None
                if c.get("author_id"):
                    partition = self.publisher.partition_for_key(self.topics.comment, c["author_id"])

                ok_k = self.publisher.send(self.topics.comment, key=c["id"], value=c, partition=partition)
                ok_m = self.repo.upsert("comment", c, id_field="id", id_prefix="comment")

                if ok_k and ok_m:
                    total += 1
                    self.stats.comment_count += 1
                else:
                    self.stats.failed_count += 1

        return True, total

    def run_spider(self) -> Dict[str, Any]:
        start = time.time()
        try:
            ok, _ = self.crawl_arctype()
            if not ok:
                return {"success": False, "message": "文章类型爬取失败"}

            ok, articles = self.crawl_articles()
            if not ok:
                return {"success": False, "message": "文章爬取失败"}

            self.crawl_comments(articles)

            self.publisher.flush()

            return {
                "success": True,
                "message": "爬虫任务完成",
                "data": {
                    "arctype_count": self.stats.arctype_count,
                    "article_count": self.stats.article_count,
                    "comment_count": self.stats.comment_count,
                    "failed_count": self.stats.failed_count,
                    "elapsed_time": round(time.time() - start, 2),
                },
            }
        except Exception as e:
            logger.exception("run_spider error: %s", e)
            return {"success": False, "message": f"爬虫运行异常: {str(e)}"}
        finally:
            # 资源释放
            self.publisher.close()
            self.repo.close()

    def get_status(self) -> Dict[str, Any]:
        return {
            "status": "ready",
            "stats": self.stats.__dict__,
            "cache": {
                "arctype_count": len(self.arctypes),
                "article_seen": len(self.article_seen),
            },
        }
