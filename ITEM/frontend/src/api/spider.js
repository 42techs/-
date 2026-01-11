// src/api/spider.js
import http from "@/utils/http";
import { ElMessage } from 'element-plus'; 
import { useAuthStore } from "@/stores/auth"; // 直接使用Pinia的authStore

/**
 * 启动爬虫任务（后端路径：/api/spider/start）
 * 启动爬虫任务（后端路径：/api/spider/start）
 * 注意：后端爬虫已改为忽略传入关键词/页数，前端只负责触发任务
 */
export const runSpider = async () => {
  // 从Pinia获取用户信息（更可靠）
  const authStore = useAuthStore();
  const user_id = authStore.user?.id;

  // 1. 前置校验：用户登录态
  if (!user_id) {
    ElMessage.error('请先登录后再启动爬虫！');
    return Promise.reject(new Error('用户ID不能为空，未检测到登录状态'));
  }

  try {
    // 后端现在不需要任何参数，这里仅触发任务
    const response = await http.post("/api/spider/start", {});
    ElMessage.success('爬虫任务已提交！');
    return response;
  } catch (error) {
    ElMessage.error(`启动爬虫失败：${error.message || '服务器异常'}`);
    return Promise.reject(error);
  }
};

/**
 * 获取单个任务详情（后端路径：/api/spider/tasks/{taskId}）
 * @param {string} taskId - 任务ID
 */
export const spiderStatus = async (taskId) => {
  if (!taskId) {
    ElMessage.error('任务ID不能为空！');
    return Promise.reject(new Error("任务ID不能为空"));
  }
  try {
    const response = await http.get(`/api/spider/tasks/${taskId}`);
    return response;
  } catch (error) {
    ElMessage.error(`获取任务详情失败：${error.message}`);
    return Promise.reject(error);
  }
};

/**
 * 获取爬虫整体状态（后端路径：/api/spider/status）
 */
export const getSpiderGlobalStatus = async () => {
  try {
    const response = await http.get("/api/spider/status");
    return response;
  } catch (error) {
    ElMessage.error(`获取爬虫状态失败：${error.message}`);
    return Promise.reject(error);
  }
};

/**
 * 获取任务列表（后端路径：/api/spider/tasks）
 * @param {Object} params - 分页/筛选参数 {page, per_page, status}
 */
export const getSpiderTasks = async (params = {}) => {
  try {
    const response = await http.get("/api/spider/tasks", { params });
    return response;
  } catch (error) {
    ElMessage.error(`获取任务列表失败：${error.message}`);
    return Promise.reject(error);
  }
};

/**
 * 测试爬虫配置（后端路径：/api/spider/test）
 */
export const testSpider = async () => {
  try {
    const response = await http.get("/api/spider/test");
    ElMessage.success('爬虫配置测试成功！');
    return response;
  } catch (error) {
    ElMessage.error(`测试爬虫配置失败：${error.message}`);
    return Promise.reject(error);
  }
};