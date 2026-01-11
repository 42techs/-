<template>
  <div class="sentiment-analysis">
    <h2>❤️ 情感分析</h2>

    <div v-if="!data?.statistics" class="empty">
      <p>暂无情感数据</p>
    </div>

    <div v-else>
      <!-- 核心指标 -->
      <div class="stats-overview">
        <div class="stat-box">
          <div class="stat-label">分析总数</div>
          <div class="stat-value">{{ data.statistics.total_analyzed }}</div>
        </div>
        <div class="stat-box">
          <div class="stat-label">平均情感</div>
          <div class="stat-value" :class="getSentimentClass(data.statistics.average_sentiment)">
            {{ data.statistics.average_sentiment?.toFixed(4) }}
          </div>
        </div>
        <div class="stat-box">
          <div class="stat-label">中位数</div>
          <div class="stat-value">{{ data.statistics.median_sentiment?.toFixed(4) }}</div>
        </div>
        <div class="stat-box">
          <div class="stat-label">标准差</div>
          <div class="stat-value">{{ data.statistics.std_sentiment?.toFixed(4) }}</div>
        </div>
      </div>

      <!-- 三分类分布 -->
      <div class="distribution-grid">
        <section class="pie-section">
          <h3>情感分类分布</h3>
          <div class="pie-chart">
            <svg viewBox="0 0 200 200" class="pie-svg">
              <circle
                v-for="(segment, index) in pieSegments"
                :key="index"
                :cx="100"
                :cy="100"
                :r="80"
                :stroke="segment.color"
                :stroke-width="60"
                :stroke-dasharray="`${segment.dashArray} ${circumference}`"
                :stroke-dashoffset="segment.offset"
                fill="transparent"
                class="pie-segment"
              />
            </svg>
            <div class="pie-center">
              <div class="total-label">总计</div>
              <div class="total-value">{{ data.statistics.total_analyzed }}</div>
            </div>
          </div>
          <div class="legend">
            <div class="legend-item" v-for="item in sentimentCategories" :key="item.key">
              <div class="legend-color" :style="{ background: item.color }"></div>
              <span class="legend-label">{{ item.label }}</span>
              <span class="legend-value">
                {{ data.statistics[`${item.key}_count`] }}
                ({{ (data.statistics[`${item.key}_ratio`] * 100).toFixed(1) }}%)
              </span>
            </div>
          </div>
        </section>

        <!-- 细粒度分布 -->
        <section class="distribution-section">
          <h3>细粒度情感分布</h3>
          <div class="distribution-bars">
            <div 
              v-for="(item, index) in detailedDistribution" 
              :key="index"
              class="dist-bar-item"
            >
              <span class="dist-label">{{ item.label }}</span>
              <div class="dist-bar-bg">
                <div 
                  class="dist-bar-fill" 
                  :style="{ 
                    width: `${(item.count / maxDistCount) * 100}%`,
                    background: item.color 
                  }"
                ></div>
              </div>
              <span class="dist-count">{{ item.count }}</span>
            </div>
          </div>
        </section>
      </div>

      <!-- 详细结果列表 -->
      <section class="details-section" v-if="data.detailed_results">
        <div class="section-header">
          <h3>详细分析结果（前20条）</h3>
          <div class="filter-buttons">
            <button 
              v-for="filter in sentimentFilters" 
              :key="filter.value"
              :class="['filter-btn', { active: activeFilter === filter.value }]"
              @click="activeFilter = filter.value"
            >
              {{ filter.label }}
            </button>
          </div>
        </div>

        <div class="results-list">
          <div 
            v-for="(item, index) in filteredResults" 
            :key="index"
            class="result-card"
          >
            <div class="result-header">
              <span class="result-id">#{{ item.text_id + 1 }}</span>
              <span 
                class="sentiment-badge" 
                :class="`badge-${item.sentiment_label}`"
              >
                {{ getLabelText(item.sentiment_label) }}
              </span>
              <span class="sentiment-score">
                分数: {{ item.sentiment_score?.toFixed(4) }}
              </span>
              <span 
                class="intensity-badge"
                :class="`intensity-${item.sentiment_intensity}`"
              >
                {{ getIntensityText(item.sentiment_intensity) }}
              </span>
            </div>
            <p class="result-text">{{ item.text_preview }}</p>
            <div class="result-meta">
              <span>文本长度: {{ item.text_length }} 字</span>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  data: {
    type: Object,
    default: () => ({})
  }
})

const activeFilter = ref('all')

const circumference = 2 * Math.PI * 80

const sentimentCategories = [
  { key: 'positive', label: '积极', color: '#10b981' },
  { key: 'neutral', label: '中性', color: '#6b7280' },
  { key: 'negative', label: '消极', color: '#ef4444' }
]

const sentimentFilters = [
  { value: 'all', label: '全部' },
  { value: 'positive', label: '积极' },
  { value: 'neutral', label: '中性' },
  { value: 'negative', label: '消极' }
]

const pieSegments = computed(() => {
  const stats = props.data?.statistics || {}
  const total = stats.total_analyzed || 1
  
  let currentOffset = 0
  return sentimentCategories.map(cat => {
    const count = stats[`${cat.key}_count`] || 0
    const percent = count / total
    const dashArray = percent * circumference
    
    const segment = {
      color: cat.color,
      dashArray: dashArray,
      offset: -currentOffset
    }
    
    currentOffset += dashArray
    return segment
  })
})

