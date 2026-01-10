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
  position: sticky; /* 桌面端导航栏固定在顶部 */
  top: 0;
  z-index: 999;
}

.container {
  max-width: 1440px; /* 扩大桌面端容器宽度 */
  margin: 0 auto;
  padding: 0 32px; /* 增加左右内边距 */
  height: 72px; /* 提升导航栏高度，更适配桌面端 */
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.brand {
  display: flex;
  align-items: center;
  gap: 16px; /* 增大品牌区间距 */
  font-weight: 700;
  color: #1a202c;
}

.logo {
  font-size: 1.8rem; /* 增大logo尺寸 */
}

.title {
  font-size: 1.25rem; /* 增大标题字号 */
}

.nav {
  display: flex;
  gap: 16px; /* 增大导航项间距 */
}

.nav a {
  padding: 10px 20px; /* 增大导航项点击区域 */
  color: #718096;
  text-decoration: none;
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.2s;
  font-size: 1rem; /* 增大导航文字 */
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
  gap: 20px; /* 增大操作区间距 */
}

.user {
  color: #2d3748;
  font-weight: 500;
  font-size: 1rem; /* 增大用户名文字 */
}

.logout {
  padding: 10px 20px; /* 增大按钮点击区域 */
  background: #f56565;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 0.9375rem; /* 增大按钮文字 */
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.logout:hover {
  background: #e53e3e;
  transform: translateY(-1px);
}

/* 桌面端默认显示导航，仅移动端隐藏 */
@media (max-width: 768px) {
  .nav {
    display: none;
  }
}
</style>