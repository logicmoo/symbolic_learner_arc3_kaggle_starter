import { useEffect, useMemo, useState } from "react";
import { WorkflowRunnerTodoReference } from "./WorkflowRunnerTodoReference";
import { jsonValueToMetta } from "../lib/mettaResourceCodec";

type DocumentRecord = { document?: Record<string, any> };
type RuntimeRun = {
  id: string; workflowId: string; workflowVersion: number; status: string;
  createdAt?: string; updatedAt?: string; error?: string;
  inputs: unknown; outputs: unknown;
  steps: Array<{ stepId: string; status: string; attempt?: number; error?: string }>;
  events: Array<{ id: number | string; stepId?: string; kind: string; payload?: unknown; createdAt: string }>;
  artifacts: Array<{ id: string; stepId?: string; name: string; datatype?: string; payload?: unknown; createdAt?: string }>;
  logs: Array<{ id: number | string; stepId?: string; stream: string; message: string; createdAt?: string }>;
};
type WorkflowStep = { id: string; label?: string; kind?: string; operation?: string; implementation?: string; dependsOn?: string[]; inputs?: unknown; outputs?: unknown; form?: Record<string, { type?: string; label?: string; description?: string; default?: unknown; options?: unknown[] }> };
type FrozenWorkflow = { id: string; version: number; label?: string; description?: string; steps: WorkflowStep[] };
type GoalRun = {
  id: string; goalId: string; goalVariantId?: string; planId: string; planVariantId: string;
  contextId?: string; contextVariantId?: string; workflowRunId: string; status: string; createdAt?: string; workflowRun: RuntimeRun;
};
type Mode = "goalRuns" | "workflowRuns" | "execs" | "events" | "states" | "runtimeContexts" | "logs";

async function api(path: string, init?: RequestInit) {
  const response = await fetch(path, { headers: { "Content-Type": "application/json" }, ...init });
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.error || payload.detail || response.statusText);
  return payload;
}

const stamp = (value?: string) => value ? value.replace("T", " ").slice(0, 19) : "—";

