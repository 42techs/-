import { defineStore } from "pinia";
import { loginApi, profileApi } from "@/api/auth";
import {
  setTokens,
  clearTokens,
  getAccessToken,
  getRefreshToken,
  isTokenExpired,
} from "@/utils/token";
import router from "@/router";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    user: null,
    bootstrapped: false,
    refreshing: false,
  }),

  getters: {
    isAuthed: () => !!getAccessToken() && !isTokenExpired(),
  },

  actions: {
    async login({ username, password }) {
      const resp = await loginApi({ username, password });
      const data = resp.data.data;

      setTokens({
        access_token: data.access_token,
        refresh_token: data.refresh_token,
        expires_in: 86400,
      });

      this.user = data.user;
      return this.user;
    },

    async bootstrap() {
      try {
        if (getAccessToken() && !isTokenExpired()) {
          const resp = await profileApi();
          this.user = resp.data.data.user;
        } else if (getRefreshToken()) {
          // 由 http.js 自动刷新
          const resp = await profileApi();
          this.user = resp.data.data.user;
        }
      } catch {
        clearTokens();
        this.user = null;
      } finally {
        this.bootstrapped = true;
      }
    },

    logout() {
      clearTokens();
      this.user = null;
      router.push("/login");
    },
  },
});
