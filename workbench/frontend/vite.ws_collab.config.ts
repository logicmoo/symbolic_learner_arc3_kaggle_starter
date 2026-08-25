import { resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Dedicated build for the ws_collab plugin admin. It shares the workbench's
// React components (src/components, src/lib) so the controls/editors are
// maintained once, and emits a self-contained static bundle into the plugin's
// package data (ws_collab/admin/react) that the standalone/PyPI server serves.
const HERE = fileURLToPath(new URL(".", import.meta.url));

export default defineConfig({
  plugins: [react()],
  root: resolve(HERE, "src/plugins/ws_collab"),
  base: "./",
  build: {
    outDir: resolve(HERE, "../plugins/ws_collab/ws_collab/admin/react"),
    emptyOutDir: true,
    sourcemap: false,
  },
});