function WorkflowRunProjection({ run, workflow, busy, onCommand }: { run: RuntimeRun; workflow: FrozenWorkflow | null; busy: boolean; onCommand: (command: "pause" | "resume" | "advance" | "replay" | "cancel") => void }) {
  const [view, setView] = useState<"topology" | "chronology">("topology");
  const [selectedStepId, setSelectedStepId] = useState("");
  const [selectedEventId, setSelectedEventId] = useState("");
  const steps = workflow?.steps || [];
  const selectedStep = steps.find(step => step.id === selectedStepId) || steps[0];
  const selectedEvent = run.events.find(event => String(event.id) === selectedEventId);
  const selectStep = (stepId: string) => { setSelectedStepId(stepId); setSelectedEventId(""); };
  const selectEvent = (event: RuntimeRun["events"][number]) => { setSelectedEventId(String(event.id)); if (event.stepId) setSelectedStepId(event.stepId); };
  const width = Math.max(760, steps.length * 180);
  const positions = new Map(steps.map((step, index) => [step.id, { x: 95 + index * 170, y: 75 + (index % 2) * 105 }]));
  const stepRuntime = selectedStep ? run.steps.find(item => item.stepId === selectedStep.id) : undefined;
  const artifacts = run.artifacts.filter(item => !selectedStep || item.stepId === selectedStep.id);
  const logs = run.logs.filter(item => !selectedStep || item.stepId === selectedStep.id);

  return <section className="run-projection" aria-label="Selected workflow run projection">
    <div className="run-projection-heading">
      <div><span>FROZEN WORKFLOW v{run.workflowVersion}</span><h2>{workflow?.label || run.workflowId}</h2><small>{run.id} · {run.status} · {run.events.length} durable events</small></div>
      <div className="run-projection-modes" role="group" aria-label="Workflow run view"><button className={view === "topology" ? "active" : ""} onClick={() => setView("topology")}>Topology</button><button className={view === "chronology" ? "active" : ""} onClick={() => setView("chronology")}>Chronology</button></div>
    </div>
    <div className="run-command-controls"><span>RUN CONTROL</span><button disabled={busy || run.status !== "running"} onClick={() => onCommand("pause")}>Pause</button><button disabled={busy || run.status !== "paused"} onClick={() => onCommand("resume")}>Resume</button><button disabled={busy || ["waiting", "paused", "completed", "failed", "cancelled"].includes(run.status)} onClick={() => onCommand("advance")}>Advance</button><button disabled={busy} onClick={() => onCommand("replay")}>Replay as new run</button><button className="danger" disabled={busy || ["completed", "failed", "cancelled"].includes(run.status)} onClick={() => onCommand("cancel")}>Cancel</button></div>
    {view === "topology" ? workflow ? <div className="run-topology-scroll">
      <svg className="run-topology" viewBox={`0 0 ${width} 270`} style={{ minWidth: width }}>
        <defs><marker id={`run-arrow-${run.id}`} viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L10 5L0 10z" /></marker></defs>
        {steps.flatMap(step => (step.dependsOn || []).map(parentId => { const parent = positions.get(parentId), child = positions.get(step.id); if (!parent || !child) return null; const mid = (parent.x + child.x) / 2; return <path key={`${parentId}:${step.id}`} className="run-topology-edge" d={`M${parent.x + 57},${parent.y} C${mid},${parent.y} ${mid},${child.y} ${child.x - 57},${child.y}`} markerEnd={`url(#run-arrow-${run.id})`} />; }))}
        {steps.map((step, index) => { const position = positions.get(step.id)!; const status = run.steps.find(item => item.stepId === step.id)?.status || "defined"; return <g key={step.id} transform={`translate(${position.x - 60},${position.y - 35})`} className={`run-topology-node ${status} ${selectedStep?.id === step.id ? "selected" : ""}`} role="button" tabIndex={0} onClick={() => selectStep(step.id)} onKeyDown={event => { if (event.key === "Enter" || event.key === " ") selectStep(step.id); }}><rect width="120" height="70" rx="8" /><text x="60" y="19" textAnchor="middle" className="node-index">{index + 1}</text><text x="60" y="38" textAnchor="middle" className="node-title">{step.label || step.id}</text><text x="60" y="57" textAnchor="middle" className="node-status">{status}</text></g>; })}
      </svg>
    </div> : <div className="studio-empty">The persisted workflow definition is unavailable.</div>
      : <div className="run-chronology" aria-label="Durable event chronology">{run.events.map((event, index) => <button key={event.id} className={String(event.id) === selectedEventId ? "selected" : ""} onClick={() => selectEvent(event)}><span>{index + 1}</span><b>{event.kind}</b><small>{event.stepId || "workflow"}</small><time>{stamp(event.createdAt)}</time></button>)}{!run.events.length && <div className="studio-empty">This run has no durable events.</div>}</div>}
    <div className="run-projection-inspector">
      <div><span>{selectedEvent ? "EVENT" : "STEP"}</span><h3>{selectedEvent?.kind || selectedStep?.label || selectedStep?.id || "Select a node"}</h3><p>{selectedEvent?.stepId || selectedStep?.implementation || selectedStep?.operation || selectedStep?.kind || "workflow"}</p></div>
      <dl><div><dt>Status</dt><dd>{stepRuntime?.status || run.status}</dd></div><div><dt>Attempt</dt><dd>{stepRuntime?.attempt || 0}</dd></div><div><dt>Artifacts</dt><dd>{artifacts.length}</dd></div><div><dt>Logs</dt><dd>{logs.length}</dd></div></dl>
      {selectedEvent && <pre>{jsonValueToMetta(selectedEvent.payload || {})}</pre>}
      {!selectedEvent && selectedStep && <><details><summary>Step contract</summary><pre>{jsonValueToMetta({ inputs: selectedStep.inputs || {}, outputs: selectedStep.outputs || {} })}</pre></details>{artifacts.map(item => <details key={item.id}><summary>Artifact · {item.name}</summary><pre>{jsonValueToMetta(item.payload)}</pre></details>)}{logs.map(item => <details key={item.id}><summary>{item.stream} log</summary><pre>{item.message}</pre></details>)}</>}
    </div>
  </section>;
}

