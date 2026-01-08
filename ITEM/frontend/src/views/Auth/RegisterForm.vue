<!-- src/views/Auth/RegisterForm.vue -->
<template>
  <form @submit.prevent="handleRegister" class="auth-form">
    <div class="form-group">
      <label for="username">用户名</label>
      <input 
        type="text" 
        id="username"
        v-model="form.username" 
        placeholder="请输入用户名（3-20位字符）"
        :class="{ 'error': errors.username }"
      />
      <span v-if="errors.username" class="error-message">{{ errors.username }}</span>
    </div>
    
    <div class="form-group">
      <label for="email">邮箱</label>
      <input 
        type="email" 
        id="email"
        v-model="form.email" 
        placeholder="请输入邮箱地址"
        :class="{ 'error': errors.email }"
      />
      <span v-if="errors.email" class="error-message">{{ errors.email }}</span>
    </div>
    
    <div class="form-group">
      <label for="password">密码</label>
      <input 
        type="password" 
        id="password"
        v-model="form.password" 
        placeholder="请输入密码（至少6位）"
        :class="{ 'error': errors.password }"
      />
      <span v-if="errors.password" class="error-message">{{ errors.password }}</span>
    </div>
    
    <div class="form-group">
      <label for="confirmPassword">确认密码</label>
      <input 
        type="password" 
        id="confirmPassword"
        v-model="form.confirmPassword" 
        placeholder="请再次输入密码"
        :class="{ 'error': errors.confirmPassword }"
      />
      <span v-if="errors.confirmPassword" class="error-message">{{ errors.confirmPassword }}</span>
    </div>

    <button type="submit" :disabled="loading" class="submit-btn">
      {{ loading ? '注册中...' : '注册' }}
    </button>

    <div class="auth-footer">
      <a href="#" @click.prevent="$emit('switch-to-login')">已有账号？立即登录</a>
    </div>
  </form>
</template>

<script>
export default {
  name: 'RegisterForm',
  emits: ['switch-to-login'],
  data() {
    return {
      form: {
        username: '',
        email: '',
        password: '',
        confirmPassword: ''
      },
      errors: {
        username: '',
        email: '',
        password: '',
        confirmPassword: ''
      },
      loading: false
    };
  },
  methods: {
    validateForm() {
      this.errors = { 
        username: '', 
        email: '', 
        password: '', 
        confirmPassword: '' 
      };
      let isValid = true;

      // 用户名验证
      if (!this.form.username.trim()) {
        this.errors.username = '请输入用户名';
        isValid = false;
      } else if (this.form.username.length < 3 || this.form.username.length > 20) {
        this.errors.username = '用户名长度应为3-20个字符';
        isValid = false;
      }

      // 邮箱验证
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!this.form.email) {
        this.errors.email = '请输入邮箱地址';
        isValid = false;
      } else if (!emailRegex.test(this.form.email)) {
        this.errors.email = '邮箱格式不正确';
        isValid = false;
      }

      // 密码验证
      if (!this.form.password) {
        this.errors.password = '请输入密码';
        isValid = false;
      } else if (this.form.password.length < 6) {
        this.errors.password = '密码长度至少6位';
        isValid = false;
      }

      // 确认密码验证
      if (!this.form.confirmPassword) {
        this.errors.confirmPassword = '请确认密码';
        isValid = false;
      } else if (this.form.password !== this.form.confirmPassword) {
        this.errors.confirmPassword = '两次输入的密码不一致';
        isValid = false;
      }

      return isValid;
    },

    async handleRegister() {
      if (!this.validateForm()) {
        return;
      }

      this.loading = true;
      
      try {
        // 模拟API调用
        const response = await this.$http.post('/api/auth/register', this.form);
        
        // 显示成功消息
        this.$message.success('注册成功！请登录');
        
        // 切换到登录视图
        this.$emit('switch-to-login');
        
      } catch (error) {
        const message = error.response?.data?.message || '注册失败，请稍后重试';
        this.$message.error(message);
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>

<style scoped>
.auth-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}
.form-group {
  display: flex;
  flex-direction: column;
}
.form-group label {
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #333;
}
.form-group input {
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  transition: border-color 0.3s ease;
}
.form-group input:focus {
  outline: none;
  border-color: #1890ff;
}
.form-group input.error {
  border-color: #ff4d4f;
}
.error-message {
  color: #ff4d4f;
  font-size: 0.875rem;
  margin-top: 0.25rem;
}
.submit-btn {
  padding: 0.75rem;
  background-color: #1890ff;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.3s ease;
}
.submit-btn:hover:not(:disabled) {
  background-color: #40a9ff;
}
.submit-btn:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}
.auth-footer {
  text-align: center;
  margin-top: 1rem;
}
.auth-footer a {
  color: #1890ff;
  text-decoration: none;
}
.auth-footer a:hover {
  text-decoration: underline;
}
</style>