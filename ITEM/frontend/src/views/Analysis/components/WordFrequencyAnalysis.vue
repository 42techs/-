<template>
  <div class="word-frequency-analysis">
    <h2>📊 词频分析</h2>
    
    <div class="stats-grid">
      <div class="stat-box">
        <div class="stat-label">总词数</div>
        <div class="stat-value">{{ data?.total_words?.toLocaleString() || 0 }}</div>
      </div>
      <div class="stat-box">
        <div class="stat-label">唯一词数</div>
        <div class="stat-value">{{ data?.unique_words?.toLocaleString() || 0 }}</div>
      </div>
      <div class="stat-box">
        <div class="stat-label">词汇多样性</div>
        <div class="stat-value">{{ data?.vocabulary_diversity || 0 }}</div>
      </div>
    </div>

    <div class="analysis-sections">
      <!-- 高频词 -->
      <section class="section">
        <h3>🔤 高频词 TOP 20</h3>
        <div class="word-list">
          <div 
            v-for="(item, index) in data?.word_frequency?.slice(0, 20)" 
            :key="index"
            class="word-item"
          >
            <span class="rank">{{ index + 1 }}</span>
            <span class="word">{{ item.word }}</span>
            <div class="bar-container">
              <div 
                class="bar" 
                :style="{ width: `${(item.count / maxCount) * 100}%` }"
              ></div>
            </div>
            <span class="count">{{ item.count }}</span>
          </div>
        </div>
      </section>

      <!-- TF-IDF 关键词 -->
      <section class="section">
        <h3>🎯 TF-IDF 关键词</h3>
        <div class="keyword-tags">
          <div 
            v-for="(item, index) in data?.keywords_tfidf?.slice(0, 15)" 
            :key="index"
            class="keyword-tag"
            :style="{ fontSize: `${12 + item.weight * 8}px` }"
          >
            {{ item.word }}
            <span class="weight">{{ item.weight.toFixed(3) }}</span>
          </div>
        </div>
      </section>

      <!-- TextRank 关键词 -->
      <section class="section">
        <h3>⭐ TextRank 关键词</h3>
        <div class="keyword-tags">
          <div 
            v-for="(item, index) in data?.keywords_textrank?.slice(0, 15)" 
            :key="index"
            class="keyword-tag textrank"
            :style="{ fontSize: `${12 + item.weight * 8}px` }"
          >
            {{ item.word }}
            <span class="weight">{{ item.weight.toFixed(3) }}</span>
          </div>
        </div>
      </section>
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

const maxCount = computed(() => {
  const words = props.data?.word_frequency || []
  return words.length > 0 ? words[0].count : 1
})
</script>

<style scoped>
.word-frequency-analysis h2 {
  font-size: 24px;
  margin-bottom: 20px;
  color: #1a1a1a;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 30px;
}

.stat-box {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  border-radius: 10px;
  color: white;
}

.stat-label {
  font-size: 14px;
  opacity: 0.9;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
}

.analysis-sections {
  display: grid;
  gap: 25px;
}

.section {
  background: #f9fafb;
  padding: 20px;
  border-radius: 10px;
}

.section h3 {
  font-size: 18px;
  margin-bottom: 15px;
  color: #374151;
}

.word-list {
  display: grid;
  gap: 10px;
}

.word-item {
  display: grid;
  grid-template-columns: 40px 120px 1fr 80px;
  align-items: center;
  gap: 10px;
  padding: 10px;
  background: white;
  border-radius: 6px;
}

.rank {
  text-align: center;
  font-weight: 700;
  color: #6b7280;
}

.word {
  font-weight: 500;
  color: #1f2937;
}

.bar-container {
  background: #e5e7eb;
  height: 8px;
  border-radius: 4px;
  overflow: hidden;
}

.bar {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6, #8b5cf6);
  transition: width 0.3s;
}

.count {
  text-align: right;
  font-weight: 600;
  color: #3b82f6;
}

.keyword-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.keyword-tag {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 8px 16px;
  background: white;
  border: 2px solid #3b82f6;
  border-radius: 20px;
  color: #3b82f6;
  font-weight: 500;
  transition: all 0.2s;
}

.keyword-tag:hover {
  background: #3b82f6;
  color: white;
}

.keyword-tag.textrank {
  border-color: #8b5cf6;
  color: #8b5cf6;
}

.keyword-tag.textrank:hover {
  background: #8b5cf6;
  color: white;
}

.weight {
  font-size: 10px;
  opacity: 0.7;
}
</style>