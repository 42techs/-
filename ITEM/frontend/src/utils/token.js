// src/utils/token.js
const ACCESS_KEY = "access_token";
const REFRESH_KEY = "refresh_token";
const EXPIRE_KEY = "token_expire";

/**
 * 获取Access Token
 * @returns {string|null}
 */
export function getAccessToken() {
  try {
    return localStorage.getItem(ACCESS_KEY);
  } catch (e) {
    console.error('获取Access Token失败：', e);
    return null;
  }
}

/**
 * 获取Refresh Token
 * @returns {string|null}
 */
export function getRefreshToken() {
  try {
    return localStorage.getItem(REFRESH_KEY);
  } catch (e) {
    console.error('获取Refresh Token失败：', e);
    return null;
  }
}

/**
 * 设置Token（兼容后端未返回expires_in的情况）
 * @param {Object} params - Token参数
 * @param {string} params.access_token - Access Token
 * @param {string} params.refresh_token - Refresh Token
 * @param {number} [params.expires_in] - 过期时间（秒），默认3600秒
 */
export function setTokens({ access_token, refresh_token, expires_in }) {
  try {
    if (access_token) localStorage.setItem(ACCESS_KEY, access_token);
    if (refresh_token) localStorage.setItem(REFRESH_KEY, refresh_token);
    
  // 计算过期时间（毫秒），默认24小时（与后端默认保持一致）
  const expireSeconds = expires_in || 86400;
    const expireTime = Date.now() + expireSeconds * 1000;
    localStorage.setItem(EXPIRE_KEY, expireTime.toString()); // 修复：存储为字符串避免NaN
  } catch (e) {
    console.error('设置Token失败：', e);
  }
}

/**
 * 清空所有Token
 */
export function clearTokens() {
  try {
    localStorage.removeItem(ACCESS_KEY);
    localStorage.removeItem(REFRESH_KEY);
    localStorage.removeItem(EXPIRE_KEY);
  } catch (e) {
    console.error('清空Token失败：', e);
  }
}

/**
 * 判断Token是否过期（增强容错）
 * @returns {boolean} true=过期，false=未过期
 */
export function isTokenExpired() {
  try {
    const expireTimeStr = localStorage.getItem(EXPIRE_KEY);
    // 无过期时间 → 判定为未过期（开发阶段兜底）
    if (!expireTimeStr) return false;
    
    const expireTime = Number(expireTimeStr);
    // 非有效数字 → 判定为未过期
    if (isNaN(expireTime)) return false;
    
    // 提前30秒过期（缓冲时间）
    const now = Date.now();
    return now > expireTime - 30 * 1000;
  } catch (e) {
    console.error('判定Token过期状态失败：', e);
    return false; // 异常时默认未过期，避免误退出
  }
}