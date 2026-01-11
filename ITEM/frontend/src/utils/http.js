import axios from "axios";
import { getAccessToken, getRefreshToken, setTokens, clearTokens } from "@/utils/token";

// 调试：打印基础配置
console.log('API基础地址：', import.meta?.env?.VITE_API_BASE_URL || "");

// 核心：baseURL设为空，所有请求走Vite代理（/api -> 后端）
const http = axios.create({
  baseURL: "",
  timeout: 30000,
  // 明确 transformRequest：确保对象被序列化为 JSON 字符串
  transformRequest: [(data, headers) => {
    if (typeof FormData !== 'undefined' && data instanceof FormData) {
      return data;
    }
    if (typeof data === 'object') {
      try {
        return JSON.stringify(data);
      } catch (e) {
        return data;
      }
    }
    return data;
  }],
  // 强制设置标准JSON请求头（匹配后端request.get_json要求）
  headers: {
    "Content-Type": "application/json;charset=utf-8",
    "Accept": "application/json"
  }
});

// 工具函数：兼容不同Axios版本的headers转对象
function headersToObject(headers) {
  if (!headers) return {};
  // 兼容AxiosHeaders对象和普通对象
  if (typeof headers.entries === 'function') {
    return Object.fromEntries(headers.entries());
  }
  // 普通对象直接返回
  return { ...headers };
}

http.interceptors.request.use(
  (config) => {
    // 注意：让 axios 负责对普通对象进行序列化（避免重复或不一致的 JSON 编码）
    // 如果 data 已经是 string 或者是 FormData，则保留原样
    if (config.data && ['post', 'put', 'patch'].includes((config.method || '').toLowerCase())) {
      // 如果是 FormData（文件上传等），不要设置 Content-Type，浏览器会自动处理 boundary
      if (typeof FormData !== 'undefined' && config.data instanceof FormData) {
        // keep as-is
      } else if (typeof config.data === 'string') {
        // 已经序列化为字符串，保持原样
      } else {
        // 普通对象交由 axios 进行序列化为 JSON
        // 确保 Content-Type 存在
        config.headers['Content-Type'] = config.headers['Content-Type'] || 'application/json;charset=utf-8';
      }
    }

  // ========== 核心修复：兼容Axios headers格式 ==========
  // 保护：有些 axios 版本会把 headers 设为 undefined
  config.headers = config.headers || {};
  // 1. 强制重置Content-Type（防止被覆盖）
  config.headers['Content-Type'] = 'application/json;charset=utf-8';
  // 2. 移除可能导致冲突的请求头
  delete config.headers['content-type']; // 移除小写版本，避免重复
  delete config.headers['Authorization']; // 先清空，再重新设置，避免脏数据
    
    // 打印请求信息（兼容不同Axios版本的headers）
  // 计算实际目标URL用于日志：在开发模式下如果配置了 VITE_API_BASE_URL 则显示该目标，
  // 否则显示相对 URL 拼接当前 origin（仅用于日志，不影响请求策略）
  const apiBase = import.meta?.env?.VITE_API_BASE_URL || '';
  const fullUrl = config.url ? (apiBase ? `${apiBase.replace(/\/$/, '')}${config.url}` : `${window.location.origin}${config.url}`) : '未知URL';
    // 打印序列化后的 payload（如果 transformRequest 已经序列化）
    let loggedData = config.data;
    try {
      if (typeof config.data === 'string') {
        loggedData = JSON.parse(config.data);
      }
    } catch (e) {
      // keep original
    }
    console.log('请求发送：', {
      url: config.url,
      method: config.method,
      fullUrl,
      headers: headersToObject(config.headers), // 兼容处理
      data: loggedData
    });
    
  // 排除不需要Token的接口（登录/注册/刷新都不应携带旧的 Authorization）
  const isAuthApi = config.url?.includes('/api/auth/login') || config.url?.includes('/api/auth/register') || config.url?.includes('/api/auth/refresh');
    if (!isAuthApi) {
      const token = getAccessToken();
      if (token && typeof token === "string") {
        // 严格规范Token格式：去除前后空格
        const cleanToken = token.trim();
        config.headers.Authorization = `Bearer ${cleanToken}`;
        console.log(`添加Token：Bearer ${cleanToken.substring(0, 10)}...`); // 脱敏打印
      } else {
        console.warn('Token不存在或格式错误，跳过Authorization头设置', token);
      }
    } else {
      console.log('登录/注册接口，不携带Token（正常逻辑：登录接口本身不需要Token）');
    }
    
    return config;
  },
  (error) => {
    console.error("请求拦截器错误：", error);
    return Promise.reject(error);
  }
);

// 刷新token并发控制
let isRefreshing = false;
let pendingQueue = [];

function resolveQueue(error, token = null) {
  pendingQueue.forEach((p) => {
    if (error) {
      p.reject(error);
    } else {
      p.resolve(token);
    }
  });
  pendingQueue = [];
}

