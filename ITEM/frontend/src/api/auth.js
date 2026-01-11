import http from '@/utils/http';

/**
 * 注册接口（严格对齐后端参数名）
 * @param {Object} data - 注册参数 {username, email, password}
 */
export function registerApi(data) {
  // 前端前置校验（和后端保持一致）
  const requiredFields = ['username', 'email', 'password'];
  const missingFields = requiredFields.filter(field => !data?.[field]);
  
  if (missingFields.length > 0) {
    return Promise.reject(new Error(`注册失败：${missingFields.join('、')}不能为空`));
  }

  // 严格按照后端要求传递参数
  return http.post('/api/auth/register', {
    username: data.username.trim(),
    email: data.email.trim(),
    password: data.password.trim()
  });
}

/**
 * 登录接口（严格对齐后端参数名）
 * @param {Object} data - 登录参数 {username, password}
 */
export function loginApi(data) {
  // 前端前置校验（和后端保持一致）
  const requiredFields = ['username', 'password'];
  const missingFields = requiredFields.filter(field => !data?.[field]);
  
  if (missingFields.length > 0) {
    return Promise.reject(new Error(`登录失败：${missingFields.join('、')}不能为空`));
  }

  // 严格按照后端要求传递参数
  return http.post('/api/auth/login', {
    username: data.username.trim(),
    password: data.password.trim()
  });
}

/**
 * 刷新Token接口（严格对齐后端参数名）
 * @param {String} refreshToken - 刷新令牌
 */
export function refreshTokenApi(refreshToken) {
  // 支持传入字符串（refresh token）或对象 { refresh_token: '...' }
  let tokenValue = null;
  if (!refreshToken) {
    return Promise.reject(new Error('刷新Token失败：刷新令牌不能为空'));
  }

  if (typeof refreshToken === 'string') {
    tokenValue = refreshToken;
  } else if (typeof refreshToken === 'object' && refreshToken.refresh_token) {
    tokenValue = refreshToken.refresh_token;
  } else {
    return Promise.reject(new Error('刷新Token失败：参数格式错误'));
  }

  return http.post('/api/auth/refresh', {
    refresh_token: tokenValue
  });
}

/**
 * 获取用户信息接口
 */
export function getUserProfileApi() {
  return http.get('/api/auth/profile');
}

/**
 * 修改密码接口（严格对齐后端参数名）
 * @param {Object} data - 密码参数 {current_password, new_password}
 */
export function changePasswordApi(data) {
  const requiredFields = ['current_password', 'new_password'];
  const missingFields = requiredFields.filter(field => !data?.[field]);
  
  if (missingFields.length > 0) {
    return Promise.reject(new Error(`修改密码失败：${missingFields.join('、')}不能为空`));
  }

  return http.post('/api/auth/change-password', {
    current_password: data.current_password.trim(),
    new_password: data.new_password.trim()
  });
}

export const profileApi = getUserProfileApi;

/**
 * 退出登录接口（前端仅清空Token，后端无logout接口则空实现）
 */
export function logoutApi() {
  // 后端未提供logout接口，前端仅清空本地Token
  return new Promise((resolve) => {
    resolve({ success: true, message: "退出登录成功" });
  });
}