import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getToken, clearTokens, setTokens } from '@/utils/token'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(getToken())

  const isLoggedIn = computed(() => !!token.value)
  const username = computed(() => user.value?.username || '用户')

  function setUser(userData) {
    user.value = userData
  }

  function login(userData, tokens) {
    user.value = userData
    token.value = tokens.access_token
    setTokens(tokens)
  }

  function logout() {
    user.value = null
    token.value = null
    clearTokens()
  }

  function updateToken(newToken) {
    token.value = newToken
  }

  return {
    user,
    token,
    isLoggedIn,
    username,
    setUser,
    login,
    logout,
    updateToken
  }
})