function HumanInputForm({ step, busy, onSubmit }: { step?: WorkflowStep; busy: boolean; onSubmit: (values: Record<string, unknown>) => void }) {
  const fields = Object.entries(step?.form || {});
  const initial = () => Object.fromEntries(fields.map(([name, spec]) => [name, spec.default ?? (/boolean/i.test(spec.type || "") ? false : "")]));
  const [values, setValues] = useState<Record<string, unknown>>(initial);
  useEffect(() => setValues(initial()), [step?.id]);
  if (!fields.length) return <div className="human-input-contract"><p>This step has no form contract. Submit a JSON object in the advanced editor.</p><textarea className="raw-json-editor" defaultValue="{}" onChange={event => { try { setValues(JSON.parse(event.target.value)); } catch { /* keep the last valid value */ } }} /><button className="run-button" disabled={busy} onClick={() => onSubmit(values)}>Submit human input</button></div>;
  return <div className="human-input-contract">{fields.map(([name, spec]) => {
    const type = String(spec.type || "Text");
    const label = spec.label || name.replaceAll("_", " ");
    if (/boolean/i.test(type)) return <label key={name} className="human-boolean"><input type="checkbox" checked={Boolean(values[name])} onChange={event => setValues(current => ({ ...current, [name]: event.target.checked }))} /><span><b>{label}</b><small>{spec.description || type}</small></span></label>;
    if (spec.options?.length) return <label key={name}><span>{label} <em>{type}</em></span><select value={String(values[name] ?? "")} onChange={event => setValues(current => ({ ...current, [name]: event.target.value }))}>{spec.options.map(option => <option key={String(option)} value={String(option)}>{String(option)}</option>)}</select></label>;
    return <label key={name}><span>{label} <em>{type}</em></span><textarea value={typeof values[name] === "string" ? String(values[name]) : JSON.stringify(values[name] ?? "")} onChange={event => { const raw = event.target.value; let value: unknown = raw; if (/number|integer|float/i.test(type)) value = raw === "" ? null : Number(raw); else if (/object|map|list|array|any/i.test(type)) { try { value = JSON.parse(raw); } catch { value = raw; } } setValues(current => ({ ...current, [name]: value })); }} /><small>{spec.description}</small></label>;
  })}<button className="run-button" disabled={busy} onClick={() => onSubmit(values)}>Submit human input</button></div>;
}

