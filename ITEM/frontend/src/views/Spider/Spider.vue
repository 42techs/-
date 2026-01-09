<template>
  <div class="spider-page">
    <div class="page-header">
      <div class="header-content">
        <div class="header-icon">🕷️</div>
        <div>
          <h1 class="page-title">爬虫控制台</h1>
          <p class="page-subtitle">智能数据采集与管理平台</p>
        </div>
      </div>
      <div class="header-decoration">
        <div class="deco-circle"></div>
        <div class="deco-circle"></div>
      </div>
    </div>

    <div class="content-wrapper">
      <!-- 控制面板 -->
      <section class="card control-card">
        <div class="card-header">
          <div class="header-left">
            <div class="icon-badge">⚡</div>
            <h3 class="card-title">任务控制</h3>
          </div>
          <div v-if="running" class="status-indicator running">
            <span class="pulse-dot"></span>
            <span>运行中</span>
          </div>
        </div>

        <div class="card-body">
          <button 
            :disabled="running" 
            @click="startSpider"
            class="action-btn"
            :class="{ 'btn-disabled': running }"
          >
            <span class="btn-icon">🚀</span>
            <span class="btn-text">{{ running ? '任务进行中...' : '启动爬虫任务' }}</span>
          </button>

          <div class="info-box">
            <span class="info-icon">💡</span>
            <p>点击按钮将创建新的爬虫任务,系统会自动返回任务ID并开始实时监控任务状态</p>
          </div>
        </div>
      </section>

      <!-- 任务状态 -->
      <section v-if="taskId" class="card status-card">
        <div class="card-header">
          <div class="header-left">
            <div class="icon-badge gradient-blue">📊</div>
            <h3 class="card-title">任务状态</h3>
          </div>
        </div>

        <div class="card-body">
          <div class="status-grid">
            <div class="status-item">
              <span class="status-label">任务ID</span>
              <span class="status-value monospace">{{ taskId }}</span>
            </div>

            <div class="status-item">
              <span class="status-label">当前状态</span>
              <span class="status-badge" :class="statusClass">
                <span class="badge-dot"></span>
                {{ statusText }}
              </span>
            </div>

            <div v-if="error" class="status-item full-width">
              <span class="status-label">错误信息</span>
              <div class="error-box">
                <span class="error-icon">⚠️</span>
                <span class="error-text">{{ error }}</span>
              </div>
            </div>
          </div>

          <!-- 进度条 -->
          <div v-if="running" class="progress-section">
            <div class="progress-header">
              <span class="progress-label">任务进度</span>
              <span class="progress-percentage">{{ progress }}%</span>
            </div>
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: progress + '%' }"></div>
            </div>
          </div>
        </div>
      </section>

      <!-- 结果展示 -->
      <section v-if="result" class="card result-card">
        <div class="card-header">
          <div class="header-left">
            <div class="icon-badge gradient-green">✅</div>
            <h3 class="card-title">执行结果</h3>
          </div>
          <button @click="copyResult" class="copy-btn">
            <span>📋</span>
            <span>复制</span>
          </button>
        </div>

        <div class="card-body">
          <div class="result-container">
            <pre class="result-content">{{ result }}</pre>
          </div>
        </div>
      </section>

      <!-- 历史记录 -->
      <section class="card history-card">
        <div class="card-header">
          <div class="header-left">
            <div class="icon-badge gradient-purple">📜</div>
            <h3 class="card-title">任务历史</h3>
          </div>
        </div>

        <div class="card-body">
          <div class="empty-state">
            <div class="empty-icon">🔭</div>
            <p class="empty-text">暂无历史记录</p>
            <p class="empty-hint">启动任务后将在此处显示历史记录</p>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onBeforeUnmount } from "vue";
import { runSpider, spiderStatus, spiderResult } from "@/api/spider";

const taskId = ref("");
const status = ref("");
const error = ref("");
const result = ref("");
const running = ref(false);
const progress = ref(0);

let timer = null;
let progressTimer = null;

const statusClass = computed(() => {
  const statusMap = {
    'PENDING': 'status-pending',
    'RUNNING': 'status-running',
    'SUCCESS': 'status-success',
    'FAILED': 'status-failed'
  };
  return statusMap[status.value] || 'status-pending';
});

