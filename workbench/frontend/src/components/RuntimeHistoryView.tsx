import { cloneElement, isValidElement, lazy, Suspense, useEffect, useMemo, useState, type ReactElement, type ReactNode } from "react";
import { createPortal } from "react-dom";
import { jsonValueToMetta } from "../lib/mettaResourceCodec";
import { WorkflowRunsControl } from "./WorkflowRunsControl";
import { ThreeStateAccordionMember, ThreeStateAccordionStack, type AccordionDisplayMode } from "./ThreeStateAccordion";
import { replaceWorkbenchLocation } from "../lib/workbenchNavigation";

const WorkflowRunnerTodoReference = lazy(() =>
  import("./WorkflowRunnerTodoReference").then((module) => ({
    default: module.WorkflowRunnerTodoReference,
  })),
);

type DocumentRecord = { document?: Record<string, any> };
type RuntimeRun = {
  id: string;
  workflowId: string;
  workflowVersion: number;
  status: string;
  createdAt?: string;
  updatedAt?: string;
  error?: string;
  inputs: unknown;
  outputs: unknown;
  steps: Array<{
    stepId: string;
    status: string;
    attempt?: number;
    error?: string;
  }>;
  events: Array<{
    id: number | string;
    stepId?: string;
    kind: string;
    payload?: unknown;
    createdAt: string;
  }>;
  artifacts: Array<{
    id: string;
    stepId?: string;
    name: string;
    datatype?: string;
    representation?: string;
    payload?: unknown;
    contentHash?: string;
    provenance?: Record<string, unknown>;
    createdAt?: string;
    redacted?: boolean;
  }>;
  captureGroups?: Array<{
    id: string;
    markerName: string;
    iteration: number;
    iterationCount: number;
    memberArtifactIds: string[];
    memberNames: string[];
  }>;
  logs: Array<{
    id: number | string;
    stepId?: string;
    stream: string;
    message: string;
    createdAt?: string;
  }>;
};
type WorkflowStep = {
  id: string;
  label?: string;
  kind?: string;
  operation?: string;
  implementation?: string;
  dependsOn?: string[];
  inputs?: unknown;
  outputs?: unknown;
  while?: WorkflowWhile | WorkflowWhile[];
  form?: Record<
    string,
    {
      type?: string;
      label?: string;
      description?: string;
      default?: unknown;
      options?: unknown[];
      secret?: boolean;
      sensitive?: boolean;
    }
  >;
};
type WorkflowWhile = {
  condition?: unknown;
  operator?: "truthy" | "not_empty" | "equals" | "less_than" | string;
  conditionPort?: unknown;
  maxIterations: number;
  targetStepId?: string;
};
type FrozenWorkflow = {
  id: string;
  version: number;
  label?: string;
  description?: string;
  steps: WorkflowStep[];
};
type WorkflowInputContract =
  | string
  | {
      datatype?: string;
      type?: string;
      representation?: string;
      default?: unknown;
      options?: unknown[];
    };
type GoalRun = {
  id: string;
  goalId: string;
  goalVariantId?: string;
  planId: string;
  planVariantId: string;
  contextId?: string;
  contextVariantId?: string;
  workflowRunId: string;
  status: string;
  createdAt?: string;
  workflowRun: RuntimeRun;
};
type InvocationTrace = {
  id: string;
  kind: string;
  status: string;
  createdAt?: string;
  logPath: string;
  modelId?: string;
  operationId?: string;
  prompt?: string;
  error?: unknown;
  response?: { text?: string; latencyMs?: number; backendId?: string };
  implementation?: { id?: string; label?: string; implementation?: string };
  operation?: { id?: string; label?: string };
  inputs?: unknown;
  result?: unknown;
};
type Mode =
  | "goalRuns"
  | "workflowRuns"
  | "execs"
  | "events"
  | "states"
  | "runtimeContexts"
  | "logs";
const runtimeRecordFromLocation = (mode: Mode) => {
  const parameters = new URLSearchParams(window.location.search);
  return parameters.get(mode === "states" ? "state" : "runtimeRecord") || "";
};
type RuntimeRecordKind =
  | "workflow run"
  | "step execution"
  | "event"
  | "state artifact"
  | "runtime context"
  | "log";
type RuntimeHistoryRow = {
  key: string;
  a: string;
  b: string;
  c: string;
  d: string;
  e: string;
  run: RuntimeRun;
  recordKind: RuntimeRecordKind;
  record: unknown;
};
type RunStatusFilter = "all" | "running" | "failed" | "cancelled";
type RunWorkspacePanel = "launcher" | "spline" | "runs" | "objects";
type MemoryValueView = "guess" | "image" | "metta" | "json" | "text";
type BootstrappedStateValue = {
  kind: "state_value";
  id: string;
  label?: string;
  enabled: boolean;
  datatype: string;
  source: Record<string, unknown>;
  preferredRenderer: string;
  treatAsList: boolean;
  allowRedefinition: boolean;
  applicability: string[];
  captureGroupIds?: string[];
  defaultValue?: unknown;
  value?: unknown;
};
type StateApplicability =
  | "startup"
  | "steps"
  | "chapter"
  | "game"
  | "always"
  | "postMortem";
type StateValueProperties = {
  enabled: boolean;
  datatype: string;
  applicability: StateApplicability[];
  preferredRenderer: MemoryValueView;
  treatAsList: boolean;
};
const STATE_APPLICABILITY: Array<[StateApplicability, string]> = [
  ["startup", "STARTUP"],
  ["steps", "STEPS"],
  ["chapter", "CHAPTER"],
  ["game", "GAME"],
  ["always", "ALWAYS"],
  ["postMortem", "POST-MORTEM"],
];

function StateValuePropertyEditor({
  value,
  onChange,
}: {
  value: StateValueProperties;
  onChange: (value: StateValueProperties) => void;
}) {
  return (
    <div
      className={`state-value-properties ${value.enabled ? "enabled" : "disabled"}`}
      data-properties={JSON.stringify(value)}
    >
      <div
        className="state-applicability"
        role="group"
        aria-label="State value applicability"
      >
        <label className="state-enabled">
          <input
            type="checkbox"
            checked={value.enabled}
            onChange={(event) =>
              onChange({ ...value, enabled: event.target.checked })
            }
          />
          <span>{value.enabled ? "ENABLED" : "DISABLED · ALWAYS IGNORE"}</span>
        </label>
        {STATE_APPLICABILITY.map(([key, label]) => (
          <label key={key}>
            <input
              type="checkbox"
              disabled={!value.enabled}
              checked={value.applicability.includes(key)}
              onChange={() =>
                onChange({
                  ...value,
                  applicability: value.applicability.includes(key)
                    ? value.applicability.filter((item) => item !== key)
                    : [...value.applicability, key],
                })
              }
            />
            <span>{label}</span>
          </label>
        ))}
      </div>
      <div className="state-render-properties">
        <label>
          <span>Datatype</span>
          <input
            type="text"
            value={value.datatype}
            placeholder="semantic datatype…"
            onChange={(event) =>
              onChange({ ...value, datatype: event.target.value })
            }
          />
        </label>
        <label>
          <span>Preferred Renderer</span>
          <select
            disabled={!value.enabled}
            value={value.preferredRenderer}
            onChange={(event) =>
              onChange({
                ...value,
                preferredRenderer: event.target.value as MemoryValueView,
              })
            }
          >
            <option value="guess">Guess</option>
            <option value="image">Image</option>
            <option value="metta">MeTTa</option>
            <option value="json">JSON</option>
            <option value="text">Small textbox</option>
          </select>
        </label>
        <label>
          <input
            type="checkbox"
            disabled={!value.enabled}
            checked={value.treatAsList}
            onChange={(event) =>
              onChange({ ...value, treatAsList: event.target.checked })
            }
          />
          <span>Treat As List</span>
        </label>
      </div>
    </div>
  );
}

function BootstrappedStateValues({
  values,
  durable,
}: {
  values: BootstrappedStateValue[];
  durable: boolean;
}) {
  if (!values.length) return null;
  const groups = new Map<string, BootstrappedStateValue[]>();
  values.forEach((value) =>
    (value.captureGroupIds || []).forEach((groupId) =>
      groups.set(groupId, [...(groups.get(groupId) || []), value]),
    ),
  );
  return (
    <section className="detected-memory-preflight">
      <header>
        <span>DETECTED MEMORY VALUES</span>
        <b>
          {values.length} {durable ? "durable" : "preflight"} state-value
          definitions
        </b>
        <small>
          {durable
            ? "Frozen with the selected run"
            : "System bootstrap · review in Workflow Runner before launch"}
        </small>
      </header>
      {groups.size > 0 && <div className="preflight-capture-groups"><strong>INFERRED VALUE GROUPS</strong>{[...groups].map(([groupId, members]) => <article key={groupId}><div><b>{groupId}</b><small>Repeated output boundary · {members.length} tracked values</small></div><span>{members.map((member) => member.label || member.id).join(" · ")}</span></article>)}</div>}
      <div>
        {values.map((value) => (
          <article
            key={value.id}
            className={value.enabled ? "enabled" : "disabled"}
          >
            <span>{value.enabled ? "ON" : "IGNORE"}</span>
            <div>
              <b>{value.id}</b>
              <small>
                {String(value.source.kind || "source")} ·{" "}
                {value.datatype || "unknown"}
              </small>
            </div>
            <em>
              {value.preferredRenderer}
              {value.treatAsList ? " · list" : ""}
              {value.allowRedefinition ? " · redefine" : ""}
              {value.captureGroupIds?.length ? ` · ${value.captureGroupIds.join(" · ")}` : ""}
            </em>
          </article>
        ))}
      </div>
    </section>
  );
}

function PanelFrameControls({
  panel,
  maximized,
  minimized,
  onMaximize,
  onMinimize,
  onRestore,
}: {
  panel: RunWorkspacePanel;
  maximized: boolean;
  minimized: boolean;
  onMaximize: () => void;
  onMinimize: () => void;
  onRestore: () => void;
}) {
  if (minimized) return null;
  return (
    <div
      className="panel-frame-controls"
      role="group"
      aria-label={`${panel} panel controls`}
    >
      <button
        type="button"
        title={`Minimize ${panel}`}
        aria-label={`Minimize ${panel}`}
        onClick={(event) => {
          event.currentTarget
            .closest(".panel-frame")
            ?.classList.remove("display-all");
          onMinimize();
        }}
      >
        −
      </button>
      <button
        type="button"
        title={`Restore default ${panel}`}
        aria-label={`Restore default ${panel}`}
        onClick={(event) => {
          event.currentTarget
            .closest(".panel-frame")
            ?.classList.remove("display-all");
          onRestore();
        }}
      >
        *
      </button>
      <button
        type="button"
        title={`Display all ${panel} content`}
        aria-label={`Display all ${panel} content`}
        onClick={(event) => {
          onRestore();
          event.currentTarget
            .closest(".panel-frame")
            ?.classList.add("display-all");
        }}
      >
        +
      </button>
      <button
        type="button"
        title={`${panel} takes over the middle workspace`}
        aria-label={`${panel} takes over the middle workspace`}
        disabled={maximized}
        onClick={(event) => {
          event.currentTarget
            .closest(".panel-frame")
            ?.classList.remove("display-all");
          onMaximize();
        }}
      >
        [ـ]
      </button>
    </div>
  );
  return (
    <div
      className="panel-frame-controls"
      role="group"
      aria-label={`${panel} panel controls`}
    >
      <button
        type="button"
        title={`Minimize ${panel}`}
        aria-label={`Minimize ${panel}`}
        disabled={minimized}
        onClick={onMinimize}
      >
        —
      </button>
      <button
        type="button"
        title={`Default ${panel}`}
        aria-label={`Default ${panel}`}
        disabled={!maximized && !minimized}
        onClick={onRestore}
      >
        ◇
      </button>
      <button
        type="button"
        title={`Maximize ${panel}`}
        aria-label={`Maximize ${panel}`}
        disabled={maximized}
        onClick={onMaximize}
      >
        □
      </button>
    </div>
  );
}

async function api(path: string, init?: RequestInit) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  const payload = await response.json();
  if (!response.ok)
    throw new Error(payload.error || payload.detail || response.statusText);
  return payload;
}

const stamp = (value?: string) =>
  value ? value.replace("T", " ").slice(0, 19) : "—";
const artifactColors = [
  "#101820",
  "#2d8cff",
  "#ff3b4f",
  "#28c76f",
  "#ffd43b",
  "#8b5cf6",
  "#ff9f43",
  "#19d3da",
  "#f8fafc",
  "#5b6573",
];
function visualArtifactPayload(
  payload: unknown,
): { image?: string; grid?: number[][] } | null {
  if (
    Array.isArray(payload) &&
    payload.length > 0 &&
    payload.every(
      (row) =>
        Array.isArray(row) && row.every((cell) => typeof cell === "number"),
    )
  )
    return { grid: payload as number[][] };
  if (typeof payload === "string" && payload.startsWith("data:image/"))
    return { image: payload };
  if (payload && typeof payload === "object") {
    const value = payload as Record<string, unknown>;
    const image = [value.dataUrl, value.data_url, value.image].find(
      (item) => typeof item === "string" && item.startsWith("data:image/"),
    );
    if (typeof image === "string") return { image };
    if (
      Array.isArray(value.grid) &&
      value.grid.length > 0 &&
      value.grid.every(
        (row) =>
          Array.isArray(row) && row.every((cell) => typeof cell === "number"),
      )
    )
      return { grid: value.grid as number[][] };
  }
  return null;
}
function ArtifactVisual({
  artifact,
}: {
  artifact: RuntimeRun["artifacts"][number];
}) {
  const visual = visualArtifactPayload(artifact.payload);
  if (!visual) return null;
  return (
    <figure className="run-artifact-visual">
      <figcaption>
        <b>{artifact.name}</b>
        <span>{artifact.datatype || "visual artifact"}</span>
      </figcaption>
      {visual.image ? (
        <img src={visual.image} alt={artifact.name} />
      ) : (
        <div
          className="run-artifact-grid"
          style={{
            gridTemplateColumns: `repeat(${visual.grid?.[0]?.length || 1}, 1fr)`,
          }}
        >
          {visual.grid?.flatMap((row, rowIndex) =>
            row.map((cell, columnIndex) => (
              <i
                key={`${rowIndex}:${columnIndex}`}
                style={{
                  background:
                    artifactColors[Math.abs(cell) % artifactColors.length],
                }}
                title={`${columnIndex},${rowIndex}: ${cell}`}
              />
            )),
          )}
        </div>
      )}
    </figure>
  );
}
function artifactRecords(
  artifact: RuntimeRun["artifacts"][number],
  collectionKeys: string[],
): Record<string, unknown>[] {
  const payload = artifact.payload;
  if (Array.isArray(payload))
    return payload.filter((item) => item && typeof item === "object") as Record<
      string,
      unknown
    >[];
  if (!payload || typeof payload !== "object") return [];
  const record = payload as Record<string, unknown>;
  for (const key of collectionKeys)
    if (Array.isArray(record[key]))
      return (record[key] as unknown[]).filter(
        (item) => item && typeof item === "object",
      ) as Record<string, unknown>[];
  return [record];
}
function objectArtifactRecords(
  artifact: RuntimeRun["artifacts"][number],
): Record<string, unknown>[] {
  const payload = artifact.payload;
  if (Array.isArray(payload))
    return payload.filter((item) => item && typeof item === "object") as Record<
      string,
      unknown
    >[];
  if (!payload || typeof payload !== "object") return [];
  const record = payload as Record<string, unknown>;
  for (const key of ["objects", "entities", "objectAnnotations"]) {
    if (Array.isArray(record[key]))
      return (record[key] as unknown[]).filter(
        (item) => item && typeof item === "object",
      ) as Record<string, unknown>[];
  }
  return /object_list/i.test(String(artifact.representation || ""))
    ? [record]
    : [];
}
function gameIdentity(value: unknown): string {
  if (typeof value === "string" || typeof value === "number")
    return String(value);
  if (!value || typeof value !== "object") return "";
  const record = value as Record<string, unknown>;
  for (const key of ["game_id", "gameId", "selected_game_id", "selectedGameId"])
    if (typeof record[key] === "string" || typeof record[key] === "number")
      return String(record[key]);
  for (const key of [
    "game",
    "selected_game",
    "selectedGame",
    "current_game",
    "currentGame",
  ]) {
    const nested = gameIdentity(record[key]);
    if (nested) return nested;
  }
  return "";
}
function levelIdentity(value: unknown): string {
  if (!value || typeof value !== "object") return "";
  const record = value as Record<string, unknown>;
  for (const key of ["level_id", "levelId", "level", "stage_id", "stageId"])
    if (typeof record[key] === "string" || typeof record[key] === "number")
      return String(record[key]);
  return "";
}

