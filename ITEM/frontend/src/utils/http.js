import axios from 'axios'
import { getToken } from './token'

const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api',
  timeout: 300000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
http.interceptors.request.use(
  (config) => {
    const token = getToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    console.log('发送请求:', config.method.toUpperCase(), config.url, config.params || config.data)
    return config
  },
  (error) => {
    console.error('Request Error:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
http.interceptors.response.use(
  (response) => {
    console.log('响应成功:', response.config.url, response.data)
    return response.data
  },
  (error) => {
    console.error('Response Error:', error)
    
    if (error.response) {
      const { status, data } = error.response
      
      // 详细打印错误信息
      console.error('错误详情:', {
        status,
        message: data?.message,
        error: data?.error,
        data: data
      })
      
      if (status === 401) {
        // Token 过期，跳转登录
        localStorage.clear()
        window.location.href = '/auth'
        return Promise.reject({ message: '登录已过期，请重新登录' })
      }
      
      // 返回后端的错误信息
      const errorMessage = data?.message || data?.error || `请求失败 (${status})`
      return Promise.reject({ 
        message: errorMessage,
        status,
        data 
      })
    }
    
    // 网络错误
    if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
      return Promise.reject({ message: '请求超时，请重试' })
    }
    
    if (error.code === 'ERR_NETWORK') {
      return Promise.reject({ message: '网络错误，请检查后端服务' })
    }
    
    return Promise.reject({ message: error.message || '未知错误' })
  }
)

export default http