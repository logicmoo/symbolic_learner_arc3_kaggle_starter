import { lazy, Suspense, useEffect, useMemo, useState } from "react";
import { jsonValueToMetta } from "../lib/mettaResourceCodec";

const WorkflowRunnerTodoReference = lazy(() => import("./WorkflowRunnerTodoReference").then(module => ({ default: module.WorkflowRunnerTodoReference })));

type DocumentRecord = { document?: Record<string, any> };
type RuntimeRun = {
  id: string; workflowId: string; workflowVersion: number; status: string;
  createdAt?: string; updatedAt?: string; error?: string;
  inputs: unknown; outputs: unknown;
  steps: Array<{ stepId: string; status: string; attempt?: number; error?: string }>;
  events: Array<{ id: number | string; stepId?: string; kind: string; payload?: unknown; createdAt: string }>;
  artifacts: Array<{ id: string; stepId?: string; name: string; datatype?: string; representation?: string; payload?: unknown; contentHash?: string; provenance?: Record<string, unknown>; createdAt?: string }>;
  logs: Array<{ id: number | string; stepId?: string; stream: string; message: string; createdAt?: string }>;
};
type WorkflowStep = { id: string; label?: string; kind?: string; operation?: string; implementation?: string; dependsOn?: string[]; inputs?: unknown; outputs?: unknown; form?: Record<string, { type?: string; label?: string; description?: string; default?: unknown; options?: unknown[]; secret?: boolean; sensitive?: boolean }> };
type FrozenWorkflow = { id: string; version: number; label?: string; description?: string; steps: WorkflowStep[] };
type WorkflowInputContract = string | { datatype?: string; type?: string; representation?: string; default?: unknown; options?: unknown[] };
type GoalRun = {
  id: string; goalId: string; goalVariantId?: string; planId: string; planVariantId: string;
  contextId?: string; contextVariantId?: string; workflowRunId: string; status: string; createdAt?: string; workflowRun: RuntimeRun;
};
type InvocationTrace = {
  id: string; kind: string; status: string; createdAt?: string; logPath: string;
  modelId?: string; operationId?: string; prompt?: string; error?: unknown;
  response?: { text?: string; latencyMs?: number; backendId?: string };
  implementation?: { id?: string; label?: string; implementation?: string };
  operation?: { id?: string; label?: string };
  inputs?: unknown; result?: unknown;
};
type Mode = "goalRuns" | "workflowRuns" | "execs" | "events" | "states" | "runtimeContexts" | "logs";

async function api(path: string, init?: RequestInit) {
  const response = await fetch(path, { headers: { "Content-Type": "application/json" }, ...init });
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.error || payload.detail || response.statusText);
  return payload;
}

const stamp = (value?: string) => value ? value.replace("T", " ").slice(0, 19) : "—";
const artifactColors = ["#101820", "#2d8cff", "#ff3b4f", "#28c76f", "#ffd43b", "#8b5cf6", "#ff9f43", "#19d3da", "#f8fafc", "#5b6573"];
function visualArtifactPayload(payload: unknown): { image?: string; grid?: number[][] } | null {
  if (Array.isArray(payload) && payload.length > 0 && payload.every(row => Array.isArray(row) && row.every(cell => typeof cell === "number"))) return { grid: payload as number[][] };
  if (typeof payload === "string" && payload.startsWith("data:image/")) return { image: payload };
  if (payload && typeof payload === "object") {
    const value = payload as Record<string, unknown>;
    const image = [value.dataUrl, value.data_url, value.image].find(item => typeof item === "string" && item.startsWith("data:image/"));
    if (typeof image === "string") return { image };
    if (Array.isArray(value.grid) && value.grid.length > 0 && value.grid.every(row => Array.isArray(row) && row.every(cell => typeof cell === "number"))) return { grid: value.grid as number[][] };
  }
  return null;
}
function ArtifactVisual({ artifact }: { artifact: RuntimeRun["artifacts"][number] }) {
  const visual = visualArtifactPayload(artifact.payload);
  if (!visual) return null;
  return <figure className="run-artifact-visual"><figcaption><b>{artifact.name}</b><span>{artifact.datatype || "visual artifact"}</span></figcaption>{visual.image ? <img src={visual.image} alt={artifact.name} /> : <div className="run-artifact-grid" style={{ gridTemplateColumns: `repeat(${visual.grid?.[0]?.length || 1}, 1fr)` }}>{visual.grid?.flatMap((row, rowIndex) => row.map((cell, columnIndex) => <i key={`${rowIndex}:${columnIndex}`} style={{ background: artifactColors[Math.abs(cell) % artifactColors.length] }} title={`${columnIndex},${rowIndex}: ${cell}`} />))}</div>}</figure>;
}
function artifactRecords(artifact: RuntimeRun["artifacts"][number], collectionKeys: string[]): Record<string, unknown>[] {
  const payload = artifact.payload;
  if (Array.isArray(payload)) return payload.filter(item => item && typeof item === "object") as Record<string, unknown>[];
  if (!payload || typeof payload !== "object") return [];
  const record = payload as Record<string, unknown>;
  for (const key of collectionKeys) if (Array.isArray(record[key])) return (record[key] as unknown[]).filter(item => item && typeof item === "object") as Record<string, unknown>[];
  return [record];
}

type RuntimeResourceKind = "operation" | "model" | "datatype";
type OpenRuntimeResource = (kind: RuntimeResourceKind, id: string) => void;

type WorkflowRunCommand = "pause" | "resume" | "advance" | "replay" | "cancel";

