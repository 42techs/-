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
        placeholder="请设置用户名（至少4位）"
        :class="{ 'input-error': error && error.includes('用户名') }"
        @input="clearError"
      />
      <!-- 用户名长度提示 -->
      <div v-if="form.username.length > 0 && form.username.length < 4" class="tips-text error-tips">
        用户名长度不能少于4位
      </div>
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
        :class="{ 'input-error': error && error.includes('邮箱') }"
        @input="clearError"
      />
      <!-- 邮箱格式提示 -->
      <div v-if="form.email.length > 0 && !emailValid" class="tips-text error-tips">
        请输入有效的邮箱地址
      </div>
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
        :class="{ 'input-error': error && error.includes('密码') }"
        @input="clearError"
      />
      <!-- 密码长度提示 -->
      <div v-if="form.password.length > 0 && form.password.length < 6" class="tips-text error-tips">
        密码长度不能少于6位
      </div>
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
        :class="{ 'input-error': error && error.includes('一致') }"
        @input="clearError"
      />
      <!-- 密码一致性提示 -->
      <div v-if="form.confirmPassword.length > 0 && form.password !== form.confirmPassword" class="tips-text error-tips">
        两次输入的密码不一致
      </div>
    </div>

    <!-- 错误提示 -->
    <div v-if="error && !hasLengthError" class="error-message">
      <span class="error-icon">⚠️</span>
      {{ error }}
    </div>

    <!-- 注册按钮 -->
    <button
      type="submit"
      class="submit-btn"
      :disabled="loading || !canSubmit"
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
        @click="emit('switch-to-login')"
      >
        立即登录
      </button>
    </div>
  </form>
</template>

<script setup>
import { ref, computed, watch } from "vue";
import { useRouter } from "vue-router";
import { registerApi } from "@/api/auth";
import { setTokens, clearTokens } from "@/utils/token";

// 定义emit
const emit = defineEmits(['switch-to-login']);
const router = useRouter();

// 表单状态
const form = ref({
  username: "",
  email: "",
  password: "",
  confirmPassword: "",
});
const loading = ref(false);
const error = ref("");

// 邮箱格式校验
const emailValid = computed(() => {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.value.email.trim());
});

// 计算是否有长度错误
const hasLengthError = computed(() => {
  return form.value.username.length > 0 && form.value.username.length < 4 ||
         form.value.password.length > 0 && form.value.password.length < 6 ||
         (form.value.confirmPassword.length > 0 && form.value.password !== form.confirmPassword) ||
         (form.value.email.length > 0 && !emailValid.value);
});

// 计算是否可以提交
const canSubmit = computed(() => {
  return form.value.username.trim().length >= 4 &&
         emailValid.value &&
         form.value.password.length >= 6 &&
         form.value.password === form.value.confirmPassword;
});

// 清空错误提示方法
const clearError = () => {
  if (error.value) {
    error.value = "";
  }
};

/**
 * 处理注册逻辑（严格对齐后端响应格式）
 */
async function handleRegister() {
  try {
    // 1. 前置校验（和后端保持一致）
    const username = form.value.username.trim();
    const email = form.value.email.trim();
    const password = form.value.password.trim();
    const confirmPassword = form.value.confirmPassword.trim();
    
    error.value = "";

    // 空值校验
    if (!username) {
      error.value = "请输入用户名";
      return;
    }
    if (!email) {
      error.value = "请输入邮箱";
      return;
    }
    if (!password) {
      error.value = "请设置密码";
      return;
    }
    if (!confirmPassword) {
      error.value = "请确认密码";
      return;
    }

    // 格式/长度校验
    if (username.length < 4) {
      error.value = "用户名长度不能少于4位";
      return;
    }
    if (!emailValid.value) {
      error.value = "请输入有效的邮箱地址";
      return;
    }
    if (password.length < 6) {
      error.value = "密码长度不能少于6位";
      return;
    }
    if (password !== confirmPassword) {
      error.value = "两次输入的密码不一致";
      return;
    }

    // 2. 调用注册接口
    loading.value = true;
    const response = await registerApi({ username, email, password });
    
    // 3. 解析后端响应（兼容两种响应格式）
    const resData = response.data || response;
    
    if (resData.success) {
      // 注册成功：存储Token并跳转到登录页
      setTokens({
        access_token: resData.data.access_token,
        refresh_token: resData.data.refresh_token,
        expires_in: resData.data.expires_in || 86400
      });
      
      // 提示用户注册成功
      error.value = "";
      alert("注册成功，请登录"); // 可替换为UI库的Toast组件
      
      // 切换到登录页
      emit("switch-to-login");
      
      // 清空表单
      form.value = { username: "", email: "", password: "", confirmPassword: "" };
    } else {
      // 后端返回的失败信息
      error.value = resData.message || "注册失败";
      clearTokens();
    }

  } catch (err) {
    // 核心：透传后端错误信息
    const errMsg = err.message || "注册失败，请稍后重试";
    console.error("注册失败详情：", err);
    error.value = errMsg;
    clearTokens();
  } finally {
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

/* 错误输入框样式 */
.input-error {
  border-color: #e53e3e !important;
}

.form-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

/* 提示文本样式 */
.tips-text {
  font-size: 0.75rem;
  margin-top: 4px;
}

.error-tips {
  color: #e53e3e;
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
  background: linear-gradient(135deg, #a7b0e8, #a078b8);
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