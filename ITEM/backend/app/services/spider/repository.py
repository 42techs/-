# app/services/spider/repository.py
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional

from pymongo import MongoClient, errors as pymongo_errors

logger = logging.getLogger(__name__)


@dataclass
class MongoRepositoryConfig:
    mongo_uri: str = "mongodb://localhost:27017"
    db_name: str = "weibo_db"
    server_selection_timeout_ms: int = 5000


class MongoRepository:
    """只负责 Mongo 存储（upsert）"""

    def __init__(self, config: MongoRepositoryConfig):
        self.config = config
        self.client = MongoClient(
            config.mongo_uri,
            serverSelectionTimeoutMS=config.server_selection_timeout_ms,
        )
        # ping 失败就抛出，调用方决定是否中断任务
        self.client.admin.command("ping")
        self.db = self.client[config.db_name]

    def upsert(self, collection: str, doc: Dict[str, Any], id_field: str = "id", id_prefix: Optional[str] = None) -> bool:
        """
        用 replace_one + upsert=True，和你原来行为一致，但更安全：
        - _id = f"{prefix}:{id}" 避免不同集合/类型互相覆盖
        """
        try:
            to_save = dict(doc)
            _id = to_save.get(id_field)
            if _id is not None:
                _id = str(_id)
                if id_prefix:
                    _id = f"{id_prefix}:{_id}"
                to_save["_id"] = _id

            coll = self.db[collection]
            coll.replace_one({"_id": to_save.get("_id")}, to_save, upsert=True)
            return True
        except pymongo_errors.PyMongoError as e:
            logger.error("Mongo upsert failed [%s]: %s", collection, e)
            return False

    def close(self):
        try:
            self.client.close()
        except Exception:
            pass
