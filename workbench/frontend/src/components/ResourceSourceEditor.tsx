import { useEffect, useMemo, useRef, useState } from "react";
import type { CSSProperties, ReactNode } from "react";
import CodeMirror from "@uiw/react-codemirror";
import { json } from "@codemirror/lang-json";
import { MarkdownDocument } from "./MarkdownDocument";
import { syntaxExtensionsFor } from "../lib/editorLanguages";
import { jsonDocumentToMetta, mettaDocumentToJson } from "../lib/mettaResourceCodec";
import { useUserUiPreferences } from "../lib/uiPreferences";
import { WorkspaceResourceFileControls, type WorkspaceResourceFileControlsProps } from "./WorkspaceResourceFileControls";
import "../styles/operation_editor.css";

type Props = { value: string; onChange: (json: string) => void; onValidityChange?: (valid: boolean) => void; className?: string; style?: CSSProperties; label?: string; showEnablement?: boolean; disabled?: boolean; path?: string; onSave?: () => void; saving?: boolean; onNavigateMarkdown?: (href: string) => void; navigateAllLocal?: boolean; fill?: boolean; fileControls?: Omit<WorkspaceResourceFileControlsProps, "disabled" | "content" | "onClientContent"> };

type JsonValue = null | boolean | number | string | JsonValue[] | { [key: string]: JsonValue };
type JsonObject = { [key: string]: JsonValue };
type JsonPathToken = string | number;

function jsonTypeLabel(value: JsonValue): string {
  if (Array.isArray(value)) return `array(len:${value.length})`;
  if (value === null) return "null";
  switch (typeof value) {
    case "string":
      return `string(${value.length})`;
    case "number":
      return Number.isInteger(value) ? "integer" : "number";
    case "boolean":
      return "boolean";
    default:
      return `object(${Object.keys(value).length})`;
  }
}

function jsonObjectField(value: JsonValue, field: string): string | null {
  if (!value || typeof value !== "object" || Array.isArray(value)) return null;
  const map = value as JsonObject;
  const direct = map[field];
  if (typeof direct === "string" && direct.trim()) return direct.trim();
  const target = field.toLowerCase();
  for (const [key, raw] of Object.entries(map)) {
    if (key.toLowerCase() === target && typeof raw === "string" && raw.trim()) return raw.trim();
  }
  return null;
}

function keysMatchingSuffix(value: JsonValue, suffixPattern: RegExp): string[] {
  if (!value || typeof value !== "object" || Array.isArray(value)) return [];
  return Object.keys(value as JsonObject).filter((key) => suffixPattern.test(key));
}

function firstStringFromKeys(value: JsonValue, keys: string[]): string | null {
  if (!value || typeof value !== "object" || Array.isArray(value)) return null;
  const map = value as JsonObject;
  for (const key of keys) {
    const raw = map[key];
    if (typeof raw === "string" && raw.trim()) return raw.trim();
  }
  return null;
}

function jsonObjectIdentifier(value: JsonValue): string | null {
  const direct = jsonObjectField(value, "id") || jsonObjectField(value, "key");
  if (direct) return direct;
  return firstStringFromKeys(value, keysMatchingSuffix(value, /(^|[_-])(id|key)$/i));
}

function jsonObjectKinds(value: JsonValue): string[] {
  const kinds: string[] = [];
  const pushUnique = (key: string) => {
    const item = jsonObjectField(value, key);
    if (item && !kinds.includes(item)) kinds.push(item);
  };
  pushUnique("subkind");
  pushUnique("kind");
  pushUnique("role");
  for (const item of keysMatchingSuffix(value, /(kind|role)$/i)) {
    const text = jsonObjectField(value, item);
    if (text && !kinds.includes(text)) kinds.push(text);
  }
  return kinds;
}

function jsonObjectKindValue(value: JsonValue): string | null {
  return jsonObjectField(value, "kind")
    || jsonObjectField(value, "type")
    || firstStringFromKeys(value, keysMatchingSuffix(value, /(^|[_-])(kind|type)$/i));
}

function jsonObjectSubkindValue(value: JsonValue): string | null {
  return jsonObjectField(value, "subkind") || firstStringFromKeys(value, keysMatchingSuffix(value, /(^|[_-])subkind$/i));
}

