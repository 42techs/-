<!-- src/views/Analysis/Analysis.vue -->
<template>
  <div class="analysis-container">
    <!-- 查询条件 -->
    <div class="query-panel">
      <el-form :model="queryForm" inline>
        <el-form-item label="数据类型">
          <el-select v-model="queryForm.data_type">
            <el-option label="文章" value="articles" />
            <el-option label="评论" value="comments" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="时间范围">
          <el-select v-model="queryForm.days">
            <el-option label="最近1天" :value="1" />
            <el-option label="最近7天" :value="7" />
            <el-option label="最近30天" :value="30" />
          </el-select>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="handleAnalysis" :loading="loading">
            开始分析
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 分析结果展示 -->
    <div v-if="analysisResult" class="analysis-results">
      <!-- 概览统计 -->
      <el-row :gutter="20" class="stats-overview">
        <el-col :span="6">
          <el-card>
            <div class="stat-item">
              <div class="stat-value">{{ analysisResult.total_items }}</div>
              <div class="stat-label">总数据量</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card>
            <div class="stat-item">
              <div class="stat-value">{{ analysisResult.word_analysis.unique_words }}</div>
              <div class="stat-label">词汇总数</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card>
            <div class="stat-item">
              <div class="stat-value">{{ analysisResult.sentiment_analysis.statistics.positive_ratio * 100 }}%</div>
              <div class="stat-label">积极情绪</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card>
            <div class="stat-item">
              <div class="stat-value">{{ analysisResult.hotspot_analysis.total_hashtags }}</div>
              <div class="stat-label">话题数量</div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 词云和关键词 -->
      <el-row :gutter="20" class="word-analysis">
        <el-col :span="12">
          <el-card header="词云分析">
            <div ref="wordCloudChart" style="height: 300px;"></div>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card header="关键词排行">
            <el-table :data="analysisResult.word_analysis.keywords_tfidf.slice(0, 10)">
              <el-table-column prop="word" label="关键词" />
              <el-table-column prop="weight" label="权重" />
            </el-table>
          </el-card>
        </el-col>
      </el-row>

      <!-- 情感分析 -->
      <el-row :gutter="20" class="sentiment-analysis">
        <el-col :span="8">
          <el-card header="情感分布">
            <div ref="sentimentChart" style="height: 300px;"></div>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card header="情感强度">
            <el-table :data="sentimentIntensityData">
              <el-table-column prop="intensity" label="强度" />
              <el-table-column prop="count" label="数量" />
            </el-table>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card header="情感统计">
            <div class="sentiment-stats">
              <div v-for="stat in sentimentStats" :key="stat.label" class="stat-row">
                <span>{{ stat.label }}:</span>
                <span>{{ stat.value }}</span>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 时间趋势 -->
      <el-row :gutter="20">
        <el-col :span="24">
          <el-card header="时间趋势分析">
            <div ref="temporalChart" style="height: 400px;"></div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 热点话题 -->
      <el-row :gutter="20">
        <el-col :span="12">
          <el-card header="热门话题">
            <el-table :data="analysisResult.hotspot_analysis.trending_hashtags.slice(0, 10)">
              <el-table-column prop="hashtag" label="话题" />
              <el-table-column prop="count" label="出现次数" />
            </el-table>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card header="@用户排行">
            <el-table :data="analysisResult.hotspot_analysis.trending_mentions.slice(0, 10)">
              <el-table-column prop="mention" label="用户" />
              <el-table-column prop="count" label="被@次数" />
            </el-table>
          </el-card>
        </el-col>
      </el-row>

      <!-- 主题分析 -->
      <el-row :gutter="20">
        <el-col :span="24">
          <el-card header="主题分析">
            <el-collapse v-model="activeTopics">
              <el-collapse-item 
                v-for="topic in analysisResult.topic_analysis.topics" 
                :key="topic.topic_id"
                :name="topic.topic_id"
                :title="`${topic.topic_name} (包含文档: ${getTopicDocCount(topic.topic_id)})`"
              >
                <div class="topic-keywords">
                  <el-tag 
                    v-for="keyword in topic.keywords" 
                    :key="keyword.word"
                    type="info"
                    size="small"
                    class="keyword-tag"
                  >
                    {{ keyword.word }} ({{ keyword.weight }})
                  </el-tag>
                </div>
              </el-collapse-item>
            </el-collapse>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script>
import { analysisAPI } from '@/api/analysis'
import * as echarts from 'echarts'

