<!-- src/views/Analysis/Analysis.vue -->
<template>
  <div class="analysis-page">
    <!-- 引入导航栏 -->
    <Navbar />
    <main class="main-content">
      <div class="page-header">
        <h1>数据分析中心</h1>
        <p>实时分析微博热点数据，生成可视化报告</p>
      </div>
      <div class="empty-state">
        <span class="icon">📊</span>
        <p>该功能正在开发中，敬请期待</p>
      </div>
    </main>
  </div>
</template>

<script setup>
import Navbar from "@/components/Navbar.vue";
</script>

<style scoped>
.analysis-page {
  min-height: 100vh;
  background: #f8fafc;
}

.main-content {
  max-width: 1440px;
  margin: 0 auto;
  padding: 56px 32px;
}

.page-header h1 {
  font-size: 2.5rem;
  font-weight: 700;
  color: #1a202c;
  margin-bottom: 8px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.page-header p {
  font-size: 1.125rem;
  color: #718096;
  margin-bottom: 40px;
}

.empty-state {
  text-align: center;
  padding: 80px 20px;
}

.empty-state .icon {
  font-size: 5rem;
  margin-bottom: 20px;
  opacity: 0.5;
}

.empty-state p {
  font-size: 1.25rem;
  color: #4a5568;
}
</style>