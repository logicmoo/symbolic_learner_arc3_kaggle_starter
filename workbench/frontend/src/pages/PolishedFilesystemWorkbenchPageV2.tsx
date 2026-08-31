import { useEffect, useMemo, useState } from "react";
import { DataCatalogPanel } from "../components/DataCatalogPanel";
import { PromptHierarchyPanel } from "../components/PromptHierarchyPanel";

type Workspace = {
  id: string;
  label: string;
  description: string;
  root: string;
  workflowFileCount: number;
  operationFileCount: number;
  backendFileCount?: number;
  modelFileCount?: number;
  promptFileCount?: number;
};

type RecordFile<T> = {
  path: string;
  source?: "shared" | "workspace";
  workspaceId?: string;
  document?: T;
  resolved?: Record<string, unknown>;
  error?: string;
};

type Workflow = {
  kind?: string;
  id: string;
  version?: number;
  label?: string;
  description?: string;
  inputs?: Record<string, unknown>;
  outputs?: Record<string, unknown>;
  steps: Array<{
    id: string;
    label?: string;
    description?: string;
    kind?: string;
    implementation?: string;
    operation?: string;
    dependsOn?: string[];
    inputs?: Record<string, unknown>;
    outputs?: Record<string, string>;
    form?: Record<string, unknown>;
  }>;
};

type ResourceDef = {
  kind: string;
  id: string;
  label?: string;
  description?: string;
  provider?: string;
  implementation?: string;
  implements?: Record<string, unknown>;
  model?: string;
  enabled?: boolean;
  inputs?: Record<string, unknown>;
  outputs?: Record<string, unknown>;
  configuration?: Record<string, unknown>;
  defaults?: Record<string, unknown>;
  capabilities?: string[];
  [key: string]: unknown;
};

type Snapshot = {
  workspace: Workspace;
  workflows: RecordFile<Workflow>[];
  operations: RecordFile<ResourceDef>[];
  operationImplementations?: RecordFile<ResourceDef>[];
  backends: RecordFile<ResourceDef>[];
  models?: RecordFile<ResourceDef>[];
  prompts?: RecordFile<ResourceDef>[];
  promptLibrary?: Record<string, unknown>;
  datatypes?: RecordFile<ResourceDef>[];
  representations?: RecordFile<ResourceDef>[];
  files: Array<{path:string;name:string;suffix:string;size:number;kind:string}>;
};

type Run = {
  id: string;
  workflowId: string;
  workflowVersion: number;
  status: string;
  error?: string;
  steps: Array<{stepId:string;status:string;attempt?:number;error?:string}>;
  artifacts: Array<{id:string;name:string;datatype?:string;representation?:string;payload?:unknown;value?:unknown;stepId?:string;producer?:string;createdAt?:string}>;
  events: Array<{id:string|number;kind:string;stepId?:string;createdAt:string;payload?:unknown}>;
  logs?: Array<{id:string|number;stream:string;message:string;createdAt?:string}>;
};

type Capability = {status:string;detail:string};
type View = "flow" | "studio" | "data" | "operations" | "models" | "prompts" | "evidence" | "checks" | "setup";

async function request(path: string, init?: RequestInit) {
  const response = await fetch(path, {headers:{"Content-Type":"application/json",...(init?.headers || {})},...init});
  const payload = await response.json();
  if (!response.ok) throw new Error(String(payload.error || payload.detail || response.statusText));
  return payload;
}

const engine = (path: string, init?: RequestInit) => request(`/workbench/engine${path}`, init);
const slug = (value: string) => value.toLowerCase().replace(/[^a-z0-9.]+/g,"_").replace(/^_+|_+$/g,"") || "item";

