import { useEffect, useMemo, useState } from "react";

type Workspace = {
  id: string;
  label: string;
  description: string;
  root: string;
  workflowDirectoryRelative: string;
  taskDirectoryRelative: string;
  backendDirectoryRelative?: string;
  workflowFileCount: number;
  taskFileCount: number;
  backendFileCount?: number;
};

type Step = {
  id: string;
  label?: string;
  description?: string;
  kind?: string;
  implementation?: string;
  operation?: string;
  dependsOn?: string[];
  inputs?: Record<string, unknown>;
  outputs?: Record<string, string>;
  parameters?: Record<string, unknown>;
  form?: Record<string, unknown>;
};

type Workflow = {
  id: string;
  version?: number;
  label?: string;
  description?: string;
  inputs?: Record<string, string>;
  outputs?: Record<string, string>;
  steps: Step[];
};

type RecordFile<T> = {
  path: string;
  source?: "shared" | "workspace";
  workspaceId?: string;
  document?: T;
  error?: string;
};

type TaskDef = {
  id: string;
  label?: string;
  description?: string;
  implementation: string;
  inputs?: Record<string, string>;
  outputs?: Record<string, string>;
  parameters?: Record<string, unknown>;
};

type BackendDef = {
  kind: "backend";
  id: string;
  label?: string;
  description?: string;
  provider: string;
  enabled?: boolean;
  capabilities?: string[];
  configuration?: Record<string, unknown>;
  settings?: Record<string, unknown>;
  model?: string;
  endpoint?: string;
  executable?: string;
};

type WorkspaceFile = {
  path: string;
  name: string;
  suffix: string;
  size: number;
  modified: number;
  kind: string;
};

type Snapshot = {
  workspace: Workspace;
  workflows: RecordFile<Workflow>[];
  tasks: RecordFile<TaskDef>[];
  backends: RecordFile<BackendDef>[];
  files: WorkspaceFile[];
};

type Run = {
  id: string;
  workflowId: string;
  workflowVersion: number;
  status: string;
  inputs: unknown;
  outputs: unknown;
  error?: string;
  steps: Array<{stepId:string;status:string;attempt?:number;error?:string}>;
  artifacts: Array<{id:string;name:string;datatype?:string;value?:unknown;producer?:string;createdAt?:string}>;
  events: Array<{id:string;kind:string;stepId?:string;createdAt:string;payload?:unknown}>;
  logs: Array<{id:string;stream:string;message:string;createdAt?:string}>;
};

type Capability = { status: string; detail: string };
type View = "canvas" | "editor" | "artifacts" | "evidence" | "tasks" | "llms" | "checks" | "setup";

type EngineImplementation = {
  name: string;
  inputs?: Record<string, unknown>;
  outputs?: Record<string, unknown>;
  [key: string]: unknown;
};

async function request(path: string, init?: RequestInit) {
  const response = await fetch(path, {
    headers: {"Content-Type": "application/json", ...(init?.headers || {})},
    ...init,
  });
  const payload: unknown = await response.json();
  if (!response.ok) {
    const detail = typeof payload === "object" && payload !== null
      ? String((payload as Record<string, unknown>).error || (payload as Record<string, unknown>).detail || response.statusText)
      : response.statusText;
    throw new Error(detail);
  }
  return payload as Record<string, any>;
}

const engine = (path: string, init?: RequestInit) => request(`/api/engine${path}`, init);
const slug = (value: string) => value.toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_+|_+$/g, "") || "item";

function isLlmBackend(record: RecordFile<BackendDef>) {
  const backend = record.document;
  if (!backend) return false;
  const provider = backend.provider.toLowerCase();
  const capabilities = (backend.capabilities || []).join(" ").toLowerCase();
  return capabilities.includes("llm") || /openai|anthropic|openrouter|ollama|unsloth|llm|model/.test(provider);
}

function backendModel(backend?: BackendDef) {
  if (!backend) return "—";
  const config = backend.configuration || {};
  return String(backend.model || config.defaultModel || config.model || backend.id);
}

function backendEndpoint(backend?: BackendDef) {
  if (!backend) return "—";
  const config = backend.configuration || {};
  return String(backend.endpoint || config.baseUrl || config.endpoint || backend.executable || config.executable || "local / configured runtime");
}

