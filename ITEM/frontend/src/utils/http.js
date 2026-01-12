import axios from "axios";
import { getToken } from "./token";

const http = axios.create({
  baseURL: "/api", // ✅ 关键：只用相对路径，走 Vite proxy
  timeout: 300000,
  headers: {
    "Content-Type": "application/json",
  },
});

// 请求拦截器
http.interceptors.request.use(
  (config) => {
    const token = getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    console.log(
      "发送请求:",
      config.method?.toUpperCase(),
      config.url,
      config.params || config.data
    );

    return config;
  },
  (error) => {
    console.error("Request Error:", error);
    return Promise.reject(error);
  }
);

// 响应拦截器
http.interceptors.response.use(
  (response) => {
    console.log("响应成功:", response.config.url, response.data);
    return response.data;
  },
  (error) => {
    console.error("Response Error:", error);

    if (error.response) {
      const { status, data } = error.response;

      if (status === 401) {
        localStorage.clear();
        window.location.href = "/auth";
        return Promise.reject({ message: "登录已过期，请重新登录" });
      }

      return Promise.reject({
        message: data?.message || `请求失败 (${status})`,
        status,
      });
    }

    if (error.code === "ERR_NETWORK") {
      return Promise.reject({ message: "网络错误，请检查后端服务" });
    }

    if (error.code === "ECONNABORTED") {
      return Promise.reject({ message: "请求超时，请重试" });
    }

    return Promise.reject({ message: error.message || "未知错误" });
  }
);

export default http;