function GenericResourceEditor({workspaceId, title, eyebrow, records, directory, kinds, description}: {
  workspaceId:string;
  title:string;
  eyebrow:string;
  records:RecordFile<ResourceDef>[];
  directory:string;
  kinds:string[];
  description:string;
}) {
  const [selected, setSelected] = useState<RecordFile<ResourceDef> | null>(null);
  const [source, setSource] = useState("");
  const [targetPath, setTargetPath] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    const first = records[0] || null;
    setSelected(first);
    setSource(first?.document ? JSON.stringify(first.document,null,2) : "");
    setTargetPath(first && (first.source === "workspace" || workspaceId === "shared") ? first.path : null);
  }, [workspaceId, records.length]);

  const select = (record: RecordFile<ResourceDef>) => {
    setSelected(record);
    setSource(record.document ? JSON.stringify(record.document,null,2) : "");
    setTargetPath(record.source === "workspace" || workspaceId === "shared" ? record.path : null);
    setMessage(null);
  };

  const makeLocal = () => {
    if (!selected?.document || workspaceId === "shared") return;
    setTargetPath(`${directory}/${slug(selected.document.id)}.${selected.document.kind}.json`);
  };

  const save = async () => {
    try {
      const document = JSON.parse(source) as ResourceDef;
      if (!document.id || !kinds.includes(document.kind)) throw new Error(`Expected kind ${kinds.join(" or ")}`);
      const path = targetPath || `${directory}/${slug(document.id)}.${document.kind}.json`;
      await request(`/workbench/workspaces/${encodeURIComponent(workspaceId)}/file`, {method:"PUT",body:JSON.stringify({path,content:JSON.stringify(document,null,2)})});
      setTargetPath(path);
      setMessage(`Saved ${path}`);
    } catch (reason) {
      setMessage(reason instanceof Error ? reason.message : String(reason));
    }
  };

  return <section className="resource-view">
    <div className="resource-heading"><div><span>{eyebrow}</span><h1>{title}</h1><p>{description}</p></div>{selected?.source === "shared" && workspaceId !== "shared" && <button onClick={makeLocal}>Make workspace override</button>}</div>
    {message && <div className="demo-notice"><b>Resource editor</b><span>{message}</span></div>}
    <div style={{display:"grid",gridTemplateColumns:"minmax(440px,1fr) minmax(430px,1fr)",gap:14}}>
      <div className="resource-table">
        <div className="resource-row resource-head"><span>Resource</span><span>Kind</span><span>Parent / provider</span><span>Source</span><span>State</span></div>
        {records.map(record => <button className="resource-row" key={`${record.workspaceId}:${record.path}`} onClick={() => select(record)} onDoubleClick={() => select(record)}>
          <b>{record.document?.label || record.document?.id || record.path}</b>
          <code>{record.document?.kind || "invalid"}</code>
          <span>{Object.keys(record.document?.implements || {}).join(", ") || record.document?.provider || "—"}</span>
          <span>{record.source}</span>
          <em>{record.error ? "error" : "ready"}</em>
        </button>)}
      </div>
      <div className="prompt-preview"><div><span>FILESYSTEM RESOURCE</span><b>{selected?.document?.id || "Select a resource"}</b><small>{selected?.path || "Double-click a resource to edit it."}</small>{selected?.resolved && <><span>RESOLVED</span><small>{JSON.stringify(selected.resolved)}</small></>}<div className="studio-actions">{selected?.source === "shared" && workspaceId !== "shared" && <button onClick={makeLocal}>Copy local</button>}<button className="primary" disabled={!selected} onClick={save}>Save</button></div></div><textarea className="raw-json-editor" style={{height:430,margin:0,border:0}} value={source} onChange={event => setSource(event.target.value)}/></div>
    </div>
  </section>;
}

