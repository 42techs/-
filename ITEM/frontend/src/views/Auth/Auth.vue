<template>
  <div class="auth-page">
    <!-- 背景渐变 -->
    <div class="bg-gradient"></div>

    <div class="auth-container">
      <!-- 品牌区 -->
      <div class="auth-header">
        <div class="logo">🚀🚀</div>
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

      <!-- 表单内容区 -->
      <div class="auth-content">
        <div v-if="loading" class="loading-container">
          <span class="loading-spinner">⏳</span>
          <p>加载中...</p>
        </div>
        
        <div v-else class="form-wrapper">
          <LoginForm
            v-show="currentView === 'login'"
            @switch-to-register="switchView('register')"
          />
          <RegisterForm
            v-show="currentView === 'register'"
            @switch-to-login="switchView('login')"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue"
import LoginForm from "./components/LoginForm.vue"
import RegisterForm from "./components/RegisterForm.vue"

const loading = ref(false)
const currentView = ref("login")

onMounted(() => {
  loading.value = false
})

function switchView(view) {
  currentView.value = view
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
}

.bg-gradient {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  opacity: 0.9;
}

.auth-container {
  background: white;
  border-radius: 24px;
  padding: 48px;
  width: 100%;
  max-width: 440px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  position: relative;
  z-index: 1;
}

.auth-header {
  text-align: center;
  margin-bottom: 32px;
}

.logo {
  font-size: 48px;
  margin-bottom: 16px;
}

.auth-header h1 {
  font-size: 28px;
  font-weight: 700;
  color: #1a202c;
  margin-bottom: 8px;
}

.auth-header p {
  font-size: 14px;
  color: #718096;
}

.auth-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 32px;
  background: #f7fafc;
  padding: 4px;
  border-radius: 12px;
}

.tab {
  flex: 1;
  padding: 12px 24px;
  background: transparent;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 600;
  color: #718096;
  cursor: pointer;
  transition: all 0.2s ease;
}

.tab.active {
  background: white;
  color: #667eea;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.auth-content {
  min-height: 300px;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 0;
}

.loading-spinner {
  font-size: 48px;
  margin-bottom: 16px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.form-wrapper {
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 640px) {
  .auth-container {
    padding: 32px 24px;
  }

  .auth-header h1 {
    font-size: 24px;
  }

  .logo {
    font-size: 36px;
  }
}
</style>