function WorkflowRunSplineWorkspace({
  run,
  workflow,
  onOpenResource,
  expandedPanel,
  minimizedPanels,
  objectDisplayMode,
  setObjectDisplayMode,
  objectsListDisplayMode,
  setObjectsListDisplayMode,
  rightColumnAccordionHost,
  splineDisplayMode,
  setSplineDisplayMode,
  setExpandedPanel,
  setPanelMinimized,
}: {
  run: RuntimeRun;
  workflow: FrozenWorkflow | null;
  onOpenResource?: OpenRuntimeResource;
  expandedPanel: RunWorkspacePanel | null;
  minimizedPanels: Set<RunWorkspacePanel>;
  objectDisplayMode: AccordionDisplayMode;
  setObjectDisplayMode: (mode: AccordionDisplayMode) => void;
  objectsListDisplayMode: AccordionDisplayMode;
  setObjectsListDisplayMode: (mode: AccordionDisplayMode) => void;
  rightColumnAccordionHost: Element | null;
  splineDisplayMode: AccordionDisplayMode;
  setSplineDisplayMode: (mode: AccordionDisplayMode) => void;
  setExpandedPanel: (panel: RunWorkspacePanel | null) => void;
  setPanelMinimized: (panel: RunWorkspacePanel, minimized: boolean) => void;
}) {
  const [view, setView] = useState<"topology" | "chronology">("topology");
  const [objectView, setObjectView] = useState<"list" | "tiles">("list");
  const [memoryScope, setMemoryScope] = useState<
    "step" | "level" | "game" | "allGames" | "postMortem"
  >("step");
  const [memoryStepId, setMemoryStepId] = useState("");
  const [memoryScopeDisplayModes, setMemoryScopeDisplayModes] = useState<Record<string, AccordionDisplayMode>>({
    startup: "scroll",
    step: "scroll",
    level: "strip",
    game: "strip",
    allGames: "strip",
    postMortem: "strip",
  });
  useEffect(() => {
    setMemoryScopeDisplayModes({
      startup: objectDisplayMode,
      step: objectDisplayMode,
      level: objectDisplayMode,
      game: objectDisplayMode,
      allGames: objectDisplayMode,
      postMortem: objectDisplayMode,
    });
  }, [objectDisplayMode]);
  const [memoryViews, setMemoryViews] = useState<
    Record<string, MemoryValueView>
  >({});
  const [stateValueProperties, setStateValueProperties] = useState<
    Record<string, StateValueProperties>
  >({});
  const steps = workflow?.steps || [];
  const width = Math.max(760, steps.length * 165);
  const positions = new Map(
    steps.map((step, index) => [
      step.id,
      { x: 85 + index * 155, y: 72 + (index % 2) * 76 },
    ]),
  );
  const repeatedWrites = new Map<string, number[]>();
  steps.forEach((step, index) => Object.values(step.outputs && typeof step.outputs === "object" ? step.outputs as Record<string, unknown> : {}).forEach((binding) => { const name=String(binding||"");if(name)repeatedWrites.set(name,[...(repeatedWrites.get(name)||[]),index]); }));
  const captureLoopEdges=[...repeatedWrites].flatMap(([markerName,indices])=>indices.length<2?[]:indices.flatMap((start,iteration)=>{const end=(indices[iteration+1]??steps.length)-1;return end>start?[{id:`${markerName}:${iteration+1}`,markerName,iteration:iteration+1,startStepId:steps[start].id,endStepId:steps[end].id}]:[]}));
  const declaredWhileEdges = steps.flatMap((step) => {
    const loops = step.while ? (Array.isArray(step.while) ? step.while : [step.while]) : [];
    return loops.map((loop, loopIndex) => {
      const executedIterations = run.events.filter((event) => {
        if (event.kind !== "loop.iteration" || event.stepId !== step.id || !event.payload || typeof event.payload !== "object") return false;
        return Number((event.payload as Record<string, unknown>).loopIndex) === loopIndex;
      }).length;
      return {
        id: `${step.id}:${loopIndex}`,
        controllerStepId: step.id,
        targetStepId: loop.targetStepId || step.id,
        loopIndex,
        executedIterations,
        maxIterations: Number(loop.maxIterations || 0),
        operator: loop.operator || "truthy",
      };
    });
  });
  const chronologyWidth = Math.max(760, run.events.length * 120 + 80);
  const focalStepId =
    memoryStepId ||
    [...run.steps]
      .reverse()
      .find((step) =>
        ["running", "waiting", "paused", "completed", "failed"].includes(
          step.status,
        ),
      )?.stepId ||
    steps[0]?.id ||
    "";
  const selectedSplineStep = steps.find((step) => step.id === focalStepId);
  const selectedSplineRuntime = run.steps.find((step) => step.stepId === focalStepId);
  const selectedSplineEvents = run.events.filter((event) => event.stepId === focalStepId);
  const selectedSplineArtifacts = run.artifacts.filter((artifact) => artifact.stepId === focalStepId);
  const selectedSplineLatestEvent = selectedSplineEvents.at(-1);
  const compactValue = (value: unknown) => {
    if (value === undefined || value === null) return "None";
    const serialized = typeof value === "string" ? value : JSON.stringify(value);
    return serialized.length > 180 ? `${serialized.slice(0, 177)}…` : serialized;
  };
  const inputs =
    run.inputs && typeof run.inputs === "object"
      ? (run.inputs as Record<string, unknown>)
      : {};
  const selectedGameId =
    gameIdentity(run.outputs) ||
    [...run.artifacts]
      .reverse()
      .map((artifact) => gameIdentity(artifact.payload))
      .find(Boolean) ||
    gameIdentity(inputs.previous_game_id) ||
    "unselected";
  const selectedGameArtifacts =
    selectedGameId === "unselected"
      ? run.artifacts
      : run.artifacts.filter(
          (artifact) => gameIdentity(artifact.payload) === selectedGameId,
        );
  const selectedLevelId =
    levelIdentity(run.outputs) ||
    [...selectedGameArtifacts]
      .reverse()
      .map((artifact) => levelIdentity(artifact.payload))
      .find(Boolean) ||
    "unselected";
  const scopedArtifacts =
    memoryScope === "allGames" || memoryScope === "postMortem"
      ? run.artifacts
      : memoryScope === "game"
        ? selectedGameArtifacts
        : memoryScope === "level"
          ? selectedGameArtifacts.filter(
              (artifact) =>
                selectedLevelId === "unselected" ||
                levelIdentity(artifact.payload) === selectedLevelId,
            )
          : selectedGameArtifacts.filter(
              (artifact) => artifact.stepId === focalStepId,
            );
  const allObjects = run.artifacts.flatMap((artifact) =>
    objectArtifactRecords(artifact).map((record) => ({ artifact, record })),
  );
  const objects = allObjects;
  const setMemoryView = (key: string, next: MemoryValueView) =>
    setMemoryViews((current) => ({ ...current, [key]: next }));
  const propertiesFor = (key: string, datatype = ""): StateValueProperties =>
    stateValueProperties[key] || {
      enabled: true,
      datatype:
        datatype ||
        (key === "objects"
          ? "object_list"
          : key === "startup"
            ? "workflow_state"
            : ""),
      applicability: STATE_APPLICABILITY.map(([value]) => value),
      preferredRenderer: memoryViews[key] || "metta",
      treatAsList: key === "objects",
    };
  const setPropertiesFor = (key: string, value: StateValueProperties) => {
    setStateValueProperties((current) => ({ ...current, [key]: value }));
    setMemoryView(key, value.preferredRenderer);
  };
  const renderMemoryValue = (
    key: string,
    value: unknown,
    artifact?: RuntimeRun["artifacts"][number],
  ) => {
    const selected =
      memoryViews[key] ||
      (artifact && visualArtifactPayload(artifact.payload) ? "image" : "metta");
    if (
      selected === "image" &&
      artifact &&
      visualArtifactPayload(artifact.payload)
    )
      return <ArtifactVisual artifact={artifact} />;
    if (selected === "guess") {
      const record =
        value && typeof value === "object"
          ? (value as Record<string, unknown>)
          : {};
      return (
        <div className="memory-guess">
          <b>
            {String(
              record.guess ||
                record.label ||
                record.name ||
                record.id ||
                "No guess recorded",
            )}
          </b>
          {typeof record.confidence === "number" && (
            <small>confidence {record.confidence.toFixed(2)}</small>
          )}
        </div>
      );
    }
    if (selected === "json") return <pre>{JSON.stringify(value, null, 2)}</pre>;
    if (selected === "text")
      return (
        <textarea
          className="memory-small-text"
          readOnly
          value={typeof value === "string" ? value : JSON.stringify(value)}
        />
      );
    return <pre>{jsonValueToMetta(value)}</pre>;
  };
  const memoryScopeSections: Array<{
    id: string;
    scope?: "step" | "level" | "game" | "allGames" | "postMortem";
    title: string;
    detail: string;
    value: unknown;
  }> = [
    ...(run.captureGroups || []).map((group) => { const ids=new Set(group.memberArtifactIds);return {id:`loop:${group.id}`,title:`${group.markerName} · ITERATION ${group.iteration}`,detail:`${group.memberArtifactIds.length} values · inferred from repeated output`,value:run.artifacts.filter((artifact)=>ids.has(artifact.id)).map((artifact)=>({name:artifact.name,stepId:artifact.stepId,value:artifact.payload}))};}),
    { id: "step", scope: "step", title: "VALUES OF STEPS", detail: steps.find((step) => step.id === focalStepId)?.label || focalStepId || "Step", value: selectedGameArtifacts.filter((artifact) => artifact.stepId === focalStepId).map((artifact) => artifact.payload) },
    { id: "level", scope: "level", title: "VALUES OF CHAPTER", detail: selectedLevelId, value: selectedGameArtifacts.filter((artifact) => selectedLevelId === "unselected" || levelIdentity(artifact.payload) === selectedLevelId).map((artifact) => artifact.payload) },
    { id: "game", scope: "game", title: "VALUES OF GAME", detail: selectedGameId, value: selectedGameArtifacts.map((artifact) => artifact.payload) },
    { id: "allGames", scope: "allGames", title: "VALUES OF ALL TIME", detail: `${run.artifacts.length} persisted states`, value: run.artifacts.map((artifact) => artifact.payload) },
    { id: "postMortem", scope: "postMortem", title: "VALUES POST-MORTEM", detail: run.status, value: [run.outputs, ...run.artifacts.map((artifact) => artifact.payload)] },
  ];
  return (
    <>
      <ThreeStateAccordionMember
        stackId="right-stack"
        label="SELECTED RUN SPLINE"
        value={run.workflowId}
        detail={run.status}
        mode={splineDisplayMode}
        onChange={setSplineDisplayMode}
        baseClass="workflow-run-spline-band panel-frame"
        scrollSize="360px"
        itemHeader={<><span className="run-projection-mode-description">SPLINE VIEW</span><div
            className="run-projection-modes"
            role="group"
            aria-label="Workflow run view"
          >
            <button
              className={view === "topology" ? "active" : ""}
              onClick={() => setView("topology")}
            >
              Topology
            </button>
            <button
              className={view === "chronology" ? "active" : ""}
              onClick={() => setView("chronology")}
            >
              Chronology
            </button>
          </div></>}
        footer={<><b>{run.id}</b><span>{run.status}</span></>}
      >
        <div className="workflow-run-spline-scroll">
          {view === "topology" ? (
            <svg viewBox={`0 0 ${width} 190`} style={{ minWidth: width }} preserveAspectRatio="xMidYMid meet">
              <defs>
                <marker
                  id={`spline-arrow-${run.id}`}
                  viewBox="0 0 10 10"
                  refX="9"
                  refY="5"
                  markerWidth="6"
                  markerHeight="6"
                  orient="auto"
                >
                  <path d="M0 0L10 5L0 10z" />
                </marker>
              </defs>
              {steps.flatMap((step) =>
                (step.dependsOn || []).map((parentId) => {
                  const parent = positions.get(parentId),
                    child = positions.get(step.id);
                  return parent && child ? (
                    <path
                      key={`${parentId}:${step.id}`}
                      className="run-topology-edge"
                      d={`M${parent.x + 48},${parent.y} C${(parent.x + child.x) / 2},${parent.y} ${(parent.x + child.x) / 2},${child.y} ${child.x - 48},${child.y}`}
                      markerEnd={`url(#spline-arrow-${run.id})`}
                    />
                  ) : null;
                }),
              )}
              {captureLoopEdges.map((edge) => { const start=positions.get(edge.startStepId),end=positions.get(edge.endStepId);if(!start||!end)return null;const top=12+Math.min(edge.iteration*5,22);return <g key={edge.id}><path className="run-topology-loop-edge" d={`M${end.x},${end.y-28} C${end.x},${top} ${start.x},${top} ${start.x},${start.y-28}`} markerEnd={`url(#spline-arrow-${run.id})`}/><text className="run-topology-loop-label" x={(start.x+end.x)/2} y={top-3} textAnchor="middle">{edge.markerName} · {edge.iteration}</text></g>;})}
              {declaredWhileEdges.map((edge) => {
                const controller = positions.get(edge.controllerStepId), target = positions.get(edge.targetStepId);
                if (!controller || !target) return null;
                const lift = 52 + edge.loopIndex * 17, middle = (controller.x + target.x) / 2;
                const path = edge.controllerStepId === edge.targetStepId
                  ? `M${controller.x + 32},${controller.y - 27} C${controller.x + 68},${controller.y - lift} ${controller.x - 68},${controller.y - lift} ${controller.x - 32},${controller.y - 27}`
                  : `M${controller.x},${controller.y - 29} C${middle},${controller.y - lift} ${middle},${target.y - lift} ${target.x},${target.y - 29}`;
                return <g key={`declared-while:${edge.id}`}><path className="run-topology-loop-edge declared" d={path} markerEnd={`url(#spline-arrow-${run.id})`}/><text className="run-topology-loop-label declared" x={middle} y={Math.min(controller.y,target.y)-lift+14} textAnchor="middle">WHILE · {edge.executedIterations}/{edge.maxIterations}</text><title>{`While ${edge.operator}; return to ${edge.targetStepId}; ${edge.executedIterations} persisted iterations of ${edge.maxIterations}`}</title></g>;
              })}
              {steps.map((step, index) => {
                const point = positions.get(step.id)!;
                const status =
                  run.steps.find((item) => item.stepId === step.id)?.status ||
                  "defined";
                return (
                  <g
                    key={step.id}
                    transform={`translate(${point.x - 50},${point.y - 25})`}
                    className={`run-topology-node ${status} ${focalStepId === step.id ? "selected" : ""}`}
                    role="button"
                    tabIndex={0}
                    aria-label={`Select workflow step ${index + 1}: ${step.label || step.id}`}
                    onClick={() => {
                      setMemoryStepId(step.id);
                      setMemoryScope("step");
                    }}
                    onKeyDown={(event) => {
                      if (event.key !== "Enter" && event.key !== " ") return;
                      event.preventDefault();
                      setMemoryStepId(step.id);
                      setMemoryScope("step");
                    }}
                  >
                    <rect width="100" height="50" rx="6" />
                    <text
                      x="50"
                      y="18"
                      textAnchor="middle"
                      className="node-index"
                    >
                      {index + 1}
                    </text>
                    <text
                      x="50"
                      y="34"
                      textAnchor="middle"
                      className="node-title"
                    >
                      {step.label || step.id}
                    </text>
                    <text
                      x="50"
                      y="45"
                      textAnchor="middle"
                      className="node-status"
                    >
                      {status}
                    </text>
                  </g>
                );
              })}
            </svg>
          ) : (
            <svg
              viewBox={`0 0 ${chronologyWidth} 190`}
              style={{ minWidth: chronologyWidth }}
              preserveAspectRatio="xMidYMid meet"
            >
              {run.events.map((event, index) => {
                const x = 55 + index * 120,
                  y = 90 + (index % 2) * 42;
                return (
                  <g
                    key={event.id}
                    transform={`translate(${x},${y})`}
                    className={`run-chronology-node ${/fail|error|cancel/i.test(event.kind) ? "failed" : /start|running|resume/i.test(event.kind) ? "running" : "completed"}`}
                  >
                    <circle r="18" />
                    <text className="event-index" textAnchor="middle" y="3">
                      {index + 1}
                    </text>
                    <text className="event-kind" textAnchor="middle" y="31">
                      {event.kind.slice(0, 18)}
                    </text>
                  </g>
                );
              })}
            </svg>
          )}
        </div>
        <section className="run-spline-node-inspector" aria-live="polite">
          <div>
            <span>SELECTED STEP</span>
            <h3>{selectedSplineStep?.label || selectedSplineStep?.id || "Select a spline node"}</h3>
            <small>{selectedSplineStep?.implementation || selectedSplineStep?.operation || selectedSplineStep?.kind || "No step selected"}</small>
            {selectedSplineStep?.operation && onOpenResource && <button type="button" className="runtime-resource-link" onClick={() => onOpenResource("operation", selectedSplineStep.operation!)}>Open Operation</button>}
          </div>
          <div>
            <span>RUNTIME</span>
            <b>{selectedSplineRuntime?.status || "defined"}</b>
            <small>{selectedSplineRuntime?.error || selectedSplineLatestEvent?.kind || "No execution event yet"}</small>
            <small>{selectedSplineEvents.length} events · {selectedSplineArtifacts.length} artifacts</small>
          </div>
          <div>
            <span>INPUTS</span>
            <code>{compactValue(selectedSplineStep?.inputs)}</code>
          </div>
          <div>
            <span>OUTPUTS</span>
            <code>{compactValue(selectedSplineStep?.outputs)}</code>
          </div>
        </section>
      </ThreeStateAccordionMember>
      {rightColumnAccordionHost && createPortal(<>
            {memoryScopeSections.map((section) => {
              const mode = memoryScopeDisplayModes[section.id];
              const propertyKey = `scope:${section.id}`;
              return (
                <ThreeStateAccordionMember
                  key={section.id}
                  stackId="right-stack"
                  label={section.title}
                  value={section.detail}
                  mode={mode}
                  onChange={(nextMode) => {
                    if (section.scope) setMemoryScope(section.scope);
                    setMemoryScopeDisplayModes((current) => ({ ...current, [section.id]: nextMode }));
                  }}
                  baseClass="detected-memory-scope-member"
                  scrollSize="320px"
                  footer={<span>{section.id === "step" ? `Step ${focalStepId || "unselected"}` : section.detail}</span>}
                >
                  <div className="detected-memory-scope-member-body">
                    {section.id === "step" && (
                      <select aria-label="Memory values workflow step" value={focalStepId} onChange={(event) => { setMemoryStepId(event.target.value); setMemoryScope("step"); }}>
                        {steps.map((step, index) => <option key={step.id} value={step.id}>{index + 1}. {step.label || step.id}</option>)}
                      </select>
                    )}
                    {renderMemoryValue(propertyKey, section.value)}
                    <StateValuePropertyEditor value={propertiesFor(propertyKey, "workflow_state")} onChange={(value) => setPropertiesFor(propertyKey, value)} />
                  </div>
                </ThreeStateAccordionMember>
              );
            })}
        <ThreeStateAccordionMember
          stackId="right-stack"
          label="DETECTED OBJECTS"
          value={`${objects.length} persisted records`}
          detail={`selected run ${run.id.slice(0, 8)}`}
          mode={objectsListDisplayMode}
          onChange={setObjectsListDisplayMode}
          baseClass="detected-objects-window"
          scrollSize="280px"
          itemHeader={<><b>Global pre-fill</b><small>{objects.length} persisted records</small></>}
          accessories={<div
            className="object-view-switch"
            role="group"
            aria-label="Detected objects view"
          >
            <button
              className={objectView === "list" ? "active" : ""}
              onClick={() => setObjectView("list")}
            >
              List
            </button>
            <button
              className={objectView === "tiles" ? "active" : ""}
              onClick={() => setObjectView("tiles")}
            >
              Tiles
            </button>
          </div>}
          footer={<><b>{objects.length}</b><span>persisted object records · {objectView} view</span></>}
        >
        <div className="detected-objects-configuration">
          <StateValuePropertyEditor
            value={propertiesFor("objects")}
            onChange={(value) => setPropertiesFor("objects", value)}
          />
        </div>
        {objects.length ? (
          <div className={`workflow-run-object-list ${objectView}`}>
            {objects.map(({ artifact, record }, index) => {
              const key = `object:${artifact.id}:${index}`;
              return (
                <article key={key}>
                  <span>{index + 1}</span>
                  <div>
                    <b>
                      {String(
                        record.label ||
                          record.name ||
                          record.id ||
                          `Object ${index + 1}`,
                      )}
                    </b>
                    <small>
                      {String(
                        record.type ||
                          record.kind ||
                          artifact.datatype ||
                          "Object",
                      )}
                    </small>
                    <select
                      aria-label={`View object ${index + 1}`}
                      value={memoryViews[key] || "metta"}
                      onChange={(event) =>
                        setMemoryView(
                          key,
                          event.target.value as MemoryValueView,
                        )
                      }
                    >
                      <option value="guess">Guess</option>
                      <option value="image">Image</option>
                      <option value="metta">MeTTa</option>
                      <option value="json">JSON</option>
                      <option value="text">Small textbox</option>
                    </select>
                  </div>
                  {renderMemoryValue(key, record, artifact)}
                  <StateValuePropertyEditor
                    value={propertiesFor(
                      key,
                      artifact.datatype || artifact.representation || "",
                    )}
                    onChange={(value) => setPropertiesFor(key, value)}
                  />
                  {onOpenResource && artifact.datatype && (
                    <button
                      onClick={() =>
                        onOpenResource("datatype", artifact.datatype!)
                      }
                    >
                      Open datatype
                    </button>
                  )}
                </article>
              );
            })}
          </div>
        ) : (
          <div className="studio-empty">
            This selected run has no persisted detected-object records yet.
          </div>
        )}
        </ThreeStateAccordionMember>
      </>, rightColumnAccordionHost)}
    </>
  );
}

