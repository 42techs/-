# app/services/spider/client.py
from __future__ import annotations

import time
import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional

import requests

logger = logging.getLogger(__name__)


@dataclass
class WeiboClientConfig:
    timeout: int = 15
    max_retries: int = 3
    backoff_base_seconds: float = 1.0

    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"
    )
    cookie: str = ""  
    referer: str = "https://weibo.com/hot/weibo/102803"


class WeiboClient:
    """只负责 HTTP 请求与重试，不做解析、不做存储"""

    def __init__(self, config: WeiboClientConfig):
        self.config = config
        self.session = requests.Session()

    def _headers(self) -> Dict[str, str]:
        headers = {
            "user-agent": self.config.user_agent,
            "accept": "application/json, text/plain, */*",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
            "referer": self.config.referer,
            "x-requested-with": "XMLHttpRequest",
        }
        if self.config.cookie:
            headers["cookie"] = self.config.cookie
        return headers

    def get_json(self, url: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """带重试的 GET JSON"""
        params = params or {}
        for attempt in range(1, self.config.max_retries + 1):
            try:
                resp = self.session.get(
                    url,
                    headers=self._headers(),
                    params=params,
                    timeout=self.config.timeout,
                )

                if resp.status_code == 200:
                    return resp.json()

                # 403 常见于 cookie 失效/风控
                if resp.status_code == 403:
                    logger.warning("403 Forbidden：可能需要更新 Cookie / 被风控")
                    return None

                logger.warning("请求失败：%s %s", resp.status_code, resp.text[:200])

            except requests.exceptions.Timeout:
                logger.warning("请求超时，第 %s/%s 次", attempt, self.config.max_retries)

            except Exception as e:
                logger.exception("请求异常：%s", e)

            # 退避
            sleep_s = self.config.backoff_base_seconds * (2 ** (attempt - 1))
            time.sleep(sleep_s)

        return None