const detailedDistribution = computed(() => {
  const dist = props.data?.sentiment_distribution || {}
  return [
    { label: '非常消极', count: dist.very_negative || 0, color: '#dc2626' },
    { label: '消极', count: dist.negative || 0, color: '#ef4444' },
    { label: '中性', count: dist.neutral || 0, color: '#6b7280' },
    { label: '积极', count: dist.positive || 0, color: '#10b981' },
    { label: '非常积极', count: dist.very_positive || 0, color: '#059669' }
  ]
})

const maxDistCount = computed(() => {
  return Math.max(...detailedDistribution.value.map(d => d.count), 1)
})

const filteredResults = computed(() => {
  const results = props.data?.detailed_results || []
  if (activeFilter.value === 'all') {
    return results.slice(0, 20)
  }
  return results.filter(r => r.sentiment_label === activeFilter.value).slice(0, 20)
})

const getSentimentClass = (score) => {
  if (score >= 0.7) return 'positive'
  if (score <= 0.3) return 'negative'
  return 'neutral'
}

const getLabelText = (label) => {
  const map = {
    'positive': '积极',
    'neutral': '中性',
    'negative': '消极'
  }
  return map[label] || label
}

const getIntensityText = (intensity) => {
  const map = {
    'strong': '强',
    'moderate': '中',
    'weak': '弱'
  }
  return map[intensity] || intensity
}
</script>

<style scoped>
.sentiment-analysis h2 {
  font-size: 24px;
  margin-bottom: 20px;
  color: #1a1a1a;
}

.empty {
  text-align: center;
  padding: 60px 20px;
  color: #6b7280;
}

.stats-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 30px;
}

.stat-box {
  background: white;
  padding: 20px;
  border-radius: 10px;
  border: 2px solid #e5e7eb;
}

.stat-label {
  font-size: 14px;
  color: #6b7280;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1f2937;
}

.stat-value.positive {
  color: #10b981;
}

.stat-value.negative {
  color: #ef4444;
}

.stat-value.neutral {
  color: #6b7280;
}

.distribution-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 30px;
}

@media (max-width: 768px) {
  .distribution-grid {
    grid-template-columns: 1fr;
  }
}

.pie-section,
.distribution-section {
  background: #f9fafb;
  padding: 20px;
  border-radius: 10px;
}

.pie-section h3,
.distribution-section h3 {
  font-size: 18px;
  margin-bottom: 20px;
  color: #374151;
}

.pie-chart {
  position: relative;
  width: 200px;
  height: 200px;
  margin: 0 auto 20px;
}

.pie-svg {
  transform: rotate(-90deg);
}

.pie-segment {
  transition: all 0.3s;
}

.pie-center {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}

.total-label {
  font-size: 12px;
  color: #6b7280;
}

.total-value {
  font-size: 24px;
  font-weight: 700;
  color: #1f2937;
}

.legend {
  display: grid;
  gap: 10px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  background: white;
  border-radius: 6px;
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: 3px;
}

.legend-label {
  flex: 1;
  font-weight: 500;
  color: #374151;
}

.legend-value {
  font-weight: 600;
  color: #6b7280;
}

.distribution-bars {
  display: grid;
  gap: 12px;
}

.dist-bar-item {
  display: grid;
  grid-template-columns: 100px 1fr 60px;
  align-items: center;
  gap: 10px;
}

.dist-label {
  font-weight: 500;
  color: #4b5563;
  font-size: 14px;
}

.dist-bar-bg {
  height: 24px;
  background: #e5e7eb;
  border-radius: 4px;
  overflow: hidden;
}

.dist-bar-fill {
  height: 100%;
  transition: width 0.3s;
}

.dist-count {
  text-align: right;
  font-weight: 600;
  color: #374151;
}

.details-section {
  background: #f9fafb;
  padding: 20px;
  border-radius: 10px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 15px;
}

.section-header h3 {
  font-size: 18px;
  color: #374151;
  margin: 0;
}

.filter-buttons {
  display: flex;
  gap: 8px;
}

.filter-btn {
  padding: 6px 16px;
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 14px;
  font-weight: 500;
  color: #6b7280;
}

.filter-btn:hover {
  border-color: #3b82f6;
  color: #3b82f6;
}

.filter-btn.active {
  background: #3b82f6;
  border-color: #3b82f6;
  color: white;
}

.results-list {
  display: grid;
  gap: 15px;
  max-height: 600px;
  overflow-y: auto;
}

.result-card {
  background: white;
  padding: 15px;
  border-radius: 8px;
  border-left: 4px solid #e5e7eb;
}

.result-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
  flex-wrap: wrap;
}

.result-id {
  font-weight: 700;
  color: #6b7280;
  font-size: 14px;
}

.sentiment-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.badge-positive {
  background: #d1fae5;
  color: #059669;
}

.badge-neutral {
  background: #e5e7eb;
  color: #4b5563;
}

.badge-negative {
  background: #fee2e2;
  color: #dc2626;
}

.sentiment-score {
  font-size: 13px;
  color: #6b7280;
  font-weight: 500;
}

.intensity-badge {
  padding: 3px 10px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 600;
  background: #f3f4f6;
  color: #6b7280;
}

.intensity-strong {
  background: #fef3c7;
  color: #92400e;
}

.result-text {
  color: #374151;
  line-height: 1.6;
  margin-bottom: 8px;
  font-size: 14px;
}

.result-meta {
  font-size: 12px;
  color: #9ca3af;
}
</style>