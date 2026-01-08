// src/api/http.js
import axios from "axios";
import { getAccessToken, getRefreshToken, setTokens, clearTokens } from "@/utils/token";

const http = axios.create({
  baseURL: import.meta?.env?.VITE_API_BASE_URL || "http://localhost:5000",
  timeout: 15000,
});

// 请求拦截：自动带上 access token
http.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// —— 刷新 token 的并发控制（避免同时 10 个请求都去刷新）——
let isRefreshing = false;
let pendingQueue = [];

function resolveQueue(error, token = null) {
  pendingQueue.forEach((p) => (error ? p.reject(error) : p.resolve(token)));
  pendingQueue = [];
}

// 响应拦截：如果 401 → 用 refresh token 换新 access token → 重放请求
http.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config;
    const status = error?.response?.status;

    // 不是 401 或者已经重试过，就直接抛
    if (status !== 401 || original._retry) throw error;

    // 没有 refresh token 无法刷新
    const refresh = getRefreshToken();
    if (!refresh) {
      clearTokens();
      throw error;
    }

    // 标记这个请求已经重试过
    original._retry = true;

    // 如果正在刷新，挂起当前请求
    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        pendingQueue.push({
          resolve: (newToken) => {
            original.headers.Authorization = `Bearer ${newToken}`;
            resolve(http(original));
          },
          reject,
        });
      });
    }

    // 开始刷新
    isRefreshing = true;

    try {
      const resp = await axios.post(
        `${http.defaults.baseURL}/api/auth/refresh`,
        { refresh_token: refresh },
        { timeout: 15000 }
      );

      if (resp.data?.code !== 0) throw new Error(resp.data?.message || "refresh failed");

      const newAccess = resp.data?.data?.access_token;
      setTokens({ access_token: newAccess, refresh_token: refresh });

      resolveQueue(null, newAccess);

      // 重放原请求
      original.headers.Authorization = `Bearer ${newAccess}`;
      return http(original);
    } catch (e) {
      resolveQueue(e, null);
      clearTokens();
      throw e;
    } finally {
      isRefreshing = false;
    }
  }
);

export default http;
