// src/api/spider.js
import http from "@/utils/http";
import { ElMessage } from 'element-plus';
import { useAuthStore } from "@/stores/auth";

export const runSpider = async () => {
  const authStore = useAuthStore();
  const user_id = authStore.user?.id;

  if (!user_id) {
    ElMessage.error('请先登录后再启动爬虫！');
    return Promise.reject(new Error('未登录'));
  }

  try {
    const response = await http.post("/spider/start", {});
    ElMessage.success('爬虫任务已提交！');
    return response;
  } catch (error) {
    ElMessage.error(`启动爬虫失败：${error.message || '服务器异常'}`);
    throw error;
  }
};

export const spiderStatus = (taskId) =>
  http.get(`/spider/tasks/${taskId}`);

export const getSpiderGlobalStatus = () =>
  http.get("/spider/status");

export const getSpiderTasks = (params = {}) =>
  http.get("/spider/tasks", { params });

export const testSpider = () =>
  http.get("/spider/test");