const statusText = computed(() => {
  const textMap = {
    'PENDING': '等待中',
    'RUNNING': '执行中',
    'SUCCESS': '已完成',
    'FAILED': '失败'
  };
  return textMap[status.value] || '未知';
});

// 修复:重命名函数以匹配按钮绑定
async function startSpider() {
  error.value = "";
  result.value = "";
  status.value = "";
  progress.value = 0;

  try {
    const resp = await runSpider();
    taskId.value = resp.task_id;
    status.value = "PENDING";
    running.value = true;

    // 模拟进度
    progressTimer = setInterval(() => {
      if (progress.value < 90) {
        progress.value += Math.random() * 10;
      }
    }, 800);

    // 轮询状态
    timer = setInterval(async () => {
      try {
        const s = await spiderStatus(taskId.value);
        status.value = s.data.status;
        error.value = s.data.error || "";

        if (status.value === "SUCCESS") {
          clearInterval(timer);
          clearInterval(progressTimer);
          timer = null;
          progressTimer = null;
          progress.value = 100;
          
          const r = await spiderResult(taskId.value);
          result.value = JSON.stringify(r.data, null, 2);
          running.value = false;
        }

        if (status.value === "FAILED") {
          clearInterval(timer);
          clearInterval(progressTimer);
          timer = null;
          progressTimer = null;
          running.value = false;
        }
      } catch (e) {
        error.value = e?.message || "轮询失败";
        clearInterval(timer);
        clearInterval(progressTimer);
        timer = null;
        progressTimer = null;
        running.value = false;
      }
    }, 1500);
  } catch (e) {
    error.value = e?.message || "启动失败";
    running.value = false;
  }
}

function copyResult() {
  if (navigator.clipboard) {
    navigator.clipboard.writeText(result.value);
    // 可以添加提示消息
    alert('复制成功!');
  }
}

onBeforeUnmount(() => {
  if (timer) clearInterval(timer);
  if (progressTimer) clearInterval(progressTimer);
});
</script>

<style scoped>
.spider-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea15 0%, #764ba215 50%, #f5576c15 100%);
  padding: 32px 24px;
}

