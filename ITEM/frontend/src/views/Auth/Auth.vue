<!-- src/views/Auth/Auth.vue -->
<template>
  <div class="auth-page">
    <div class="auth-container">
      <!-- 品牌标识 -->
      <div class="auth-header">
        <h1>微博热点分析系统</h1>
        <p>欢迎回来，请登录您的账户</p>
      </div>

      <!-- 视图切换 Tabs -->
      <div class="auth-tabs">
        <button 
          :class="['auth-tab', { 'active': currentView === 'login' }]"
          @click="currentView = 'login'"
        >
          登录
        </button>
        <button 
          :class="['auth-tab', { 'active': currentView === 'register' }]"
          @click="currentView = 'register'"
        >
          注册
        </button>
      </div>

      <!-- 动态渲染子组件 -->
      <div class="auth-content">
        <LoginForm 
          v-if="currentView === 'login'" 
          @switch-to-register="currentView = 'register'"
        />
        <RegisterForm 
          v-if="currentView === 'register'" 
          @switch-to-login="currentView = 'login'"
        />
      </div>
    </div>
  </div>
</template>

<script>
import LoginForm from './LoginForm.vue';
import RegisterForm from './RegisterForm.vue';

export default {
  name: 'AuthPage',
  components: {
    LoginForm,
    RegisterForm
  },
  data() {
    return {
      currentView: 'login'
    };
  }
};
</script>

<style scoped>
.auth-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: #f5f5f5;
}
.auth-container {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
}
.auth-tabs {
  display: flex;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid #e0e0e0;
}
.auth-tab {
  flex: 1;
  padding: 0.75rem;
  background: none;
  border: none;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all 0.3s ease;
}
.auth-tab.active {
  border-bottom-color: #1890ff;
  color: #1890ff;
  font-weight: bold;
}
.auth-header {
  text-align: center;
  margin-bottom: 2rem;
}
.auth-header h1 {
  margin: 0 0 0.5rem 0;
  color: #333;
}
.auth-header p {
  margin: 0;
  color: #666;
  font-size: 0.9rem;
}
</style>