type RuntimeResourceKind =
  | "operation"
  | "model"
  | "datatype"
  | "goal"
  | "plan"
  | "context";
type OpenRuntimeResource = (kind: RuntimeResourceKind, id: string) => void;

type WorkflowRunCommand = "pause" | "resume" | "advance" | "replay" | "cancel";

function WorkflowRunProjection({
  run,
  workflow,
  busy,
  onCommand,
  onOpenResource,
  commands = ["pause", "resume", "advance", "replay", "cancel"],
}: {
  run: RuntimeRun;
  workflow: FrozenWorkflow | null;
  busy: boolean;
  onCommand: (command: WorkflowRunCommand) => void;
  onOpenResource?: OpenRuntimeResource;
  commands?: WorkflowRunCommand[];
}) {
  const initialParameters = new URLSearchParams(window.location.search);
  const initialView =
    initialParameters.get("runView") === "chronology"
      ? "chronology"
      : "topology";
  const [view, setViewState] = useState<"topology" | "chronology">(initialView);
  const setView = (next: "topology" | "chronology") => {
    setViewState(next);
    const url = new URL(window.location.href);
    if (next === "topology") url.searchParams.delete("runView");
    else url.searchParams.set("runView", next);
    replaceWorkbenchLocation(
      url,
      next === "topology" ? "Run Topology" : "Run Chronology",
    );
  };
  const initialSelectionMatchesRun =
    initialParameters.get("run") === run.id || !initialParameters.has("run");
  const [selectedStepId, setSelectedStepId] = useState(
    initialSelectionMatchesRun ? initialParameters.get("runStep") || "" : "",
  );
  const [selectedEventId, setSelectedEventId] = useState(
    initialSelectionMatchesRun ? initialParameters.get("runEvent") || "" : "",
  );
  const steps = workflow?.steps || [];
  const selectedStep =
    steps.find((step) => step.id === selectedStepId) || steps[0];
  const selectedEvent = run.events.find(
    (event) => String(event.id) === selectedEventId,
  );
  const persistProjectionSelection = (stepId: string, eventId = "") => {
    const url = new URL(window.location.href);
    if (stepId) url.searchParams.set("runStep", stepId);
    else url.searchParams.delete("runStep");
    if (eventId) url.searchParams.set("runEvent", eventId);
    else url.searchParams.delete("runEvent");
    replaceWorkbenchLocation(
      url,
      eventId ? `Event ${eventId}` : `Step ${stepId}`,
    );
  };
  const selectStep = (stepId: string) => {
    setSelectedStepId(stepId);
    setSelectedEventId("");
    persistProjectionSelection(stepId);
  };
  const selectEvent = (event: RuntimeRun["events"][number]) => {
    const stepId = event.stepId || selectedStepId;
    setSelectedEventId(String(event.id));
    if (event.stepId) setSelectedStepId(event.stepId);
    persistProjectionSelection(stepId, String(event.id));
  };
  useEffect(() => {
    const parameters = new URLSearchParams(window.location.search);
    const matchesRun =
      parameters.get("run") === run.id || !parameters.has("run");
    setSelectedStepId(matchesRun ? parameters.get("runStep") || "" : "");
    setSelectedEventId(matchesRun ? parameters.get("runEvent") || "" : "");
  }, [run.id]);
  const width = Math.max(760, steps.length * 180);
  const positions = new Map(
    steps.map((step, index) => [
      step.id,
      { x: 95 + index * 170, y: 75 + (index % 2) * 105 },
    ]),
  );
  const chronologyWidth = Math.max(760, run.events.length * 135 + 90);
  const chronologyPositions = run.events.map((_event, index) => ({
    x: 65 + index * 135,
    y: 82 + (index % 3) * 62,
  }));
  const stepRuntime = selectedStep
    ? run.steps.find((item) => item.stepId === selectedStep.id)
    : undefined;
  const artifacts = run.artifacts.filter(
    (item) => !selectedStep || !item.stepId || item.stepId === selectedStep.id,
  );
  const logs = run.logs.filter(
    (item) => !selectedStep || item.stepId === selectedStep.id,
  );
  const stepEvents = run.events.filter(
    (event) => !selectedStep || event.stepId === selectedStep.id,
  );
  const latestStepEvent = stepEvents.at(-1);
  const visualArtifacts = run.artifacts.filter((item) =>
    visualArtifactPayload(item.payload),
  );
  const sourceVisual =
    visualArtifacts.find((item) =>
      /source|input|before|observation/i.test(item.name),
    ) || visualArtifacts[0];
  const renderedVisual =
    visualArtifacts.find(
      (item) =>
        item.id !== sourceVisual?.id &&
        /render|reconstruct|output|after|result/i.test(item.name),
    ) || visualArtifacts.find((item) => item.id !== sourceVisual?.id);
  const hypothesisRecords = run.artifacts
    .filter((item) => /hypothesis/i.test(`${item.datatype || ""} ${item.name}`))
    .flatMap((item) => artifactRecords(item, ["hypotheses", "items"]));
  const evidenceRecords = run.artifacts
    .filter((item) => /evidence/i.test(`${item.datatype || ""} ${item.name}`))
    .flatMap((item) => artifactRecords(item, ["evidence", "items"]));
  const experimentRecords = run.artifacts
    .filter((item) => /experiment/i.test(`${item.datatype || ""} ${item.name}`))
    .flatMap((item) =>
      artifactRecords(item, ["experiments", "suggestedExperiments", "items"]),
    );
  const objectRecords = run.artifacts.flatMap((artifact) =>
    objectArtifactRecords(artifact).map((record) => ({ artifact, record })),
  );
  const totalSteps = Math.max(steps.length, run.steps.length);
  const completedSteps = run.steps.filter(
    (item) => item.status === "completed",
  ).length;
  const activeSteps = run.steps.filter((item) =>
    ["running", "waiting", "paused"].includes(item.status),
  ).length;
  const failedSteps = run.steps.filter(
    (item) => item.status === "failed",
  ).length;
  const completionPercent = totalSteps
    ? Math.round((completedSteps / totalSteps) * 100)
    : run.status === "completed"
      ? 100
      : 0;

  return (
    <section
      className="run-projection"
      aria-label="Selected workflow run projection"
    >
      <div className="run-projection-heading">
        <div>
          <span>FROZEN WORKFLOW v{run.workflowVersion}</span>
          <h2>{workflow?.label || run.workflowId}</h2>
          <small>
            {run.id} · {run.status} · {run.events.length} durable events
          </small>
        </div>
        <div
          className="run-projection-modes"
          role="group"
          aria-label="Workflow run view"
        >
          <button
            className={view === "topology" ? "active" : ""}
            onClick={() => setView("topology")}
          >
            Topology
          </button>
          <button
            className={view === "chronology" ? "active" : ""}
            onClick={() => setView("chronology")}
          >
            Chronology
          </button>
        </div>
      </div>
      <div className="run-command-controls">
        <span>RUN CONTROL</span>
        {commands.includes("pause") && (
          <button
            disabled={busy || run.status !== "running"}
            onClick={() => onCommand("pause")}
          >
            Pause
          </button>
        )}
        {commands.includes("resume") && (
          <button
            disabled={busy || run.status !== "paused"}
            onClick={() => onCommand("resume")}
          >
            Resume
          </button>
        )}
        {commands.includes("advance") && (
          <button
            disabled={
              busy ||
              [
                "waiting",
                "paused",
                "completed",
                "failed",
                "cancelled",
              ].includes(run.status)
            }
            onClick={() => onCommand("advance")}
          >
            Advance
          </button>
        )}
        {commands.includes("replay") && (
          <button disabled={busy} onClick={() => onCommand("replay")}>
            Replay as new run
          </button>
        )}
        {commands.includes("cancel") && (
          <button
            className="danger"
            disabled={
              busy || ["completed", "failed", "cancelled"].includes(run.status)
            }
            onClick={() => onCommand("cancel")}
          >
            Cancel
          </button>
        )}
      </div>
      <div
        className={`run-health-strip ${failedSteps ? "unhealthy" : run.status}`}
      >
        <div className="run-health-heading">
          <span>RUN HEALTH</span>
          <b>{run.status}</b>
          <strong>{completionPercent}%</strong>
        </div>
        <div
          className="run-health-progress"
          role="progressbar"
          aria-label="Workflow completion"
          aria-valuemin={0}
          aria-valuemax={100}
          aria-valuenow={completionPercent}
        >
          <i style={{ width: `${completionPercent}%` }} />
        </div>
        <dl>
          <div>
            <dt>Completed</dt>
            <dd>
              {completedSteps} / {totalSteps}
            </dd>
          </div>
          <div>
            <dt>Active</dt>
            <dd>{activeSteps}</dd>
          </div>
          <div>
            <dt>Failures</dt>
            <dd>{failedSteps}</dd>
          </div>
          <div>
            <dt>Durable events</dt>
            <dd>{run.events.length}</dd>
          </div>
          <div>
            <dt>Artifacts</dt>
            <dd>{run.artifacts.length}</dd>
          </div>
          <div>
            <dt>Logs</dt>
            <dd>{run.logs.length}</dd>
          </div>
        </dl>
      </div>
      {view === "topology" ? (
        workflow ? (
          <div className="run-topology-scroll">
            <svg
              className="run-topology"
              viewBox={`0 0 ${width} 270`}
              style={{ minWidth: width }}
            >
              <defs>
                <marker
                  id={`run-arrow-${run.id}`}
                  viewBox="0 0 10 10"
                  refX="9"
                  refY="5"
                  markerWidth="7"
                  markerHeight="7"
                  orient="auto"
                >
                  <path d="M0 0L10 5L0 10z" />
                </marker>
              </defs>
              {steps.flatMap((step) =>
                (step.dependsOn || []).map((parentId) => {
                  const parent = positions.get(parentId),
                    child = positions.get(step.id);
                  if (!parent || !child) return null;
                  const mid = (parent.x + child.x) / 2;
                  return (
                    <path
                      key={`${parentId}:${step.id}`}
                      className="run-topology-edge"
                      d={`M${parent.x + 57},${parent.y} C${mid},${parent.y} ${mid},${child.y} ${child.x - 57},${child.y}`}
                      markerEnd={`url(#run-arrow-${run.id})`}
                    />
                  );
                }),
              )}
              {steps.map((step, index) => {
                const position = positions.get(step.id)!;
                const status =
                  run.steps.find((item) => item.stepId === step.id)?.status ||
                  "defined";
                return (
                  <g
                    key={step.id}
                    transform={`translate(${position.x - 60},${position.y - 35})`}
                    className={`run-topology-node ${status} ${selectedStep?.id === step.id ? "selected" : ""}`}
                    role="button"
                    tabIndex={0}
                    onClick={() => selectStep(step.id)}
                    onKeyDown={(event) => {
                      if (event.key === "Enter" || event.key === " ")
                        selectStep(step.id);
                    }}
                  >
                    <rect width="120" height="70" rx="8" />
                    <text
                      x="60"
                      y="19"
                      textAnchor="middle"
                      className="node-index"
                    >
                      {index + 1}
                    </text>
                    <text
                      x="60"
                      y="38"
                      textAnchor="middle"
                      className="node-title"
                    >
                      {step.label || step.id}
                    </text>
                    <text
                      x="60"
                      y="57"
                      textAnchor="middle"
                      className="node-status"
                    >
                      {status}
                    </text>
                  </g>
                );
              })}
            </svg>
          </div>
        ) : (
          <div className="studio-empty">
            The persisted workflow definition is unavailable.
          </div>
        )
      ) : (
        <div
          className="run-chronology-scroll"
          aria-label="Durable event chronology"
        >
          {run.events.length ? (
            <svg
              className="run-chronology"
              viewBox={`0 0 ${chronologyWidth} 280`}
              style={{ minWidth: chronologyWidth }}
            >
              <defs>
                <marker
                  id={`chronology-arrow-${run.id}`}
                  viewBox="0 0 10 10"
                  refX="9"
                  refY="5"
                  markerWidth="6"
                  markerHeight="6"
                  orient="auto"
                >
                  <path d="M0 0L10 5L0 10z" />
                </marker>
              </defs>
              {run.events.slice(1).map((event, index) => {
                const from = chronologyPositions[index],
                  to = chronologyPositions[index + 1],
                  midpoint = (from.x + to.x) / 2;
                return (
                  <path
                    key={`event-edge:${event.id}`}
                    className="run-chronology-edge"
                    d={`M${from.x + 22},${from.y} C${midpoint},${from.y} ${midpoint},${to.y} ${to.x - 22},${to.y}`}
                    markerEnd={`url(#chronology-arrow-${run.id})`}
                  />
                );
              })}
              {run.events.map((event, index) => {
                const point = chronologyPositions[index],
                  selected = String(event.id) === selectedEventId,
                  state = /fail|error|cancel/i.test(event.kind)
                    ? "failed"
                    : /wait|human/i.test(event.kind)
                      ? "waiting"
                      : /start|running|resume/i.test(event.kind)
                        ? "running"
                        : "completed";
                return (
                  <g
                    key={event.id}
                    transform={`translate(${point.x},${point.y})`}
                    className={`run-chronology-node ${state} ${selected ? "selected" : ""}`}
                    role="button"
                    tabIndex={0}
                    aria-label={`${index + 1}. ${event.kind}, ${event.stepId || "workflow"}, ${stamp(event.createdAt)}`}
                    onClick={() => selectEvent(event)}
                    onKeyDown={(keyboardEvent) => {
                      if (
                        keyboardEvent.key === "Enter" ||
                        keyboardEvent.key === " "
                      )
                        selectEvent(event);
                    }}
                  >
                    <circle r="22" />
                    <text className="event-index" textAnchor="middle" y="3">
                      {index + 1}
                    </text>
                    <text className="event-kind" textAnchor="middle" y="38">
                      {event.kind.length > 20
                        ? `${event.kind.slice(0, 18)}…`
                        : event.kind}
                    </text>
                    <text className="event-step" textAnchor="middle" y="50">
                      {event.stepId || "workflow"}
                    </text>
                  </g>
                );
              })}
            </svg>
          ) : (
            <div className="studio-empty">This run has no durable events.</div>
          )}
        </div>
      )}
      {selectedStep && (
        <div className="run-stage-narrative">
          <div>
            <span>SELECTED STAGE</span>
            <h3>{selectedStep.label || selectedStep.id}</h3>
            <p>
              {selectedStep.implementation ||
                selectedStep.operation ||
                selectedStep.kind ||
                "operation"}
            </p>
            {selectedStep.operation && onOpenResource && (
              <button
                type="button"
                className="runtime-resource-link"
                onClick={() =>
                  onOpenResource("operation", selectedStep.operation!)
                }
              >
                Open Operation · {selectedStep.operation}
              </button>
            )}
          </div>
          <div>
            <span>RUNTIME OUTCOME</span>
            <b>{stepRuntime?.status || "defined"}</b>
            <small>
              {stepRuntime?.error ||
                latestStepEvent?.kind ||
                "No execution event yet"}
            </small>
          </div>
          <div>
            <span>DURABLE EVIDENCE</span>
            <b>
              {artifacts.length} artifacts · {stepEvents.length} events
            </b>
            <small>
              {artifacts.map((item) => item.name).join(", ") ||
                "No produced artifacts"}
            </small>
          </div>
        </div>
      )}
      {sourceVisual && (
        <div
          className={`run-visual-comparison ${renderedVisual ? "paired" : "single"}`}
        >
          <div className="run-visual-comparison-title">
            <span>
              {renderedVisual
                ? "SOURCE / RENDER COMPARISON"
                : "VISUAL ARTIFACT"}
            </span>
            <small>Persisted run payloads · no generated preview data</small>
          </div>
          <ArtifactVisual artifact={sourceVisual} />
          {renderedVisual && <ArtifactVisual artifact={renderedVisual} />}
        </div>
      )}
      {objectRecords.length > 0 && (
        <div className="run-detected-objects">
          <div className="run-visual-comparison-title">
            <span>DETECTED OBJECTS</span>
            <small>{objectRecords.length} persisted object records</small>
          </div>
          {objectRecords.map(({ artifact, record }, index) => {
            const representationId = String(
              record.representation || artifact.representation || "",
            );
            const operationId = String(
              record.operationId || artifact.provenance?.operationId || "",
            );
            const modelId = String(
              record.modelId || artifact.provenance?.modelId || "",
            );
            return (
              <article key={`${artifact.id}:${String(record.id || index)}`}>
                <span>{index + 1}</span>
                <div>
                  <b>
                    {String(
                      record.label ||
                        record.name ||
                        record.id ||
                        `Object ${index + 1}`,
                    )}
                  </b>
                  <small>
                    {String(
                      record.type ||
                        record.kind ||
                        artifact.datatype ||
                        "Object",
                    )}
                    {typeof record.confidence === "number"
                      ? ` · confidence ${record.confidence.toFixed(2)}`
                      : ""}
                  </small>
                </div>
                {onOpenResource && (
                  <div className="runtime-resource-links">
                    {representationId && (
                      <button
                        type="button"
                        onClick={() =>
                          onOpenResource("datatype", representationId)
                        }
                      >
                        Representation · {representationId}
                      </button>
                    )}
                    {operationId && (
                      <button
                        type="button"
                        onClick={() => onOpenResource("operation", operationId)}
                      >
                        Operation · {operationId}
                      </button>
                    )}
                    {modelId && (
                      <button
                        type="button"
                        onClick={() => onOpenResource("model", modelId)}
                      >
                        Model · {modelId}
                      </button>
                    )}
                  </div>
                )}
              </article>
            );
          })}
        </div>
      )}
      {(hypothesisRecords.length > 0 ||
        evidenceRecords.length > 0 ||
        experimentRecords.length > 0) && (
        <div className="run-reasoning-evidence">
          <div className="run-visual-comparison-title">
            <span>REASONING EVIDENCE</span>
            <small>Typed artifacts persisted by this run</small>
          </div>
          {hypothesisRecords.map((record, index) => (
            <article
              className="run-hypothesis"
              key={`hypothesis:${String(record.id || index)}`}
            >
              <span>H{index + 1}</span>
              <div>
                <b>
                  {String(
                    record.statement ||
                      record.label ||
                      record.id ||
                      "Hypothesis",
                  )}
                </b>
                <small>{String(record.status || "revisable")}</small>
              </div>
              {typeof record.confidence === "number" && (
                <strong>{record.confidence.toFixed(2)}</strong>
              )}
            </article>
          ))}
          {evidenceRecords.map((record, index) => (
            <article
              className="run-evidence-record"
              key={`evidence:${String(record.id || index)}`}
            >
              <span>E{index + 1}</span>
              <div>
                <b>
                  {String(
                    record.observation ||
                      record.statement ||
                      record.id ||
                      "Evidence",
                  )}
                </b>
                <small>
                  {Array.isArray(record.supports)
                    ? `supports ${record.supports.join(", ")}`
                    : "transition evidence"}
                </small>
              </div>
            </article>
          ))}
          {experimentRecords.map((record, index) => (
            <article
              className="run-experiment"
              key={`experiment:${String(record.id || index)}`}
            >
              <span>TRY</span>
              <div>
                <b>
                  {String(
                    record.instruction ||
                      record.label ||
                      record.id ||
                      "Suggested experiment",
                  )}
                </b>
                <small>
                  {String(record.rationale || "Persisted experiment proposal")}
                </small>
              </div>
              {typeof record.expectedInformationGain === "number" && (
                <strong>{record.expectedInformationGain.toFixed(2)}</strong>
              )}
            </article>
          ))}
        </div>
      )}
      <div className="run-projection-inspector">
        <div>
          <span>{selectedEvent ? "EVENT" : "STEP"}</span>
          <h3>
            {selectedEvent?.kind ||
              selectedStep?.label ||
              selectedStep?.id ||
              "Select a node"}
          </h3>
          <p>
            {selectedEvent?.stepId ||
              selectedStep?.implementation ||
              selectedStep?.operation ||
              selectedStep?.kind ||
              "workflow"}
          </p>
        </div>
        <dl>
          <div>
            <dt>Status</dt>
            <dd>{stepRuntime?.status || run.status}</dd>
          </div>
          <div>
            <dt>Attempt</dt>
            <dd>{stepRuntime?.attempt || 0}</dd>
          </div>
          <div>
            <dt>Artifacts</dt>
            <dd>{artifacts.length}</dd>
          </div>
          <div>
            <dt>Logs</dt>
            <dd>{logs.length}</dd>
          </div>
        </dl>
        {selectedEvent && (
          <pre>{jsonValueToMetta(selectedEvent.payload || {})}</pre>
        )}
        {!selectedEvent && selectedStep && (
          <>
            <details>
              <summary>Step contract</summary>
              <pre>
                {jsonValueToMetta({
                  inputs: selectedStep.inputs || {},
                  outputs: selectedStep.outputs || {},
                })}
              </pre>
            </details>
            {artifacts.map((item) => {
              const operationId = String(item.provenance?.operationId || "");
              const modelId = String(item.provenance?.modelId || "");
              const datatypeId = String(item.datatype || "");
              const representationId = String(item.representation || "");
              return (
                <details key={item.id}>
                  <summary>
                    Artifact · {item.name} · {item.datatype || "Any"}
                    {representationId ? ` / ${representationId}` : ""}
                    {item.redacted ? " · REDACTED" : ""}
                  </summary>
                  <pre>{jsonValueToMetta(item.payload)}</pre>
                  <dl className="artifact-provenance">
                    <div>
                      <dt>Content hash</dt>
                      <dd>{item.contentHash || "unavailable"}</dd>
                    </div>
                    <div>
                      <dt>Provenance</dt>
                      <dd>{jsonValueToMetta(item.provenance || {})}</dd>
                    </div>
                  </dl>
                  {onOpenResource && (
                    <div className="runtime-resource-links">
                      {datatypeId && !/^any$/i.test(datatypeId) && (
                        <button
                          type="button"
                          onClick={() => onOpenResource("datatype", datatypeId)}
                        >
                          Open Datatype · {datatypeId}
                        </button>
                      )}
                      {representationId && (
                        <button
                          type="button"
                          onClick={() =>
                            onOpenResource("datatype", representationId)
                          }
                        >
                          Open Representation · {representationId}
                        </button>
                      )}
                      {operationId && (
                        <button
                          type="button"
                          onClick={() =>
                            onOpenResource("operation", operationId)
                          }
                        >
                          Open producing Operation · {operationId}
                        </button>
                      )}
                      {modelId && (
                        <button
                          type="button"
                          onClick={() => onOpenResource("model", modelId)}
                        >
                          Open producing Model · {modelId}
                        </button>
                      )}
                    </div>
                  )}
                </details>
              );
            })}
            {logs.map((item) => (
              <details key={item.id}>
                <summary>{item.stream} log</summary>
                <pre>{item.message}</pre>
              </details>
            ))}
          </>
        )}
      </div>
    </section>
  );
}

