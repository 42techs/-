# app/services/analysis_service.py
import jieba
import pandas as pd
import numpy as np
from collections import Counter
from snownlp import SnowNLP
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import logging
from pymongo import MongoClient
from bson import ObjectId
import re
from typing import Dict, List, Tuple, Optional
import os

logger = logging.getLogger(__name__)

class AnalysisService:
    """数据分析服务类 - 处理所有分析业务逻辑"""
    
    def __init__(self, mongo_uri: str = 'mongodb://localhost:27017/', database: str = 'weibo_nlp'):
        """初始化分析服务"""
        self.client = MongoClient(mongo_uri)
        self.db = self.client[database]
        self.stop_words = self._load_stop_words()
        
        # 配置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
        
        # 初始化jieba分词
        jieba.initialize()

    def _load_stop_words(self) -> set:
        """加载停用词"""
        stop_words_path = os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'stopwords.txt')
        try:
            with open(stop_words_path, 'r', encoding='utf-8') as f:
                stop_words = set(f.read().splitlines())
        except FileNotFoundError:
            logger.error(f"停用词文件 {stop_words_path} 未找到")
            stop_words = set()
        return stop_words

    def clean_text(self, text: str) -> str:
        """清理文本内容"""
        if not text:
            return ""
        
        # 移除HTML标签
        text = re.sub(r'<[^>]+>', '', text)
        # 移除URL
        text = re.sub(r'https?://\S+', '', text)
        # 移除特殊字符和多余空格
        text = re.sub(r'[^\w\s\u4e00-\u9fff]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text

    def segment_text(self, texts: List[str]) -> List[str]:
        """对文本列表进行分词"""
        all_words = []
        
        for text in texts:
            if not text:
                continue
                
            cleaned_text = self.clean_text(text)
            if not cleaned_text:
                continue
                
            # 使用jieba分词
            words = jieba.cut(cleaned_text)
            # 过滤停用词和短词
            filtered_words = [
                word for word in words 
                if len(word) >= 2 and word not in self.stop_words
            ]
            all_words.extend(filtered_words)
        
        return all_words

    def get_word_frequency(self, words: List[str], top_n: int = 50) -> List[Tuple[str, int]]:
        """计算词频统计"""
        word_counter = Counter(words)
        return word_counter.most_common(top_n)

    def analyze_sentiment(self, texts: List[str]) -> Dict:
        """情感分析"""
        sentiment_results = []
        total_score = 0
        valid_count = 0
        
        for i, text in enumerate(texts):
            if not text or len(text.strip()) < 5:  # 过滤过短文本
                continue
                
            try:
                s = SnowNLP(text)
                sentiment_score = s.sentiments
                
                # 情感分类
                if sentiment_score > 0.6:
                    sentiment_label = '积极'
                elif sentiment_score < 0.4:
                    sentiment_label = '消极'
                else:
                    sentiment_label = '中性'
                
                result = {
                    'text_id': i,
                    'text_preview': text[:100] + '...' if len(text) > 100 else text,
                    'sentiment_score': round(sentiment_score, 4),
                    'sentiment_label': sentiment_label,
                    'text_length': len(text)
                }
                sentiment_results.append(result)
                total_score += sentiment_score
                valid_count += 1
                
            except Exception as e:
                logger.warning(f"情感分析失败: {e}")
                continue
        
        if valid_count == 0:
            return {
                'detailed_results': [],
                'average_sentiment': 0.5,
                'positive_count': 0,
                'negative_count': 0,
                'neutral_count': 0,
                'total_texts': 0
            }
        
        avg_score = total_score / valid_count
        
        return {
            'detailed_results': sentiment_results,
            'average_sentiment': round(avg_score, 4),
            'positive_count': len([r for r in sentiment_results if r['sentiment_label'] == '积极']),
            'negative_count': len([r for r in sentiment_results if r['sentiment_label'] == '消极']),
            'neutral_count': len([r for r in sentiment_results if r['sentiment_label'] == '中性']),
            'total_texts': valid_count
        }

    def get_articles_data(self, days: int = 7) -> List[Dict]:
        """从MongoDB获取文章数据"""
        try:
            # 计算时间范围
            start_date = datetime.now() - timedelta(days=days)
            
            # 查询文章数据
            articles = list(self.db.articles.find({
                'created_at': {'$gte': start_date}
            }).sort('created_at', -1))
            
            logger.info(f"从MongoDB获取到 {len(articles)} 篇文章")
            return articles
            
        except Exception as e:
            logger.error(f"获取文章数据失败: {e}")
            return []

    def get_comments_data(self, article_id: Optional[str] = None, days: int = 7) -> List[Dict]:
        """从MongoDB获取评论数据"""
        try:
            start_date = datetime.now() - timedelta(days=days)
            query = {'created_at': {'$gte': start_date}}
            
            if article_id:
                query['article_id'] = article_id
            
            comments = list(self.db.comments.find(query).sort('created_at', -1))
            logger.info(f"从MongoDB获取到 {len(comments)} 条评论")
            return comments
            
        except Exception as e:
            logger.error(f"获取评论数据失败: {e}")
            return []

    def generate_word_cloud_data(self, words: List[str]) -> Dict:
        """生成词云数据（返回词频，不生成图片）"""
        if not words:
            return {'success': False, 'message': '无有效词汇生成词云'}
        
        word_freq = Counter(words)
        top_words = word_freq.most_common(100)
        
        return {
            'success': True,
            'word_cloud_data': [
                {'text': word, 'value': count} 
                for word, count in top_words
            ],
            'total_words': len(words),
            'unique_words': len(set(words))
        }

    def analyze_articles(self, days: int = 7) -> Dict:
        """综合分析文章数据"""
        logger.info(f"开始分析最近 {days} 天的文章数据...")
        
        try:
            # 获取文章数据
            articles = self.get_articles_data(days)
            if not articles:
                return {'success': False, 'message': '没有找到文章数据'}
            
            # 提取文章内容
            article_texts = [article.get('text_raw', '') for article in articles]
            
            # 分词和词频分析
            words = self.segment_text(article_texts)
            word_freq = self.get_word_frequency(words)
            
            # 情感分析
            sentiment_results = self.analyze_sentiment(article_texts)
            
            # 词云数据
            word_cloud_data = self.generate_word_cloud_data(words)
            
            # 统计信息
            stats = {
                'total_articles': len(articles),
                'total_words': len(words),
                'unique_words': len(set(words)),
                'avg_article_length': np.mean([len(text) for text in article_texts]) if article_texts else 0
            }
            
            return {
                'success': True,
                'analysis_type': 'articles',
                'time_range_days': days,
                'word_frequency': word_freq,
                'sentiment_analysis': sentiment_results,
                'word_cloud_data': word_cloud_data,
                'statistics': stats,
                'sample_data': {
                    'articles_sample': article_texts[:3] if article_texts else [],
                    'top_words_sample': word_freq[:10]
                }
            }
            
        except Exception as e:
            logger.error(f"文章分析失败: {e}")
            return {'success': False, 'message': f'文章分析失败: {str(e)}'}

    def analyze_comments(self, article_id: Optional[str] = None, days: int = 7) -> Dict:
        """分析评论数据"""
        logger.info(f"开始分析最近 {days} 天的评论数据...")
        
        try:
            comments = self.get_comments_data(article_id, days)
            if not comments:
                return {'success': False, 'message': '没有找到评论数据'}
            
            # 提取评论内容
            comment_texts = [comment.get('text_raw', '') for comment in comments]
            
            # 分词和词频分析
            words = self.segment_text(comment_texts)
            word_freq = self.get_word_frequency(words)
            
            # 情感分析
            sentiment_results = self.analyze_sentiment(comment_texts)
            
            # 词云数据
            word_cloud_data = self.generate_word_cloud_data(words)
            
            # 统计信息
            stats = {
                'total_comments': len(comments),
                'total_words': len(words),
                'unique_words': len(set(words)),
                'avg_comment_length': np.mean([len(text) for text in comment_texts]) if comment_texts else 0,
                'article_specific': article_id is not None
            }
            
            result = {
                'success': True,
                'analysis_type': 'comments',
                'time_range_days': days,
                'article_id': article_id,
                'word_frequency': word_freq,
                'sentiment_analysis': sentiment_results,
                'word_cloud_data': word_cloud_data,
                'statistics': stats
            }
            
            if article_id:
                result['article_info'] = f"针对文章 {article_id} 的评论分析"
            
            return result
            
        except Exception as e:
            logger.error(f"评论分析失败: {e}")
            return {'success': False, 'message': f'评论分析失败: {str(e)}'}

    def comparative_analysis(self, days: int = 7) -> Dict:
        """对比分析文章和评论"""
        logger.info("开始对比分析文章和评论数据...")
        
        try:
            # 分析文章
            articles_result = self.analyze_articles(days)
            # 分析评论
            comments_result = self.analyze_comments(None, days)
            
            if not articles_result['success'] or not comments_result['success']:
                return {'success': False, 'message': '对比分析数据获取失败'}
            
            # 对比分析
            comparison = {
                'sentiment_comparison': {
                    'articles_avg_sentiment': articles_result['sentiment_analysis']['average_sentiment'],
                    'comments_avg_sentiment': comments_result['sentiment_analysis']['average_sentiment'],
                    'sentiment_difference': round(
                        articles_result['sentiment_analysis']['average_sentiment'] - 
                        comments_result['sentiment_analysis']['average_sentiment'], 4
                    )
                },
                'word_frequency_comparison': {
                    'articles_top_words': articles_result['word_frequency'][:10],
                    'comments_top_words': comments_result['word_frequency'][:10]
                },
                'volume_comparison': {
                    'articles_count': articles_result['statistics']['total_articles'],
                    'comments_count': comments_result['statistics']['total_comments'],
                    'comments_to_articles_ratio': round(
                        comments_result['statistics']['total_comments'] / 
                        max(articles_result['statistics']['total_articles'], 1), 2
                    )
                }
            }
            
            return {
                'success': True,
                'analysis_type': 'comparative',
                'time_range_days': days,
                'comparison': comparison,
                'articles_summary': {
                    'total_articles': articles_result['statistics']['total_articles'],
                    'avg_sentiment': articles_result['sentiment_analysis']['average_sentiment']
                },
                'comments_summary': {
                    'total_comments': comments_result['statistics']['total_comments'],
                    'avg_sentiment': comments_result['sentiment_analysis']['average_sentiment']
                }
            }
            
        except Exception as e:
            logger.error(f"对比分析失败: {e}")
            return {'success': False, 'message': f'对比分析失败: {str(e)}'}

    def get_analysis_history(self, limit: int = 10) -> List[Dict]:
        """获取分析历史记录"""
        try:
            # 这里可以从MongoDB中查询分析历史
            # 暂时返回空列表，实际项目中可以完善
            return []
        except Exception as e:
            logger.error(f"获取分析历史失败: {e}")
            return []

    def export_analysis_results(self, analysis_result: Dict, format_type: str = 'json') -> Dict:
        """导出分析结果"""
        try:
            if format_type == 'json':
                return {
                    'success': True,
                    'format': 'json',
                    'data': analysis_result,
                    'export_time': datetime.now().isoformat()
                }
            else:
                return {'success': False, 'message': f'不支持的导出格式: {format_type}'}
                
        except Exception as e:
            logger.error(f"导出分析结果失败: {e}")
            return {'success': False, 'message': f'导出失败: {str(e)}'}

    def close_connection(self):
        """关闭数据库连接"""
        if hasattr(self, 'client'):
            self.client.close()