.page-header {
  max-width: 1200px;
  margin: 0 auto 40px;
  position: relative;
  overflow: hidden;
  background: white;
  border-radius: 24px;
  padding: 40px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.header-content {
  display: flex;
  align-items: center;
  gap: 24px;
  position: relative;
  z-index: 1;
}

.header-icon {
  width: 80px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 3rem;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-radius: 20px;
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.page-title {
  font-size: 2.5rem;
  font-weight: 800;
  background: linear-gradient(135deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0 0 8px 0;
}

.page-subtitle {
  font-size: 1.125rem;
  color: #718096;
  margin: 0;
}

.header-decoration {
  position: absolute;
  top: 0;
  right: 0;
  width: 200px;
  height: 200px;
  pointer-events: none;
}

.deco-circle {
  position: absolute;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
}

.deco-circle:nth-child(1) {
  width: 150px;
  height: 150px;
  top: -75px;
  right: -75px;
  animation: pulse 4s ease-in-out infinite;
}

.deco-circle:nth-child(2) {
  width: 100px;
  height: 100px;
  top: -25px;
  right: 20px;
  animation: pulse 4s ease-in-out infinite 1s;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); opacity: 0.3; }
  50% { transform: scale(1.1); opacity: 0.5; }
}

.content-wrapper {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  gap: 24px;
}

/* 卡片样式 */
.card {
  background: white;
  border-radius: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.card:hover {
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  transform: translateY(-4px);
}

.card-header {
  padding: 28px 32px;
  border-bottom: 1px solid #f1f5f9;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.icon-badge {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.75rem;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.icon-badge.gradient-blue {
  background: linear-gradient(135deg, #4facfe, #00f2fe);
}

.icon-badge.gradient-green {
  background: linear-gradient(135deg, #43e97b, #38f9d7);
}

.icon-badge.gradient-purple {
  background: linear-gradient(135deg, #a8edea, #fed6e3);
}

.card-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1a202c;
  margin: 0;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border-radius: 50px;
  font-size: 0.875rem;
  font-weight: 600;
}

.pulse-dot {
  width: 8px;
  height: 8px;
  background: white;
  border-radius: 50%;
  animation: pulse-dot 2s ease-in-out infinite;
}

@keyframes pulse-dot {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(1.3); }
}

.card-body {
  padding: 32px;
}

/* 操作按钮 */
.action-btn {
  width: 100%;
  padding: 20px 32px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border: none;
  border-radius: 16px;
  font-size: 1.125rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
  position: relative;
  overflow: hidden;
}

.action-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: left 0.5s ease;
}

.action-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
}

.action-btn:hover:not(:disabled)::before {
  left: 100%;
}

.action-btn:disabled,
.action-btn.btn-disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.btn-icon {
  font-size: 1.5rem;
}

.info-box {
  display: flex;
  gap: 12px;
  padding: 16px 20px;
  background: linear-gradient(135deg, #f0f4ff, #e8eeff);
  border-left: 4px solid #667eea;
  border-radius: 12px;
  margin-top: 20px;
}

.info-icon {
  font-size: 1.25rem;
  flex-shrink: 0;
}

.info-box p {
  margin: 0;
  color: #4a5568;
  font-size: 0.9375rem;
  line-height: 1.6;
}

/* 状态网格 */
.status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.status-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.status-item.full-width {
  grid-column: 1 / -1;
}

.status-label {
  font-size: 0.875rem;
  color: #718096;
  font-weight: 600;
}

.status-value {
  font-size: 1.125rem;
  color: #1a202c;
  font-weight: 600;
}

.status-value.monospace {
  font-family: 'Monaco', 'Consolas', monospace;
  background: #f7fafc;
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 0.9375rem;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: 50px;
  font-size: 0.9375rem;
  font-weight: 600;
  width: fit-content;
}

.status-badge.status-pending {
  background: linear-gradient(135deg, #fbbf24, #f59e0b);
  color: white;
}

.status-badge.status-running {
  background: linear-gradient(135deg, #4facfe, #00f2fe);
  color: white;
}

.status-badge.status-success {
  background: linear-gradient(135deg, #48bb78, #38a169);
  color: white;
}

.status-badge.status-failed {
  background: linear-gradient(135deg, #f56565, #e53e3e);
  color: white;
}

.badge-dot {
  width: 6px;
  height: 6px;
  background: white;
  border-radius: 50%;
  animation: pulse-dot 2s ease-in-out infinite;
}

.error-box {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  background: linear-gradient(135deg, #fed7d7, #feb2b2);
  border-left: 4px solid #f56565;
  border-radius: 12px;
}

.error-icon {
  font-size: 1.25rem;
}

.error-text {
  color: #742a2a;
  font-weight: 500;
}

/* 进度条 */
.progress-section {
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #f1f5f9;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.progress-label {
  font-size: 0.875rem;
  color: #718096;
  font-weight: 600;
}

.progress-percentage {
  font-size: 1.125rem;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.progress-bar {
  height: 12px;
  background: #e2e8f0;
  border-radius: 6px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea, #764ba2);
  border-radius: 6px;
  transition: width 0.5s ease;
  position: relative;
  overflow: hidden;
}

.progress-fill::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  animation: shimmer 2s infinite;
}

@keyframes shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

/* 结果容器 */
.result-container {
  background: #1a202c;
  border-radius: 12px;
  padding: 24px;
  overflow: auto;
  max-height: 500px;
}

.result-content {
  margin: 0;
  color: #48bb78;
  font-family: 'Monaco', 'Consolas', monospace;
  font-size: 0.875rem;
  line-height: 1.8;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.copy-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.copy-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 60px 20px;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 16px;
  opacity: 0.5;
}

.empty-text {
  font-size: 1.125rem;
  color: #2d3748;
  font-weight: 600;
  margin: 0 0 8px 0;
}

.empty-hint {
  font-size: 0.9375rem;
  color: #a0aec0;
  margin: 0;
}

/* 响应式 */
@media (max-width: 768px) {
  .spider-page {
    padding: 20px 16px;
  }

  .page-header {
    padding: 28px 24px;
    margin-bottom: 24px;
  }

  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .page-title {
    font-size: 2rem;
  }

  .card-header {
    padding: 20px 24px;
  }

  .card-body {
    padding: 24px;
  }

  .status-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .header-icon {
    width: 60px;
    height: 60px;
    font-size: 2rem;
  }

  .page-title {
    font-size: 1.75rem;
  }

  .page-subtitle {
    font-size: 1rem;
  }

  .action-btn {
    padding: 16px 24px;
    font-size: 1rem;
  }

  .btn-text {
    font-size: 0.9375rem;
  }
}
</style>