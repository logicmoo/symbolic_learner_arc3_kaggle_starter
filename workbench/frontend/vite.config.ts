import { readFileSync, readdirSync } from "node:fs";
import { relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { parse } from "@babel/parser";
import { defineConfig, loadEnv, type Plugin, type ProxyOptions } from "vite";
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

function pluginProxy(apiTarget: string): Record<string, ProxyOptions> {
  return Object.fromEntries(
    pluginProxyPrefixes().map((prefix) => [
      prefix,
      { target: apiTarget, changeOrigin: true, ws: true } satisfies ProxyOptions,
    ]),
  );
}

// Anything the dev/preview server does not own itself resolves against the API.
// A plugin route, a mounted redirect, or any other backend path therefore works
// from the web port without being enumerated here. The exclusions are the paths
// Vite must keep serving: the app shell, its module graph, and its assets.
const VITE_OWNED = [
  "$",
  "\\?",
  "@vite",
  "@id",
  "@fs",
  "@react-refresh",
  "__vite",
  "src/",
  "node_modules/",
  "assets/",
  "index\\.html",
  "favicon\\.ico",
].join("|");
const API_FALLBACK = `^/(?!${VITE_OWNED}).+`;

function apiProxy(apiTarget: string): Record<string, ProxyOptions> {
  return {
    "/api": { target: apiTarget, changeOrigin: true },
    ...pluginProxy(apiTarget),
    [API_FALLBACK]: { target: apiTarget, changeOrigin: true, ws: true },
  };
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

function tsxSourceLocations(): Plugin {
  const sourceRoot = resolve(HERE, "src");
  const normalizedSourceRoot = sourceRoot.replaceAll("\\", "/").toLowerCase();
  return {
    name: "workbench-tsx-source-locations",
    enforce: "pre",
    transform(code, id) {
      const sourceId = id.split("?", 1)[0];
      const normalizedSourceId = sourceId.replaceAll("\\", "/");
      if (!normalizedSourceId.endsWith(".tsx") || !normalizedSourceId.toLowerCase().startsWith(normalizedSourceRoot)) return;
      const source = parse(code, {
        sourceType: "module",
        sourceFilename: sourceId,
        plugins: ["typescript", "jsx"],
      });
      const displayPath = `src/${normalizedSourceId.slice(normalizedSourceRoot.length + 1)}`;
      const insertions: Array<{ position: number; value: string }> = [];
      const visit = (node: { type: string; [key: string]: unknown }) => {
        if (node.type === "JSXOpeningElement") {
          const opening = node as unknown as {
            name: { type: string; name?: string; end?: number };
            attributes: Array<{ type: string; name?: { name?: string } }>;
            loc?: { start: { line: number } };
          };
          const tag = opening.name.type === "JSXIdentifier" ? opening.name.name || "" : "";
          if (/^[a-z]/.test(tag) && opening.name.end !== undefined && !opening.attributes.some(attribute =>
            attribute.type === "JSXAttribute" && attribute.name?.name === "data-tsx-source"
          )) {
            const line = opening.loc?.start.line || 1;
            insertions.push({
              position: opening.name.end,
              value: ` data-tsx-source=${JSON.stringify(`${displayPath}:${line}`)}`,
            });
          }
        }
        for (const value of Object.values(node)) {
          if (Array.isArray(value)) {
            for (const child of value) {
              if (child && typeof child === "object" && "type" in child) {
                visit(child as { type: string; [key: string]: unknown });
              }
            }
          } else if (value && typeof value === "object" && "type" in value) {
            visit(value as { type: string; [key: string]: unknown });
          }
        }
      };
      visit(source.program as unknown as { type: string; [key: string]: unknown });
      if (!insertions.length) return;
      let transformed = code;
      for (const insertion of insertions.sort((left, right) => right.position - left.position)) {
        transformed = `${transformed.slice(0, insertion.position)}${insertion.value}${transformed.slice(insertion.position)}`;
      }
      return { code: transformed, map: null };
    },
  };
}

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, ".", "");
  const host = env.WORKBENCH_WEB_HOST || "127.0.0.1";
  const port = Number(env.WORKBENCH_WEB_PORT || "5173");
  const apiTarget = env.WORKBENCH_API_TARGET || "http://127.0.0.1:8000";

  return {
    plugins: [tsxSourceLocations(), react(), surgicalUiReloader()],
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
      proxy: apiProxy(apiTarget),
    },
    preview: {
      host,
      port,
      strictPort: true,
      proxy: apiProxy(apiTarget),
    },
  };
});
