<template>
  <div id="app">
    <!-- 显示导航栏（除了认证页面） -->
    <Navbar v-if="showNavbar" />
    
    <!-- 主内容区 -->
    <main :class="{ 'with-navbar': showNavbar }">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import Navbar from '@/components/Navbar.vue'
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { getToken } from '@/utils/token'
import { getUserInfoApi } from '@/api/auth'

const route = useRoute()

const authStore = useAuthStore()

onMounted(async () => {
  const token = getToken()
  if (token && !authStore.user) {
    try {
      const res = await getUserInfoApi()
      authStore.setUser(res.data.user)
    } catch (e) {
      // token 失效
      authStore.logout()
    }
  }
})

// 在认证页面隐藏导航栏
const showNavbar = computed(() => {
  return route.path !== '/auth' && route.path !== '/login'
})
</script>

<style>
#app {
  min-height: 100vh;
  background: #f9fafb;
}

main {
  min-height: 100vh;
}

main.with-navbar {
  padding-top: 60px;
  min-height: calc(100vh - 60px);
}
</style>