import { useEffect, useMemo, useState } from "react";
import { HierarchyResourceEditor } from "./HierarchyResourceEditor";
import { ArtifactTreeBranch } from "./ArtifactTreeBranch";
import { relationshipIds } from "./resourceRelationships";
import "../styles/operation_editor.css";

type Family = "goal" | "plan" | "context";
type Source = "shared" | "workspace";
type Specification = { kind: Family; id: string; label?: string; description?: string; children?: string[]; preferredChild?: string; goals?: string[]; successCriteria?: string[]; bindings?: string[]; [key: string]: unknown };
type Variant = { kind: "goal_interpretation" | "goal_variant" | "plan_variant" | "context_variant"; id: string; parents: string[]; label?: string; description?: string; workflow?: string; [key: string]: unknown };
type Resource = Specification | Variant;
type RecordFile<T> = { path: string; source?: Source; workspaceId?: string; document?: T; error?: string };
type Hierarchy = { specifications: RecordFile<Specification>[]; variants: RecordFile<Variant>[]; variantsBySpecification: Record<string, RecordFile<Variant>[]> };
type Payload = { workspace: { id: string; label: string; root: string }; resources: RecordFile<Resource>[]; hierarchy: Hierarchy };
type OpenDocument = { key: string; record: RecordFile<Resource>; source: string; dirty: boolean };

const slug = (value: string) => value.toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_+|_+$/g, "") || "resource";
const recordKey = (record: RecordFile<Resource>) => `${record.workspaceId || record.source || "resource"}:${record.path}:${record.document?.id || "unknown"}`;

async function request(path: string, init?: RequestInit) {
  const response = await fetch(path, { headers: { "Content-Type": "application/json", ...(init?.headers || {}) }, ...init });
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.error || payload.detail || response.statusText);
  return payload;
}