export default {
  name: 'AnalysisPage',
  data() {
    return {
      loading: false,
      queryForm: {
        data_type: 'articles',
        days: 7
      },
      analysisResult: null,
      activeTopics: [],
      charts: {
        wordCloud: null,
        sentiment: null,
        temporal: null
      }
    }
  },
  computed: {
    // 情感强度数据
    sentimentIntensityData() {
      if (!this.analysisResult) return []
      const intensityMap = {}
      this.analysisResult.sentiment_analysis.detailed_results.forEach(item => {
        intensityMap[item.sentiment_intensity] = (intensityMap[item.sentiment_intensity] || 0) + 1
      })
      return Object.keys(intensityMap).map(key => ({
        intensity: this.getIntensityLabel(key),
        count: intensityMap[key]
      }))
    },
    
    // 情感统计数据
    sentimentStats() {
      if (!this.analysisResult) return []
      const stats = this.analysisResult.sentiment_analysis.statistics
      return [
        { label: '平均情感分', value: stats.average_sentiment },
        { label: '积极内容', value: stats.positive_count },
        { label: '消极内容', value: stats.negative_count },
        { label: '中性内容', value: stats.neutral_count }
      ]
    }
  },
  methods: {
    // 执行分析
    async handleAnalysis() {
      this.loading = true
      try {
        const response = await analysisAPI.comprehensiveAnalysis(this.queryForm)
        if (response.success) {
          this.analysisResult = response.data
          this.$nextTick(() => {
            this.renderCharts()
          })
        } else {
          this.$message.error(response.message || '分析失败')
        }
      } catch (error) {
        this.$message.error('分析请求失败')
        console.error('Analysis error:', error)
      } finally {
        this.loading = false
      }
    },

    // 渲染图表
    renderCharts() {
      this.renderWordCloud()
      this.renderSentimentChart()
      this.renderTemporalChart()
    },

    // 词云图
    renderWordCloud() {
      if (this.charts.wordCloud) {
        this.charts.wordCloud.dispose()
      }
      
      const chartDom = this.$refs.wordCloudChart
      this.charts.wordCloud = echarts.init(chartDom)
      
      const wordData = this.analysisResult.word_analysis.word_frequency.slice(0, 50)
      const option = {
        series: [{
          type: 'wordCloud',
          data: wordData,
          sizeRange: [12, 60],
          rotationRange: [-45, 90],
          gridSize: 8
        }]
      }
      
      this.charts.wordCloud.setOption(option)
    },

    // 情感分布图
    renderSentimentChart() {
      if (this.charts.sentiment) {
        this.charts.sentiment.dispose()
      }
      
      const chartDom = this.$refs.sentimentChart
      this.charts.sentiment = echarts.init(chartDom)
      
      const stats = this.analysisResult.sentiment_analysis.statistics
      const option = {
        tooltip: {
          trigger: 'item'
        },
        series: [{
          type: 'pie',
          radius: ['40%', '70%'],
          data: [
            { value: stats.positive_count, name: '积极' },
            { value: stats.negative_count, name: '消极' },
            { value: stats.neutral_count, name: '中性' }
          ]
        }]
      }
      
      this.charts.sentiment.setOption(option)
    },

    // 时间趋势图
    renderTemporalChart() {
      if (this.charts.temporal) {
        this.charts.temporal.dispose()
      }
      
      const chartDom = this.$refs.temporalChart
      this.charts.temporal = echarts.init(chartDom)
      
      const dailyData = this.analysisResult.temporal_analysis.daily_distribution
      const option = {
        tooltip: {
          trigger: 'axis'
        },
        xAxis: {
          type: 'category',
          data: dailyData.map(item => item.date)
        },
        yAxis: {
          type: 'value'
        },
        series: [{
          data: dailyData.map(item => item.count),
          type: 'line',
          smooth: true
        }]
      }
      
      this.charts.temporal.setOption(option)
    },

    // 获取主题文档数量
    getTopicDocCount(topicId) {
      const dist = this.analysisResult.topic_analysis.doc_topic_distribution
      return dist[`topic_${topicId}`] || 0
    },

    // 情感强度标签
    getIntensityLabel(intensity) {
      const labels = {
        strong: '强烈',
        moderate: '中等',
        weak: '微弱'
      }
      return labels[intensity] || intensity
    }
  },

  beforeUnmount() {
    // 销毁图表实例
    Object.values(this.charts).forEach(chart => {
      if (chart) chart.dispose()
    })
  }
}
</script>

<style scoped>
.analysis-container {
  padding: 20px;
}

.query-panel {
  margin-bottom: 20px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 4px;
}

.stats-overview {
  margin-bottom: 20px;
}

.stat-item {
  text-align: center;
  padding: 10px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #409EFF;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 5px;
}

.sentiment-stats {
  padding: 10px;
}

.stat-row {
  display: flex;
  justify-content: space-between;
  margin: 8px 0;
  font-size: 14px;
}

.topic-keywords {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.keyword-tag {
  margin: 2px;
}
</style>