export function HumanInputForm({
  step,
  busy,
  draft,
  onDraft,
  onSubmit,
}: {
  step?: WorkflowStep;
  busy: boolean;
  draft: Record<string, unknown>;
  onDraft: (values: Record<string, unknown>) => void;
  onSubmit: (values: Record<string, unknown>) => void;
}) {
  const fields = Object.entries(step?.form || {});
  const initial = () =>
    Object.fromEntries(
      fields.map(([name, spec]) => [
        name,
        draft[name] ??
          spec.default ??
          (/boolean/i.test(spec.type || "") ? false : ""),
      ]),
    );
  const [values, setValues] = useState<Record<string, unknown>>(initial);
  useEffect(() => setValues(initial()), [step?.id, JSON.stringify(draft)]);
  const update = (name: string, value: unknown) =>
    setValues((current) => {
      const next = { ...current, [name]: value };
      onDraft(next);
      return next;
    });
  if (!fields.length)
    return (
      <div className="human-input-contract">
        <p>
          This step has no form contract. Submit a JSON object in the advanced
          editor.
        </p>
        <textarea
          className="raw-json-editor"
          defaultValue="{}"
          onChange={(event) => {
            try {
              setValues(JSON.parse(event.target.value));
            } catch {
              /* keep the last valid value */
            }
          }}
        />
        <button
          className="run-button"
          disabled={busy}
          onClick={() => onSubmit(values)}
        >
          Submit human input
        </button>
      </div>
    );
  return (
    <div className="human-input-contract">
      {fields.map(([name, spec]) => {
        const type = String(spec.type || "Text");
        const label = spec.label || name.replaceAll("_", " ");
        if (/boolean/i.test(type))
          return (
            <label key={name} className="human-boolean">
              <input
                type="checkbox"
                checked={Boolean(values[name])}
                onChange={(event) => update(name, event.target.checked)}
              />
              <span>
                <b>{label}</b>
                <small>{spec.description || type}</small>
              </span>
            </label>
          );
        if (spec.options?.length)
          return (
            <label key={name}>
              <span>
                {label} <em>{type}</em>
              </span>
              <select
                value={String(values[name] ?? "")}
                onChange={(event) => update(name, event.target.value)}
              >
                {spec.options.map((option) => (
                  <option key={String(option)} value={String(option)}>
                    {String(option)}
                  </option>
                ))}
              </select>
            </label>
          );
        if (spec.secret || spec.sensitive)
          return (
            <label key={name}>
              <span>
                {label} <em>secret · not saved</em>
              </span>
              <input
                type="password"
                value={String(values[name] ?? "")}
                onChange={(event) => update(name, event.target.value)}
              />
              <small>{spec.description}</small>
            </label>
          );
        if (/image|bitmap|raster/i.test(type))
          return (
            <label key={name} className="human-image-field">
              <span>
                {label} <em>{type}</em>
              </span>
              <input
                type="file"
                accept="image/*"
                onChange={(event) => {
                  const file = event.target.files?.[0];
                  if (!file) return;
                  const reader = new FileReader();
                  reader.onload = () =>
                    update(name, {
                      dataUrl: String(reader.result),
                      name: file.name,
                      mimeType: file.type,
                      size: file.size,
                    });
                  reader.readAsDataURL(file);
                }}
              />
              {visualArtifactPayload(values[name])?.image && (
                <img
                  src={visualArtifactPayload(values[name])!.image}
                  alt={`${label} preview`}
                />
              )}
              <small>
                {spec.description ||
                  "Choose an image; the preview and payload use the original file."}
              </small>
            </label>
          );
        if (/grid|matrix/i.test(type)) {
          const visual = visualArtifactPayload(values[name]);
          return (
            <label key={name} className="human-grid-field">
              <span>
                {label} <em>{type}</em>
              </span>
              <textarea
                value={
                  typeof values[name] === "string"
                    ? String(values[name])
                    : JSON.stringify(values[name] ?? [], null, 2)
                }
                onChange={(event) => {
                  try {
                    update(name, JSON.parse(event.target.value));
                  } catch {
                    update(name, event.target.value);
                  }
                }}
              />
              {visual?.grid && (
                <div
                  className="human-grid-preview"
                  style={{
                    gridTemplateColumns: `repeat(${visual.grid[0]?.length || 1}, 1fr)`,
                  }}
                >
                  {visual.grid.flatMap((row, rowIndex) =>
                    row.map((cell, columnIndex) => (
                      <i
                        key={`${rowIndex}:${columnIndex}`}
                        style={{
                          background:
                            artifactColors[
                              Math.abs(cell) % artifactColors.length
                            ],
                        }}
                      />
                    )),
                  )}
                </div>
              )}
              <small>
                {spec.description ||
                  "Enter a rectangular JSON matrix of numeric color indexes."}
              </small>
            </label>
          );
        }
        return (
          <label key={name}>
            <span>
              {label} <em>{type}</em>
            </span>
            <textarea
              value={
                typeof values[name] === "string"
                  ? String(values[name])
                  : JSON.stringify(values[name] ?? "")
              }
              onChange={(event) => {
                const raw = event.target.value;
                let value: unknown = raw;
                if (/number|integer|float/i.test(type))
                  value = raw === "" ? null : Number(raw);
                else if (/object|map|list|array|any/i.test(type)) {
                  try {
                    value = JSON.parse(raw);
                  } catch {
                    value = raw;
                  }
                }
                update(name, value);
              }}
            />
            <small>{spec.description}</small>
          </label>
        );
      })}
      <button
        className="run-button"
        disabled={busy}
        onClick={() => onSubmit(values)}
      >
        Submit human input
      </button>
    </div>
  );
}