export function PolishedFilesystemWorkbenchPage() {
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [workspace, setWorkspace] = useState<Workspace | null>(null);
  const [snapshot, setSnapshot] = useState<Snapshot | null>(null);
  const [view, setView] = useState<View>("canvas");
  const [workflowPath, setWorkflowPath] = useState("");
  const [workflowSource, setWorkflowSource] = useState("");
  const [runInputs, setRunInputs] = useState("{}");
  const [selectedStepId, setSelectedStepId] = useState<string | null>(null);
  const [run, setRun] = useState<Run | null>(null);
  const [validation, setValidation] = useState<string[] | null>(null);
  const [capabilities, setCapabilities] = useState<Record<string, Capability>>({});
  const [implementations, setImplementations] = useState<EngineImplementation[]>([]);
  const [selectedArtifactId, setSelectedArtifactId] = useState<string | null>(null);
  const [selectedBackend, setSelectedBackend] = useState<RecordFile<BackendDef> | null>(null);
  const [backendSource, setBackendSource] = useState("");
  const [backendTarget, setBackendTarget] = useState<string | null>(null);
  const [selectedTask, setSelectedTask] = useState<RecordFile<TaskDef> | null>(null);
  const [taskSource, setTaskSource] = useState("");
  const [taskTarget, setTaskTarget] = useState<string | null>(null);
  const [humanValues, setHumanValues] = useState("{}");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const workflow = useMemo<Workflow | null>(() => {
    try { return workflowSource ? JSON.parse(workflowSource) as Workflow : null; }
    catch { return null; }
  }, [workflowSource]);
  const selectedStep = workflow?.steps.find(step => step.id === selectedStepId) || null;
  const selectedRuntime = run?.steps.find(step => step.stepId === selectedStepId) || null;
  const selectedArtifact = run?.artifacts.find(item => item.id === selectedArtifactId) || run?.artifacts[0] || null;
  const llmBackends = useMemo(() => {
    const rows = (snapshot?.backends || []).filter(isLlmBackend);
    return rows.length ? rows : (snapshot?.backends || []);
  }, [snapshot]);

  useEffect(() => {
    void request("/api/workspaces")
      .then(payload => setWorkspaces((payload.workspaces || []) as Workspace[]))
      .catch(reason => setError(String(reason)));
  }, []);

  useEffect(() => {
    if (!run || ["completed", "failed", "cancelled"].includes(run.status)) return;
    const timer = window.setInterval(() => {
      void engine(`/runs/${run.id}`)
        .then(payload => setRun(payload.run as Run))
        .catch(reason => setError(String(reason)));
    }, 1000);
    return () => window.clearInterval(timer);
  }, [run?.id, run?.status]);

  const perform = async (work: () => Promise<void>) => {
    setBusy(true);
    setError(null);
    try { await work(); }
    catch (reason) { setError(reason instanceof Error ? reason.message : String(reason)); }
    finally { setBusy(false); }
  };

  const refreshSnapshot = async () => {
    if (!workspace) return null;
    const payload = await request(`/api/workspaces/${encodeURIComponent(workspace.id)}/snapshot`);
    const next = payload as unknown as Snapshot;
    setSnapshot(next);
    return next;
  };

  const openBackend = (record: RecordFile<BackendDef>) => {
    if (!workspace) return;
    setSelectedBackend(record);
    setBackendSource(record.document ? JSON.stringify(record.document, null, 2) : "");
    setBackendTarget(record.source === "workspace" || workspace.id === "shared" ? record.path : null);
  };

  const openTask = (record: RecordFile<TaskDef>) => {
    if (!workspace) return;
    setSelectedTask(record);
    setTaskSource(record.document ? JSON.stringify(record.document, null, 2) : "");
    setTaskTarget(record.source === "workspace" || workspace.id === "shared" ? record.path : null);
  };

  const loadWorkspace = (item: Workspace) => perform(async () => {
    const [snapshotPayload, implementationPayload, capabilityPayload] = await Promise.all([
      request(`/api/workspaces/${encodeURIComponent(item.id)}/snapshot`),
      engine("/implementations"),
      engine("/capabilities"),
    ]);
    const next = snapshotPayload as unknown as Snapshot;
    setWorkspace(next.workspace);
    setSnapshot(next);
    setImplementations((implementationPayload.implementations || []) as EngineImplementation[]);
    setCapabilities((capabilityPayload.capabilities || {}) as Record<string, Capability>);
    const firstWorkflow = next.workflows.find(row => row.document);
    if (firstWorkflow?.document) {
      setWorkflowPath(firstWorkflow.path);
      setWorkflowSource(JSON.stringify(firstWorkflow.document, null, 2));
      setSelectedStepId(firstWorkflow.document.steps[0]?.id || null);
      setView("canvas");
    } else {
      setWorkflowPath("");
      setWorkflowSource("");
      setSelectedStepId(null);
      setView("llms");
    }
    const firstBackend = next.backends.find(isLlmBackend) || next.backends[0] || null;
    if (firstBackend) openBackendFor(next.workspace, firstBackend);
    else { setSelectedBackend(null); setBackendSource(""); setBackendTarget(null); }
    const firstTask = next.tasks[0] || null;
    if (firstTask) openTaskFor(next.workspace, firstTask);
    else { setSelectedTask(null); setTaskSource(""); setTaskTarget(null); }
    setRun(null);
    setValidation(null);
    setSelectedArtifactId(null);
  });

  const openBackendFor = (current: Workspace, record: RecordFile<BackendDef>) => {
    setSelectedBackend(record);
    setBackendSource(record.document ? JSON.stringify(record.document, null, 2) : "");
    setBackendTarget(record.source === "workspace" || current.id === "shared" ? record.path : null);
  };

  const openTaskFor = (current: Workspace, record: RecordFile<TaskDef>) => {
    setSelectedTask(record);
    setTaskSource(record.document ? JSON.stringify(record.document, null, 2) : "");
    setTaskTarget(record.source === "workspace" || current.id === "shared" ? record.path : null);
  };

  const openWorkflow = (path: string) => perform(async () => {
    if (!workspace) return;
    const payload = await request(`/api/workspaces/${encodeURIComponent(workspace.id)}/file?path=${encodeURIComponent(path)}`);
    const content = String((payload.file as Record<string, unknown>).content || "");
    setWorkflowPath(path);
    setWorkflowSource(content);
    setValidation(null);
    try {
      const document = JSON.parse(content) as Workflow;
      setSelectedStepId(document.steps[0]?.id || null);
    } catch {
      setSelectedStepId(null);
    }
  });

  const saveWorkflow = () => perform(async () => {
    if (!workspace || !workflow) throw new Error("Select a valid workflow document first");
    const path = workflowPath || `workflows/${slug(workflow.id)}.json`;
    await request(`/api/workspaces/${encodeURIComponent(workspace.id)}/file`, {
      method: "PUT",
      body: JSON.stringify({path, content: JSON.stringify(workflow, null, 2)}),
    });
    setWorkflowPath(path);
    await refreshSnapshot();
  });

  const validateWorkflow = () => perform(async () => {
    if (!workflow) throw new Error("Invalid workflow JSON");
    const payload = await engine("/workflows/validate", {method: "POST", body: JSON.stringify(workflow)});
    setValidation((payload.errors || []) as string[]);
  });

  const startRun = () => perform(async () => {
    if (!workflow || !workspace) throw new Error("Invalid workflow JSON");
    let saved = workflow;
    if (!saved.version) {
      const payload = await engine("/workflows", {method: "POST", body: JSON.stringify(saved)});
      saved = payload.workflow as Workflow;
      const content = JSON.stringify(saved, null, 2);
      setWorkflowSource(content);
      const path = workflowPath || `workflows/${slug(saved.id)}.json`;
      await request(`/api/workspaces/${encodeURIComponent(workspace.id)}/file`, {
        method: "PUT",
        body: JSON.stringify({path, content}),
      });
      setWorkflowPath(path);
    }
    const payload = await engine("/runs", {
      method: "POST",
      body: JSON.stringify({workflowId: saved.id, version: saved.version, inputs: JSON.parse(runInputs)}),
    });
    setRun(payload.run as Run);
    setSelectedArtifactId(null);
  });

  const command = (name: string) => perform(async () => {
    if (!run) return;
    const payload = await engine(`/runs/${run.id}/commands`, {method: "POST", body: JSON.stringify({command: name})});
    setRun(payload.run as Run);
  });

  const submitHuman = () => perform(async () => {
    if (!run || !selectedStepId) return;
    const payload = await engine(`/runs/${run.id}/steps/${selectedStepId}/input`, {method: "POST", body: humanValues});
    setRun(payload.run as Run);
  });

  const saveBackend = () => perform(async () => {
    if (!workspace) throw new Error("Select a workspace");
    const document = JSON.parse(backendSource) as BackendDef;
    if (document.kind !== "backend") throw new Error("Backend must declare kind: backend");
    const path = backendTarget || `backends/${slug(document.id)}.json`;
    await request(`/api/workspaces/${encodeURIComponent(workspace.id)}/file`, {
      method: "PUT",
      body: JSON.stringify({path, content: JSON.stringify(document, null, 2)}),
    });
    const next = await refreshSnapshot();
    const saved = next?.backends.find(row => row.path === path && (workspace.id === "shared" || row.source === "workspace"));
    if (saved) openBackend(saved);
  });

  const makeWorkspaceBackend = () => {
    if (!workspace || workspace.id === "shared" || !selectedBackend?.document) return;
    const document = {...selectedBackend.document};
    setBackendSource(JSON.stringify(document, null, 2));
    setBackendTarget(`backends/${slug(document.id)}.json`);
  };

  const saveTask = () => perform(async () => {
    if (!workspace) throw new Error("Select a workspace");
    const document = JSON.parse(taskSource) as TaskDef;
    const path = taskTarget || `tasks/${slug(document.id)}.json`;
    await request(`/api/workspaces/${encodeURIComponent(workspace.id)}/file`, {
      method: "PUT",
      body: JSON.stringify({path, content: JSON.stringify(document, null, 2)}),
    });
    const next = await refreshSnapshot();
    const saved = next?.tasks.find(row => row.path === path && (workspace.id === "shared" || row.source === "workspace"));
    if (saved) openTask(saved);
  });

  const makeWorkspaceTask = () => {
    if (!workspace || workspace.id === "shared" || !selectedTask?.document) return;
    const document = {...selectedTask.document};
    setTaskSource(JSON.stringify(document, null, 2));
    setTaskTarget(`tasks/${slug(document.id)}.json`);
  };

  if (!workspace) {
    return <main className="workbench-shell">
      <section className="workspace-gate">
        <div className="brand-lockup">
          <span className="brand-mark">M</span>
          <div><b>MeTTa Symbolic Learner Workbench</b><small>Choose a filesystem workspace</small></div>
        </div>
        <div className="workspace-picker-grid">
          {workspaces.map(item => <button className={`workspace-card ${item.id === "shared" ? "shared-workspace-card" : ""}`} key={item.root} onClick={() => loadWorkspace(item)}>
            <span className="workspace-kind">{item.id === "shared" ? "SHARED LIBRARY" : "FILESYSTEM WORKSPACE"}</span>
            <h2>{item.label}</h2>
            <p>{item.description || "Filesystem workspace"}</p>
            <strong>{item.workflowFileCount} workflows · {item.taskFileCount || 0} tasks · {item.backendFileCount || 0} backends</strong>
            <small>{item.root}</small>
          </button>)}
        </div>
        {error && <div className="backend-error"><b>Error</b><span>{error}</span><button onClick={() => setError(null)}>×</button></div>}
      </section>
    </main>;
  }

  const currentStepNumber = Math.max(1, workflow?.steps.findIndex(item => item.id === selectedStepId)! + 1 || 1);
  const nav: Array<[View, string, string]> = [
    ["canvas", "⌘", "Flow"],
    ["editor", "▱", "Studio"],
    ["artifacts", "◇", "Data"],
    ["tasks", "▦", "Tasks"],
    ["llms", "✦", "LLMs"],
    ["checks", "✓", "Checks"],
    ["setup", "⚙", "Setup"],
  ];

  return <main className="workbench">
    <header className="topbar">
      <div className="brand"><span className="brand-mark">M</span><div><strong>MeTTaSymbolicLearnerWorkbench</strong><small>NEUROSYMBOLIC EXPERIMENT DESKTOP</small></div></div>
      <div className="run-context"><span className="pulse"/><b>{run ? run.status : "backend live"}</b><span>/</span><span>{workspace.label}</span><span>/</span><span>{run ? `run ${run.id.slice(0, 8)}` : "ready"}</span></div>
      <div className="toolbar"><button className="icon-button" title="Pause" disabled={!run} onClick={() => command("pause")}>Ⅱ</button><button className="icon-button" title="Stop" disabled={!run} onClick={() => command("cancel")}>□</button><button className="run-button" disabled={busy || !workflow} onClick={startRun}><span>▶</span>Run workflow</button></div>
    </header>
    {error && <div className="backend-error"><b>Error</b><span>{error}</span><button onClick={() => setError(null)}>×</button></div>}

    <section className="workspace">
      <aside className="rail">
        <div className="rail-section"><span>WORKSPACE</span>{nav.map(([id, glyph, label]) => <button key={id} className={`rail-icon ${view === id ? "selected" : ""}`} onClick={() => setView(id)}><span>{glyph}</span><small>{label}</small></button>)}</div>
        <div className="rail-bottom"><button className="rail-icon" onClick={() => {setWorkspace(null); setSnapshot(null); setRun(null);}} title="Switch workspace">↩<small>Switch</small></button></div>
      </aside>

      <aside className="stages-panel">
        <div className="panel-label"><span>RUN PIPELINE</span><button onClick={() => setView("editor")}>•••</button></div>
        <div className="workflow-title"><b>{workflow?.label || workflow?.id || workspace.label}</b><small>{workflow?.description || `${workspace.label} filesystem workflow`}</small></div>
        <div className="stage-list">
          {(workflow?.steps || []).map((item, index) => {
            const status = run?.steps.find(step => step.stepId === item.id)?.status || "defined";
            const active = selectedStepId === item.id;
            return <button key={item.id} className={`stage-button ${active ? "active" : ""} ${status === "completed" ? "done" : ""}`} onClick={() => {setSelectedStepId(item.id); setView("canvas");}}>
              <span className="stage-number">{index + 1}</span><span className="stage-line"/><span className={`stage-icon ${item.kind === "human" ? "amber" : index % 3 === 1 ? "violet" : "cyan"}`}>{status === "completed" ? "✓" : index + 1}</span><div><small>{item.kind || "TASK"}</small><b>{item.label || item.id}</b></div>{item.kind === "subworkflow" && <span className="nested-badge">↳</span>}
            </button>;
          })}
          {!workflow && <div className="studio-empty">No workflow file in this workspace.</div>}
        </div>
        <div className="run-health"><div><span>RUN HEALTH</span><b>{run?.status || "ready"}</b></div><div className="health-bar"><i style={{width: workflow?.steps.length ? `${Math.round(((run?.steps.filter(step => step.status === "completed").length || 0) / workflow.steps.length) * 100)}%` : "0%"}}/></div><small>{run ? `${run.steps.filter(step => step.status === "completed").length} steps complete · ${run.events.length} durable events` : "No active run"}</small></div>
      </aside>

      <section className="main-stage">
        <nav className="view-tabs"><button className={view === "canvas" ? "active" : ""} onClick={() => setView("canvas")}>Workflow canvas</button><button className={view === "editor" ? "active" : ""} onClick={() => setView("editor")}>Workflow editor</button><button className={view === "artifacts" ? "active" : ""} onClick={() => setView("artifacts")}>Artifact explorer <span>{run?.artifacts.length || 0}</span></button><button className={view === "evidence" ? "active" : ""} onClick={() => setView("evidence")}>Evidence & provenance <span>{run?.events.length || 0}</span></button></nav>

        {view === "canvas" && <section className="canvas-view">
          <div className="canvas-heading"><div><span>STAGE {currentStepNumber} OF {workflow?.steps.length || 0}</span><h1>{selectedStep?.label || selectedStep?.id || "Select a workflow step"}</h1><p>{selectedStep?.description || selectedStep?.implementation || selectedStep?.operation || "This view is populated from the selected filesystem workflow."}</p></div><div className={`stage-state ${selectedRuntime?.status || "active"}`}>{(selectedRuntime?.status || "defined").toUpperCase()}</div></div>
          {selectedStep ? <div className="stage-story"><div className="subworkflow-head"><span>{selectedStep.kind === "human" ? "HUMAN" : "STEP"}</span><b>{selectedStep.implementation || selectedStep.operation || selectedStep.kind || "task"}</b><small>{selectedStep.dependsOn?.length ? `depends on ${selectedStep.dependsOn.join(", ")}` : "no explicit dependencies"}</small></div><div className="detail-note"><b>Inputs</b><span><code>{JSON.stringify(selectedStep.inputs || {})}</code></span></div><div className="detail-note"><b>Outputs</b><span><code>{JSON.stringify(selectedStep.outputs || {})}</code></span></div>{selectedRuntime?.status === "waiting" && <div className="human-pause"><div className="pause-ring">Ⅱ</div><b>Waiting for human input</b><span>This is a real engine wait state. Submit the values required by the step form.</span><textarea className="raw-json-editor" style={{height:120}} value={humanValues} onChange={event => setHumanValues(event.target.value)}/><button className="run-button" onClick={submitHuman}>Submit input</button></div>}</div> : <div className="stage-story"><div className="studio-empty">Choose a workflow or use the LLMs, Tasks, Checks, and Setup pages.</div></div>}
          {run && <div className="event-console"><div><span>LIVE RUN EVENT</span><small>{run.status}</small></div>{run.events.slice(-4).reverse().map(event => <p key={event.id}><time>{event.createdAt.slice(11, 19)}</time><i/><span>{event.kind}{event.stepId ? ` · ${event.stepId}` : ""}</span></p>)}</div>}
        </section>}

        {view === "editor" && <section className="editor-surface"><div className="studio-view"><div className="studio-topline"><div><span>WORKFLOW STUDIO</span><h1>{workflow?.label || workflow?.id || "No workflow"}</h1><p>Real JSON from {workspace.root}</p></div><div className="studio-actions"><button onClick={validateWorkflow} disabled={!workflow}>Validate</button><button onClick={saveWorkflow} disabled={!workflow}>Save file</button><button className="primary" onClick={startRun} disabled={!workflow || busy}>Run</button></div></div>{snapshot?.workflows.length ? <select value={workflowPath} onChange={event => openWorkflow(event.target.value)}>{snapshot.workflows.map(row => <option key={row.path} value={row.path}>{row.document?.label || row.document?.id || row.path}</option>)}</select> : null}<textarea className="raw-json-editor" value={workflowSource} onChange={event => setWorkflowSource(event.target.value)} placeholder="No workflow selected"/><div className="workflow-fields"><label className="wide"><span>RUN INPUTS</span><textarea value={runInputs} onChange={event => setRunInputs(event.target.value)}/></label></div>{validation && <div className={validation.length ? "validation bad" : "validation good"}>{validation.length ? validation.join("\n") : "Validated by backend"}</div>}</div></section>}

        {view === "artifacts" && <section className="artifact-view"><div className="artifact-table"><div className="table-head"><span>ARTIFACT</span><span>TYPE</span><span>PRODUCER</span><span>CREATED</span><span/></div>{run?.artifacts.map(item => <button key={item.id} className={selectedArtifact?.id === item.id ? "selected" : ""} onClick={() => setSelectedArtifactId(item.id)}><span><i className="cyan"/>{item.name}</span><span>{item.datatype || "artifact"}</span><span>{item.producer || "engine"}</span><span>{item.createdAt?.slice(11, 19) || "—"}</span><span>›</span></button>) || <div className="studio-empty">Run a workflow to create persisted artifacts.</div>}</div><aside className="artifact-detail">{selectedArtifact ? <><span className="detail-eyebrow">ARTIFACT DETAIL</span><h2>{selectedArtifact.name}</h2><span className="type-chip">{selectedArtifact.datatype || "artifact"}</span><pre>{JSON.stringify(selectedArtifact, null, 2)}</pre></> : <div className="studio-empty">No artifact selected.</div>}</aside></section>}

        {view === "evidence" && <section className="evidence-view"><div className="evidence-summary"><span>RUN EVIDENCE</span><strong>{run?.events.length || 0}<small> events</small></strong><p>Every entry below comes from the persisted workflow-engine run rather than a UI sample.</p><div className="metric-row"><div><span>logs</span><b>{run?.logs.length || 0}</b></div><div><span>artifacts</span><b>{run?.artifacts.length || 0}</b></div></div></div><div className="lineage"><h2>Provenance timeline</h2>{run?.events.map((event, index) => <div className="lineage-node" key={event.id}><span>{index + 1}</span><b>{event.kind}</b><small>{event.stepId || "workflow"} · {event.createdAt}</small></div>) || <p>Run a workflow to generate evidence.</p>}{run?.logs.map(log => <pre className="mini-code" key={log.id}>{log.stream}: {log.message}</pre>)}</div></section>}

        {view === "tasks" && <section className="resource-view"><div className="resource-heading"><div><span>PROCESSING RESOURCES</span><h1>Task library</h1><p>Workspace tasks plus inherited shared tasks, all loaded from disk.</p></div>{selectedTask?.source === "shared" && workspace.id !== "shared" ? <button onClick={makeWorkspaceTask}>Make workspace copy</button> : null}</div><div className="resource-table"><div className="resource-row resource-head"><span>Task</span><span>Implementation</span><span>Source</span><span>Ports</span><span>State</span></div>{snapshot?.tasks.map(row => <button className="resource-row" key={`${row.workspaceId}:${row.path}`} onClick={() => openTask(row)}><b>{row.document?.label || row.document?.id || row.path}</b><code>{row.document?.implementation || "—"}</code><span>{row.source}</span><span>{Object.keys(row.document?.inputs || {}).join(", ") || "∅"} → {Object.keys(row.document?.outputs || {}).join(", ") || "∅"}</span><em>{row.error ? "error" : "ready"}</em></button>)}</div>{selectedTask && <div className="prompt-preview"><div><span>TASK DEFINITION</span><b>{selectedTask.document?.id}</b><small>{selectedTask.path}</small><div className="studio-actions">{selectedTask.source === "shared" && workspace.id !== "shared" && <button onClick={makeWorkspaceTask}>Copy local</button>}<button className="primary" onClick={saveTask}>Save</button></div></div><textarea className="raw-json-editor" style={{height:260,margin:0,border:0}} value={taskSource} onChange={event => setTaskSource(event.target.value)}/></div>}</section>}

        {view === "llms" && <section className="resource-view"><div className="resource-heading"><div><span>MODEL BACKENDS</span><h1>Language models</h1><p>Every workspace inherits the shared LLM backends and may override them locally.</p></div>{selectedBackend?.source === "shared" && workspace.id !== "shared" ? <button onClick={makeWorkspaceBackend}>Make workspace-specific</button> : null}</div><div className="model-grid">{llmBackends.map(row => {const item = row.document; const selected = selectedBackend?.path === row.path && selectedBackend?.workspaceId === row.workspaceId; return <button className={`model-card ${selected ? "selected" : ""}`} key={`${row.workspaceId}:${row.path}`} onClick={() => openBackend(row)}><span>{row.source === "shared" ? "SHARED BACKEND" : "WORKSPACE BACKEND"}</span><b>{item?.label || item?.id || row.path}</b><small>{item?.provider || "backend"}</small><p>{item?.description || "Filesystem backend definition"}</p><em>{backendModel(item)} · {item?.enabled === false ? "disabled" : "available"}</em></button>;})}</div>{selectedBackend?.document ? <div className="prompt-preview"><div><span>ACTIVE BACKEND</span><b>{selectedBackend.document.label || selectedBackend.document.id}</b><small>{selectedBackend.source} · {selectedBackend.path}</small><span>MODEL</span><b>{backendModel(selectedBackend.document)}</b><span>ENDPOINT / EXECUTABLE</span><small>{backendEndpoint(selectedBackend.document)}</small><span>CAPABILITIES</span><small>{(selectedBackend.document.capabilities || []).join(", ") || "not declared"}</small><div className="studio-actions">{selectedBackend.source === "shared" && workspace.id !== "shared" && <button onClick={makeWorkspaceBackend}>Copy local</button>}<button className="primary" onClick={saveBackend}>Save backend</button></div></div><textarea className="raw-json-editor" style={{height:330,margin:0,border:0}} value={backendSource} onChange={event => setBackendSource(event.target.value)}/></div> : <div className="demo-notice"><b>No LLM backend definitions found</b><span>Add a backend JSON file to shared/backends or this workspace's backends directory. The page itself is always available.</span></div>}</section>}

        {view === "checks" && <section className="resource-view"><div className="resource-heading"><div><span>VALIDATION</span><h1>Checks & diagnostics</h1><p>Workflow validation and runtime capability probes are computed by the backend.</p></div><button onClick={validateWorkflow} disabled={!workflow}>Run validation</button></div><div className="checks-summary"><div className="check-score">{validation === null ? "—" : validation.length ? "!" : "✓"}<small>{validation === null ? "idle" : validation.length ? "issues" : "pass"}</small><span>WORKFLOW CHECK</span></div><div className="check-list">{Object.entries(capabilities).map(([name, value]) => <div key={name}><span>{value.status === "implemented" ? "✓" : value.status === "partial" ? "◐" : "·"}</span><b>{name}</b><small>{value.detail}</small><em>{value.status}</em></div>)}</div></div>{validation?.length ? <pre className="mini-code">{validation.join("\n")}</pre> : null}</section>}

        {view === "setup" && <section className="resource-view"><div className="resource-heading"><div><span>WORKSPACE SETUP</span><h1>{workspace.label}</h1><p>{workspace.root}</p></div><button onClick={() => {setWorkspace(null); setSnapshot(null); setRun(null);}}>Switch workspace</button></div><div className="settings-grid"><label><span>WORKSPACE TYPE</span><select value={workspace.id === "shared" ? "shared" : "project"} disabled><option value="shared">Shared library</option><option value="project">Project workspace</option></select><small>{snapshot?.files.length || 0} editable text files discovered from disk.</small></label><label><span>ENGINE IMPLEMENTATIONS</span><select value={implementations.length} disabled><option value={implementations.length}>{implementations.length} registered implementations</option></select><small>These registrations come from the running FastAPI backend.</small></label></div><div className="resource-table" style={{marginTop:14}}><div className="resource-row resource-head"><span>File</span><span>Suffix</span><span>Kind</span><span>Path</span><span>Bytes</span></div>{snapshot?.files.slice(0,500).map(file => <div className="resource-row" key={file.path}><b>{file.name}</b><code>{file.suffix || "—"}</code><span>{file.kind}</span><span>{file.path}</span><em>{file.size}</em></div>)}</div></section>}
      </section>

      <aside className="inspector">
        <div className="inspector-head"><span>LIVE INSPECTOR</span><div><span className="live-dot"/> real data</div></div>
        {view === "llms" && selectedBackend?.document ? <><div className="inspect-section"><div className="section-title"><span>LLM BACKEND</span><b>{selectedBackend.document.provider}</b></div><pre className="mini-code">{JSON.stringify(selectedBackend.document.configuration || selectedBackend.document.settings || {}, null, 2)}</pre></div><div className="provenance-foot"><span>FILESYSTEM SOURCE</span><code>{selectedBackend.path}</code><span className="verified">✓ loaded from {selectedBackend.source}</span></div></> : selectedStep ? <><div className="inspect-section"><div className="section-title"><span>STEP</span><b>{selectedRuntime?.status || "defined"}</b></div><div className="object-list"><button className="selected"><i style={{background:"var(--cyan)"}}/><span><b>{selectedStep.label || selectedStep.id}</b><small>{selectedStep.implementation || selectedStep.kind || "task"}</small></span><em>{selectedRuntime?.attempt || 0}</em></button></div></div><div className="inspect-section"><div className="section-title"><span>INPUTS / OUTPUTS</span></div><pre className="mini-code">{JSON.stringify({inputs:selectedStep.inputs || {}, outputs:selectedStep.outputs || {}}, null, 2)}</pre></div><div className="provenance-foot"><span>WORKFLOW FILE</span><code>{workflowPath || "—"}</code><span className="verified">✓ filesystem backed</span></div></> : <div className="inspect-section"><div className="section-title"><span>WORKSPACE</span></div><pre className="mini-code">{JSON.stringify({id:workspace.id,root:workspace.root,files:snapshot?.files.length || 0}, null, 2)}</pre></div>}
      </aside>
    </section>

    <footer><span><i className="online"/> Backend connected</span><span>{workspace.id === "shared" ? "Shared library" : workspace.id}</span><span>{llmBackends.length} LLM backends</span><span>{run?.artifacts.length || 0} artifacts</span><span className="footer-right">filesystem workspace</span></footer>
  </main>;
}
