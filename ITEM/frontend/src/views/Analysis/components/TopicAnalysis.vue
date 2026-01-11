<template>
  <div class="topic-analysis">
    <h2>主题建模分析</h2>

    <div v-if="!data?.topics || data.topics.length === 0" class="empty">
      <p>{{ data?.message || '暂无主题数据' }}</p>
    </div>

    <div v-else>
      <div class="model-info">
        <div class="info-item">
          <span class="label">主题数量:</span>
          <span class="value">{{ data.n_topics }}</span>
        </div>
        <div class="info-item">
          <span class="label">困惑度:</span>
          <span class="value">{{ data.perplexity?.toFixed(2) }}</span>
        </div>
      </div>

      <div class="topics-grid">
        <div 
          v-for="topic in data.topics" 
          :key="topic.topic_id"
          class="topic-card"
        >
          <div class="topic-header">
            <h3>{{ topic.topic_name }}</h3>
            <span class="coherence">
              一致性: {{ topic.coherence?.toFixed(3) }}
            </span>
          </div>

          <div class="keywords-cloud">
            <div 
              v-for="(kw, index) in topic.keywords" 
              :key="index"
              class="keyword"
              :style="{ 
                fontSize: `${12 + (1 - index / topic.keywords.length) * 6}px`,
                opacity: 1 - (index / topic.keywords.length) * 0.5
              }"
            >
              {{ kw.word }}
            </div>
          </div>

          <div class="keyword-weights">
            <div 
              v-for="(kw, index) in topic.keywords.slice(0, 5)" 
              :key="index"
              class="weight-bar"
            >
              <span class="kw-word">{{ kw.word }}</span>
              <div class="bar-bg">
                <div 
                  class="bar-fill" 
                  :style="{ width: `${(kw.weight / topic.keywords[0].weight) * 100}%` }"
                ></div>
              </div>
              <span class="kw-weight">{{ kw.weight.toFixed(3) }}</span>
            </div>
          </div>
        </div>
      </div>

      <div v-if="data.doc_topic_distribution" class="distribution-section">
        <h3>📊 文档主题分布</h3>
        <div class="distribution-bars">
          <div 
            v-for="(count, key) in data.doc_topic_distribution" 
            :key="key"
            class="dist-item"
          >
            <span class="dist-label">{{ key.replace('topic_', '主题 ') }}</span>
            <div class="dist-bar-bg">
              <div 
                class="dist-bar-fill" 
                :style="{ width: `${(count / totalDocs) * 100}%` }"
              ></div>
            </div>
            <span class="dist-count">{{ count }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  data: {
    type: Object,
    default: () => ({})
  }
})

const totalDocs = computed(() => {
  if (!props.data?.doc_topic_distribution) return 1
  return Object.values(props.data.doc_topic_distribution).reduce((a, b) => a + b, 0)
})
</script>

<style scoped>
.topic-analysis h2 {
  font-size: 24px;
  margin-bottom: 20px;
  color: #1a1a1a;
}

.empty {
  text-align: center;
  padding: 60px 20px;
  color: #6b7280;
}

.model-info {
  display: flex;
  gap: 30px;
  margin-bottom: 25px;
  padding: 15px;
  background: #f0f9ff;
  border-radius: 8px;
  border-left: 4px solid #3b82f6;
}

.info-item {
  display: flex;
  gap: 10px;
}

.info-item .label {
  color: #6b7280;
  font-size: 14px;
}

.info-item .value {
  font-weight: 700;
  color: #1f2937;
}

.topics-grid {
  display: grid;
  gap: 20px;
  margin-bottom: 30px;
}

.topic-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 25px;
  border-radius: 12px;
  color: white;
}

.topic-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.topic-header h3 {
  font-size: 20px;
  margin: 0;
}

.coherence {
  font-size: 12px;
  background: rgba(255,255,255,0.2);
  padding: 4px 12px;
  border-radius: 12px;
}

.keywords-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 20px;
  padding: 15px;
  background: rgba(255,255,255,0.1);
  border-radius: 8px;
}

.keyword {
  font-weight: 500;
  transition: transform 0.2s;
}

.keyword:hover {
  transform: scale(1.1);
}

.keyword-weights {
  display: grid;
  gap: 8px;
}

.weight-bar {
  display: grid;
  grid-template-columns: 100px 1fr 60px;
  align-items: center;
  gap: 10px;
}

.kw-word {
  font-size: 14px;
  font-weight: 500;
}

.bar-bg {
  height: 6px;
  background: rgba(255,255,255,0.2);
  border-radius: 3px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  background: white;
  transition: width 0.3s;
}

.kw-weight {
  font-size: 12px;
  text-align: right;
}

.distribution-section {
  background: #f9fafb;
  padding: 20px;
  border-radius: 10px;
}

.distribution-section h3 {
  font-size: 18px;
  margin-bottom: 15px;
  color: #374151;
}

.distribution-bars {
  display: grid;
  gap: 12px;
}

.dist-item {
  display: grid;
  grid-template-columns: 100px 1fr 60px;
  align-items: center;
  gap: 10px;
}

.dist-label {
  font-weight: 500;
  color: #4b5563;
}

.dist-bar-bg {
  height: 24px;
  background: #e5e7eb;
  border-radius: 4px;
  overflow: hidden;
}

.dist-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #8b5cf6, #ec4899);
  transition: width 0.3s;
}

.dist-count {
  text-align: right;
  font-weight: 600;
  color: #8b5cf6;
}
</style>