function WorkflowRunProjection({ run, workflow, busy, onCommand, onOpenResource, commands = ["pause", "resume", "advance", "replay", "cancel"] }: { run: RuntimeRun; workflow: FrozenWorkflow | null; busy: boolean; onCommand: (command: WorkflowRunCommand) => void; onOpenResource?: OpenRuntimeResource; commands?: WorkflowRunCommand[] }) {
  const initialView = new URLSearchParams(window.location.search).get("runView") === "chronology" ? "chronology" : "topology";
  const [view, setViewState] = useState<"topology" | "chronology">(initialView);
  const setView = (next: "topology" | "chronology") => { setViewState(next); const url = new URL(window.location.href); if (next === "topology") url.searchParams.delete("runView"); else url.searchParams.set("runView", next); window.history.replaceState(null, "", `${url.pathname}${url.search}${url.hash}`); };
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
  const artifacts = run.artifacts.filter(item => !selectedStep || !item.stepId || item.stepId === selectedStep.id);
  const logs = run.logs.filter(item => !selectedStep || item.stepId === selectedStep.id);
  const stepEvents = run.events.filter(event => !selectedStep || event.stepId === selectedStep.id);
  const latestStepEvent = stepEvents.at(-1);
  const visualArtifacts = run.artifacts.filter(item => visualArtifactPayload(item.payload));
  const sourceVisual = visualArtifacts.find(item => /source|input|before|observation/i.test(item.name)) || visualArtifacts[0];
  const renderedVisual = visualArtifacts.find(item => item.id !== sourceVisual?.id && /render|reconstruct|output|after|result/i.test(item.name)) || visualArtifacts.find(item => item.id !== sourceVisual?.id);
  const hypothesisRecords = run.artifacts.filter(item => /hypothesis/i.test(`${item.datatype || ""} ${item.name}`)).flatMap(item => artifactRecords(item, ["hypotheses", "items"]));
  const evidenceRecords = run.artifacts.filter(item => /evidence/i.test(`${item.datatype || ""} ${item.name}`)).flatMap(item => artifactRecords(item, ["evidence", "items"]));
  const experimentRecords = run.artifacts.filter(item => /experiment/i.test(`${item.datatype || ""} ${item.name}`)).flatMap(item => artifactRecords(item, ["experiments", "suggestedExperiments", "items"]));
  const totalSteps = Math.max(steps.length, run.steps.length);
  const completedSteps = run.steps.filter(item => item.status === "completed").length;
  const activeSteps = run.steps.filter(item => ["running", "waiting", "paused"].includes(item.status)).length;
  const failedSteps = run.steps.filter(item => item.status === "failed").length;
  const completionPercent = totalSteps ? Math.round(completedSteps / totalSteps * 100) : run.status === "completed" ? 100 : 0;

  return <section className="run-projection" aria-label="Selected workflow run projection">
    <div className="run-projection-heading">
      <div><span>FROZEN WORKFLOW v{run.workflowVersion}</span><h2>{workflow?.label || run.workflowId}</h2><small>{run.id} · {run.status} · {run.events.length} durable events</small></div>
      <div className="run-projection-modes" role="group" aria-label="Workflow run view"><button className={view === "topology" ? "active" : ""} onClick={() => setView("topology")}>Topology</button><button className={view === "chronology" ? "active" : ""} onClick={() => setView("chronology")}>Chronology</button></div>
    </div>
    <div className="run-command-controls"><span>RUN CONTROL</span>{commands.includes("pause") && <button disabled={busy || run.status !== "running"} onClick={() => onCommand("pause")}>Pause</button>}{commands.includes("resume") && <button disabled={busy || run.status !== "paused"} onClick={() => onCommand("resume")}>Resume</button>}{commands.includes("advance") && <button disabled={busy || ["waiting", "paused", "completed", "failed", "cancelled"].includes(run.status)} onClick={() => onCommand("advance")}>Advance</button>}{commands.includes("replay") && <button disabled={busy} onClick={() => onCommand("replay")}>Replay as new run</button>}{commands.includes("cancel") && <button className="danger" disabled={busy || ["completed", "failed", "cancelled"].includes(run.status)} onClick={() => onCommand("cancel")}>Cancel</button>}</div>
    <div className={`run-health-strip ${failedSteps ? "unhealthy" : run.status}`}>
      <div className="run-health-heading"><span>RUN HEALTH</span><b>{run.status}</b><strong>{completionPercent}%</strong></div>
      <div className="run-health-progress" role="progressbar" aria-label="Workflow completion" aria-valuemin={0} aria-valuemax={100} aria-valuenow={completionPercent}><i style={{ width: `${completionPercent}%` }} /></div>
      <dl><div><dt>Completed</dt><dd>{completedSteps} / {totalSteps}</dd></div><div><dt>Active</dt><dd>{activeSteps}</dd></div><div><dt>Failures</dt><dd>{failedSteps}</dd></div><div><dt>Durable events</dt><dd>{run.events.length}</dd></div><div><dt>Artifacts</dt><dd>{run.artifacts.length}</dd></div><div><dt>Logs</dt><dd>{run.logs.length}</dd></div></dl>
    </div>
    {view === "topology" ? workflow ? <div className="run-topology-scroll">
      <svg className="run-topology" viewBox={`0 0 ${width} 270`} style={{ minWidth: width }}>
        <defs><marker id={`run-arrow-${run.id}`} viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L10 5L0 10z" /></marker></defs>
        {steps.flatMap(step => (step.dependsOn || []).map(parentId => { const parent = positions.get(parentId), child = positions.get(step.id); if (!parent || !child) return null; const mid = (parent.x + child.x) / 2; return <path key={`${parentId}:${step.id}`} className="run-topology-edge" d={`M${parent.x + 57},${parent.y} C${mid},${parent.y} ${mid},${child.y} ${child.x - 57},${child.y}`} markerEnd={`url(#run-arrow-${run.id})`} />; }))}
        {steps.map((step, index) => { const position = positions.get(step.id)!; const status = run.steps.find(item => item.stepId === step.id)?.status || "defined"; return <g key={step.id} transform={`translate(${position.x - 60},${position.y - 35})`} className={`run-topology-node ${status} ${selectedStep?.id === step.id ? "selected" : ""}`} role="button" tabIndex={0} onClick={() => selectStep(step.id)} onKeyDown={event => { if (event.key === "Enter" || event.key === " ") selectStep(step.id); }}><rect width="120" height="70" rx="8" /><text x="60" y="19" textAnchor="middle" className="node-index">{index + 1}</text><text x="60" y="38" textAnchor="middle" className="node-title">{step.label || step.id}</text><text x="60" y="57" textAnchor="middle" className="node-status">{status}</text></g>; })}
      </svg>
    </div> : <div className="studio-empty">The persisted workflow definition is unavailable.</div>
      : <div className="run-chronology" aria-label="Durable event chronology">{run.events.map((event, index) => <button key={event.id} className={String(event.id) === selectedEventId ? "selected" : ""} onClick={() => selectEvent(event)}><span>{index + 1}</span><b>{event.kind}</b><small>{event.stepId || "workflow"}</small><time>{stamp(event.createdAt)}</time></button>)}{!run.events.length && <div className="studio-empty">This run has no durable events.</div>}</div>}
    {selectedStep && <div className="run-stage-narrative"><div><span>SELECTED STAGE</span><h3>{selectedStep.label || selectedStep.id}</h3><p>{selectedStep.implementation || selectedStep.operation || selectedStep.kind || "operation"}</p>{selectedStep.operation && onOpenResource && <button type="button" className="runtime-resource-link" onClick={() => onOpenResource("operation", selectedStep.operation!)}>Open Operation · {selectedStep.operation}</button>}</div><div><span>RUNTIME OUTCOME</span><b>{stepRuntime?.status || "defined"}</b><small>{stepRuntime?.error || latestStepEvent?.kind || "No execution event yet"}</small></div><div><span>DURABLE EVIDENCE</span><b>{artifacts.length} artifacts · {stepEvents.length} events</b><small>{artifacts.map(item => item.name).join(", ") || "No produced artifacts"}</small></div></div>}
    {sourceVisual && <div className={`run-visual-comparison ${renderedVisual ? "paired" : "single"}`}><div className="run-visual-comparison-title"><span>{renderedVisual ? "SOURCE / RENDER COMPARISON" : "VISUAL ARTIFACT"}</span><small>Persisted run payloads · no generated preview data</small></div><ArtifactVisual artifact={sourceVisual} />{renderedVisual && <ArtifactVisual artifact={renderedVisual} />}</div>}
    {(hypothesisRecords.length > 0 || evidenceRecords.length > 0 || experimentRecords.length > 0) && <div className="run-reasoning-evidence"><div className="run-visual-comparison-title"><span>REASONING EVIDENCE</span><small>Typed artifacts persisted by this run</small></div>{hypothesisRecords.map((record, index) => <article className="run-hypothesis" key={`hypothesis:${String(record.id || index)}`}><span>H{index + 1}</span><div><b>{String(record.statement || record.label || record.id || "Hypothesis")}</b><small>{String(record.status || "revisable")}</small></div>{typeof record.confidence === "number" && <strong>{record.confidence.toFixed(2)}</strong>}</article>)}{evidenceRecords.map((record, index) => <article className="run-evidence-record" key={`evidence:${String(record.id || index)}`}><span>E{index + 1}</span><div><b>{String(record.observation || record.statement || record.id || "Evidence")}</b><small>{Array.isArray(record.supports) ? `supports ${record.supports.join(", ")}` : "transition evidence"}</small></div></article>)}{experimentRecords.map((record, index) => <article className="run-experiment" key={`experiment:${String(record.id || index)}`}><span>TRY</span><div><b>{String(record.instruction || record.label || record.id || "Suggested experiment")}</b><small>{String(record.rationale || "Persisted experiment proposal")}</small></div>{typeof record.expectedInformationGain === "number" && <strong>{record.expectedInformationGain.toFixed(2)}</strong>}</article>)}</div>}
    <div className="run-projection-inspector">
      <div><span>{selectedEvent ? "EVENT" : "STEP"}</span><h3>{selectedEvent?.kind || selectedStep?.label || selectedStep?.id || "Select a node"}</h3><p>{selectedEvent?.stepId || selectedStep?.implementation || selectedStep?.operation || selectedStep?.kind || "workflow"}</p></div>
      <dl><div><dt>Status</dt><dd>{stepRuntime?.status || run.status}</dd></div><div><dt>Attempt</dt><dd>{stepRuntime?.attempt || 0}</dd></div><div><dt>Artifacts</dt><dd>{artifacts.length}</dd></div><div><dt>Logs</dt><dd>{logs.length}</dd></div></dl>
      {selectedEvent && <pre>{jsonValueToMetta(selectedEvent.payload || {})}</pre>}
      {!selectedEvent && selectedStep && <><details><summary>Step contract</summary><pre>{jsonValueToMetta({ inputs: selectedStep.inputs || {}, outputs: selectedStep.outputs || {} })}</pre></details>{artifacts.map(item => { const operationId = String(item.provenance?.operationId || ""); const modelId = String(item.provenance?.modelId || ""); const datatypeId = String(item.datatype || ""); const representationId = String(item.representation || ""); return <details key={item.id}><summary>Artifact · {item.name} · {item.datatype || "Any"}{representationId ? ` / ${representationId}` : ""}</summary><pre>{jsonValueToMetta(item.payload)}</pre><dl className="artifact-provenance"><div><dt>Content hash</dt><dd>{item.contentHash || "unavailable"}</dd></div><div><dt>Provenance</dt><dd>{jsonValueToMetta(item.provenance || {})}</dd></div></dl>{onOpenResource && <div className="runtime-resource-links">{datatypeId && !/^any$/i.test(datatypeId) && <button type="button" onClick={() => onOpenResource("datatype", datatypeId)}>Open Datatype · {datatypeId}</button>}{representationId && <button type="button" onClick={() => onOpenResource("datatype", representationId)}>Open Representation · {representationId}</button>}{operationId && <button type="button" onClick={() => onOpenResource("operation", operationId)}>Open producing Operation · {operationId}</button>}{modelId && <button type="button" onClick={() => onOpenResource("model", modelId)}>Open producing Model · {modelId}</button>}</div>}</details>})}{logs.map(item => <details key={item.id}><summary>{item.stream} log</summary><pre>{item.message}</pre></details>)}</>}
    </div>
  </section>;
}