function jsonObjectRoleValue(value: JsonValue): string | null {
  return jsonObjectField(value, "role") || firstStringFromKeys(value, keysMatchingSuffix(value, /(^|[_-])role$/i));
}

function normalizedKindLabels(kind: string | null, subkind: string | null): { kind: string | null; subkind: string | null } {
  if (kind && subkind && /_defined_by_json$/i.test(kind) && !/_defined_by_json$/i.test(subkind)) {
    return { kind: subkind, subkind: kind };
  }
  return { kind, subkind };
}

function jsonObjectNameLike(value: JsonValue): string | null {
  const direct = jsonObjectField(value, "name") || jsonObjectField(value, "label");
  if (direct) return direct;
  return firstStringFromKeys(value, keysMatchingSuffix(value, /(^|[_-])(name|label)$/i));
}

function jsonObjectParentName(value: JsonValue): string | null {
  return jsonObjectField(value, "parentName") || jsonObjectField(value, "parent_name");
}

function longestStringInDict(value: JsonValue): { text: string; keyed: boolean } | null {
  let longest = "";
  let longestKeyed = false;
  const visit = (node: JsonValue, depth: number, keyed: boolean) => {
    if (depth > 4) return;
    if (typeof node === "string") {
      if (node.length > longest.length) {
        longest = node;
        longestKeyed = keyed;
      }
      return;
    }
    if (Array.isArray(node)) {
      node.forEach((entry) => visit(entry, depth + 1, false));
      return;
    }
    if (node && typeof node === "object") {
      Object.values(node).forEach((entry) => visit(entry, depth + 1, true));
    }
  };
  visit(value, 0, false);
  return longest.trim() ? { text: longest.trim(), keyed: longestKeyed } : null;
}

function jsonNodeSummary(value: JsonValue): string {
  const parts = jsonNodeSummaryParts(value);
  const tags = [
    parts.id ? `id:${parts.id}` : "",
    parts.kind ? `kind:${parts.kind}` : "",
    parts.name ? `name:${parts.name}` : "",
  ].filter(Boolean);
  return tags.length ? `${tags.join(" · ")} · ${parts.type}` : parts.type;
}

function jsonNodeSummaryParts(value: JsonValue): { id: string | null; kind: string | null; name: string | null; type: string } {
  const normalizedKinds = normalizedKindLabels(jsonObjectKindValue(value), jsonObjectSubkindValue(value));
  return {
    id: jsonObjectIdentifier(value),
    kind: normalizedKinds.kind,
    name: jsonObjectNameLike(value),
    type: jsonTypeLabel(value),
  };
}

function jsonObjectTokenGroup(value: JsonValue, exactKeys: string[], suffixPattern: RegExp): Array<{ label: string; value: string }> {
  if (!value || typeof value !== "object" || Array.isArray(value)) return [];
  const map = value as JsonObject;
  const exact = new Set(exactKeys.map((key) => key.toLowerCase()));
  const seen = new Set<string>();
  const tokens: Array<{ label: string; value: string }> = [];
  for (const [rawKey, rawValue] of Object.entries(map)) {
    if (typeof rawValue !== "string") continue;
    const trimmed = rawValue.trim();
    if (!trimmed) continue;
    const key = rawKey.toLowerCase();
    if (!exact.has(key) && !suffixPattern.test(rawKey)) continue;
    const identity = `${key}:${trimmed}`;
    if (seen.has(identity)) continue;
    seen.add(identity);
    tokens.push({ label: key, value: trimmed });
  }
  return tokens;
}

function jsonNodePromotedTokens(value: JsonValue): Array<{ className: string; text: string }> {
  const idTokens = jsonObjectTokenGroup(value, ["id", "key"], /(^|[_-])(id|key)$/i)
    .map((item) => ({ className: "json-tree-token-id", text: `${item.label}:${item.value}` }));
  const kindTokens = jsonObjectTokenGroup(value, ["kind", "type", "role"], /(^|[_-])(kind|type|role)$/i)
    .map((item) => ({ className: "json-tree-token-kind", text: `${item.label}:${item.value}` }));
  const nameTokens = jsonObjectTokenGroup(value, ["name", "label"], /(^|[_-])(name|label)$/i)
    .map((item) => ({ className: "json-tree-token-name", text: `${item.label}:${item.value}` }));
  return [...idTokens, ...kindTokens, ...nameTokens];
}

