"""基础分析器 - 所有分析器的父类"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class BaseAnalyzer(ABC):
    """抽象基础分析器"""
    
    def __init__(self):
        self.logger = logger
    
    @abstractmethod
    def analyze(self, data: List[Dict]) -> Dict[str, Any]:
        """执行分析"""
        pass
    
    def validate_data(self, data: List[Dict]) -> bool:
        """验证数据有效性"""
        return data is not None and len(data) > 0