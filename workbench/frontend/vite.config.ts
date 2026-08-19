import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, ".", "");
  const host = env.WORKBENCH_WEB_HOST || "127.0.0.1";
  const port = Number(env.WORKBENCH_WEB_PORT || "5173");
  const apiTarget = env.WORKBENCH_API_TARGET || "http://127.0.0.1:8000";

  return {
    plugins: [react()],
    server: {
      host,
      port,
      strictPort: true,
      proxy: {
        "/api": {
          target: apiTarget,
          changeOrigin: true,
        },
      },
    },
    preview: {
      host,
      port,
      strictPort: true,
      proxy: {
        "/api": {
          target: apiTarget,
          changeOrigin: true,
        },
      },
    },
  };
});