export function HumanInputForm({ step, busy, draft, onDraft, onSubmit }: { step?: WorkflowStep; busy: boolean; draft: Record<string, unknown>; onDraft: (values: Record<string, unknown>) => void; onSubmit: (values: Record<string, unknown>) => void }) {
  const fields = Object.entries(step?.form || {});
  const initial = () => Object.fromEntries(fields.map(([name, spec]) => [name, draft[name] ?? spec.default ?? (/boolean/i.test(spec.type || "") ? false : "")]));
  const [values, setValues] = useState<Record<string, unknown>>(initial);
  useEffect(() => setValues(initial()), [step?.id, JSON.stringify(draft)]);
  const update = (name: string, value: unknown) => setValues(current => { const next = { ...current, [name]: value }; onDraft(next); return next; });
  if (!fields.length) return <div className="human-input-contract"><p>This step has no form contract. Submit a JSON object in the advanced editor.</p><textarea className="raw-json-editor" defaultValue="{}" onChange={event => { try { setValues(JSON.parse(event.target.value)); } catch { /* keep the last valid value */ } }} /><button className="run-button" disabled={busy} onClick={() => onSubmit(values)}>Submit human input</button></div>;
  return <div className="human-input-contract">{fields.map(([name, spec]) => {
    const type = String(spec.type || "Text");
    const label = spec.label || name.replaceAll("_", " ");
    if (/boolean/i.test(type)) return <label key={name} className="human-boolean"><input type="checkbox" checked={Boolean(values[name])} onChange={event => update(name, event.target.checked)} /><span><b>{label}</b><small>{spec.description || type}</small></span></label>;
    if (spec.options?.length) return <label key={name}><span>{label} <em>{type}</em></span><select value={String(values[name] ?? "")} onChange={event => update(name, event.target.value)}>{spec.options.map(option => <option key={String(option)} value={String(option)}>{String(option)}</option>)}</select></label>;
    if (spec.secret || spec.sensitive) return <label key={name}><span>{label} <em>secret · not saved</em></span><input type="password" value={String(values[name] ?? "")} onChange={event => update(name, event.target.value)} /><small>{spec.description}</small></label>;
    if (/image|bitmap|raster/i.test(type)) return <label key={name} className="human-image-field"><span>{label} <em>{type}</em></span><input type="file" accept="image/*" onChange={event => { const file = event.target.files?.[0]; if (!file) return; const reader = new FileReader(); reader.onload = () => update(name, { dataUrl: String(reader.result), name: file.name, mimeType: file.type, size: file.size }); reader.readAsDataURL(file); }} />{visualArtifactPayload(values[name])?.image && <img src={visualArtifactPayload(values[name])!.image} alt={`${label} preview`} />}<small>{spec.description || "Choose an image; the preview and payload use the original file."}</small></label>;
    if (/grid|matrix/i.test(type)) { const visual = visualArtifactPayload(values[name]); return <label key={name} className="human-grid-field"><span>{label} <em>{type}</em></span><textarea value={typeof values[name] === "string" ? String(values[name]) : JSON.stringify(values[name] ?? [], null, 2)} onChange={event => { try { update(name, JSON.parse(event.target.value)); } catch { update(name, event.target.value); } }} />{visual?.grid && <div className="human-grid-preview" style={{ gridTemplateColumns: `repeat(${visual.grid[0]?.length || 1}, 1fr)` }}>{visual.grid.flatMap((row, rowIndex) => row.map((cell, columnIndex) => <i key={`${rowIndex}:${columnIndex}`} style={{ background: artifactColors[Math.abs(cell) % artifactColors.length] }} />))}</div>}<small>{spec.description || "Enter a rectangular JSON matrix of numeric color indexes."}</small></label>; }
    return <label key={name}><span>{label} <em>{type}</em></span><textarea value={typeof values[name] === "string" ? String(values[name]) : JSON.stringify(values[name] ?? "")} onChange={event => { const raw = event.target.value; let value: unknown = raw; if (/number|integer|float/i.test(type)) value = raw === "" ? null : Number(raw); else if (/object|map|list|array|any/i.test(type)) { try { value = JSON.parse(raw); } catch { value = raw; } } update(name, value); }} /><small>{spec.description}</small></label>;
  })}<button className="run-button" disabled={busy} onClick={() => onSubmit(values)}>Submit human input</button></div>;
}

