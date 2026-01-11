import { createRouter, createWebHistory } from 'vue-router';
import { getToken } from '@/utils/token';

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
    meta: { title: '首页' }
  },
  {
    path: '/auth',
    name: 'Auth',
    component: () => import('@/views/Auth/Auth.vue'),
    meta: { title: '用户认证' }
  },
  {
    path: '/login',
    redirect: '/auth' // 统一重定向到 /auth
  },
  {
    path: '/spider',
    name: 'Spider',
    component: () => import('@/views/Spider/Spider.vue'),
    meta: { 
      requiresAuth: true,
      title: '爬虫管理'
    }
  },
  {
    path: '/analysis',
    name: 'Analysis',
    component: () => import('@/views/Analysis/Analysis.vue'),
    meta: { 
      requiresAuth: true,
      title: '数据分析'
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  document.title = to.meta.title || 'Social Network Hot Topic and Emotion Analysis System';

  // 检查是否需要认证
  if (to.meta.requiresAuth) {
    const token = getToken();
    if (!token) {
      // 未登录，跳转到认证页
      next({
        path: '/auth',
        query: { redirect: to.fullPath }
      });
    } else {
      next();
    }
  } else {
    next();
  }
});

export default router;