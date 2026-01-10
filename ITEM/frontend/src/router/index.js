// src/router/index.js
import { createRouter, createWebHistory } from "vue-router";
import Auth from "../views/Auth/Auth.vue";
import Home from "../views/Home.vue"; 
import Spider from "../views/Spider/Spider.vue";
// 新增Analysis组件（先创建占位，后续可完善）
import Analysis from "../views/Analysis/Analysis.vue";
import { useAuthStore } from "../stores/auth";

const routes = [
  { 
    path: "/login", 
    component: Auth, 
    meta: { public: true } 
  },
  { 
    path: "/", 
    component: Home, 
    meta: { requiresAuth: true } 
  },
  { 
    path: "/spider", 
    component: Spider, 
    meta: { requiresAuth: true } 
  },
  // 新增/analysis路由
  { 
    path: "/analysis", 
    component: Analysis, 
    meta: { requiresAuth: true } 
  },
  // 新增404重定向，避免路由匹配失败警告
  {
    path: "/:pathMatch(.*)*",
    redirect: "/"
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// 修复路由守卫：正确使用next()，规范权限校验逻辑
router.beforeEach(async (to, from, next) => {
  const auth = useAuthStore();

  // 首次进入/刷新页面时，拉取用户信息恢复登录态
  if (!auth.bootstrapped) {
    await auth.bootstrap();
  }

  // 公开页面（如登录页）直接放行
  if (to.meta.public) {
    // 已登录用户访问登录页，自动跳回首页
    if (auth.isAuthed) {
      next("/");
    } else {
      next();
    }
    return;
  }

  // 需要登录的页面：未登录则跳转到登录页（携带重定向参数）
  if (to.meta.requiresAuth && !auth.isAuthed) {
    next({ 
      path: "/login", 
      query: { redirect: to.fullPath } // 登录后返回原页面
    });
    return;
  }

  // 其他情况正常放行
  next();
});

export default router;