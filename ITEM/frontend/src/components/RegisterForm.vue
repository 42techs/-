<template>
  <form class="register-form" @submit.prevent="handleRegister">
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
        placeholder="请设置用户名"
        required
        minlength="4"
      />
    </div>

    <!-- 邮箱输入框 -->
    <div class="form-group">
      <label class="form-label">
        <span class="label-icon">📧</span>
        邮箱
      </label>
      <input
        v-model="form.email"
        type="email"
        class="form-input"
        placeholder="请输入邮箱"
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
        placeholder="请设置密码（至少6位）"
        required
        minlength="6"
      />
    </div>

    <!-- 确认密码 -->
    <div class="form-group">
      <label class="form-label">
        <span class="label-icon">🔐</span>
        确认密码
      </label>
      <input
        v-model="form.confirmPassword"
        type="password"
        class="form-input"
        placeholder="请再次输入密码"
        required
        minlength="6"
      />
    </div>

    <!-- 错误提示 -->
    <div v-if="error" class="error-message">
      <span class="error-icon">⚠️</span>
      {{ error }}
    </div>

    <!-- 注册按钮 -->
    <button
      type="submit"
      class="submit-btn"
      :disabled="loading"
    >
      <span v-if="loading" class="loading-spinner">⏳</span>
      <span>{{ loading ? '注册中...' : '注册' }}</span>
    </button>

    <!-- 切换登录 -->
    <div class="form-footer">
      <span>已有账号？</span>
      <button
        type="button"
        class="switch-btn"
        @click="$emit('switch-to-login')"
      >
        立即登录
      </button>
    </div>
  </form>
</template>

<script setup>
import { ref } from "vue";
import { registerApi } from "@/api/auth";

// 表单状态
const form = ref({
  username: "",
  email: "",
  password: "",
  confirmPassword: "",
});
const loading = ref(false); // 加载状态
const error = ref(""); // 错误信息

/**
 * 处理注册逻辑（核心修复：优先提取后端错误信息）
 */
async function handleRegister() {
  try {
    // 前置校验：密码一致性
    if (form.value.password !== form.value.confirmPassword) {
      error.value = "两次输入的密码不一致";
      return;
    }

    // 前置空值校验
    const username = form.value.username.trim();
    const email = form.value.email.trim();
    const password = form.value.password.trim();
    
    if (!username) {
      error.value = "请输入用户名";
      return;
    }
    if (!email) {
      error.value = "请输入邮箱";
      return;
    }
    if (!password) {
      error.value = "请输入密码";
      return;
    }

    // 清空之前的错误
    error.value = "";
    // 设置加载状态
    loading.value = true;

    // 调用注册接口
    const resp = await registerApi({
      username,
      email,
      password,
    });

    // 注册成功：提示并切换到登录
    alert("注册成功，请登录");
    $emit("switch-to-login");
    
    // 清空表单
    form.value = { username: "", email: "", password: "", confirmPassword: "" };
  } catch (err) {
    // 核心修复：优先显示后端返回的具体错误（如"用户名已存在"）
    console.error("注册失败详情：", err);
    error.value = err.message || "注册失败，请稍后重试";
  } finally {
    // 关闭加载状态
    loading.value = false;
  }
}
</script>

<style scoped>
.register-form {
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