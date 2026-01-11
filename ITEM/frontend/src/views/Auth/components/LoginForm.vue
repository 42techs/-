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
        :class="{ 'input-error': error && (error.includes('用户名') || error.includes('不存在')) }"
        @input="clearError"
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
        placeholder="请输入密码（至少6位）"
        :class="{ 'input-error': error && (error.includes('密码') || error.includes('错误')) }"
        @input="clearError"
      />
      <!-- 密码长度提示 -->
      <div v-if="form.password.length > 0 && form.password.length < 6" class="tips-text error-tips">
        密码长度不能少于6位
      </div>
    </div>

    <!-- 错误提示 -->
    <div v-if="error && !passwordLengthError" class="error-message">
      <span class="error-icon">⚠️</span>
      {{ error }}
    </div>

    <!-- 登录按钮 -->
    <button
      type="submit"
      class="submit-btn"
      :disabled="loading || !canSubmit"
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
        @click="emit('switch-to-register')"
      >
        立即注册
      </button>
    </div>
  </form>
</template>

<script setup>
import { ref, computed } from "vue";
import { useRouter, useRoute } from "vue-router";
import { useAuthStore } from "@/stores/auth"; // 引入auth store
import { loginApi } from "@/api/auth";
import { setTokens, clearTokens } from "@/utils/token";

// 定义emit
const emit = defineEmits(['switch-to-register']);
const router = useRouter();
const route = useRoute();
const authStore = useAuthStore(); // 初始化auth store

// 表单状态
const form = ref({
  username: "",
  password: "",
});
const loading = ref(false);
const error = ref("");

// 计算是否有密码长度错误
const passwordLengthError = computed(() => {
  return form.value.password.length > 0 && form.value.password.length < 6;
});

// 计算是否可以提交
const canSubmit = computed(() => {
  return form.value.username.trim().length > 0 && form.value.password.length >= 6;
});

// 清空错误提示方法
const clearError = () => {
  if (error.value) {
    error.value = "";
  }
};

/**
 * 处理登录逻辑（严格对齐后端AuthService.authenticate_user逻辑）
 */
async function handleLogin() {
  try {
    // 前置校验（和后端保持一致）
    const username = form.value.username.trim();
    const password = form.value.password.trim();
    
    error.value = "";

    if (!username) {
      error.value = "请输入用户名";
      return;
    }

    if (password.length < 6) {
      error.value = "密码长度不能少于6位";
      return;
    }

    loading.value = true;

    // 调用登录接口（后端返回ServiceResult格式）
    const response = await loginApi({ username, password });
    console.log('登录接口返回：', response);
    
    // 严格解析后端响应（适配api_ok返回格式）
    if (response.success) {
      // 存储Token到本地（对齐后端返回的data结构）
      setTokens({
        access_token: response.data.access_token,
        refresh_token: response.data.refresh_token,
        expires_in: response.data.expires_in || 86400 // 优先使用后端返回的过期时间
      });
      
      // 同步更新auth store状态（核心修复：之前缺失）
      authStore.user = response.data.user || { username };
      
  // 跳转到首页（支持redirect参数）
  // router.currentRoute 是一个 ref，在 setup 外直接访问会导致 undefined，
  // 在组件中使用 useRoute() 更安全
  const redirect = route?.query?.redirect || "/";
  await router.push(redirect);
      
      // 清空表单
      form.value = { username: "", password: "" };
    } else {
      // 后端返回的业务错误
      error.value = response.message || "登录失败";
      clearTokens();
    }

  } catch (err) {
    // 捕获所有错误（包括过滤后的401错误）
    const errMsg = err.message || "登录失败，请稍后重试";
    console.error("登录错误：", errMsg);
    error.value = errMsg;
    clearTokens();
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

.input-error {
  border-color: #e53e3e !important;
}

.form-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

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
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
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