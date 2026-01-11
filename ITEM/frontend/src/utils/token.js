const TOKEN_KEY = 'access_token'
const REFRESH_TOKEN_KEY = 'refresh_token'
const EXPIRES_KEY = 'token_expires_at'

// 基础 token 操作
export const getToken = () => {
  return localStorage.getItem(TOKEN_KEY)
}

export const setToken = (token) => {
  localStorage.setItem(TOKEN_KEY, token)
}

export const removeToken = () => {
  localStorage.removeItem(TOKEN_KEY)
}

// 新增：兼容旧代码的别名
export const getAccessToken = () => {
  return localStorage.getItem(TOKEN_KEY)
}

export const setAccessToken = (token) => {
  localStorage.setItem(TOKEN_KEY, token)
}

// Refresh Token 操作
export const getRefreshToken = () => {
  return localStorage.getItem(REFRESH_TOKEN_KEY)
}

export const setRefreshToken = (token) => {
  localStorage.setItem(REFRESH_TOKEN_KEY, token)
}

// 批量设置 tokens
export const setTokens = (tokens) => {
  if (tokens.access_token) {
    localStorage.setItem(TOKEN_KEY, tokens.access_token)
  }
  if (tokens.refresh_token) {
    localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refresh_token)
  }
  if (tokens.expires_in) {
    const expiresAt = Date.now() + tokens.expires_in * 1000
    localStorage.setItem(EXPIRES_KEY, expiresAt.toString())
  }
}

// 清除所有 tokens
export const clearTokens = () => {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(REFRESH_TOKEN_KEY)
  localStorage.removeItem(EXPIRES_KEY)
}

// Token 过期检查
export const isTokenExpired = () => {
  const expiresAt = localStorage.getItem(EXPIRES_KEY)
  if (!expiresAt) return true
  return Date.now() > parseInt(expiresAt)
}

// 获取 Token 过期时间
export const getTokenExpiration = () => {
  const expiresAt = localStorage.getItem(EXPIRES_KEY)
  return expiresAt ? parseInt(expiresAt) : null
}