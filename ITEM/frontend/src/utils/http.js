import axios from "axios";
import { getAccessToken, getRefreshToken, setTokens, clearTokens } from "./token";
import { useAuthStore } from "@/stores/auth";

const http = axios.create({
  baseURL: "",
  timeout: 15000,
  headers: {
    "Content-Type": "application/json;charset=utf-8",
  },
});

/* 请求拦截：携带 access token */
http.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

/* 刷新并发控制 */
let isRefreshing = false;
let queue = [];

function resolveQueue(err, token = null) {
  queue.forEach((p) => (err ? p.reject(err) : p.resolve(token)));
  queue = [];
}

/* 响应拦截 */
http.interceptors.response.use(
  (res) => res,
  async (error) => {
    const { response, config } = error;
    if (!response) return Promise.reject(error);

    /* 登录 / 注册接口：401 直接抛给页面 */
    if (
      response.status === 401 &&
      (config.url.includes("/auth/login") ||
        config.url.includes("/auth/register"))
    ) {
      return Promise.reject(
        new Error(response.data?.message || "用户名或密码错误")
      );
    }

    /* 非 401 */
    if (response.status !== 401) {
      return Promise.reject(
        new Error(response.data?.message || "请求失败")
      );
    }

    /* 已重试过 */
    if (config._retry) {
      clearTokens();
      return Promise.reject(new Error("登录状态已失效，请重新登录"));
    }
    config._retry = true;

    const refreshToken = getRefreshToken();
    if (!refreshToken) {
      clearTokens();
      return Promise.reject(new Error("无刷新令牌，请重新登录"));
    }

    /* 正在刷新：排队 */
    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        queue.push({
          resolve: (newToken) => {
            config.headers.Authorization = `Bearer ${newToken}`;
            resolve(http(config));
          },
          reject,
        });
      });
    }

    /* 开始刷新 */
    isRefreshing = true;
    try {
      const resp = await http.post("/api/auth/refresh", {
        refresh_token: refreshToken,
      });

      if (resp.data?.code !== 200) {
        throw new Error(resp.data?.message || "刷新失败");
      }

      const newAccessToken = resp.data.data.access_token;
      setTokens({
        access_token: newAccessToken,
        refresh_token: refreshToken,
        expires_in: 86400,
      });

      resolveQueue(null, newAccessToken);

      config.headers.Authorization = `Bearer ${newAccessToken}`;
      return http(config);
    } catch (e) {
      resolveQueue(e);
      clearTokens();
      return Promise.reject(new Error("登录状态已过期，请重新登录"));
    } finally {
      isRefreshing = false;
    }
  }
);

export default http;
