# app/services/spider/service.py
from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from .client import WeiboClient
from .parser import WeiboParser
from .publisher import NullPublisher
from .repository import MongoRepository

logger = logging.getLogger(__name__)


@dataclass
class SpiderStats:
    arctype_count: int = 0
    article_count: int = 0
    comment_count: int = 0
    failed_count: int = 0


class SpiderService:
    """
    爬虫服务 - 简化版(仅MongoDB存储)
    - client 拉数据
    - parser 解析
    - repo 写 mongo
    """

    def __init__(
        self,
        client: WeiboClient,
        parser: WeiboParser,
        repo: MongoRepository,
    ):
        self.client = client
        self.parser = parser
        self.repo = repo
        self.stats = SpiderStats()

        logger.info("SpiderService 初始化: 仅MongoDB存储模式")

        # 缓存
        self.article_seen: set[str] = set()
        self.arctypes: List[Dict[str, Any]] = []

    def crawl_arctype(self) -> Tuple[bool, List[Dict[str, Any]]]:
        """爬取文章类型"""
        url = "https://weibo.com/ajax/feed/allGroups"
        json_data = self.client.get_json(url, params={})
        if not json_data:
            self.stats.failed_count += 1
            logger.error("获取文章类型失败")
            return False, []

        arctypes = self.parser.parse_arctypes(json_data)
        if not arctypes:
            self.stats.failed_count += 1
            logger.warning("解析文章类型为空")
            return False, []

        out: List[Dict[str, Any]] = []
        for a in arctypes:
            # 仅存储到MongoDB
            ok_m = self.repo.upsert("arctype", a, id_field="gid", id_prefix="arctype")
            if ok_m:
                out.append(a)
                self.stats.arctype_count += 1
                logger.info(f"保存文章类型: {a['title']}")
            else:
                self.stats.failed_count += 1
                logger.error(f"保存文章类型失败: {a['title']}")

        self.arctypes = out
        logger.info(f"文章类型爬取完成,共 {len(out)} 个")
        return True, out

    def crawl_articles(self) -> Tuple[bool, List[Dict[str, Any]]]:
        """爬取文章"""
        if not self.arctypes:
            logger.warning("文章类型列表为空,跳过文章爬取")
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

            logger.info(f"正在爬取类型: {arctype['title']}")
            json_data = self.client.get_json(url, params=params)
            if not json_data:
                self.stats.failed_count += 1
                logger.error(f"获取文章失败: {arctype['title']}")
                continue

            articles = self.parser.parse_articles(json_data, arctype_title=arctype["title"])
            for art in articles:
                if art["id"] in self.article_seen:
                    continue
                self.article_seen.add(art["id"])

                # 仅存储到MongoDB
                ok_m = self.repo.upsert("article", art, id_field="id", id_prefix="article")

                if ok_m:
                    all_articles.append(art)
                    self.stats.article_count += 1
                else:
                    self.stats.failed_count += 1

            logger.info(f"类型 {arctype['title']} 爬取完成,获得 {len(articles)} 篇文章")

        logger.info(f"文章爬取完成,共 {len(all_articles)} 篇")
        return True, all_articles

    def crawl_comments(self, articles: List[Dict[str, Any]]) -> Tuple[bool, int]:
        """爬取评论"""
        if not articles:
            logger.warning("文章列表为空,跳过评论爬取")
            return False, 0

        url = "https://weibo.com/ajax/statuses/buildComments"
        total = 0

        for idx, art in enumerate(articles):
            time.sleep(1)
            params = {"id": art["id"], "is_show_bulletin": 2}
            
            logger.info(f"正在爬取评论 [{idx+1}/{len(articles)}]: {art['text_raw'][:30]}...")
            json_data = self.client.get_json(url, params=params)
            if not json_data:
                self.stats.failed_count += 1
                logger.error(f"获取评论失败: {art['id']}")
                continue

            comments = self.parser.parse_comments(
                json_data,
                article_id=art["id"],
                author_id=art.get("author_id", ""),
            )

            for c in comments:
                # 仅存储到MongoDB
                ok_m = self.repo.upsert("comment", c, id_field="id", id_prefix="comment")

                if ok_m:
                    total += 1
                    self.stats.comment_count += 1
                else:
                    self.stats.failed_count += 1

            if comments:
                logger.info(f"获得 {len(comments)} 条评论")

        logger.info(f"评论爬取完成,共 {total} 条")
        return True, total

    def run_spider(self, **kwargs) -> Dict[str, Any]:
        """执行爬虫任务"""
        start = time.time()
        
        logger.info(f"爬虫任务开始,参数: {kwargs}")
        
        try:
            # 爬取文章类型
            ok, _ = self.crawl_arctype()
            if not ok:
                return {"success": False, "message": "文章类型爬取失败"}

            # 爬取文章
            ok, articles = self.crawl_articles()
            if not ok:
                return {"success": False, "message": "文章爬取失败"}

            # 爬取评论
            self.crawl_comments(articles)

            elapsed = round(time.time() - start, 2)
            logger.info(f"爬虫任务完成,耗时 {elapsed}s")

            return {
                "success": True,
                "message": "爬虫任务完成",
                "params_received": kwargs,
                "data": {
                    "arctype_count": self.stats.arctype_count,
                    "article_count": self.stats.article_count,
                    "comment_count": self.stats.comment_count,
                    "failed_count": self.stats.failed_count,
                    "elapsed_time": elapsed,
                },
            }
        except Exception as e:
            logger.exception(f"爬虫任务异常: {e}")
            return {"success": False, "message": f"爬虫运行异常: {str(e)}"}
        finally:
            self.repo.close()

    def get_status(self) -> Dict[str, Any]:
        """获取爬虫状态"""
        return {
            "status": "ready",
            "stats": self.stats.__dict__,
            "cache": {
                "arctype_count": len(self.arctypes),
                "article_seen": len(self.article_seen),
            },
        }