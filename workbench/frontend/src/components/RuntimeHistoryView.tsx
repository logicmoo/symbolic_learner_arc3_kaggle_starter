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

export function RuntimeHistoryView({ mode, workspaceId, goals = [], plans = [], contexts = [], workflows = [], onSelectRun }:{
  mode: Mode; workspaceId: string; goals?: DocumentRecord[]; plans?: DocumentRecord[]; contexts?: DocumentRecord[]; workflows?: DocumentRecord[];
  onSelectRun?: (run: RuntimeRun) => void;
}) {
  const [runs, setRuns] = useState<RuntimeRun[]>([]), [goalRuns, setGoalRuns] = useState<GoalRun[]>([]);
  const [selectedId, setSelectedId] = useState<string>(""), [error, setError] = useState<string>(""), [busy, setBusy] = useState(false);
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
  const [inputs, setInputs] = useState("{}"), [humanValues, setHumanValues] = useState("{}");
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
  const selectedGoalRun = goalRuns.find(row => row.id === selectedId);
  const waitingStep = selectedGoalRun?.workflowRun.steps.find(step => step.status === "waiting");
  const submitHumanInput = async () => {
    if (!selectedGoalRun || !waitingStep) return;
    setBusy(true); setError("");
    try {
      const payload = await api(`/api/engine/runs/${encodeURIComponent(selectedGoalRun.workflowRunId)}/steps/${encodeURIComponent(waitingStep.stepId)}/input`, { method: "POST", body: JSON.stringify(JSON.parse(humanValues)) });
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
    {waitingStep && <div className="human-pause goal-run-human"><div className="pause-ring">Ⅱ</div><b>Waiting for {waitingStep.stepId}</b><textarea className="raw-json-editor" value={humanValues} onChange={event => setHumanValues(event.target.value)} /><button className="run-button" disabled={busy} onClick={() => void submitHumanInput()}>Submit human input</button></div>}
  </section>;

  const rows = mode === "workflowRuns" ? runs.map(run => ({ key: run.id, a: run.workflowId, b: run.status, c: `${run.steps.length} steps`, d: run.id.slice(0, 8), e: stamp(run.createdAt), run }))
    : mode === "execs" ? runs.flatMap(run => run.steps.map(step => ({ key: `${run.id}:${step.stepId}`, a: step.stepId, b: step.status, c: `attempt ${step.attempt || 0}`, d: run.id.slice(0, 8), e: step.error || "—", run })))
    : mode === "events" ? runs.flatMap(run => run.events.map(event => ({ key: `${run.id}:${event.id}`, a: event.kind, b: event.stepId || "workflow", c: stamp(event.createdAt), d: run.id.slice(0, 8), e: jsonValueToMetta(event.payload || {}), run })))
    : mode === "states" ? runs.flatMap(run => run.artifacts.map(item => ({ key: item.id, a: item.name, b: item.datatype || "Any", c: item.stepId || "input", d: run.id.slice(0, 8), e: jsonValueToMetta(item.payload), run })))
    : mode === "runtimeContexts" ? goalRuns.filter(item => item.contextId).map(item => ({ key: `context:${item.id}`, a: item.contextVariantId || item.contextId || "context", b: item.status, c: stamp(item.createdAt), d: item.workflowRunId.slice(0, 8), e: item.contextId || "—", run: item.workflowRun }))
    : runs.flatMap(run => run.logs.map(log => ({ key: `${run.id}:${log.id}`, a: log.stream, b: log.stepId || "workflow", c: stamp(log.createdAt), d: run.id.slice(0, 8), e: log.message, run })));
  return <section className="resource-view runtime-history-view">
    <div className="resource-heading"><div><span>PERSISTENT ENGINE HISTORY</span><h1>{title}</h1><p>Records are loaded from the durable workflow-engine database across application sessions.</p></div><button onClick={refresh}>Refresh</button></div>
    {mode === "workflowRuns" && <WorkflowRunnerTodoReference />}
    {error && <div className="backend-error"><b>Error</b><span>{error}</span></div>}
    <div className="resource-table"><div className="resource-row resource-head"><span>Record</span><span>Status / type</span><span>Step / time</span><span>Run</span><span>Detail</span></div>{rows.map(row => <button className="resource-row" key={row.key} onClick={() => chooseRun(row.run)}><b>{row.a}</b><code>{row.b}</code><span>{row.c}</span><span>{row.d}</span><em title={row.e}>{row.e}</em></button>)}{!rows.length && <div className="studio-empty">No persisted {title.toLowerCase()} yet.</div>}</div>
    {selectedRun && <div className="demo-notice"><b>SELECTED RUN {selectedRun.id.slice(0, 8)}</b><span>{selectedRun.workflowId} · {selectedRun.status} · {selectedRun.events.length} events · {selectedRun.artifacts.length} states</span></div>}
  </section>;
}
