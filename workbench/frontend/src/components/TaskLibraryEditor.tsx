import { useEffect, useMemo, useState } from "react";

type Source = "shared" | "workspace";
type ModelStrategy = "single" | "parallel" | "compare" | "fallback";

type RecordFile<T> = {
  path: string;
  source?: Source;
  workspaceId?: string;
  document?: T;
  error?: string;
  resolved?: {enabled?:boolean;backendId?:string;defaults?:Record<string,unknown>};
};

type TaskDef = {
  id: string;
  label?: string;
  description?: string;
  implementation: string;
  inputs?: Record<string,string>;
  outputs?: Record<string,string>;
  parameters?: Record<string,unknown>;
  modelSelection?: {
    models?: string[];
    strategy?: ModelStrategy;
  };
};

type ModelDef = {
  kind: "model";
  id: string;
  label?: string;
  backend: string;
  model: string;
  enabled?: boolean;
  defaults?: Record<string,unknown>;
};

type Snapshot = {
  workspace:{id:string;label:string;root:string};
  tasks:RecordFile<TaskDef>[];
  models:RecordFile<ModelDef>[];
};

const slug = (value:string) => value.toLowerCase().replace(/[^a-z0-9]+/g,"_").replace(/^_+|_+$/g,"") || "task";

async function request(path:string,init?:RequestInit) {
  const response = await fetch(path,{headers:{"Content-Type":"application/json",...(init?.headers || {})},...init});
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.error || payload.detail || response.statusText);
  return payload;
}

