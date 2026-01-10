<template>
  <div class="auth-page">
    <!-- 背景渐变 -->
    <div class="bg-gradient"></div>

    <div class="auth-container">
      <!-- 品牌区 -->
      <div class="auth-header">
        <div class="logo">🚀</div>
        <h1>微博热点分析</h1>
        <p>数据驱动决策</p>
      </div>

      <!-- 登录/注册切换 -->
      <div class="auth-tabs">
        <button
          :class="['tab', { active: currentView === 'login' }]"
          @click="switchView('login')"
          type="button"
        >
          登录
        </button>
        <button
          :class="['tab', { active: currentView === 'register' }]"
          @click="switchView('register')"
          type="button"
        >
          注册
        </button>
      </div>

      <!-- 内容区 -->
      <div class="auth-content">
        <transition name="fade" mode="out-in">
          <LoginForm
            v-if="currentView === 'login'"
            key="login"
            @switch-to-register="switchView('register')"
          />
          <RegisterForm
            v-else
            key="register"
            @switch-to-login="switchView('login')"
          />
        </transition>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import LoginForm from "@/components/LoginForm.vue";
import RegisterForm from "@/components/RegisterForm.vue";

// 当前视图（login/register）
const currentView = ref("login");

/**
 * 切换登录/注册视图
 * @param {string} view - 目标视图名称
 */
const switchView = (view) => {
  if (view === "login" || view === "register") {
    currentView.value = view;
  }
};
</script>

<style scoped>
/* 关键修改：确保登录页铺满整个屏幕 */
.auth-page {
  min-height: 100vh;
  width: 100vw; /* 新增：宽度铺满屏幕 */
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  position: relative;
  overflow: hidden;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  margin: 0; /* 新增：清除默认外边距 */
}

/* 背景渐变动画 */
.bg-gradient {
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 20% 50%, rgba(102, 126, 234, 0.3) 0%, transparent 50%),
    radial-gradient(circle at 80% 80%, rgba(118, 75, 162, 0.3) 0%, transparent 50%);
  animation: shift 20s ease-in-out infinite;
}

@keyframes shift {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.8;
  }
}

.auth-container {
  position: relative;
  z-index: 1;
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  padding: 48px;
  width: 100%;
  max-width: 440px; /* 保持表单宽度，避免过宽 */
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3), 0 0 0 1px rgba(255, 255, 255, 0.1) inset;
  animation: slideUp 0.5s ease-out;
  box-sizing: border-box; /* 新增：盒模型适配 */
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
}

/* 品牌区样式 */
.auth-header {
  text-align: center;
  margin-bottom: 32px;
}

.logo {
  font-size: 3rem;
  margin-bottom: 16px;
  display: inline-block;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-8px);
  }
}

.auth-header h1 {
  font-size: 1.75rem;
  font-weight: 700;
  color: #1a202c;
  margin: 0 0 8px;
}

.auth-header p {
  color: #718096;
  font-size: 0.875rem;
  margin: 0;
}

/* 切换标签样式 */
.auth-tabs {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  background: #f7fafc;
  padding: 4px;
  border-radius: 12px;
  margin-bottom: 32px;
}

.tab {
  padding: 12px;
  background: transparent;
  border: none;
  border-radius: 8px;
  font-size: 0.9375rem;
  font-weight: 600;
  color: #718096;
  cursor: pointer;
  transition: all 0.2s ease;
}

.tab.active {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.tab:hover:not(.active) {
  background: #f0f4ff;
  color: #4a5568;
}

/* 内容区样式 */
.auth-content {
  margin-bottom: 16px;
}

/* 过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 响应式优化 */
@media (max-width: 480px) {
  .auth-container {
    padding: 32px 24px;
  }

  .logo {
    font-size: 2.5rem;
  }

  .auth-header h1 {
    font-size: 1.5rem;
  }
}

/* 适配深色模式（可选） */
@media (prefers-color-scheme: dark) {
  .auth-container {
    background: rgba(17, 24, 39, 0.98);
  }

  .auth-header h1 {
    color: #f9fafb;
  }

  .auth-header p {
    color: #d1d5db;
  }

  .auth-tabs {
    background: #374151;
  }

  .tab {
    color: #d1d5db;
  }

  .tab:hover:not(.active) {
    background: #4b5563;
  }
}

/* 新增：全局样式重置（解决body默认边距） */
:global(body) {
  margin: 0;
  padding: 0;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}
:global(html) {
  box-sizing: border-box;
}
:global(*), :global(*::before), :global(*::after) {
  box-sizing: inherit;
}
</style>