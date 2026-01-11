<template>
  <div class="spider-page">
    <Navbar />
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
      <!-- 控制面板（新增参数输入） -->
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
            @click="handleStartSpider"
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

          <!-- 全局错误提示 -->
          <div v-if="globalError" class="error-message global-error">
            <span class="error-icon">❌</span>
            <span class="error-text">{{ globalError }}</span>
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
              <span class="progress-percentage">{{ progress.toFixed(1) }}%</span>
            </div>
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: `${progress.toFixed(1)}%` }"></div>
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
          <button @click="handleCopyResult" class="copy-btn" :disabled="!result">
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
          <!-- 手动刷新按钮 -->
          <button @click="fetchTaskHistory" class="copy-btn">
            <span>🔄</span>
            <span>刷新</span>
          </button>
        </div>

        <div class="card-body">
          <div v-if="taskHistory.length === 0" class="empty-state">
            <div class="empty-icon">🔭</div>
            <p class="empty-text">暂无历史记录</p>
            <p class="empty-hint">启动任务后将在此处显示历史记录</p>
          </div>
          <div v-else class="history-list">
            <div v-for="task in taskHistory" :key="task.id || task.task_id" class="history-item">
              <div class="history-id">ID: {{ (task.id || task.task_id).slice(0, 8) }}...</div>
              <div class="history-status" :class="`status-${(task.status || '').toLowerCase()}`">
                {{ task.status === 'PENDING' ? '等待中' : task.status === 'RUNNING' ? '执行中' : task.status === 'SUCCESS' ? '已完成' : '失败' }}
              </div>
              <div class="history-time">{{ formatTime(task.created_at || task.create_time) }}</div>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onBeforeUnmount, onMounted } from "vue";
import { runSpider, spiderStatus, getSpiderTasks } from "@/api/spider";
import Navbar from "@/components/Navbar.vue";

// 新增：爬虫参数配置
const taskParams = ref({
  keyword: "",
  page: 1
});

// 状态管理
const taskId = ref(""); // 爬虫任务ID
const status = ref(""); // 任务状态(PENDING/RUNNING/SUCCESS/FAILED/PARAM_ERROR/NOT_STARTED)
const error = ref(""); // 错误信息
const result = ref(""); // 任务执行结果
const running = ref(false); // 是否正在运行
const progress = ref(0); // 任务进度(0-100)
const globalError = ref(""); // 全局错误（404/500等）
const taskHistory = ref([]); // 任务历史列表

// 定时器管理
let statusTimer = null; // 状态轮询定时器
let progressTimer = null; // 进度模拟定时器
let historyTimer = null; // 任务历史轮询定时器

// 计算属性 - 状态样式映射
const statusClass = computed(() => {
  const statusMap = {
    PENDING: "status-pending",
    RUNNING: "status-running",
    SUCCESS: "status-success",
    FAILED: "status-failed",
    PARAM_ERROR: "status-failed",
    NOT_STARTED: "status-pending"
  };
  return statusMap[status.value] || "status-pending";
});

// 计算属性 - 状态文本映射（中文展示）
const statusText = computed(() => {
  const textMap = {
    PENDING: "等待中",
    RUNNING: "执行中",
    SUCCESS: "已完成",
    FAILED: "失败",
    PARAM_ERROR: "参数错误",
    NOT_STARTED: "未启动"
  };
  return textMap[status.value] || "未知";
});

/**
 * 格式化时间显示
 * @param {string} timeStr - ISO格式时间字符串
 * @returns {string} 格式化后的时间
 */
function formatTime(timeStr) {
  if (!timeStr) return "未知时间";
  try {
    const date = new Date(timeStr);
    return date.toLocaleString("zh-CN", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });
  } catch (e) {
    return timeStr.slice(0, 19).replace("T", " ");
  }
}

/**
 * 启动爬虫任务
 */