function WorkflowInputsEditor({
  workflowId,
  contract,
  source,
  onSource,
}: {
  workflowId: string;
  contract: Record<string, WorkflowInputContract>;
  source: string;
  onSource: (source: string) => void;
}) {
  const entries = Object.entries(contract);
  const label = (value: WorkflowInputContract) =>
    typeof value === "string"
      ? value
      : String(value.datatype || value.type || "Any");
  const isText = (value: WorkflowInputContract) =>
    /text|string|markdown|natural.?language/i.test(label(value));
  const parseSource = () => {
    try {
      const value = JSON.parse(source);
      return value && typeof value === "object" && !Array.isArray(value)
        ? (value as Record<string, unknown>)
        : {};
    } catch {
      return {};
    }
  };
  const rawValue = (value: unknown, spec: WorkflowInputContract) =>
    value === undefined
      ? ""
      : isText(spec) && typeof value === "string"
        ? value
        : JSON.stringify(value, null, 2);
  const initialDrafts = () => {
    const values = parseSource();
    return Object.fromEntries(
      entries.map(([name, spec]) => [
        name,
        rawValue(
          values[name] ?? (typeof spec === "object" ? spec.default : undefined),
          spec,
        ),
      ]),
    );
  };
  const [drafts, setDrafts] = useState<Record<string, string>>(initialDrafts);
  const [fieldError, setFieldError] = useState("");
  useEffect(() => {
    setDrafts(initialDrafts());
    setFieldError("");
  }, [workflowId]);
  const materialize = (next: Record<string, string>) =>
    Object.fromEntries(
      entries.map(([name, spec]) => {
        const raw = next[name] || "";
        const options = typeof spec === "object" ? spec.options : undefined;
        const selectedOption = options?.find(
          (option) =>
            (typeof option === "string" ? option : JSON.stringify(option)) ===
            raw,
        );
        if (selectedOption !== undefined) return [name, selectedOption];
        if (isText(spec)) return [name, raw];
        if (/^any$/i.test(label(spec))) {
          try {
            return [name, JSON.parse(raw)];
          } catch {
            return [name, raw];
          }
        }
        if (!raw.trim()) return [name, null];
        try {
          return [name, JSON.parse(raw)];
        } catch {
          throw new Error(`${name} (${label(spec)}) must be valid JSON.`);
        }
      }),
    );
  const update = (name: string, value: string) => {
    const next = { ...drafts, [name]: value };
    setDrafts(next);
    try {
      onSource(JSON.stringify(materialize(next), null, 2));
      setFieldError("");
    } catch (reason) {
      setFieldError(reason instanceof Error ? reason.message : String(reason));
    }
  };
  if (!entries.length) return null;
  return (
    <div className="goal-workflow-inputs">
      <div className="llm-subhead">
        <div>
          <span>WORKFLOW INPUT CONTRACT</span>
          <b>{workflowId}</b>
          <small>
            Datatype-aware fields update the advanced JSON source below.
          </small>
        </div>
      </div>
      <div className="workflow-fields">
        {entries.map(([name, spec]) => {
          const type = label(spec),
            options = typeof spec === "object" ? spec.options : undefined;
          return (
            <label key={name}>
              <span>
                {name} <em>{type}</em>
              </span>
              {options?.length ? (
                <select
                  value={drafts[name] || ""}
                  onChange={(event) => update(name, event.target.value)}
                >
                  {options.map((option) => (
                    <option
                      key={JSON.stringify(option)}
                      value={
                        typeof option === "string"
                          ? option
                          : JSON.stringify(option)
                      }
                    >
                      {String(option)}
                    </option>
                  ))}
                </select>
              ) : /boolean/i.test(type) ? (
                <input
                  type="checkbox"
                  checked={drafts[name] === "true"}
                  onChange={(event) =>
                    update(name, String(event.target.checked))
                  }
                />
              ) : /number|integer|float|double/i.test(type) ? (
                <input
                  type="number"
                  value={drafts[name] || ""}
                  onChange={(event) => update(name, event.target.value)}
                />
              ) : (
                <textarea
                  value={drafts[name] || ""}
                  placeholder={
                    isText(spec) ? `Enter ${name}…` : `Enter ${type} as JSON…`
                  }
                  onChange={(event) => update(name, event.target.value)}
                />
              )}
            </label>
          );
        })}
      </div>
      {fieldError && <div className="validation bad">{fieldError}</div>}
    </div>
  );
}

function RuntimeRecordInspector({
  row,
  onOpenResource,
}: {
  row: RuntimeHistoryRow;
  onOpenResource?: OpenRuntimeResource;
}) {
  const artifact =
    row.recordKind === "state artifact"
      ? (row.record as RuntimeRun["artifacts"][number])
      : undefined;
  const context =
    row.recordKind === "runtime context" ? (row.record as GoalRun) : undefined;
  return (
    <section
      className="run-projection-inspector"
      aria-label="Selected durable runtime record"
    >
      <div>
        <span>DURABLE {row.recordKind.toUpperCase()}</span>
        <h3>{row.a}</h3>
        <p>
          Run {row.run.id} · {row.run.workflowId}
        </p>
        {artifact && onOpenResource && (
          <div className="runtime-resource-links">
            {artifact.datatype && (
              <button
                type="button"
                onClick={() => onOpenResource("datatype", artifact.datatype!)}
              >
                Datatype · {artifact.datatype}
              </button>
            )}
            {artifact.representation && (
              <button
                type="button"
                onClick={() =>
                  onOpenResource("datatype", artifact.representation!)
                }
              >
                Representation · {artifact.representation}
              </button>
            )}
            {Boolean(artifact.provenance?.operationId) && (
              <button
                type="button"
                onClick={() =>
                  onOpenResource(
                    "operation",
                    String(artifact.provenance?.operationId),
                  )
                }
              >
                Operation · {String(artifact.provenance?.operationId)}
              </button>
            )}
            {Boolean(artifact.provenance?.modelId) && (
              <button
                type="button"
                onClick={() =>
                  onOpenResource("model", String(artifact.provenance?.modelId))
                }
              >
                Model · {String(artifact.provenance?.modelId)}
              </button>
            )}
          </div>
        )}
      </div>
      {context && onOpenResource && (
        <div className="runtime-resource-links">
          {context.contextId && (
            <button
              type="button"
              onClick={() => onOpenResource("context", context.contextId!)}
            >
              AtomSpace · {context.contextId}
            </button>
          )}
          {context.contextVariantId && (
            <button
              type="button"
              onClick={() =>
                onOpenResource("context", context.contextVariantId!)
              }
            >
              Resolved alternative · {context.contextVariantId}
            </button>
          )}
        </div>
      )}
      <dl>
        <div>
          <dt>Record key</dt>
          <dd>{row.key}</dd>
        </div>
        <div>
          <dt>Status / type</dt>
          <dd>{row.b}</dd>
        </div>
        <div>
          <dt>Step / time</dt>
          <dd>{row.c}</dd>
        </div>
        <div>
          <dt>Run status</dt>
          <dd>{row.run.status}</dd>
        </div>
      </dl>
      <details open>
        <summary>Complete persisted record</summary>
        <pre>{jsonValueToMetta(row.record)}</pre>
      </details>
    </section>
  );
}

