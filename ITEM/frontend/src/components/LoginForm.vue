<template>
  <form class="login-form" @submit.prevent="handleLogin">
    <!-- 用户名输入框 -->
    <div class="form-group">
      <label class="form-label">
        <span class="label-icon">👤</span>
        用户名
      </label>
      <input
        v-model="form.username"
        type="text"
        class="form-input"
        placeholder="请输入用户名"
        required
      />
    </div>

    <!-- 密码输入框 -->
    <div class="form-group">
      <label class="form-label">
        <span class="label-icon">🔒</span>
        密码
      </label>
      <input
        v-model="form.password"
        type="password"
        class="form-input"
        placeholder="请输入密码"
        required
      />
    </div>

    <!-- 错误提示 -->
    <div v-if="error" class="error-message">
      <span class="error-icon">⚠️</span>
      {{ error }}
    </div>

    <!-- 登录按钮 -->
    <button
      type="submit"
      class="submit-btn"
      :disabled="loading"
    >
      <span v-if="loading" class="loading-spinner">⏳</span>
      <span>{{ loading ? '登录中...' : '登录' }}</span>
    </button>

    <!-- 切换注册 -->
    <div class="form-footer">
      <span>还没有账号？</span>
      <button
        type="button"
        class="switch-btn"
        @click="$emit('switch-to-register')"
      >
        立即注册
      </button>
    </div>
  </form>
</template>

<script setup>
import { ref } from "vue";
import { useRouter, useRoute } from "vue-router";
import { useAuthStore } from "@/stores/auth";

// 路由实例
const router = useRouter();
const route = useRoute();
// 权限仓库
const authStore = useAuthStore();

// 表单状态
const form = ref({
  username: "",
  password: "",
});
const loading = ref(false);
const error = ref("");

/**
 * 处理登录逻辑（核心修复：简化逻辑，优化错误提示）
 */
async function handleLogin() {
  try {
    // 前置校验
    const username = form.value.username.trim();
    const password = form.value.password.trim();
    
    if (!username) {
      error.value = "请输入用户名";
      return;
    }
    if (!password) {
      error.value = "请输入密码";
      return;
    }

    error.value = "";
    loading.value = true;

    // 调用登录接口
    await authStore.login({ username, password });

    // 登录成功跳转
    alert("登录成功！即将跳转首页");
    const redirect = route.query.redirect || "/";
    const validRedirect = typeof redirect === "string" && redirect.startsWith("/") 
      ? redirect 
      : "/";
    await router.push(validRedirect);

    // 清空表单
    form.value.username = "";
    form.value.password = "";

  } catch (err) {
    // 核心修复：直接显示后端返回的错误信息
    console.error("登录错误：", err.message);
    error.value = err.message;
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  font-size: 0.875rem;
  color: #4a5568;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.label-icon {
  font-size: 1rem;
}

.form-input {
  padding: 14px 16px;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  font-size: 0.9375rem;
  color: #1a202c;
  transition: all 0.2s ease;
}

.form-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.error-message {
  padding: 12px 16px;
  background: linear-gradient(135deg, #fed7d7, #feb2b2);
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
  color: #742a2a;
  font-size: 0.875rem;
  font-weight: 500;
}

.error-icon {
  font-size: 1rem;
}

.submit-btn {
  width: 100%;
  padding: 16px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.submit-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.submit-btn:hover:not(:disabled) {
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
  transform: translateY(-1px);
}

.loading-spinner {
  font-size: 1.2rem;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.form-footer {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 0.875rem;
  color: #718096;
}

.switch-btn {
  background: none;
  border: none;
  color: #667eea;
  font-weight: 600;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.switch-btn:hover {
  background: rgba(102, 126, 234, 0.1);
}
</style>