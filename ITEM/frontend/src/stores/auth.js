import { defineStore } from "pinia";
import { loginApi, profileApi, refreshTokenApi } from "@/api/auth";
import { setTokens, clearTokens, getAccessToken, isTokenExpired, getRefreshToken } from "@/utils/token";
import router from "@/router";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    user: null,
    bootstrapped: false,
    refreshing: false
  }),
  getters: {
    isAuthed: (s) => {
      const hasToken = !!getAccessToken();
      const tokenNotExpired = !isTokenExpired();
      const final = hasToken && tokenNotExpired;
      console.log('isAuthed计算：', { 
        hasToken, 
        tokenNotExpired, 
        user: s.user,
        final 
      });
      return final;
    }
  },
  actions: {
    async login({ username, password }) {
      try {
        console.log('开始登录，参数：', { username, password });
        // 直接调用登录接口（走代理）
        const resp = await loginApi({ username, password });
        
        // 校验后端返回的token
        const access_token = resp?.data?.access_token || resp?.access_token;
        const refresh_token = resp?.data?.refresh_token || resp?.refresh_token;
        
        if (!access_token || !refresh_token) {
          throw new Error(resp?.message || "登录失败，请检查账号密码");
        }

        // 存储token
        setTokens({ 
          access_token, 
          refresh_token, 
          expires_in: resp?.data?.expires_in || resp?.expires_in || 86400 
        });
        
        // 获取用户信息
        try {
          const profileResp = await profileApi();
          this.user = profileResp?.data?.user || profileResp?.user || { username };
          console.log("获取用户信息成功：", this.user);
        } catch (e) {
          console.warn("获取用户信息失败：", e);
          this.user = { username };
        }

        console.log('登录成功，Token已存储');
  // 跳转首页
  // router.currentRoute 在 Pinia action 中是一个 ref：使用 .value 访问并保险判断
  const current = router && router.currentRoute ? router.currentRoute : null;
  const redirect = (current && current.value && current.value.query && current.value.query.redirect) || "/";
  await router.push(redirect);
        return this.user;
      } catch (error) {
        console.error('登录失败详情：', error);
        throw new Error(error.message || "登录失败，请稍后重试");
      }
    },

    async bootstrap() {
      try {
        if (this.bootstrapped) return; // 避免重复执行
        
        if (getAccessToken() && !isTokenExpired()) {
          const resp = await profileApi();
          this.user = resp?.data?.user || resp?.user || null;
        } else if (getRefreshToken()) {
          await this.refreshToken();
        }
      } catch (err) {
        clearTokens();
        this.user = null;
        console.error('bootstrap失败：', err);
      } finally {
        this.bootstrapped = true;
      }
    },

    async refreshToken() {
      if (this.refreshing) return;
      this.refreshing = true;

      try {
        const refreshToken = getRefreshToken();
        if (!refreshToken) throw new Error("登录状态已失效，请重新登录");

        const resp = await refreshTokenApi({ refresh_token: refreshToken });
        const access_token = resp?.data?.access_token || resp?.access_token;
        
        if (!access_token) throw new Error(resp?.message || "登录状态已过期");
        
        setTokens({ 
          access_token, 
          refresh_token, 
          expires_in: resp?.data?.expires_in || resp?.expires_in || 86400 
        });
        
        const profileResp = await profileApi();
        this.user = profileResp?.data?.user || profileResp?.user || null;
      } catch (err) {
        this.logout();
        router.push("/login");
        throw err;
      } finally {
        this.refreshing = false;
      }
    },

    logout() {
      clearTokens();
      this.user = null;
      this.refreshing = false;
      router.push("/login");
    }
  },
});