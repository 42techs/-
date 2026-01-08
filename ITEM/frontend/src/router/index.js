// src/router/index.js
import { createRouter, createWebHistory } from "vue-router";
import Auth from "../views/Auth/Auth.vue";
import Home from "../views/Home.vue"; 
import { useAuthStore } from "../stores/auth";

import Spider from "../views/Spider/Spider.vue";

const routes = [
  { path: "/login", component: Auth, meta: { public: true } },
  { path: "/", component: Home, meta: { requiresAuth: true } },
  { path: "/spider", component: Spider, meta: { requiresAuth: true } },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach(async (to) => {
  const auth = useAuthStore();

  // 首次进入时拉一次 profile（刷新页面也能恢复登录态）
  if (!auth.bootstrapped) await auth.bootstrap();

  if (to.meta.public) return true;

  if (to.meta.requiresAuth && !auth.isAuthed) {
    return { path: "/login", query: { redirect: to.fullPath } };
  }

  return true;
});

export default router;
