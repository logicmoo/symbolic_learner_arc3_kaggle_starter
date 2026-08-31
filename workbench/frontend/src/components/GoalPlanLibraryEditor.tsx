import { useEffect, useMemo, useState } from "react";
import type { JSX } from "react";
import { HierarchyResourceEditor } from "./HierarchyResourceEditor";
import { ArtifactTreeBranch } from "./ArtifactTreeBranch";
import { implementedByResource, implementsResource, inheritsFromResource, relationshipIds } from "./resourceRelationships";
import { ResourceSourceEditor } from "./ResourceSourceEditor";
import { ResourceEnablementBadge, enablementClass, resolveResourceEnablement } from "./resourceEnablement";
import { ResourceExecutionPlayground } from "./ResourceExecutionPlayground";
import type { TreeRelationshipMode } from "./useArtifactTreeFilter";
import "../styles/operation_editor.css";

type Family = "goal" | "plan" | "context";
type Source = "shared" | "workspace";
type BaseKind = "goal" | "planning_strategy" | "atomspace";
type Specification = { kind: BaseKind; id: string; implements?: Record<string, unknown>; inheritsFrom?: Record<string, unknown>; label?: string; description?: string; enabled?: boolean; implementedBy?: Record<string, unknown>; preferredImplementation?: string; goals?: string[]; successCriteria?: string[]; bindings?: string[]; [key: string]: unknown };
type Variant = Specification & { implements: Record<string, unknown>; workflow?: string };
type Resource = Specification | Variant;
type RecordFile<T> = { path: string; source?: Source; workspaceId?: string; document?: T; error?: string };
type Hierarchy = { specifications: RecordFile<Specification>[]; variants: RecordFile<Variant>[]; implementedByResource: Record<string, RecordFile<Variant>[]> };
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
  const directory = family === "goal" ? "goals" : family === "plan" ? "planning_strategies" : "contexts";
  const endpoint = family === "plan" ? "plans" : directory;
  const specificationDirectory = family === "context" ? "design/atomspaces" : `design/${directory}`;
  const parentKind: BaseKind = family === "goal" ? "goal" : family === "plan" ? "planning_strategy" : "atomspace";
  const familyLabel = family === "goal" ? "Goal" : family === "plan" ? "Planning Strategy" : "AtomSpace";
  const familyNoun = family === "context" ? "AtomSpace" : family;
  const [payload, setPayload] = useState<Payload | null>(null);
  const [openDocs, setOpenDocs] = useState<OpenDocument[]>([]);
  const [activeKey, setActiveKey] = useState<string | null>(null);
  const [compareKey, setCompareKey] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    const next = await request(`/workbench/workspaces/${encodeURIComponent(workspaceId)}/${endpoint}`) as Payload;
    setPayload(next);
    return next;
  };
  useEffect(() => { setOpenDocs([]); setActiveKey(null); setCompareKey(null); void load().catch(reason => setError(String(reason))); }, [workspaceId, family]);

  const specifications = payload?.hierarchy.specifications || [];
  const variants = payload?.hierarchy.variants || [];
  const implementationsByResource = payload?.hierarchy.implementedByResource || {};
  const ordered = useMemo(() => [...specifications].sort((a, b) => String(a.document?.label || a.path).localeCompare(String(b.document?.label || b.path))), [specifications]);
  const open = (record: RecordFile<Resource>) => { const key = recordKey(record); setOpenDocs(current => current.some(doc => doc.key === key) ? current : [...current, { key, record, source: record.document ? JSON.stringify(record.document, null, 2) : "", dirty: false }]); setActiveKey(key); };
  useEffect(() => { if (!payload || openDocs.length) return; const requestedId = new URLSearchParams(window.location.search).get("resource"); const requested = requestedId ? payload.resources.find(record => record.document?.id === requestedId) : undefined; if (requested) open(requested); else if (ordered[0]) open(ordered[0] as RecordFile<Resource>); }, [payload, ordered]);
  const updateSource = (key: string, source: string) => setOpenDocs(current => current.map(doc => doc.key === key ? { ...doc, source, dirty: true } : doc));
  const active = openDocs.find(doc => doc.key === activeKey) || null;
  const close = (key: string) => { setOpenDocs(current => { const index = current.findIndex(doc => doc.key === key); const next = current.filter(doc => doc.key !== key); if (activeKey === key) setActiveKey(next[Math.max(0, index - 1)]?.key || next[0]?.key || null); if (compareKey === key) setCompareKey(null); return next; }); };
  const chooseComparison = () => { if (compareKey) { setCompareKey(null); return; } const other = [...openDocs].reverse().find(doc => doc.key !== activeKey); if (other) setCompareKey(other.key); };
  const perform = async (work: () => Promise<void>) => { setBusy(true); setError(null); try { await work(); } catch (reason) { setError(reason instanceof Error ? reason.message : String(reason)); } finally { setBusy(false); } };

  const newSpecification = () => {
    const id = `new_${family}`;
    const document: Specification = { kind: parentKind, id, label: `New ${familyLabel}`, description: family === "plan" ? "Strategy for selecting, generating, or adapting an executable workflow (a PDDL plan in PDDL terminology)." : `Abstract ${familyNoun} specification.`, implementedBy: {}, ...(family === "goal" ? { successCriteria: [] } : family === "plan" ? { goals: [] } : { bindings: [] }) };
    open({ path: `${specificationDirectory}/${id}.${parentKind}.json`, source: workspaceId === "shared" ? "shared" : "workspace", workspaceId, document });
  };
  const newVariant = (parent: Specification) => {
    const id = `${parent.id}.alternative`;
    const document: Variant = { kind: parentKind, id, implements: implementsResource(parent.id), inheritsFrom: inheritsFromResource(parent.id), label: `${parent.label || parent.id} — Alternative`, description: `Concrete ${familyNoun} implementation.` };
    open({ path: `${specificationDirectory}/${slug(id)}.${parentKind}.json`, source: workspaceId === "shared" ? "shared" : "workspace", workspaceId, document });
  };
  const saveDoc = (doc: OpenDocument) => perform(async () => {
    let document: Resource;
    try { document = JSON.parse(doc.source) as Resource; } catch { throw new Error(`${familyLabel} resource source is invalid`); }
    if (!document.id || document.kind !== parentKind) throw new Error(`${familyLabel} resource requires id and kind='${parentKind}'`);
    const path = workspaceId === "shared" || doc.record.source === "workspace" ? doc.record.path : `${specificationDirectory}/${slug(document.id)}.${parentKind}.json`;
    await request(`/workbench/workspaces/${encodeURIComponent(workspaceId)}/file`, { method: "PUT", body: JSON.stringify({ path, content: JSON.stringify(document, null, 2) }) });
    const next = await load();
    const saved = next.resources.find(row => row.document?.id === document.id);
    if (saved) { const key = recordKey(saved); setOpenDocs(current => current.map(item => item.key === doc.key ? { key, record: saved, source: JSON.stringify(saved.document, null, 2), dirty: false } : item)); if (activeKey === doc.key) setActiveKey(key); if (compareKey === doc.key) setCompareKey(key); }
  });

  const renderEditor = (doc: OpenDocument, secondary = false) => {
    let document: Resource | null = null;
    try { document = doc.source ? JSON.parse(doc.source) as Resource : null; } catch { document = null; }
    const isParent = Boolean(document && !relationshipIds(document.implements).length);
    const parent = isParent ? document as Specification : null;
    const variant = document && !isParent ? document as Variant : null;
    const alternatives = parent ? implementationsByResource[parent.id] || [] : [];
    const patchParent = (patch: Partial<Specification>) => parent && updateSource(doc.key, JSON.stringify({ ...parent, ...patch }, null, 2));
    const setPreferred = (id: string) => { if (!parent) return; const implementedBy = Object.assign({}, ...alternatives.flatMap(row => row.document?.id ? [implementedByResource(row.document.id)] : [])); patchParent({ preferredImplementation: id || undefined, implementedBy }); };
    return <section className={`operation-editor-document ${secondary ? "secondary" : "primary"}`} key={doc.key}><div className="operation-editor-toolbar"><div><span>{parent ? `ABSTRACT ${familyLabel.toUpperCase()}` : `${familyLabel.toUpperCase()} IMPLEMENTATION`}{doc.dirty ? " · UNSAVED" : ""}</span><h2>{document?.label || document?.id || doc.record.path}</h2><small>{doc.record.source} · {doc.record.path}</small></div><div className="operation-editor-actions">{!secondary && <button onClick={chooseComparison}>{compareKey ? "Single pane" : "Split view"}</button>}{parent && <button onClick={() => newVariant(parent)}>+ Implementation</button>}<button className="primary" disabled={busy || !document} onClick={() => saveDoc(doc)}>Save</button></div></div><div className="operation-editor-scroll">{!document && <div className="demo-notice"><b>Invalid resource</b><span>Fix the source before saving.</span></div>}{parent && <><div className="operation-abstract-summary"><div><span>PREFERRED IMPLEMENTATION</span><select value={parent.preferredImplementation || ""} onChange={event => setPreferred(event.target.value)}><option value="">planner-selected</option>{alternatives.map(row => <option key={row.document?.id} value={row.document?.id}>{row.document?.label || row.document?.id}</option>)}</select></div><div><span>IMPLEMENTATIONS</span><code>{alternatives.length}</code></div><div><span>{family === "goal" ? "SUCCESS CRITERIA" : family === "plan" ? "GOALS" : "BINDINGS"}</span><code>{(family === "goal" ? parent.successCriteria : family === "plan" ? parent.goals : parent.bindings)?.length || 0}</code></div></div><div className="operation-model-list compact">{alternatives.map(row => { const implementation = row.document!; const preferred = parent.preferredImplementation === implementation.id; return <button className={`operation-model-option ${preferred ? "selected" : ""}`} key={implementation.id} data-tree-search={JSON.stringify(implementation)} onClick={() => open(row as RecordFile<Resource>)}><span><b>{implementation.label || implementation.id}</b><small>{implementation.description || implementation.id}</small></span><em>{preferred ? "preferred" : "alternative"}</em></button>; })}</div></>}{variant && <div className="implementation-summary"><div><span>IMPLEMENTS</span><b>{relationshipIds(variant.implements).join(", ")}</b></div><div><span>INHERITS FROM</span><b>{relationshipIds(variant.inheritsFrom).join(", ") || "none"}</b></div><div><span>WORKFLOW</span><b>{variant.workflow || "planner-selected"}</b></div></div>}{document&&<ResourceExecutionPlayground workspaceId={workspaceId} resource={document}/>}<ResourceSourceEditor value={doc.source} onChange={value => updateSource(doc.key, value)} label={`Edit this ${family} resource directly`} /></div></section>;
  };

  if (!payload) return <section className="resource-view"><div className="studio-empty">Loading {directory}…</div></section>;
  const leftPane = (relationshipMode: TreeRelationshipMode) => {
    const records = payload.resources.filter(record => record.document);
    const byId = new Map(records.map(record => [record.document!.id, record]));
    const parentIds = (document: Resource) => relationshipIds(
      relationshipMode === "implementation"
        ? document.implements
        : relationshipMode === "inheritance"
          ? document.inheritsFrom
          : document.dependsOn,
    );
    const children = new Map<string, RecordFile<Resource>[]>();
    for (const record of records) {
      for (const parentId of parentIds(record.document!)) {
        const rows = children.get(parentId) || [];
        rows.push(record);
        children.set(parentId, rows);
      }
    }
    const roots = records.filter(record => !parentIds(record.document!).some(id => byId.has(id)));
    const relationLabel = relationshipMode === "implementation" ? "implementations" : relationshipMode === "inheritance" ? "inheritors" : "dependents";
    const renderNode = (record: RecordFile<Resource>, trail: string[] = []): JSX.Element => {
      const item = record.document!;
      const descendants = (children.get(item.id) || []).filter(child => !trail.includes(child.document!.id));
      const state = resolveResourceEnablement(item);
      const isImplementationRoot = relationshipIds(item.implements).length === 0;
      return <ArtifactTreeBranch key={`${relationshipMode}:${trail.join(">")}:${item.id}`} label={item.label || item.id} searchValue={item} header={<div className="inheritance-row"><button className={`operation-tree-row ${trail.length ? "operation-child" : "operation-parent"} ${enablementClass(state)} ${active?.record.document?.id === item.id ? "selected" : ""}`} onClick={() => open(record)}><span className={`operation-kind-badge${trail.length ? " llm" : ""}`}>{trail.length ? "CHILD" : familyLabel.toUpperCase()}</span><span><b>{item.label || item.id}</b><small>{item.description || item.id}</small></span><em>{descendants.length} {relationLabel} {item.preferredImplementation ? ` · preferred ${item.preferredImplementation}` : ""} <ResourceEnablementBadge state={state} /></em></button>{relationshipMode === "implementation" && isImplementationRoot && <button className="hier-mini" onClick={() => newVariant(item)}>+ implementation</button>}</div>}>{descendants.length ? descendants.map(child => renderNode(child, [...trail, item.id])) : undefined}</ArtifactTreeBranch>;
    };
    return <>{roots.map(record => renderNode(record))}</>;
  };
  const tabs = openDocs.map(doc => ({ key: doc.key, kind: relationshipIds(doc.record.document?.implements).length ? "SPEC" : familyLabel.toUpperCase(), label: doc.record.document?.label || doc.record.document?.id || doc.record.path, dirty: doc.dirty }));
 return <HierarchyResourceEditor workspaceId={workspaceId} categoryTree={family === "goal" ? "goals" : family === "plan" ? "plans" : "atomspaces"} eyebrow={`${familyLabel.toUpperCase()} CONTRACT SYSTEM`} title={`${familyLabel}s & alternatives`} description={family === "plan" ? "Strategies guide planners; the concrete human- or machine-produced plan is stored and executed as a Workflow." : `Abstract ${directory} and concrete alternatives are separate inherited filesystem resources.`} headerActions={<button onClick={newSpecification}>+ Abstract {familyLabel.toLowerCase()}</button>} error={error} onDismissError={() => setError(null)} leftPane={leftPane} tabs={tabs} activeKey={activeKey} compareKey={compareKey} onActivate={setActiveKey} onClose={close} renderEditor={(key, secondary) => { const doc = openDocs.find(item => item.key === key); return doc ? renderEditor(doc, secondary) : null; }} emptyEditor={<div className="studio-empty">Select or create a {familyLabel.toLowerCase()}.</div>} footer={<div className="demo-notice"><b>Filesystem hierarchy</b><span>{specifications.length} specification(s) · {variants.length} alternatives · shared inheritance with workspace overrides.</span></div>} />;
}
