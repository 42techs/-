# app/services/spider/parser.py
from __future__ import annotations

import re
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class ParsedArctype:
    title: str
    gid: str
    containerid: str
    crawl_time: str


@dataclass
class ParsedArticle:
    id: str
    text_raw: str
    reposts_count: int
    comments_count: int
    attitudes_count: int
    region_name: str
    created_at: str
    article_type: str
    article_url: str
    author_id: str
    author_name: str
    crawl_time: str


@dataclass
class ParsedComment:
    id: str
    text_raw: str
    created_at: str
    source: str
    like_counts: int
    article_id: str
    user_id: str
    user_name: str
    gender: str
    crawl_time: str


class WeiboParser:
    """只负责把 JSON 转成结构化 dict，不做网络、不做存储"""

    TAG_RE = re.compile(r"<[^>]+>")
    URL_RE = re.compile(r"https?://\S+")
    SPACE_RE = re.compile(r"\s+")

    @staticmethod
    def clean_text(text: Optional[str]) -> str:
        if not text:
            return ""
        text = WeiboParser.TAG_RE.sub("", text)
        text = WeiboParser.URL_RE.sub("", text)
        text = WeiboParser.SPACE_RE.sub(" ", text).strip()
        return text

    @staticmethod
    def _now_str() -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def parse_arctypes(json_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        兼容你原来逻辑：从 allGroups -> groups[3]/groups[4] 拿 group
        注意：微博返回结构可能变，必要时这里要做容错
        """
        groups = json_data.get("groups") or []
        if len(groups) <= 4:
            return []

        # 原实现用了 numpy append，这里用纯 Python
        g1 = (groups[3] or {}).get("group") or []
        g2 = (groups[4] or {}).get("group") or []
        merged = list(g1) + list(g2)

        out: List[Dict[str, Any]] = []
        for it in merged:
            out.append(
                {
                    "title": it.get("title", ""),
                    "gid": str(it.get("gid", "")),
                    "containerid": str(it.get("containerid", "")),
                    "crawl_time": WeiboParser._now_str(),
                }
            )
        return out

    @staticmethod
    def parse_articles(json_data: Dict[str, Any], arctype_title: str) -> List[Dict[str, Any]]:
        statuses = json_data.get("statuses") or []
        out: List[Dict[str, Any]] = []

        for article in statuses:
            try:
                article_id = str(article["id"])
                user = article.get("user") or {}
                user_id = str(user.get("id", ""))
                mblogid = article.get("mblogid", "")

                # created_at: "Tue Nov 12 16:05:52 +0800 2024"
                created_at_raw = article.get("created_at")
                created_at = created_at_raw
                if created_at_raw:
                    try:
                        created_at = datetime.strptime(created_at_raw, "%a %b %d %H:%M:%S %z %Y").strftime(
                            "%Y-%m-%d %H:%M:%S"
                        )
                    except Exception:
                        # 保底：原值输出
                        created_at = created_at_raw

                out.append(
                    {
                        "id": article_id,
                        "text_raw": WeiboParser.clean_text(article.get("text_raw", "")),
                        "reposts_count": int(article.get("reposts_count", 0) or 0),
                        "comments_count": int(article.get("comments_count", 0) or 0),
                        "attitudes_count": int(article.get("attitudes_count", 0) or 0),
                        "region_name": (article.get("region_name", "") or "").replace("发布于", "").strip(),
                        "created_at": created_at,
                        "article_type": arctype_title,
                        "article_url": f"https://weibo.com/{user_id}/{mblogid}",
                        "author_id": user_id,
                        "author_name": user.get("screen_name", ""),
                        "crawl_time": WeiboParser._now_str(),
                    }
                )
            except Exception as e:
                logger.debug("parse_articles skip: %s", e)
                continue

        return out

    @staticmethod
    def parse_comments(json_data: Dict[str, Any], article_id: str, author_id: str) -> List[Dict[str, Any]]:
        data_list = json_data.get("data") or []
        out: List[Dict[str, Any]] = []

        for comment in data_list:
            try:
                c_id = str(comment["id"])
                user = comment.get("user") or {}
                gender = "男" if user.get("gender") == "m" else "女"

                created_at_raw = comment.get("created_at")
                created_at = created_at_raw
                if created_at_raw:
                    try:
                        created_at = datetime.strptime(created_at_raw, "%a %b %d %H:%M:%S %z %Y").strftime(
                            "%Y-%m-%d %H:%M:%S"
                        )
                    except Exception:
                        created_at = created_at_raw

                out.append(
                    {
                        "id": c_id,
                        "text_raw": WeiboParser.clean_text(comment.get("text_raw", "")),
                        "created_at": created_at,
                        "source": (comment.get("source", "") or "").replace("来自", "").strip(),
                        "like_counts": int(comment.get("like_counts", 0) or 0),
                        "article_id": article_id,
                        "user_id": str(user.get("id", "")),
                        "user_name": user.get("screen_name", ""),
                        "gender": gender,
                        "crawl_time": WeiboParser._now_str(),
                        # author_id 不作为字段也行，但你分区时可能用得到
                        "author_id": author_id,
                    }
                )
            except Exception as e:
                logger.debug("parse_comments skip: %s", e)
                continue

        return out
