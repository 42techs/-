<template>
  <div class="layout">
    <Navbar />

    <main class="content">
      <h1>欢迎你，{{ user.username }}</h1>

      <section class="card">
        <h3>当前登录用户</h3>
        <ul>
          <li><strong>ID：</strong>{{ user.id }}</li>
          <li><strong>用户名：</strong>{{ user.username }}</li>
          <li><strong>邮箱：</strong>{{ user.email }}</li>
        </ul>
      </section>

      <section class="card">
        <h3>功能入口（占位）</h3>
        <div class="actions">
          <button disabled>舆情分析（TODO）</button>
          <button disabled>爬虫管理（TODO）</button>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { computed } from "vue";
import { useAuthStore } from "@/stores/auth";
import Navbar from "@/components/Navbar.vue";

const auth = useAuthStore();
const user = computed(() => auth.user || {});
</script>

<style scoped>
.layout {
  min-height: 100vh;
  background: #f3f4f6;
}

.content {
  padding: 24px;
  max-width: 960px;
  margin: 0 auto;
}

.card {
  background: #fff;
  border-radius: 12px;
  padding: 16px 20px;
  margin-top: 20px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
}

.actions {
  display: flex;
  gap: 12px;
  margin-top: 12px;
}

button {
  padding: 10px 14px;
  border-radius: 8px;
  border: none;
  background: #2563eb;
  color: #fff;
  cursor: pointer;
}

button:disabled {
  background: #9ca3af;
  cursor: not-allowed;
}
</style>
