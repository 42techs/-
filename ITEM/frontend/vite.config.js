import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import { fileURLToPath, URL } from "node:url";

export default defineConfig({
  plugins: [vue()],

  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },

  server: {
    proxy: {
      /**
       * 前端请求：
       *   /api/auth/login
       *
       * 实际转发到：
       *   http://10.244.181.48:5000/api/auth/login
       */
      "/api": {
        target: "http://10.244.181.48:5000",
        changeOrigin: true,
        secure: false,

        // ⭐ 关键：保留 /api，不做 rewrite
        // 因为你的后端接口本身就有 /api
      },
    },
  },
});
