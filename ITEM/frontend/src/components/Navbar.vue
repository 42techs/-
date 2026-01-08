<template>
  <header class="navbar">
    <div class="left">
      <strong class="logo">Weibo NLP</strong>

      <nav class="menu">
        <RouterLink to="/">首页</RouterLink>
        <RouterLink to="/analysis">分析</RouterLink>
        <RouterLink to="/spider">爬虫</RouterLink>
      </nav>
    </div>

    <div class="right">
      <span class="user">{{ user?.username }}</span>
      <button class="logout" @click="onLogout">退出</button>
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
  height: 56px;
  padding: 0 20px;
  background: #1f2937;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.logo {
  font-size: 18px;
}

.menu a {
  color: #d1d5db;
  margin-right: 12px;
  text-decoration: none;
}

.menu a.router-link-active {
  color: #fff;
  font-weight: 600;
}

.right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logout {
  background: #ef4444;
  color: #fff;
  border: none;
  padding: 6px 10px;
  border-radius: 6px;
  cursor: pointer;
}
</style>