async function handleStartSpider() {
  // 防止重复点击
  if (running.value) return;

  // 重置状态
  error.value = "";
  result.value = "";
  status.value = "";
  progress.value = 0;
  globalError.value = "";

  try {
    // 调用启动接口（不再传递关键词/页码）
    const resp = await runSpider();
    
    // 适配后端返回的成功码 code: 0
    if (resp.code !== 0) {
      throw new Error(resp.message || "启动爬虫任务失败");
    }

    // 从resp.data中获取task_id（适配后端返回字段）
    const taskIdVal = resp.data?.task_id || resp.data?.id;
    if (!taskIdVal) {
      throw new Error("未获取到有效任务ID");
    }

    // 更新状态
    taskId.value = taskIdVal;
    status.value = resp.data?.status || "PENDING";
    running.value = true;

    // 启动温和的进度推进，直到后端返回更精确的数据
    let rampRate = 0.3 + Math.random() * 0.7; // 每秒增长 0.3-1.0%
    progressTimer = setInterval(() => {
      if (progress.value < 80) {
        progress.value = Math.min(progress.value + rampRate, 80);
      }
    }, 1000);

    // 轮询任务状态
    statusTimer = setInterval(async () => {
      await checkSpiderStatus();
    }, 8000); // 延长轮询间隔至 8 秒，减少频繁请求

    // 立即刷新任务历史
    await fetchTaskHistory();

  } catch (e) {
    const errMsg = e?.message || "启动爬虫任务失败";
    // 精准的错误提示
    if (errMsg.includes("404")) {
      globalError.value = `接口不存在：请检查后端服务（http://10.244.181.48:5000）是否启动，或接口路径是否正确`;
    } else if (errMsg.includes("401")) {
      globalError.value = "登录状态失效：请重新登录后再尝试启动任务";
    } else if (errMsg.includes("未配置微博Cookie")) {
      globalError.value = "配置错误：后端未配置微博Cookie，无法启动爬虫任务";
    } else if (errMsg.includes("已有爬虫任务正在运行")) {
      globalError.value = "任务冲突：已有爬虫任务正在运行，请先等待该任务完成";
    } else if (errMsg.includes("500")) {
      globalError.value = "服务器错误：后端处理请求时发生异常，请联系管理员";
    } else {
      // 排除成功消息被误判的情况
      if (!errMsg.includes("爬虫任务创建成功")) {
        globalError.value = errMsg;
      }
    }
    
    // 只有真正的错误才更新error状态
    if (globalError.value) {
      error.value = errMsg;
      running.value = false;
      clearAllTimers();
      console.error("启动爬虫失败：", e);
    }
  }
}

/**
 * 检查爬虫任务状态（适配更多后端状态）
 */
async function checkSpiderStatus() {
  if (!taskId.value) return;

  try {
    const resp = await spiderStatus(taskId.value);
    
    // 适配后端状态查询的成功码
    if (resp.code !== 0) {
      throw new Error(resp.message || "获取任务状态失败");
    }

    // 从resp.data中获取任务详情（适配后端返回结构）
    const taskData = resp.data;
    status.value = taskData?.status || "";
    error.value = taskData?.error || "";

    // 任务参数错误
    if (status.value === "PARAM_ERROR") {
      clearAllTimers();
      running.value = false;
      error.value = "爬虫参数错误：" + (taskData?.error || "请检查关键词或页数配置");
      await fetchTaskHistory();
      return;
    }

    // 任务未启动
    if (status.value === "NOT_STARTED") {
      error.value = "任务未启动：" + (taskData?.error || "请检查后端爬虫配置");
      return;
    }

    // 当任务成功完成
    if (status.value === 'SUCCESS') {
      clearAllTimers();
      progress.value = 100;
      running.value = false;
      const resObj = taskData?.result || {};
      // 如果包含统计信息，优先展示 summary
      if (resObj && (resObj.arctype_count || resObj.article_count || resObj.comment_count || resObj.failed_count !== undefined)) {
        const summary = {
          arctype_count: resObj.arctype_count || 0,
          article_count: resObj.article_count || 0,
          comment_count: resObj.comment_count || 0,
          failed_count: resObj.failed_count || 0,
          elapsed_time: resObj.elapsed_time || 0
        };
        result.value = JSON.stringify({ summary, full: resObj }, null, 2);
      } else {
        result.value = JSON.stringify(resObj, null, 2);
      }
      // 刷新任务历史
      await fetchTaskHistory();
    }

    // 任务失败
    if (status.value === "FAILED") {
      clearAllTimers();
      running.value = false;
      // 如果是 Kafka 无法连接，给出更友好的运维指引
      const rawErr = taskData?.error || "任务执行失败，具体原因请查看后端日志";
      if (rawErr && rawErr.includes('NoBrokersAvailable')) {
        error.value = "任务失败：消息队列不可用（NoBrokersAvailable），请联系运维检查 Kafka 服务（broker/advertised.listeners）或稍后重试";
      } else {
        error.value = rawErr;
      }
      // 刷新任务历史
      await fetchTaskHistory();
    }

    // 任务仍在运行：利用后端返回的部分统计信息估算进度
    if (status.value === 'RUNNING') {
      const res = taskData?.result || {};
      // 优先使用 elapsed_time 与后端预估总时长（如果有）
      if (res.elapsed_time && res.estimated_total_time) {
        const pct = Math.min((res.elapsed_time / res.estimated_total_time) * 100, 99);
        progress.value = Math.max(progress.value, pct);
      } else if ((res.article_count || 0) > 0 && (res.arctype_count || 0) > 0) {
        // 基于抓取量估算（粗略）
        const got = (res.article_count || 0) + (res.comment_count || 0);
        const target = (res.arctype_count || 0) * 50; // 假设每个 arctype 平均 50 条
        if (target > 0) {
          const pct = Math.min((got / target) * 100, 98);
          progress.value = Math.max(progress.value, pct);
        } else {
          progress.value = Math.min(98, progress.value + 0.5 + Math.random() * 1.0);
        }
      } else if (res.params_received) {
        // 如果只收到回传参数，轻微增长
        progress.value = Math.min(95, progress.value + 0.8 + Math.random() * 0.8);
      } else {
        // 没有信息时温和推进
        progress.value = Math.min(95, progress.value + 0.5 + Math.random() * 0.7);
      }
      // 避免进度瞬间回退
      progress.value = Math.max(progress.value, 1);
    }

  } catch (e) {
    error.value = e?.message || "轮询任务状态失败";
    clearAllTimers();
    running.value = false;
  }
}

