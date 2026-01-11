<template>
  <div class="home">
    <div class="hero">
      <h1 class="title">社交媒体 NLP 分析平台</h1>
      <p class="subtitle">Social Media Natural Language Processing Analysis Platform</p>
      <div class="features">
        <div class="feature-card">
          <div class="feature-icon">🕷️</div>
          <h3>数据采集</h3>
          <p>支持微博数据智能采集</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">📊</div>
          <h3>词频分析</h3>
          <p>TF-IDF & TextRank 提取</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">❤️</div>
          <h3>情感分析</h3>
          <p>基于 SnowNLP 情感识别</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">🧠</div>
          <h3>主题建模</h3>
          <p>LDA 主题自动发现</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">📈</div>
          <h3>时间趋势</h3>
          <p>数据时序分析与预测</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">🔥</div>
          <h3>热点追踪</h3>
          <p>话题热度实时监控</p>
        </div>
      </div>
      <div class="cta-buttons">
        <router-link to="/spider" class="btn btn-primary">开始采集</router-link>
        <router-link to="/analysis" class="btn btn-secondary">查看分析</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
// 可以添加一些首页逻辑
</script>

<style scoped>
.home {
  min-height: calc(100vh - 60px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
}

.hero {
  max-width: 1400px; /* 增大最大宽度 */
  text-align: center;
  width: 100%;
}

.title {
  font-size: 56px; /* 增大字体大小 */
  font-weight: 800;
  color: #1a1a1a;
  margin-bottom: 15px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.subtitle {
  font-size: 22px; /* 增大字体大小 */
  color: #6b7280;
  margin-bottom: 60px;
}

.features {
  display: grid;
  grid-template-columns: repeat(3, 1fr); /* 3列布局 */
  gap: 20px;
  margin-bottom: 60px;
}

.feature-card {
  background: white;
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s, box-shadow 0.2s;
  text-align: center;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.feature-icon {
  font-size: 72px; /* 增大图标 */
  margin-bottom: 20px;
}

.feature-card h3 {
  font-size: 24px; /* 增大标题字体 */
  color: #1f2937;
  margin-bottom: 15px;
}

.feature-card p {
  font-size: 16px; /* 增大描述字体 */
  color: #6b7280;
}

.cta-buttons {
  display: flex;
  gap: 30px;
  justify-content: center;
}

.btn {
  padding: 16px 40px;
  border-radius: 8px;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.2s;
  font-size: 18px; /* 增大按钮字体 */
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover {
  background: #2563eb;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
}

.btn-secondary {
  background: white;
  color: #3b82f6;
  border: 2px solid #3b82f6;
}

.btn-secondary:hover {
  background: #3b82f6;
  color: white;
}

@media (max-width: 1024px) {
  .features {
    grid-template-columns: repeat(2, 1fr); /* 2列布局 */
  }
}

@media (max-width: 768px) {
  .features {
    grid-template-columns: 1fr; /* 1列布局 */
  }

  .title {
    font-size: 48px; /* 调整标题字体大小 */
  }

  .subtitle {
    font-size: 18px; /* 调整副标题字体大小 */
  }

  .cta-buttons {
    flex-direction: column;
  }

  .btn {
    width: 100%;
  }
}
</style>
