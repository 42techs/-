// src/stores/auth.js
import { defineStore } from "pinia";
import { loginApi, profileApi } from "@/api/auth";
import { setTokens, clearTokens, getAccessToken } from "@/utils/token";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    user: null,
    bootstrapped: false,
  }),
  getters: {
    isAuthed: (s) => !!s.user && !!getAccessToken(),
  },
  actions: {
    async login({ username, password }) {
      const resp = await loginApi({ username, password });
      if (resp.code !== 0) throw new Error(resp.message || "登录失败");

      const { user, access_token, refresh_token } = resp.data;
      setTokens({ access_token, refresh_token });
      this.user = user;
      return user;
    },
    async bootstrap() {
      // 页面刷新后，尝试用 access token 拉取用户信息
      try {
        const resp = await profileApi();
        if (resp.code === 0) this.user = resp.data.user;
      } catch {
        // token 过期会触发 http.js 刷新逻辑；失败则清空
        clearTokens();
        this.user = null;
      } finally {
        this.bootstrapped = true;
      }
    },
    logout() {
      clearTokens();
      this.user = null;
    },
  },
});

