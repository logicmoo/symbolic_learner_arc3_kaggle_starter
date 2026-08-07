"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";

type Stage = {
  id: number;
  short: string;
  title: string;
  description: string;
  status: "done" | "active" | "waiting";
  accent: string;
};

type View = "canvas" | "editor" | "artifacts" | "evidence" | "operations" | "llms" | "checks" | "setup";

type RunEvent = {
  id: number;
  kind: string;
  stage: number;
  createdAt: string;
  message: string;
  tone: "ok" | "info" | "wait";
  payload: Record<string, unknown>;
};

type RunArtifact = {
  id: number;
  name: string;
  type: string;
  producer: string;
  value: string;
  confidence: number;
  version: number;
  payload: Record<string, unknown>;
  createdAt: string;
};

type WorkbenchOperationEvent = {
  id: number;
  step: number;
  kind: string;
  message: string;
  payload: Record<string, unknown>;
  createdAt: string;
};

type WorkbenchOperation = {
  id: string;
  parentOperationId: string | null;
  kind: "workflow_design" | "workflow_execution";
  workflowId: string;
  status: "running" | "waiting" | "paused" | "completed" | "failed";
  currentStep: number;
  totalSteps: number;
  summary: string;
  events: WorkbenchOperationEvent[];
};

type RunSnapshot = {
  id: string;
  workflowId: string;
  worldId: string;
  episode: number;
  status: "running" | "paused" | "waiting" | "concluded";
  stage: number;
  maxStage: number;
  chosenAction: string | null;
  modelVersion: number;
  artifacts: RunArtifact[];
  events: RunEvent[];
  cursor: number;
  operation: WorkbenchOperation;
};

type WorkflowStep = {
  id: string;
  kind: "operation" | "subworkflow" | "transaction";
  operation: string;
  implementation: string;
  inputs: Record<string, string>;
  outputs: Record<string, string>;
  parameters: Record<string, unknown>;
  profile?: string;
  model?: string;
  analysisLevel?: number;
  continueOnError?: boolean;
};

type WorkflowDocument = {
  id: string;
  label: string;
  description: string;
  steps: WorkflowStep[];
};

type Catalog = {
  workflows: WorkflowDocument[];
  operations: { id: string; ports: string; routes: string }[];
  datatypes: { id: string; kind: string; meaning: string; relations: string }[];
};

const stages: Stage[] = [
  { id: 1, short: "WORLD", title: "Select world", description: "Bind a scenario, environment adapter, and success interface.", status: "done", accent: "cyan" },
  { id: 2, short: "OBSERVE", title: "Capture initial state", description: "Start the episode and preserve the first raw observation.", status: "done", accent: "cyan" },
  { id: 3, short: "OBJECTIFY", title: "Objectify observation", description: "Extract stable entities, facts, programs, and reconstruction evidence.", status: "active", accent: "violet" },
  { id: 4, short: "ACT", title: "Observe action", description: "Pause while a person chooses an intervention in the world.", status: "waiting", accent: "amber" },
  { id: 5, short: "RE-OBSERVE", title: "Capture result", description: "Acquire and objectify the world after the intervention.", status: "waiting", accent: "cyan" },
  { id: 6, short: "LEARN", title: "Explain transition", description: "Compare before, action, and after; update the world model.", status: "waiting", accent: "green" },
  { id: 7, short: "DECIDE", title: "Repeat or conclude", description: "Choose the next uncertainty or finish when the goal is understood.", status: "waiting", accent: "pink" },
];

const substeps = [
  ["01", "Extract entities", "vision.segment", "8 candidates"],
  ["02", "Assign identities", "symbolic.identity", "8 stable IDs"],
  ["03", "Derive properties", "prolog.properties", "41 facts"],
  ["04", "Generate Turtle", "llm.turtle", "8 programs"],
  ["05", "Render programs", "turtle.runtime", "8 renders"],
  ["06", "Compare source", "vision.diff", "96.4% match"],
  ["07", "Record evidence", "evidence.commit", "v3 saved"],
];

const artifactFallbackRows = [
  { name: "source_observation", type: "VisualObservation", producer: "arc3.capture", value: "64×64 · rgba", confidence: "1.00", version: 1, color: "cyan" },
  { name: "entity_set", type: "EntitySet", producer: "vision.segment", value: "8 entities", confidence: "0.94", version: 1, color: "violet" },
  { name: "object_identities", type: "IdentityMap", producer: "symbolic.identity", value: "8 mappings", confidence: "0.91", version: 1, color: "violet" },
  { name: "symbolic_facts", type: "PrologFactSet", producer: "prolog.properties", value: "41 clauses", confidence: "0.89", version: 1, color: "green" },
  { name: "turtle_programs", type: "ExecutableView", producer: "llm.turtle", value: "8 programs", confidence: "0.87", version: 1, color: "amber" },
  { name: "reconstruction", type: "VisualObservation", producer: "turtle.runtime", value: "64×64 · rgba", confidence: "0.96", version: 1, color: "cyan" },
  { name: "evidence", type: "EvidenceBundle", producer: "vision.diff", value: "3 findings", confidence: "0.96", version: 1, color: "pink" },
];

const gridCells = [
  [1,1,1,1,1,1,1,1,1,1,1,1],
  [1,0,0,0,0,0,0,0,0,0,0,1],
  [1,0,3,3,3,0,0,7,7,0,0,1],
  [1,0,3,0,3,0,0,7,7,0,0,1],
  [1,0,3,3,3,0,0,0,0,0,0,1],
  [1,0,0,0,0,0,5,5,5,5,0,1],
  [1,0,0,8,0,0,5,0,0,5,0,1],
  [1,0,0,8,0,0,5,5,5,5,0,1],
  [1,0,0,8,0,0,0,0,0,0,0,1],
  [1,0,0,8,8,8,0,9,9,9,0,1],
  [1,0,0,0,0,0,0,0,0,9,0,1],
  [1,1,1,1,1,1,1,1,1,1,1,1],
];

const colors: Record<number, string> = { 0: "#101923", 1: "#334352", 3: "#f25588", 5: "#28d7c0", 7: "#f6c453", 8: "#8a72f8", 9: "#54a8ff" };

const operationCatalog = [
  { operation: "capture_observation", implementation: "arc3.capture", runtime: "Python", ports: "world → observation", state: "ready" },
  { operation: "extract_entities", implementation: "vision.segment", runtime: "Python", ports: "observation → entity_set", state: "ready" },
  { operation: "assign_identities", implementation: "symbolic.identity", runtime: "Prolog", ports: "entity_set → identity_map", state: "ready" },
  { operation: "derive_properties", implementation: "prolog.properties", runtime: "SWI-Prolog", ports: "identities → fact_set", state: "ready" },
  { operation: "generate_turtle", implementation: "llm.turtle", runtime: "LLM", ports: "entities + facts → programs", state: "ready" },
  { operation: "compare_reconstruction", implementation: "vision.diff", runtime: "Python", ports: "source + render → evidence", state: "ready" },
];