export function GoalPlanLibraryEditor({ workspaceId, family }: { workspaceId: string; family: Family }) {
  const directory = family === "goal" ? "goals" : family === "plan" ? "plans" : "contexts";
  const variantKind = family === "goal" ? "goal_variant" : family === "plan" ? "plan_variant" : "context_variant";
  const familyLabel = family === "goal" ? "Goal" : family === "plan" ? "Plan" : "AtomSpace";
  const [payload, setPayload] = useState<Payload | null>(null);
  const [openDocs, setOpenDocs] = useState<OpenDocument[]>([]);
  const [activeKey, setActiveKey] = useState<string | null>(null);
  const [compareKey, setCompareKey] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    const next = await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/${directory}`) as Payload;
    setPayload(next);
    return next;
  };
  useEffect(() => { setOpenDocs([]); setActiveKey(null); setCompareKey(null); void load().catch(reason => setError(String(reason))); }, [workspaceId, family]);

  const specifications = payload?.hierarchy.specifications || [];
  const variants = payload?.hierarchy.variants || [];
  const children = payload?.hierarchy.variantsBySpecification || {};
  const ordered = useMemo(() => [...specifications].sort((a, b) => String(a.document?.label || a.path).localeCompare(String(b.document?.label || b.path))), [specifications]);
  const open = (record: RecordFile<Resource>) => { const key = recordKey(record); setOpenDocs(current => current.some(doc => doc.key === key) ? current : [...current, { key, record, source: record.document ? JSON.stringify(record.document, null, 2) : "", dirty: false }]); setActiveKey(key); };
  useEffect(() => { if (payload && openDocs.length === 0 && ordered[0]) open(ordered[0] as RecordFile<Resource>); }, [payload, ordered]);
  const updateSource = (key: string, source: string) => setOpenDocs(current => current.map(doc => doc.key === key ? { ...doc, source, dirty: true } : doc));
  const active = openDocs.find(doc => doc.key === activeKey) || null;
  const close = (key: string) => { setOpenDocs(current => { const index = current.findIndex(doc => doc.key === key); const next = current.filter(doc => doc.key !== key); if (activeKey === key) setActiveKey(next[Math.max(0, index - 1)]?.key || next[0]?.key || null); if (compareKey === key) setCompareKey(null); return next; }); };
  const chooseComparison = () => { if (compareKey) { setCompareKey(null); return; } const other = [...openDocs].reverse().find(doc => doc.key !== activeKey); if (other) setCompareKey(other.key); };
  const perform = async (work: () => Promise<void>) => { setBusy(true); setError(null); try { await work(); } catch (reason) { setError(reason instanceof Error ? reason.message : String(reason)); } finally { setBusy(false); } };

  const newSpecification = () => {
    const id = `new_${family}`;
    const document: Specification = { kind: family, id, label: `New ${familyLabel}`, description: `Abstract ${family} specification.`, children: [], ...(family === "goal" ? { successCriteria: [] } : family === "plan" ? { goals: [] } : { bindings: [] }) };
    open({ path: `${directory}/${id}.${family}.json`, source: workspaceId === "shared" ? "shared" : "workspace", workspaceId, document });
  };
  const newVariant = (parent: Specification) => {
    const id = `${parent.id}.alternative`;
    const document: Variant = { kind: variantKind, id, parents: [parent.id], label: `${parent.label || parent.id} — Alternative`, description: `Concrete ${family} alternative.` };
    open({ path: `${directory}/${slug(id)}.${variantKind}.json`, source: workspaceId === "shared" ? "shared" : "workspace", workspaceId, document });
  };
  const saveDoc = (doc: OpenDocument) => perform(async () => {
    let document: Resource;
    try { document = JSON.parse(doc.source) as Resource; } catch { throw new Error(`${familyLabel} resource JSON is invalid`); }
    const kinds = family === "goal" ? ["goal", "goal_interpretation", "goal_variant"] : family === "plan" ? ["plan", "plan_variant"] : ["context", "context_variant"];
    if (!document.id || !kinds.includes(document.kind)) throw new Error(`${familyLabel} resource requires id and a valid kind`);
    if (document.kind !== family && !relationshipIds((document as Variant).parents).length) throw new Error(`${familyLabel} variant requires parents`);
    const path = workspaceId === "shared" || doc.record.source === "workspace" ? doc.record.path : `${directory}/${slug(document.id)}.${document.kind}.json`;
    await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/file`, { method: "PUT", body: JSON.stringify({ path, content: JSON.stringify(document, null, 2) }) });
    const next = await load();
    const saved = next.resources.find(row => row.document?.id === document.id);
    if (saved) { const key = recordKey(saved); setOpenDocs(current => current.map(item => item.key === doc.key ? { key, record: saved, source: JSON.stringify(saved.document, null, 2), dirty: false } : item)); if (activeKey === doc.key) setActiveKey(key); if (compareKey === doc.key) setCompareKey(key); }
  });

  const renderEditor = (doc: OpenDocument, secondary = false) => {
    let document: Resource | null = null;
    try { document = doc.source ? JSON.parse(doc.source) as Resource : null; } catch { document = null; }
    const parent = document?.kind === family ? document as Specification : null;
    const variant = document && document.kind !== family ? document as Variant : null;
    const alternatives = parent ? children[parent.id] || [] : [];
    const patchParent = (patch: Partial<Specification>) => parent && updateSource(doc.key, JSON.stringify({ ...parent, ...patch }, null, 2));
    const setPreferred = (id: string) => { if (!parent) return; const children = alternatives.map(row => row.document?.id).filter(Boolean) as string[]; patchParent({ preferredChild: id || undefined, children }); };
    return <section className={`operation-editor-document ${secondary ? "secondary" : "primary"}`} key={doc.key}><div className="operation-editor-toolbar"><div><span>{parent ? `ABSTRACT ${familyLabel.toUpperCase()}` : `${familyLabel.toUpperCase()} VARIANT`}{doc.dirty ? " · UNSAVED" : ""}</span><h2>{document?.label || document?.id || doc.record.path}</h2><small>{doc.record.source} · {doc.record.path}</small></div><div className="operation-editor-actions">{!secondary && <button onClick={chooseComparison}>{compareKey ? "Single pane" : "Split view"}</button>}{parent && <button onClick={() => newVariant(parent)}>+ Alternative</button>}<button className="primary" disabled={busy || !document} onClick={() => saveDoc(doc)}>Save</button></div></div><div className="operation-editor-scroll">{!document && <div className="demo-notice"><b>Invalid JSON</b><span>Fix the JSON before saving.</span></div>}{parent && <><div className="operation-abstract-summary"><div><span>PREFERRED VARIANT</span><select value={parent.preferredChild || ""} onChange={event => setPreferred(event.target.value)}><option value="">planner-selected</option>{alternatives.map(row => <option key={row.document?.id} value={row.document?.id}>{row.document?.label || row.document?.id}</option>)}</select></div><div><span>ALTERNATIVES</span><code>{alternatives.length}</code></div><div><span>{family === "goal" ? "SUCCESS CRITERIA" : family === "plan" ? "GOALS" : "BINDINGS"}</span><code>{(family === "goal" ? parent.successCriteria : family === "plan" ? parent.goals : parent.bindings)?.length || 0}</code></div></div><div className="operation-model-list compact">{alternatives.map(row => { const child = row.document!; const preferred = parent.preferredChild === child.id; return <button className={`operation-model-option ${preferred ? "selected" : ""}`} key={child.id} data-tree-search={JSON.stringify(child)} onClick={() => open(row as RecordFile<Resource>)}><span><b>{child.label || child.id}</b><small>{child.description || child.id}</small></span><em>{preferred ? "preferred" : "alternative"}</em></button>; })}</div></>}{variant && <div className="implementation-summary"><div><span>IMPLEMENTS</span><b>{relationshipIds(variant.parents).join(", ")}</b></div><div><span>WORKFLOW</span><b>{variant.workflow || "planner-selected"}</b></div></div>}<div className="operation-json-block"><div className="llm-subhead"><div><span>RESOURCE JSON</span><b>Edit this {family} resource directly</b></div></div><textarea className="raw-json-editor operation-visible-editor" value={doc.source} onChange={event => updateSource(doc.key, event.target.value)} /></div></div></section>;
  };

  if (!payload) return <section className="resource-view"><div className="studio-empty">Loading {directory}…</div></section>;
  const leftPane = <>{ordered.map(record => { const item = record.document; if (!item) return null; const alternatives = children[item.id] || []; return <ArtifactTreeBranch key={item.id} label={item.label || item.id} searchValue={item} header={<div className="inheritance-row"><button className={`operation-tree-row operation-parent ${active?.record.document?.id === item.id ? "selected" : ""}`} onClick={() => open(record as RecordFile<Resource>)}><span className="operation-kind-badge">{familyLabel.toUpperCase()}</span><span><b>{item.label || item.id}</b><small>{item.description || item.id}</small></span><em>{alternatives.length} alternatives</em></button><button className="hier-mini" onClick={() => newVariant(item)}>+ alt</button></div>}>{alternatives.length ? alternatives.map(row => { const child = row.document!; const preferred = item.preferredChild === child.id; return <button className={`operation-tree-row operation-child ${active?.record.document?.id === child.id ? "selected" : ""}`} key={child.id} data-tree-search={JSON.stringify(child)} onClick={() => open(row as RecordFile<Resource>)}><span className="operation-kind-badge llm">ALT</span><span><b>{child.label || child.id}</b><small>{child.description || child.id}</small></span><em>{preferred ? "preferred" : ""}</em></button>; }) : undefined}</ArtifactTreeBranch>; })}</>;
  const tabs = openDocs.map(doc => ({ key: doc.key, kind: doc.record.document?.kind === family ? familyLabel.toUpperCase() : "ALT", label: doc.record.document?.label || doc.record.document?.id || doc.record.path, dirty: doc.dirty }));
  return <HierarchyResourceEditor eyebrow={`${familyLabel.toUpperCase()} CONTRACT SYSTEM`} title={`${familyLabel}s & alternatives`} description={`Abstract ${directory} and concrete variants are separate inherited filesystem resources.`} headerActions={<button onClick={newSpecification}>+ Abstract {familyLabel.toLowerCase()}</button>} error={error} onDismissError={() => setError(null)} leftPane={leftPane} tabs={tabs} activeKey={activeKey} compareKey={compareKey} onActivate={setActiveKey} onClose={close} renderEditor={(key, secondary) => { const doc = openDocs.find(item => item.key === key); return doc ? renderEditor(doc, secondary) : null; }} emptyEditor={<div className="studio-empty">Select or create a {family}.</div>} footer={<div className="demo-notice"><b>Filesystem hierarchy</b><span>{specifications.length} specification(s) · {variants.length} variants · shared inheritance with workspace overrides.</span></div>} />;
}