function jsonNodeTooltip(value: JsonValue): { text: string; source: "length" | "description" | "longest"; keyed: boolean } | null {
  if (Array.isArray(value)) {
    return { text: `length: ${value.length}`, source: "length", keyed: false };
  }
  const explicit = jsonObjectField(value, "description");
  if (explicit) return { text: explicit, source: "description", keyed: true };
  const longest = longestStringInDict(value);
  if (!longest) return null;
  return { text: longest.text, source: "longest", keyed: longest.keyed };
}

function formatPrimitivePreview(value: JsonValue): string {
  if (value === null) return "null";
  if (typeof value === "string") return `"${value}"`;
  if (typeof value === "boolean") return value ? "true" : "false";
  if (typeof value === "number") return `${value}`;
  return "…";
}

function simpleValueDisplay(value: JsonValue): string | null {
  if (Array.isArray(value)) return null;
  if (value && typeof value === "object") return null;
  return formatPrimitivePreview(value);
}

function arrayPreviewInfo(value: JsonValue, suppressValue: string | null = null): { mode: "horizontal" | "vertical"; values: string[]; truncated: boolean } | null {
  if (!Array.isArray(value) || value.length === 0) return null;
  const previewValues = value.slice(0, 8).filter((entry) => !(typeof entry === "string" && suppressValue && entry.trim() === suppressValue.trim()));
  if (previewValues.length === 0) return null;
  const allStrings = previewValues.every((entry) => typeof entry === "string");
  const hasNonAlphaNumericString = allStrings && previewValues.some((entry) => /[^A-Za-z0-9]/.test(entry as string));
  return {
    mode: hasNonAlphaNumericString ? "vertical" : "horizontal",
    values: previewValues.map((entry) => formatPrimitivePreview(entry)),
    truncated: value.length > previewValues.length,
  };
}

function collectExpandablePaths(value: JsonValue, path: string, out: Set<string>) {
  if (Array.isArray(value)) {
    out.add(path);
    value.forEach((entry, index) => collectExpandablePaths(entry, `${path}[${index}]`, out));
    return;
  }
  if (value && typeof value === "object") {
    out.add(path);
    Object.entries(value).forEach(([key, entry]) => collectExpandablePaths(entry, path === "$" ? `$.${key}` : `${path}.${key}`, out));
  }
}

function parseJsonPath(path: string): JsonPathToken[] {
  if (!path.startsWith("$")) return [];
  const tokens: JsonPathToken[] = [];
  let index = 1;
  while (index < path.length) {
    const char = path[index];
    if (char === ".") {
      index += 1;
      const start = index;
      while (index < path.length && path[index] !== "." && path[index] !== "[") index += 1;
      const key = path.slice(start, index);
      if (key) tokens.push(key);
      continue;
    }
    if (char === "[") {
      const end = path.indexOf("]", index);
      if (end <= index + 1) break;
      const numberText = path.slice(index + 1, end);
      const parsed = Number.parseInt(numberText, 10);
      if (!Number.isNaN(parsed)) tokens.push(parsed);
      index = end + 1;
      continue;
    }
    index += 1;
  }
  return tokens;
}

function getNodeAtPath(root: JsonValue, path: string): JsonValue | null {
  const tokens = parseJsonPath(path);
  let current: JsonValue = root;
  for (const token of tokens) {
    if (typeof token === "number") {
      if (!Array.isArray(current) || token < 0 || token >= current.length) return null;
      current = current[token];
      continue;
    }
    if (!current || typeof current !== "object" || Array.isArray(current) || !(token in current)) return null;
    current = (current as JsonObject)[token];
  }
  return current;
}

