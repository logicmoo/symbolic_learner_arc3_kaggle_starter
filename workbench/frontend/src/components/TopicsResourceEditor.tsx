import { useEffect, useMemo, useState } from "react";
import { jsonDocumentToMetta } from "../lib/mettaResourceCodec";
import { ResourceSourceEditor } from "./ResourceSourceEditor";
import { ArtifactTreeBranch } from "./ArtifactTreeBranch";
import "../styles/operation_editor.css";

type Source = "shared" | "workspace";
type Query = { kinds?: string[]; where?: Record<string, unknown> };
type TopicDoc = {
  kind: "artifact_category";
  id: string;
  label?: string;
  description?: string;
  path: string;
  trees?: string[];
  query?: Query;
  parentMode?: string;
  [key: string]: unknown;
};
type TopicRecord = { path: string; source?: Source; workspaceId?: string; document?: TopicDoc; error?: string };

const NEW_KEY = "__new__";
const fileSlug = (value: string) => value.trim().replace(/[^a-zA-Z0-9_.-]+/g, "_").replace(/^_+|_+$/g, "") || "topic";

async function request(path: string, init?: RequestInit) {
  const response = await fetch(path, { headers: { "Content-Type": "application/json", ...(init?.headers || {}) }, ...init });
  const text = await response.text();
  let payload: any = {};
  try { payload = text ? JSON.parse(text) : {}; } catch { payload = { detail: text }; }
  if (!response.ok) throw new Error(payload.error || payload.detail || response.statusText);
  return payload;
}

const NEW_TEMPLATE = (): TopicDoc => ({
  kind: "artifact_category",
  id: "topics.new_topic",
  label: "New Topic",
  description: "Describe what this topic annotates.",
  path: "new-topic",
  trees: ["operations"],
  query: { kinds: ["operation"], where: { topics: { contains: "new-topic" } } },
  parentMode: "show",
});

