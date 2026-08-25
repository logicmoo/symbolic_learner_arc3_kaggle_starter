import { useState, type ReactNode } from "react";
import "../styles/super_control.css";

// A renderer contributed to the Super Control as one tab over the SAME resource.
// Built-in renderers (Source, Markdown, Config, Resource, Inheritance, Runner) and
// plugin-contributed renderers (e.g. ws_collab's "Stream") share this shape.
export type SuperRenderer = {
  id: string;
  label: string;
  render: () => ReactNode;
};

// The file capability owned by the Super Control (not by the source renderer).
export type SuperFileActions = {
  dirty?: boolean;
  busy?: boolean;
  onSave?: () => void | Promise<void>;
  onSaveAs?: () => void | Promise<void>;
  onReload?: () => void | Promise<void>;
  onDownload?: () => void | Promise<void>;
  // Extra file-scoped controls (e.g. ws_collab "Serve as stream: server / my UI").
  extraActions?: ReactNode;
};

export type SuperControlProps = {
  label?: string;
  renderers: SuperRenderer[];
  fileActions?: SuperFileActions;
  // A page declares its default view; the symmetric toggle switches between them
  // unless the page locks the view.
  initialView?: "file" | "tabs";
  lockView?: boolean;
  // Which renderer is the focused "editable file" view (defaults to the first).
  sourceRendererId?: string;
  className?: string;
};

type SplitDir = "off" | "left" | "right" | "up" | "down";

export function SuperControl({
  label,
  renderers,
  fileActions,
  initialView = "tabs",
  lockView = false,
  sourceRendererId,
  className = "",
}: SuperControlProps) {
  const [view, setView] = useState<"file" | "tabs">(initialView);
  const [activeId, setActiveId] = useState<string>(renderers[0]?.id || "");
  const [activeId2, setActiveId2] = useState<string>(renderers[1]?.id || renderers[0]?.id || "");
  const [display, setDisplay] = useState<"tabs" | "stack">("tabs");
  const [split, setSplit] = useState<SplitDir>("off");

  const sourceId = sourceRendererId || renderers[0]?.id || "";
  const rendererById = (id: string) => renderers.find((entry) => entry.id === id) || renderers[0];

  const fileToolbar = fileActions ? (
    <div className="super-file-toolbar">
      {fileActions.onSave && <button disabled={fileActions.busy || fileActions.dirty === false} onClick={() => void fileActions.onSave!()}>Save</button>}
      {fileActions.onSaveAs && <button disabled={fileActions.busy} onClick={() => void fileActions.onSaveAs!()}>Save As…</button>}
      {fileActions.onReload && <button disabled={fileActions.busy} onClick={() => void fileActions.onReload!()}>Reload</button>}
      {fileActions.onDownload && <button disabled={fileActions.busy} onClick={() => void fileActions.onDownload!()}>Download</button>}
      {fileActions.extraActions}
    </div>
  ) : null;

  if (view === "file") {
    return <section className={`super-control super-file-view ${className}`.trim()}>
      <header className="super-control-bar">
        <span className="super-control-title">{label || "FILE"}</span>
        {fileToolbar}
        {!lockView && <button className="super-view-toggle" onClick={() => setView("tabs")}>▣ Super Control</button>}
      </header>
      <div className="super-file-body">{rendererById(sourceId)?.render()}</div>
    </section>;
  }

  const paneTabs = (active: string, onPick: (id: string) => void) =>
    <div className="super-pane-tabs">{renderers.map((entry) => <button key={entry.id} className={active === entry.id ? "active" : ""} onClick={() => onPick(entry.id)}>{entry.label}</button>)}</div>;

  return <section className={`super-control super-tabs-view ${className}`.trim()}>
    <nav className="backend-aggregate-tabs" role="tablist">
      <span className="backend-tabs-label">RENDERERS</span>
      {renderers.map((entry) => <button key={entry.id} role="tab" aria-selected={display === "tabs" && split === "off" && activeId === entry.id} className={display === "tabs" && split === "off" && activeId === entry.id ? "active" : ""} onClick={() => { setSplit("off"); setDisplay("tabs"); setActiveId(entry.id); }}>{entry.label}</button>)}
      <span className="backend-view-mode">
        <b>DISPLAY</b>
        <button className={split === "off" && display === "stack" ? "active" : ""} aria-pressed={split === "off" && display === "stack"} onClick={() => { setSplit("off"); setDisplay("stack"); }}>↕ Stack</button>
        <button className={split === "off" && display === "tabs" ? "active" : ""} aria-pressed={split === "off" && display === "tabs"} onClick={() => { setSplit("off"); setDisplay("tabs"); }}>▣ Tabs</button>
        {split === "off"
          ? <button onClick={() => setSplit("right")}>Split</button>
          : <>
              <button className={split === "left" ? "active" : ""} onClick={() => setSplit("left")} title="Other pane on the left">⬅</button>
              <button className={split === "right" ? "active" : ""} onClick={() => setSplit("right")} title="Other pane on the right">➡</button>
              <button className={split === "up" ? "active" : ""} onClick={() => setSplit("up")} title="Other pane above">⬆</button>
              <button className={split === "down" ? "active" : ""} onClick={() => setSplit("down")} title="Other pane below">⬇</button>
              <button onClick={() => setSplit("off")}>Unsplit</button>
            </>}
        {!lockView && <button className="super-view-toggle" onClick={() => setView("file")}>⛶ Editable File</button>}
      </span>
    </nav>
    {fileToolbar}
    {split !== "off"
      ? <div className={`super-split split-${split}`}>
          <div className="super-pane">{paneTabs(activeId, setActiveId)}<div className="super-pane-body">{rendererById(activeId)?.render()}</div></div>
          <div className="super-pane">{paneTabs(activeId2, setActiveId2)}<div className="super-pane-body">{rendererById(activeId2)?.render()}</div></div>
        </div>
      : display === "stack"
      ? <div className="super-stack">{renderers.map((entry) => <div key={entry.id} className="super-stack-section"><div className="studio-section-label">{entry.label}</div>{entry.render()}</div>)}</div>
      : <div className="super-single">{rendererById(activeId)?.render()}</div>}
  </section>;
}