export function RuntimeHistoryView({ mode, workspaceId, goals = [], plans = [], contexts = [], workflows = [], onSelectRun }:{
  mode: Mode; workspaceId: string; goals?: DocumentRecord[]; plans?: DocumentRecord[]; contexts?: DocumentRecord[]; workflows?: DocumentRecord[];
  onSelectRun?: (run: RuntimeRun) => void;
}) {
  const [runs, setRuns] = useState<RuntimeRun[]>([]), [goalRuns, setGoalRuns] = useState<GoalRun[]>([]);
  const [selectedId, setSelectedId] = useState<string>(""), [error, setError] = useState<string>(""), [busy, setBusy] = useState(false);
  const [frozenWorkflow, setFrozenWorkflow] = useState<FrozenWorkflow | null>(null);
  const goalDocs = useMemo(() => goals.map(row => row.document).filter(Boolean) as Record<string, any>[], [goals]);
  const planDocs = useMemo(() => plans.map(row => row.document).filter(Boolean) as Record<string, any>[], [plans]);
  const contextDocs = useMemo(() => contexts.map(row => row.document).filter(Boolean) as Record<string, any>[], [contexts]);
  const workflowIds = useMemo(() => new Set(workflows.map(row => row.document?.id).filter(Boolean)), [workflows]);
  const goalSpecs = goalDocs.filter(doc => doc.kind === "goal"), planSpecs = planDocs.filter(doc => doc.kind === "planning_strategy" || doc.kind === "plan");
  const contextSpecs = contextDocs.filter(doc => doc.kind === "context");
  const availablePlanSpecs = planSpecs.filter(plan => (plan.children || []).some((childId: string) => workflowIds.has(planDocs.find(doc => doc.id === childId)?.workflow)));
  const [goalId, setGoalId] = useState(""), [goalVariantId, setGoalVariantId] = useState("");
  const [planId, setPlanId] = useState(""), [planVariantId, setPlanVariantId] = useState("");
  const [contextId, setContextId] = useState(""), [contextVariantId, setContextVariantId] = useState("");
  const [inputs, setInputs] = useState("{}");
  const goalVariants = goalDocs.filter(doc => doc.kind === "goal_variant" && (doc.parents || []).includes(goalId));
  const planVariants = planDocs.filter(doc => (doc.kind === "planning_strategy_variant" || doc.kind === "plan_variant") && (doc.parents || []).includes(planId) && workflowIds.has(doc.workflow));
  const contextVariants = contextDocs.filter(doc => doc.kind === "context_variant" && (doc.parents || []).includes(contextId));

  const refresh = async () => {
    setError("");
    try {
      const [runPayload, goalPayload] = await Promise.all([
        api("/api/engine/runs?limit=200"),
        api(`/api/goal-runs?workspace_id=${encodeURIComponent(workspaceId)}&limit=200`),
      ]);
      setRuns(runPayload.runs || []); setGoalRuns(goalPayload.goalRuns || []);
    } catch (reason) { setError(String(reason)); }
  };
  useEffect(() => { void refresh(); }, [workspaceId]);
  useEffect(() => {
    if (!goalId && goalSpecs[0]) setGoalId(String(goalSpecs[0].id));
    if ((!planId || !availablePlanSpecs.some(doc => doc.id === planId)) && availablePlanSpecs[0]) setPlanId(String(availablePlanSpecs[0].id));
    if (!availablePlanSpecs.length) setPlanId("");
  }, [goalDocs.length, planDocs.length, workflows.length]);
  useEffect(() => {
    const parent = goalSpecs.find(doc => doc.id === goalId);
    const preferred = goalVariants.find(doc => doc.id === parent?.preferredChild);
    if (!goalVariants.some(doc => doc.id === goalVariantId)) setGoalVariantId(String(preferred?.id || goalVariants[0]?.id || ""));
  }, [goalId, goalDocs.length]);
  useEffect(() => {
    const parent = planSpecs.find(doc => doc.id === planId);
    const preferred = planVariants.find(doc => doc.id === parent?.preferredChild);
    if (!planVariants.some(doc => doc.id === planVariantId)) setPlanVariantId(String(preferred?.id || planVariants[0]?.id || ""));
  }, [planId, planDocs.length, workflows.length]);
  useEffect(() => {
    const parent = contextSpecs.find(doc => doc.id === contextId);
    const preferred = contextVariants.find(doc => doc.id === parent?.preferredChild);
    if (!contextId) setContextVariantId("");
    else if (!contextVariants.some(doc => doc.id === contextVariantId)) setContextVariantId(String(preferred?.id || contextVariants[0]?.id || ""));
  }, [contextId, contextDocs.length]);

  const startGoalRun = async () => {
    setBusy(true); setError("");
    try {
      const payload = await api("/api/goal-runs", { method: "POST", body: JSON.stringify({ workspaceId, goalId, goalVariantId, planId, planVariantId, contextId: contextId || undefined, contextVariantId: contextVariantId || undefined, inputs: JSON.parse(inputs) }) });
      onSelectRun?.(payload.goalRun.workflowRun); await refresh(); setSelectedId(payload.goalRun.id);
    } catch (reason) { setError(String(reason)); } finally { setBusy(false); }
  };
  const chooseRun = (run: RuntimeRun) => { setSelectedId(run.id); onSelectRun?.(run); };
  const selectedRun = runs.find(row => row.id === selectedId) || runs[0];
  useEffect(() => {
    if (mode !== "workflowRuns" || !selectedRun) { setFrozenWorkflow(null); return; }
    let active = true;
    void api(`/api/engine/workflows/${encodeURIComponent(selectedRun.workflowId)}?version=${selectedRun.workflowVersion}`)
      .then(payload => { if (active) setFrozenWorkflow(payload.workflow as FrozenWorkflow); })
      .catch(reason => { if (active) { setFrozenWorkflow(null); setError(String(reason)); } });
    return () => { active = false; };
  }, [mode, selectedRun?.id, selectedRun?.workflowId, selectedRun?.workflowVersion]);
  const selectedGoalRun = goalRuns.find(row => row.id === selectedId);
  const [goalRunWorkflow, setGoalRunWorkflow] = useState<FrozenWorkflow | null>(null);
  useEffect(() => {
    if (!selectedGoalRun) { setGoalRunWorkflow(null); return; }
    let active = true;
    const run = selectedGoalRun.workflowRun;
    void api(`/api/engine/workflows/${encodeURIComponent(run.workflowId)}?version=${run.workflowVersion}`).then(payload => { if (active) setGoalRunWorkflow(payload.workflow as FrozenWorkflow); }).catch(reason => { if (active) setError(String(reason)); });
    return () => { active = false; };
  }, [selectedGoalRun?.id]);
  const waitingStep = selectedGoalRun?.workflowRun.steps.find(step => step.status === "waiting");
  const waitingStepDefinition = goalRunWorkflow?.steps.find(step => step.id === waitingStep?.stepId);
  const submitHumanInput = async (values: Record<string, unknown>) => {
    if (!selectedGoalRun || !waitingStep) return;
    setBusy(true); setError("");
    try {
      const payload = await api(`/api/engine/runs/${encodeURIComponent(selectedGoalRun.workflowRunId)}/steps/${encodeURIComponent(waitingStep.stepId)}/input`, { method: "POST", body: JSON.stringify(values) });
      onSelectRun?.(payload.run); await refresh();
    } catch (reason) { setError(String(reason)); } finally { setBusy(false); }
  };
  const commandGoalRun = async (command: "resume" | "cancel") => {
    if (!selectedGoalRun) return;
    setBusy(true); setError("");
    try {
      const payload = await api(`/api/engine/runs/${encodeURIComponent(selectedGoalRun.workflowRunId)}/commands`, { method: "POST", body: JSON.stringify({ command }) });
      onSelectRun?.(payload.run); await refresh();
    } catch (reason) { setError(String(reason)); } finally { setBusy(false); }
  };
  const commandWorkflowRun = async (command: "pause" | "resume" | "advance" | "replay" | "cancel") => {
    if (!selectedRun) return;
    setBusy(true); setError("");
    try {
      const payload = await api(`/api/engine/runs/${encodeURIComponent(selectedRun.id)}/commands`, { method: "POST", body: JSON.stringify({ command }) });
      const updated = payload.run as RuntimeRun;
      setRuns(current => command === "replay" ? [updated, ...current] : current.map(item => item.id === updated.id ? updated : item));
      setSelectedId(updated.id); onSelectRun?.(updated);
    } catch (reason) { setError(String(reason)); } finally { setBusy(false); }
  };
  const title = { goalRuns: "Goal Runs", workflowRuns: "Workflow Runs", execs: "Execs", events: "Events", states: "States", runtimeContexts: "Contexts", logs: "Logs" }[mode];

  if (mode === "goalRuns") return <section className="resource-view runtime-history-view">
    <div className="resource-heading"><div><span>DURABLE RUNTIME</span><h1>Goal Runs</h1><p>Goals, planning strategies, contexts, executable workflows/plans, and their runs are linked in persistent records.</p></div><button onClick={refresh}>Refresh</button></div>
    {error && <div className="backend-error"><b>Error</b><span>{error}</span></div>}
    <div className="settings-grid goal-run-form">
      <label><span>GOAL</span><select value={goalId} onChange={event => setGoalId(event.target.value)}>{goalSpecs.map(doc => <option key={doc.id} value={doc.id}>{doc.label || doc.id}</option>)}</select></label>
      <label><span>GOAL VARIANT</span><select value={goalVariantId} onChange={event => setGoalVariantId(event.target.value)}>{goalVariants.map(doc => <option key={doc.id} value={doc.id}>{doc.label || doc.id}</option>)}</select></label>
      <label><span>PLANNING STRATEGY</span><select value={planId} onChange={event => setPlanId(event.target.value)}>{availablePlanSpecs.filter(doc => !goalId || (doc.goals || []).includes(goalId)).map(doc => <option key={doc.id} value={doc.id}>{doc.label || doc.id}</option>)}</select><small>{availablePlanSpecs.length ? "Only strategies resolving to a workflow in this workspace are runnable." : "No strategy variant names a workflow available in this workspace."}</small></label>
      <label><span>STRATEGY VARIANT</span><select value={planVariantId} onChange={event => setPlanVariantId(event.target.value)}>{planVariants.map(doc => <option key={doc.id} value={doc.id}>{doc.label || doc.id}</option>)}</select></label>
      <label><span>CONTEXT</span><select value={contextId} onChange={event => setContextId(event.target.value)}><option value="">none</option>{contextDocs.filter(doc => doc.kind === "context").map(doc => <option key={doc.id} value={doc.id}>{doc.label || doc.id}</option>)}</select></label>
      <label><span>CONTEXT VARIANT</span><select value={contextVariantId} disabled={!contextId} onChange={event => setContextVariantId(event.target.value)}><option value="">none</option>{contextVariants.map(doc => <option key={doc.id} value={doc.id}>{doc.label || doc.id}</option>)}</select></label>
      <label><span>WORKFLOW INPUTS (JSON)</span><textarea value={inputs} onChange={event => setInputs(event.target.value)} /></label>
    </div>
    <button className="run-button" disabled={busy || !goalId || !planId} onClick={startGoalRun}>▶ Pursue goal</button>
    <div className="resource-table"><div className="resource-row resource-head"><span>Goal</span><span>Strategy variant</span><span>Status</span><span>Workflow/plan run</span><span>Created</span></div>{goalRuns.map(row => <button className="resource-row" key={row.id} onClick={() => { setSelectedId(row.id); onSelectRun?.(row.workflowRun); }}><b>{row.goalVariantId || row.goalId}</b><code>{row.planVariantId}</code><span>{row.status}</span><span>{row.workflowRunId.slice(0, 8)}</span><em>{stamp(row.createdAt)}</em></button>)}</div>
    {selectedGoalRun && <div className="goal-run-controls"><div><b>Selected pursuit</b><span>{selectedGoalRun.goalVariantId} · {selectedGoalRun.planVariantId} · {selectedGoalRun.contextVariantId || "no context"}</span></div><button disabled={busy || selectedGoalRun.status !== "paused"} onClick={() => void commandGoalRun("resume")}>Resume</button><button disabled={busy || ["completed", "failed", "cancelled"].includes(selectedGoalRun.status)} onClick={() => void commandGoalRun("cancel")}>Cancel</button></div>}
    {waitingStep && <div className="human-pause goal-run-human"><div className="pause-ring">Ⅱ</div><b>Waiting for {waitingStep.stepId}</b><span>{waitingStepDefinition?.label || "Provide the values required by this workflow step."}</span><HumanInputForm step={waitingStepDefinition} busy={busy} onSubmit={values => void submitHumanInput(values)} /></div>}
  </section>;

  const rows = mode === "workflowRuns" ? runs.map(run => ({ key: run.id, a: run.workflowId, b: run.status, c: `${run.steps.length} steps`, d: run.id.slice(0, 8), e: stamp(run.createdAt), run }))
    : mode === "execs" ? runs.flatMap(run => run.steps.map(step => ({ key: `${run.id}:${step.stepId}`, a: step.stepId, b: step.status, c: `attempt ${step.attempt || 0}`, d: run.id.slice(0, 8), e: step.error || "—", run })))
    : mode === "events" ? runs.flatMap(run => run.events.map(event => ({ key: `${run.id}:${event.id}`, a: event.kind, b: event.stepId || "workflow", c: stamp(event.createdAt), d: run.id.slice(0, 8), e: jsonValueToMetta(event.payload || {}), run })))
    : mode === "states" ? runs.flatMap(run => run.artifacts.map(item => ({ key: item.id, a: item.name, b: item.datatype || "Any", c: item.stepId || "input", d: run.id.slice(0, 8), e: jsonValueToMetta(item.payload), run })))
    : mode === "runtimeContexts" ? goalRuns.filter(item => item.contextId).map(item => ({ key: `context:${item.id}`, a: item.contextVariantId || item.contextId || "context", b: item.status, c: stamp(item.createdAt), d: item.workflowRunId.slice(0, 8), e: item.contextId || "—", run: item.workflowRun }))
    : runs.flatMap(run => run.logs.map(log => ({ key: `${run.id}:${log.id}`, a: log.stream, b: log.stepId || "workflow", c: stamp(log.createdAt), d: run.id.slice(0, 8), e: log.message, run })));
  return <section className="resource-view runtime-history-view">
    <div className="resource-heading"><div><span>PERSISTENT ENGINE HISTORY</span><h1>{title}</h1><p>Records are loaded from the durable workflow-engine database across application sessions.</p></div><button onClick={refresh}>Refresh</button></div>
    {error && <div className="backend-error"><b>Error</b><span>{error}</span></div>}
    <div className="resource-table"><div className="resource-row resource-head"><span>Record</span><span>Status / type</span><span>Step / time</span><span>Run</span><span>Detail</span></div>{rows.map(row => <button className="resource-row" key={row.key} onClick={() => chooseRun(row.run)}><b>{row.a}</b><code>{row.b}</code><span>{row.c}</span><span>{row.d}</span><em title={row.e}>{row.e}</em></button>)}{!rows.length && <div className="studio-empty">No persisted {title.toLowerCase()} yet.</div>}</div>
    {mode === "workflowRuns" && selectedRun && <WorkflowRunProjection run={selectedRun} workflow={frozenWorkflow} busy={busy} onCommand={command => void commandWorkflowRun(command)} />}
    {mode === "workflowRuns" && <WorkflowRunnerTodoReference />}
    {mode !== "workflowRuns" && selectedRun && <div className="demo-notice"><b>SELECTED RUN {selectedRun.id.slice(0, 8)}</b><span>{selectedRun.workflowId} · {selectedRun.status} · {selectedRun.events.length} events · {selectedRun.artifacts.length} states</span></div>}
  </section>;
}
