import type { Extension } from "@codemirror/state";
import { css } from "@codemirror/lang-css";
import { html } from "@codemirror/lang-html";
import { javascript } from "@codemirror/lang-javascript";
import { json } from "@codemirror/lang-json";
import { markdown } from "@codemirror/lang-markdown";
import { python } from "@codemirror/lang-python";

// Shared CodeMirror language extensions selected by file extension. Central so
// every editor (docs, workspace files, resource source, chat) highlights the
// same way. MeTTa has no official grammar yet -> plain text (no extension).
export function syntaxExtensionsFor(path: string): Extension[] {
  const suffix = path.toLowerCase().split(".").pop();
  if (suffix === "json" || suffix === "ipynb") return [json()];
  if (suffix === "md" || suffix === "markdown") return [markdown()];
  if (suffix === "py") return [python()];
  if (["js", "mjs", "cjs", "ts", "tsx", "jsx"].includes(suffix || ""))
    return [javascript({ typescript: suffix === "ts" || suffix === "tsx", jsx: suffix === "tsx" || suffix === "jsx" })];
  if (suffix === "css") return [css()];
  if (suffix === "html" || suffix === "htm") return [html()];
  return [];
}

// Coarse file kind used to decide which editor tab frames to show.
export function fileKindOf(path: string): "markdown" | "json" | "metta" | "code" | "text" {
  const suffix = path.toLowerCase().split(".").pop() || "";
  if (suffix === "md" || suffix === "markdown") return "markdown";
  if (suffix === "json" || suffix === "jsonl" || suffix === "ipynb") return "json";
  if (suffix === "metta") return "metta";
  if (["py", "js", "mjs", "cjs", "ts", "tsx", "jsx", "css", "html", "htm", "pl", "prolog"].includes(suffix)) return "code";
  return "text";
}