function updateJsonAtPath(root: JsonObject, path: string, updater: (target: JsonValue, parent: JsonValue | null, key: JsonPathToken | null) => JsonValue | null): JsonObject | null {
  const tokens = parseJsonPath(path);
  const cloned = JSON.parse(JSON.stringify(root)) as JsonObject;
  if (tokens.length === 0) return null;
  let parent: JsonValue | null = null;
  let current: JsonValue = cloned;
  let currentKey: JsonPathToken | null = null;
  for (const token of tokens) {
    parent = current;
    currentKey = token;
    if (typeof token === "number") {
      if (!Array.isArray(current) || token < 0 || token >= current.length) return null;
      current = current[token];
    } else {
      if (!current || typeof current !== "object" || Array.isArray(current) || !(token in current)) return null;
      current = (current as JsonObject)[token];
    }
  }
  const next = updater(current, parent, currentKey);
  if (next === null) {
    if (parent === null || currentKey === null) return null;
    if (typeof currentKey === "number") {
      if (!Array.isArray(parent)) return null;
      parent.splice(currentKey, 1);
    } else {
      if (!parent || typeof parent !== "object" || Array.isArray(parent)) return null;
      delete (parent as JsonObject)[currentKey];
    }
    return cloned;
  }
  if (parent === null || currentKey === null) return cloned;
  if (typeof currentKey === "number") {
    if (!Array.isArray(parent) || currentKey < 0 || currentKey >= parent.length) return null;
    parent[currentKey] = next;
  } else {
    if (!parent || typeof parent !== "object" || Array.isArray(parent)) return null;
    (parent as JsonObject)[currentKey] = next;
  }
  return cloned;
}