function WorkflowInputsEditor({ workflowId, contract, source, onSource }: { workflowId: string; contract: Record<string, WorkflowInputContract>; source: string; onSource: (source: string) => void }) {
  const entries = Object.entries(contract);
  const label = (value: WorkflowInputContract) => typeof value === "string" ? value : String(value.datatype || value.type || "Any");
  const isText = (value: WorkflowInputContract) => /text|string|markdown|natural.?language/i.test(label(value));
  const parseSource = () => { try { const value = JSON.parse(source); return value && typeof value === "object" && !Array.isArray(value) ? value as Record<string, unknown> : {}; } catch { return {}; } };
  const rawValue = (value: unknown, spec: WorkflowInputContract) => value === undefined ? "" : isText(spec) && typeof value === "string" ? value : JSON.stringify(value, null, 2);
  const initialDrafts = () => { const values = parseSource(); return Object.fromEntries(entries.map(([name, spec]) => [name, rawValue(values[name] ?? (typeof spec === "object" ? spec.default : undefined), spec)])); };
  const [drafts, setDrafts] = useState<Record<string, string>>(initialDrafts);
  const [fieldError, setFieldError] = useState("");
  useEffect(() => { setDrafts(initialDrafts()); setFieldError(""); }, [workflowId]);
  const materialize = (next: Record<string, string>) => Object.fromEntries(entries.map(([name, spec]) => { const raw = next[name] || ""; const options = typeof spec === "object" ? spec.options : undefined; const selectedOption = options?.find(option => (typeof option === "string" ? option : JSON.stringify(option)) === raw); if (selectedOption !== undefined) return [name, selectedOption]; if (isText(spec)) return [name, raw]; if (/^any$/i.test(label(spec))) { try { return [name, JSON.parse(raw)]; } catch { return [name, raw]; } } if (!raw.trim()) return [name, null]; try { return [name, JSON.parse(raw)]; } catch { throw new Error(`${name} (${label(spec)}) must be valid JSON.`); } }));
  const update = (name: string, value: string) => { const next = { ...drafts, [name]: value }; setDrafts(next); try { onSource(JSON.stringify(materialize(next), null, 2)); setFieldError(""); } catch (reason) { setFieldError(reason instanceof Error ? reason.message : String(reason)); } };
  if (!entries.length) return null;
  return <div className="goal-workflow-inputs"><div className="llm-subhead"><div><span>WORKFLOW INPUT CONTRACT</span><b>{workflowId}</b><small>Datatype-aware fields update the advanced JSON source below.</small></div></div><div className="workflow-fields">{entries.map(([name, spec]) => { const type = label(spec), options = typeof spec === "object" ? spec.options : undefined; return <label key={name}><span>{name} <em>{type}</em></span>{options?.length ? <select value={drafts[name] || ""} onChange={event => update(name, event.target.value)}>{options.map(option => <option key={JSON.stringify(option)} value={typeof option === "string" ? option : JSON.stringify(option)}>{String(option)}</option>)}</select> : /boolean/i.test(type) ? <input type="checkbox" checked={drafts[name] === "true"} onChange={event => update(name, String(event.target.checked))} /> : /number|integer|float|double/i.test(type) ? <input type="number" value={drafts[name] || ""} onChange={event => update(name, event.target.value)} /> : <textarea value={drafts[name] || ""} placeholder={isText(spec) ? `Enter ${name}…` : `Enter ${type} as JSON…`} onChange={event => update(name, event.target.value)} />}</label>; })}</div>{fieldError && <div className="validation bad">{fieldError}</div>}</div>;
}

