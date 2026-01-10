"""主题分析器"""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from typing import List, Dict
import jieba
from .base_analyzer import BaseAnalyzer

class TopicAnalyzer(BaseAnalyzer):
    """主题建模分析器 - LDA主题模型"""
    
    def __init__(self, stop_words: set, n_topics: int = 5):
        super().__init__()
        self.stop_words = stop_words
        self.n_topics = n_topics
    
    def analyze(self, texts: List[str]) -> Dict:
        """主题分析"""
        if not texts or len(texts) < 10:  # 主题分析需要足够的文本
            return {'topics': [], 'message': '文本数量不足，无法进行主题分析'}
        
        try:
            # 分词预处理
            processed_texts = [self._preprocess(text) for text in texts]
            processed_texts = [t for t in processed_texts if t]  # 过滤空文本
            
            if len(processed_texts) < 5:
                return {'topics': [], 'message': '有效文本不足'}
            
            # TF-IDF向量化
            vectorizer = TfidfVectorizer(
                max_features=1000,
                max_df=0.8,
                min_df=2
            )
            tfidf_matrix = vectorizer.fit_transform(processed_texts)
            
            # LDA主题模型
            lda = LatentDirichletAllocation(
                n_components=min(self.n_topics, len(processed_texts) // 2),
                random_state=42,
                max_iter=20
            )
            lda.fit(tfidf_matrix)
            
            # 提取主题词
            feature_names = vectorizer.get_feature_names_out()
            topics = []
            
            for topic_idx, topic in enumerate(lda.components_):
                top_indices = topic.argsort()[-10:][::-1]
                top_words = [
                    {
                        'word': feature_names[i],
                        'weight': round(float(topic[i]), 4)
                    }
                    for i in top_indices
                ]
                
                topics.append({
                    'topic_id': topic_idx,
                    'topic_name': f"主题 {topic_idx + 1}",
                    'keywords': top_words,
                    'coherence': round(float(topic[top_indices].sum()), 4)
                })
            
            # 文档-主题分布
            doc_topic_dist = lda.transform(tfidf_matrix)
            
            return {
                'topics': topics,
                'n_topics': len(topics),
                'perplexity': round(lda.perplexity(tfidf_matrix), 4),
                'doc_topic_distribution': self._summarize_doc_distribution(doc_topic_dist)
            }
            
        except Exception as e:
            self.logger.error(f"主题分析失败: {e}")
            return {'topics': [], 'error': str(e)}
    
    def _preprocess(self, text: str) -> str:
        """文本预处理"""
        if not text:
            return ""
        words = jieba.cut(text)
        filtered = [w for w in words if len(w) >= 2 and w not in self.stop_words]
        return ' '.join(filtered)
    
    def _summarize_doc_distribution(self, doc_topic_dist) -> Dict:
        """总结文档主题分布"""
        import numpy as np
        dominant_topics = doc_topic_dist.argmax(axis=1)
        topic_counts = np.bincount(dominant_topics, minlength=self.n_topics)
        
        return {
            f'topic_{i}': int(count) 
            for i, count in enumerate(topic_counts)
        }