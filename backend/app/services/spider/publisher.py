# -*- coding: utf-8 -*-
# app/services/spider/publisher.py
from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional

from kafka import KafkaProducer
from kafka.errors import KafkaError

logger = logging.getLogger(__name__)


@dataclass
class KafkaPublisherConfig:
    bootstrap_servers: str = "localhost:9092"
    acks: str = "all"
    retries: int = 5
    retry_backoff_ms: int = 300
    compression_type: str = "gzip"
    request_timeout_ms: int = 30000


class KafkaPublisher:
    """只负责把 dict 发到 Kafka"""

    def __init__(self, config: KafkaPublisherConfig):
        self.config = config
        self.producer = KafkaProducer(
            bootstrap_servers=config.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode("utf-8"),
            key_serializer=lambda k: k.encode("utf-8") if k else None,
            acks=config.acks,
            retries=config.retries,
            retry_backoff_ms=config.retry_backoff_ms,
            compression_type=config.compression_type,
            request_timeout_ms=config.request_timeout_ms,
        )

    def send(self, topic: str, key: Optional[str], value: Dict[str, Any], partition: Optional[int] = None) -> bool:
        try:
            future = self.producer.send(topic, key=key, value=value, partition=partition)
            meta = future.get(timeout=10)
            logger.debug("Kafka send ok topic=%s partition=%s", topic, meta.partition)
            return True
        except KafkaError as e:
            logger.error("Kafka send failed topic=%s err=%s", topic, e)
            return False

    def flush(self):
        self.producer.flush()

    def close(self):
        try:
            self.producer.close()
        except Exception:
            pass

    def partition_for_key(self, topic: str, key: str) -> Optional[int]:
        """
        可选：根据 Kafka 实际分区数算 partition，避免你原来写死 3 的问题。
        如果拿不到 partitions，返回 None（让 Kafka 自己分区）。
        """
        try:
            parts = self.producer.partitions_for(topic)
            if not parts:
                return None
            num = len(parts)
            # 简单 hash
            return (hash(key) & 0x7fffffff) % num
        except Exception:
            return None


class NullPublisher:
    """空发布器（用于不使用Kafka的场景）"""
    
    def send(self, topic: str, key: Optional[str], value: Dict[str, Any], partition: Optional[int] = None) -> bool:
        """不实际发送，直接返回成功"""
        logger.debug("NullPublisher: skip sending to topic=%s", topic)
        return True
    
    def flush(self):
        """空操作"""
        pass
    
    def close(self):
        """空操作"""
        pass
    
    def partition_for_key(self, topic: str, key: str) -> Optional[int]:
        """返回None"""
        return None