// src/router/index.js
import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "../stores/auth";
import { h } from 'vue';

// 第一步：静态导入Auth组件（登录页核心，避免动态导入的500错误）
import AuthView from "../views/Auth/Auth.vue";

// 兜底组件（简化版）
const createFallbackComponent = (message) => ({
  render() {
    return h('div', {
      style: { padding: '20px', textAlign: 'center', color: 'red', fontSize: '16px' }
    }, message);
  }
});

// 第二步：静态注册所有路由（确保初始化时就有路由表）
const routes = [
  {
    path: "/login",          // 明确的/login路径
    name: "login",           // 增加name，确保匹配可靠
    component: AuthView,     // 静态导入的Auth组件
    meta: { requiresAuth: false }
  },
  {
    path: "/",
    name: "home",
    component: () => import("../views/Home.vue").catch(() => createFallbackComponent("首页加载失败")),
    meta: { requiresAuth: true }
  },
  {
    path: "/spider",
    name: "spider",
    component: () => import("../views/Spider/Spider.vue").catch(() => createFallbackComponent("爬虫页面加载失败")),
    meta: { requiresAuth: true }
  },
  {
    path: "/analysis",
    name: "analysis",
    component: () => import("../views/Analysis/Analysis.vue").catch(() => createFallbackComponent("分析页面加载失败")),
    meta: { requiresAuth: true }
  },
  {
    path: "/:pathMatch(.*)*", // 所有未知路径跳/login
    redirect: { name: "login" }
  }
];

// 第三步：创建路由实例（初始化时就有完整路由表）
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: routes, // 直接传入完整路由表，不再动态添加
  scrollBehavior: () => ({ top: 0 })
});

// 第四步：优化路由守卫（增加bootstrapped校验）
router.beforeEach(async (to, _, next) => {
  try {
    const authStore = useAuthStore();
    // 确保bootstrap只执行一次
    if (!authStore.bootstrapped) {
      await authStore.bootstrap();
    }
    
    // 未登录访问需要鉴权的页面 → 跳登录
    if (to.meta.requiresAuth && !authStore.isAuthed) {
      next({ name: "login", query: { redirect: to.fullPath } });
    } 
    // 已登录访问登录页 → 跳首页
    else if (to.name === "login" && authStore.isAuthed) {
      next({ name: "home" });
    } 
    // 其他情况正常放行
    else {
      next();
    }
  } catch (error) {
    console.error("路由守卫错误：", error);
    next(); // 出错时强制放行，避免白屏
  }
});

export default router;