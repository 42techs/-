<template>
  <div class="hotspot-analysis">
    <h2>🔥 热点分析</h2>

    <div v-if="!data?.trending_hashtags" class="empty">
      <p>暂无热点数据</p>
    </div>

    <div v-else>
      <!-- 传播统计 -->
      <div class="propagation-stats" v-if="data.propagation_analysis">
        <div class="stat-card total">
          <div class="stat-icon">🎯</div>
          <div class="stat-content">
            <div class="stat-label">总互动量</div>
            <div class="stat-value">
              {{ data.propagation_analysis.total_engagement?.toLocaleString() || 0 }}
            </div>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon">🔄</div>
          <div class="stat-content">
            <div class="stat-label">转发</div>
            <div class="stat-value">
              {{ data.propagation_analysis.total_reposts?.toLocaleString() || 0 }}
            </div>
            <div class="stat-avg">
              平均: {{ data.propagation_analysis.avg_reposts || 0 }}
            </div>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon">💬</div>
          <div class="stat-content">
            <div class="stat-label">评论</div>
            <div class="stat-value">
              {{ data.propagation_analysis.total_comments?.toLocaleString() || 0 }}
            </div>
            <div class="stat-avg">
              平均: {{ data.propagation_analysis.avg_comments || 0 }}
            </div>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon">❤️</div>
          <div class="stat-content">
            <div class="stat-label">点赞</div>
            <div class="stat-value">
              {{ data.propagation_analysis.total_likes?.toLocaleString() || 0 }}
            </div>
            <div class="stat-avg">
              平均: {{ data.propagation_analysis.avg_likes || 0 }}
            </div>
          </div>
        </div>
      </div>

      <!-- 热门话题标签 -->
      <section class="section">
        <h3>🏷️ 热门话题标签 TOP 10</h3>
        <div class="hashtag-list">
          <div 
            v-for="(item, index) in data.trending_hashtags?.slice(0, 10)" 
            :key="index"
            class="hashtag-item"
          >
            <span class="rank">{{ index + 1 }}</span>
            <span class="hashtag">#{{ item.hashtag }}#</span>
            <div class="bar-container">
              <div 
                class="bar" 
                :style="{ width: `${(item.count / maxHashtagCount) * 100}%` }"
              ></div>
            </div>
            <span class="count">{{ item.count.toLocaleString() }}</span>
          </div>
        </div>
      </section>

      <!-- 热门@用户 -->
      <section class="section">
        <h3>👥 热门@用户 TOP 10</h3>
        <div class="mention-list">
          <div 
            v-for="(item, index) in data.trending_mentions?.slice(0, 10)" 
            :key="index"
            class="mention-item"
          >
            <span class="rank">{{ index + 1 }}</span>
            <span class="mention">@{{ item.mention }}</span>
            <div class="bar-container">
              <div 
                class="bar" 
                :style="{ width: `${(item.count / maxMentionCount) * 100}%` }"
              ></div>
            </div>
            <span class="count">{{ item.count.toLocaleString() }}</span>
          </div>
        </div>
      </section>

      <!-- 热门内容 -->
      <section class="section">
        <h3>📝 热门内容 TOP 5</h3>
        <div class="hot-contents">
          <div 
            v-for="(item, index) in data.hot_contents?.slice(0, 5)" 
            :key="index"
            class="content-card"
          >
            <div class="content-header">
              <span class="content-rank">NO.{{ index + 1 }}</span>
              <span class="heat-score">🔥 {{ item.heat_score?.toLocaleString() }}</span>
            </div>
            <p class="content-text">{{ item.text_preview }}</p>
            <div class="content-stats">
              <span class="stat-item">
                <span class="icon">🔄</span>
                {{ item.reposts?.toLocaleString() || 0 }}
              </span>
              <span class="stat-item">
                <span class="icon">💬</span>
                {{ item.comments?.toLocaleString() || 0 }}
              </span>
              <span class="stat-item">
                <span class="icon">❤️</span>
                {{ item.likes?.toLocaleString() || 0 }}
              </span>
            </div>
            <div class="content-time">
              {{ formatTime(item.created_at) }}
            </div>
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

const maxHashtagCount = computed(() => {
  const items = props.data?.trending_hashtags || []
  return items.length > 0 ? items[0].count : 1
})

const maxMentionCount = computed(() => {
  const items = props.data?.trending_mentions || []
  return items.length > 0 ? items[0].count : 1
})

const formatTime = (timeStr) => {
  if (!timeStr) return '-'
  return new Date(timeStr).toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<style scoped>
.hotspot-analysis h2 {
  font-size: 24px;
  margin-bottom: 20px;
  color: #1a1a1a;
}

.empty {
  text-align: center;
  padding: 60px 20px;
  color: #6b7280;
}

.propagation-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 30px;
}

.stat-card {
  display: flex;
  gap: 12px;
  background: white;
  padding: 15px;
  border-radius: 10px;
  border: 2px solid #e5e7eb;
}

.stat-card.total {
  background: linear-gradient(135deg, #f59e0b 0%, #ea580c 100%);
  color: white;
  border: none;
}

.stat-icon {
  font-size: 28px;
}

.stat-content {
  flex: 1;
}

.stat-label {
  font-size: 12px;
  opacity: 0.8;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 20px;
  font-weight: 700;
}

.stat-avg {
  font-size: 11px;
  opacity: 0.7;
  margin-top: 2px;
}

.section {
  background: #f9fafb;
  padding: 20px;
  border-radius: 10px;
  margin-bottom: 20px;
}

.section h3 {
  font-size: 18px;
  margin-bottom: 15px;
  color: #374151;
}

.hashtag-list,
.mention-list {
  display: grid;
  gap: 10px;
}

.hashtag-item,
.mention-item {
  display: grid;
  grid-template-columns: 40px 150px 1fr 100px;
  align-items: center;
  gap: 10px;
  padding: 12px;
  background: white;
  border-radius: 6px;
}

.rank {
  text-align: center;
  font-weight: 700;
  color: #6b7280;
  font-size: 16px;
}

.hashtag,
.mention {
  font-weight: 600;
  color: #3b82f6;
}

.bar-container {
  background: #e5e7eb;
  height: 10px;
  border-radius: 5px;
  overflow: hidden;
}

.bar {
  height: 100%;
  background: linear-gradient(90deg, #f59e0b, #ea580c);
  transition: width 0.3s;
}

.count {
  text-align: right;
  font-weight: 600;
  color: #f59e0b;
  font-size: 15px;
}

.hot-contents {
  display: grid;
  gap: 15px;
}

.content-card {
  background: white;
  padding: 20px;
  border-radius: 10px;
  border-left: 4px solid #f59e0b;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.content-rank {
  font-weight: 700;
  color: #f59e0b;
  font-size: 14px;
}

.heat-score {
  font-weight: 600;
  color: #dc2626;
  font-size: 15px;
}

.content-text {
  color: #374151;
  line-height: 1.6;
  margin-bottom: 12px;
  font-size: 15px;
}

.content-stats {
  display: flex;
  gap: 20px;
  margin-bottom: 10px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 14px;
  color: #6b7280;
}

.stat-item .icon {
  font-size: 16px;
}

.content-time {
  font-size: 12px;
  color: #9ca3af;
}
</style>