<template>
  <div class="analysis-container">
    <div class="header">
      <h1>数据分析中心</h1>
      <p class="subtitle">Social Media NLP Analysis Platform</p>
    </div>

    <!-- 控制面板 -->
    <div class="control-panel">
      <div class="filters">
        <div class="filter-item">
          <label>数据类型</label>
          <!-- 移除@change事件，仅依赖按钮点击 -->
          <select v-model="filters.type">
            <option value="articles">文章</option>
            <option value="comments">评论</option>
          </select>
        </div>

        <div class="filter-item">
          <label>时间范围</label>
          <select v-model="filters.days">
            <option :value="1">最近1天</option>
            <option :value="7">最近7天</option>
            <option :value="14">最近14天</option>
            <option :value="30">最近30天</option>
            <option :value="90">最近90天</option>
          </select>
        </div>

        <div class="filter-item" v-if="filters.type === 'comments'">
          <label>文章ID（可选）</label>
          <input 
            v-model="filters.articleId" 
            type="text" 
            placeholder="输入文章ID"
          />
        </div>

        <!-- 仅点击按钮时执行分析 -->
        <button 
          class="btn-refresh" 
          @click="loadAnalysis"
          :disabled="loading"
        >
          {{ loading ? '分析中...' : '刷新分析' }}
        </button>
      </div>

      <div class="stats-bar" v-if="analysisData">
        <div class="stat-card">
          <div class="stat-label">总数据量</div>
          <div class="stat-value">{{ analysisData.total_items || 0 }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">分析时间</div>
          <div class="stat-value">{{ formatDate(analysisData.analysis_timestamp) }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">数据类型</div>
          <div class="stat-value">{{ filters.type === 'articles' ? '文章' : '评论' }}</div>
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>正在分析数据，请稍候...</p>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="error-state">
      <p>{{ error }}</p>
      <button @click="loadAnalysis">重试</button>
    </div>

    <!-- 分析结果 -->
    <div v-else-if="analysisData" class="analysis-content">
      <!-- 标签页导航 -->
      <div class="tabs">
        <button 
          v-for="tab in tabs" 
          :key="tab.key"
          :class="['tab', { active: activeTab === tab.key }]"
          @click="activeTab = tab.key"
        >
          <span class="tab-icon">{{ tab.icon }}</span>
          <span class="tab-label">{{ tab.label }}</span>
        </button>
      </div>

      <!-- 标签页内容 -->
      <div class="tab-content">
        <WordFrequencyAnalysis 
          v-show="activeTab === 'word'"
          :data="analysisData.word_analysis"
        />
        
        <SentimentAnalysis 
          v-show="activeTab === 'sentiment'"
          :data="analysisData.sentiment_analysis"
        />
        
        <TopicAnalysis 
          v-show="activeTab === 'topic'"
          :data="analysisData.topic_analysis"
        />
        
        <TemporalAnalysis 
          v-show="activeTab === 'temporal'"
          :data="analysisData.temporal_analysis"
        />
        
        <HotspotAnalysis 
          v-show="activeTab === 'hotspot'"
          :data="analysisData.hotspot_analysis"
        />
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else class="empty-state">
      <p>👆 选择条件后点击"刷新分析"开始分析</p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getComprehensiveAnalysis } from '@/api/analysis'
import WordFrequencyAnalysis from './components/WordFrequencyAnalysis.vue'
import SentimentAnalysis from './components/SentimentAnalysis.vue'
import TopicAnalysis from './components/TopicAnalysis.vue'
import TemporalAnalysis from './components/TemporalAnalysis.vue'
import HotspotAnalysis from './components/HotspotAnalysis.vue'

const loading = ref(false)
const error = ref(null)
const analysisData = ref(null)
const activeTab = ref('word')

const filters = reactive({
  type: 'articles',
  days: 7,
  articleId: ''
})

const tabs = [
  { key: 'word', label: '词频分析', icon: '📊' },
  { key: 'sentiment', label: '情感分析', icon: '❤️' },
  { key: 'topic', label: '主题建模', icon: '🧠' },
  { key: 'temporal', label: '时间趋势', icon: '📈' },
  { key: 'hotspot', label: '热点分析', icon: '🔥' }
]

const loadAnalysis = async () => {
  loading.value = true
  error.value = null

  try {
    const params = {
      type: filters.type,
      days: filters.days
    }
    
    if (filters.type === 'comments' && filters.articleId) {
      params.article_id = filters.articleId
    }

    console.log('发送分析请求，参数:', params)

    const response = await getComprehensiveAnalysis(params)
    
    console.log('原始响应:', response)
    
    // 🔧 关键修复：正确解析响应结构
    // 响应格式: { success: true, data: {...}, message: '...' }
    if (response.success) {
      analysisData.value = response.data
      console.log('分析数据:', analysisData.value)
      
      // 检查是否有有效数据
      if (analysisData.value.total_items === 0) {
        error.value = analysisData.value.message || '暂无数据'
      }
    } else {
      error.value = response.message || '分析失败'
      console.error('分析失败:', response)
    }
  } catch (err) {
    console.error('分析请求错误:', err)
    
    // 显示详细错误信息
    if (err.message) {
      error.value = err.message
    } else if (err.data?.message) {
      error.value = err.data.message
    } else {
      error.value = '分析失败，请查看控制台获取详细信息'
    }
  } finally {
    loading.value = false
  }
}

const formatDate = (timestamp) => {
  if (!timestamp) return '-'
  return new Date(timestamp).toLocaleString('zh-CN')
}

onMounted(() => {
  // 可以自动加载一次
  // loadAnalysis()
})
</script>

<style scoped>
.analysis-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.header {
  text-align: center;
  margin-bottom: 30px;
}

.header h1 {
  font-size: 32px;
  font-weight: 700;
  color: #1a1a1a;
  margin-bottom: 8px;
}

.subtitle {
  color: #666;
  font-size: 14px;
}

.control-panel {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  margin-bottom: 20px;
}

.filters {
  display: flex;
  gap: 15px;
  align-items: flex-end;
  flex-wrap: wrap;
  margin-bottom: 20px;
}

.filter-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.filter-item label {
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.filter-item select,
.filter-item input {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  min-width: 150px;
}

.btn-refresh {
  padding: 8px 20px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: background 0.2s;
}

.btn-refresh:hover:not(:disabled) {
  background: #2563eb;
}

.btn-refresh:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.stats-bar {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.stat-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 15px;
  border-radius: 8px;
  color: white;
}

.stat-label {
  font-size: 12px;
  opacity: 0.9;
  margin-bottom: 5px;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
}

.loading-state,
.error-state,
.empty-state {
  text-align: center;
  padding: 60px 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  overflow-x: auto;
  padding-bottom: 5px;
}

.tab {
  padding: 12px 20px;
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 8px;
  white-space: nowrap;
}

.tab:hover {
  border-color: #3b82f6;
}

.tab.active {
  background: #3b82f6;
  color: white;
  border-color: #3b82f6;
}

.tab-icon {
  font-size: 18px;
}

.tab-label {
  font-weight: 500;
}

.tab-content {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  min-height: 500px;
}
</style>