export function TopicsResourceEditor({ workspaceId }: { workspaceId: string }) {
  const [records, setRecords] = useState<TopicRecord[]>([]);
  const [loaded, setLoaded] = useState(false);
  const [selectedKey, setSelectedKey] = useState<string | null>(null);
  const [source, setSource] = useState("");
  const [dirty, setDirty] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [status, setStatus] = useState<string | null>(null);

  const load = async () => {
    const payload = await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/artifact-categories`);
    const next = ((payload.artifactCategories || []) as TopicRecord[]).filter((record) => record.document && record.document.kind === "artifact_category");
    setRecords(next);
    setLoaded(true);
    return next;
  };
  useEffect(() => {
    setSelectedKey(null); setSource(""); setDirty(false);
    void load().then((loadedRecords) => {
      const requested = new URLSearchParams(window.location.search).get("resource");
      if (!requested) return;
      const match = loadedRecords.find((record) => record.document && (record.document.path === requested || record.document.id === requested));
      if (match && match.document) { setSelectedKey(match.document.id); setSource(JSON.stringify(match.document, null, 2)); setDirty(false); setStatus(null); setError(null); }
    }).catch((reason) => setError(String(reason)));
  }, [workspaceId]);

  const grouped = useMemo(() => {
    const groups = new Map<string, TopicRecord[]>();
    for (const record of records) {
      const path = record.document?.path || record.path;
      const top = path.split("/")[0] || "misc";
      const list = groups.get(top) || [];
      list.push(record);
      groups.set(top, list);
    }
    return [...groups.entries()]
      .map(([name, rows]) => [name, rows.sort((a, b) => String(a.document?.path || "").localeCompare(String(b.document?.path || "")))] as const)
      .sort((a, b) => a[0].localeCompare(b[0]));
  }, [records]);

  const selected = selectedKey === NEW_KEY
    ? { path: "", workspaceId, document: NEW_TEMPLATE(), source: "workspace" as Source }
    : records.find((record) => record.document?.id === selectedKey) || null;

  const select = (record: TopicRecord) => {
    setSelectedKey(record.document?.id || null);
    setSource(record.document ? JSON.stringify(record.document, null, 2) : "");
    setDirty(false);
    setStatus(null);
    setError(null);
  };
  const newTopic = () => {
    setSelectedKey(NEW_KEY);
    setSource(JSON.stringify(NEW_TEMPLATE(), null, 2));
    setDirty(false);
    setStatus(null);
    setError(null);
  };
  const perform = async (work: () => Promise<void>) => {
    setBusy(true); setError(null);
    try { await work(); } catch (reason) { setError(reason instanceof Error ? reason.message : String(reason)); } finally { setBusy(false); }
  };

  const save = () => perform(async () => {
    let document: TopicDoc;
    try { document = JSON.parse(source) as TopicDoc; } catch { throw new Error("Topic source is not valid JSON"); }
    if (document.kind !== "artifact_category") throw new Error('Topic must declare kind: artifact_category');
    if (!document.id || !String(document.path || "").trim()) throw new Error("Topic requires an id and a path");
    const isNew = selectedKey === NEW_KEY;
    const targetWorkspace = isNew ? workspaceId : (selected?.workspaceId || workspaceId);
    const path = isNew ? `design/categories/${fileSlug(document.id)}.artifact_category.metta` : (selected?.path as string);
    const content = jsonDocumentToMetta(JSON.stringify(document));
    await request(`/api/workspaces/${encodeURIComponent(targetWorkspace)}/file`, { method: "PUT", body: JSON.stringify({ path, content }) });
    await load();
    setSelectedKey(document.id);
    setDirty(false);
    setStatus(`Saved ${document.id}`);
  });

  const remove = () => {
    if (!selected || selectedKey === NEW_KEY || !selected.path) return;
    if (!window.confirm(`Delete topic "${selected.document?.id}"? This removes ${selected.path}.`)) return;
    void perform(async () => {
      const targetWorkspace = selected.workspaceId || workspaceId;
      await request(`/api/workspaces/${encodeURIComponent(targetWorkspace)}/file?path=${encodeURIComponent(selected.path)}`, { method: "DELETE" });
      await load();
      setSelectedKey(null); setSource(""); setDirty(false);
      setStatus(`Deleted ${selected.document?.id}`);
    });
  };

  const doc = selected?.document || null;

  return (
    <section className="resource-view operation-hierarchy-page">
      <div className="resource-heading">
        <div>
          <span>TOPIC TAXONOMY</span>
          <h1>Topics</h1>
          <p>Create, rename, reparent, and delete topics that classify resources for selection. Nesting comes from the <code>path</code> (e.g. <code>workflow/workflow-language</code>). See the <b>Topics</b> help tab for the full model.</p>
        </div>
        <div className="operation-editor-actions">
          <button onClick={newTopic}>+ New topic</button>
        </div>
      </div>
      {error && <div className="demo-notice"><b>Topic editor error</b><span>{error}</span></div>}
      {status && !error && <div className="demo-notice"><b>{status}</b><span>{records.length} topic resources.</span></div>}
      <div className="operation-hierarchy-panes" style={{ display: "flex", gap: "16px", alignItems: "flex-start" }}>
        <div className="operation-tree-pane" style={{ flex: "0 0 320px", maxHeight: "70vh", overflow: "auto" }}>
          {!loaded && <div className="studio-empty">Loading topics…</div>}
          {grouped.map(([name, rows]) => (
            <ArtifactTreeBranch key={name} label={name} searchValue={{ topic: name }} header={<div className="inheritance-row"><span className="operation-tree-row operation-parent"><span className="operation-kind-badge">GROUP</span><span><b>{name}</b><small>{rows.length} topic{rows.length === 1 ? "" : "s"}</small></span></span></div>}>
              {rows.map((record) => {
                const item = record.document!;
                const isSelected = selectedKey === item.id;
                const nested = item.path.includes("/");
                return (
                  <button
                    key={item.id}
                    className={`operation-tree-row ${nested ? "operation-child" : "operation-parent"} ${isSelected ? "selected" : ""}`}
                    data-tree-search={JSON.stringify(item)}
                    onClick={() => select(record)}
                  >
                    <span className="operation-kind-badge">TOPIC</span>
                    <span><b>{item.label || item.id}</b><small>{item.path}{record.source === "shared" ? " · shared" : ""}</small></span>
                    <em>{(item.trees || []).join(", ") || "operations"}</em>
                  </button>
                );
              })}
            </ArtifactTreeBranch>
          ))}
        </div>
        <div className="operation-editor-workspace" style={{ flex: "1 1 auto", minWidth: 0 }}>
          {!selected ? (
            <div className="studio-empty">Select a topic on the left, or create a new one.</div>
          ) : (
            <section className="operation-editor-document primary">
              <div className="operation-editor-toolbar">
                <div>
                  <span>{selectedKey === NEW_KEY ? "NEW TOPIC" : "TOPIC"}{dirty ? " · UNSAVED" : ""}</span>
                  <h2>{doc?.label || doc?.id}</h2>
                  <small>{selectedKey === NEW_KEY ? `will write design/categories/${fileSlug(doc?.id || "topic")}.artifact_category.metta` : `${selected.source || "workspace"} · ${selected.path}`}</small>
                </div>
                <div className="operation-editor-actions">
                  <button className="primary" disabled={busy} onClick={save}>Save</button>
                  <button disabled={busy || selectedKey === NEW_KEY} onClick={remove}>Delete</button>
                </div>
              </div>
              <div className="operation-editor-scroll">
                {doc && (
                  <div className="operation-abstract-summary">
                    <div><span>PATH</span><code>{doc.path}</code></div>
                    <div><span>TREES</span><code>{(doc.trees || []).join(", ") || "—"}</code></div>
                    <div><span>KINDS</span><code>{(doc.query?.kinds || []).join(", ") || "—"}</code></div>
                    <div><span>PARENT MODE</span><code>{doc.parentMode || "user"}</code></div>
                  </div>
                )}
                <ResourceSourceEditor
                  value={source}
                  onChange={(value) => { setSource(value); setDirty(true); }}
                  label="Edit this topic resource directly"
                />
              </div>
            </section>
          )}
        </div>
      </div>
    </section>
  );
}
