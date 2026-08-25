import { useEffect, useMemo, useState, type ReactNode } from "react";
import CodeMirror from "@uiw/react-codemirror";
import { MarkdownDocument } from "./MarkdownDocument";
import { syntaxExtensionsFor } from "../lib/editorLanguages";
import "../styles/file_editor_frame.css";

export type UniversalResourceEditorProps = {
  path: string;
  format: "markdown" | "source" | "image";
  value: string;
  original?: string;
  onChange: (value: string) => void;
  onSave?: () => void;
  saving?: boolean;
  readOnly?: boolean;
  imageSrc?: string;
  onNavigateMarkdown?: (href: string) => void;
  navigateAllLocal?: boolean;
  /** Extra tab frames appended after the built-in ones (Source/Preview). */
  extraTabs?: { id: string; label: string; render: () => ReactNode }[];
  /** Extra action buttons shown in the toolbar. */
  extraActions?: ReactNode;
};

// A type-driven tabbed resource/file editor. Which tabs appear is decided by the
// file's format/extension: markdown gets Markdown (render) + Source, images get a
// single view, everything else gets Source + Markdown. New option tabs plug in via
// extraTabs — this is the universal editor legacy editors migrate onto.
export function UniversalResourceEditor({
  path, format, value, original, onChange, onSave, saving = false,
  readOnly = false, imageSrc, onNavigateMarkdown, navigateAllLocal = false, extraTabs = [], extraActions,
}: UniversalResourceEditorProps) {
  const tabs = useMemo(() => {
    const base: { id: string; label: string }[] = [];
    if (format === "image") {
      base.push({ id: "image", label: "Image" });
    } else if (format === "markdown") {
      // Markdown files default to the rendered view, with Source alongside.
      base.push({ id: "preview", label: "Markdown" });
      base.push({ id: "source", label: readOnly ? "Source (read-only)" : "Source" });
    } else {
      // Any other text file: Source first, but Markdown render is always available.
      base.push({ id: "source", label: readOnly ? "Source (read-only)" : "Source" });
      base.push({ id: "preview", label: "Markdown" });
    }
    return [...base, ...extraTabs.map((t) => ({ id: t.id, label: t.label }))];
  }, [format, readOnly, extraTabs]);

  const [active, setActive] = useState(tabs[0]?.id ?? "source");
  // Reset to the natural default tab whenever the opened file changes.
  useEffect(() => { setActive(format === "markdown" ? "preview" : format === "image" ? "image" : "source"); }, [path, format]);

  const ext = (path.split(".").pop() || "TEXT").toUpperCase();
  const dirty = original !== undefined && value !== original;
  const extra = extraTabs.find((t) => t.id === active);

  return (
    <section className="file-editor-frame">
      <div className="file-editor-tabs" role="tablist">
        {tabs.map((t) => (
          <button key={t.id} type="button" role="tab" aria-selected={active === t.id}
            className={`file-editor-tab${active === t.id ? " is-active" : ""}`} onClick={() => setActive(t.id)}>
            {t.label}
          </button>
        ))}
        <span className="file-editor-spacer" />
        <span className="file-editor-kind">{ext}</span>
        {extraActions}
        {active === "source" && !readOnly && onSave && (
          <button type="button" className="file-editor-save" disabled={saving || !dirty} onClick={onSave}>
            {saving ? "Saving…" : "Save to filesystem"}
          </button>
        )}
      </div>
      <div className="file-editor-body">
        {active === "image" && imageSrc && (
          <figure className="repository-image-view"><img src={imageSrc} alt={path} /><figcaption>{path}</figcaption></figure>
        )}
        {active === "preview" && (
          <MarkdownDocument content={value} onNavigateMarkdown={onNavigateMarkdown} navigateAllLocal={navigateAllLocal} />
        )}
        {active === "source" && (
          <CodeMirror value={value} height="100%" theme="dark" editable={!readOnly} readOnly={readOnly}
            basicSetup={{ lineNumbers: true, foldGutter: true }} extensions={syntaxExtensionsFor(path)}
            onChange={onChange} aria-label={`Edit ${path}`} />
        )}
        {extra && <div className="file-editor-extra">{extra.render()}</div>}
      </div>
    </section>
  );
}
