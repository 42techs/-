<template>
  <div class="layout">
    <Navbar />

    <main class="main">
      <!-- 欢迎区 -->
      <section class="welcome">
        <h1>欢迎回来，<span>{{ userName }}</span></h1>
        <p>数据驱动决策，洞察趋势</p>
      </section>

      <!-- 统计卡片 -->
      <div class="stats">
        <div class="stat">
          <div class="stat-icon">📊</div>
          <div>
            <div class="stat-label">今日分析</div>
            <div class="stat-value">128</div>
            <div class="stat-change positive">+12%</div>
          </div>
        </div>

        <div class="stat">
          <div class="stat-icon">🕷️</div>
          <div>
            <div class="stat-label">爬虫任务</div>
            <div class="stat-value">45</div>
            <div class="stat-change positive">+8%</div>
          </div>
        </div>

        <div class="stat">
          <div class="stat-icon">⚡</div>
          <div>
            <div class="stat-label">处理速度</div>
            <div class="stat-value">2.3s</div>
            <div class="stat-change">优秀</div>
          </div>
        </div>
      </div>

      <!-- 主要内容 -->
      <div class="grid">
        <!-- 个人资料 -->
        <section class="card">
          <div class="card-header">
            <h3>👤 个人资料</h3>
            <span class="badge">已验证</span>
          </div>
          <div class="card-body">
            <div class="info">
              <span class="label">用户ID</span>
              <span class="value">{{ user.id || 'N/A' }}</span>
            </div>
            <div class="info">
              <span class="label">用户名</span>
              <span class="value">{{ user.username || 'N/A' }}</span>
            </div>
            <div class="info">
              <span class="label">邮箱</span>
              <span class="value">{{ user.email || 'N/A' }}</span>
            </div>
          </div>
        </section>

        <!-- 快速操作 -->
        <section class="card">
          <div class="card-header">
            <h3>⚡ 快速操作</h3>
          </div>
          <div class="card-body">
            <button class="action" disabled>
              <span class="action-icon">📈</span>
              <div>
                <div class="action-title">舆情分析</div>
                <div class="action-desc">实时监控热点话题</div>
              </div>
              <span class="tag">开发中</span>
            </button>

            <button class="action" disabled>
              <span class="action-icon">🕸️</span>
              <div>
                <div class="action-title">爬虫管理</div>
                <div class="action-desc">智能数据采集</div>
              </div>
              <span class="tag">即将上线</span>
            </button>
          </div>
        </section>
      </div>

      <!-- 最近活动 -->
      <section class="card activity">
        <div class="card-header">
          <h3>📋 最近活动</h3>
        </div>
        <div class="timeline">
          <div class="timeline-item">
            <div class="timeline-dot"></div>
            <div>
              <div class="timeline-title">账户登录</div>
              <div class="timeline-desc">成功登录系统</div>
              <div class="timeline-time">刚刚</div>
            </div>
          </div>
          <div class="timeline-item">
            <div class="timeline-dot"></div>
            <div>
              <div class="timeline-title">数据更新</div>
              <div class="timeline-desc">同步最新用户信息</div>
              <div class="timeline-time">5分钟前</div>
            </div>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { computed } from "vue";
import { useAuthStore } from "@/stores/auth";
import Navbar from "@/components/Navbar.vue";

// 获取用户信息
const authStore = useAuthStore();
const user = computed(() => authStore.user || {});
// 处理用户名默认值
const userName = computed(() => user.value.username || "用户");
</script>

<style scoped>
.layout {
  min-height: 100vh;
  background: #f8fafc;
}

.main {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 24px;
}

/* 欢迎区样式 */
.welcome {
  margin-bottom: 40px;
}

.welcome h1 {
  font-size: 2.5rem;
  font-weight: 700;
  color: #1a202c;
  margin-bottom: 8px;
}