const validationChecks = [
  ["Typed port compatibility", "42 connections checked", "pass"],
  ["Nested workflow cycles", "No recursive cycle detected", "pass"],
  ["Required implementations", "18 of 18 resources available", "pass"],
  ["Human input boundary", "Pause and resume contract valid", "pass"],
  ["World adapter", "ls20 observation/action bridge bound", "pass"],
];

function Tooltip({ text, children }: { text: string; children: React.ReactNode }) {
  return <span className="tip" tabIndex={0}>{children}<span className="tip-copy">{text}</span></span>;
}

function ArcGrid({ reconstruction = false }: { reconstruction?: boolean }) {
  return (
    <div className={`arc-grid ${reconstruction ? "reconstruction" : ""}`} aria-label={reconstruction ? "Turtle reconstruction" : "ARC3 source observation"}>
      {gridCells.flatMap((row, y) => row.map((cell, x) => (
        <span key={`${x}-${y}`} style={{ background: colors[cell], opacity: reconstruction && x === 9 && y === 10 ? .4 : 1 }} />
      )))}
    </div>
  );
}

function StageInspector({ stage, chosenAction, onAction, onRepeat, onConclude }: { stage: Stage; chosenAction: string | null; onAction: (action: string) => void; onRepeat: () => void; onConclude: () => void }) {
  if (stage.id === 1) return <div className="stage-story"><div className="world-card active-world"><span className="world-glyph">LS</span><div><strong>ls20</strong><small>ARC3 visual world · local adapter</small></div><span className="status-pill ok">bound</span></div><div className="world-card"><span className="world-glyph muted">+</span><div><strong>Choose another world</strong><small>Register any compatible observation/action adapter</small></div></div><div className="detail-note"><b>Boundary contract</b><span>External states become typed observations. The workbench core never depends on game-specific classes.</span></div></div>;
  if (stage.id === 2) return <div className="stage-story"><div className="two-visual"><div><label>Raw frame</label><ArcGrid /></div><div className="capture-meta"><b>Observation #000</b><span>episode ls20/L1</span><span>step 0 · 04:17:08.233</span><span>SHA 91d4…a8c2</span><span className="status-pill ok">immutable source</span></div></div><div className="detail-note"><b>Why preserve raw input?</b><span>Every later fact, program, and prediction can be traced back to the exact pixels the system received.</span></div></div>;
  if (stage.id === 4) return <div className="stage-story"><div className="human-pause"><div className="pause-ring">Ⅱ</div><b>{chosenAction ? `${chosenAction} captured` : "Waiting for a human action"}</b><span>{chosenAction ? "The action is recorded with the episode and the resulting observation is ready to capture." : "Use the controls below or press an arrow key. The action and resulting state will be captured automatically."}</span><div className="action-pad" aria-label="Human action controls"><button onClick={() => onAction("UP")} aria-label="Move up">↑</button><button onClick={() => onAction("LEFT")} aria-label="Move left">←</button><button onClick={() => onAction("DOWN")} aria-label="Move down">↓</button><button onClick={() => onAction("RIGHT")} aria-label="Move right">→</button><button className="space-action" onClick={() => onAction("SPACE")}>SPACE</button></div></div></div>;
  if (stage.id === 5) return <div className="stage-story"><div className="compare-strip"><div><label>Before · step 0</label><ArcGrid /></div><div className="action-chip">action<br/><b>{chosenAction ?? "—"}</b></div><div><label>After · step 1</label><ArcGrid reconstruction /></div></div><div className="detail-note"><b>Automatic handoff</b><span>The same Objectify Observation subworkflow runs again, producing a comparable versioned artifact set.</span></div></div>;
  if (stage.id === 6) return <div className="stage-story"><div className="hypothesis-card"><span className="rank">H1</span><div><b>Blue hook translates toward the yellow marker</b><small>Supported by position delta (+1, 0) after RIGHT</small></div><strong>0.72</strong></div><div className="hypothesis-card"><span className="rank">H2</span><div><b>Action moves the selected object</b><small>Identity preserved; no color or topology change</small></div><strong>0.64</strong></div><div className="detail-note"><b>Next useful experiment</b><span>Try UP. It maximally separates free translation from goal-directed motion.</span></div></div>;
  if (stage.id === 7) return <div className="stage-story"><div className="decision-card"><span className="decision-icon">↻</span><div><b>Continue observing</b><small>3 unresolved transition hypotheses</small></div><button onClick={onRepeat}>Repeat from action</button></div><div className="decision-card"><span className="decision-icon">✓</span><div><b>Conclude this demonstration</b><small>Freeze the current learned model and evidence bundle</small></div><button onClick={onConclude}>Conclude model</button></div></div>;

  return (
    <div className="subworkflow">
      <div className="subworkflow-head"><span>SUBWORKFLOW</span><b>objectify_observation</b><small>7 operations · typed ports · isolated slots</small></div>
      {substeps.map((s, i) => <Tooltip key={s[0]} text={`${s[2]} reads its declared input silo and appends a new versioned result. Clickable in the implementation workbench.`}><div className={`substep ${i < 5 ? "complete" : i === 5 ? "running" : "queued"}`}><span className="sub-index">{s[0]}</span><span className="sub-dot"/><div><b>{s[1]}</b><small>{s[2]}</small></div><em>{s[3]}</em></div></Tooltip>)}
    </div>
  );
}

