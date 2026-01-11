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
          :aria-selected="currentView === 'login'"
        >
          登录
        </button>
        <button
          :class="['tab', { active: currentView === 'register' }]"
          @click="switchView('register')"
          type="button"
          :aria-selected="currentView === 'register'"
        >
          注册
        </button>
      </div>

      <!-- 内容区：修复加载态和Transition警告 -->
      <div class="auth-content">
        <!-- 加载态 -->
        <div v-if="loading" class="loading-container">
          <span class="loading-spinner">⏳</span>
          <p>表单加载中...</p>
        </div>
        
        <!-- 核心修复：给Transition加固定根div -->
        <transition name="fade" mode="out-in" v-else>
          <div key="form-wrapper" class="form-wrapper">
            <component
              :is="currentComponentCompiled"
              key="currentView"
              @switch-to-register="switchView('register')"
              @switch-to-login="switchView('login')"
            />
          </div>
        </transition>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onErrorCaptured, markRaw } from "vue"; // 新增 markRaw

// 初始加载态为true
const loading = ref(true);
// 存储编译后的组件（核心修复：用markRaw标记，避免响应式）
const loginFormCompiled = ref(null);
const registerFormCompiled = ref(null);
// 当前视图
const currentView = ref("login");

// 预加载登录表单（页面挂载时）
onMounted(async () => {
  await loadLoginForm();
});

// 加载登录表单（带错误处理和加载态控制 + markRaw修复）
async function loadLoginForm() {
  try {
    loading.value = true;
    // 🔥 注意：确认实际路径！如果是 login/LoginForm.vue 就改成这个路径
    const module = await import("@/views/loginform/LoginForm.vue");
    // 核心修复：用markRaw标记组件，消除响应式警告
    loginFormCompiled.value = markRaw(module.default);
    loading.value = false;
  } catch (err) {
    loading.value = false;
    console.error("LoginForm加载失败：", err);
    // 错误组件也标记markRaw
    loginFormCompiled.value = markRaw({
      template: '<div class="component-error">登录表单加载失败，请检查文件路径</div>'
    });
  }
}

// 加载注册表单（带错误处理和加载态控制 + markRaw修复）
async function loadRegisterForm() {
  try {
    loading.value = true;
    const module = await import("@/views/register/RegisterForm.vue");
    // 核心修复：用markRaw标记组件
    registerFormCompiled.value = markRaw(module.default);
    loading.value = false;
  } catch (err) {
    loading.value = false;
    console.error("RegisterForm加载失败：", err);
    registerFormCompiled.value = markRaw({
      template: '<div class="component-error">注册表单加载失败，请检查文件路径</div>'
    });
  }
}

// 切换视图逻辑（核心修复：简化缓存逻辑 + 确保markRaw生效）
async function switchView(view) {
  if (!["login", "register"].includes(view)) {
    view = "login";
  }
  
  // 如果视图未变化，直接返回（避免重复加载）
  if (currentView.value === view) return;
  
  currentView.value = view;
  loading.value = true;
  
  try {
    // 只加载未缓存的组件
    if (view === "login" && !loginFormCompiled.value) {
      await loadLoginForm();
    } else if (view === "register" && !registerFormCompiled.value) {
      await loadRegisterForm();
    }
  } catch (err) {
    console.error("切换视图失败：", err);
  } finally {
    loading.value = false;
  }
}

// 计算当前编译后的组件（核心修复：确保返回非响应式组件）
const currentComponentCompiled = computed(() => {
  return currentView.value === "login" 
    ? loginFormCompiled.value 
    : registerFormCompiled.value;
});

// 全局错误捕获
onErrorCaptured((error) => {
  console.error("Auth页面错误：", error);
  loading.value = false;
  return true;
});
</script>

<!-- 全局样式 -->
<style>
body {
  margin: 0;
  padding: 0;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}
html {
  box-sizing: border-box;
}
*, *::before, *::after {
  box-sizing: inherit;
}

.component-error {
  padding: 20px;
  text-align: center;
  color: #e53e3e;
  background: #fed7d7;
  border-radius: 8px;
  margin: 10px 0;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 0;
  gap: 12px;
  color: #718096;
}

.loading-spinner {
  font-size: 2rem;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>

<!-- 局部样式 -->
<style scoped>
.auth-page {
  min-height: 100vh;
  width: 100vw;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  position: relative;
  overflow: hidden;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  margin: 0;
}

.bg-gradient {
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 20% 50%, rgba(102, 126, 234, 0.3) 0%, transparent 50%),
    radial-gradient(circle at 80% 80%, rgba(118, 75, 162, 0.3) 0%, transparent 50%);
  animation: shift 20s ease-in-out infinite;
}

@keyframes shift {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.8; }
}

.auth-container {
  position: relative;
  z-index: 1;
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  padding: 48px;
  width: 100%;
  max-width: 440px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3), 0 0 0 1px rgba(255, 255, 255, 0.1) inset;
  animation: slideUp 0.5s ease-out;
  box-sizing: border-box;
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px); }
}

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
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
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

.auth-content {
  margin-bottom: 16px;
}

/* 新增：表单容器样式，确保布局不变 */
.form-wrapper {
  width: 100%;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

/* 响应式 */
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

/* 深色模式 */
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
  :deep(.loading-container) {
    color: #d1d5db;
  }
}
</style>