"""词频分析器"""
import jieba
import jieba.analyse
from collections import Counter
from typing import List, Dict, Tuple
from .base_analyzer import BaseAnalyzer

class WordFrequencyAnalyzer(BaseAnalyzer):
    """词频与关键词提取分析器"""
    
    def __init__(self, stop_words: set):
        super().__init__()
        self.stop_words = stop_words
        jieba.initialize()
    
    def analyze(self, texts: List[str], top_n: int = 50) -> Dict:
        """词频分析"""
        if not texts:
            return self._empty_result()
        
        # 分词
        words = self._segment_texts(texts)
        
        # 词频统计
        word_freq = Counter(words).most_common(top_n)
        
        # TF-IDF关键词提取
        keywords_tfidf = self._extract_keywords_tfidf(texts, top_n)
        
        # TextRank关键词提取
        keywords_textrank = self._extract_keywords_textrank(texts, top_n)
        
        return {
            'word_frequency': [{'word': w, 'count': c} for w, c in word_freq],
            'keywords_tfidf': keywords_tfidf,
            'keywords_textrank': keywords_textrank,
            'total_words': len(words),
            'unique_words': len(set(words)),
            'vocabulary_diversity': round(len(set(words)) / max(len(words), 1), 4)
        }
    
    def _segment_texts(self, texts: List[str]) -> List[str]:
        """文本分词"""
        all_words = []
        for text in texts:
            if not text:
                continue
            words = jieba.cut(text)
            filtered_words = [
                word for word in words 
                if len(word) >= 2 and word not in self.stop_words
            ]
            all_words.extend(filtered_words)
        return all_words
    
    def _extract_keywords_tfidf(self, texts: List[str], top_n: int) -> List[Dict]:
        """TF-IDF关键词提取"""
        combined_text = ' '.join(texts)
        keywords = jieba.analyse.extract_tags(
            combined_text, 
            topK=top_n, 
            withWeight=True
        )
        return [{'word': word, 'weight': round(weight, 4)} for word, weight in keywords]
    
    def _extract_keywords_textrank(self, texts: List[str], top_n: int) -> List[Dict]:
        """TextRank关键词提取"""
        combined_text = ' '.join(texts)
        keywords = jieba.analyse.textrank(
            combined_text, 
            topK=top_n, 
            withWeight=True
        )
        return [{'word': word, 'weight': round(weight, 4)} for word, weight in keywords]
    
    def _empty_result(self) -> Dict:
        return {
            'word_frequency': [],
            'keywords_tfidf': [],
            'keywords_textrank': [],
            'total_words': 0,
            'unique_words': 0,
            'vocabulary_diversity': 0
        }