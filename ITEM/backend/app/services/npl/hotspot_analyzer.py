"""热点话题分析器"""
from typing import List, Dict
from collections import Counter, defaultdict
import re
from .base_analyzer import BaseAnalyzer

class HotspotAnalyzer(BaseAnalyzer):
    """热点话题与趋势分析器"""
    
    def analyze(self, data: List[Dict], text_field: str = 'text_raw') -> Dict:
        """热点分析"""
        if not data:
            return self._empty_result()
        
        try:
            # 提取话题标签
            hashtags = self._extract_hashtags(data, text_field)
            
            # 提取@用户
            mentions = self._extract_mentions(data, text_field)
            
            # 热门内容（按互动量）
            hot_contents = self._find_hot_contents(data)
            
            # 传播分析
            propagation = self._analyze_propagation(data)
            
            return {
                'trending_hashtags': hashtags[:20],
                'trending_mentions': mentions[:20],
                'hot_contents': hot_contents[:10],
                'propagation_analysis': propagation,
                'total_hashtags': len(hashtags),
                'total_mentions': len(mentions)
            }
            
        except Exception as e:
            self.logger.error(f"热点分析失败: {e}")
            return self._empty_result()
    
    def _extract_hashtags(self, data: List[Dict], text_field: str) -> List[Dict]:
        """提取话题标签"""
        hashtag_counter = Counter()
        
        for item in data:
            text = item.get(text_field, '')
            # 匹配 #话题# 格式
            hashtags = re.findall(r'#([^#]+)#', text)
            hashtag_counter.update(hashtags)
        
        return [
            {'hashtag': tag, 'count': count}
            for tag, count in hashtag_counter.most_common(50)
        ]
    
    def _extract_mentions(self, data: List[Dict], text_field: str) -> List[Dict]:
        """提取@用户"""
        mention_counter = Counter()
        
        for item in data:
            text = item.get(text_field, '')
            # 匹配 @用户 格式
            mentions = re.findall(r'@([\w\u4e00-\u9fff]+)', text)
            mention_counter.update(mentions)
        
        return [
            {'mention': user, 'count': count}
            for user, count in mention_counter.most_common(50)
        ]
    
    def _find_hot_contents(self, data: List[Dict]) -> List[Dict]:
        """找出热门内容"""
        scored_contents = []
        
        for item in data:
            # 计算热度分数（转发+评论+点赞）
            reposts = item.get('reposts_count', 0) or 0
            comments = item.get('comments_count', 0) or 0
            likes = item.get('attitudes_count', 0) or 0
            
            heat_score = reposts * 3 + comments * 2 + likes
            
            scored_contents.append({
                'content_id': str(item.get('_id', '')),
                'text_preview': item.get('text_raw', '')[:100],
                'heat_score': heat_score,
                'reposts': reposts,
                'comments': comments,
                'likes': likes,
                'created_at': item.get('created_at', '').isoformat() if hasattr(item.get('created_at', ''), 'isoformat') else str(item.get('created_at', ''))
            })
        
        # 按热度排序
        scored_contents.sort(key=lambda x: x['heat_score'], reverse=True)
        return scored_contents
    
    def _analyze_propagation(self, data: List[Dict]) -> Dict:
        """传播分析"""
        total_reposts = sum(item.get('reposts_count', 0) or 0 for item in data)
        total_comments = sum(item.get('comments_count', 0) or 0 for item in data)
        total_likes = sum(item.get('attitudes_count', 0) or 0 for item in data)
        
        return {
            'total_engagement': total_reposts + total_comments + total_likes,
            'total_reposts': total_reposts,
            'total_comments': total_comments,
            'total_likes': total_likes,
            'avg_reposts': round(total_reposts / max(len(data), 1), 2),
            'avg_comments': round(total_comments / max(len(data), 1), 2),
            'avg_likes': round(total_likes / max(len(data), 1), 2)
        }
    
    def _empty_result(self) -> Dict:
        return {
            'trending_hashtags': [],
            'trending_mentions': [],
            'hot_contents': [],
            'propagation_analysis': {},
            'total_hashtags': 0,
            'total_mentions': 0
        }