.welcome h1 span {
  background: linear-gradient(135deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.welcome p {
  color: #718096;
  font-size: 1.125rem;
  margin: 0;
}

/* 统计卡片样式 */
.stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
}

.stat {
  background: white;
  padding: 24px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: all 0.2s ease;
}

.stat:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08);
}

.stat-icon {
  font-size: 2rem;
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
  border-radius: 12px;
}

.stat-label {
  font-size: 0.875rem;
  color: #718096;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 1.875rem;
  font-weight: 700;
  color: #1a202c;
}

.stat-change {
  font-size: 0.875rem;
  color: #718096;
}

.stat-change.positive {
  color: #48bb78;
}

/* 网格布局 */
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 24px;
  margin-bottom: 24px;
}

/* 卡片通用样式 */
.card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  overflow: hidden;
  transition: all 0.2s ease;
}

.card:hover {
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08);
}

.card.activity {
  grid-column: 1 / -1;
}

.card-header {
  padding: 24px;
  border-bottom: 1px solid #f1f5f9;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1a202c;
  margin: 0;
}

.badge {
  padding: 4px 12px;
  background: linear-gradient(135deg, #48bb78, #38a169);
  color: white;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
}

.card-body {
  padding: 24px;
}

/* 信息项样式 */
.info {
  display: flex;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid #f7fafc;
}

.info:last-child {
  border-bottom: none;
}

.label {
  font-size: 0.875rem;
  color: #718096;
}

.value {
  font-weight: 600;
  color: #1a202c;
}

/* 操作按钮样式 */
.action {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: #f8fafc;
  border: 2px solid transparent;
  border-radius: 12px;
  cursor: not-allowed;
  transition: all 0.2s ease;
  margin-bottom: 12px;
}

.action:last-child {
  margin-bottom: 0;
}

.action-icon {
  font-size: 1.75rem;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04);
}

.action-title {
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 2px;
}

.action-desc {
  font-size: 0.875rem;
  color: #718096;
}

.tag {
  margin-left: auto;
  padding: 4px 12px;
  background: linear-gradient(135deg, #fbbf24, #f59e0b);
  color: white;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
}

/* 时间线样式 */
.timeline {
  padding: 24px;
}

.timeline-item {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
  position: relative;
}

.timeline-item:last-child {
  margin-bottom: 0;
}

.timeline-item:not(:last-child)::after {
  content: "";
  position: absolute;
  left: 11px;
  top: 32px;
  bottom: -24px;
  width: 2px;
  background: #e2e8f0;
}

.timeline-dot {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea, #764ba2);
  flex-shrink: 0;
  position: relative;
  z-index: 1;
}

.timeline-title {
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 2px;
}

.timeline-desc {
  font-size: 0.875rem;
  color: #718096;
  margin-bottom: 4px;
}

.timeline-time {
  font-size: 0.75rem;
  color: #a0aec0;
}

/* 响应式优化 */
@media (max-width: 768px) {
  .main {
    padding: 24px 16px;
  }

  .welcome h1 {
    font-size: 2rem;
  }

  .stats {
    grid-template-columns: 1fr;
  }

  .grid {
    grid-template-columns: 1fr;
  }
}

/* 适配深色模式（可选） */
@media (prefers-color-scheme: dark) {
  .layout {
    background: #1a1a2e;
  }

  .stat,
  .card {
    background: #16213e;
  }

  .welcome h1 {
    color: #e94560;
  }

  .welcome p {
    color: #a5d8ff;
  }

  .stat-label,
  .label,
  .timeline-desc,
  .timeline-time,
  .action-desc {
    color: #a5d8ff;
  }

  .stat-value,
  .value,
  .timeline-title,
  .action-title {
    color: #ffffff;
  }

  .card-header {
    border-bottom-color: #0f3460;
  }

  .info {
    border-bottom-color: #0f3460;
  }

  .action {
    background: #0f3460;
  }

  .action-icon {
    background: #16213e;
  }

  .timeline-item:not(:last-child)::after {
    background: #0f3460;
  }
}
</style>