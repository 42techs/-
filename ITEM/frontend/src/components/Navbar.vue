<template>
  <nav class="navbar">
    <div class="navbar-container">
      <div class="navbar-brand">
        <router-link to="/" class="logo">
          📊 NLP Analysis
        </router-link>
      </div>

      <div class="navbar-menu">
        <router-link to="/" class="nav-link">首页</router-link>
        <router-link to="/spider" class="nav-link">数据采集</router-link>
        <router-link to="/analysis" class="nav-link">数据分析</router-link>
      </div>

      <div class="navbar-actions">
        <!-- 已登录：显示用户名 + 邮箱 + 退出 -->
        <div v-if="isLoggedIn" class="user-info">
          <div class="user-text">
            <span class="username">{{ username || '用户' }}</span>
            <span class="email">{{ email || '-' }}</span>
          </div>
          <button @click="handleLogout" class="btn-logout">退出</button>
        </div>

        <!-- 未登录：显示登录按钮 -->
        <router-link v-else to="/auth" class="btn-login">登录</router-link>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const isLoggedIn = computed(() => authStore.isLoggedIn)
const username = computed(() => authStore.username)
const email = computed(() => authStore.email)

const handleLogout = () => {
  authStore.logout()
  router.push('/auth')
}
</script>

<style scoped>
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 60px;
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  z-index: 1000;
}

.navbar-container {
  max-width: 1400px;
  margin: 0 auto;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.navbar-brand .logo {
  font-size: 20px;
  font-weight: 700;
  color: #1a1a1a;
  text-decoration: none;
  transition: color 0.2s;
}

.logo:hover {
  color: #3b82f6;
}

.navbar-menu {
  display: flex;
  gap: 30px;
  flex: 1;
  justify-content: center;
}

.nav-link {
  text-decoration: none;
  color: #4b5563;
  font-weight: 500;
  transition: color 0.2s;
  position: relative;
  padding: 5px 0;
}

.nav-link:hover {
  color: #3b82f6;
}

.nav-link.router-link-active {
  color: #3b82f6;
}

.nav-link.router-link-active::after {
  content: '';
  position: absolute;
  bottom: -8px;
  left: 0;
  right: 0;
  height: 2px;
  background: #3b82f6;
}

.navbar-actions {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.user-text {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
  text-align: right;
}

.username {
  color: #374151;
  font-weight: 600;
}

.email {
  font-size: 12px;
  color: #6b7280;
}

.btn-logout,
.btn-login {
  padding: 8px 20px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: background 0.2s;
  text-decoration: none;
  display: inline-block;
}

.btn-logout:hover,
.btn-login:hover {
  background: #2563eb;
}

@media (max-width: 768px) {
  .navbar-menu {
    gap: 15px;
  }

  .nav-link {
    font-size: 14px;
  }

  .user-text {
    display: none;
  }
}
</style>
