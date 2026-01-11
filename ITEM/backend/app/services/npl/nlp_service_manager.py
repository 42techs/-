"""NLP服务管理器 - 统一管理所有分析器"""
from typing import Dict, List, Optional
from pymongo import MongoClient
from datetime import datetime, timedelta
import logging
import os

from .word_frequency_analyzer import WordFrequencyAnalyzer
from .sentiment_analyzer import SentimentAnalyzer
from .topic_analyzer import TopicAnalyzer
from .temporal_analyzer import TemporalAnalyzer
from .hotspot_analyzer import HotspotAnalyzer

logger = logging.getLogger(__name__)

class NLPServiceManager:
    """NLP服务管理器"""
    
    def __init__(self, mongo_uri: str, database: str):
        self.client = MongoClient(mongo_uri)
        self.db = self.client[database]
        
        # 加载停用词
        self.stop_words = self._load_stop_words()
        
        # 初始化各个分析器
        self.word_analyzer = WordFrequencyAnalyzer(self.stop_words)
        self.sentiment_analyzer = SentimentAnalyzer()
        self.topic_analyzer = TopicAnalyzer(self.stop_words, n_topics=5)
        self.temporal_analyzer = TemporalAnalyzer()
        self.hotspot_analyzer = HotspotAnalyzer()
    
    def comprehensive_analysis(
        self, 
        data_type: str = 'articles',
        days: int = 7,
        article_id: Optional[str] = None
    ) -> Dict:
        """综合分析 - 一次性执行所有分析"""
        logger.info(f"开始综合分析: type={data_type}, days={days}")
        
        try:
            # 获取数据
            data = self._fetch_data(data_type, days, article_id)
            
            if not data:
                return {'success': False, 'message': '没有找到数据'}
            
            texts = [item.get('text_raw', '') for item in data]
            texts = [t for t in texts if t and len(t.strip()) > 0]
            
            if not texts:
                return {'success': False, 'message': '没有有效文本'}
            
            # 执行各项分析
            results = {
                'success': True,
                'data_type': data_type,
                'time_range_days': days,
                'total_items': len(data),
                'analysis_timestamp': datetime.now().isoformat(),
                
                # 词频分析
                'word_analysis': self.word_analyzer.analyze(texts, top_n=50),
                
                # 情感分析
                'sentiment_analysis': self.sentiment_analyzer.analyze(texts),
                
                # 主题分析
                'topic_analysis': self.topic_analyzer.analyze(texts),
                
                # 时间序列分析
                'temporal_analysis': self.temporal_analyzer.analyze(data),
                
                # 热点分析
                'hotspot_analysis': self.hotspot_analyzer.analyze(data)
            }
            
            return results
            
        except Exception as e:
            logger.error(f"综合分析失败: {e}")
            return {'success': False, 'message': f'分析失败: {str(e)}'}
    
    def _fetch_data(
        self, 
        data_type: str, 
        days: int, 
        article_id: Optional[str]
    ) -> List[Dict]:
        """获取数据"""
        start_date = datetime.now() - timedelta(days=days)
        
        if data_type in ('articles', 'article'):
            query = {'created_at': {'$gte': start_date}}
            return list(self.db.articles.find(query).sort('created_at', -1))
        
        elif data_type in ('comments', 'comment'):
            query = {'created_at': {'$gte': start_date}}
            if article_id:
                query['article_id'] = article_id
            return list(self.db.comments.find(query).sort('created_at', -1))
        
        return []
    
    def _load_stop_words(self) -> set:
        """加载停用词"""
        # 首先尝试从同目录下的 stopwords.txt 加载（每行一个词）
        try:
            here = os.path.dirname(__file__)
            path = os.path.join(here, 'stopwords.txt')
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    words = {line.strip() for line in f if line.strip() and not line.strip().startswith('#')}
                    logger.info(f'Loaded {len(words)} stop words from {path}')
                    return words
        except Exception as e:
            logger.warning(f'加载停用词文件失败: {e}')

        # 回退到基础停用词集（最小集，避免完全为空）
        base_stop_words = {
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人'
        }
        return base_stop_words
    
    def close(self):
        """关闭数据库连接"""
        if hasattr(self, 'client'):
            self.client.close()