function OperationSpline({ operations }: { operations: WorkbenchOperation[] }) {
  const [selected, setSelected] = useState<{ operation: WorkbenchOperation; event: WorkbenchOperationEvent; previous?: WorkbenchOperationEvent } | null>(null);
  const [mode, setMode] = useState<"topology" | "chronology">("topology");
  if (!operations.length) return null;
  return <section className="operation-spline-panel" aria-label="Workbench operation progress">
    <div className="spline-heading"><div><span>WORKBENCH OPERATION SPLINE</span><b>{mode === "topology" ? "Semantic steps · arcs show circle-backs" : "Ordered events · left-to-right audit trail"}</b></div><div className="spline-mode" role="group" aria-label="Spline layout"><button className={mode === "topology" ? "active" : ""} onClick={() => setMode("topology")}>Topology</button><button className={mode === "chronology" ? "active" : ""} onClick={() => setMode("chronology")}>Chronology</button></div><small>{operations.length > 1 ? "design → execution handoff" : operations[0].kind.replace("_", " ")}</small></div>
    {operations.map((operation, operationIndex) => {
      const points = operation.events.length ? operation.events : [{ id: 0, step: 0, kind: "operation.pending", message: operation.summary, payload: {}, createdAt: "" }];
      const positions = points.map((event, index) => ({
        x: mode === "topology"
          ? 20 + Math.max(0, Math.min(operation.totalSteps, event.step)) / operation.totalSteps * 960 + ((index % 3) - 1) * 4
          : 20 + (points.length === 1 ? .5 : index / (points.length - 1)) * 960,
        y: 46 + Math.sin(index * 1.37) * 20,
      }));
      return <div className="spline-row" key={operation.id}>
        <div className="spline-label"><span>{operationIndex + 1}</span><div><b>{operation.kind === "workflow_design" ? "Design workflow" : "Run workflow"}</b><small>{operation.currentStep} / {operation.totalSteps} · {operation.status}</small></div></div>
        <div className="spline-track">
          <svg viewBox="0 0 1000 94" preserveAspectRatio="none">
            <path className="spline-base" d="M20 48 C210 18 330 74 500 46 S790 20 980 48"/>
            <path className={`spline-progress ${operation.status}`} style={{ strokeDasharray: `${Math.max(4, operation.currentStep / operation.totalSteps * 100)} 100` }} pathLength="100" d="M20 48 C210 18 330 74 500 46 S790 20 980 48"/>
            {positions.slice(1).map((position, index) => {
              const previousPosition = positions[index];
              const from = points[index];
              const to = points[index + 1];
              const loopsBack = mode === "topology" && to.step < from.step;
              const d = loopsBack
                ? `M${previousPosition.x} ${previousPosition.y} C${previousPosition.x + 75} 92 ${position.x - 75} 92 ${position.x} ${position.y}`
                : `M${previousPosition.x} ${previousPosition.y} C${(previousPosition.x + position.x) / 2} ${previousPosition.y - 15} ${(previousPosition.x + position.x) / 2} ${position.y + 15} ${position.x} ${position.y}`;
              return <path key={`${from.id}-${to.id}`} className={loopsBack ? "spline-loopback" : "spline-history"} d={d}><title>{loopsBack ? `Circle back: step ${from.step} → ${to.step}` : `${from.kind} → ${to.kind}`}</title></path>;
            })}
          </svg>
          {points.map((event, index) => {
            const left = positions[index].x / 10;
            const top = positions[index].y / .94;
            const last = index === points.length - 1;
            const state = !last || operation.status === "completed" ? "done" : operation.status;
            const previous = index ? points[index - 1] : undefined;
            const loopsBack = Boolean(mode === "topology" && previous && event.step < previous.step);
            const tip = `${loopsBack ? `↩ circle back from step ${previous?.step}: ` : ""}${event.kind} — ${event.message}`;
            return <button key={event.id} className={`spline-node tip ${state} ${loopsBack ? "loop-target" : ""} ${selected?.event.id === event.id ? "selected" : ""}`} style={{ left: `${left}%`, top: `${top}%` }} onClick={() => setSelected({ operation, event, previous })} aria-label={`Inspect ${event.kind}`}><i/><span className="node-step">{loopsBack ? "↩" : event.step}</span><span className="tip-copy">{tip}</span></button>;
          })}
        </div>
      </div>;
    })}
    {selected && <div className="spline-inspection"><div><span>PINNED OPERATION EVENT</span><b>{selected.event.kind}</b></div><p>{selected.event.message}</p><dl><div><dt>View</dt><dd>{mode}</dd></div><div><dt>Operation</dt><dd>{selected.operation.kind.replace("_", " ")}</dd></div><div><dt>Step</dt><dd>{selected.previous && selected.event.step < selected.previous.step ? `${selected.previous.step} ↩ ${selected.event.step} circle-back` : selected.event.step}</dd></div><div><dt>Time</dt><dd>{selected.event.createdAt || "pending"}</dd></div><div><dt>Payload</dt><dd>{Object.keys(selected.event.payload).length ? JSON.stringify(selected.event.payload) : "—"}</dd></div></dl><button onClick={() => setSelected(null)}>×</button></div>}
  </section>;
}

