import { readFileSync, readdirSync } from "node:fs";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { defineConfig, loadEnv, type Plugin } from "vite";
import react from "@vitejs/plugin-react";

const HERE = fileURLToPath(new URL(".", import.meta.url));

// Plugins mount themselves on the workbench API port under the route prefix
// declared in their own plugin.json. The dev/preview proxy is generated from
// those manifests, plus any path another plugin asked web_proxy to mount, so a
// new plugin never needs this file edited.
function pluginProxyPrefixes(): string[] {
  const root = resolve(HERE, "../plugins");
  const prefixes = new Set<string>();
  let directories: string[] = [];
  try {
    directories = readdirSync(root, { withFileTypes: true })
      .filter((entry) => entry.isDirectory())
      .map((entry) => entry.name);
  } catch {
    return [];
  }
  const add = (value: unknown) => {
    const prefix = String(value ?? "").trim().replace(/^\/+|\/+$/g, "");
    if (prefix) prefixes.add(`/${prefix}`);
  };
  for (const name of directories) {
    try {
      const manifest = JSON.parse(readFileSync(resolve(root, name, "plugin.json"), "utf8"));
      add(manifest.routePrefix || `/plugins/${manifest.id || name}`);
      for (const mount of Array.isArray(manifest.mounts) ? manifest.mounts : []) add(mount?.path);
    } catch {
      // A plugin without a readable manifest is reported by the API catalog.
    }
  }
  return [...prefixes];
}

function pluginProxy(apiTarget: string): Record<string, unknown> {
  return Object.fromEntries(
    pluginProxyPrefixes().map((prefix) => [
      prefix,
      { target: apiTarget, changeOrigin: true, ws: true },
    ]),
  );
}

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
        ...pluginProxy(apiTarget),
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
        ...pluginProxy(apiTarget),
      },
    },
  };
});
