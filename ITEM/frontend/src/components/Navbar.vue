<template>
  <header class="navbar">
    <div class="container">
      <div class="brand">
        <span class="logo">🚀</span>
        <span class="title">Weibo NLP</span>
      </div>

      <nav class="nav">
        <RouterLink to="/">首页</RouterLink>
        <RouterLink to="/analysis">分析</RouterLink>
        <RouterLink to="/spider">爬虫</RouterLink>
      </nav>

      <div class="actions">
        <span class="user">{{ user?.username }}</span>
        <button class="logout" @click="onLogout">退出</button>
      </div>
    </div>
  </header>
</template>

<script setup>
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import { computed } from "vue";

const router = useRouter();
const auth = useAuthStore();
const user = computed(() => auth.user);

function onLogout() {
  auth.logout();
  router.replace("/login");
}
</script>

<style scoped>
.navbar {
  background: white;
  border-bottom: 1px solid #e2e8f0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  font-weight: 700;
  color: #1a202c;
}

.logo {
  font-size: 1.5rem;
}

.title {
  font-size: 1.125rem;
}

.nav {
  display: flex;
  gap: 8px;
}

.nav a {
  padding: 8px 16px;
  color: #718096;
  text-decoration: none;
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.2s;
}

.nav a:hover {
  color: #667eea;
  background: rgba(102, 126, 234, 0.1);
}

.nav a.router-link-active {
  color: white;
  background: linear-gradient(135deg, #667eea, #764ba2);
}

.actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user {
  color: #2d3748;
  font-weight: 500;
}

.logout {
  padding: 8px 16px;
  background: #f56565;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.logout:hover {
  background: #e53e3e;
  transform: translateY(-1px);
}

@media (max-width: 768px) {
  .nav {
    display: none;
  }
}
</style>