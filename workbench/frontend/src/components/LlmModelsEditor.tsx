import { useEffect, useMemo, useState } from "react";

type Source = "shared" | "workspace";

type RecordFile<T> = {
  path: string;
  source?: Source;
  workspaceId?: string;
  document?: T;
  error?: string;
  resolved?: ModelResolution;
};

type BackendDef = {
  kind: "backend";
  id: string;
  label?: string;
  description?: string;
  provider: string;
  official?: boolean;
  enabled?: boolean;
  capabilities?: string[];
  configuration?: Record<string, unknown>;
};

type ModelDef = {
  kind: "model";
  id: string;
  label?: string;
  description?: string;
  backend: string;
  model: string;
  enabled?: boolean;
  capabilities?: string[];
  defaults?: Record<string, unknown>;
  environment?: Record<string, unknown>;
};

type ModelResolution = {
  backendId: string;
  backendSource?: Source;
  backendPath?: string;
  backend?: BackendDef | null;
  configuration?: Record<string, unknown>;
  defaults?: Record<string, unknown>;
  enabled?: boolean;
};

type Library<T> = {
  shared: RecordFile<T>[];
  workspace: RecordFile<T>[];
  effective: RecordFile<T>[];
};

type Snapshot = {
  workspace: {id:string;label:string;root:string};
  backends: RecordFile<BackendDef>[];
  backendLibrary?: Library<BackendDef>;
  models: RecordFile<ModelDef>[];
  modelLibrary?: Library<ModelDef>;
};

type Layout = "tiles" | "list";
type LlmSection = "models" | "backends";

const slug = (value: string) => value.toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_+|_+$/g, "") || "model";

async function request(path: string, init?: RequestInit) {
  const response = await fetch(path, {headers:{"Content-Type":"application/json", ...(init?.headers || {})}, ...init});
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.error || payload.detail || response.statusText);
  return payload;
}

function isLlmBackend(record: RecordFile<BackendDef>) {
  const item = record.document;
  if (!item) return false;
  const caps = (item.capabilities || []).join(" ").toLowerCase();
  return caps.includes("llm") || /openai|anthropic|openrouter|groq|ollama|unsloth|llm/.test(item.provider.toLowerCase());
}

function numberValue(value: unknown, fallback = 0) {
  return typeof value === "number" && Number.isFinite(value) ? value : fallback;
}

function ModelEditorForm({source,onChange,backends}:{source:string;onChange:(value:string)=>void;backends:RecordFile<BackendDef>[]}) {
  const document = useMemo<ModelDef | null>(() => { try { return JSON.parse(source) as ModelDef; } catch { return null; } }, [source]);
  if (!document) return <div className="demo-notice"><b>Invalid model JSON</b><span>Fix the JSON source before using the structured configurator.</span></div>;
  const defaults = document.defaults || {};
  const update = (patch: Partial<ModelDef>) => onChange(JSON.stringify({...document, ...patch}, null, 2));
  const updateDefault = (name: string, value: unknown) => update({defaults:{...defaults, [name]:value}});
  return <div className="model-config-form">
    <label><span>ID</span><input value={document.id} onChange={event => update({id:event.target.value})}/></label>
    <label><span>LABEL</span><input value={document.label || ""} onChange={event => update({label:event.target.value})}/></label>
    <label><span>BACKEND</span><select value={document.backend} onChange={event => update({backend:event.target.value})}>{backends.filter(row => row.document).map(row => <option key={`${row.workspaceId}:${row.path}`} value={row.document!.id}>{row.document!.label || row.document!.id}</option>)}</select></label>
    <label><span>REMOTE / LOCAL MODEL ID</span><input value={document.model} onChange={event => update({model:event.target.value})}/></label>
    <label><span>TEMPERATURE</span><input type="number" step="0.01" value={numberValue(defaults.temperature)} onChange={event => updateDefault("temperature", Number(event.target.value))}/></label>
    <label><span>TOP P</span><input type="number" step="0.01" value={numberValue(defaults.topP, 1)} onChange={event => updateDefault("topP", Number(event.target.value))}/></label>
    <label><span>MAX OUTPUT TOKENS</span><input type="number" step="1" value={numberValue(defaults.maxOutputTokens, 12000)} onChange={event => updateDefault("maxOutputTokens", Number(event.target.value))}/></label>
    <label><span>REASONING EFFORT</span><select value={String(defaults.reasoningEffort || "medium")} onChange={event => updateDefault("reasoningEffort", event.target.value)}><option value="low">low</option><option value="medium">medium</option><option value="high">high</option></select></label>
    <label><span>TIMEOUT SECONDS</span><input type="number" step="1" value={numberValue(defaults.timeoutSeconds, 300)} onChange={event => updateDefault("timeoutSeconds", Number(event.target.value))}/></label>
    <label className="model-enable-field"><span>AVAILABLE TO TASKS</span><input type="checkbox" checked={document.enabled !== false} onChange={event => update({enabled:event.target.checked})}/></label>
  </div>;
}