/**
 * 获取任务历史列表（增强容错：适配多种后端返回格式）
 */
async function fetchTaskHistory() {
  try {
    // 显示加载状态（可选）
    const resp = await getSpiderTasks({ page: 1, per_page: 10 });
    // 增强容错：适配多种后端返回格式
    let tasks = [];
    if (resp.code === 0) {
      // 兼容：data.tasks / data / 直接返回数组
      tasks = resp.data?.tasks || resp.data || [];
      // 额外兼容：如果是对象包含list字段
      if (tasks.list) tasks = tasks.list;
    } else {
      // 兼容后端未返回code的情况
      tasks = resp.data?.tasks || resp.data || [];
    }
    
    // 标准化任务数据格式
    taskHistory.value = tasks.map(task => ({
      id: task.id || task.task_id,
      status: task.status || 'UNKNOWN',
      created_at: task.created_at || task.create_time || new Date().toISOString(),
      ...task
    }));
    
    console.log("任务历史数据（标准化后）：", taskHistory.value); // 调试用
  } catch (e) {
    console.error("获取任务历史失败：", e);
    taskHistory.value = [];
  }
}

/**
 * 复制结果到剪贴板
 */
async function handleCopyResult() {
  if (!result.value) return;

  try {
    if (navigator.clipboard) {
      await navigator.clipboard.writeText(result.value);
      alert("结果复制成功！");
    } else {
      // 降级方案：兼容旧浏览器
      const textArea = document.createElement("textarea");
      textArea.value = result.value;
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand("copy");
      document.body.removeChild(textArea);
      alert("结果复制成功！");
    }
  } catch (e) {
    error.value = "复制失败：" + e.message;
    alert("复制失败，请手动复制结果内容");
  }
}

/**
 * 清除所有定时器
 */
function clearAllTimers() {
  if (statusTimer) {
    clearInterval(statusTimer);
    statusTimer = null;
  }
  if (progressTimer) {
    clearInterval(progressTimer);
    progressTimer = null;
  }
  if (historyTimer) {
    clearInterval(historyTimer);
    historyTimer = null;
  }
}

// 组件挂载时初始化
onMounted(async () => {
  // 初始加载任务历史
  await fetchTaskHistory();
  // 启动任务历史轮询（每15秒刷新一次）
  historyTimer = setInterval(() => {
    fetchTaskHistory();
  }, 15000);
});