export function ResourceSourceEditor({ value, onChange, onValidityChange, className = "", style, label = "Edit this resource directly", showEnablement = true, disabled = false, path, onSave, saving = false, onNavigateMarkdown, navigateAllLocal = false, fill = false, fileControls }: Props) {
  const { resourceSourceFileControlsPlacement } = useUserUiPreferences();
  const [format, setFormat] = useState<"metta" | "json" | "tree" | "markdown" | "text">("metta");
  const [display, setDisplay] = useState<"tabs" | "stack">("tabs");
  const [metta, setMetta] = useState("");
  const [jsonDraft, setJsonDraft] = useState(value);
  const [error, setError] = useState("");
  const [treeExpandedPaths, setTreeExpandedPaths] = useState<Set<string>>(new Set(["$"]));
  const [selectedTreePath, setSelectedTreePath] = useState("$");
  const [treeRenderNormal, setTreeRenderNormal] = useState(false);
  const [contextMenu, setContextMenu] = useState<{ x: number; y: number; path: string } | null>(null);
  const emittedJson = useRef<string | null>(null);

  // Purely content-driven: structured (JSON object, or MeTTa convertible to one) ->
  // offer MeTTa/JSON/Tree; otherwise edit as plain text. Markdown render is always
  // available. sourceLang is the language edits are emitted back in.
  const detect = useMemo(() => {
    if (!value.trim()) return { structured: false, lang: "text" as "json" | "metta" | "text", json: value };
    try { const p = JSON.parse(value); if (p && typeof p === "object" && !Array.isArray(p)) return { structured: true, lang: "json" as "json" | "metta" | "text", json: value }; } catch { /* not json */ }
    try { const j = mettaDocumentToJson(value); const p = JSON.parse(j); if (p && typeof p === "object" && !Array.isArray(p)) return { structured: true, lang: "metta" as "json" | "metta" | "text", json: j }; } catch { /* not metta */ }
    return { structured: false, lang: "text" as "json" | "metta" | "text", json: value };
  }, [value]);
  const structured = detect.structured;
  const sourceLang = detect.lang;

  useEffect(() => {
    if (value === emittedJson.current) { emittedJson.current = null; setJsonDraft(value); return; }
    if (!value) { setJsonDraft(""); setMetta(""); setError(""); onValidityChange?.(true); return; }
    if (!structured) { setJsonDraft(value); setMetta(""); setError(""); onValidityChange?.(true); return; }
    setJsonDraft(detect.json);
    try { setMetta(sourceLang === "metta" ? value : jsonDocumentToMetta(detect.json)); setError(""); onValidityChange?.(true); }
    catch (reason) { setError(reason instanceof Error ? reason.message : String(reason)); onValidityChange?.(false); }
  }, [value, structured, sourceLang, detect.json]);

  // Keep the active tab valid for the detected content.
  useEffect(() => {
    setFormat((current) => structured ? (current === "text" ? "metta" : current) : (current === "markdown" ? "markdown" : "text"));
  }, [structured]);

  const editMetta = (next: string) => {
    setMetta(next);
    try { const json = mettaDocumentToJson(next); setJsonDraft(json); const out = sourceLang === "metta" ? next : json; emittedJson.current = out; onChange(out); setError(""); onValidityChange?.(true); }
    catch (reason) { setError(reason instanceof Error ? reason.message : String(reason)); onValidityChange?.(false); }
  };
  const editJson = (next: string) => {
    setJsonDraft(next);
    try {
      const parsed = JSON.parse(next);
      if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) throw new Error("A resource document must be a JSON object");
      setMetta(jsonDocumentToMetta(next)); const out = sourceLang === "metta" ? jsonDocumentToMetta(next) : next; emittedJson.current = out; onChange(out); setError(""); onValidityChange?.(true);
    } catch (reason) { setError(reason instanceof Error ? reason.message : String(reason)); onValidityChange?.(false); }
  };
  const editText = (next: string) => { setJsonDraft(next); emittedJson.current = next; onChange(next); setError(""); onValidityChange?.(true); };
  const loadClientContent = (content: string) => {
    try {
      const parsed = JSON.parse(content);
      if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) throw new Error("A resource document must be a JSON object");
      onChange(`${JSON.stringify(parsed, null, 2)}\n`);
    } catch {
      onChange(mettaDocumentToJson(content));
    }
  };
  // A "resource" is a structured document that declares a kind ? only then do we
  // show resource affordances (enable/disable).
  let resource: Record<string, unknown> | null = null;
  try { const parsed = JSON.parse(detect.json); if (parsed && typeof parsed === "object" && !Array.isArray(parsed) && "kind" in parsed) resource = parsed; } catch { /* Invalid source remains editable. */ }
  const resourceEnabled = resource?.enabled !== false;
  const setEnabled = (enabled: boolean) => { if (!disabled && resource) onChange(JSON.stringify({ ...resource, enabled }, null, 2)); };
  const parsedTreeRoot = useMemo(() => {
    try {
      const parsed = JSON.parse(value);
      if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) return null;
      return parsed as JsonObject;
    } catch {
      return null;
    }
  }, [value]);
  const allExpandablePaths = useMemo(() => {
    const paths = new Set<string>();
    if (parsedTreeRoot) collectExpandablePaths(parsedTreeRoot, "$", paths);
    return paths;
  }, [parsedTreeRoot]);
  const treeSelectionType = useMemo(() => {
    if (!parsedTreeRoot) return "";
    const selected = getNodeAtPath(parsedTreeRoot, selectedTreePath);
    return selected === null ? "missing" : treeRenderNormal ? jsonTypeLabel(selected) : jsonNodeSummary(selected);
  }, [parsedTreeRoot, selectedTreePath, treeRenderNormal]);

  useEffect(() => {
    if (!contextMenu) return;
    const close = () => setContextMenu(null);
    const closeOnEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape") close();
    };
    window.addEventListener("click", close);
    window.addEventListener("keydown", closeOnEscape);
    return () => {
      window.removeEventListener("click", close);
      window.removeEventListener("keydown", closeOnEscape);
    };
  }, [contextMenu]);

  const togglePath = (path: string) => {
    setTreeExpandedPaths((previous) => {
      const next = new Set(previous);
      if (next.has(path)) next.delete(path);
      else next.add(path);
      return next;
    });
  };

  const expandSelectedBranch = () => {
    if (!parsedTreeRoot) return;
    setTreeExpandedPaths((previous) => {
      const next = new Set(previous);
      const prefixDot = `${selectedTreePath}.`;
      const prefixBracket = `${selectedTreePath}[`;
      for (const candidate of allExpandablePaths) {
        if (candidate === selectedTreePath || candidate.startsWith(prefixDot) || candidate.startsWith(prefixBracket)) {
          next.add(candidate);
        }
      }
      return next;
    });
  };

  const collapseSelectedBranch = () => {
    setTreeExpandedPaths((previous) => {
      const next = new Set(previous);
      const prefixDot = `${selectedTreePath}.`;
      const prefixBracket = `${selectedTreePath}[`;
      for (const candidate of Array.from(next)) {
        if (candidate !== selectedTreePath && (candidate.startsWith(prefixDot) || candidate.startsWith(prefixBracket))) {
          next.delete(candidate);
        }
      }
      if (selectedTreePath !== "$") {
        next.delete(selectedTreePath);
      }
      next.add("$");
      return next;
    });
  };

  const collapseSelectedChildren = () => {
    setTreeExpandedPaths((previous) => {
      const next = new Set(previous);
      const prefixDot = `${selectedTreePath}.`;
      const prefixBracket = `${selectedTreePath}[`;
      for (const candidate of Array.from(next)) {
        if (candidate.startsWith(prefixDot) || candidate.startsWith(prefixBracket)) {
          next.delete(candidate);
        }
      }
      next.add("$");
      next.add(selectedTreePath);
      return next;
    });
  };

  const writeTreeDocument = (nextRoot: JsonObject) => {
    const nextText = `${JSON.stringify(nextRoot, null, 2)}\n`;
    emittedJson.current = nextText;
    onChange(nextText);
  };

  const addKeyAtPath = (path: string) => {
    if (disabled || !parsedTreeRoot) return;
    const node = getNodeAtPath(parsedTreeRoot, path);
    if (!node || typeof node !== "object" || Array.isArray(node)) return;
    const key = window.prompt("New key name");
    if (!key || !key.trim()) return;
    const valueInput = window.prompt("New value (JSON literal or plain text)", "\"\"");
    if (valueInput === null) return;
    let nextValue: JsonValue;
    try {
      nextValue = JSON.parse(valueInput) as JsonValue;
    } catch {
      nextValue = valueInput;
    }
    const updated = updateJsonAtPath(parsedTreeRoot, path, (target) => {
      if (!target || typeof target !== "object" || Array.isArray(target)) return target;
      return { ...(target as JsonObject), [key.trim()]: nextValue };
    });
    if (updated) writeTreeDocument(updated);
  };

  const deleteAtPath = (path: string) => {
    if (disabled || !parsedTreeRoot || path === "$") return;
    if (!window.confirm(`Delete ${path}?`)) return;
    const updated = updateJsonAtPath(parsedTreeRoot, path, () => null);
    if (updated) writeTreeDocument(updated);
  };

  const renderTreeNode = (node: JsonValue, path: string, labelText: string): ReactNode => {
    const isArray = Array.isArray(node);
    const isObject = Boolean(node && typeof node === "object" && !isArray);
    const children: Array<[string, JsonValue, string]> = isArray
      ? (node as JsonValue[]).map((entry, index) => {
        const entryId = jsonObjectIdentifier(entry);
        const entryKind = jsonObjectKinds(entry)[0] || null;
        const entryName = jsonObjectNameLike(entry);
        const preferredLabel = treeRenderNormal ? `[${index}]` : (entryName || entryId || entryKind || `[${index}]`);
        return [`${path}[${index}]`, entry, preferredLabel];
      })
      : isObject
        ? (() => {
          const mapNode = node as JsonObject;
          const suppressMetadataKeys = new Set<string>();
          if (!treeRenderNormal && jsonObjectIdentifier(node)) {
            suppressMetadataKeys.add("id");
            Object.keys(mapNode).forEach((key) => { if (/_id$/i.test(key)) suppressMetadataKeys.add(key); });
          }
          if (!treeRenderNormal && jsonObjectKinds(node).length > 0) {
            suppressMetadataKeys.add("subkind");
            suppressMetadataKeys.add("kind");
            suppressMetadataKeys.add("role");
            Object.keys(mapNode).forEach((key) => { if (/(kind|role)$/i.test(key)) suppressMetadataKeys.add(key); });
          }
          if (!treeRenderNormal && jsonObjectNameLike(node)) {
            suppressMetadataKeys.add("label");
            suppressMetadataKeys.add("name");
            suppressMetadataKeys.add("parentName");
            suppressMetadataKeys.add("parent_name");
            Object.keys(mapNode).forEach((key) => { if (/(name|label)$/i.test(key)) suppressMetadataKeys.add(key); });
          }
          if (!treeRenderNormal && jsonObjectField(node, "description")) {
            suppressMetadataKeys.add("description");
          }
          return Object.entries(mapNode)
            .filter(([key]) => !suppressMetadataKeys.has(key))
            .map(([key, entry]) => [path === "$" ? `$.${key}` : `${path}.${key}`, entry, key]);
        })()
        : [];
    const hasChildren = children.length > 0;
    const expanded = treeExpandedPaths.has(path);
    const selected = selectedTreePath === path;

    const tooltip = jsonNodeTooltip(node);
    const preview = arrayPreviewInfo(
      node,
      tooltip && tooltip.source === "longest" && !tooltip.keyed ? tooltip.text : null,
    );
    const inlineValue = simpleValueDisplay(node);
    const promotedTokens = jsonNodePromotedTokens(node);
    const detailText = inlineValue ?? (treeRenderNormal ? jsonTypeLabel(node) : jsonNodeSummary(node));
    return <div key={path} className="json-tree-node">
      <div className={`json-tree-row ${selected ? "selected" : ""}`} onContextMenu={(event) => {
        if (disabled) return;
        event.preventDefault();
        setSelectedTreePath(path);
        setContextMenu({ x: event.clientX, y: event.clientY, path });
      }}>
        <button type="button" className="json-tree-toggle" disabled={disabled || !hasChildren} onClick={() => togglePath(path)}>{hasChildren ? (expanded ? "▾" : "▸") : "·"}</button>
        <button type="button" className="json-tree-label" title={tooltip?.text || undefined} disabled={disabled} onClick={() => setSelectedTreePath(path)}>
          <span className="json-tree-main">
            <code>{labelText}</code>
            {inlineValue || treeRenderNormal
              ? <span>{detailText}</span>
              : <span className="json-tree-metadata">
                {promotedTokens.length
                  ? promotedTokens.map((token, index) => <span key={`${path}-token-${index}`} className={`json-tree-token ${token.className}`}>{index > 0 ? <span className="json-tree-token-sep"> · </span> : null}{token.text}</span>)
                  : <span>{detailText}</span>}
              </span>}
          </span>
          {preview
            ? <span className={`json-tree-array-preview ${preview.mode}`}>
              {preview.values.map((entry, index) => <span key={`${path}-preview-${index}`}>{entry}</span>)}
              {preview.truncated ? <span>…</span> : null}
            </span>
            : null}
        </button>
      </div>
      {hasChildren && expanded ? <div className="json-tree-children">{children.map(([childPath, childNode, childLabel]) => renderTreeNode(childNode, childPath, childLabel))}</div> : null}
    </div>;
  };

  const renderedFileControls = fileControls
    ? <WorkspaceResourceFileControls {...fileControls} content={format === "metta" ? metta : jsonDraft} onClientContent={loadClientContent} disabled={disabled} />
    : null;

  // Each tab's existence will later be gated by a detection policy; for now every
  // tab is offered (show: true). `structured` still drives the sensible default tab.
  const tabPolicies: { id: "metta" | "json" | "tree" | "text" | "markdown"; label: string; show: boolean }[] = [
    { id: "metta", label: "MeTTa", show: true },
    { id: "json", label: "JSON", show: true },
    { id: "tree", label: "Tree", show: true },
    { id: "text", label: "Text", show: true },
    { id: "markdown", label: "Markdown", show: true },
  ];
  const renderFormatBody = (fmt: "metta" | "json" | "tree" | "markdown" | "text") => {
    if (fmt === "tree") return <div className={`json-tree-browser operation-visible-editor ${className}`.trim()} style={style}>
        <div className="json-tree-toolbar">
          <span>Path <code>{selectedTreePath}</code>{treeSelectionType ? <> &middot; <b>{treeSelectionType}</b></> : null}</span>
          <div>
            <button type="button" className={treeRenderNormal ? "active" : ""} disabled={disabled || !parsedTreeRoot} onClick={() => setTreeRenderNormal((previous) => !previous)}>{treeRenderNormal ? "Enhanced labels" : "Normal labels"}</button>
            <button type="button" disabled={disabled || !parsedTreeRoot} onClick={() => expandSelectedBranch()}>Expand branch</button>
            <button type="button" disabled={disabled || !parsedTreeRoot} onClick={() => collapseSelectedBranch()}>Collapse branch</button>
            <button type="button" disabled={disabled || !parsedTreeRoot} onClick={() => collapseSelectedChildren()}>Collapse children</button>
            <button type="button" disabled={disabled || !parsedTreeRoot} onClick={() => setTreeExpandedPaths(new Set(allExpandablePaths))}>Expand all</button>
            <button type="button" disabled={disabled || !parsedTreeRoot} onClick={() => setTreeExpandedPaths(new Set(["$"]))}>Collapse all</button>
          </div>
        </div>
        {parsedTreeRoot ? <div className="json-tree-root">{renderTreeNode(parsedTreeRoot, "$", "$")}</div> : <div className="validation bad">Tree mode needs valid JSON object source. Fix syntax in JSON or MeTTa mode first.</div>}
        {contextMenu && parsedTreeRoot ? <div className="json-tree-context-menu" style={{ left: contextMenu.x, top: contextMenu.y }}>
          <button type="button" onClick={() => { addKeyAtPath(contextMenu.path); setContextMenu(null); }}>Add key</button>
          <button type="button" disabled={contextMenu.path === "$"} onClick={() => { deleteAtPath(contextMenu.path); setContextMenu(null); }}>Delete element</button>
          <button type="button" onClick={() => setContextMenu(null)}>Cancel</button>
        </div> : null}
      </div>;
    if (fmt === "markdown") return <div className={`raw-json-editor operation-visible-editor ${className}`.trim()} style={style}><MarkdownDocument content={jsonDraft} navigateAllLocal={navigateAllLocal} onNavigateMarkdown={onNavigateMarkdown} /></div>;
    if (fmt === "text") return <div className={`raw-json-editor operation-visible-editor ${className}`.trim()} style={style}><CodeMirror value={jsonDraft} height="100%" theme="dark" editable={!disabled} readOnly={disabled} basicSetup={{ lineNumbers: true, foldGutter: true, highlightActiveLine: !disabled }} extensions={syntaxExtensionsFor(path || "")} onChange={editText} /></div>;
    return <div className={`raw-json-editor operation-visible-editor ${className}`.trim()} style={style} aria-invalid={Boolean(error)}><CodeMirror value={fmt === "metta" ? metta : jsonDraft} height="100%" theme="dark" editable={!disabled} readOnly={disabled} basicSetup={{ lineNumbers: true, foldGutter: true, highlightActiveLine: !disabled }} extensions={fmt === "json" ? [json()] : []} onChange={value => fmt === "metta" ? editMetta(value) : editJson(value)} /></div>;
  };
  return <div className={`operation-json-block resource-source-editor${fill ? " fill" : ""}`}>
    <div className="llm-subhead"><div><span>RESOURCE SOURCE</span><b>{label}</b></div><div className="source-format-tabs"><button disabled={disabled} className="resource-enable-action" title="Switch tabbed / stacked view" onClick={()=>setDisplay(d=>d==="tabs"?"stack":"tabs")}>{display==="tabs"?"Stack":"Tabs"}</button>{showEnablement&&resource&&<button disabled={disabled} className={`resource-enable-action ${resourceEnabled?"disable-resource":"enable-resource"}`} onClick={()=>setEnabled(!resourceEnabled)}>{resourceEnabled?"Disable Resource":"Enable Resource"}</button>}{tabPolicies.filter(t=>t.show).map(t=><button key={t.id} disabled={disabled} className={display==="tabs"&&format===t.id?"active":""} onClick={()=>{if(display==="stack"){const el=document.getElementById(`rse-sec-${t.id}`);if(el)el.scrollIntoView({behavior:"smooth",block:"start"});}else{setFormat(t.id);}}}>{t.label}</button>)}{onSave?<button disabled={disabled||saving} className="resource-enable-action" onClick={()=>onSave()}>{saving?"Saving...":"Save"}</button>:null}</div></div>
    {resourceSourceFileControlsPlacement === "above" ? renderedFileControls : null}
    {display === "stack"
      ? <div className="rse-stack">{tabPolicies.filter(t => t.show).map(t => <section key={t.id} id={`rse-sec-${t.id}`} className="rse-stack-section"><div className="rse-stack-header">{t.label}</div>{renderFormatBody(t.id)}</section>)}</div>
      : renderFormatBody(format)}
    {error && <div className="validation bad">Invalid {format === "metta" ? "MeTTa" : "JSON"} syntax: {error}. Draft preserved; synchronization and saving are paused until this is fixed.</div>}
    {resourceSourceFileControlsPlacement === "below" ? renderedFileControls : null}
  </div>;
}