function WorkflowStudio({
  catalog,
  draft,
  selectedWorkflowId,
  selectedStep,
  rawMode,
  rawText,
  tab,
  onTab,
  onSelectWorkflow,
  onDraft,
  onSelectStep,
  onUpdateStep,
  onMoveStep,
  onDeleteStep,
  onAddStep,
  onOperation,
  onSave,
  onRawMode,
  onRawText,
}: {
  catalog: Catalog | null;
  draft: WorkflowDocument | null;
  selectedWorkflowId: string | null;
  selectedStep: number | null;
  rawMode: boolean;
  rawText: string;
  tab: "workflows" | "operations" | "datatypes";
  onTab: (tab: "workflows" | "operations" | "datatypes") => void;
  onSelectWorkflow: (workflow: WorkflowDocument) => void;
  onDraft: (workflow: WorkflowDocument) => void;
  onSelectStep: (index: number | null) => void;
  onUpdateStep: (index: number, patch: Partial<WorkflowStep>) => void;
  onMoveStep: (index: number, delta: number) => void;
  onDeleteStep: (index: number) => void;
  onAddStep: (kind: "operation" | "subworkflow") => void;
  onOperation: (operation: "new" | "example" | "delete") => void;
  onSave: (runAfter?: boolean) => void;
  onRawMode: (raw: boolean) => void;
  onRawText: (raw: string) => void;
}) {
  const step = selectedStep === null ? null : draft?.steps[selectedStep] ?? null;
  const jsonOnBlur = (index: number, key: "inputs" | "outputs" | "parameters") => (event: React.FocusEvent<HTMLTextAreaElement>) => {
    try {
      const parsed = JSON.parse(event.currentTarget.value) as Record<string, never>;
      event.currentTarget.setCustomValidity("");
      onUpdateStep(index, { [key]: parsed });
    } catch {
      event.currentTarget.setCustomValidity("Enter a valid JSON object");
      event.currentTarget.reportValidity();
    }
  };

  return <div className="studio-view">
    <div className="studio-topline">
      <div><span>WORKFLOW DESKTOP</span><h1>Compose typed workflows</h1><p>Feature-equivalent to the Python Tk editor, backed by shared persistent workflow documents.</p></div>
      <div className="studio-tabs">
        <button className={tab === "workflows" ? "active" : ""} onClick={() => onTab("workflows")}>Workflows</button>
        <button className={tab === "operations" ? "active" : ""} onClick={() => onTab("operations")}>Operations / implementations</button>
        <button className={tab === "datatypes" ? "active" : ""} onClick={() => onTab("datatypes")}>Datatype manifest</button>
      </div>
    </div>

    {tab === "workflows" && <div className="studio-workflows">
      <aside className="workflow-library">
        <span>WORKFLOW LIBRARY</span>
        <div>{catalog?.workflows.map((workflow) => <button key={workflow.id} className={workflow.id === selectedWorkflowId ? "selected" : ""} onClick={() => onSelectWorkflow(workflow)}><b>{workflow.label}</b><small>{workflow.id}</small><em>{workflow.steps.length} items</em></button>)}</div>
        <div className="library-actions"><button onClick={() => onOperation("new")}>＋ New</button><button onClick={() => onOperation("example")}>Add typed example</button><button className="danger" onClick={() => onOperation("delete")}>Delete</button></div>
      </aside>

      <section className="workflow-editor">
        {!draft ? <div className="studio-empty">Loading workflow catalog…</div> : <>
          <div className="workflow-fields">
            <label><span>ID</span><input value={draft.id} onChange={(event) => onDraft({ ...draft, id: event.target.value })}/></label>
            <label><span>Label</span><input value={draft.label} onChange={(event) => onDraft({ ...draft, label: event.target.value })}/></label>
            <label className="wide"><span>Description</span><textarea value={draft.description} onChange={(event) => onDraft({ ...draft, description: event.target.value })}/></label>
          </div>

          {rawMode ? <textarea className="raw-json-editor" value={rawText} onChange={(event) => onRawText(event.target.value)} spellCheck={false}/> : <>
            <div className="ordered-head"><span>ORDERED ITEMS</span><div><button onClick={() => onAddStep("operation")}>＋ Add operation</button><button onClick={() => onAddStep("subworkflow")}>＋ Add subworkflow</button></div></div>
            <div className="step-table">
              <div className="step-row step-head"><span>#</span><span>Item ID</span><span>Type</span><span>Operation / subworkflow</span><span>Implementation</span><span>Input slots</span><span>Output slots</span><span>Optional</span></div>
              {draft.steps.map((item, index) => <button key={`${item.id}-${index}`} className={`step-row ${selectedStep === index ? "selected" : ""}`} onClick={() => onSelectStep(index)}><span>{index + 1}</span><b>{item.id}</b><span>{item.kind}</span><code>{item.operation}</code><span>{item.implementation}</span><small>{Object.keys(item.inputs).length} bound</small><small>{Object.keys(item.outputs).length} bound</small><em>{item.continueOnError ? "yes" : ""}</em></button>)}
            </div>
            <div className="step-actions"><button disabled={selectedStep === null} onClick={() => selectedStep !== null && onMoveStep(selectedStep, -1)}>↑ Move up</button><button disabled={selectedStep === null} onClick={() => selectedStep !== null && onMoveStep(selectedStep, 1)}>↓ Move down</button><button disabled={selectedStep === null} onClick={() => selectedStep !== null && onDeleteStep(selectedStep)}>Delete item</button></div>

            {step && selectedStep !== null && <div className="step-editor">
              <div className="step-editor-title"><span>EDIT ITEM {selectedStep + 1}</span><b>{step.kind === "subworkflow" ? "Nested workflow bindings" : "Typed operation route"}</b></div>
              <label><span>Item ID</span><input value={step.id} onChange={(event) => onUpdateStep(selectedStep, { id: event.target.value })}/></label>
              <label><span>{step.kind === "subworkflow" ? "Subworkflow" : "Operation"}</span><select value={step.operation} onChange={(event) => onUpdateStep(selectedStep, { operation: event.target.value })}>{step.kind === "subworkflow" ? catalog?.workflows.filter((workflow) => workflow.id !== draft.id).map((workflow) => <option key={workflow.id}>{workflow.id}</option>) : catalog?.operations.map((operation) => <option key={operation.id}>{operation.id}</option>)}</select></label>
              <label><span>Implementation</span><input value={step.implementation} onChange={(event) => onUpdateStep(selectedStep, { implementation: event.target.value })}/></label>
              <label><span>Profile</span><input value={step.profile ?? ""} placeholder="optional model route" onChange={(event) => onUpdateStep(selectedStep, { profile: event.target.value || undefined })}/></label>
              <label><span>Model</span><input value={step.model ?? ""} placeholder="$selected" onChange={(event) => onUpdateStep(selectedStep, { model: event.target.value || undefined })}/></label>
              <label><span>Analysis level</span><select value={step.analysisLevel ?? ""} onChange={(event) => onUpdateStep(selectedStep, { analysisLevel: event.target.value ? Number(event.target.value) : undefined })}><option value="">default</option><option value="2">2</option><option value="3">3</option><option value="4">4</option></select></label>
              <label className="json-field"><span>Inputs JSON</span><textarea key={`${step.id}-inputs`} defaultValue={JSON.stringify(step.inputs, null, 2)} onBlur={jsonOnBlur(selectedStep, "inputs")}/></label>
              <label className="json-field"><span>Outputs JSON</span><textarea key={`${step.id}-outputs`} defaultValue={JSON.stringify(step.outputs, null, 2)} onBlur={jsonOnBlur(selectedStep, "outputs")}/></label>
              <label className="json-field"><span>Parameters JSON</span><textarea key={`${step.id}-parameters`} defaultValue={JSON.stringify(step.parameters, null, 2)} onBlur={jsonOnBlur(selectedStep, "parameters")}/></label>
              <label className="check-field"><input type="checkbox" checked={Boolean(step.continueOnError)} onChange={(event) => onUpdateStep(selectedStep, { continueOnError: event.target.checked })}/><span>Continue on error</span></label>
            </div>}
          </>}

          <div className="studio-actions"><button onClick={() => onSave(false)}>Save</button><button className="primary" onClick={() => onSave(true)}>Save and run selected</button><button onClick={() => { onRawMode(!rawMode); if (!rawMode) onRawText(JSON.stringify(draft, null, 2)); }}>{rawMode ? "Return to form" : "Edit raw JSON"}</button></div>
        </>}
      </section>
    </div>}

    {tab === "operations" && <div className="studio-catalog"><div className="catalog-row catalog-head"><span>Operation</span><span>Typed ports</span><span>Implementation species / routes</span></div>{catalog?.operations.map((operation) => <div className="catalog-row" key={operation.id}><b>{operation.id}</b><span>{operation.ports}</span><code>{operation.routes}</code></div>)}</div>}
    {tab === "datatypes" && <div className="studio-catalog"><div className="catalog-row datatype-row catalog-head"><span>Datatype</span><span>Kind</span><span>Meaning</span><span>Relations</span></div>{catalog?.datatypes.map((datatype) => <div className="catalog-row datatype-row" key={datatype.id}><b>{datatype.id}</b><em>{datatype.kind}</em><span>{datatype.meaning}</span><code>{datatype.relations}</code></div>)}<div className="manifest-actions"><button onClick={() => onTab("datatypes")}>Open datatype graph</button><button onClick={() => onRawText(JSON.stringify(catalog?.datatypes ?? [], null, 2))}>Open manifest</button><button onClick={() => onTab("operations")}>Open operation catalog</button></div></div>}
  </div>;
}