export function TaskLibraryEditor({workspaceId}:{workspaceId:string}) {
  const [snapshot,setSnapshot] = useState<Snapshot | null>(null);
  const [selected,setSelected] = useState<RecordFile<TaskDef> | null>(null);
  const [source,setSource] = useState("");
  const [target,setTarget] = useState<string | null>(null);
  const [busy,setBusy] = useState(false);
  const [error,setError] = useState<string | null>(null);

  const load = async () => {
    const next = await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/snapshot`) as Snapshot;
    setSnapshot(next);
    return next;
  };

  useEffect(() => { void load().catch(reason => setError(String(reason))); }, [workspaceId]);

  const document = useMemo<TaskDef | null>(() => { try { return source ? JSON.parse(source) as TaskDef : null; } catch { return null; } }, [source]);
  const enabledModels = (snapshot?.models || []).filter(row => row.document && (row.resolved?.enabled ?? row.document.enabled !== false));
  const selectedModels = document?.modelSelection?.models || [];
  const strategy = document?.modelSelection?.strategy || (selectedModels.length > 1 ? "parallel" : "single");

  const perform = async (work:()=>Promise<void>) => { setBusy(true);setError(null);try{await work();}catch(reason){setError(reason instanceof Error?reason.message:String(reason));}finally{setBusy(false);} };

  const openTask = (record:RecordFile<TaskDef>) => {
    setSelected(record);
    setSource(record.document ? JSON.stringify(record.document,null,2) : "");
    setTarget(workspaceId === "shared" || record.source === "workspace" ? record.path : null);
  };

  useEffect(() => {
    if (snapshot && !selected && snapshot.tasks[0]) openTask(snapshot.tasks[0]);
  }, [snapshot]);

  const ensureWorkspaceTarget = (task:TaskDef) => {
    if (workspaceId !== "shared" && selected?.source === "shared" && !target) setTarget(`tasks/${slug(task.id)}.json`);
  };

  const updateDocument = (next:TaskDef) => {
    ensureWorkspaceTarget(next);
    setSource(JSON.stringify(next,null,2));
  };

  const updateSelection = (models:string[], nextStrategy:ModelStrategy = strategy) => {
    if (!document) return;
    const normalizedStrategy = models.length <= 1 && nextStrategy === "parallel" ? "single" : nextStrategy;
    updateDocument({...document,modelSelection:{models,strategy:normalizedStrategy}});
  };

  const toggleModel = (id:string) => {
    const next = selectedModels.includes(id) ? selectedModels.filter(item => item !== id) : [...selectedModels,id];
    updateSelection(next, next.length > 1 && strategy === "single" ? "parallel" : strategy);
  };

  const save = () => perform(async () => {
    if (!document) throw new Error("Task JSON is invalid");
    const path = target || `tasks/${slug(document.id)}.json`;
    await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/file`,{method:"PUT",body:JSON.stringify({path,content:JSON.stringify(document,null,2)})});
    const next = await load();
    const saved = next.tasks.find(row => row.path === path && (workspaceId === "shared" || row.source === "workspace")) || next.tasks.find(row => row.document?.id === document.id);
    if (saved) openTask(saved);
  });

  const makeWorkspaceCopy = () => {
    if (!document || workspaceId === "shared") return;
    setTarget(`tasks/${slug(document.id)}.json`);
  };

  if (!snapshot) return <section className="resource-view"><div className="studio-empty">Loading task library…</div></section>;

  return <section className="resource-view task-model-editor">
    <div className="resource-heading"><div><span>PROCESSING RESOURCES</span><h1>Task library</h1><p>Task definitions are filesystem resources. LLM tasks can select one or several models from the models enabled on the LLMs page.</p></div>{selected?.source === "shared" && workspaceId !== "shared" ? <button onClick={makeWorkspaceCopy}>Make workspace copy</button> : null}</div>
    {error && <div className="demo-notice"><b>Task editor error</b><span>{error}</span></div>}

    <div className="resource-table"><div className="resource-row resource-head"><span>Task</span><span>Implementation</span><span>Source</span><span>Ports</span><span>Models</span></div>{snapshot.tasks.map(row => <button className="resource-row" key={`${row.workspaceId}:${row.path}`} onClick={() => openTask(row)}><b>{row.document?.label || row.document?.id || row.path}</b><code>{row.document?.implementation || "—"}</code><span>{row.source}</span><span>{Object.keys(row.document?.inputs || {}).join(", ") || "∅"} → {Object.keys(row.document?.outputs || {}).join(", ") || "∅"}</span><em>{row.document?.modelSelection?.models?.length ? `${row.document.modelSelection.models.length} selected` : "default"}</em></button>)}</div>

    {selected && <div className="task-editor-layout">
      <div className="task-definition-panel"><div className="llm-subhead"><div><span>TASK DEFINITION</span><b>{document?.label || document?.id || selected.path}</b></div><div className="studio-actions">{selected.source === "shared" && workspaceId !== "shared" && <button onClick={makeWorkspaceCopy}>Copy local</button>}<button className="primary" onClick={save} disabled={busy || !document}>Save task</button></div></div><textarea className="raw-json-editor task-raw-editor" value={source} onChange={event => setSource(event.target.value)}/></div>

      <div className="task-model-selection"><div className="llm-subhead"><div><span>MODEL DISPATCH</span><b>Models allowed for this task</b></div><div className="studio-actions"><button onClick={() => updateSelection(enabledModels.map(row => row.document!.id), enabledModels.length > 1 ? "parallel" : "single")}>Select all enabled</button><button onClick={() => updateSelection([],"single")}>Clear</button></div></div>
        <p className="task-model-help">Only models enabled on the LLMs page appear here. Selecting several preserves the ARC-style ability to try the same LLM task with multiple model configurations.</p>
        <label className="strategy-field"><span>DISPATCH STRATEGY</span><select value={strategy} onChange={event => updateSelection(selectedModels,event.target.value as ModelStrategy)}><option value="single">single</option><option value="parallel">parallel — run every selected model</option><option value="compare">compare — retain every candidate for comparison</option><option value="fallback">fallback — try models in order until one succeeds</option></select></label>
        <div className="task-model-list">{enabledModels.map(row => {const item=row.document!;const checked=selectedModels.includes(item.id);return <label className={`task-model-option ${checked?"selected":""}`} key={item.id}><input type="checkbox" checked={checked} onChange={() => toggleModel(item.id)}/><span><b>{item.label || item.id}</b><small>{item.backend} → {item.model}</small></span><em>temp {String((item.defaults || {}).temperature ?? "—")}</em></label>;})}</div>
        {!enabledModels.length && <div className="demo-notice"><b>No models are enabled</b><span>Open the LLMs page and enable one or more model configurations before assigning models to this task.</span></div>}
        <div className="task-model-summary"><span>Persisted task configuration</span><pre className="mini-code">{JSON.stringify(document?.modelSelection || {models:[],strategy:"single"},null,2)}</pre></div>
      </div>
    </div>}
  </section>;
}
