import { defineConfig, loadEnv, type Plugin } from "vite";
import react from "@vitejs/plugin-react";

function surgicalUiReloader(): Plugin {
  let reloadTimer: ReturnType<typeof setTimeout> | undefined;
  const reloadableSource = /(?:^|[\\/])frontend[\\/](?:src[\\/].*\.(?:css|ts|tsx)|index\.html)$/i;
  return {
    name: "workbench-surgical-ui-reloader",
    handleHotUpdate(context) {
      if (!reloadableSource.test(context.file)) return [];
      if (reloadTimer) clearTimeout(reloadTimer);
      reloadTimer = setTimeout(() => {
        context.server.ws.send({
          type: "custom",
          event: "workbench:surgical-ui-change",
          data: { file: context.file, changedAt: new Date().toISOString() },
        });
      }, 180);
      // Disable component-by-component HMR. One allowlisted, debounced page
      // reload restores from the application's session-state lifecycle.
      return [];
    },
  };
}

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, ".", "");
  const host = env.WORKBENCH_WEB_HOST || "127.0.0.1";
  const port = Number(env.WORKBENCH_WEB_PORT || "5173");
  const apiTarget = env.WORKBENCH_API_TARGET || "http://127.0.0.1:8000";

  return {
    plugins: [react(), surgicalUiReloader()],
    server: {
      host,
      port,
      strictPort: true,
      watch: {
        ignored: [
          "**/dist/**",
          "**/runtime/**",
          "**/workspaces/**",
          "**/tests/**",
          "**/*.log",
        ],
      },
      proxy: {
        "/api": {
          target: apiTarget,
          changeOrigin: true,
        },
        "/web-proxy": {
          target: apiTarget,
          changeOrigin: true,
          ws: true,
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
        "/web-proxy": {
          target: apiTarget,
          changeOrigin: true,
          ws: true,
        },
      },
    },
  };
});
