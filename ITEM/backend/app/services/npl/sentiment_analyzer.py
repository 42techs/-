"""情感分析器"""
from snownlp import SnowNLP
from typing import List, Dict
import numpy as np
from .base_analyzer import BaseAnalyzer

class SentimentAnalyzer(BaseAnalyzer):
    """情感分析器 - 支持细粒度情感分析"""
    
    def analyze(self, texts: List[str]) -> Dict:
        """执行情感分析"""
        if not texts:
            return self._empty_result()
        
        sentiment_scores = []
        sentiment_labels = []
        emotion_distribution = {'positive': 0, 'negative': 0, 'neutral': 0}
        
        detailed_results = []
        
        for idx, text in enumerate(texts):
            if not text or len(text.strip()) < 5:
                continue
            
            try:
                s = SnowNLP(text)
                score = s.sentiments
                
                # 细粒度情感分类
                label = self._classify_sentiment(score)
                sentiment_scores.append(score)
                sentiment_labels.append(label)
                emotion_distribution[label] += 1
                
                # 情感强度
                intensity = self._calculate_intensity(score)
                
                detailed_results.append({
                    'text_id': idx,
                    'text_preview': text[:100] + '...' if len(text) > 100 else text,
                    'sentiment_score': round(score, 4),
                    'sentiment_label': label,
                    'sentiment_intensity': intensity,
                    'text_length': len(text)
                })
                
            except Exception as e:
                self.logger.warning(f"情感分析失败: {e}")
                continue
        
        if not sentiment_scores:
            return self._empty_result()
        
        return {
            'detailed_results': detailed_results,
            'statistics': {
                'average_sentiment': round(np.mean(sentiment_scores), 4),
                'median_sentiment': round(np.median(sentiment_scores), 4),
                'std_sentiment': round(np.std(sentiment_scores), 4),
                'positive_count': emotion_distribution['positive'],
                'negative_count': emotion_distribution['negative'],
                'neutral_count': emotion_distribution['neutral'],
                'total_analyzed': len(sentiment_scores),
                'positive_ratio': round(emotion_distribution['positive'] / len(sentiment_scores), 4),
                'negative_ratio': round(emotion_distribution['negative'] / len(sentiment_scores), 4),
                'neutral_ratio': round(emotion_distribution['neutral'] / len(sentiment_scores), 4)
            },
            'sentiment_distribution': self._calculate_distribution(sentiment_scores)
        }
    
    def _classify_sentiment(self, score: float) -> str:
        """情感分类"""
        if score >= 0.7:
            return 'positive'
        elif score <= 0.3:
            return 'negative'
        else:
            return 'neutral'
    
    def _calculate_intensity(self, score: float) -> str:
        """计算情感强度"""
        if score >= 0.8 or score <= 0.2:
            return 'strong'
        elif score >= 0.6 or score <= 0.4:
            return 'moderate'
        else:
            return 'weak'
    
    def _calculate_distribution(self, scores: List[float]) -> Dict:
        """计算情感分布"""
        bins = [0, 0.2, 0.4, 0.6, 0.8, 1.0]
        hist, _ = np.histogram(scores, bins=bins)
        
        return {
            'very_negative': int(hist[0]),
            'negative': int(hist[1]),
            'neutral': int(hist[2]),
            'positive': int(hist[3]),
            'very_positive': int(hist[4])
        }
    
    def _empty_result(self) -> Dict:
        return {
            'detailed_results': [],
            'statistics': {
                'average_sentiment': 0.5,
                'median_sentiment': 0.5,
                'std_sentiment': 0,
                'positive_count': 0,
                'negative_count': 0,
                'neutral_count': 0,
                'total_analyzed': 0,
                'positive_ratio': 0,
                'negative_ratio': 0,
                'neutral_ratio': 0
            },
            'sentiment_distribution': {
                'very_negative': 0, 'negative': 0, 'neutral': 0,
                'positive': 0, 'very_positive': 0
            }
        }