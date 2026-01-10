// src/api/spider.js
import http from "@/utils/http";
// 引入Element UI的消息提示（如果你的项目用了其他UI库，替换为对应提示组件）
import { ElMessage } from 'element-plus'; 

/**
 * 启动爬虫任务（后端路径：/api/spider/start）
 * @param {Object} taskParams - 爬虫任务参数（包含user_id和爬虫配置）
 * @param {string} taskParams.user_id - 用户ID（必传）
 * @param {string} [taskParams.keyword] - 爬虫关键词（可选，根据你的业务补充）
 * @param {number} [taskParams.page] - 爬取页数（可选，根据你的业务补充）
 */
export const runSpider = async (taskParams = {}) => {
  // 1. 优先从入参获取user_id，若未传则从本地存储/登录态中获取（兜底）
  let { user_id, ...otherParams } = taskParams;
  
  // 2. 兜底获取user_id（适配不同登录态存储方式，你可根据实际情况调整）
  if (!user_id) {
    // 方式1：从localStorage获取登录用户信息（最常见）
    const userInfoStr = localStorage.getItem('userInfo');
    if (userInfoStr) {
      const userInfo = JSON.parse(userInfoStr);
      // 适配常见的字段名：id / userId / user_id
      user_id = userInfo.id || userInfo.userId || userInfo.user_id;
    }

    // 方式2：若用Vuex/Pinia，取消注释下方代码（替换为你的状态管理路径）
    // import { useUserStore } from '@/stores/user';
    // const userStore = useUserStore();
    // user_id = userStore.user?.id;
  }

  // 3. 前置校验：user_id为空则直接拒绝请求，避免后端500错误
  if (!user_id) {
    ElMessage.error('请先登录后再启动爬虫！');
    return Promise.reject(new Error('用户ID不能为空，未检测到登录状态'));
  }

  // 4. 拼接请求参数：必传user_id + 其他爬虫参数
  const requestData = {
    user_id, // 核心：传递user_id给后端
    ...otherParams // 透传其他爬虫参数（如keyword、page等）
  };

  try {
    const response = await http.post("/api/spider/start", requestData);
    ElMessage.success('爬虫任务已提交！');
    return response;
  } catch (error) {
    // 统一错误提示
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