export function RuntimeHistoryView({ mode, workspaceId, goals = [], plans = [], contexts = [], workflows = [], onSelectRun, onOpenResource }:{
  mode: Mode; workspaceId: string; goals?: DocumentRecord[]; plans?: DocumentRecord[]; contexts?: DocumentRecord[]; workflows?: DocumentRecord[];
  onSelectRun?: (run: RuntimeRun) => void;
  onOpenResource?: OpenRuntimeResource;
}) {
  const [runs, setRuns] = useState<RuntimeRun[]>([]), [goalRuns, setGoalRuns] = useState<GoalRun[]>([]);
  const [invocations, setInvocations] = useState<InvocationTrace[]>([]), [selectedInvocationId, setSelectedInvocationId] = useState("");
  const [historyFilter, setHistoryFilter] = useState(""), [runLimit, setRunLimit] = useState(50), [goalRunLimit, setGoalRunLimit] = useState(50), [invocationLimit, setInvocationLimit] = useState(50);
  const [selectedId, setSelectedId] = useState<string>(""), [error, setError] = useState<string>(""), [busy, setBusy] = useState(false);
  const [frozenWorkflow, setFrozenWorkflow] = useState<FrozenWorkflow | null>(null);
  const goalDocs = useMemo(() => goals.map(row => row.document).filter(Boolean) as Record<string, any>[], [goals]);
  const planDocs = useMemo(() => plans.map(row => row.document).filter(Boolean) as Record<string, any>[], [plans]);
  const contextDocs = useMemo(() => contexts.map(row => row.document).filter(Boolean) as Record<string, any>[], [contexts]);
  const workflowIds = useMemo(() => new Set(workflows.map(row => row.document?.id).filter(Boolean)), [workflows]);
  const isRootResource = (doc: Record<string, any>) => !Array.isArray(doc.parents) || doc.parents.length === 0;
  const goalSpecs = goalDocs.filter(doc => doc.kind === "goal" && isRootResource(doc));
  const planSpecs = planDocs.filter(doc => (doc.kind === "planning_strategy" || doc.kind === "plan") && isRootResource(doc));
  const contextSpecs = contextDocs.filter(doc => (doc.kind === "atomspace" || doc.kind === "context") && isRootResource(doc));
  const [goalId, setGoalId] = useState(""), [goalVariantId, setGoalVariantId] = useState("");
  const [planId, setPlanId] = useState(""), [planVariantId, setPlanVariantId] = useState("");
  const [contextId, setContextId] = useState(""), [contextVariantId, setContextVariantId] = useState("");
  const availablePlanSpecs = planSpecs.filter(plan => (!goalId || (plan.goals || []).includes(goalId)) && (plan.children || []).some((childId: string) => workflowIds.has(planDocs.find(doc => doc.id === childId)?.workflow)));
  const [inputs, setInputs] = useState("{}");
  const [humanDraft, setHumanDraft] = useState<Record<string, unknown>>({}), [draftLoaded, setDraftLoaded] = useState(false), [draftStatus, setDraftStatus] = useState("");
  const goalVariants = goalDocs.filter(doc => (doc.parents || []).includes(goalId));
  const planVariants = planDocs.filter(doc => (doc.parents || []).includes(planId) && workflowIds.has(doc.workflow));
  const contextVariants = contextDocs.filter(doc => (doc.parents || []).includes(contextId));
  const selectedPlanVariant = planVariants.find(doc => doc.id === planVariantId);
  const selectedGoalWorkflow = workflows.map(row => row.document).find(doc => doc?.id === selectedPlanVariant?.workflow) as Record<string, any> | undefined;

  const refresh = async () => {
    setError("");
    try {
      const includeInvocations = mode === "execs" || mode === "logs";
      const includeGoalRuns = mode === "goalRuns" || mode === "runtimeContexts";
      const includeWorkflowRuns = !includeGoalRuns;
      const [runPayload, goalPayload, operationPayload, modelPayload] = await Promise.all([
        includeWorkflowRuns ? api(`/api/engine/runs?workspace_id=${encodeURIComponent(workspaceId)}&limit=${runLimit}`) : Promise.resolve({ runs: [] }),
        includeGoalRuns ? api(`/api/goal-runs?workspace_id=${encodeURIComponent(workspaceId)}&limit=${goalRunLimit}`) : Promise.resolve({ goalRuns: [] }),
        includeInvocations ? api(`/api/workspaces/${encodeURIComponent(workspaceId)}/operations/invocations?limit=${invocationLimit}`) : Promise.resolve({ invocations: [] }),
        includeInvocations ? api(`/api/workspaces/${encodeURIComponent(workspaceId)}/models/invocations?limit=${invocationLimit}`) : Promise.resolve({ invocations: [] }),
      ]);
      const normalizeRun = (run: RuntimeRun): RuntimeRun => ({ ...run, steps: run.steps || [], events: run.events || [], artifacts: run.artifacts || [], logs: run.logs || [] });
      const loadedRuns = (runPayload.runs || []).map(normalizeRun);
      const requestedRunId = mode === "workflowRuns" ? new URLSearchParams(window.location.search).get("run") : null;
      if (requestedRunId && !loadedRuns.some((run: RuntimeRun) => run.id === requestedRunId)) {
        const requestedPayload = await api(`/api/engine/runs/${encodeURIComponent(requestedRunId)}`);
        if (requestedPayload.run) loadedRuns.unshift(normalizeRun(requestedPayload.run as RuntimeRun));
      }
      setRuns(loadedRuns);
      if (requestedRunId) setSelectedId(requestedRunId);
      const normalizeGoalRun = (goalRun: GoalRun): GoalRun => ({ ...goalRun, workflowRun: normalizeRun(goalRun.workflowRun) });
      const loadedGoalRuns = (goalPayload.goalRuns || []).map(normalizeGoalRun);
      const requestedGoalRunId = mode === "goalRuns" ? new URLSearchParams(window.location.search).get("goalRun") : null;
      if (requestedGoalRunId && !loadedGoalRuns.some((goalRun: GoalRun) => goalRun.id === requestedGoalRunId)) {
        const requestedPayload = await api(`/api/goal-runs/${encodeURIComponent(requestedGoalRunId)}`);
        if (requestedPayload.goalRun) loadedGoalRuns.unshift(normalizeGoalRun(requestedPayload.goalRun as GoalRun));
      }
      setGoalRuns(loadedGoalRuns);
      if (requestedGoalRunId) setSelectedId(requestedGoalRunId);
      setInvocations([...(operationPayload.invocations || []), ...(modelPayload.invocations || [])].sort((a: InvocationTrace, b: InvocationTrace) => String(b.createdAt || "").localeCompare(String(a.createdAt || ""))));
    } catch (reason) { setError(String(reason)); }
  };
  useEffect(() => { setRunLimit(50); setGoalRunLimit(50); setInvocationLimit(50); setHistoryFilter(""); }, [workspaceId, mode]);
  useEffect(() => { void refresh(); }, [workspaceId, mode, runLimit, goalRunLimit, invocationLimit]);
  useEffect(() => {
    if (!goalId && goalSpecs[0]) setGoalId(String(goalSpecs[0].id));
    if ((!planId || !availablePlanSpecs.some(doc => doc.id === planId)) && availablePlanSpecs[0]) setPlanId(String(availablePlanSpecs[0].id));
    if (!availablePlanSpecs.length) setPlanId("");
  }, [goalId, goalDocs.length, planDocs.length, workflows.length]);
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
      onSelectRun?.(payload.goalRun.workflowRun); await refresh(); selectGoalRun(payload.goalRun);
    } catch (reason) { setError(String(reason)); } finally { setBusy(false); }
  };
  const persistRuntimeSelection = (parameter: "run" | "goalRun", id: string) => { const url = new URL(window.location.href); url.searchParams.set(parameter, id); url.searchParams.delete(parameter === "run" ? "goalRun" : "run"); window.history.replaceState(null, "", `${url.pathname}${url.search}${url.hash}`); };
  const chooseRun = (run: RuntimeRun) => { setSelectedId(run.id); if (mode === "workflowRuns") persistRuntimeSelection("run", run.id); onSelectRun?.(run); };
  const selectGoalRun = (goalRun: GoalRun) => { setSelectedId(goalRun.id); persistRuntimeSelection("goalRun", goalRun.id); onSelectRun?.(goalRun.workflowRun); };
  const selectedRun = runs.find(row => row.id === selectedId) || runs[0];
  const selectedInvocation = invocations.find(row => row.id === selectedInvocationId);
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
  useEffect(() => {
    if (!selectedGoalRun || !waitingStep) { setHumanDraft({}); setDraftLoaded(false); return; }
    setDraftLoaded(false); setDraftStatus("Loading saved draft…");
    void api(`/api/engine/runs/${encodeURIComponent(selectedGoalRun.workflowRunId)}/steps/${encodeURIComponent(waitingStep.stepId)}/draft`).then(payload => { setHumanDraft(payload.draft?.values || {}); setDraftLoaded(true); setDraftStatus(payload.draft?.updatedAt ? `Draft restored · ${stamp(payload.draft.updatedAt)}` : "Draft autosave ready"); }).catch(reason => { setDraftLoaded(true); setDraftStatus(`Draft unavailable · ${String(reason)}`); });
  }, [selectedGoalRun?.id, waitingStep?.stepId]);
  useEffect(() => {
    if (!draftLoaded || !selectedGoalRun || !waitingStep) return;
    setDraftStatus("Saving draft…");
    const timer = window.setTimeout(() => { void api(`/api/engine/runs/${encodeURIComponent(selectedGoalRun.workflowRunId)}/steps/${encodeURIComponent(waitingStep.stepId)}/draft`, { method: "PUT", body: JSON.stringify(humanDraft) }).then(payload => setDraftStatus(`Draft saved · ${stamp(payload.draft?.updatedAt)}`)).catch(reason => setDraftStatus(`Draft save failed · ${String(reason)}`)); }, 500);
    return () => window.clearTimeout(timer);
  }, [humanDraft, draftLoaded, selectedGoalRun?.id, waitingStep?.stepId]);
  const submitHumanInput = async (values: Record<string, unknown>) => {
    if (!selectedGoalRun || !waitingStep) return;
    setBusy(true); setError("");
    try {
      const payload = await api(`/api/engine/runs/${encodeURIComponent(selectedGoalRun.workflowRunId)}/steps/${encodeURIComponent(waitingStep.stepId)}/input`, { method: "POST", body: JSON.stringify(values) });
      onSelectRun?.(payload.run); await refresh();
    } catch (reason) { setError(String(reason)); } finally { setBusy(false); }
  };
  const commandGoalRun = async (command: Exclude<WorkflowRunCommand, "replay">) => {
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
      <label><span>CONTEXT</span><select value={contextId} onChange={event => setContextId(event.target.value)}><option value="">none</option>{contextSpecs.map(doc => <option key={doc.id} value={doc.id}>{doc.label || doc.id}</option>)}</select></label>
      <label><span>CONTEXT VARIANT</span><select value={contextVariantId} disabled={!contextId} onChange={event => setContextVariantId(event.target.value)}><option value="">none</option>{contextVariants.map(doc => <option key={doc.id} value={doc.id}>{doc.label || doc.id}</option>)}</select></label>
      {selectedGoalWorkflow && <WorkflowInputsEditor key={selectedGoalWorkflow.id} workflowId={String(selectedGoalWorkflow.id)} contract={(selectedGoalWorkflow.inputs || {}) as Record<string, WorkflowInputContract>} source={inputs} onSource={setInputs} />}
      <label><span>ADVANCED WORKFLOW INPUTS (JSON)</span><textarea value={inputs} onChange={event => setInputs(event.target.value)} /></label>
    </div>
    <button className="run-button" disabled={busy || !goalId || !planId} onClick={startGoalRun}>▶ Pursue goal</button>
    <div className="resource-table"><div className="resource-row resource-head"><span>Goal</span><span>Strategy variant</span><span>Status</span><span>Workflow/plan run</span><span>Created</span></div>{goalRuns.map(row => <button className="resource-row" key={row.id} onClick={() => selectGoalRun(row)}><b>{row.goalVariantId || row.goalId}</b><code>{row.planVariantId}</code><span>{row.status}</span><span>{row.workflowRunId.slice(0, 8)}</span><em>{stamp(row.createdAt)}</em></button>)}</div>
    {goalRuns.length >= goalRunLimit && <button type="button" className="runtime-load-older" onClick={() => setGoalRunLimit(limit => Math.min(500, limit + 50))}>Load 50 older goal runs</button>}
    {selectedGoalRun && <div className="goal-run-controls"><div><b>Selected pursuit</b><span>{selectedGoalRun.goalVariantId} · {selectedGoalRun.planVariantId} · {selectedGoalRun.contextVariantId || "no context"}</span></div></div>}
    {waitingStep && <div className="human-pause goal-run-human"><div className="pause-ring">Ⅱ</div><b>Waiting for {waitingStep.stepId}</b><span>{waitingStepDefinition?.label || "Provide the values required by this workflow step."}</span><small className="human-draft-status">{draftStatus}</small><HumanInputForm step={waitingStepDefinition} busy={busy} draft={humanDraft} onDraft={setHumanDraft} onSubmit={values => void submitHumanInput(values)} /></div>}
    {selectedGoalRun && <WorkflowRunProjection run={selectedGoalRun.workflowRun} workflow={goalRunWorkflow} busy={busy} commands={["pause", "resume", "advance", "cancel"]} onCommand={command => void commandGoalRun(command as Exclude<WorkflowRunCommand, "replay">)} onOpenResource={onOpenResource} />}
  </section>;

  const invocationRows = invocations.map(trace => {
    const errorDetail = typeof trace.error === "string" ? trace.error : trace.error && typeof trace.error === "object" ? String((trace.error as { message?: unknown }).message || jsonValueToMetta(trace.error)) : "";
    return { key: `invocation:${trace.id}`, a: trace.modelId || trace.operationId || trace.operation?.id || trace.id, b: trace.status, c: trace.kind === "model_invocation_trace" ? "model" : "operation", d: trace.id.slice(-8), e: errorDetail || trace.response?.text || trace.implementation?.label || "durable invocation trace", trace };
  });
  const rows = mode === "workflowRuns" ? runs.map(run => ({ key: run.id, a: run.workflowId, b: run.status, c: `${run.steps.length} steps`, d: run.id.slice(0, 8), e: stamp(run.createdAt), run }))
    : mode === "execs" ? [...invocationRows, ...runs.flatMap(run => run.steps.map(step => ({ key: `${run.id}:${step.stepId}`, a: step.stepId, b: step.status, c: `attempt ${step.attempt || 0}`, d: run.id.slice(0, 8), e: step.error || "—", run })))]
    : mode === "events" ? runs.flatMap(run => run.events.map(event => ({ key: `${run.id}:${event.id}`, a: event.kind, b: event.stepId || "workflow", c: stamp(event.createdAt), d: run.id.slice(0, 8), e: jsonValueToMetta(event.payload || {}), run })))
    : mode === "states" ? runs.flatMap(run => run.artifacts.map(item => ({ key: item.id, a: item.name, b: item.datatype || "Any", c: item.stepId || "input", d: run.id.slice(0, 8), e: jsonValueToMetta(item.payload), run })))
    : mode === "runtimeContexts" ? goalRuns.filter(item => item.contextId).map(item => ({ key: `context:${item.id}`, a: item.contextVariantId || item.contextId || "context", b: item.status, c: stamp(item.createdAt), d: item.workflowRunId.slice(0, 8), e: item.contextId || "—", run: item.workflowRun }))
    : [...invocationRows, ...runs.flatMap(run => run.logs.map(log => ({ key: `${run.id}:${log.id}`, a: log.stream, b: log.stepId || "workflow", c: stamp(log.createdAt), d: run.id.slice(0, 8), e: log.message, run })))];
  const normalizedFilter = historyFilter.trim().toLowerCase();
  const visibleRows = normalizedFilter ? rows.filter(row => [row.a, row.b, row.c, row.d, row.e].some(value => String(value).toLowerCase().includes(normalizedFilter))) : rows;
  const canLoadMoreInvocations = (mode === "execs" || mode === "logs") && invocations.length >= invocationLimit;
  const canLoadMoreRuns = runs.length >= runLimit;
  return <section className="resource-view runtime-history-view">
    <div className="resource-heading"><div><span>PERSISTENT RUNTIME HISTORY</span><h1>{title}</h1><p>{mode === "execs" || mode === "logs" ? "Workflow-engine records and standalone resource invocation traces are loaded from their durable workspace stores." : "Records are loaded from the durable workflow-engine database across application sessions."}</p></div><button onClick={refresh}>Refresh</button></div>
    {error && <div className="backend-error"><b>Error</b><span>{error}</span></div>}
    <div className="runtime-history-tools"><label><span>FILTER RECORDS</span><input value={historyFilter} onChange={event => setHistoryFilter(event.target.value)} placeholder="ID, status, type, run, or detail…" /></label><small>{visibleRows.length} of {rows.length} loaded records</small>{canLoadMoreRuns && <button type="button" onClick={() => setRunLimit(limit => Math.min(500, limit + 50))}>Load 50 older runs</button>}{canLoadMoreInvocations && <button type="button" onClick={() => setInvocationLimit(limit => Math.min(1000, limit + 100))}>Load 100 older invocations</button>}</div>
    <div className="resource-table"><div className="resource-row resource-head"><span>Record</span><span>Status / type</span><span>Step / time</span><span>Run</span><span>Detail</span></div>{visibleRows.map(row => <button className="resource-row" key={row.key} onClick={() => { if ("trace" in row) { setSelectedInvocationId(row.trace.id); setSelectedId(""); } else { setSelectedInvocationId(""); chooseRun(row.run); } }}><b>{row.a}</b><code>{row.b}</code><span>{row.c}</span><span>{row.d}</span><em title={row.e}>{row.e}</em></button>)}{!visibleRows.length && <div className="studio-empty">{rows.length ? "No loaded records match this filter." : `No persisted ${title.toLowerCase()} yet.`}</div>}</div>
    {selectedInvocation && <section className="run-projection-inspector" aria-label="Selected standalone invocation"><div><span>STANDALONE {selectedInvocation.kind === "model_invocation_trace" ? "MODEL" : "OPERATION"} EXECUTION</span><h3>{selectedInvocation.modelId || selectedInvocation.operationId || selectedInvocation.operation?.label || selectedInvocation.operation?.id}</h3><p>{stamp(selectedInvocation.createdAt)} · {selectedInvocation.status}</p>{onOpenResource && selectedInvocation.modelId && <button type="button" className="runtime-resource-link" onClick={() => onOpenResource("model", selectedInvocation.modelId!)}>Open Model · {selectedInvocation.modelId}</button>}{onOpenResource && (selectedInvocation.operationId || selectedInvocation.operation?.id) && <button type="button" className="runtime-resource-link" onClick={() => onOpenResource("operation", String(selectedInvocation.operationId || selectedInvocation.operation?.id))}>Open Operation · {selectedInvocation.operationId || selectedInvocation.operation?.id}</button>}</div><dl><div><dt>Trace</dt><dd>{selectedInvocation.id}</dd></div><div><dt>Backend</dt><dd>{selectedInvocation.response?.backendId || selectedInvocation.implementation?.implementation || "resolved runtime"}</dd></div><div><dt>Latency</dt><dd>{selectedInvocation.response?.latencyMs != null ? `${selectedInvocation.response.latencyMs} ms` : "—"}</dd></div><div><dt>Log</dt><dd>{selectedInvocation.logPath}</dd></div></dl><details open><summary>Complete durable trace</summary><pre>{jsonValueToMetta(selectedInvocation)}</pre></details></section>}
    {mode === "workflowRuns" && selectedRun && <WorkflowRunProjection run={selectedRun} workflow={frozenWorkflow} busy={busy} onCommand={command => void commandWorkflowRun(command)} onOpenResource={onOpenResource} />}
    {mode === "workflowRuns" && <Suspense fallback={<div className="studio-empty">Loading workflow runner reference…</div>}><WorkflowRunnerTodoReference /></Suspense>}
    {mode !== "workflowRuns" && selectedRun && <div className="demo-notice"><b>SELECTED RUN {selectedRun.id.slice(0, 8)}</b><span>{selectedRun.workflowId} · {selectedRun.status} · {selectedRun.events.length} events · {selectedRun.artifacts.length} states</span></div>}
  </section>;
}
