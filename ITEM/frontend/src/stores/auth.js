import { defineStore } from 'pinia'
import { getToken, setTokens, clearTokens } from '@/utils/token'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: getToken(),
    user: null
  }),

  getters: {
    isLoggedIn: (state) => !!state.token && !!state.user,
    username: (state) => state.user?.username || '',
    email: (state) => state.user?.email || ''
  },

  actions: {
    login(authData) {
      this.token = authData.access_token
      setTokens(authData.access_token, authData.refresh_token)
    },

    setUser(user) {
      this.user = user
    },

    logout() {
      this.token = null
      this.user = null
      clearTokens()
    }
  }
})
