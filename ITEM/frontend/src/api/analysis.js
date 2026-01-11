import http from '@/utils/http'

/**
 * 获取综合分析结果
 * @param {Object} params - { type: 'articles'|'comments', days: 1-90, article_id?: string }
 */
export const getComprehensiveAnalysis = (params) => {
  return http.get('/analysis/comprehensive', { params })
}

/**
 * 生成词云图配置
 * @param {Array} wordData - [{ word, count }]
 */
export const generateWordCloud = (wordData) => {
  return http.post('/analysis/charts/word-cloud', { word_data: wordData })
}

/**
 * 生成情感饼图配置
 * @param {Object} sentimentStats - { positive_count, neutral_count, negative_count }
 */
export const generateSentimentPie = (sentimentStats) => {
  return http.post('/analysis/charts/sentiment-pie', { sentiment_stats: sentimentStats })
}

/**
 * 生成时间趋势图配置
 * @param {Array} dailyData - [{ date, count }]
 */
export const generateTemporalLine = (dailyData) => {
  return http.post('/analysis/charts/temporal-line', { daily_data: dailyData })
}