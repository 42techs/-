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
      // 配置代理将 /api 路径的请求转发到后端地址
      '/api': {
        target: 'http://10.244.181.48:5000',
        changeOrigin: true,
        secure: false, // 如果后端是 HTTP，不是 HTTPS
      }
    }
  }
});
