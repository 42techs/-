import http from '@/utils/http'

// 登录接口
export const loginApi = (data) => {
  return http.post('/auth/login', data)
}

// 注册接口
export const registerApi = (data) => {
  return http.post('/auth/register', data)
}

// 刷新 Token
export const refreshTokenApi = (refreshToken) => {
  return http.post('/auth/refresh', { refresh_token: refreshToken })
}

// 退出登录
export const logoutApi = () => {
  return http.post('/auth/logout')
}

// 获取用户信息
export const getUserInfoApi = () => {
  return http.get('/auth/user')
}