// 组件卸载前清除定时器（防止内存泄漏）
onBeforeUnmount(() => {
  clearAllTimers();
});
</script>

<style scoped>
/* 原有样式 + 新增参数输入样式 */
.spider-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea15 0%, #764ba215 50%, #f5576c15 100%);
  padding: 0;
}

.page-header {
  max-width: 1440px;
  margin: 0 auto 48px;
  position: relative;
  overflow: hidden;
  background: white;
  border-radius: 24px;
  padding: 56px 48px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
  margin-top: 24px;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 32px;
  position: relative;
  z-index: 1;
}

.header-icon {
  width: 100px;
  height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 4rem;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-radius: 24px;
  box-shadow: 0 12px 32px rgba(102, 126, 234, 0.3);
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

.page-title {
  font-size: 3rem;
  font-weight: 800;
  background: linear-gradient(135deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0 0 12px 0;
}

.page-subtitle {
  font-size: 1.25rem;
  color: #718096;
  margin: 0;
}

.header-decoration {
  position: absolute;
  top: 0;
  right: 0;
  width: 300px;
  height: 300px;
  pointer-events: none;
}

.deco-circle {
  position: absolute;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
}

.deco-circle:nth-child(1) {
  width: 200px;
  height: 200px;
  top: -100px;
  right: -100px;
  animation: pulse 4s ease-in-out infinite;
}

.deco-circle:nth-child(2) {
  width: 150px;
  height: 150px;
  top: -50px;
  right: 50px;
  animation: pulse 4s ease-in-out infinite 1s;
}

@keyframes pulse {
  0%,
  100% {
    transform: scale(1);
    opacity: 0.3;
  }
  50% {
    transform: scale(1.1);
    opacity: 0.5;
  }
}

.content-wrapper {
  max-width: 1440px;
  margin: 0 auto 64px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 28px;
  padding: 0 32px;
}

.control-card {
  grid-column: 1 / 2;
}
.status-card, .result-card, .history-card {
  grid-column: 2 / 3;
}

/* 卡片样式 */
.card {
  background: white;
  border-radius: 20px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.card:hover {
  box-shadow: 0 12px 36px rgba(0, 0, 0, 0.12);
  transform: translateY(-4px);
}

.card-header {
  padding: 32px 36px;
  border-bottom: 1px solid #f1f5f9;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.icon-badge {
  width: 64px;
  height: 64px;
  border-radius: 20px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.3);
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
  font-size: 1.75rem;
  font-weight: 700;
  color: #1a202c;
  margin: 0;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 20px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border-radius: 50px;
  font-size: 1rem;
  font-weight: 600;
}

.pulse-dot {
  width: 10px;
  height: 10px;
  background: white;
  border-radius: 50%;
  animation: pulse-dot 2s ease-in-out infinite;
}

@keyframes pulse-dot {
  0%,
  100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.5;
    transform: scale(1.3);
  }
}

.card-body {
  padding: 36px;
}

/* 新增：表单样式 */
.form-group {
  margin-bottom: 24px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  font-size: 1rem;
  font-weight: 600;
  color: #2d3748;
  display: flex;
  align-items: center;
}

.form-label .required {
  color: #e53e3e;
  margin-left: 4px;
}

.form-input {
  padding: 16px 20px;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  font-size: 1rem;
  color: #1a202c;
  transition: all 0.2s ease;
}

.form-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

/* 操作按钮 */
.action-btn {
  width: 100%;
  padding: 24px 36px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border: none;
  border-radius: 20px;
  font-size: 1.25rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.3);
  position: relative;
  overflow: hidden;
}

.action-btn::before {
  content: "";
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
  box-shadow: 0 10px 28px rgba(102, 126, 234, 0.4);
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
  font-size: 2rem;
}