export function PolishedFilesystemWorkbenchPageV2() {
  const [workspaces,setWorkspaces] = useState<Workspace[]>([]);
  const [workspace,setWorkspace] = useState<Workspace|null>(null);
  const [snapshot,setSnapshot] = useState<Snapshot|null>(null);
  const [view,setView] = useState<View>("flow");
  const [workflowPath,setWorkflowPath] = useState("");
  const [workflowSource,setWorkflowSource] = useState("");
  const [selectedStepId,setSelectedStepId] = useState<string|null>(null);
  const [runInputs,setRunInputs] = useState("{}");
  const [run,setRun] = useState<Run|null>(null);
  const [humanValues,setHumanValues] = useState("{}");
  const [capabilities,setCapabilities] = useState<Record<string,Capability>>({});
  const [validation,setValidation] = useState<string[]|null>(null);
  const [error,setError] = useState<string|null>(null);
  const [busy,setBusy] = useState(false);

  const workflow = useMemo(() => { try { return workflowSource ? JSON.parse(workflowSource) as Workflow : null; } catch { return null; } },[workflowSource]);
  const selectedStep = workflow?.steps.find(step => step.id === selectedStepId) || null;
  const selectedRuntime = run?.steps.find(step => step.stepId === selectedStepId) || null;
  const modelRecords = useMemo(() => [...(snapshot?.backends || []),...(snapshot?.models || [])], [snapshot]);
  const operationRecords = useMemo(() => [...(snapshot?.operations || []),...(snapshot?.operationImplementations || [])], [snapshot]);

  useEffect(() => { void request("/workbench/workspaces").then(payload => setWorkspaces(payload.workspaces || [])).catch(reason => setError(String(reason))); },[]);
  useEffect(() => {
    if (!run || ["completed","failed","cancelled"].includes(run.status)) return;
    const timer = window.setInterval(() => void engine(`/runs/${run.id}`).then(payload => setRun(payload.run)).catch(reason => setError(String(reason))),1000);
    return () => window.clearInterval(timer);
  },[run?.id,run?.status]);

  const perform = async (work:()=>Promise<void>) => { setBusy(true); setError(null); try { await work(); } catch(reason) { setError(reason instanceof Error ? reason.message : String(reason)); } finally { setBusy(false); } };

  const loadWorkspace = (item:Workspace) => perform(async () => {
    const [payload,caps] = await Promise.all([request(`/workbench/workspaces/${encodeURIComponent(item.id)}/snapshot`),engine("/capabilities")]);
    const next = payload as Snapshot;
    setWorkspace(next.workspace); setSnapshot(next); setCapabilities(caps.capabilities || {});
    const first = next.workflows.find(record => record.document);
    if (first?.document) { setWorkflowPath(first.path); setWorkflowSource(JSON.stringify(first.document,null,2)); setSelectedStepId(first.document.steps[0]?.id || null); setView("flow"); }
    else { setWorkflowPath(""); setWorkflowSource(""); setSelectedStepId(null); setView("data"); }
    setRun(null); setValidation(null);
  });

  const refreshSnapshot = async () => { if (!workspace) return; const payload = await request(`/workbench/workspaces/${encodeURIComponent(workspace.id)}/snapshot`); setSnapshot(payload as Snapshot); };
  const openWorkflow = async (path:string) => { if (!workspace) return; const payload = await request(`/workbench/workspaces/${encodeURIComponent(workspace.id)}/file?path=${encodeURIComponent(path)}`); const content = String(payload.file?.content || ""); setWorkflowPath(path); setWorkflowSource(content); try { const doc = JSON.parse(content) as Workflow; setSelectedStepId(doc.steps[0]?.id || null); } catch { setSelectedStepId(null); } };
  const saveWorkflow = () => perform(async () => { if (!workspace || !workflow) throw new Error("Select valid workflow JSON"); const path = workflowPath || `workflows/${slug(workflow.id)}.workflow.json`; await request(`/workbench/workspaces/${encodeURIComponent(workspace.id)}/file`,{method:"PUT",body:JSON.stringify({path,content:JSON.stringify(workflow,null,2)})}); setWorkflowPath(path); await refreshSnapshot(); });
  const validateWorkflow = () => perform(async () => { if (!workflow) throw new Error("Invalid workflow JSON"); const payload = await engine("/workflows/validate",{method:"POST",body:JSON.stringify(workflow)}); setValidation(payload.errors || []); });
  const startRun = () => perform(async () => {
    if (!workspace || !workflow) throw new Error("Invalid workflow JSON");
    let saved = workflow;
    if (!saved.version) {
      const response = await engine("/workflows",{method:"POST",body:JSON.stringify(saved)}); saved = response.workflow as Workflow;
      const path = workflowPath || `workflows/${slug(saved.id)}.workflow.json`;
      const content = JSON.stringify(saved,null,2); setWorkflowSource(content); setWorkflowPath(path);
      await request(`/workbench/workspaces/${encodeURIComponent(workspace.id)}/file`,{method:"PUT",body:JSON.stringify({path,content})});
    }
    const response = await engine("/runs",{method:"POST",body:JSON.stringify({workflowId:saved.id,version:saved.version,inputs:JSON.parse(runInputs)})}); setRun(response.run);
  });
  const command = (name:string) => perform(async () => { if (!run) return; const response = await engine(`/runs/${run.id}/commands`,{method:"POST",body:JSON.stringify({command:name})}); setRun(response.run); });
  const submitHuman = () => perform(async () => { if (!run || !selectedStepId) return; const response = await engine(`/runs/${run.id}/steps/${selectedStepId}/input`,{method:"POST",body:humanValues}); setRun(response.run); });

  if (!workspace) return <main className="workbench-shell"><section className="workspace-gate"><div className="brand-lockup"><span className="brand-mark">M</span><div><b>MeTTa Symbolic Learner Workbench</b><small>Choose a filesystem workspace</small></div></div><div className="workspace-picker-grid">{workspaces.map(item => <button className={`workspace-card ${item.id === "shared" ? "shared-workspace-card" : ""}`} key={item.root} onClick={() => loadWorkspace(item)}><span className="workspace-kind">{item.id === "shared" ? "SHARED LIBRARY" : "FILESYSTEM WORKSPACE"}</span><h2>{item.label}</h2><p>{item.description}</p><strong>{item.workflowFileCount} workflows · {item.operationFileCount || 0} operations · {item.modelFileCount || item.backendFileCount || 0} models</strong><small>{item.root}</small></button>)}</div>{error && <div className="backend-error"><b>Error</b><span>{error}</span><button onClick={() => setError(null)}>×</button></div>}</section></main>;

  const nav:Array<[View,string,string]> = [["flow","⌘","Flow"],["studio","▱","Studio"],["data","◇","Data"],["operations","▦","Operations"],["models","✦","Models"],["prompts","¶","Prompts"],["evidence","◎","Evidence"],["checks","✓","Checks"],["setup","⚙","Setup"]];
  const complete = run?.steps.filter(step => step.status === "completed").length || 0;

  return <main className="workbench">
    <header className="topbar"><div className="brand"><span className="brand-mark">M</span><div><strong>MeTTaSymbolicLearnerWorkbench</strong><small>REPRESENTATION-INDEPENDENT SYMBOLIC WORKBENCH</small></div></div><div className="run-context"><span className="pulse"/><b>{run?.status || "backend live"}</b><span>/</span><span>{workspace.label}</span><span>/</span><span>{view}</span></div><div className="toolbar"><button className="icon-button" disabled={!run} onClick={() => command("pause")}>Ⅱ</button><button className="icon-button" disabled={!run} onClick={() => command("cancel")}>□</button><button className="run-button" disabled={busy || !workflow} onClick={startRun}><span>▶</span>Run workflow</button></div></header>
    {error && <div className="backend-error"><b>Error</b><span>{error}</span><button onClick={() => setError(null)}>×</button></div>}
    <section className="workspace">
      <aside className="rail"><div className="rail-section"><span>WORKSPACE</span>{nav.map(([id,glyph,label]) => <button key={id} className={`rail-icon ${view === id ? "selected" : ""}`} onClick={() => setView(id)}><span>{glyph}</span><small>{label}</small></button>)}</div><div className="rail-bottom"><button className="rail-icon" onClick={() => {setWorkspace(null);setSnapshot(null);setRun(null);}}>↩<small>Switch</small></button></div></aside>
      <aside className="stages-panel"><div className="panel-label"><span>RUN PIPELINE</span><button onClick={() => setView("studio")}>•••</button></div><div className="workflow-title"><b>{workflow?.label || workflow?.id || workspace.label}</b><small>{workflow?.description || "Filesystem workflow"}</small></div><div className="stage-list">{(workflow?.steps || []).map((step,index) => {const status = run?.steps.find(item => item.stepId === step.id)?.status || "defined"; return <button key={step.id} className={`stage-button ${selectedStepId === step.id ? "active" : ""} ${status === "completed" ? "done" : ""}`} onClick={() => {setSelectedStepId(step.id);setView("flow");}}><span className="stage-number">{index+1}</span><span className="stage-line"/><span className={`stage-icon ${step.kind === "human" ? "amber" : index % 3 === 1 ? "violet" : "cyan"}`}>{status === "completed" ? "✓" : index+1}</span><div><small>{step.kind || "OPERATION"}</small><b>{step.label || step.id}</b></div></button>;})}{!workflow && <div className="studio-empty">No workflow in this workspace.</div>}</div><div className="run-health"><div><span>RUN HEALTH</span><b>{run?.status || "ready"}</b></div><div className="health-bar"><i style={{width:workflow?.steps.length ? `${Math.round((complete/workflow.steps.length)*100)}%` : "0%"}}/></div><small>{run ? `${complete} steps complete · ${run.events.length} events` : "No active run"}</small></div></aside>
      <section className="main-stage">
        {view === "flow" && <section className="canvas-view"><div className="canvas-heading"><div><span>WORKFLOW STEP</span><h1>{selectedStep?.label || selectedStep?.id || "Select a step"}</h1><p>{selectedStep?.description || selectedStep?.implementation || selectedStep?.operation || "Abstract operation execution is resolved by the engine."}</p></div><div className={`stage-state ${selectedRuntime?.status || "active"}`}>{(selectedRuntime?.status || "defined").toUpperCase()}</div></div>{selectedStep && <div className="stage-story"><div className="subworkflow-head"><span>{selectedStep.kind || "OPERATION"}</span><b>{selectedStep.implementation || selectedStep.operation || selectedStep.id}</b><small>{selectedStep.dependsOn?.length ? `depends on ${selectedStep.dependsOn.join(", ")}` : "no explicit dependencies"}</small></div><div className="detail-note"><b>Inputs</b><span><code>{JSON.stringify(selectedStep.inputs || {})}</code></span></div><div className="detail-note"><b>Outputs</b><span><code>{JSON.stringify(selectedStep.outputs || {})}</code></span></div>{selectedRuntime?.status === "waiting" && <div className="human-pause"><div className="pause-ring">Ⅱ</div><b>Waiting for human input</b><textarea className="raw-json-editor" style={{height:120}} value={humanValues} onChange={event => setHumanValues(event.target.value)}/><button className="run-button" onClick={submitHuman}>Submit input</button></div>}</div>}{run && <div className="event-console"><div><span>LIVE RUN EVENTS</span><small>{run.status}</small></div>{run.events.slice(-5).reverse().map(event => <p key={String(event.id)}><time>{event.createdAt?.slice(11,19)}</time><i/><span>{event.kind}{event.stepId ? ` · ${event.stepId}` : ""}</span></p>)}</div>}</section>}

        {view === "studio" && <section className="editor-surface"><div className="studio-view"><div className="studio-topline"><div><span>WORKFLOW STUDIO</span><h1>{workflow?.label || workflow?.id || "No workflow"}</h1><p>Workflows request abstract operation and data contracts; planners select implementations and representations.</p></div><div className="studio-actions"><button disabled={!workflow} onClick={validateWorkflow}>Validate</button><button disabled={!workflow} onClick={saveWorkflow}>Save</button><button className="primary" disabled={!workflow || busy} onClick={startRun}>Run</button></div></div>{snapshot?.workflows.length ? <select value={workflowPath} onChange={event => void openWorkflow(event.target.value)}>{snapshot.workflows.map(record => <option key={record.path} value={record.path}>{record.document?.label || record.document?.id || record.path}</option>)}</select> : null}<textarea className="raw-json-editor" value={workflowSource} onChange={event => setWorkflowSource(event.target.value)}/><div className="workflow-fields"><label className="wide"><span>RUN INPUTS</span><textarea value={runInputs} onChange={event => setRunInputs(event.target.value)}/></label></div>{validation && <div className={validation.length ? "validation bad" : "validation good"}>{validation.length ? validation.join("\n") : "Validated by backend"}</div>}</div></section>}

        {view === "data" && <DataCatalogPanel workspaceId={workspace.id}/>} 
        {view === "prompts" && <PromptHierarchyPanel workspaceId={workspace.id}/>} 
        {view === "operations" && <GenericResourceEditor workspaceId={workspace.id} title="Operations & implementations" eyebrow="ABSTRACT OPERATION CONTRACT SYSTEM" records={operationRecords} directory="operations" kinds={["operation","operation_implementation"]} description="Abstract operations and their Python, Prolog, MeTTa, LLM, and other interchangeable implementations."/>}
        {view === "models" && <GenericResourceEditor workspaceId={workspace.id} title="Models & backends" eyebrow="MODEL CONFIGURATION" records={modelRecords} directory="models" kinds={["backend","model","profile"]} description="Backends provide execution services; models and profiles inherit them and configure model identity and generation defaults."/>}

        {view === "evidence" && <section className="evidence-view"><div className="evidence-summary"><span>RUN EVIDENCE</span><strong>{run?.events.length || 0}<small> events</small></strong><p>Artifacts retain semantic datatype and, as representation-aware execution expands, their concrete representation and conversion provenance.</p><div className="metric-row"><div><span>artifacts</span><b>{run?.artifacts.length || 0}</b></div><div><span>logs</span><b>{run?.logs?.length || 0}</b></div></div></div><div className="lineage"><h2>Artifacts & provenance</h2>{run?.artifacts.map((artifact,index) => <div className="lineage-node" key={artifact.id}><span>{index+1}</span><b>{artifact.name}</b><small>{artifact.datatype || "artifact"}{artifact.representation ? ` / ${artifact.representation}` : ""} · {artifact.stepId || artifact.producer || "workflow"}</small></div>)}{!run && <p>Run a workflow to generate durable evidence.</p>}</div></section>}

        {view === "checks" && <section className="resource-view"><div className="resource-heading"><div><span>VALIDATION</span><h1>Checks & diagnostics</h1><p>Engine capabilities and workflow validation are read from the running backend.</p></div><button disabled={!workflow} onClick={validateWorkflow}>Validate workflow</button></div><div className="checks-summary"><div className="check-score">{validation === null ? "—" : validation.length ? "!" : "✓"}<small>{validation === null ? "idle" : validation.length ? "issues" : "pass"}</small><span>WORKFLOW CHECK</span></div><div className="check-list">{Object.entries(capabilities).map(([name,value]) => <div key={name}><span>{value.status === "implemented" ? "✓" : value.status === "partial" ? "◐" : "·"}</span><b>{name}</b><small>{value.detail}</small><em>{value.status}</em></div>)}</div></div></section>}

        {view === "setup" && <section className="resource-view"><div className="resource-heading"><div><span>WORKSPACE SETUP</span><h1>{workspace.label}</h1><p>{workspace.root}</p></div><button onClick={() => void refreshSnapshot()}>Refresh filesystem</button></div><div className="settings-grid"><label><span>DATA RESOURCES</span><select value={(snapshot?.datatypes?.length || 0)+(snapshot?.representations?.length || 0)} disabled><option>{snapshot?.datatypes?.length || 0} datatypes · {snapshot?.representations?.length || 0} representations</option></select><small>First-class semantic and concrete data resources.</small></label><label><span>KNOWLEDGE RESOURCES</span><select value={(snapshot?.prompts?.length || 0)+operationRecords.length+modelRecords.length} disabled><option>{snapshot?.prompts?.length || 0} prompts · {operationRecords.length} operation resources · {modelRecords.length} model resources</option></select><small>All loaded from shared + workspace filesystem definitions.</small></label></div><div className="resource-table" style={{marginTop:14}}><div className="resource-row resource-head"><span>File</span><span>Suffix</span><span>Kind</span><span>Path</span><span>Bytes</span></div>{snapshot?.files.slice(0,500).map(file => <div className="resource-row" key={file.path}><b>{file.name}</b><code>{file.suffix || "—"}</code><span>{file.kind}</span><span>{file.path}</span><em>{file.size}</em></div>)}</div></section>}
      </section>
      <aside className="inspector"><div className="inspector-head"><span>LIVE INSPECTOR</span><div><span className="live-dot"/> real data</div></div>{selectedStep && (view === "flow" || view === "studio") ? <><div className="inspect-section"><div className="section-title"><span>STEP</span><b>{selectedRuntime?.status || "defined"}</b></div><pre className="mini-code">{JSON.stringify(selectedStep,null,2)}</pre></div><div className="provenance-foot"><span>WORKFLOW FILE</span><code>{workflowPath || "—"}</code><span className="verified">✓ filesystem backed</span></div></> : <div className="inspect-section"><div className="section-title"><span>WORKSPACE</span><b>{view}</b></div><pre className="mini-code">{JSON.stringify({workspace:workspace.id,files:snapshot?.files.length || 0,datatypes:snapshot?.datatypes?.length || 0,representations:snapshot?.representations?.length || 0,prompts:snapshot?.prompts?.length || 0,operations:operationRecords.length,models:modelRecords.length},null,2)}</pre></div>}</aside>
    </section>
    <footer><span><i className="online"/> Backend connected</span><span>{workspace.id === "shared" ? "Shared library" : workspace.id}</span><span>{snapshot?.datatypes?.length || 0} datatypes</span><span>{snapshot?.representations?.length || 0} representations</span><span>{snapshot?.prompts?.length || 0} prompts</span><span className="footer-right">filesystem workspace</span></footer>
  </main>;
}
