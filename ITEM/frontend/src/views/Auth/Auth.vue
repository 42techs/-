<template>
  <div class="auth-page">
    <!-- 简化背景 -->
    <div class="bg-gradient"></div>
    
    <div class="auth-container">
      <!-- 精简品牌区 -->
      <div class="auth-header">
        <div class="logo">🚀</div>
        <h1>微博热点分析</h1>
        <p>数据驱动决策</p>
      </div>

      <!-- 简化切换 -->
      <div class="auth-tabs">
        <button 
          :class="['tab', { active: currentView === 'login' }]"
          @click="switchView('login')"
        >
          登录
        </button>
        <button 
          :class="['tab', { active: currentView === 'register' }]"
          @click="switchView('register')"
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

<script>
import LoginForm from './LoginForm.vue';
import RegisterForm from './RegisterForm.vue';

export default {
  name: 'AuthPage',
  components: { LoginForm, RegisterForm },
  data() {
    return {
      currentView: 'login'
    };
  },
  methods: {
    switchView(view) {
      this.currentView = view;
    }
  }
};
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  position: relative;
  overflow: hidden;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* 简化背景 */
.bg-gradient {
  position: absolute;
  inset: 0;
  background: 
    radial-gradient(circle at 20% 50%, rgba(102, 126, 234, 0.3) 0%, transparent 50%),
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
  box-shadow: 
    0 20px 60px rgba(0, 0, 0, 0.3),
    0 0 0 1px rgba(255, 255, 255, 0.1) inset;
  animation: slideUp 0.5s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
}

/* 精简品牌区 */
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

/* 简化Tabs */
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
  transition: all 0.2s;
}

.tab.active {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

/* 内容区 */
.auth-content {
  margin-bottom: 16px;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s;
}

.fade-enter-from,
.fade-leave-to {
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
</style>