// 响应拦截：修复兼容性问题 + 过滤底层错误 + 核心修复401分类
http.interceptors.response.use(
  (res) => {
    console.log('响应接收：', res.data);
    // 统一返回后端的原始响应数据（适配api_ok格式）
    return res.data;
  },
  async (error) => {
    const originalRequest = error.config || {}; // 兼容config为undefined的情况
    const responseStatus = error?.response?.status;
    const errorData = error.response?.data || {};

    // 打印完整错误信息（修复兼容性+增强排查）
    console.error('请求错误详情：', {
      url: originalRequest.url,
      fullUrl: originalRequest.url ? `${window.location.origin}${originalRequest.url}` : '未知URL',
      status: responseStatus,
      error: error.message,
      responseData: errorData,
      // 兼容处理headers打印
      requestHeaders: headersToObject(originalRequest.headers),
      responseHeaders: headersToObject(error.response?.headers)
    });

    // 1. 网络错误/配置错误（修复undefined问题）
    if (!error.response) {
      let errMsg = "无法连接到服务器，请稍后重试";
      // 区分配置错误和网络错误
      if (error.message.includes("config.headers.entries is not a function")) {
        errMsg = "请求配置错误（headers格式不兼容），已自动修复";
      } else if (error.message.includes("ERR_CONNECTION_REFUSED")) {
        errMsg = "服务器连接失败，请检查后端服务是否启动";
      } else if (error.message.includes("timeout")) {
        errMsg = "请求超时（服务器无响应）";
      } else if (error.message.includes("CORS")) {
        errMsg = "跨域访问被拒绝，请检查代理配置";
      }
      return Promise.reject(new Error(errMsg));
    }

    // 2. 登录/注册接口错误：核心修复401错误分类
    const isLoginRequest = originalRequest.url?.includes('/api/auth/login');
    const isRegisterRequest = originalRequest.url?.includes('/api/auth/register');
    
    if (isLoginRequest || isRegisterRequest) {
      clearTokens();
      const rawMsg = (errorData && (errorData.message || errorData.msg)) || '';
      let userMsg = '';

      // 如果检测到数据库/底层库错误关键词，不直接展示给用户，记录到控制台并显示友好信息
      const isDbError = rawMsg && (rawMsg.includes('1045') || rawMsg.includes('OperationalError') || rawMsg.includes('pymysql') || rawMsg.includes('Access denied'));
      if (isDbError) {
        // 记录详细错误以便开发者排查，但不暴露给最终用户
        console.error('后端数据库/底层错误（已屏蔽展示给用户）：', rawMsg);
        userMsg = isLoginRequest ? "登录失败，请联系管理员检查后端服务或数据库配置" : "注册失败，请联系管理员检查后端服务或数据库配置";
        return Promise.reject(new Error(userMsg));
      }

      // 否则如果后端返回了明确的 message，就显示该消息（便于展示业务错误，例如用户名已存在）
      if (rawMsg) {
        return Promise.reject(new Error(rawMsg));
      }

      // 5xx：后端内部错误，记录详情并向用户展示友好提示
      if (responseStatus && responseStatus >= 500) {
        console.error('后端 5xx 错误详情：', errorData);
        userMsg = "服务器内部错误，请联系管理员";
        return Promise.reject(new Error(userMsg));
      }

      // 最后根据状态码使用通用提示
      if (responseStatus === 401) {
        userMsg = isLoginRequest ? "用户名或密码错误，或账号未授权" : "注册失败，未被授权";
      } else {
        userMsg = isLoginRequest ? "用户名或密码错误" : "注册失败";
      }

      return Promise.reject(new Error(userMsg));
    }

    // 3. 500错误：统一提示
    if (responseStatus === 500) {
      return Promise.reject(new Error("服务器内部错误，请稍后重试"));
    }

    // 4. 400错误：透传业务错误
    if (responseStatus === 400) {
      const errMsg = errorData.message || "输入参数有误，请检查后重试";
      return Promise.reject(new Error(errMsg));
    }

    // 5. 其他401错误（token过期/无效）：非登录接口的401
    if (responseStatus === 401) {
      // 如果本次请求就是刷新接口本身，短路并清理Token，避免无限刷新循环
      if (originalRequest.url && originalRequest.url.includes('/api/auth/refresh')) {
        clearTokens();
        return Promise.reject(new Error('登录状态已过期，请重新登录'));
      }
      // 增强401排查日志（兼容处理）
      console.error('401错误详情（非登录接口）：', {
        hasToken: !!getAccessToken(),
        tokenValue: getAccessToken()?.substring(0, 20) + '...' || '无',
        requestHeaders: headersToObject(originalRequest.headers),
        responseHeaders: headersToObject(error.response?.headers)
      });
      
      if (originalRequest._retry) {
        clearTokens();
        return Promise.reject(new Error("登录状态已失效，请重新登录"));
      }
      originalRequest._retry = true;

      const refreshToken = getRefreshToken();
      if (!refreshToken) {
        clearTokens();
        return Promise.reject(new Error("登录状态已失效，请重新登录"));
      }

      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          pendingQueue.push({
            resolve: (newToken) => {
              originalRequest.headers.Authorization = `Bearer ${newToken}`;
              resolve(http(originalRequest));
            },
            reject: (err) => reject(err)
          });
        });
      }

      isRefreshing = true;
      try {
        // 刷新Token请求（传递对象，request 拦截器会让 axios 处理序列化）
        const refreshResp = await http.post("/api/auth/refresh", { 
          refresh_token: refreshToken 
        });
        const newAccessToken = refreshResp?.data?.access_token || refreshResp?.access_token;
        
        if (!newAccessToken) {
          throw new Error("登录状态已过期");
        }

        setTokens({ 
          access_token: newAccessToken, 
          refresh_token: refreshToken,
          expires_in: refreshResp?.data?.expires_in || refreshResp?.expires_in || 86400
        });
        resolveQueue(null, newAccessToken);

        // 重新设置Token
        originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
        return http(originalRequest);
      } catch (refreshErr) {
        resolveQueue(refreshErr, null);
        clearTokens();
        return Promise.reject(new Error("登录状态已过期，请重新登录"));
      } finally {
        isRefreshing = false;
      }
    }

    // 6. 404错误
    if (responseStatus === 404) {
      return Promise.reject(new Error("请求的接口不存在"));
    }

    // 其他错误默认提示
    return Promise.reject(new Error(errorData.message || "请求处理失败，请稍后重试"));
  }
);

export default http;