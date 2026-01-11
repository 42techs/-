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

const route = useRoute()

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