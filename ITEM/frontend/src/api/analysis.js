// src/api/analysis.js
import http from '@/utils/http';

/**
 * 文章分析接口
 * @param {Object} params - {days}
 */
export function analyzeArticlesApi(params) {
  return http.get('/api/analysis/article', { params });
}

/**
 * 评论分析接口
 * @param {Object} params - {days, article_id}
 */
export function analyzeCommentsApi(params) {
  return http.get('/api/analysis/comment', { params });
}

/**
 * 对比分析接口
 * @param {Object} params - {days}
 */
export function comparativeAnalysisApi(params) {
  return http.get('/api/analysis/comparative', { params });
}

/**
 * 词频分析接口
 * @param {Object} params - {type, days, top_n}
 */
export function getWordFrequencyApi(params) {
  return http.get('/api/analysis/word-frequency', { params });
}

/**
 * 情感分析接口
 * @param {Object} params - {type, days}
 */
export function getSentimentAnalysisApi(params) {
  return http.get('/api/analysis/sentiment', { params });
}

/**
 * 词云数据接口
 * @param {Object} params - {type, days}
 */
export function getWordCloudDataApi(params) {
  return http.get('/api/analysis/word-cloud', { params });
}

/**
 * 获取分析统计信息
 * @param {Object} params - {days}
 */
export function getAnalysisStatsApi(params) {
  return http.get('/api/analysis/stats', { params });
}

/**
 * 综合分析（一次性返回词频、情感、统计等）
 * @param {Object} params - {type: 'articles'|'comments', days: number, article_id?: string}
 */
export function comprehensiveAnalysisApi(params) {
  return http.get('/api/analysis/comprehensive', { params });
}

/**
 * 导出分析结果
 * @param {Object} data - {analysis_type, days, format}
 */
export function exportAnalysisApi(data) {
  return http.post('/api/analysis/export', data);
}

/**
 * 分析服务健康检查
 */
export function analysisHealthCheckApi() {
  return http.get('/api/analysis/health');
}