export function LlmModelsEditor({workspaceId}:{workspaceId:string}) {
  const [snapshot,setSnapshot] = useState<Snapshot | null>(null);
  const [section,setSection] = useState<LlmSection>("models");
  const [layout,setLayout] = useState<Layout>("tiles");
  const [selectedModel,setSelectedModel] = useState<RecordFile<ModelDef> | null>(null);
  const [modelSource,setModelSource] = useState("");
  const [modelTarget,setModelTarget] = useState<string | null>(null);
  const [selectedBackend,setSelectedBackend] = useState<RecordFile<BackendDef> | null>(null);
  const [backendSource,setBackendSource] = useState("");
  const [backendTarget,setBackendTarget] = useState<string | null>(null);
  const [busy,setBusy] = useState(false);
  const [error,setError] = useState<string | null>(null);

  const load = async () => {
    const next = await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/snapshot`) as Snapshot;
    setSnapshot(next);
    return next;
  };

  useEffect(() => { void load().catch(reason => setError(String(reason))); }, [workspaceId]);

  const effectiveModels = snapshot?.models || [];
  const sharedModels = snapshot?.modelLibrary?.shared || effectiveModels.filter(row => row.source === "shared");
  const workspaceModels = snapshot?.modelLibrary?.workspace || effectiveModels.filter(row => row.source === "workspace");
  const effectiveBackends = (snapshot?.backends || []).filter(isLlmBackend);
  const sharedBackends = (snapshot?.backendLibrary?.shared || snapshot?.backends || []).filter(isLlmBackend);
  const workspaceBackends = (snapshot?.backendLibrary?.workspace || []).filter(isLlmBackend);
  const effectiveById = useMemo(() => new Map(effectiveModels.filter(row => row.document).map(row => [row.document!.id, row])), [effectiveModels]);
  const activeModels = effectiveModels.filter(row => row.document && (row.resolved?.enabled ?? row.document.enabled !== false));

  const perform = async (work:()=>Promise<void>) => { setBusy(true); setError(null); try { await work(); } catch (reason) { setError(reason instanceof Error ? reason.message : String(reason)); } finally { setBusy(false); } };

  const openModel = (record: RecordFile<ModelDef>) => {
    const editable = workspaceId === "shared" || record.source === "workspace";
    setSelectedModel(record);
    setModelSource(record.document ? JSON.stringify(record.document, null, 2) : "");
    setModelTarget(editable ? record.path : null);
  };

  const openBackend = (record: RecordFile<BackendDef>) => {
    const editable = workspaceId === "shared" || record.source === "workspace";
    setSelectedBackend(record);
    setBackendSource(record.document ? JSON.stringify(record.document, null, 2) : "");
    setBackendTarget(editable ? record.path : null);
  };

  useEffect(() => {
    if (!snapshot) return;
    if (!selectedModel && effectiveModels[0]) openModel(effectiveModels[0]);
    if (!selectedBackend && effectiveBackends[0]) openBackend(effectiveBackends[0]);
  }, [snapshot]);

  const saveModel = () => perform(async () => {
    const document = JSON.parse(modelSource) as ModelDef;
    if (document.kind !== "model" || !document.id || !document.backend || !document.model) throw new Error("Model requires kind, id, backend, and model");
    const path = modelTarget || `models/${slug(document.id)}.json`;
    await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/file`, {method:"PUT", body:JSON.stringify({path,content:JSON.stringify(document,null,2)})});
    const next = await load();
    const saved = next.models.find(row => row.document?.id === document.id) || null;
    if (saved) openModel(saved);
  });

  const makeWorkspaceModel = (record = selectedModel) => {
    if (!record?.document || workspaceId === "shared") return;
    const document = {...record.document};
    setSelectedModel({...record,source:"workspace",workspaceId,path:`models/${slug(document.id)}.json`,document});
    setModelSource(JSON.stringify(document,null,2));
    setModelTarget(`models/${slug(document.id)}.json`);
  };

  const cloneVariant = (record = selectedModel) => {
    if (!record?.document) return;
    const base = record.document;
    const id = `${base.id}-variant`;
    const document: ModelDef = {...base,id,label:`${base.label || base.id} variant`};
    setSelectedModel({...record,source:workspaceId === "shared" ? "shared" : "workspace",workspaceId,path:`models/${slug(id)}.json`,document});
    setModelSource(JSON.stringify(document,null,2));
    setModelTarget(`models/${slug(id)}.json`);
  };

  const toggleAvailability = (record: RecordFile<ModelDef>) => perform(async () => {
    if (!record.document) return;
    const effective = effectiveById.get(record.document.id);
    const base = effective?.document || record.document;
    const currentlyEnabled = effective?.resolved?.enabled ?? base.enabled !== false;
    const document = {...base, enabled:!currentlyEnabled};
    const path = workspaceId === "shared" || effective?.source === "workspace" ? (effective?.path || record.path) : `models/${slug(document.id)}.json`;
    await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/file`, {method:"PUT",body:JSON.stringify({path,content:JSON.stringify(document,null,2)})});
    await load();
  });

  const saveBackend = () => perform(async () => {
    const document = JSON.parse(backendSource) as BackendDef;
    if (document.kind !== "backend" || !document.id || !document.provider) throw new Error("Backend requires kind, id, and provider");
    const path = backendTarget || `backends/${slug(document.id)}.json`;
    await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/file`, {method:"PUT", body:JSON.stringify({path,content:JSON.stringify(document,null,2)})});
    const next = await load();
    const saved = next.backends.find(row => row.document?.id === document.id) || null;
    if (saved) openBackend(saved);
  });

  const makeWorkspaceBackend = (record = selectedBackend) => {
    if (!record?.document || workspaceId === "shared") return;
    const document = {...record.document, official:false};
    setSelectedBackend({...record,source:"workspace",workspaceId,path:`backends/${slug(document.id)}.json`,document});
    setBackendSource(JSON.stringify(document,null,2));
    setBackendTarget(`backends/${slug(document.id)}.json`);
  };

  const renderModel = (record: RecordFile<ModelDef>, library = false) => {
    if (!record.document) return null;
    const effective = effectiveById.get(record.document.id) || record;
    const available = effective.resolved?.enabled ?? effective.document?.enabled !== false;
    const customized = effective.source === "workspace";
    const content = <>
      <span>{customized ? "WORKSPACE CUSTOM" : library ? "SHARED MODEL" : "ENABLED MODEL"}</span>
      <b>{record.document.label || record.document.id}</b>
      <small>{record.document.backend} → {record.document.model}</small>
      <p>{record.document.description || "Filesystem model configuration"}</p>
      <em>temp {String((record.document.defaults || {}).temperature ?? "—")} · {available ? "enabled" : "disabled"}</em>
    </>;
    return <div className={`model-library-item ${layout === "list" ? "list" : "tile"} ${selectedModel?.document?.id === record.document.id ? "selected" : ""}`} key={`${record.workspaceId}:${record.path}`}>
      <button className="model-library-open" onClick={() => openModel(record)}>{content}</button>
      <button className={`model-availability ${available ? "on" : "off"}`} onClick={() => toggleAvailability(record)}>{available ? "Enabled for tasks" : "Disabled"}</button>
      {library && workspaceId !== "shared" && !customized && <button className="model-customize" onClick={() => {openModel(record); makeWorkspaceModel(record);}}>Customize</button>}
    </div>;
  };

  if (!snapshot) return <section className="resource-view"><div className="studio-empty">Loading filesystem model library…</div>{error && <div className="backend-error"><b>Error</b><span>{error}</span></div>}</section>;

  return <section className="resource-view llm-model-editor">
    <div className="resource-heading"><div><span>LLM CONFIGURATION</span><h1>Models & backends</h1><p>Backends define provider connectivity. Models inherit a backend and add model IDs, temperature, reasoning, token, and task-availability settings.</p></div><div className="llm-section-switch"><button className={section === "models" ? "active" : ""} onClick={() => setSection("models")}>Models</button><button className={section === "backends" ? "active" : ""} onClick={() => setSection("backends")}>Backends</button></div></div>
    {error && <div className="demo-notice"><b>Configuration error</b><span>{error}</span></div>}

    {section === "models" && <>
      <div className="llm-subhead"><div><span>BACKEND ROUTES</span><b>Official providers + workspace overrides</b></div></div>
      <div className="backend-strip">{[...sharedBackends.filter(row => row.document?.official), ...workspaceBackends].map(row => <button key={`${row.source}:${row.path}`} className={`backend-chip ${row.source === "workspace" ? "workspace" : "official"}`} onClick={() => {openBackend(row);setSection("backends");}}><span>{row.source === "workspace" ? "WORKSPACE" : "OFFICIAL"}</span><b>{row.document?.label || row.document?.id}</b><small>{row.document?.provider}</small></button>)}</div>

      <div className="llm-subhead"><div><span>AVAILABLE TO TASKS</span><b>{activeModels.length} enabled model configurations</b></div><button onClick={() => selectedModel && cloneVariant()}>New variant from selected</button></div>
      <div className="model-grid active-model-grid">{activeModels.map(row => renderModel(row))}</div>

      <div className="llm-subhead library-heading"><div><span>{workspaceId === "shared" ? "SHARED MODEL DEFINITIONS" : "SHARED MODEL LIBRARY"}</span><b>{sharedModels.length} reusable configurations</b></div><div className="layout-switch"><button className={layout === "tiles" ? "active" : ""} onClick={() => setLayout("tiles")}>▦ Tiles</button><button className={layout === "list" ? "active" : ""} onClick={() => setLayout("list")}>☰ List</button></div></div>
      <div className={`shared-model-library ${layout}`}>{sharedModels.map(row => renderModel(row,true))}</div>

      {workspaceModels.length > 0 && <><div className="llm-subhead"><div><span>WORKSPACE MODEL FILES</span><b>Local overrides and variants</b></div></div><div className="model-grid">{workspaceModels.map(row => renderModel(row))}</div></>}

      {selectedModel?.document && <div className="model-editor-panel">
        <div className="model-editor-meta"><span>MODEL CONFIGURATOR</span><h2>{selectedModel.document.label || selectedModel.document.id}</h2><small>{selectedModel.source} · {selectedModel.path}</small><div className="studio-actions">{selectedModel.source === "shared" && workspaceId !== "shared" && <button onClick={() => makeWorkspaceModel()}>Customize in workspace</button>}<button onClick={() => cloneVariant()}>Clone variant</button><button className="primary" onClick={saveModel} disabled={busy}>Save model</button></div><span>INHERITED BACKEND</span><pre className="mini-code">{JSON.stringify((effectiveById.get(selectedModel.document.id)?.resolved || selectedModel.resolved)?.configuration || {},null,2)}</pre></div>
        <div><ModelEditorForm source={modelSource} onChange={setModelSource} backends={effectiveBackends}/><textarea className="raw-json-editor model-raw-editor" value={modelSource} onChange={event => setModelSource(event.target.value)}/></div>
      </div>}
    </>}

    {section === "backends" && <>
      <div className="llm-subhead"><div><span>OFFICIAL BACKENDS</span><b>Shared provider transports</b></div></div>
      <div className="model-grid">{sharedBackends.map(row => <button key={`shared:${row.path}`} className={`model-card ${selectedBackend?.path === row.path && selectedBackend?.source === row.source ? "selected" : ""}`} onClick={() => openBackend(row)}><span>{row.document?.official ? "OFFICIAL BACKEND" : "SHARED BACKEND"}</span><b>{row.document?.label || row.document?.id}</b><small>{row.document?.provider}</small><p>{row.document?.description}</p><em>{row.document?.enabled === false ? "disabled" : "enabled"}</em></button>)}</div>
      {workspaceId !== "shared" && workspaceBackends.length > 0 && <><div className="llm-subhead"><div><span>WORKSPACE BACKENDS</span><b>Local provider overrides</b></div></div><div className="model-grid">{workspaceBackends.map(row => <button key={`workspace:${row.path}`} className={`model-card ${selectedBackend?.path === row.path && selectedBackend?.source === row.source ? "selected" : ""}`} onClick={() => openBackend(row)}><span>WORKSPACE BACKEND</span><b>{row.document?.label || row.document?.id}</b><small>{row.document?.provider}</small><p>{row.document?.description}</p><em>{row.document?.enabled === false ? "disabled" : "enabled"}</em></button>)}</div></>}
      {selectedBackend?.document && <div className="model-editor-panel"><div className="model-editor-meta"><span>BACKEND CONFIGURATOR</span><h2>{selectedBackend.document.label || selectedBackend.document.id}</h2><small>{selectedBackend.source} · {selectedBackend.path}</small><div className="studio-actions">{selectedBackend.source === "shared" && workspaceId !== "shared" && <button onClick={() => makeWorkspaceBackend()}>Customize in workspace</button>}<button className="primary" onClick={saveBackend} disabled={busy}>Save backend</button></div><span>PROVIDER</span><b>{selectedBackend.document.provider}</b><span>CAPABILITIES</span><small>{(selectedBackend.document.capabilities || []).join(", ")}</small></div><textarea className="raw-json-editor model-raw-editor" value={backendSource} onChange={event => setBackendSource(event.target.value)}/></div>}
    </>}
  </section>;
}