.info-box {
  display: flex;
  gap: 16px;
  padding: 20px 24px;
  background: linear-gradient(135deg, #f0f4ff, #e8eeff);
  border-left: 4px solid #667eea;
  border-radius: 16px;
  margin-top: 24px;
}

.info-icon {
  font-size: 1.5rem;
  flex-shrink: 0;
}

.info-box p {
  margin: 0;
  color: #4a5568;
  font-size: 1rem;
  line-height: 1.8;
}

/* 全局错误提示 */
.global-error {
  margin-top: 24px;
  background: linear-gradient(135deg, #fed7d7, #feb2b2);
  border-left: 4px solid #e53e3e;
}

.error-message {
  padding: 12px 16px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
  color: #742a2a;
  font-size: 0.875rem;
  font-weight: 500;
}

.error-icon {
  font-size: 1rem;
}

.error-text {
  flex: 1;
}

/* 状态网格 */
.status-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.status-item {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.status-item.full-width {
  grid-column: 1 / -1;
}

.status-label {
  font-size: 1rem;
  color: #718096;
  font-weight: 600;
}

.status-value {
  font-size: 1.25rem;
  color: #1a202c;
  font-weight: 600;
}

.status-value.monospace {
  font-family: "Monaco", "Consolas", monospace;
  background: #f7fafc;
  padding: 12px 16px;
  border-radius: 12px;
  font-size: 1rem;
  word-break: break-all;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 10px 20px;
  border-radius: 50px;
  font-size: 1rem;
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
  width: 8px;
  height: 8px;
  background: white;
  border-radius: 50%;
  animation: pulse-dot 2s ease-in-out infinite;
}

.error-box {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px 24px;
  background: linear-gradient(135deg, #fed7d7, #feb2b2);
  border-left: 4px solid #f56565;
  border-radius: 16px;
}

/* 进度条 */
.progress-section {
  margin-top: 28px;
  padding-top: 28px;
  border-top: 1px solid #f1f5f9;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.progress-label {
  font-size: 1rem;
  color: #718096;
  font-weight: 600;
}

.progress-percentage {
  font-size: 1.25rem;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.progress-bar {
  height: 16px;
  background: #e2e8f0;
  border-radius: 8px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea, #764ba2);
  border-radius: 8px;
  transition: width 0.5s ease;
  position: relative;
  overflow: hidden;
}

.progress-fill::after {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  animation: shimmer 2s infinite;
}

@keyframes shimmer {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

/* 结果容器 */
.result-container {
  background: #1a202c;
  border-radius: 16px;
  padding: 32px;
  overflow: auto;
  max-height: 600px;
}

.result-content {
  margin: 0;
  color: #48bb78;
  font-family: "Monaco", "Consolas", monospace;
  font-size: 1rem;
  line-height: 1.8;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.copy-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.copy-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.copy-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.3);
}

/* 任务历史列表 */
.history-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 400px;
  overflow-y: auto;
  padding-right: 8px;
}

.history-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: #f7fafc;
  border-radius: 8px;
  font-size: 0.875rem;
  transition: all 0.2s ease;
}

.history-item:hover {
  background: #f0f4ff;
  transform: translateX(4px);
}

.history-id {
  font-family: monospace;
  color: #2d3748;
  font-weight: 600;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.history-status {
  padding: 4px 8px;
  border-radius: 4px;
  font-weight: 600;
  color: white;
  min-width: 60px;
  text-align: center;
}

.history-status.status-pending {
  background: #f59e0b;
}

.history-status.status-running {
  background: #00f2fe;
}

.history-status.status-success {
  background: #48bb78;
}

.history-status.status-failed {
  background: #e53e3e;
}

.history-time {
  color: #718096;
  font-size: 0.75rem;
  margin-left: 12px;
  white-space: nowrap;
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 80px 20px;
}

.empty-icon {
  font-size: 5rem;
  margin-bottom: 20px;
  opacity: 0.5;
}

.empty-text {
  font-size: 1.25rem;
  color: #2d3748;
  font-weight: 600;
  margin: 0 0 8px 0;
}

.empty-hint {
  font-size: 1rem;
  color: #a0aec0;
  margin: 0;
}

/* 响应式优化 */
@media (max-width: 1024px) {
  .content-wrapper {
    grid-template-columns: 1fr;
  }
  .control-card, .status-card, .result-card, .history-card {
    grid-column: 1 / -1;
  }
}

@media (max-width: 768px) {
  .spider-page {
    padding: 0;
  }

  .page-header {
    padding: 32px 24px;
    margin-bottom: 24px;
    margin-top: 16px;
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

  .history-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .history-time {
    margin-left: 0;
    margin-top: 4px;
  }
}
</style>