export function RuntimeHistoryView({
  mode,
  workspaceId,
  goals = [],
  plans = [],
  contexts = [],
  workflows = [],
  preflightStateValues = [],
  runLauncher,
  leftColumnDisplayMode,
  rightColumnDisplayMode,
  showDesignReference = true,
  onSelectRun,
  onOpenResource,
}: {
  mode: Mode;
  workspaceId: string;
  goals?: DocumentRecord[];
  plans?: DocumentRecord[];
  contexts?: DocumentRecord[];
  workflows?: DocumentRecord[];
  preflightStateValues?: BootstrappedStateValue[];
  runLauncher?: ReactNode;
  leftColumnDisplayMode?: AccordionDisplayMode;
  rightColumnDisplayMode?: AccordionDisplayMode;
  showDesignReference?: boolean;
  onSelectRun?: (run: RuntimeRun) => void;
  onOpenResource?: OpenRuntimeResource;
}) {
  const [runs, setRuns] = useState<RuntimeRun[]>([]),
    [goalRuns, setGoalRuns] = useState<GoalRun[]>([]);
  const [invocations, setInvocations] = useState<InvocationTrace[]>([]),
    [selectedInvocationId, setSelectedInvocationId] = useState("");
  const [selectedRecordKey, setSelectedRecordKey] = useState(
    () => runtimeRecordFromLocation(mode),
  );
  const [historyFilter, setHistoryFilter] = useState(""),
    [runLimit, setRunLimit] = useState(50),
    [goalRunLimit, setGoalRunLimit] = useState(50),
    [invocationLimit, setInvocationLimit] = useState(50);
  const [runStatusFilter, setRunStatusFilter] =
    useState<RunStatusFilter>("all");
  const [expandedPanel, setExpandedPanel] = useState<RunWorkspacePanel | null>(
    null,
  );
  const [workflowRunsDisplayMode, setWorkflowRunsDisplayMode] =
    useState<AccordionDisplayMode>("scroll");
  const [launcherDisplayMode, setLauncherDisplayMode] =
    useState<AccordionDisplayMode>("scroll");
  const [objectDisplayMode, setObjectDisplayMode] =
    useState<AccordionDisplayMode>("scroll");
  const [objectsListDisplayMode, setObjectsListDisplayMode] =
    useState<AccordionDisplayMode>("scroll");
  const [splineDisplayMode, setSplineDisplayMode] =
    useState<AccordionDisplayMode>("full");
  const [referenceDisplayMode, setReferenceDisplayMode] =
    useState<AccordionDisplayMode>("strip");
  const [rightColumnAccordionHost, setRightColumnAccordionHost] =
    useState<HTMLDivElement | null>(null);
  const setRightColumnDisplayMode = (nextMode: AccordionDisplayMode) => {
    setWorkflowRunsDisplayMode(nextMode);
    setObjectDisplayMode(nextMode);
    setObjectsListDisplayMode(nextMode);
  };
  useEffect(() => {
    if (leftColumnDisplayMode) setLauncherDisplayMode(leftColumnDisplayMode);
  }, [leftColumnDisplayMode]);
  useEffect(() => {
    if (rightColumnDisplayMode) setRightColumnDisplayMode(rightColumnDisplayMode);
  }, [rightColumnDisplayMode]);
  const [minimizedPanels, setMinimizedPanels] = useState<
    Set<RunWorkspacePanel>
  >(() => new Set());
  const setPanelMinimized = (panel: RunWorkspacePanel, minimized: boolean) =>
    setMinimizedPanels((current) => {
      const next = new Set(current);
      if (minimized) next.add(panel);
      else next.delete(panel);
      return next;
    });
  useEffect(() => {
    if (mode !== "workflowRuns") return;
    const toggleFromTitle = (event: MouseEvent) => {
      const target = event.target instanceof Element ? event.target : null;
      if (target?.closest(".durable-runs-accordion .panel-title-toggle")) {
        event.stopPropagation();
        setWorkflowRunsDisplayMode("strip");
        return;
      }
      const panel: RunWorkspacePanel | null = target?.closest(".workflow-runs-control .panel-title-toggle")
        ? "runs"
        : null;
      if (!panel) return;
      event.stopPropagation();
      setPanelMinimized(panel, !minimizedPanels.has(panel));
    };
    document.addEventListener("click", toggleFromTitle, true);
    return () => document.removeEventListener("click", toggleFromTitle, true);
  }, [mode, minimizedPanels]);
  const [selectedId, setSelectedId] = useState<string>(""),
    [error, setError] = useState<string>(""),
    [busy, setBusy] = useState(false);
  const [frozenWorkflow, setFrozenWorkflow] = useState<FrozenWorkflow | null>(
    null,
  );
  const goalDocs = useMemo(
    () =>
      goals.map((row) => row.document).filter(Boolean) as Record<string, any>[],
    [goals],
  );
  const planDocs = useMemo(
    () =>
      plans.map((row) => row.document).filter(Boolean) as Record<string, any>[],
    [plans],
  );
  const contextDocs = useMemo(
    () =>
      contexts.map((row) => row.document).filter(Boolean) as Record<
        string,
        any
      >[],
    [contexts],
  );
  const workflowIds = useMemo(
    () => new Set(workflows.map((row) => row.document?.id).filter(Boolean)),
    [workflows],
  );
  const isRootResource = (doc: Record<string, any>) =>
    !Array.isArray(doc.parents) || doc.parents.length === 0;
  const goalSpecs = goalDocs.filter(
    (doc) => doc.kind === "goal" && isRootResource(doc),
  );
  const planSpecs = planDocs.filter(
    (doc) =>
      (doc.kind === "planning_strategy" || doc.kind === "plan") &&
      isRootResource(doc),
  );
  const contextSpecs = contextDocs.filter(
    (doc) =>
      (doc.kind === "atomspace" || doc.kind === "context") &&
      isRootResource(doc),
  );
  const [goalId, setGoalId] = useState(""),
    [goalVariantId, setGoalVariantId] = useState("");
  const [planId, setPlanId] = useState(""),
    [planVariantId, setPlanVariantId] = useState("");
  const [contextId, setContextId] = useState(""),
    [contextVariantId, setContextVariantId] = useState("");
  const availablePlanSpecs = planSpecs.filter(
    (plan) =>
      (!goalId || (plan.goals || []).includes(goalId)) &&
      (plan.children || []).some((childId: string) =>
        workflowIds.has(planDocs.find((doc) => doc.id === childId)?.workflow),
      ),
  );
  const [inputs, setInputs] = useState("{}");
  const [humanDraft, setHumanDraft] = useState<Record<string, unknown>>({}),
    [draftLoaded, setDraftLoaded] = useState(false),
    [draftStatus, setDraftStatus] = useState(""),
    [humanDraftDirty, setHumanDraftDirty] = useState(false);
  const [workflowHumanDraft, setWorkflowHumanDraft] = useState<
      Record<string, unknown>
    >({}),
    [workflowDraftLoaded, setWorkflowDraftLoaded] = useState(false),
    [workflowDraftStatus, setWorkflowDraftStatus] = useState(""),
    [workflowDraftDirty, setWorkflowDraftDirty] = useState(false);
  const goalVariants = goalDocs.filter((doc) =>
    (doc.parents || []).includes(goalId),
  );
  const planVariants = planDocs.filter(
    (doc) =>
      (doc.parents || []).includes(planId) && workflowIds.has(doc.workflow),
  );
  const contextVariants = contextDocs.filter((doc) =>
    (doc.parents || []).includes(contextId),
  );
  const selectedPlanVariant = planVariants.find(
    (doc) => doc.id === planVariantId,
  );
  const selectedGoalWorkflow = workflows
    .map((row) => row.document)
    .find((doc) => doc?.id === selectedPlanVariant?.workflow) as
    | Record<string, any>
    | undefined;

  const refresh = async () => {
    setError("");
    try {
      const includeInvocations = mode === "execs" || mode === "logs";
      const includeGoalRuns = mode === "goalRuns" || mode === "runtimeContexts";
      const includeWorkflowRuns = !includeGoalRuns;
      const [runPayload, goalPayload, operationPayload, modelPayload] =
        await Promise.all([
          includeWorkflowRuns
            ? api(
                `/api/engine/runs?workspace_id=${encodeURIComponent(workspaceId)}&limit=${runLimit}`,
              )
            : Promise.resolve({ runs: [] }),
          includeGoalRuns
            ? api(
                `/api/goal-runs?workspace_id=${encodeURIComponent(workspaceId)}&limit=${goalRunLimit}`,
              )
            : Promise.resolve({ goalRuns: [] }),
          includeInvocations
            ? api(
                `/api/workspaces/${encodeURIComponent(workspaceId)}/operations/invocations?limit=${invocationLimit}`,
              )
            : Promise.resolve({ invocations: [] }),
          includeInvocations
            ? api(
                `/api/workspaces/${encodeURIComponent(workspaceId)}/models/invocations?limit=${invocationLimit}`,
              )
            : Promise.resolve({ invocations: [] }),
        ]);
      const normalizeRun = (run: RuntimeRun): RuntimeRun => ({
        ...run,
        steps: run.steps || [],
        events: run.events || [],
        artifacts: run.artifacts || [],
        logs: run.logs || [],
      });
      const loadedRuns = (runPayload.runs || []).map(normalizeRun);
      const locationParameters = new URLSearchParams(window.location.search);
      const requestedRunId =
        mode === "workflowRuns"
          ? locationParameters.get("run")
          : null;
      if (
        requestedRunId &&
        !loadedRuns.some((run: RuntimeRun) => run.id === requestedRunId)
      ) {
        const requestedPayload = await api(
          `/api/engine/runs/${encodeURIComponent(requestedRunId)}`,
        );
        if (requestedPayload.run)
          loadedRuns.unshift(normalizeRun(requestedPayload.run as RuntimeRun));
      }
      const requestedStateId =
        mode === "states" ? locationParameters.get("state") : null;
      if (
        requestedStateId &&
        !loadedRuns.some((run: RuntimeRun) =>
          run.artifacts.some((artifact) => artifact.id === requestedStateId),
        )
      ) {
        try {
          const requestedPayload = await api(
            `/api/engine/states/${encodeURIComponent(requestedStateId)}`,
          );
          if (
            requestedPayload.run &&
            requestedPayload.run.workspaceId === workspaceId
          )
            loadedRuns.unshift(
              normalizeRun(requestedPayload.run as RuntimeRun),
            );
        } catch {
          // An unknown or cross-workspace state must not hide the normal history.
        }
      }
      setRuns(loadedRuns);
      if (requestedRunId) setSelectedId(requestedRunId);
      else if (requestedStateId) {
        const stateRun = loadedRuns.find((run: RuntimeRun) =>
          run.artifacts.some((artifact) => artifact.id === requestedStateId),
        );
        setSelectedRecordKey(stateRun ? requestedStateId : "");
        setSelectedId(stateRun?.id || "");
      }
      else if (mode === "workflowRuns")
        setSelectedId((current) =>
          loadedRuns.some((run: RuntimeRun) => run.id === current)
            ? current
            : (
                loadedRuns.find((run: RuntimeRun) =>
                  ["running", "waiting", "paused"].includes(run.status),
                ) || loadedRuns[0]
              )?.id || "",
        );
      const normalizeGoalRun = (goalRun: GoalRun): GoalRun => ({
        ...goalRun,
        workflowRun: normalizeRun(goalRun.workflowRun),
      });
      const loadedGoalRuns = (goalPayload.goalRuns || []).map(normalizeGoalRun);
      const requestedGoalRunId =
        mode === "goalRuns"
          ? new URLSearchParams(window.location.search).get("goalRun")
          : null;
      if (
        requestedGoalRunId &&
        !loadedGoalRuns.some(
          (goalRun: GoalRun) => goalRun.id === requestedGoalRunId,
        )
      ) {
        const requestedPayload = await api(
          `/api/goal-runs/${encodeURIComponent(requestedGoalRunId)}`,
        );
        if (requestedPayload.goalRun)
          loadedGoalRuns.unshift(
            normalizeGoalRun(requestedPayload.goalRun as GoalRun),
          );
      }
      setGoalRuns(loadedGoalRuns);
      if (requestedGoalRunId) setSelectedId(requestedGoalRunId);
      setInvocations(
        [
          ...(operationPayload.invocations || []),
          ...(modelPayload.invocations || []),
        ].sort((a: InvocationTrace, b: InvocationTrace) =>
          String(b.createdAt || "").localeCompare(String(a.createdAt || "")),
        ),
      );
    } catch (reason) {
      setError(String(reason));
    }
  };
  useEffect(() => {
    setRunLimit(50);
    setGoalRunLimit(50);
    setInvocationLimit(50);
    setHistoryFilter("");
    setRunStatusFilter("all");
    setSelectedRecordKey(runtimeRecordFromLocation(mode));
  }, [workspaceId, mode]);
  useEffect(() => {
    void refresh();
  }, [workspaceId, mode, runLimit, goalRunLimit, invocationLimit]);
  useEffect(() => {
    const restoreRuntimeLocation = () => {
      setSelectedRecordKey(runtimeRecordFromLocation(mode));
      void refresh();
    };
    window.addEventListener("popstate", restoreRuntimeLocation);
    return () =>
      window.removeEventListener("popstate", restoreRuntimeLocation);
  }, [workspaceId, mode, runLimit, goalRunLimit, invocationLimit]);
  useEffect(() => {
    if (!goalId && goalSpecs[0]) setGoalId(String(goalSpecs[0].id));
    if (
      (!planId || !availablePlanSpecs.some((doc) => doc.id === planId)) &&
      availablePlanSpecs[0]
    )
      setPlanId(String(availablePlanSpecs[0].id));
    if (!availablePlanSpecs.length) setPlanId("");
  }, [goalId, goalDocs.length, planDocs.length, workflows.length]);
  useEffect(() => {
    const parent = goalSpecs.find((doc) => doc.id === goalId);
    const preferred = goalVariants.find(
      (doc) => doc.id === parent?.preferredChild,
    );
    if (!goalVariants.some((doc) => doc.id === goalVariantId))
      setGoalVariantId(String(preferred?.id || goalVariants[0]?.id || ""));
  }, [goalId, goalDocs.length]);
  useEffect(() => {
    const parent = planSpecs.find((doc) => doc.id === planId);
    const preferred = planVariants.find(
      (doc) => doc.id === parent?.preferredChild,
    );
    if (!planVariants.some((doc) => doc.id === planVariantId))
      setPlanVariantId(String(preferred?.id || planVariants[0]?.id || ""));
  }, [planId, planDocs.length, workflows.length]);
  useEffect(() => {
    const parent = contextSpecs.find((doc) => doc.id === contextId);
    const preferred = contextVariants.find(
      (doc) => doc.id === parent?.preferredChild,
    );
    if (!contextId) setContextVariantId("");
    else if (!contextVariants.some((doc) => doc.id === contextVariantId))
      setContextVariantId(
        String(preferred?.id || contextVariants[0]?.id || ""),
      );
  }, [contextId, contextDocs.length]);

  const startGoalRun = async () => {
    setBusy(true);
    setError("");
    try {
      const payload = await api("/api/goal-runs", {
        method: "POST",
        body: JSON.stringify({
          workspaceId,
          goalId,
          goalVariantId,
          planId,
          planVariantId,
          contextId: contextId || undefined,
          contextVariantId: contextVariantId || undefined,
          inputs: JSON.parse(inputs),
        }),
      });
      onSelectRun?.(payload.goalRun.workflowRun);
      await refresh();
      selectGoalRun(payload.goalRun);
    } catch (reason) {
      setError(String(reason));
    } finally {
      setBusy(false);
    }
  };
  const persistRuntimeSelection = (
    parameter: "run" | "goalRun",
    id: string,
  ) => {
    const url = new URL(window.location.href);
    url.searchParams.set(parameter, id);
    url.searchParams.delete(parameter === "run" ? "goalRun" : "run");
    url.searchParams.delete("runStep");
    url.searchParams.delete("runEvent");
    replaceWorkbenchLocation(
      url,
      `${parameter === "goalRun" ? "Goal Run" : "Run"} ${id}`,
    );
  };
  const chooseRun = (run: RuntimeRun) => {
    setSelectedId(run.id);
    if (mode === "workflowRuns") persistRuntimeSelection("run", run.id);
    onSelectRun?.(run);
  };
  const selectRuntimeRecord = (row: RuntimeHistoryRow) => {
    setSelectedInvocationId("");
    setSelectedRecordKey(row.key);
    chooseRun(row.run);
    const url = new URL(window.location.href);
    if (mode === "states") {
      url.searchParams.set("state", row.key);
      url.searchParams.delete("runtimeRecord");
    } else {
      url.searchParams.set("runtimeRecord", row.key);
      url.searchParams.delete("state");
    }
    replaceWorkbenchLocation(url, row.key);
  };
  const selectGoalRun = (goalRun: GoalRun) => {
    setSelectedId(goalRun.id);
    persistRuntimeSelection("goalRun", goalRun.id);
    onSelectRun?.(goalRun.workflowRun);
  };
  const selectedRun = runs.find((row) => row.id === selectedId) || runs[0];
  const durableStateValues = useMemo<BootstrappedStateValue[]>(() => {
    const started = selectedRun?.events.find(
      (event) => event.kind === "workflow.started",
    );
    const payload =
      started?.payload && typeof started.payload === "object"
        ? (started.payload as Record<string, unknown>)
        : {};
    return Array.isArray(payload.stateValues)
      ? (payload.stateValues.filter(
          (value) => value && typeof value === "object",
        ) as BootstrappedStateValue[])
      : [];
  }, [selectedRun?.id, selectedRun?.events]);
  const displayedStateValues = durableStateValues.length
    ? durableStateValues
    : preflightStateValues;
  useEffect(() => {
    if (mode === "workflowRuns" && selectedRun) onSelectRun?.(selectedRun);
  }, [mode, selectedRun?.id]);
  const selectedInvocation = invocations.find(
    (row) => row.id === selectedInvocationId,
  );
  useEffect(() => {
    if (mode !== "workflowRuns" || !selectedRun) return;
    const url = new URL(window.location.href);
    if (url.searchParams.has("run")) return;
    url.searchParams.set("run", selectedRun.id);
    window.history.replaceState(
      null,
      "",
      `${url.pathname}${url.search}${url.hash}`,
    );
  }, [mode, selectedRun?.id]);
  useEffect(() => {
    if (mode !== "workflowRuns" || !selectedRun) {
      setFrozenWorkflow(null);
      return;
    }
    let active = true;
    void api(
      `/api/engine/workflows/${encodeURIComponent(selectedRun.workflowId)}?version=${selectedRun.workflowVersion}`,
    )
      .then((payload) => {
        if (active) setFrozenWorkflow(payload.workflow as FrozenWorkflow);
      })
      .catch((reason) => {
        if (active) {
          setFrozenWorkflow(null);
          setError(String(reason));
        }
      });
    return () => {
      active = false;
    };
  }, [
    mode,
    selectedRun?.id,
    selectedRun?.workflowId,
    selectedRun?.workflowVersion,
  ]);
  const workflowWaitingStep = selectedRun?.steps.find(
    (step) => step.status === "waiting",
  );
  const workflowWaitingDefinition = frozenWorkflow?.steps.find(
    (step) => step.id === workflowWaitingStep?.stepId,
  );
  useEffect(() => {
    if (mode !== "workflowRuns" || !selectedRun || !workflowWaitingStep) {
      setWorkflowHumanDraft({});
      setWorkflowDraftLoaded(false);
      setWorkflowDraftDirty(false);
      setWorkflowDraftStatus("");
      return;
    }
    setWorkflowDraftLoaded(false);
    setWorkflowDraftStatus("Loading saved draft…");
    void api(
      `/api/engine/runs/${encodeURIComponent(selectedRun.id)}/steps/${encodeURIComponent(workflowWaitingStep.stepId)}/draft`,
    )
      .then((payload) => {
        setWorkflowHumanDraft(payload.draft?.values || {});
        setWorkflowDraftDirty(false);
        setWorkflowDraftLoaded(true);
        setWorkflowDraftStatus(
          payload.draft?.updatedAt
            ? `Draft restored · ${stamp(payload.draft.updatedAt)}`
            : "Draft autosave ready",
        );
      })
      .catch((reason) => {
        setWorkflowDraftLoaded(true);
        setWorkflowDraftStatus(`Draft unavailable · ${String(reason)}`);
      });
  }, [mode, selectedRun?.id, workflowWaitingStep?.stepId]);
  useEffect(() => {
    if (
      !workflowDraftLoaded ||
      !workflowDraftDirty ||
      !selectedRun ||
      !workflowWaitingStep
    )
      return;
    setWorkflowDraftStatus("Saving draft…");
    const timer = window.setTimeout(() => {
      void api(
        `/api/engine/runs/${encodeURIComponent(selectedRun.id)}/steps/${encodeURIComponent(workflowWaitingStep.stepId)}/draft`,
        { method: "PUT", body: JSON.stringify(workflowHumanDraft) },
      )
        .then((payload) => {
          setWorkflowDraftDirty(false);
          setWorkflowDraftStatus(
            `Draft saved · ${stamp(payload.draft?.updatedAt)}`,
          );
        })
        .catch((reason) =>
          setWorkflowDraftStatus(`Draft save failed · ${String(reason)}`),
        );
    }, 500);
    return () => window.clearTimeout(timer);
  }, [
    workflowHumanDraft,
    workflowDraftLoaded,
    workflowDraftDirty,
    selectedRun?.id,
    workflowWaitingStep?.stepId,
  ]);
  const selectedGoalRun = goalRuns.find((row) => row.id === selectedId);
  const [goalRunWorkflow, setGoalRunWorkflow] = useState<FrozenWorkflow | null>(
    null,
  );
  useEffect(() => {
    if (!selectedGoalRun) {
      setGoalRunWorkflow(null);
      return;
    }
    let active = true;
    const run = selectedGoalRun.workflowRun;
    void api(
      `/api/engine/workflows/${encodeURIComponent(run.workflowId)}?version=${run.workflowVersion}`,
    )
      .then((payload) => {
        if (active) setGoalRunWorkflow(payload.workflow as FrozenWorkflow);
      })
      .catch((reason) => {
        if (active) setError(String(reason));
      });
    return () => {
      active = false;
    };
  }, [selectedGoalRun?.id]);
  const waitingStep = selectedGoalRun?.workflowRun.steps.find(
    (step) => step.status === "waiting",
  );
  const waitingStepDefinition = goalRunWorkflow?.steps.find(
    (step) => step.id === waitingStep?.stepId,
  );
  useEffect(() => {
    if (!selectedGoalRun || !waitingStep) {
      setHumanDraft({});
      setDraftLoaded(false);
      setHumanDraftDirty(false);
      return;
    }
    setDraftLoaded(false);
    setDraftStatus("Loading saved draft…");
    void api(
      `/api/engine/runs/${encodeURIComponent(selectedGoalRun.workflowRunId)}/steps/${encodeURIComponent(waitingStep.stepId)}/draft`,
    )
      .then((payload) => {
        setHumanDraft(payload.draft?.values || {});
        setHumanDraftDirty(false);
        setDraftLoaded(true);
        setDraftStatus(
          payload.draft?.updatedAt
            ? `Draft restored · ${stamp(payload.draft.updatedAt)}`
            : "Draft autosave ready",
        );
      })
      .catch((reason) => {
        setDraftLoaded(true);
        setDraftStatus(`Draft unavailable · ${String(reason)}`);
      });
  }, [selectedGoalRun?.id, waitingStep?.stepId]);
  useEffect(() => {
    if (!draftLoaded || !humanDraftDirty || !selectedGoalRun || !waitingStep)
      return;
    setDraftStatus("Saving draft…");
    const timer = window.setTimeout(() => {
      void api(
        `/api/engine/runs/${encodeURIComponent(selectedGoalRun.workflowRunId)}/steps/${encodeURIComponent(waitingStep.stepId)}/draft`,
        { method: "PUT", body: JSON.stringify(humanDraft) },
      )
        .then((payload) => {
          setHumanDraftDirty(false);
          setDraftStatus(`Draft saved · ${stamp(payload.draft?.updatedAt)}`);
        })
        .catch((reason) =>
          setDraftStatus(`Draft save failed · ${String(reason)}`),
        );
    }, 500);
    return () => window.clearTimeout(timer);
  }, [
    humanDraft,
    draftLoaded,
    humanDraftDirty,
    selectedGoalRun?.id,
    waitingStep?.stepId,
  ]);
  const submitHumanInput = async (values: Record<string, unknown>) => {
    if (!selectedGoalRun || !waitingStep) return;
    setBusy(true);
    setError("");
    try {
      const payload = await api(
        `/api/engine/runs/${encodeURIComponent(selectedGoalRun.workflowRunId)}/steps/${encodeURIComponent(waitingStep.stepId)}/input`,
        { method: "POST", body: JSON.stringify(values) },
      );
      onSelectRun?.(payload.run);
      await refresh();
    } catch (reason) {
      setError(String(reason));
    } finally {
      setBusy(false);
    }
  };
  const commandGoalRun = async (
    command: Exclude<WorkflowRunCommand, "replay">,
  ) => {
    if (!selectedGoalRun) return;
    setBusy(true);
    setError("");
    try {
      const payload = await api(
        `/api/engine/runs/${encodeURIComponent(selectedGoalRun.workflowRunId)}/commands`,
        { method: "POST", body: JSON.stringify({ command }) },
      );
      onSelectRun?.(payload.run);
      await refresh();
    } catch (reason) {
      setError(String(reason));
    } finally {
      setBusy(false);
    }
  };
  const commandWorkflowRun = async (
    command: "pause" | "resume" | "advance" | "replay" | "cancel",
  ) => {
    if (!selectedRun) return;
    setBusy(true);
    setError("");
    try {
      const payload = await api(
        `/api/engine/runs/${encodeURIComponent(selectedRun.id)}/commands`,
        { method: "POST", body: JSON.stringify({ command }) },
      );
      const updated = payload.run as RuntimeRun;
      setRuns((current) =>
        command === "replay"
          ? [updated, ...current]
          : current.map((item) => (item.id === updated.id ? updated : item)),
      );
      chooseRun(updated);
    } catch (reason) {
      setError(String(reason));
    } finally {
      setBusy(false);
    }
  };
  const submitWorkflowHumanInput = async (values: Record<string, unknown>) => {
    if (!selectedRun || !workflowWaitingStep) return;
    setBusy(true);
    setError("");
    try {
      const payload = await api(
        `/api/engine/runs/${encodeURIComponent(selectedRun.id)}/steps/${encodeURIComponent(workflowWaitingStep.stepId)}/input`,
        { method: "POST", body: JSON.stringify(values) },
      );
      const updated = payload.run as RuntimeRun;
      setRuns((current) =>
        current.map((item) => (item.id === updated.id ? updated : item)),
      );
      setWorkflowHumanDraft({});
      setWorkflowDraftLoaded(false);
      setWorkflowDraftDirty(false);
      chooseRun(updated);
    } catch (reason) {
      setError(String(reason));
    } finally {
      setBusy(false);
    }
  };
  const title = {
    goalRuns: "Goal Runs",
    workflowRuns: "Workflow Runs",
    execs: "Executions",
    events: "Events",
    states: "States",
    runtimeContexts: "Runtime Contexts",
    logs: "Logs",
  }[mode];

  if (mode === "goalRuns")
    return (
      <section className="resource-view runtime-history-view">
        <div className="resource-heading">
          <div>
            <span>DURABLE RUNTIME</span>
            <h1>Goal Runs</h1>
            <p>
              Goals, planning strategies, AtomSpace bindings, executable
              Workflows, and their runs are linked in persistent records.
            </p>
          </div>
          <button onClick={refresh}>Refresh</button>
        </div>
        {error && (
          <div className="backend-error">
            <b>Error</b>
            <span>{error}</span>
          </div>
        )}
        <div className="settings-grid goal-run-form">
          <label>
            <span>GOAL</span>
            <select
              value={goalId}
              onChange={(event) => setGoalId(event.target.value)}
            >
              {goalSpecs.map((doc) => (
                <option key={doc.id} value={doc.id}>
                  {doc.label || doc.id}
                </option>
              ))}
            </select>
          </label>
          <label>
            <span>GOAL INTERPRETATION</span>
            <select
              value={goalVariantId}
              onChange={(event) => setGoalVariantId(event.target.value)}
            >
              {goalVariants.map((doc) => (
                <option key={doc.id} value={doc.id}>
                  {doc.label || doc.id}
                </option>
              ))}
            </select>
          </label>
          <label>
            <span>PLANNING STRATEGY</span>
            <select
              value={planId}
              onChange={(event) => setPlanId(event.target.value)}
            >
              {availablePlanSpecs
                .filter((doc) => !goalId || (doc.goals || []).includes(goalId))
                .map((doc) => (
                  <option key={doc.id} value={doc.id}>
                    {doc.label || doc.id}
                  </option>
                ))}
            </select>
            <small>
              {availablePlanSpecs.length
                ? "Only strategies resolving to a workflow in this workspace are runnable."
                : "No strategy alternative names a workflow available in this workspace."}
            </small>
          </label>
          <label>
            <span>STRATEGY ALTERNATIVE</span>
            <select
              value={planVariantId}
              onChange={(event) => setPlanVariantId(event.target.value)}
            >
              {planVariants.map((doc) => (
                <option key={doc.id} value={doc.id}>
                  {doc.label || doc.id}
                </option>
              ))}
            </select>
          </label>
          <label>
            <span>ATOMSPACE</span>
            <select
              value={contextId}
              onChange={(event) => setContextId(event.target.value)}
            >
              <option value="">none</option>
              {contextSpecs.map((doc) => (
                <option key={doc.id} value={doc.id}>
                  {doc.label || doc.id}
                </option>
              ))}
            </select>
          </label>
          <label>
            <span>ATOMSPACE ALTERNATIVE</span>
            <select
              value={contextVariantId}
              disabled={!contextId}
              onChange={(event) => setContextVariantId(event.target.value)}
            >
              <option value="">none</option>
              {contextVariants.map((doc) => (
                <option key={doc.id} value={doc.id}>
                  {doc.label || doc.id}
                </option>
              ))}
            </select>
          </label>
          {selectedGoalWorkflow && (
            <WorkflowInputsEditor
              key={selectedGoalWorkflow.id}
              workflowId={String(selectedGoalWorkflow.id)}
              contract={
                (selectedGoalWorkflow.inputs || {}) as Record<
                  string,
                  WorkflowInputContract
                >
              }
              source={inputs}
              onSource={setInputs}
            />
          )}
          <label>
            <span>ADVANCED WORKFLOW INPUTS (JSON)</span>
            <textarea
              value={inputs}
              onChange={(event) => setInputs(event.target.value)}
            />
          </label>
        </div>
        <button
          className="run-button"
          disabled={busy || !goalId || !planId}
          onClick={startGoalRun}
        >
          ▶ Pursue goal
        </button>
        <div className="resource-table">
          <div className="resource-row resource-head">
            <span>Goal</span>
            <span>Strategy alternative</span>
            <span>Status</span>
            <span>Workflow/plan run</span>
            <span>Created</span>
          </div>
          {goalRuns.map((row) => (
            <button
              className="resource-row"
              key={row.id}
              onClick={() => selectGoalRun(row)}
            >
              <b>{row.goalVariantId || row.goalId}</b>
              <code>{row.planVariantId}</code>
              <span>{row.status}</span>
              <span>{row.workflowRunId.slice(0, 8)}</span>
              <em>{stamp(row.createdAt)}</em>
            </button>
          ))}
        </div>
        {goalRuns.length >= goalRunLimit && (
          <button
            type="button"
            className="runtime-load-older"
            onClick={() =>
              setGoalRunLimit((limit) => Math.min(500, limit + 50))
            }
          >
            Load 50 older goal runs
          </button>
        )}
        {selectedGoalRun && (
          <div className="goal-run-controls">
            <div>
              <b>Selected pursuit</b>
              <span>
                {selectedGoalRun.goalVariantId} ·{" "}
                {selectedGoalRun.planVariantId} ·{" "}
                {selectedGoalRun.contextVariantId || "no context"}
              </span>
            </div>
            {onOpenResource && (
              <div className="runtime-resource-links">
                <button
                  type="button"
                  onClick={() =>
                    onOpenResource(
                      "goal",
                      selectedGoalRun.goalVariantId || selectedGoalRun.goalId,
                    )
                  }
                >
                  Goal ·{" "}
                  {selectedGoalRun.goalVariantId || selectedGoalRun.goalId}
                </button>
                <button
                  type="button"
                  onClick={() =>
                    onOpenResource(
                      "plan",
                      selectedGoalRun.planVariantId || selectedGoalRun.planId,
                    )
                  }
                >
                  Planning strategy ·{" "}
                  {selectedGoalRun.planVariantId || selectedGoalRun.planId}
                </button>
                {(selectedGoalRun.contextVariantId ||
                  selectedGoalRun.contextId) && (
                  <button
                    type="button"
                    onClick={() =>
                      onOpenResource(
                        "context",
                        selectedGoalRun.contextVariantId ||
                          selectedGoalRun.contextId!,
                      )
                    }
                  >
                    AtomSpace ·{" "}
                    {selectedGoalRun.contextVariantId ||
                      selectedGoalRun.contextId}
                  </button>
                )}
              </div>
            )}
          </div>
        )}
        {waitingStep && (
          <div className="human-pause goal-run-human">
            <div className="pause-ring">Ⅱ</div>
            <b>Waiting for {waitingStep.stepId}</b>
            <span>
              {waitingStepDefinition?.label ||
                "Provide the values required by this workflow step."}
            </span>
            <small className="human-draft-status">{draftStatus}</small>
            <HumanInputForm
              step={waitingStepDefinition}
              busy={busy}
              draft={humanDraft}
              onDraft={(values) => {
                setHumanDraft(values);
                setHumanDraftDirty(true);
              }}
              onSubmit={(values) => void submitHumanInput(values)}
            />
          </div>
        )}
        {selectedGoalRun && (
          <WorkflowRunProjection
            run={selectedGoalRun.workflowRun}
            workflow={goalRunWorkflow}
            busy={busy}
            commands={["pause", "resume", "advance", "cancel"]}
            onCommand={(command) =>
              void commandGoalRun(
                command as Exclude<WorkflowRunCommand, "replay">,
              )
            }
            onOpenResource={onOpenResource}
          />
        )}
      </section>
    );

  const invocationRows = invocations.map((trace) => {
    const errorDetail =
      typeof trace.error === "string"
        ? trace.error
        : trace.error && typeof trace.error === "object"
          ? String(
              (trace.error as { message?: unknown }).message ||
                jsonValueToMetta(trace.error),
            )
          : "";
    return {
      key: `invocation:${trace.id}`,
      a: trace.modelId || trace.operationId || trace.operation?.id || trace.id,
      b: trace.status,
      c: trace.kind === "model_invocation_trace" ? "model" : "operation",
      d: trace.id.slice(-8),
      e:
        errorDetail ||
        trace.response?.text ||
        trace.implementation?.label ||
        "durable invocation trace",
      trace,
    };
  });
  const baseRows =
    mode === "workflowRuns"
      ? runs.map((run) => ({
          key: run.id,
          a: run.workflowId,
          b: run.status,
          c: `${run.steps.length} steps`,
          d: run.id.slice(0, 8),
          e: stamp(run.createdAt),
          run,
        }))
      : mode === "execs"
        ? [
            ...invocationRows,
            ...runs.flatMap((run) =>
              run.steps.map((step) => ({
                key: `${run.id}:${step.stepId}`,
                a: step.stepId,
                b: step.status,
                c: `attempt ${step.attempt || 0}`,
                d: run.id.slice(0, 8),
                e: step.error || "—",
                run,
              })),
            ),
          ]
        : mode === "events"
          ? runs.flatMap((run) =>
              run.events.map((event) => ({
                key: `${run.id}:${event.id}`,
                a: event.kind,
                b: event.stepId || "workflow",
                c: stamp(event.createdAt),
                d: run.id.slice(0, 8),
                e: jsonValueToMetta(event.payload || {}),
                run,
              })),
            )
          : mode === "states"
            ? runs.flatMap((run) =>
                run.artifacts.map((item) => ({
                  key: item.id,
                  a: item.name,
                  b: item.datatype || "Any",
                  c: item.stepId || "input",
                  d: run.id.slice(0, 8),
                  e: jsonValueToMetta(item.payload),
                  run,
                })),
              )
            : mode === "runtimeContexts"
              ? goalRuns
                  .filter((item) => item.contextId)
                  .map((item) => ({
                    key: `context:${item.id}`,
                    a: item.contextVariantId || item.contextId || "context",
                    b: item.status,
                    c: stamp(item.createdAt),
                    d: item.workflowRunId.slice(0, 8),
                    e: item.contextId || "—",
                    run: item.workflowRun,
                  }))
              : [
                  ...invocationRows,
                  ...runs.flatMap((run) =>
                    run.logs.map((log) => ({
                      key: `${run.id}:${log.id}`,
                      a: log.stream,
                      b: log.stepId || "workflow",
                      c: stamp(log.createdAt),
                      d: run.id.slice(0, 8),
                      e: log.message,
                      run,
                    })),
                  ),
                ];
  const rows = baseRows.map((row) => {
    if ("trace" in row) return row;
    const recordKind: RuntimeRecordKind =
      mode === "workflowRuns"
        ? "workflow run"
        : mode === "execs"
          ? "step execution"
          : mode === "events"
            ? "event"
            : mode === "states"
              ? "state artifact"
              : mode === "runtimeContexts"
                ? "runtime context"
                : "log";
    const record =
      recordKind === "workflow run"
        ? row.run
        : recordKind === "step execution"
          ? row.run.steps.find(
              (item) => `${row.run.id}:${item.stepId}` === row.key,
            )
          : recordKind === "event"
            ? row.run.events.find(
                (item) => `${row.run.id}:${item.id}` === row.key,
              )
            : recordKind === "state artifact"
              ? row.run.artifacts.find((item) => item.id === row.key)
              : recordKind === "runtime context"
                ? goalRuns.find((item) => `context:${item.id}` === row.key)
                : row.run.logs.find(
                    (item) => `${row.run.id}:${item.id}` === row.key,
                  );
    return { ...row, recordKind, record } as RuntimeHistoryRow;
  });
  const selectedRuntimeRow = rows.find(
    (row): row is RuntimeHistoryRow =>
      !("trace" in row) && row.key === selectedRecordKey,
  );
  const normalizedFilter = historyFilter.trim().toLowerCase();
  const runStatusCounts = {
    running: runs.filter((run) =>
      ["running", "waiting", "paused"].includes(run.status),
    ).length,
    failed: runs.filter((run) => run.status === "failed").length,
    cancelled: runs.filter((run) => run.status === "cancelled").length,
  };
  const statusRows =
    mode !== "workflowRuns" || runStatusFilter === "all"
      ? rows
      : rows.filter((row) => {
          if ("trace" in row) return false;
          return runStatusFilter === "running"
            ? ["running", "waiting", "paused"].includes(row.run.status)
            : row.run.status === runStatusFilter;
        });
  const visibleRows = normalizedFilter
    ? statusRows.filter((row) =>
        [row.a, row.b, row.c, row.d, row.e].some((value) =>
          String(value).toLowerCase().includes(normalizedFilter),
        ),
      )
    : statusRows;
  const canLoadMoreInvocations =
    (mode === "execs" || mode === "logs") &&
    invocations.length >= invocationLimit;
  const canLoadMoreRuns = runs.length >= runLimit;
  const titlebarViewActions =
    mode === "workflowRuns"
      ? document.querySelector(".topbar-view-actions")
      : null;
  const leftColumnStack = mode === "workflowRuns"
    ? document.querySelector('[data-accordion-stack="left-stack"]:not([data-accordion-member])')
    : null;
  return (
    <>
      {titlebarViewActions &&
        createPortal(
          <>
            {false && <div className="right-column-accordion-master" role="group" aria-label="Set all right column accordion sizes">
              <span>RIGHT COLUMN</span>
              <button type="button" aria-label="Collapse all right column panels to strips" aria-pressed={rightColumnDisplayMode === "strip"} title="Collapse all right column panels to strips" onClick={() => setRightColumnDisplayMode("strip")}>−</button>
              <button type="button" aria-label="Give all right column panels scrolling windows" aria-pressed={rightColumnDisplayMode === "scroll"} title="Give all right column panels scrolling windows" onClick={() => setRightColumnDisplayMode("scroll")}>*</button>
              <button type="button" aria-label="Show all right column panel content" aria-pressed={rightColumnDisplayMode === "full"} title="Show all right column panel content" onClick={() => setRightColumnDisplayMode("full")}>+</button>
            </div>}
            {minimizedPanels.has("runs") && (
              <button
                type="button"
                className="topbar-panel-restore"
                onClick={() => setPanelMinimized("runs", false)}
              >
                Restore Workflow Runs
              </button>
            )}
            {minimizedPanels.has("objects") && (
              <button
                type="button"
                className="topbar-panel-restore"
                onClick={() => setPanelMinimized("objects", false)}
              >
                Restore Detected Objects
              </button>
            )}
            {minimizedPanels.has("spline") && (
              <button
                type="button"
                className="topbar-panel-restore"
                onClick={() => setPanelMinimized("spline", false)}
              >
                Restore Selected Run Spline
              </button>
            )}
          </>,
          titlebarViewActions,
        )}
      {leftColumnStack && isValidElement(runLauncher) && createPortal(
        cloneElement(runLauncher as ReactElement<{ displayMode?: AccordionDisplayMode; onDisplayModeChange?: (mode: AccordionDisplayMode) => void }>, {
          displayMode: launcherDisplayMode,
          onDisplayModeChange: setLauncherDisplayMode,
        }),
        leftColumnStack,
      )}
      <section
        className={`resource-view runtime-history-view ${expandedPanel ? `panel-maximized-${expandedPanel}` : ""}`}
      >
        {mode === "workflowRuns" && !leftColumnStack && isValidElement(runLauncher) && cloneElement(runLauncher as ReactElement<{ displayMode?: AccordionDisplayMode; onDisplayModeChange?: (mode: AccordionDisplayMode) => void }>, {
          displayMode: launcherDisplayMode,
          onDisplayModeChange: setLauncherDisplayMode,
        })}
        <ThreeStateAccordionStack id="right-stack" hostRef={setRightColumnAccordionHost}>
        <WorkflowRunsControl
          workflowRuns={mode === "workflowRuns"}
          modern={false}
          displayMode={workflowRunsDisplayMode}
          onDisplayModeChange={setWorkflowRunsDisplayMode}
          value={`${visibleRows.length} visible · ${runs.length} loaded`}
          detail={selectedRun ? `${selectedRun.id.slice(0, 8)} · ${selectedRun.status}` : "Select a durable run"}
          accessories={<button type="button" onClick={refresh}>Refresh</button>}
          footer={<><b>{visibleRows.length}</b><span>of {runs.length} loaded records · {runStatusFilter}</span></>}
        >
          {mode !== "workflowRuns" && <div className="resource-heading">
            <button
              type="button"
              className="panel-title-toggle"
              title="Persistent runtime history"
            >
              <span>PERSISTENT RUNTIME HISTORY</span>
              <h1>{title}</h1>
              <p>
                {mode === "execs" || mode === "logs"
                  ? "Workflow-engine records and standalone resource invocation traces are loaded from their durable workspace stores."
                  : "Records are loaded from the durable workflow-engine database across application sessions."}
              </p>
            </button>
            <button onClick={refresh}>Refresh</button>
          </div>}
          {error && (
            <div className="backend-error">
              <b>Error</b>
              <span>{error}</span>
            </div>
          )}
          <div className={mode === "workflowRuns" ? "durable-runs-tools" : "runtime-history-tools"}>
            <label>
              <span>FILTER RECORDS</span>
              <input
                value={historyFilter}
                onChange={(event) => setHistoryFilter(event.target.value)}
                placeholder="ID, status, type, run, or detail…"
              />
            </label>
            {mode === "workflowRuns" && (
              <div
                className="runtime-status-filters"
                role="group"
                aria-label="Filter workflow runs by status"
              >
                <button
                  type="button"
                  className={runStatusFilter === "all" ? "active" : ""}
                  aria-pressed={runStatusFilter === "all"}
                  onClick={() => setRunStatusFilter("all")}
                >
                  All <b>{runs.length}</b>
                </button>
                <button
                  type="button"
                  className={
                    runStatusFilter === "running" ? "active running" : "running"
                  }
                  aria-pressed={runStatusFilter === "running"}
                  onClick={() => setRunStatusFilter("running")}
                >
                  Running <b>{runStatusCounts.running}</b>
                </button>
                <button
                  type="button"
                  className={
                    runStatusFilter === "failed" ? "active failed" : "failed"
                  }
                  aria-pressed={runStatusFilter === "failed"}
                  onClick={() => setRunStatusFilter("failed")}
                >
                  Failed <b>{runStatusCounts.failed}</b>
                </button>
                <button
                  type="button"
                  className={
                    runStatusFilter === "cancelled"
                      ? "active cancelled"
                      : "cancelled"
                  }
                  aria-pressed={runStatusFilter === "cancelled"}
                  onClick={() => setRunStatusFilter("cancelled")}
                >
                  Cancelled <b>{runStatusCounts.cancelled}</b>
                </button>
              </div>
            )}
            <small>
              {visibleRows.length} of {rows.length} loaded records
            </small>
            {canLoadMoreRuns && (
              <button
                type="button"
                onClick={() =>
                  setRunLimit((limit) => Math.min(500, limit + 50))
                }
              >
                Load 50 older runs
              </button>
            )}
            {canLoadMoreInvocations && (
              <button
                type="button"
                onClick={() =>
                  setInvocationLimit((limit) => Math.min(1000, limit + 100))
                }
              >
                Load 100 older invocations
              </button>
            )}
          </div>
          <div className={mode === "workflowRuns" ? "durable-runs-records resource-table" : "resource-table"}>
            <div className="resource-row resource-head">
              <span>Record</span>
              <span>Status / type</span>
              <span>Step / time</span>
              <span>Run</span>
              <span>Detail</span>
            </div>
            {visibleRows.map((row) => (
              <button
                className={`resource-row ${!("trace" in row) && (mode === "workflowRuns" ? row.run.id === selectedRun?.id : row.key === selectedRecordKey) ? "selected" : ""}`}
                aria-pressed={
                  !("trace" in row) &&
                  (mode === "workflowRuns"
                    ? row.run.id === selectedRun?.id
                    : row.key === selectedRecordKey)
                }
                key={row.key}
                onClick={() => {
                  if ("trace" in row) {
                    setSelectedInvocationId(row.trace.id);
                    setSelectedRecordKey("");
                    setSelectedId("");
                  } else selectRuntimeRecord(row);
                }}
              >
                <b>{row.a}</b>
                <code>{row.b}</code>
                <span>{row.c}</span>
                <span>{row.d}</span>
                <em title={row.e}>{row.e}</em>
              </button>
            ))}
            {!visibleRows.length && (
              <div className="studio-empty">
                {rows.length
                  ? "No loaded records match this filter."
                  : `No persisted ${title.toLowerCase()} yet.`}
              </div>
            )}
          </div>
        </WorkflowRunsControl>
        {mode === "workflowRuns" && selectedRun && (
          <WorkflowRunSplineWorkspace
            run={selectedRun}
            workflow={frozenWorkflow}
            onOpenResource={onOpenResource}
            expandedPanel={expandedPanel}
            minimizedPanels={minimizedPanels}
            objectDisplayMode={objectDisplayMode}
            setObjectDisplayMode={setObjectDisplayMode}
            objectsListDisplayMode={objectsListDisplayMode}
            setObjectsListDisplayMode={setObjectsListDisplayMode}
            rightColumnAccordionHost={rightColumnAccordionHost}
            splineDisplayMode={splineDisplayMode}
            setSplineDisplayMode={setSplineDisplayMode}
            setExpandedPanel={setExpandedPanel}
            setPanelMinimized={setPanelMinimized}
          />
        )}
        </ThreeStateAccordionStack>
        {selectedRuntimeRow && mode !== "workflowRuns" && (
          <RuntimeRecordInspector
            row={selectedRuntimeRow}
            onOpenResource={onOpenResource}
          />
        )}
        {selectedInvocation && (
          <section
            className="run-projection-inspector"
            aria-label="Selected standalone invocation"
          >
            <div>
              <span>
                STANDALONE{" "}
                {selectedInvocation.kind === "model_invocation_trace"
                  ? "MODEL"
                  : "OPERATION"}{" "}
                EXECUTION
              </span>
              <h3>
                {selectedInvocation.modelId ||
                  selectedInvocation.operationId ||
                  selectedInvocation.operation?.label ||
                  selectedInvocation.operation?.id}
              </h3>
              <p>
                {stamp(selectedInvocation.createdAt)} ·{" "}
                {selectedInvocation.status}
              </p>
              {onOpenResource && selectedInvocation.modelId && (
                <button
                  type="button"
                  className="runtime-resource-link"
                  onClick={() =>
                    onOpenResource("model", selectedInvocation.modelId!)
                  }
                >
                  Open Model · {selectedInvocation.modelId}
                </button>
              )}
              {onOpenResource &&
                (selectedInvocation.operationId ||
                  selectedInvocation.operation?.id) && (
                  <button
                    type="button"
                    className="runtime-resource-link"
                    onClick={() =>
                      onOpenResource(
                        "operation",
                        String(
                          selectedInvocation.operationId ||
                            selectedInvocation.operation?.id,
                        ),
                      )
                    }
                  >
                    Open Operation ·{" "}
                    {selectedInvocation.operationId ||
                      selectedInvocation.operation?.id}
                  </button>
                )}
            </div>
            <dl>
              <div>
                <dt>Trace</dt>
                <dd>{selectedInvocation.id}</dd>
              </div>
              <div>
                <dt>Backend</dt>
                <dd>
                  {selectedInvocation.response?.backendId ||
                    selectedInvocation.implementation?.implementation ||
                    "resolved runtime"}
                </dd>
              </div>
              <div>
                <dt>Latency</dt>
                <dd>
                  {selectedInvocation.response?.latencyMs != null
                    ? `${selectedInvocation.response.latencyMs} ms`
                    : "—"}
                </dd>
              </div>
              <div>
                <dt>Log</dt>
                <dd>{selectedInvocation.logPath}</dd>
              </div>
            </dl>
            <details open>
              <summary>Complete durable trace</summary>
              <pre>{jsonValueToMetta(selectedInvocation)}</pre>
            </details>
          </section>
        )}
        {mode === "workflowRuns" && selectedRun && workflowWaitingStep && (
          <div className="human-pause workflow-run-human">
            <div className="pause-ring">Ⅱ</div>
            <b>Waiting for {workflowWaitingStep.stepId}</b>
            <span>
              {workflowWaitingDefinition?.label ||
                "Provide the values required by this workflow step."}
            </span>
            <small className="human-draft-status">{workflowDraftStatus}</small>
            <HumanInputForm
              step={workflowWaitingDefinition}
              busy={busy}
              draft={workflowHumanDraft}
              onDraft={(values) => {
                setWorkflowHumanDraft(values);
                setWorkflowDraftDirty(true);
              }}
              onSubmit={(values) => void submitWorkflowHumanInput(values)}
            />
          </div>
        )}
        {mode === "workflowRuns" && showDesignReference && (
          <Suspense
            fallback={
              <div className="studio-empty">
                Loading workflow runner reference…
              </div>
            }
          >
            <WorkflowRunnerTodoReference displayMode={referenceDisplayMode} onDisplayModeChange={setReferenceDisplayMode} />
          </Suspense>
        )}
        {mode !== "workflowRuns" && selectedRun && (
          <div className="demo-notice">
            <b>SELECTED RUN {selectedRun.id.slice(0, 8)}</b>
            <span>
              {selectedRun.workflowId} · {selectedRun.status} ·{" "}
              {selectedRun.events.length} events ·{" "}
              {selectedRun.artifacts.length} states
            </span>
          </div>
        )}
      </section>
    </>
  );
}