export function WorkbenchPage() {
  const [activeStage, setActiveStage] = useState(3);
  const [view, setView] = useState<View>("canvas");
  const [selectedArtifact, setSelectedArtifact] = useState("source_observation");
  const [run, setRun] = useState<RunSnapshot | null>(null);
  const [events, setEvents] = useState<RunEvent[]>([]);
  const [eventCursor, setEventCursor] = useState(0);
  const [backendError, setBackendError] = useState<string | null>(null);
  const [commandPending, setCommandPending] = useState(false);
  const [designOperation, setDesignOperation] = useState<WorkbenchOperation | null>(null);
  const [catalog, setCatalog] = useState<Catalog | null>(null);
  const [studioTab, setStudioTab] = useState<"workflows" | "operations" | "datatypes">("workflows");
  const [selectedWorkflowId, setSelectedWorkflowId] = useState<string | null>(null);
  const [draft, setDraft] = useState<WorkflowDocument | null>(null);
  const [originalWorkflowId, setOriginalWorkflowId] = useState<string | null>(null);
  const [selectedStep, setSelectedStep] = useState<number | null>(null);
  const [rawMode, setRawMode] = useState(false);
  const [rawText, setRawText] = useState("");
  const started = useRef(false);
  const cursor = useRef(0);
  const stage = stages[activeStage - 1];

  const artifactRows = useMemo(() => {
    if (!run?.artifacts.length) return artifactFallbackRows;
    return run.artifacts.map((artifact) => ({
      ...artifact,
      confidence: artifact.confidence.toFixed(2),
      color: artifactFallbackRows.find((row) => row.name === artifact.name)?.color ?? "cyan",
    }));
  }, [run]);
  const selected = useMemo(
    () => artifactRows.find((artifact) => artifact.name === selectedArtifact) ?? artifactRows[0] ?? artifactFallbackRows[0],
    [artifactRows, selectedArtifact],
  );
  const running = run?.status === "running";
  const concluded = run?.status === "concluded";
  const chosenAction = run?.chosenAction ?? null;
  const maxStage = run?.maxStage ?? 3;

  const applySnapshot = useCallback((snapshot: RunSnapshot) => {
    setRun(snapshot);
    setEvents(snapshot.events);
    cursor.current = snapshot.cursor;
    setEventCursor(snapshot.cursor);
    setActiveStage(snapshot.stage);
    setBackendError(null);
  }, []);

  const createBackendRun = useCallback(async (workflowId = "arc3_human_observation", parentOperationId?: string) => {
    setCommandPending(true);
    try {
      const response = await fetch("/api/runs", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ workflowId, worldId: "ls20", parentOperationId }),
      });
      const payload = await response.json() as { run?: RunSnapshot; error?: string };
      if (!response.ok || !payload.run) throw new Error(payload.error || "Run creation failed");
      applySnapshot(payload.run);
      setView("canvas");
    } catch (error) {
      setBackendError(error instanceof Error ? error.message : "Backend unavailable");
    } finally {
      setCommandPending(false);
    }
  }, [applySnapshot]);

  const sendCommand = useCallback(async (command: string, input?: Record<string, unknown>) => {
    if (!run || commandPending) return null;
    setCommandPending(true);
    try {
      const response = await fetch(`/api/runs/${run.id}/commands`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ command, input }),
      });
      const payload = await response.json() as { run?: RunSnapshot; error?: string };
      if (!response.ok || !payload.run) throw new Error(payload.error || "Command failed");
      applySnapshot(payload.run);
      return payload.run;
    } catch (error) {
      setBackendError(error instanceof Error ? error.message : "Command failed");
      return null;
    } finally {
      setCommandPending(false);
    }
  }, [applySnapshot, commandPending, run]);

  const loadCatalog = useCallback(async () => {
    try {
      const response = await fetch("/api/workflows", { cache: "no-store" });
      const payload = await response.json() as Catalog & { error?: string };
      if (!response.ok) throw new Error(payload.error || "Workflow catalog failed");
      setCatalog(payload);
      if (!draft && payload.workflows.length) {
        const first = payload.workflows[0];
        setSelectedWorkflowId(first.id);
        setOriginalWorkflowId(first.id);
        setDraft(structuredClone(first));
        setRawText(JSON.stringify(first, null, 2));
      }
    } catch (error) {
      setBackendError(error instanceof Error ? error.message : "Workflow catalog unavailable");
    }
  }, [draft]);

  const selectWorkflow = (workflow: WorkflowDocument) => {
    setSelectedWorkflowId(workflow.id);
    setOriginalWorkflowId(workflow.id);
    setDraft(structuredClone(workflow));
    setRawText(JSON.stringify(workflow, null, 2));
    setSelectedStep(null);
    setRawMode(false);
  };

  const workflowOperation = async (operation: "new" | "example" | "delete") => {
    try {
      const response = await fetch("/api/workflows", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ operation, id: operation === "delete" ? selectedWorkflowId : undefined }),
      });
      const payload = await response.json() as { workflows?: WorkflowDocument[]; operation?: WorkbenchOperation; error?: string };
      if (!response.ok || !payload.workflows) throw new Error(payload.error || "Workflow operation failed");
      const nextCatalog = { ...(catalog as Catalog), workflows: payload.workflows };
      setCatalog(nextCatalog);
      const next = operation === "delete" ? payload.workflows[0] : payload.workflows.at(-1);
      if (next) selectWorkflow(next);
    } catch (error) {
      setBackendError(error instanceof Error ? error.message : "Workflow operation failed");
    }
  };

  const saveDraft = async (runAfter = false) => {
    if (!draft) return;
    try {
      const candidate = rawMode ? JSON.parse(rawText) as WorkflowDocument : draft;
      const response = await fetch("/api/workflows", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ operation: "save", workflow: candidate, originalId: originalWorkflowId }),
      });
      const payload = await response.json() as { workflows?: WorkflowDocument[]; operation?: WorkbenchOperation; error?: string };
      if (!response.ok || !payload.workflows) throw new Error(payload.error || "Workflow save failed");
      setCatalog(current => current ? { ...current, workflows: payload.workflows! } : current);
      const saved = payload.workflows.find((workflow) => workflow.id === candidate.id) ?? candidate;
      selectWorkflow(saved);
      if (payload.operation) setDesignOperation(payload.operation);
      if (runAfter) await createBackendRun(saved.id, payload.operation?.id);
      else await sendCommand("save_snapshot", { workflowId: saved.id });
    } catch (error) {
      setBackendError(error instanceof Error ? error.message : "Workflow save failed");
    }
  };

  const addStep = (kind: "operation" | "subworkflow") => {
    if (!draft) return;
    const operation = kind === "operation" ? (catalog?.operations[0]?.id ?? "capture_observation") : (catalog?.workflows.find((workflow) => workflow.id !== draft.id)?.id ?? "objectify_observation");
    const step: WorkflowStep = { id: `${kind}_${draft.steps.length + 1}`, kind, operation, implementation: kind === "operation" ? "python.default" : "nested workflow", inputs: {}, outputs: {}, parameters: {} };
    setDraft({ ...draft, steps: [...draft.steps, step] });
    setSelectedStep(draft.steps.length);
  };

  const updateStep = (index: number, patch: Partial<WorkflowStep>) => {
    if (!draft) return;
    setDraft({ ...draft, steps: draft.steps.map((step, row) => row === index ? { ...step, ...patch } : step) });
  };

  const moveStep = (index: number, delta: number) => {
    if (!draft) return;
    const target = index + delta;
    if (target < 0 || target >= draft.steps.length) return;
    const steps = [...draft.steps];
    [steps[index], steps[target]] = [steps[target], steps[index]];
    setDraft({ ...draft, steps });
    setSelectedStep(target);
  };

  const deleteStep = (index: number) => {
    if (!draft) return;
    setDraft({ ...draft, steps: draft.steps.filter((_, row) => row !== index) });
    setSelectedStep(null);
  };

  useEffect(() => {
    if (started.current) return;
    started.current = true;
    void createBackendRun();
    void loadCatalog();
  }, [createBackendRun, loadCatalog]);

  useEffect(() => {
    if (!run) return;
    const timer = window.setInterval(async () => {
      try {
        const response = await fetch(`/api/runs/${run.id}/events?after=${cursor.current}`, { cache: "no-store" });
        if (!response.ok) return;
        const payload = await response.json() as { events: RunEvent[]; cursor: number };
        if (payload.events.length) {
          setEvents(current => [...current, ...payload.events.filter((event) => !current.some((item) => item.id === event.id))]);
          cursor.current = payload.cursor;
          setEventCursor(payload.cursor);
        }
      } catch {
        // The next polling interval retries without mutating the visible run.
      }
    }, 1200);
    return () => window.clearInterval(timer);
  }, [run]);

  const runNext = () => { void sendCommand("run_next").then((next) => { if (next) setView("canvas"); }); };
  const chooseAction = (action: string) => { if (run?.stage === 4) void sendCommand("human_action", { action }).then((next) => { if (next) setView("canvas"); }); };
  const repeatFromAction = () => { void sendCommand("repeat").then((next) => { if (next) setView("canvas"); }); };
  const concludeModel = () => { void sendCommand("conclude"); };

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      if (run?.stage !== 4) return;
      const actions: Record<string, string> = { ArrowUp: "UP", ArrowLeft: "LEFT", ArrowDown: "DOWN", ArrowRight: "RIGHT", " ": "SPACE" };
      const action = actions[event.key];
      if (!action) return;
      event.preventDefault();
      void sendCommand("human_action", { action }).then((next) => { if (next) setView("canvas"); });
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [run?.stage, sendCommand]);

  const statusFor = (id: number) => id < maxStage ? "done" : id === maxStage ? (run?.status === "waiting" ? "waiting" : "active") : "waiting";

  return (
    <main className="workbench">
      <header className="topbar">
        <div className="brand"><span className="brand-mark">M</span><div><strong>MeTTaSymbolicLearnerWorkbench</strong><small>NEUROSYMBOLIC EXPERIMENT DESKTOP</small></div></div>
        <div className="run-context"><span className={`pulse ${run?.status ?? "connecting"}`}/><b>{run?.workflowId ?? "connecting_backend"}</b><span>/</span><span>{run?.worldId ?? "—"}</span><span>/</span><span>episode {String(run?.episode ?? 0).padStart(3, "0")}</span></div>
        <div className="toolbar">
          <Tooltip text="Pause or resume through the backend command bus. Intermediate state remains inspectable."><button disabled={!run || commandPending} className="icon-button" aria-label={running ? "Pause run" : "Resume run"} onClick={() => void sendCommand("toggle_pause")}>{running ? "Ⅱ" : "▶"}</button></Tooltip>
          <Tooltip text="Persist a backend event that ties this workflow configuration to the current execution history."><button disabled={!run || commandPending} className="icon-button" aria-label="Save workflow snapshot" onClick={() => void sendCommand("save_snapshot")}>⌑</button></Tooltip>
          <button disabled={!run || commandPending} className="run-button" onClick={runNext}><span>▶</span> {run?.stage === 4 && !chosenAction ? "Await action" : run?.stage === 7 ? "Complete" : commandPending ? "Working…" : "Run next"}</button>
        </div>
      </header>

      {backendError && <div className="backend-error" role="alert"><b>Backend event error</b><span>{backendError}</span><button onClick={() => setBackendError(null)}>×</button></div>}

      <section className="workspace">
        <aside className="rail">
          <div className="rail-section"><span>WORKSPACE</span>
            <Tooltip text="The runnable experiment: seven top-level stages, each able to invoke nested workflows."><button className={`rail-icon ${view === "canvas" ? "selected" : ""}`} onClick={() => setView("canvas")}>⌘<small>Flow</small></button></Tooltip>
            <Tooltip text="The full typed workflow editor from the Python Tk desktop, available in the browser."><button className={`rail-icon ${view === "editor" ? "selected" : ""}`} onClick={() => { setView("editor"); void loadCatalog(); }}>⌑<small>Studio</small></button></Tooltip>
            <Tooltip text="Browse typed observations, facts, programs, predictions, and evidence."><button className={`rail-icon ${view === "artifacts" || view === "evidence" ? "selected" : ""}`} onClick={() => setView("artifacts")}>◇<small>Data</small></button></Tooltip>
            <Tooltip text="Inspect processing resources and choose alternate implementations."><button className={`rail-icon ${view === "operations" ? "selected" : ""}`} onClick={() => setView("operations")}>▦<small>Operations</small></button></Tooltip>
            <Tooltip text="Compare prompts, models, reasoning budgets, and transcripts."><button className={`rail-icon ${view === "llms" ? "selected" : ""}`} onClick={() => setView("llms")}>✦<small>LLMs</small></button></Tooltip>
          </div>
          <div className="rail-bottom"><Tooltip text="Validate typed ports, missing resources, and workflow cycles."><button className={`rail-icon ${view === "checks" ? "selected" : ""}`} onClick={() => setView("checks")}>✓<small>Checks</small></button></Tooltip><Tooltip text="Workbench preferences and adapter configuration."><button className={`rail-icon ${view === "setup" ? "selected" : ""}`} onClick={() => setView("setup")}>⚙<small>Setup</small></button></Tooltip></div>
        </aside>

        <aside className="stages-panel">
          <div className="panel-label"><span>RUN PIPELINE</span><button aria-label="More workflow options">•••</button></div>
          <div className="workflow-title"><b>Learn a world by observation</b><small>Human apprenticeship · v1.4</small></div>
          <div className="stage-list">
            {stages.map((s) => { const status = statusFor(s.id); return <Tooltip key={s.id} text={s.description}><button onClick={() => { setActiveStage(s.id); setView("canvas"); }} className={`stage-button ${s.id === activeStage ? "active" : ""} ${status}`}><span className="stage-number">{s.id}</span><span className="stage-line"/><span className={`stage-icon ${s.accent}`}>{status === "done" ? "✓" : s.id === activeStage ? "●" : "○"}</span><div><small>{s.short}</small><b>{s.title}</b></div>{s.id === 3 && <span className="nested-badge">↳ 7</span>}</button></Tooltip>; })}
          </div>
          <div className="run-health"><div><span>RUN HEALTH</span><b>{run?.status ?? "connecting"}</b></div><div className="health-bar"><i style={{width: `${maxStage / 7 * 100}%`}}/></div><small>{Math.max(0, maxStage - 1)} stages complete · {run?.stage === 4 && !chosenAction ? "awaiting input" : concluded ? "model concluded" : `${events.length} durable events`}</small></div>
        </aside>

        <section className="main-stage">
          <nav className="view-tabs">
            <button className={view === "canvas" ? "active" : ""} onClick={() => setView("canvas")}>Workflow canvas</button>
            <button className={view === "editor" ? "active" : ""} onClick={() => setView("editor")}>Workflow editor</button>
            <button className={view === "artifacts" ? "active" : ""} onClick={() => setView("artifacts")}>Artifact explorer <span>7</span></button>
            <button className={view === "evidence" ? "active" : ""} onClick={() => setView("evidence")}>Evidence & provenance <span>18</span></button>
            <div className="view-actions"><Tooltip text="Zoom the workflow canvas to fit all active nodes."><button>⌗</button></Tooltip><Tooltip text="Open this view as a full-screen inspector."><button>↗</button></Tooltip></div>
          </nav>

          {view === "editor" && <div className="editor-surface">{designOperation && <OperationSpline operations={[designOperation]}/>}<WorkflowStudio catalog={catalog} draft={draft} selectedWorkflowId={selectedWorkflowId} selectedStep={selectedStep} rawMode={rawMode} rawText={rawText} tab={studioTab} onTab={setStudioTab} onSelectWorkflow={selectWorkflow} onDraft={setDraft} onSelectStep={setSelectedStep} onUpdateStep={updateStep} onMoveStep={moveStep} onDeleteStep={deleteStep} onAddStep={addStep} onOperation={(operation) => void workflowOperation(operation)} onSave={(runAfter) => void saveDraft(runAfter)} onRawMode={setRawMode} onRawText={setRawText}/></div>}

          {view === "canvas" && <div className="canvas-view">
            <div className="canvas-heading"><div><span>STAGE {stage.id} OF 7</span><h1>{stage.title}</h1><p>{stage.description}</p></div><div className={`stage-state ${statusFor(stage.id)}`}>{concluded && stage.id === 7 ? "MODEL SAVED" : statusFor(stage.id) === "done" ? "COMPLETED" : stage.id === activeStage && running ? "RUNNING" : stage.id === 4 ? "HUMAN INPUT" : "READY"}</div></div>
            {run?.operation && (
              <OperationSpline operations={designOperation && run.operation.parentOperationId === designOperation.id ? [designOperation, run.operation] : [run.operation]}/>
            )}
            <StageInspector stage={stage} chosenAction={chosenAction} onAction={chooseAction} onRepeat={repeatFromAction} onConclude={concludeModel}/>
            <div className="event-console" aria-live="polite"><div><span>LIVE RUN EVENTS</span><small>{run ? `backend cursor ${eventCursor}` : "connecting"}</small></div>{events.slice(-4).map((event) => <p key={event.id} className={event.tone}><time>{event.createdAt.includes("T") ? new Date(event.createdAt).toLocaleTimeString([], { hour12: false }) : event.createdAt.slice(11, 19)}</time><i/><span><b>{event.kind}</b> · {event.message}</span></p>)}</div>
          </div>}

          {view === "artifacts" && <div className="artifact-view">
            <div className="artifact-table"><div className="table-head"><span>ARTIFACT / SILO</span><span>TYPE</span><span>PRODUCER</span><span>VALUE</span><span>CONF.</span></div>{artifactRows.map(a => <Tooltip key={a.name} text={`Open ${a.name}. Versioned output from ${a.producer}; click to inspect its exact value and lineage.`}><button className={selectedArtifact === a.name ? "selected" : ""} onClick={() => setSelectedArtifact(a.name)}><span><i className={a.color}/>{a.name}<small>v{a.version}</small></span><span>{a.type}</span><span>{a.producer}</span><span>{a.value}</span><span>{a.confidence}</span></button></Tooltip>)}</div>
            <aside className="artifact-detail"><div className="detail-eyebrow">SELECTED ARTIFACT</div><h2>{selected.name}</h2><div className="type-chip">{selected.type}</div>{selected.name.includes("observation") || selected.name === "reconstruction" ? <ArcGrid reconstruction={selected.name === "reconstruction"}/> : <pre>{selected.name === "turtle_programs" ? "object(blue_hook, [\n  penup, set_pos(9,9),\n  setcolor(blue), pendown,\n  fwd(3), rot(90), fwd(2)\n])." : selected.name === "symbolic_facts" ? "object_identity(o7, blue_hook, step_0).\ncolor(blue_hook, blue).\nshape(blue_hook, hook).\nbounds(blue_hook, 9, 9, 3, 2)." : "evidence(match(source, render, 0.964)).\nevidence(identity_count, 8).\nwarning(pixel_delta, [9-10])."}</pre>}<dl><div><dt>Producer</dt><dd>{selected.producer}</dd></div><div><dt>Confidence</dt><dd>{selected.confidence}</dd></div><div><dt>Version</dt><dd>{selected.version} · append-only</dd></div><div><dt>Run</dt><dd>{run?.id.slice(0, 8) ?? "pending"}</dd></div></dl></aside>
          </div>}

          {view === "evidence" && <div className="evidence-view"><div className="evidence-summary"><span>OBJECTIFICATION QUALITY</span><strong>96.4<small>%</small></strong><p>Reconstruction agreement across shape, color, topology, and position.</p><div className="metric-row"><div><b>8 / 8</b><span>identities stable</span></div><div><b>41</b><span>facts grounded</span></div><div><b>1</b><span>pixel anomaly</span></div></div></div><div className="lineage"><h2>Artifact lineage</h2><p>Hover any node to see why the boundary is preserved.</p>{["source_observation", "entity_set", "symbolic_facts", "turtle_programs", "reconstruction", "evidence"].map((n,i) => <Tooltip key={n} text={i === 0 ? "Immutable input from the external world." : `Produced from ${i === 3 ? "entities + properties" : "the previous typed artifact"}; exact parents recorded in provenance.`}><div className={`lineage-node n${i}`}><span>{i+1}</span><b>{n}</b><small>{artifactRows.find(a => a.name === n)?.producer}</small></div></Tooltip>)}</div></div>}

          {view === "operations" && <div className="resource-view"><div className="resource-heading"><div><span>PROCESSING RESOURCES</span><h1>Operation catalog</h1><p>Each operation declares typed ports and may have several swappable implementations.</p></div><button onClick={() => void sendCommand("refresh_catalog")}>↻ Refresh catalog</button></div><div className="resource-table"><div className="resource-row resource-head"><span>OPERATION</span><span>IMPLEMENTATION</span><span>RUNTIME</span><span>TYPED PORTS</span><span>STATE</span></div>{operationCatalog.map(row => <Tooltip key={row.operation} text={`${row.implementation} can be replaced without changing the workflow as long as its typed port contract remains compatible.`}><button className="resource-row" onClick={() => { setView("editor"); setStudioTab("operations"); }}><b>{row.operation}</b><code>{row.implementation}</code><span>{row.runtime}</span><span>{row.ports}</span><em>● {row.state}</em></button></Tooltip>)}</div></div>}

          {view === "llms" && <div className="resource-view"><div className="resource-heading"><div><span>MODEL ROUTING</span><h1>LLM laboratory</h1><p>Compare providers, prompts, reasoning budgets, outputs, and independent critiques.</p></div><button onClick={() => void sendCommand("compare_models")}>▶ Compare selected</button></div><div className="model-grid">{[
            ["Primary generator", "GPT-5.6", "medium reasoning", "Produces Turtle programs and candidate explanations", "selected"],
            ["Independent critic", "Claude Sonnet", "standard", "Grades grounding and flags unsupported claims", ""],
            ["Local baseline", "Qwen 32B", "temperature 0", "Measures transfer to a home-runnable model", ""],
          ].map(model => <Tooltip key={model[0]} text={`Route configuration is saved with every transcript. ${model[3]}`}><button className={`model-card ${model[4]}`} onClick={() => void sendCommand("compare_models", { route: model[1] })}><span>{model[0]}</span><b>{model[1]}</b><small>{model[2]}</small><p>{model[3]}</p><em>inspect route →</em></button></Tooltip>)}</div><div className="prompt-preview"><div><span>PROMPT COMPOSITION</span><b>objectify / turtle_generator</b></div><pre><i>01</i> system / symbolic_visual_reasoner.md{"\n"}<i>02</i> contract / typed_turtle_output.md{"\n"}<i>03</i> context / object_identities.pl{"\n"}<i>04</i> observation / source_image.png{"\n"}<i>05</i> critique / reconstruction_diff.json</pre></div></div>}

          {view === "checks" && <div className="resource-view"><div className="resource-heading"><div><span>PRE-RUN VALIDATION</span><h1>Workflow checks</h1><p>Structural problems are caught before a nested workflow can modify experiment state.</p></div><button onClick={() => void sendCommand("validate")}>✓ Run checks</button></div><div className="checks-summary"><div className="check-score">5<small>/ 5</small><span>checks passing</span></div><div className="check-list">{validationChecks.map(check => <div key={check[0]}><span>✓</span><b>{check[0]}</b><small>{check[1]}</small><em>{check[2]}</em></div>)}</div></div></div>}

          {view === "setup" && <div className="resource-view"><div className="resource-heading"><div><span>WORKBENCH CONFIGURATION</span><h1>Experiment setup</h1><p>Settings are recorded by the backend with the run that consumed them.</p></div><button onClick={() => void sendCommand("save_config")}>Save configuration</button></div><div className="settings-grid"><label><span>World adapter</span><select defaultValue="ls20"><option>ls20 · local ARC3 adapter</option><option>generic visual world</option></select><small>Converts external state and actions at the framework boundary.</small></label><label><span>Symbolic runtime</span><select defaultValue="SWI-Prolog 9.2"><option>SWI-Prolog 9.2</option><option>MeTTa · planned route</option></select><small>Executes facts, rules, and symbolic queries.</small></label><label><span>Evidence policy</span><select defaultValue="append"><option value="append">Append-only with full provenance</option><option>Ephemeral demonstration</option></select><small>Preserves every artifact version and its exact producer.</small></label><label><span>Human boundary</span><select defaultValue="pause"><option value="pause">Pause for observed action</option><option>Autonomous candidate selection</option></select><small>Switches apprenticeship mode to agentic simulation.</small></label></div><div className="demo-notice connected"><b>Backend connected</b><span>Run state, ordered events, workflow documents, and artifact versions are persisted on the server. Python, Prolog, LLM, and Turtle adapters can publish through the same command and event contracts.</span></div></div>}
        </section>

        <aside className="inspector">
          <div className="inspector-head"><span>LIVE INSPECTOR</span><div><span className="live-dot"/> following run</div></div>
          <div className="visual-pair"><div><label>SOURCE</label><ArcGrid /></div><div><label>RENDER</label><ArcGrid reconstruction /></div></div>
          <div className="match-row"><span>visual agreement</span><b>96.4%</b></div><div className="match-track"><i/></div>
          <div className="inspect-section"><div className="section-title"><span>OBJECTS</span><b>8 found</b></div><div className="object-list"><Tooltip text="Stable identity o7 links pixels, facts, Turtle code, and later observations."><button className="selected"><i style={{background: colors[9]}}/><span><b>blue_hook</b><small>o7 · hook · 6px</small></span><em>0.97</em></button></Tooltip><Tooltip text="This marker may represent a target or a state-dependent goal cue."><button><i style={{background: colors[7]}}/><span><b>yellow_marker</b><small>o3 · block · 4px</small></span><em>0.95</em></button></Tooltip><Tooltip text="The border is retained as a semantic container, not discarded as background."><button><i style={{background: colors[1]}}/><span><b>room_boundary</b><small>o1 · frame · 44px</small></span><em>1.00</em></button></Tooltip></div></div>
          <div className="inspect-section"><div className="section-title"><span>EXECUTABLE VIEW</span><b>Turtle DSL</b></div><pre className="mini-code"><span>object</span>(blue_hook, [\n  penup, set_pos(9,9),\n  setcolor(<i>blue</i>), pendown,\n  fwd(3), rot(90), fwd(2)\n]).</pre><Tooltip text="The program is rendered and compared back to the source, turning generation quality into testable evidence."><button className="open-code" onClick={() => {setView("artifacts"); setSelectedArtifact("turtle_programs")}}>Open program & reconstruction <span>→</span></button></Tooltip></div>
          <div className="provenance-foot"><span>PROVENANCE</span><code>run_014 / stage_03 / v3</code><span className="verified">✓ verified</span></div>
        </aside>
      </section>
      <footer><span><i className={run ? "online" : "live-dot"}/> Backend {run ? "connected" : "connecting"}</span><span>SWI-Prolog 9.2 contract</span><span>Python 3.12 contract</span><span>{run?.artifacts.length ?? 0} artifacts</span><span className="footer-right">cursor {eventCursor} · run {run?.id.slice(0, 8) ?? "pending"} · <kbd>?</kbd> shortcuts</span></footer>
    </main>
  );
}
