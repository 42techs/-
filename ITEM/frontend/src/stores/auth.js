import { defineStore } from 'pinia'
import { getToken, setTokens, clearTokens } from '@/utils/token'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: getToken(), // 从本地获取 token
    user: JSON.parse(localStorage.getItem('user')) || null // 从本地获取用户信息，如果没有则为 null
  }),

  getters: {
    isLoggedIn: (state) => !!state.token && !!state.user,
    username: (state) => state.user?.username || '',
    email: (state) => state.user?.email || ''
  },

  actions: {
    // 登录方法：设置 token 和用户信息
    login(authData) {
      this.token = authData.access_token
      this.setUser(authData.user)  // 保存用户信息到 store
      setTokens(authData.access_token, authData.refresh_token)
      localStorage.setItem('user', JSON.stringify(authData.user))  // 存储用户信息到 localStorage
    },

    // 设置用户信息
    setUser(user) {
      this.user = user
    },

    // 退出登录方法：清除 token 和用户信息
    logout() {
      this.token = null
      this.user = null
      clearTokens()
      localStorage.removeItem('user')  // 清除本地存储的用户信息
    }
  }
})
