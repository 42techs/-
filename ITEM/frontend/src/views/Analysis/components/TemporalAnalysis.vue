<template>
  <div class="temporal-analysis">
    <h2>📈 时间序列分析</h2>

    <div v-if="!data?.daily_distribution" class="empty">
      <p>暂无时间数据</p>
    </div>

    <div v-else>
      <!-- 趋势概览 -->
      <div class="trend-overview">
        <div class="trend-card">
          <div class="trend-icon">📊</div>
          <div class="trend-content">
            <div class="trend-label">趋势方向</div>
            <div class="trend-value" :class="trendClass">
              {{ trendText }}
            </div>
          </div>
        </div>

        <div class="trend-card">
          <div class="trend-icon">📅</div>
          <div class="trend-content">
            <div class="trend-label">统计天数</div>
            <div class="trend-value">
              {{ data.trend_analysis?.total_days || 0 }} 天
            </div>
          </div>
        </div>

        <div class="trend-card">
          <div class="trend-icon">📏</div>
          <div class="trend-content">
            <div class="trend-label">日均数量</div>
            <div class="trend-value">
              {{ data.trend_analysis?.avg_daily_count?.toFixed(1) || 0 }}
            </div>
          </div>
        </div>
      </div>

      <!-- 每日分布图表 -->
      <section class="chart-section">
        <h3>每日数据分布</h3>
        <div class="simple-chart">
          <div 
            v-for="(item, index) in data.daily_distribution" 
            :key="index"
            class="chart-bar"
          >
            <div class="bar-wrapper">
              <div 
                class="bar" 
                :style="{ height: `${(item.count / maxDaily) * 100}%` }"
                :title="`${item.date}: ${item.count}`"
              ></div>
            </div>
            <div class="bar-label">{{ formatDate(item.date) }}</div>
            <div class="bar-value">{{ item.count }}</div>
          </div>
        </div>
      </section>

      <!-- 高峰时段 -->
      <section class="peak-section" v-if="data.trend_analysis?.peak_hours">
        <h3>🔥 高峰活跃时段</h3>
        <div class="peak-hours">
          <div 
            v-for="(hour, index) in data.trend_analysis.peak_hours" 
            :key="index"
            class="peak-hour"
          >
            {{ hour }}
          </div>
        </div>
      </section>

      <!-- 星期分布 -->
      <section class="weekday-section" v-if="data.weekday_distribution">
        <h3>星期活跃度分布</h3>
        <div class="weekday-bars">
          <div 
            v-for="(item, index) in data.weekday_distribution" 
            :key="index"
            class="weekday-item"
          >
            <span class="weekday-label">{{ item.weekday }}</span>
            <div class="weekday-bar-bg">
              <div 
                class="weekday-bar-fill" 
                :style="{ width: `${(item.count / maxWeekday) * 100}%` }"
              ></div>
            </div>
            <span class="weekday-count">{{ item.count }}</span>
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
    default: () => ({}),
  }
})

const maxDaily = computed(() => {
  const items = props.data?.daily_distribution || []
  return items.length > 0 ? Math.max(...items.map(i => i.count)) : 1
})

const maxWeekday = computed(() => {
  const items = props.data?.weekday_distribution || []
  return items.length > 0 ? Math.max(...items.map(i => i.count)) : 1
})

const trendText = computed(() => {
  const direction = props.data?.trend_analysis?.trend_direction
  const map = {
    'increasing': '↗️ 增长中',
    'decreasing': '↘️ 下降中',
    'stable': '→ 稳定',
  }
  return map[direction] || '-'
})

const trendClass = computed(() => {
  const direction = props.data?.trend_analysis?.trend_direction
  return {
    'increasing': 'trend-up',
    'decreasing': 'trend-down',
    'stable': 'trend-stable',
  }[direction]
})

const formatDate = (dateStr) => {
  return dateStr ? dateStr.slice(5) : ''
}
</script>

<style scoped>
.temporal-analysis h2 {
  font-size: 24px;
  margin-bottom: 20px;
  color: #1a1a1a;
}

.empty {
  text-align: center;
  padding: 60px 20px;
  color: #6b7280;
}

.trend-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 30px;
}

.trend-card {
  display: flex;
  gap: 15px;
  background: white;
  padding: 20px;
  border-radius: 10px;
  border: 2px solid #e5e7eb;
}

.trend-icon {
  font-size: 32px;
}

.trend-content {
  flex: 1;
}

.trend-label {
  font-size: 14px;
  color: #6b7280;
  margin-bottom: 5px;
}

.trend-value {
  font-size: 22px;
  font-weight: 700;
  color: #1f2937;
}

.trend-value.trend-up {
  color: #10b981;
}

.trend-value.trend-down {
  color: #ef4444;
}

.trend-value.trend-stable {
  color: #6b7280;
}

.chart-section {
  background: #f9fafb;
  padding: 20px;
  border-radius: 10px;
  margin-bottom: 20px;
}

.chart-section h3 {
  font-size: 18px;
  margin-bottom: 20px;
  color: #374151;
}

.simple-chart {
  display: flex;
  gap: 8px;
  align-items: flex-end;
  height: 250px;
  padding: 10px;
  background: white;
  border-radius: 8px;
}

.chart-bar {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
}

.bar-wrapper {
  flex: 1;
  width: 100%;
  display: flex;
  align-items: flex-end;
  justify-content: center;
}

.bar {
  width: 100%;
  max-width: 50px;  /* Increase max width if necessary */
  background: linear-gradient(to top, #3b82f6, #8b5cf6);
  border-radius: 4px 4px 0 0;
  transition: all 0.3s;
  cursor: pointer;
}

.bar:hover {
  opacity: 0.8;
}

.bar-label {
  font-size: 12px;
  color: #6b7280;
  white-space: nowrap;
  text-align: center;
}

.bar-value {
  font-size: 12px;
  font-weight: 600;
  color: #3b82f6;
}

.peak-section {
  background: #fef3c7;
  padding: 20px;
  border-radius: 10px;
  border-left: 4px solid #f59e0b;
  margin-bottom: 20px;
}

.peak-section h3 {
  font-size: 18px;
  margin-bottom: 15px;
  color: #92400e;
}

.peak-hours {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.peak-hour {
  padding: 10px 20px;
  background: white;
  border: 2px solid #f59e0b;
  border-radius: 20px;
  font-weight: 500;
  color: #92400e;
}

.weekday-section {
  background: #f9fafb;
  padding: 20px;
  border-radius: 10px;
}

.weekday-section h3 {
  font-size: 18px;
  margin-bottom: 15px;
  color: #374151;
}

.weekday-bars {
  display: grid;
  gap: 12px;
}

.weekday-item {
  display: grid;
  grid-template-columns: 100px 1fr 80px;
  align-items: center;
  gap: 15px;
}

.weekday-label {
  font-weight: 500;
  color: #4b5563;
}

.weekday-bar-bg {
  height: 24px;
  background: #e5e7eb;
  border-radius: 4px;
  overflow: hidden;
}

.weekday-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6, #06b6d4);
  transition: width 0.3s;
}

.weekday-count {
  text-align: right;
  font-weight: 600;
  color: #3b82f6;
}
</style>
