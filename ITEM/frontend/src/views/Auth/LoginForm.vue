<template>
  <form class="card" @submit.prevent="onSubmit">
    <h2>登录</h2>

    <label class="field">
      <span>用户名</span>
      <input v-model.trim="username" autocomplete="username" />
    </label>

    <label class="field">
      <span>密码</span>
      <input v-model="password" type="password" autocomplete="current-password" />
    </label>

    <p v-if="error" class="error">{{ error }}</p>

    <button :disabled="loading" type="submit">
      {{ loading ? "登录中..." : "登录" }}
    </button>
  </form>
</template>

<script setup>
import { ref } from "vue";
import { useRouter, useRoute } from "vue-router";
import { useAuthStore } from "@/stores/auth";

const router = useRouter();
const route = useRoute();
const auth = useAuthStore();

const username = ref("");
const password = ref("");
const loading = ref(false);
const error = ref("");

function validate() {
  // ✅ 前端负责 “不能为空” 校验
  if (!username.value) return "请输入用户名";
  if (!password.value) return "请输入密码";
  return "";
}

async function onSubmit() {
  error.value = validate();
  if (error.value) return;

  loading.value = true;
  try {
    await auth.login({ username: username.value, password: password.value });

    // 登录后跳转：优先回到之前想访问的页面
    const redirect = route.query.redirect || "/";
    router.replace(redirect);
  } catch (e) {
    error.value = e?.message || "登录失败";
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.card { max-width: 360px; padding: 16px; border: 1px solid #ddd; border-radius: 12px; }
.field { display: grid; gap: 6px; margin: 10px 0; }
.error { color: #c00; margin: 8px 0; }
button { width: 100%; padding: 10px; border-radius: 10px; }
</style>
