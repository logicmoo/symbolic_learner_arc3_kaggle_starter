import { useEffect, useMemo, useRef, useState } from "react";
import type { CSSProperties, DragEvent as ReactDragEvent, PointerEvent as ReactPointerEvent, ReactNode, RefObject } from "react";
import dagre from "@dagrejs/dagre";
import {
  Background,
  Controls,
  Handle,
  MarkerType,
  MiniMap,
  Position,
  ReactFlow,
  type Edge,
  type Node,
  type NodeProps,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { relationshipIds } from "./resourceRelationships";
import {
  ThreeStateAccordionMember,
  ThreeStateAccordionStack,
  type AccordionDisplayMode,
} from "./ThreeStateAccordion";
import {
  OperationPlayground,
  type OperationDef,
  type OperationImplementationDef,
} from "./OperationPlayground";
import {
  WorkflowPageHost,
  type WorkflowPageComponentRegistry,
  type WorkflowPageDefinition,
  type WorkflowPageMemberDefinition,
} from "./WorkflowPageHost";
import { ResourceSourceEditor } from "./ResourceSourceEditor";
import { WorkflowPageSourceEditor } from "./WorkflowPageSourceEditor";
import "../styles/english_workflow.css";
import "../styles/english_workflow_order.css";
import "../styles/visual_image_diff.css";

type VisualFrame = {
  id: string;
  label: string;
  assetPath: string;
};

const VISUAL_PROMPT_DRAG_TYPE = "application/x-symbolic-workbench-prompt";
const VISUAL_ORDER_DRAG_TYPE = "application/x-symbolic-workbench-prompt-order";

function draggedPromptId(event: ReactDragEvent): string {
  return event.dataTransfer.getData(VISUAL_PROMPT_DRAG_TYPE) || event.dataTransfer.getData("text/plain");
}

function draggedOrderEntry(event: ReactDragEvent): { entryId: string; parentGroupId?: string } | null {
  const [scope, entryId] = event.dataTransfer.getData(VISUAL_ORDER_DRAG_TYPE).split("\n");
  return scope && entryId ? { entryId, parentGroupId: scope === "__root__" ? undefined : scope } : null;
}

type VisualCommand = {
  fromFrameId: string;
  toFrameId: string;
  command: string;
  label?: string;
};

type PromptGroupDefinition = {
  id: string;
  label: string;
  transaction: string;
  operation: string;
  implementation?: string;
  profile?: string;
  continueOnError?: boolean;
  focalGroup?: string;
  parentGroup?: string;
  colorKey?: string;
  prompts: string[];
};

type VisualImageDiffDocument = {
  id: string;
  label: string;
  description?: string;
  promptProfileId: string;
  runtimeWorkflowId?: string;
  promptGroups?: PromptGroupDefinition[];
  frames: VisualFrame[];
  commands: VisualCommand[];
};

type PromptChoice = {
  id: string;
  kind?: string;
  label?: string;
  description?: string;
  text?: string | string[];
  applicability?: string[];
  buttonName?: string;
  classificationId?: string;
  produces?: string[];
  prompts?: string[];
  enabled?: boolean;
  path?: string;
  source?: string;
  workspaceId?: string;
};

type ModelChoice = {
  id: string;
  label?: string;
  backendId?: string;
  backendLabel?: string;
  enabled?: boolean;
};

type UploadedImage = {
  id: string;
  label: string;
  dataUrl: string;
};

type ModelInvocation = {
  modelId?: string;
  backendId?: string;
  text?: string;
  latencyMs?: number;
  inputTokens?: number;
  outputTokens?: number;
  responseId?: string;
  debugLogPath?: string;
};

type VisualColumnRatios = {
  left: number;
  center: number;
  right: number;
};

type PromptCompositionEntry = {
  id: string;
  kind: "prompt" | "group";
  label?: string;
  transactionId?: string;
  operationId?: string;
  implementationId?: string;
  profileId?: string;
  continueOnError?: boolean;
  focalGroup?: string;
  parentGroup?: string;
  colorKey?: string;
  promptId?: string;
  modelId?: string;
  visibleToPeers: boolean;
  visibleToUpdates: boolean;
  workflowStep?: Record<string, unknown>;
  steps?: PromptCompositionEntry[];
};

type VisualDataFieldPlan = {
  name: string;
  inputPromptIds: string[];
  outputPromptIds: string[];
};

type VisualDataStack = {
  entry: PromptCompositionEntry;
  index: number;
  promptIds: string[];
  fields: VisualDataFieldPlan[];
};

type VisualFlowNodeData = {
  kind: "prompt" | "data" | "group" | "gap" | "dataDetail";
  color: string;
  content: ReactNode;
};

type VisualFlowNode = Node<VisualFlowNodeData, "visualPipeline">;

function VisualPipelineFlowNode({ data }: NodeProps<VisualFlowNode>) {
  return <div className={`visual-flow-node ${data.kind}`} style={{ "--visual-flow-color": data.color } as CSSProperties}>
    {data.kind === "prompt" && <><Handle id="sequence-in" type="target" position={Position.Left} style={{ top: "34%" }} /><Handle id="data-in" type="target" position={Position.Left} style={{ top: "68%" }} /></>}
    {data.kind === "prompt" && <Handle id="data-out" type="source" position={Position.Bottom} />}
    {data.kind === "data" && <><Handle id="data-target" type="target" position={Position.Right} /><Handle id="data-source" type="source" position={Position.Right} /></>}
    {data.kind === "dataDetail" && <Handle id="detail-target" type="target" position={Position.Left} />}
    {data.content}
  </div>;
}

const VISUAL_FLOW_NODE_TYPES = { visualPipeline: VisualPipelineFlowNode };

type OperationCatalogItem = OperationDef & {
  implements?: Record<string, unknown>;
  modelSelection?: { models?: string[]; strategy?: string };
};

type Props = {
  pageDefinition: WorkflowPageDefinition;
  workspaceId: string;
  workspaceLabel: string;
  models: ModelChoice[];
  operations: OperationCatalogItem[];
  operationImplementations: OperationCatalogItem[];
  onPageDefinitionSaved: () => Promise<unknown> | unknown;
};

const MANIFEST_PATH = "design/visual_image_diffs/default.visual_image_diff.json";
const STEP_APPLICABILITY = "visual_image_diff.pipeline_step";
const VISUAL_COLUMN_RATIOS_STORAGE = "workbench.visualImageDiff.columnRatios.v2";
const DEFAULT_VISUAL_COLUMN_RATIOS: VisualColumnRatios = { left: 1, center: 2.8, right: 1.9 };

function workflowStepFor(entry: PromptCompositionEntry, operation: OperationCatalogItem): Record<string, unknown> {
  if (entry.workflowStep) return entry.workflowStep;
  return {
    id: entry.transactionId || entry.id,
    label: entry.label || operation.label || operation.id,
    kind: "operation",
    operation: operation.id,
    ...(entry.implementationId ? { implementationVariant: entry.implementationId } : {}),
    inputs: Object.fromEntries(Object.keys(operation.inputs || {}).map((name) => [name, name])),
    outputs: Object.fromEntries(Object.keys(operation.outputs || {}).map((name) => [name, name])),
    parameters: {
      ...(entry.profileId ? { profile: entry.profileId } : {}),
      transaction: entry.transactionId || entry.id,
    },
    ...(entry.continueOnError ? { continue_on_error: true } : {}),
  };
}

function storedVisualColumnRatios(): VisualColumnRatios {
  if (typeof window === "undefined") return DEFAULT_VISUAL_COLUMN_RATIOS;
  try {
    const value = JSON.parse(window.localStorage.getItem(VISUAL_COLUMN_RATIOS_STORAGE) || "null") as Partial<VisualColumnRatios> | null;
    if (value && [value.left, value.center, value.right].every((part) => typeof part === "number" && Number.isFinite(part) && part > 0)) {
      return { left: value.left!, center: value.center!, right: value.right! };
    }
  } catch {
    // A malformed stored layout should never prevent the filesystem page from opening.
  }
  return DEFAULT_VISUAL_COLUMN_RATIOS;
}

function resizedPair(first: number, second: number, delta: number, firstMinimum: number, secondMinimum: number): [number, number] {
  const combined = first + second;
  const nextFirst = Math.min(combined - secondMinimum, Math.max(firstMinimum, first + delta));
  return [nextFirst, combined - nextFirst];
}

const modelOptionLabel = (model: ModelChoice) =>
  `${model.backendLabel || model.backendId || model.id} · ${model.label || model.id}`;

function operationInputValues(operation: OperationCatalogItem, availableData: Record<string, unknown>) {
  const values: Record<string, unknown> = {};
  const has = (name: string) => Object.prototype.hasOwnProperty.call(availableData, name);
  for (const name of Object.keys(operation.inputs || {})) {
    if (has(name)) {
      values[name] = availableData[name];
      continue;
    }
    const normalized = name.toLowerCase();
    const alias = normalized.includes("image")
      ? normalized.includes("previous") || normalized.includes("parent") || normalized.includes("before") ? "previous_image" : normalized.includes("images") ? "images" : "current_image"
      : normalized.includes("manifest") ? "source_manifest"
        : normalized.includes("sequence") || normalized.includes("command") || normalized.includes("context") ? "sequence_context"
          : "";
    if (alias && has(alias)) values[name] = availableData[alias];
  }
  return values;
}

async function request(path: string, init?: RequestInit) {
  const response = await fetch(path, {
    cache: "no-store",
    headers: { "Content-Type": "application/json", ...(init?.headers || {}) },
    ...init,
  });
  const raw = await response.text();
  let payload: Record<string, unknown> = {};
  try {
    payload = raw ? JSON.parse(raw) as Record<string, unknown> : {};
  } catch {
    throw new Error(raw || response.statusText);
  }
  if (!response.ok) {
    const detail = payload.detail || payload.error || response.statusText;
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  return payload;
}

async function readImageFile(file: File): Promise<UploadedImage> {
  const dataUrl = await new Promise<string>((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result || ""));
    reader.onerror = () => reject(reader.error || new Error(`Could not read ${file.name}`));
    reader.readAsDataURL(file);
  });
  return { id: `${Date.now()}:${file.name}:${Math.random()}`, label: file.name, dataUrl };
}

async function loadImage(source: string): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const image = new Image();
    image.onload = () => resolve(image);
    image.onerror = () => reject(new Error(`Could not load image input: ${source.slice(0, 80)}`));
    image.src = source;
  });
}

async function makeImageContactSheet(inputs: Array<{ label: string; source: string }>): Promise<string> {
  const limited = inputs.slice(0, 12);
  const images = await Promise.all(limited.map(async (input) => ({ ...input, image: await loadImage(input.source) })));
  const columns = Math.min(3, Math.max(1, images.length));
  const cellWidth = 512;
  const cellHeight = 544;
  const rows = Math.ceil(images.length / columns);
  const canvas = window.document.createElement("canvas");
  canvas.width = cellWidth * columns;
  canvas.height = cellHeight * rows;
  const context = canvas.getContext("2d");
  if (!context) throw new Error("This browser could not prepare the image contact sheet.");
  context.fillStyle = "#061118";
  context.fillRect(0, 0, canvas.width, canvas.height);
  context.font = "18px ui-monospace, monospace";
  images.forEach(({ image, label }, index) => {
    const column = index % columns;
    const row = Math.floor(index / columns);
    const left = column * cellWidth;
    const top = row * cellHeight;
    const scale = Math.min(cellWidth / image.naturalWidth, 512 / image.naturalHeight);
    const width = Math.max(1, Math.round(image.naturalWidth * scale));
    const height = Math.max(1, Math.round(image.naturalHeight * scale));
    context.fillStyle = "#4ee8dc";
    context.fillText(`${index + 1}. ${label}`, left + 10, top + 22, cellWidth - 20);
    context.imageSmoothingEnabled = false;
    context.drawImage(image, left + Math.floor((cellWidth - width) / 2), top + 32 + Math.floor((512 - height) / 2), width, height);
  });
  return canvas.toDataURL("image/png");
}

function documentsFrom(value: unknown): PromptChoice[] {
  if (!Array.isArray(value)) return [];
  return value.flatMap((item): PromptChoice[] => {
    if (!item || typeof item !== "object" || Array.isArray(item)) return [];
    const record = item as Record<string, unknown>;
    const document = record.document && typeof record.document === "object" && !Array.isArray(record.document)
      ? record.document as PromptChoice
      : record as PromptChoice;
    return document.id ? [{
      ...document,
      path: String(record.path || document.path || ""),
      source: String(record.source || document.source || ""),
      workspaceId: String(record.workspaceId || document.workspaceId || ""),
    }] : [];
  });
}

function editablePromptSource(prompt: PromptChoice) {
  return JSON.stringify(prompt, (key, value) =>
    ["path", "source", "workspaceId"].includes(key) ? undefined : value, 2);
}

function promptText(prompt: PromptChoice | undefined) {
  if (!prompt) return "";
  return Array.isArray(prompt.text) ? prompt.text.join("\n\n") : String(prompt.text || "");
}

function newPromptEntry(promptId: string, suffix = "") : PromptCompositionEntry {
  return {
    id: `${Date.now()}:${promptId}:${suffix}:${Math.random()}`,
    kind: "prompt",
    promptId,
    visibleToPeers: true,
    visibleToUpdates: false,
  };
}

function promptEntries(entries: PromptCompositionEntry[]): PromptCompositionEntry[] {
  return entries.flatMap((entry) => entry.kind === "group" ? promptEntries(entry.steps || []) : [entry]);
}

function promptEntryCount(entries: PromptCompositionEntry[]) {
  return promptEntries(entries).length;
}

function visualDataFieldPlan(
  entries: PromptCompositionEntry[],
  promptById: Map<string, PromptChoice>,
): VisualDataFieldPlan[] {
  const active = promptEntries(entries).flatMap((entry) => {
    const prompt = promptById.get(entry.promptId || "");
    return prompt ? [prompt] : [];
  });
  const fields = new Map<string, VisualDataFieldPlan>();
  const sourcePromptId = "visual_image_diff.pipeline.source";
  if (active.some((prompt) => prompt.id === sourcePromptId)) {
    fields.set("image_pair", { name: "image_pair", inputPromptIds: [sourcePromptId], outputPromptIds: [] });
    fields.set("transition_command", { name: "transition_command", inputPromptIds: [sourcePromptId], outputPromptIds: [] });
  }
  active.forEach((prompt) => (prompt.produces || []).forEach((name) => {
    const field = fields.get(name) || { name, inputPromptIds: [], outputPromptIds: [] };
    if (!field.outputPromptIds.includes(prompt.id)) field.outputPromptIds.push(prompt.id);
    fields.set(name, field);
  }));
  active.forEach((prompt) => {
    const ownOutputs = new Set(prompt.produces || []);
    const source = promptText(prompt);
    fields.forEach((field) => {
      if (ownOutputs.has(field.name) || !source.includes(field.name)) return;
      if (!field.inputPromptIds.includes(prompt.id)) field.inputPromptIds.push(prompt.id);
    });
  });
  return [...fields.values()];
}

function shuffledEntries(entries: PromptCompositionEntry[]) {
  const next = [...entries];
  for (let index = next.length - 1; index > 0; index -= 1) {
    const target = Math.floor(Math.random() * (index + 1));
    [next[index], next[target]] = [next[target], next[index]];
  }
  return next;
}

type VisualImageDiffOperationBinding = {
  operation?: OperationCatalogItem;
  variants: Array<OperationCatalogItem & OperationImplementationDef>;
  selectedImplementation?: OperationCatalogItem & OperationImplementationDef;
  promptResources: Array<{ step: PromptCompositionEntry; resource: PromptChoice }>;
  selectedUsesPrompts: boolean;
};

function resolveVisualImageDiffOperationBinding(
  entry: PromptCompositionEntry,
  prompts: PromptChoice[],
  operations: OperationCatalogItem[],
  operationImplementations: OperationCatalogItem[],
): VisualImageDiffOperationBinding {
  const operation = entry.kind === "group" && entry.operationId
    ? operations.find((candidate) => candidate.id === entry.operationId)
    : undefined;
  const variants = operation
    ? operationImplementations.filter((candidate): candidate is OperationCatalogItem & OperationImplementationDef => Boolean(candidate.implementation && relationshipIds(candidate.implements).includes(operation.id)))
    : [];
  const directImplementation = operation?.implementation && (!entry.implementationId || operation.id === entry.implementationId)
    ? operation as OperationCatalogItem & OperationImplementationDef
    : undefined;
  const selectedImplementation = directImplementation
    || variants.find((candidate) => candidate.id === entry.implementationId)
    || variants.find((candidate) => candidate.id === operation?.preferredImplementation)
    || variants.find((candidate) => candidate.implementation === "llm.complete");
  const promptResources = entry.kind === "group" ? promptEntries(entry.steps || []).flatMap((step) => {
    const resource = prompts.find((candidate) => candidate.id === step.promptId);
    return resource ? [{ step, resource }] : [];
  }) : [];
  return {
    operation,
    variants,
    selectedImplementation,
    promptResources,
    selectedUsesPrompts: selectedImplementation?.implementation === "llm.complete",
  };
}

function VisualImageDiffPlaygroundHeader({ entry, title, binding }: {
  entry: PromptCompositionEntry;
  title: string;
  binding: VisualImageDiffOperationBinding;
}) {
  const { operation, selectedImplementation, selectedUsesPrompts } = binding;
  return <div className="visual-image-diff-operation-binding">
    <span>{operation ? selectedUsesPrompts ? "WORKFLOW ITEM + PROMPT PLAYGROUND" : "WORKFLOW ITEM + NON-PROMPT OPERATION PLAYGROUND" : "WORKFLOW ITEM + OPERATION PLAYGROUND"}</span>
    <b>{operation ? selectedImplementation?.label || operation.label || operation.id : "Operation binding unresolved"}</b>
    <code>{operation ? `${entry.transactionId} → ${operation.id}${selectedImplementation ? ` → ${selectedImplementation.id}` : ""}` : entry.transactionId || title}</code>
  </div>;
}

function VisualImageDiffOperationSurface({ entry, title, workspaceId, prompts, models, operations, operationImplementations, availableData, onInspectPrompt, onWorkflowStep, onImplementation, onInvocationComplete, showHeader = false, binding: suppliedBinding }: {
  entry: PromptCompositionEntry;
  title: string;
  workspaceId: string;
  prompts: PromptChoice[];
  models: ModelChoice[];
  operations: OperationCatalogItem[];
  operationImplementations: OperationCatalogItem[];
  availableData: Record<string, unknown>;
  onInspectPrompt: (promptId: string) => void;
  onWorkflowStep: (id: string, workflowStep: Record<string, unknown>) => void;
  onImplementation: (id: string, implementationId: string) => void;
  onInvocationComplete: (outputs: Record<string, unknown>) => void;
  showHeader?: boolean;
  binding?: VisualImageDiffOperationBinding;
}) {
  const binding = suppliedBinding || resolveVisualImageDiffOperationBinding(entry, prompts, operations, operationImplementations);
  const { operation, variants, selectedImplementation, promptResources, selectedUsesPrompts } = binding;
  if (!operation) return entry.transactionId ? <div className="demo-notice visual-image-diff-operation-unresolved">
    {showHeader && <VisualImageDiffPlaygroundHeader entry={entry} title={title} binding={binding} />}
    <b>Operation binding unresolved</b>
    <span>The filesystem transaction <code>{entry.transactionId}</code> does not declare an Operation resource. Bind an Operation in the Visual Image Diff manifest before running or editing this workflow item.</span>
  </div> : null;
  const inputValues = operationInputValues(operation, availableData);
  return <>
    {showHeader && <VisualImageDiffPlaygroundHeader entry={entry} title={title} binding={binding} />}
    <section className="visual-image-diff-operation-surface" aria-label={`${title} workflow item and Operation playground`}>
      <div className="visual-image-diff-prompt-debug-bindings">
        <span>{selectedUsesPrompts ? "PROMPT RESOURCES EXECUTED BY THIS VERSION" : "NON-PROMPT IMPLEMENTATION"}</span>
        {selectedUsesPrompts
          ? promptResources.map(({ step, resource }) => <button type="button" key={step.id} onClick={() => onInspectPrompt(resource.id)}>{resource.buttonName || resource.label || resource.id}<small>{resource.id}</small></button>)
          : <p>This selected implementation calls Python and Prolog directly. It makes no Prompt or LLM request. Switch back to the Prompted LLM implementation to execute the nested Prompt resources.</p>}
      </div>
      <OperationPlayground
        key={`${entry.id}:${operation.id}`}
        workspaceId={workspaceId}
        operation={operation}
        variants={variants}
        models={models.filter((model) => model.enabled !== false).map((model) => ({ id: model.id, label: modelOptionLabel(model), enabled: model.enabled }))}
        workflowStep={workflowStepFor(entry, operation)}
        onWorkflowStepChange={(workflowStep) => onWorkflowStep(entry.id, workflowStep)}
        selectedImplementationVariant={selectedImplementation?.id}
        onImplementationVariantChange={(implementationId) => onImplementation(entry.id, implementationId)}
        inputValues={inputValues}
        expectedInputNames={Object.keys(inputValues)}
        onInvocationComplete={onInvocationComplete}
      />
    </section>
  </>;
}

type VisualCorrespondenceLine = {
  id: string;
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  colorKey: string;
  direction: "input" | "output";
};

function VisualCorrespondenceOverlay({ containerRef, version }: { containerRef: RefObject<HTMLDivElement | null>; version: string }) {
  const [lines, setLines] = useState<VisualCorrespondenceLine[]>([]);
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;
    let frame = 0;
    const update = () => {
      cancelAnimationFrame(frame);
      frame = requestAnimationFrame(() => {
        const containerRect = container.getBoundingClientRect();
        const promptRows = [...container.querySelectorAll<HTMLElement>(".visual-image-diff-subaccordion-strip-control.prompt")]
          .filter((node) => node.getClientRects().length > 0);
        const next: VisualCorrespondenceLine[] = [];
        container.querySelectorAll<HTMLElement>("[data-visual-field]").forEach((fieldNode) => {
          const fieldRect = fieldNode.getBoundingClientRect();
          const colorKey = fieldNode.dataset.stackKey || "S1";
          (["input", "output"] as const).forEach((direction) => {
            const promptIds = (fieldNode.dataset[direction === "input" ? "inputPromptIds" : "outputPromptIds"] || "").split(" ").filter(Boolean);
            promptIds.forEach((promptId) => {
              const promptNode = promptRows.find((node) => node.querySelector<HTMLSelectElement>('select[aria-label^="Prompt at position"]')?.value === promptId);
              if (!promptNode) return;
              const promptRect = promptNode.getBoundingClientRect();
              next.push({
                id: `${colorKey}:${fieldNode.dataset.visualField}:${direction}:${promptId}`,
                x1: fieldRect.right - containerRect.left,
                y1: fieldRect.top + fieldRect.height / 2 - containerRect.top,
                x2: promptRect.left - containerRect.left,
                y2: promptRect.top + promptRect.height / 2 - containerRect.top,
                colorKey,
                direction,
              });
            });
          });
        });
        setLines(next);
      });
    };
    update();
    const observer = new ResizeObserver(update);
    observer.observe(container);
    container.addEventListener("scroll", update, true);
    window.addEventListener("resize", update);
    return () => {
      cancelAnimationFrame(frame);
      observer.disconnect();
      container.removeEventListener("scroll", update, true);
      window.removeEventListener("resize", update);
    };
  }, [containerRef, version]);
  const color = (key: string) => ({ S1: "#4fc4d4", S2: "#7acb72", S3: "#e2b75b", S4: "#d17ad6", S5: "#ef7d85" }[key] || "#4fc4d4");
  return <svg className="visual-correspondence-overlay" aria-hidden="true">
    <defs><marker id="visual-correspondence-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="context-stroke" /></marker></defs>
    {lines.map((line) => {
      const bend = Math.max(18, (line.x2 - line.x1) * .45);
      const path = `M ${line.x1} ${line.y1} C ${line.x1 + bend} ${line.y1}, ${line.x2 - bend} ${line.y2}, ${line.x2} ${line.y2}`;
      return <path key={line.id} d={path} stroke={color(line.colorKey)} className={`visual-correspondence-line ${line.direction}`} markerStart={line.direction === "output" ? "url(#visual-correspondence-arrow)" : undefined} markerEnd={line.direction === "input" ? "url(#visual-correspondence-arrow)" : undefined} />;
    })}
  </svg>;
}

function VisualPipelineGraph({ stacks, promptById, prompts, models, generationOrder, selectedGroupId, availableData, busy, onSelectGroup, onInspectPrompt, onPrompt, onDropPrompt, onInsertPrompt, onMoveCall, onReplaceCall, onModel, onPeers, onUpdates, onMove, onRemove, onCopyGroup, onShuffleGroup, onClearGroup, onDataField, onRunEntry, onAddPrompt, onAddGroup, onRestore, onShuffleOrder, onClearOrder }: {
  stacks: VisualDataStack[];
  promptById: Map<string, PromptChoice>;
  prompts: PromptChoice[];
  models: ModelChoice[];
  generationOrder: PromptCompositionEntry[];
  selectedGroupId: string | null;
  availableData: Record<string, unknown>;
  busy: boolean;
  onSelectGroup: (id: string) => void;
  onInspectPrompt: (promptId: string) => void;
  onPrompt: (id: string, promptId: string, parentGroupId?: string) => void;
  onDropPrompt: (entry: PromptCompositionEntry, promptId: string, parentGroupId?: string) => void;
  onInsertPrompt: (promptId: string, parentGroupId: string, targetIndex: number) => void;
  onMoveCall: (entryId: string, sourceGroupId: string, targetGroupId: string, targetIndex: number) => void;
  onReplaceCall: (entryId: string, sourceGroupId: string, targetEntryId: string, targetGroupId: string) => void;
  onModel: (id: string, modelId: string, parentGroupId?: string) => void;
  onPeers: (id: string, value: boolean, parentGroupId?: string) => void;
  onUpdates: (id: string, value: boolean, parentGroupId?: string) => void;
  onMove: (id: string, targetIndex: number, parentGroupId?: string) => void;
  onRemove: (id: string, parentGroupId?: string) => void;
  onCopyGroup: (id: string) => void;
  onShuffleGroup: (id: string) => void;
  onClearGroup: (id: string) => void;
  onDataField: (name: string, value: string) => void;
  onRunEntry: (entry: PromptCompositionEntry, parentGroupId?: string) => void;
  onAddPrompt: (promptId: string) => void;
  onAddGroup: () => void;
  onRestore: () => void;
  onShuffleOrder: () => void;
  onClearOrder: () => void;
}) {
  const [addPromptId, setAddPromptId] = useState("");
  const [flowNodePositions, setFlowNodePositions] = useState<Record<string, { x: number; y: number }>>({});
  const resolvedPosition = (nodeId: string, fallback: { x: number; y: number }) => flowNodePositions[nodeId] || fallback;
  const colors: Record<string, string> = { S1: "#4fc4d4", S2: "#7acb72", S3: "#e2b75b", S4: "#d17ad6", S5: "#ef7d85" };
  const callRows = stacks.flatMap((stack) => (stack.entry.steps || []).map((step, promptIndex) => ({ stack, step, promptIndex })));
  const layout = new dagre.graphlib.Graph().setDefaultEdgeLabel(() => ({}));
  layout.setGraph({ rankdir: "TB", ranksep: 70, nodesep: 36, marginx: 20, marginy: 20 });
  callRows.forEach(({ step }) => layout.setNode(`prompt:${step.id}`, { width: 480, height: 52 }));
  callRows.slice(1).forEach(({ step }, index) => layout.setEdge(`prompt:${callRows[index].step.id}`, `prompt:${step.id}`));
  dagre.layout(layout);
  const promptPositions = new Map(callRows.map(({ step }, index) => {
    const point = layout.node(`prompt:${step.id}`) as { x: number; y: number } | undefined;
    return [step.id, { x: 650, y: (point?.y || index * 122) - 26 }];
  }));
  const nodes: VisualFlowNode[] = [];
  const edges: Edge[] = [];
  let dataCursorY = 20;
  let globalCallOrdinal = 1;
  stacks.forEach((stack, stackIndex) => {
    const key = stack.entry.colorKey || `S${stackIndex + 1}`;
    const color = colors[key] || colors.S1;
    const steps = stack.entry.steps || [];
    const naturalFirstPosition = steps[0] ? promptPositions.get(steps[0].id) : undefined;
    const desiredFirstY = Math.max(naturalFirstPosition?.y || dataCursorY + 58, dataCursorY + 58);
    const stackOffsetY = desiredFirstY - (naturalFirstPosition?.y || desiredFirstY);
    steps.forEach((step) => {
      const natural = promptPositions.get(step.id);
      if (natural && stackOffsetY) promptPositions.set(step.id, { ...natural, y: natural.y + stackOffsetY });
    });
    const firstPosition = steps[0] ? promptPositions.get(steps[0].id) : undefined;
    const groupTop = Math.max(0, (firstPosition?.y || dataCursorY) - 54);
    nodes.push({
      id: `group:${stack.entry.id}`,
      type: "visualPipeline",
      position: resolvedPosition(`group:${stack.entry.id}`, { x: 20, y: groupTop }),
      draggable: true,
      dragHandle: ".visual-flow-node-drag-handle",
      selectable: false,
      data: { kind: "group", color, content: <div className="visual-flow-group-controls">
        <span className="visual-flow-node-drag-handle" title={`Drag group ${key}`}>⠿</span><button type="button" title={`Group ${key}: ${stack.entry.label || "UNTITLED"} (${steps.length} calls)`} aria-pressed={selectedGroupId === stack.entry.id} onClick={() => onSelectGroup(stack.entry.id)}>{key} · {stack.entry.label || "UNTITLED"}<small>focal: {stack.entry.focalGroup || `stack_${stackIndex + 1}`}</small></button>
        <select title={`Model override for ${stack.entry.label || key}`} aria-label={`Graph model override for ${stack.entry.label || key}`} value={stack.entry.modelId || ""} onChange={(event) => onModel(stack.entry.id, event.target.value)}><option value="">Inherited model</option>{models.filter((model) => model.enabled !== false).map((model) => <option key={model.id} value={model.id}>{modelOptionLabel(model)}</option>)}</select>
        <button type="button" title={`Run group ${key}`} disabled={busy} onClick={() => onRunEntry(stack.entry)}>RUN</button><button type="button" title={`Copy group ${key}`} onClick={() => onCopyGroup(stack.entry.id)}>COPY</button><button type="button" title={`Shuffle calls in group ${key}`} disabled={steps.length < 2} onClick={() => onShuffleGroup(stack.entry.id)}>SHUFFLE</button><button type="button" title={`Clear calls in group ${key}`} disabled={!steps.length} onClick={() => onClearGroup(stack.entry.id)}>CLEAR</button><button type="button" title={`Remove group ${key}`} onClick={() => onRemove(stack.entry.id)}>REMOVE</button>
      </div> },
      style: { width: 570 },
    });
    const stackDataTop = Math.max(dataCursorY, groupTop + 58);
    stack.fields.forEach((field, fieldIndex) => {
      const nodeId = `data:${stack.entry.id}:${field.name}`;
      const value = availableData[field.name];
      const editorValue = value === undefined ? "" : typeof value === "string" ? value : JSON.stringify(value);
      nodes.push({
        id: nodeId,
        type: "visualPipeline",
        position: resolvedPosition(nodeId, { x: 30, y: stackDataTop + fieldIndex * 62 }),
        draggable: true,
        dragHandle: ".visual-flow-node-drag-handle",
        data: {
          kind: "data",
          color,
          content: <label className="visual-flow-data-content" title={`Datafield ${field.name}`}>
            <code><span className="visual-flow-node-drag-handle" title={`Drag ${field.name} node`}>⠿</span>{field.name}</code>
            <input title={`Edit datafield ${field.name}`} aria-label={`Edit graph datafield ${field.name}`} value={editorValue} placeholder="Not produced" onChange={(event) => onDataField(field.name, event.target.value)} />
            <label className="visual-flow-data-upload-inline" title={`Upload file into ${field.name}`}>
              <span>UP</span>
              <input type="file" onChange={(event) => {
                const file = event.target.files?.[0];
                if (!file) return;
                const reader = new FileReader();
                reader.onload = () => onDataField(field.name, String(reader.result || ""));
                if (file.type.startsWith("image/")) reader.readAsDataURL(file);
                else reader.readAsText(file);
              }} />
            </label>
          </label>,
        },
        style: { width: 400 },
      });
      field.inputPromptIds.filter((id) => stack.promptIds.includes(id)).forEach((promptId) => {
        const target = steps.find((step) => step.promptId === promptId);
        if (target) edges.push({ id: `input:${nodeId}:${target.id}`, source: nodeId, sourceHandle: "data-source", target: `prompt:${target.id}`, targetHandle: "data-in", type: "smoothstep", markerEnd: { type: MarkerType.ArrowClosed }, style: { stroke: color, strokeWidth: 1.6 } });
      });
      field.outputPromptIds.filter((id) => stack.promptIds.includes(id)).forEach((promptId) => {
        const source = steps.find((step) => step.promptId === promptId);
        if (source) edges.push({ id: `output:${source.id}:${nodeId}`, source: `prompt:${source.id}`, sourceHandle: "data-out", target: nodeId, targetHandle: "data-target", type: "smoothstep", markerEnd: { type: MarkerType.ArrowClosed }, animated: true, style: { stroke: color, strokeWidth: 1.8 } });
      });
    });
    dataCursorY = stackDataTop + Math.max(stack.fields.length * 62, steps.length * 122) + 70;
    steps.forEach((step, promptIndex) => {
      const prompt = promptById.get(step.promptId || "");
      const callOrdinal = globalCallOrdinal;
      globalCallOrdinal += 1;
      nodes.push({
        id: `prompt:${step.id}`,
        type: "visualPipeline",
        position: resolvedPosition(`prompt:${step.id}`, promptPositions.get(step.id) || { x: 650, y: callOrdinal * 100 }),
        draggable: true,
        dragHandle: ".visual-flow-node-drag-handle",
        data: { kind: "prompt", color, content: <div className="visual-flow-prompt-content" title={`Prompt call ${callOrdinal} in ${stack.entry.label || key}`} draggable onDragStart={(event) => { event.dataTransfer.effectAllowed = "move"; event.dataTransfer.setData(VISUAL_ORDER_DRAG_TYPE, `${stack.entry.id}\n${step.id}`); }} onDragOver={(event) => { if (event.dataTransfer.types.includes(VISUAL_PROMPT_DRAG_TYPE) || event.dataTransfer.types.includes(VISUAL_ORDER_DRAG_TYPE)) event.preventDefault(); }} onDrop={(event) => { const orderEntry = draggedOrderEntry(event); if (orderEntry?.parentGroupId) { event.preventDefault(); event.stopPropagation(); onReplaceCall(orderEntry.entryId, orderEntry.parentGroupId, step.id, stack.entry.id); return; } const droppedPromptId = draggedPromptId(event); if (!droppedPromptId) return; event.preventDefault(); onDropPrompt(step, droppedPromptId, stack.entry.id); }}>
          <b title={`Global call ${callOrdinal}`}><span className="visual-flow-node-drag-handle" title={`Drag call ${callOrdinal} node`}>⠿</span>{callOrdinal}</b><select title={`Prompt selector for call ${callOrdinal}`} aria-label={`Graph Prompt call ${callOrdinal}`} value={step.promptId || ""} onFocus={() => step.promptId && onInspectPrompt(step.promptId)} onChange={(event) => { onPrompt(step.id, event.target.value, stack.entry.id); onInspectPrompt(event.target.value); }}>{prompts.map((choice) => <option key={choice.id} value={choice.id}>{choice.buttonName || choice.label || choice.id}</option>)}</select>
          <label title="Visible to peer prompt types"><input type="checkbox" checked={step.visibleToPeers} onChange={(event) => onPeers(step.id, event.target.checked, stack.entry.id)} />P</label><label title="Visible to later updates of this prompt type"><input type="checkbox" checked={step.visibleToUpdates} onChange={(event) => onUpdates(step.id, event.target.checked, stack.entry.id)} />U</label>
          <select title={`Move call ${callOrdinal} to another position`} aria-label={`Graph order for ${prompt?.buttonName || step.promptId}`} value={promptIndex} onChange={(event) => onMove(step.id, Number(event.target.value), stack.entry.id)}>{steps.map((_, index) => <option key={index} value={index}>{index + 1}</option>)}</select>
          <button type="button" title={`Run call ${callOrdinal}`} disabled={busy || !step.promptId} onClick={() => onRunEntry(step, stack.entry.id)}>RUN</button><button type="button" title={`Remove call ${callOrdinal}`} onClick={() => onRemove(step.id, stack.entry.id)}>×</button>
        </div> },
        style: { width: 480 },
      });
    });
    Array.from({ length: steps.length + 1 }, (_, insertionIndex) => {
      const before = steps[insertionIndex - 1] ? promptPositions.get(steps[insertionIndex - 1].id)?.y : undefined;
      const after = steps[insertionIndex] ? promptPositions.get(steps[insertionIndex].id)?.y : undefined;
      const y = before === undefined ? (after || groupTop) - 34 : after === undefined ? before + 62 : (before + after) / 2;
      const position = globalCallOrdinal - steps.length + insertionIndex;
      const gapNodeId = `gap:${stack.entry.id}:${insertionIndex}`;
      nodes.push({ id: gapNodeId, type: "visualPipeline", position: resolvedPosition(gapNodeId, { x: 608, y }), draggable: true, dragHandle: ".visual-flow-gap", selectable: false, data: { kind: "gap", color, content: <button type="button" className="visual-flow-gap" title={`Insert here at position ${position}, or move a call here`} aria-label={`Insert or move Prompt to graph position ${position}`} onDragOver={(event) => { if (event.dataTransfer.types.includes(VISUAL_PROMPT_DRAG_TYPE) || event.dataTransfer.types.includes(VISUAL_ORDER_DRAG_TYPE)) event.preventDefault(); }} onDrop={(event) => { const orderEntry = draggedOrderEntry(event); if (orderEntry?.parentGroupId) { event.preventDefault(); event.stopPropagation(); onMoveCall(orderEntry.entryId, orderEntry.parentGroupId, stack.entry.id, insertionIndex); return; } const promptId = draggedPromptId(event); if (!promptId) return; event.preventDefault(); event.stopPropagation(); onInsertPrompt(promptId, stack.entry.id, insertionIndex); }}>+</button> }, style: { width: 28 } });
    });
  });
  callRows.slice(1).forEach(({ step }, index) => edges.push({ id: `sequence:${callRows[index].step.id}:${step.id}`, source: `prompt:${callRows[index].step.id}`, sourceHandle: "data-out", target: `prompt:${step.id}`, targetHandle: "sequence-in", type: "smoothstep", style: { stroke: "#77e6dc", strokeWidth: 2.4 }, zIndex: -1 }));
  return <section className="visual-pipeline-graph-mode" aria-label="Visual pipeline correspondence graph">
    <div className="visual-pipeline-graph-legend"><b>DATA AND RESULTS</b><span>Prompt contract correspondence · live from the two-column model</span><b>AUTHORING</b></div>
    <div className="visual-pipeline-graph-toolbar" aria-label="Graph pipeline authoring controls">
      <select title="Select a Prompt to append to the selected group" aria-label="Prompt resource to add in graph" value={addPromptId} onChange={(event) => setAddPromptId(event.target.value)}><option value="">Select Prompt to add</option>{prompts.map((prompt) => <option key={prompt.id} value={prompt.id}>{prompt.buttonName || prompt.label || prompt.id}</option>)}</select>
      <button type="button" title="Add the selected Prompt call" disabled={busy || !addPromptId} onClick={() => onAddPrompt(addPromptId)}>ADD PROMPT</button>
      <button type="button" title="Add a new prompt group" disabled={busy} onClick={onAddGroup}>ADD GROUP</button>
      <button type="button" title="Restore the filesystem profile group ordering" disabled={busy} onClick={onRestore}>RESTORE</button>
      <button type="button" title="Shuffle all top-level groups" disabled={busy || generationOrder.length < 2} onClick={onShuffleOrder}>SHUFFLE ALL</button>
      <button type="button" title="Clear all top-level groups and calls" disabled={busy || !generationOrder.length} onClick={onClearOrder}>CLEAR ALL</button>
    </div>
    <div className="visual-react-flow-canvas" aria-label="Automatically laid out editable Visual Pipeline graph">
      <ReactFlow nodes={nodes} edges={edges} nodeTypes={VISUAL_FLOW_NODE_TYPES} nodesDraggable nodesConnectable={false} elementsSelectable elevateNodesOnSelect fitView fitViewOptions={{ padding: .12 }} minZoom={.25} maxZoom={1.8}
        onNodeDragStop={(_event, node) => {
          setFlowNodePositions((current) => ({ ...current, [String(node.id)]: { x: node.position.x, y: node.position.y } }));
        }}>
        <Background gap={24} size={1} color="#24444d" />
        <MiniMap pannable zoomable nodeColor={(node) => String((node.data as VisualFlowNodeData)?.color || "#4fc4d4")} />
        <Controls showInteractive={false} />
      </ReactFlow>
    </div>
  </section>;
}

function VisualStackIdentity({ entry, index, side }: { entry: PromptCompositionEntry; index: number; side: "data" | "authoring" }) {
  const key = entry.colorKey || `S${index + 1}`;
  return <header className="visual-corresponding-stack-identity" data-stack-key={key}>
    <b><span>{key}</span> · STACK {index + 1} — {entry.label || "UNTITLED"}</b>
    <small>focal group: <code>{entry.focalGroup || `stack_${index + 1}`}</code></small>
    {entry.parentGroup && <small>parent: <code>{entry.parentGroup}</code></small>}
    <small>{side === "data" ? "DATA AND RESULTS" : "AUTHORING"} · color/key: {key}</small>
  </header>;
}

function CompositionOrderAccordionItem({ entry, ordinal, index, siblingCount, stackId, parentGroupId, selectedGroupId, inspectedPromptId, workspaceId, prompts, models, operations, operationImplementations, availableData, busy, modeFor, onMode, onRunEntry, onInspectPrompt, onSelectGroup, onShuffleGroup, onCopyGroup, onClearGroup, onWorkflowStep, onImplementation, onInvocationComplete, onPeers, onUpdates, onPrompt, onDropPrompt, onModel, onMove, onRemove }: {
  entry: PromptCompositionEntry;
  ordinal: string;
  index: number;
  siblingCount: number;
  stackId: string;
  parentGroupId?: string;
  selectedGroupId: string | null;
  inspectedPromptId: string;
  workspaceId: string;
  prompts: PromptChoice[];
  models: ModelChoice[];
  operations: OperationCatalogItem[];
  operationImplementations: OperationCatalogItem[];
  availableData: Record<string, unknown>;
  busy: boolean;
  modeFor: (entryId: string, fallback?: AccordionDisplayMode) => AccordionDisplayMode;
  onMode: (entryId: string, mode: AccordionDisplayMode) => void;
  onRunEntry: (entry: PromptCompositionEntry, ordinal: string, parentGroupId?: string) => void;
  onInspectPrompt: (promptId: string) => void;
  onSelectGroup: (id: string) => void;
  onShuffleGroup: (id: string) => void;
  onCopyGroup: (id: string) => void;
  onClearGroup: (id: string) => void;
  onWorkflowStep: (id: string, workflowStep: Record<string, unknown>) => void;
  onImplementation: (id: string, implementationId: string) => void;
  onInvocationComplete: (outputs: Record<string, unknown>) => void;
  onPeers: (id: string, value: boolean, parentGroupId?: string) => void;
  onUpdates: (id: string, value: boolean, parentGroupId?: string) => void;
  onPrompt: (id: string, promptId: string, parentGroupId?: string) => void;
  onDropPrompt: (entry: PromptCompositionEntry, promptId: string, parentGroupId?: string) => void;
  onModel: (id: string, modelId: string, parentGroupId?: string) => void;
  onMove: (id: string, targetIndex: number, parentGroupId?: string) => void;
  onRemove: (id: string, parentGroupId?: string) => void;
}) {
  const isGroup = entry.kind === "group";
  const prompt = prompts.find((candidate) => candidate.id === entry.promptId);
  const title = isGroup ? entry.label ? `[group] ${entry.label}` : "[group]" : prompt?.buttonName || prompt?.label || entry.promptId || "Select prompt";
  const selected = isGroup && selectedGroupId === entry.id;
  const inspected = !isGroup && Boolean(entry.promptId) && inspectedPromptId === entry.promptId;
  const inspect = () => { if (!isGroup && entry.promptId) onInspectPrompt(entry.promptId); };
  const childStackId = `visual-image-diff-uix-group-${entry.id}`;
  const operationBinding = resolveVisualImageDiffOperationBinding(entry, prompts, operations, operationImplementations);
  const [playgroundOpen, setPlaygroundOpen] = useState(false);
  const groupHeaderActions = isGroup ? <div className="generation-order-group-actions visual-image-diff-subaccordion-header-actions">
    <button type="button" className="generation-order-group-picker" aria-label={`Select group ${ordinal} for insertion in subaccordion`} aria-pressed={selected} onClick={() => onSelectGroup(entry.id)}>{selected ? "SELECTED" : "SELECT"}</button>
    <button type="button" className="generation-order-group-copy" aria-label={`Copy group ${ordinal} in subaccordion`} onClick={() => onCopyGroup(entry.id)}>COPY</button>
    <button type="button" className="generation-order-group-shuffle" aria-label={`Shuffle group ${ordinal} in subaccordion`} disabled={(entry.steps?.length || 0) < 2} onClick={() => onShuffleGroup(entry.id)}>SHUFFLE</button>
    <button type="button" className="generation-order-group-clear" aria-label={`Clear group ${ordinal} in subaccordion`} disabled={!entry.steps?.length} onClick={() => onClearGroup(entry.id)}>CLEAR</button>
  </div> : undefined;
  const playgroundFooter = isGroup ? <div className="visual-image-diff-playground-footer">
    <div className="visual-image-diff-playground-footer-line">
      <VisualImageDiffPlaygroundHeader entry={entry} title={title} binding={operationBinding} />
      <button type="button" aria-expanded={playgroundOpen} onClick={() => setPlaygroundOpen((current) => !current)}>INPUT / OUTPUT</button>
      <button type="button" disabled={busy} onClick={() => onRunEntry(entry, ordinal, parentGroupId)}>RUN GROUP</button>
    </div>
    {playgroundOpen && <VisualImageDiffOperationSurface entry={entry} title={title} workspaceId={workspaceId} prompts={prompts} models={models} operations={operations} operationImplementations={operationImplementations} availableData={availableData} binding={operationBinding} onInspectPrompt={onInspectPrompt} onWorkflowStep={onWorkflowStep} onImplementation={onImplementation} onInvocationComplete={onInvocationComplete} />}
  </div> : null;
  return <ThreeStateAccordionMember
    stackId={stackId}
    memberKey={entry.id}
    managedOrder={index}
    label={`${ordinal} · ${isGroup ? "GROUP" : "PROMPT STEP"}`}
    value={title}
    detail={isGroup ? `${entry.steps?.length || 0} nested prompt steps` : prompt?.id || "Select a Prompt resource"}
    mode={modeFor(entry.id, isGroup ? "scroll" : "strip")}
    onChange={(value) => { onMode(entry.id, value); inspect(); }}
    baseClass={`english-workflow-contract-panel visual-image-diff-subaccordion-item ${selected ? "selected" : ""} ${inspected ? "inspected" : ""}`}
    scrollSize="420px"
    itemHeader={isGroup ? groupHeaderActions : null}
    footer={playgroundFooter}
    stripContent={(cycleMode) => <div className={`visual-image-diff-subaccordion-strip-control ${isGroup ? "group" : "prompt"} ${parentGroupId ? "nested" : "top-level"}`} onPointerDown={inspect} onFocusCapture={inspect} onDragOver={(event) => { if (event.dataTransfer.types.includes(VISUAL_PROMPT_DRAG_TYPE) || event.dataTransfer.types.includes(VISUAL_ORDER_DRAG_TYPE)) event.preventDefault(); }} onDrop={(event) => { const orderEntry = draggedOrderEntry(event); if (orderEntry && parentGroupId === orderEntry.parentGroupId) { event.preventDefault(); event.stopPropagation(); onMove(orderEntry.entryId, index, parentGroupId); return; } const promptId = draggedPromptId(event); if (!promptId) return; event.preventDefault(); event.stopPropagation(); onDropPrompt(entry, promptId, parentGroupId); }}>
      <button type="button" className="visual-image-diff-subaccordion-strip-ordinal" aria-label={`Cycle accordion size for ${title} at position ${ordinal}`} title="Cycle this accordion through strip, scrolling, and full states" onClick={cycleMode}>{ordinal}</button>
      <button type="button" className="visual-image-diff-order-title" disabled={busy || (!isGroup && !entry.promptId)} aria-label={`Run ${title} at position ${ordinal} from compact strip`} title="Run only this visual prompt step" onClick={() => onRunEntry(entry, ordinal, parentGroupId)}>{title}</button>
      <span className="generation-order-flags">
        <span>visible</span>
        <label title="Let later prompt types see this value."><input type="checkbox" aria-label={`Share ${title} with peers at position ${ordinal} in compact strip`} checked={entry.visibleToPeers} onChange={(event) => onPeers(entry.id, event.target.checked, parentGroupId)} /><span>peers</span></label>
        <label title="Let a later occurrence of this prompt type see and update its previous value."><input type="checkbox" aria-label={`Share ${title} with updates at position ${ordinal} in compact strip`} checked={entry.visibleToUpdates} onChange={(event) => onUpdates(entry.id, event.target.checked, parentGroupId)} /><span>updates</span></label>
      </span>
      <select aria-label={`Prompt at position ${ordinal} in compact strip`} value={entry.promptId || ""} disabled={isGroup} onChange={(event) => { onPrompt(entry.id, event.target.value, parentGroupId); onInspectPrompt(event.target.value); }}>
        {isGroup ? <option value="">Simultaneous group</option> : <><option value="">Select prompt</option>{prompts.map((choice) => <option key={choice.id} value={choice.id}>{choice.buttonName || choice.label || choice.id}</option>)}</>}
      </select>
      {!parentGroupId && <select aria-label={`Model override at position ${ordinal} in compact strip`} value={entry.modelId || ""} onChange={(event) => onModel(entry.id, event.target.value)}><option value="">Inherited model</option>{models.filter((model) => model.enabled !== false).map((model) => <option key={model.id} value={model.id}>{modelOptionLabel(model)}</option>)}</select>}
      <span className="visual-image-diff-drag-order" draggable role="button" tabIndex={0} aria-label={`Drag ${title} to reorder position ${ordinal} in compact strip`} title="Drag onto another item in this pipeline stack to reorder" onDragStart={(event) => { event.dataTransfer.effectAllowed = "move"; event.dataTransfer.setData(VISUAL_ORDER_DRAG_TYPE, `${parentGroupId || "__root__"}\n${entry.id}`); }}>⋮⋮</span>
      <select className="visual-image-diff-order-position" aria-label={`Order ${title} at position ${ordinal} in compact strip`} value={index} onChange={(event) => onMove(entry.id, Number(event.target.value), parentGroupId)}>{Array.from({ length: siblingCount }, (_, targetIndex) => <option key={targetIndex} value={targetIndex}>Position {targetIndex + 1}</option>)}</select>
      {!isGroup && <button type="button" className="visual-image-diff-override-step" disabled={!entry.promptId} aria-label={`Override ${title} at position ${ordinal} in compact strip`} title="Open the selected Prompt resource to edit or create a child override" onClick={() => entry.promptId && onInspectPrompt(entry.promptId)}>OVERRIDE</button>}
      <button type="button" className="visual-image-diff-remove-step" aria-label={`Remove ${title} at position ${ordinal} in compact strip`} title="Remove this item from the pipeline" onClick={() => onRemove(entry.id, parentGroupId)}>REMOVE</button>
    </div>}
  >
    {isGroup && <div className="visual-image-diff-subaccordion-group-body">
      <VisualStackIdentity entry={entry} index={index} side="authoring" />
      {entry.steps?.length ? <ThreeStateAccordionStack id={childStackId} className="visual-image-diff-uix-nested-stack" controlsLabel={`${ordinal} · NESTED PROMPT STACK`}>
        {entry.steps.map((child, childIndex) => <CompositionOrderAccordionItem key={child.id} entry={child} ordinal={`${ordinal}.${childIndex + 1}`} index={childIndex} siblingCount={entry.steps?.length || 0} stackId={childStackId} parentGroupId={entry.id} selectedGroupId={selectedGroupId} inspectedPromptId={inspectedPromptId} workspaceId={workspaceId} prompts={prompts} models={models} operations={operations} operationImplementations={operationImplementations} availableData={availableData} busy={busy} modeFor={modeFor} onMode={onMode} onRunEntry={onRunEntry} onInspectPrompt={onInspectPrompt} onSelectGroup={onSelectGroup} onShuffleGroup={onShuffleGroup} onCopyGroup={onCopyGroup} onClearGroup={onClearGroup} onWorkflowStep={onWorkflowStep} onImplementation={onImplementation} onInvocationComplete={onInvocationComplete} onPeers={onPeers} onUpdates={onUpdates} onPrompt={onPrompt} onDropPrompt={onDropPrompt} onModel={onModel} onMove={onMove} onRemove={onRemove} />)}
      </ThreeStateAccordionStack> : <p>Empty simultaneous prompt group. Select it, then use an inline + step button.</p>}
    </div>}
  </ThreeStateAccordionMember>;
}

export function VisualImageDiffPage({ pageDefinition, workspaceId, workspaceLabel, models, operations, operationImplementations, onPageDefinitionSaved }: Props) {
  const [document, setDocument] = useState<VisualImageDiffDocument | null>(null);
  const [prompts, setPrompts] = useState<PromptChoice[]>([]);
  const [promptDrafts, setPromptDrafts] = useState<Record<string, string>>({});
  const [promptSavedContent, setPromptSavedContent] = useState<Record<string, string>>({});
  const [promptDiskContent, setPromptDiskContent] = useState<Record<string, string>>({});
  const [promptDraftValidity, setPromptDraftValidity] = useState<Record<string, boolean>>({});
  const [savingPromptId, setSavingPromptId] = useState("");
  const [reloadingPromptId, setReloadingPromptId] = useState("");
  const [profileStepIds, setProfileStepIds] = useState<string[]>([]);
  const [profileGroups, setProfileGroups] = useState<PromptGroupDefinition[]>([]);
  const [generationOrder, setGenerationOrder] = useState<PromptCompositionEntry[]>([]);
  const [selectedGroupId, setSelectedGroupId] = useState<string | null>(null);
  const [inspectedPromptId, setInspectedPromptId] = useState("");
  const [message, setMessage] = useState("Loading filesystem resources…");
  const [uploadedImages, setUploadedImages] = useState<UploadedImage[]>([]);
  const [runModel, setRunModel] = useState("");
  const [running, setRunning] = useState(false);
  const [runError, setRunError] = useState("");
  const [runResult, setRunResult] = useState<ModelInvocation | null>(null);
  const [submittedImageCount, setSubmittedImageCount] = useState(0);
  const [workflowData, setWorkflowData] = useState<Record<string, unknown>>({});
  const [plannedDataFields, setPlannedDataFields] = useState<VisualDataFieldPlan[]>([]);
  const [generatedDataFieldNames, setGeneratedDataFieldNames] = useState<string[]>([]);
  const [subaccordionModes, setSubaccordionModes] = useState<Record<string, AccordionDisplayMode>>({});
  const [presentationMode, setPresentationMode] = useState<"columns" | "graph">("columns");
  const [columnRatios, setColumnRatios] = useState<VisualColumnRatios>(storedVisualColumnRatios);
  const columnsRef = useRef<HTMLDivElement>(null);
  const initializedWorkspace = useRef("");
  const [modes, setModes] = useState<Record<string, AccordionDisplayMode>>({
    sequence: "scroll",
    group: "scroll",
    groupAccordion: "scroll",
    prompt: "scroll",
    composed: "scroll",
    pageSpecification: "strip",
    context: "scroll",
    outputs: "scroll",
  });
  const mode = (key: string, fallback: AccordionDisplayMode = "scroll") => modes[key] || fallback;
  const setMode = (key: string, value: AccordionDisplayMode) => setModes((current) => ({ ...current, [key]: value }));
  const subaccordionMode = (entryId: string, fallback: AccordionDisplayMode = "scroll") => subaccordionModes[entryId] || fallback;
  const setSubaccordionMode = (entryId: string, value: AccordionDisplayMode) => setSubaccordionModes((current) => ({ ...current, [entryId]: value }));

  useEffect(() => {
    window.localStorage.setItem(VISUAL_COLUMN_RATIOS_STORAGE, JSON.stringify(columnRatios));
  }, [columnRatios]);

  const nudgeColumnBoundary = (boundary: "left" | "right", delta: number) => {
    setColumnRatios((current) => {
      if (boundary === "left") {
        const [left, center] = resizedPair(current.left, current.center, delta, 0.55, 0.75);
        return { ...current, left, center };
      }
      const [center, right] = resizedPair(current.center, current.right, delta, 0.75, 0.55);
      return { ...current, center, right };
    });
  };

  const beginColumnResize = (boundary: "left" | "right", event: ReactPointerEvent<HTMLDivElement>) => {
    if (window.matchMedia("(max-width: 1180px)").matches || !columnsRef.current) return;
    event.preventDefault();
    const frame = columnsRef.current;
    const startX = event.clientX;
    const start = columnRatios;
    const total = start.left + start.center + start.right;
    const usableWidth = Math.max(1, frame.getBoundingClientRect().width - 16);
    const leftMinimum = Math.min(start.left, 220 / usableWidth * total);
    const centerMinimum = Math.min(start.center, 280 / usableWidth * total);
    const rightMinimum = Math.min(start.right, 220 / usableWidth * total);

    const onPointerMove = (moveEvent: PointerEvent) => {
      const delta = (moveEvent.clientX - startX) / usableWidth * total;
      if (boundary === "left") {
        const [left, center] = resizedPair(start.left, start.center, delta, leftMinimum, centerMinimum);
        setColumnRatios({ left, center, right: start.right });
      } else {
        const [center, right] = resizedPair(start.center, start.right, delta, centerMinimum, rightMinimum);
        setColumnRatios({ left: start.left, center, right });
      }
    };
    const stop = () => {
      window.removeEventListener("pointermove", onPointerMove);
      window.removeEventListener("pointerup", stop);
      window.removeEventListener("pointercancel", stop);
      window.document.body.classList.remove("resizing-visual-image-columns");
    };

    window.document.body.classList.add("resizing-visual-image-columns");
    window.addEventListener("pointermove", onPointerMove);
    window.addEventListener("pointerup", stop);
    window.addEventListener("pointercancel", stop);
  };

  const columnGridStyle = {
    "--visual-image-left-width": `${columnRatios.left}fr`,
    "--visual-image-center-width": `${columnRatios.center}fr`,
    "--visual-image-right-width": `${columnRatios.right}fr`,
  } as CSSProperties;
  const totalColumnRatio = columnRatios.left + columnRatios.center + columnRatios.right;

  useEffect(() => {
    const enabled = models.filter((model) => model.enabled !== false);
    if (!runModel || !enabled.some((model) => model.id === runModel)) setRunModel(enabled[0]?.id || "");
  }, [models, runModel]);

  useEffect(() => {
    if (!inspectedPromptId) return;
    const promptMember = pageDefinition.layout.columns
      .find((column) => column.id === "right")?.members
      .map((member) => typeof member === "string" ? null : member)
      .find((member) => member?.options?.promptId === inspectedPromptId);
    if (!promptMember) return;
    const modeKey = `prompt:${promptMember.id}`;
    setModes((current) => current[modeKey] === "scroll" ? current : { ...current, [modeKey]: "scroll" });
    const frame = window.requestAnimationFrame(() => {
      const panel = window.document.getElementById(promptMember.id);
      panel?.scrollIntoView({ behavior: "smooth", block: "start", inline: "nearest" });
    });
    return () => window.cancelAnimationFrame(frame);
  }, [inspectedPromptId, pageDefinition]);

  useEffect(() => {
    let cancelled = false;
    setWorkflowData({});
    setPlannedDataFields([]);
    setGeneratedDataFieldNames([]);
    setMessage("Loading filesystem resources…");
    Promise.all([
      request(`/workbench/workspaces/${encodeURIComponent(workspaceId)}/file?path=${encodeURIComponent(MANIFEST_PATH)}`),
      request(`/workbench/workspaces/${encodeURIComponent(workspaceId)}/prompts`),
    ]).then(([manifestPayload, promptPayload]) => {
      if (cancelled) return;
      const file = manifestPayload.file && typeof manifestPayload.file === "object"
        ? manifestPayload.file as Record<string, unknown>
        : {};
      const nextDocument = JSON.parse(String(file.content || "{}")) as VisualImageDiffDocument;
      const library = promptPayload.promptLibrary && typeof promptPayload.promptLibrary === "object"
        ? promptPayload.promptLibrary as Record<string, unknown>
        : {};
      const hierarchy = library.hierarchy && typeof library.hierarchy === "object"
        ? library.hierarchy as Record<string, unknown>
        : {};
      const choices = new Map<string, PromptChoice>();
      [promptPayload.prompts, hierarchy.prompts, hierarchy.promptImplementations, hierarchy.promptProfiles]
        .flatMap(documentsFrom)
        .forEach((prompt) => choices.set(prompt.id, prompt));
      const nextPrompts = [...choices.values()].map((prompt) => ({
        ...prompt,
        workspaceId: prompt.workspaceId || workspaceId,
      }));
      const profile = choices.get(nextDocument.promptProfileId);
      const classifiedSteps = nextPrompts
        .filter((prompt) => prompt.applicability?.includes(STEP_APPLICABILITY))
        .sort((left, right) => String(left.classificationId || "￿").localeCompare(String(right.classificationId || "￿")));
      setDocument(nextDocument);
      setPrompts(classifiedSteps);
      const initialSources = Object.fromEntries(classifiedSteps.map((prompt) => [prompt.id, editablePromptSource(prompt)]));
      setPromptDrafts(initialSources);
      setPromptSavedContent(initialSources);
      setPromptDiskContent(initialSources);
      setPromptDraftValidity(Object.fromEntries(classifiedSteps.map((prompt) => [prompt.id, true])));
      if (initializedWorkspace.current !== workspaceId) {
        const profileSteps = (profile?.prompts || []).filter((id) => choices.has(id));
        const initialPromptIds = profileSteps.length ? profileSteps : classifiedSteps.map((prompt) => prompt.id);
        const configuredGroups = (nextDocument.promptGroups || []).filter((group) => group.prompts.some((id) => choices.has(id)));
        const groupedEntries: PromptCompositionEntry[] = configuredGroups.map((group) => ({
          id: `${workspaceId}:${group.id}:group`,
          kind: "group",
          label: group.label,
          transactionId: group.transaction,
          operationId: group.operation,
          implementationId: group.implementation,
          profileId: group.profile,
          continueOnError: group.continueOnError,
          focalGroup: group.focalGroup,
          parentGroup: group.parentGroup,
          colorKey: group.colorKey,
          visibleToPeers: true,
          visibleToUpdates: false,
          steps: group.prompts.filter((id) => choices.has(id)).map((promptId, index) => newPromptEntry(promptId, `${group.id}:${index}`)),
        }));
        const profileGroupId = groupedEntries[0]?.id || `${workspaceId}:${nextDocument.promptProfileId}:group`;
        setProfileStepIds(initialPromptIds);
        setProfileGroups(configuredGroups);
        setGenerationOrder(groupedEntries.length ? groupedEntries : [{
          id: profileGroupId,
          kind: "group",
          visibleToPeers: true,
          visibleToUpdates: false,
          steps: initialPromptIds.map((promptId, index) => newPromptEntry(promptId, `profile:${index}`)),
        }]);
        setSelectedGroupId(profileGroupId);
        setInspectedPromptId(initialPromptIds[0] || classifiedSteps[0]?.id || "");
        initializedWorkspace.current = workspaceId;
      }
      setMessage(`${classifiedSteps.length} prompt resources · starting group ${profile?.label || nextDocument.promptProfileId}`);
    }).catch((reason) => {
      if (!cancelled) setMessage(reason instanceof Error ? reason.message : String(reason));
    });
    return () => { cancelled = true; };
  }, [workspaceId]);

  useEffect(() => {
    if (!workspaceId || !prompts.length) return;
    let cancelled = false;
    const poll = async () => {
      try {
        const payload = await request(`/workbench/workspaces/${encodeURIComponent(workspaceId)}/prompts`);
        if (cancelled) return;
        const library = payload.promptLibrary && typeof payload.promptLibrary === "object"
          ? payload.promptLibrary as Record<string, unknown>
          : {};
        const hierarchy = library.hierarchy && typeof library.hierarchy === "object"
          ? library.hierarchy as Record<string, unknown>
          : {};
        const latest = new Map(
          [payload.prompts, hierarchy.prompts, hierarchy.promptImplementations, hierarchy.promptProfiles]
            .flatMap(documentsFrom)
            .map((prompt) => [prompt.id, editablePromptSource(prompt)]),
        );
        setPromptDiskContent((current) => {
          const next = { ...current };
          for (const prompt of prompts) {
            const refreshed = latest.get(prompt.id);
            if (refreshed !== undefined) next[prompt.id] = refreshed;
          }
          return next;
        });
      } catch {
        // Keep current editor state when polling fails.
      }
    };
    const handle = window.setInterval(() => { void poll(); }, 5000);
    return () => {
      cancelled = true;
      window.clearInterval(handle);
    };
  }, [workspaceId, prompts]);

  const promptById = useMemo(() => new Map(prompts.map((prompt) => [prompt.id, prompt])), [prompts]);
  const activePromptEntries = useMemo(() => promptEntries(generationOrder), [generationOrder]);
  const middleFlowDataFields = useMemo(
    () => visualDataFieldPlan(generationOrder, promptById),
    [generationOrder, promptById],
  );
  const visualDataStacks = useMemo<VisualDataStack[]>(() => generationOrder.flatMap((entry, index) => {
    if (entry.kind !== "group") return [];
    const promptIds = promptEntries(entry.steps || []).flatMap((step) => step.promptId ? [step.promptId] : []);
    const promptIdSet = new Set(promptIds);
    return [{
      entry,
      index,
      promptIds,
      fields: middleFlowDataFields.filter((field) => field.inputPromptIds.some((id) => promptIdSet.has(id)) || field.outputPromptIds.some((id) => promptIdSet.has(id))),
    }];
  }), [generationOrder, middleFlowDataFields]);
  const inspectedPrompt = useMemo(() => promptById.get(inspectedPromptId)
    || promptById.get(activePromptEntries[0]?.promptId || "")
    || prompts[0], [activePromptEntries, inspectedPromptId, promptById, prompts]);
  const composedPrompt = useMemo(() => activePromptEntries
    .map((entry) => promptText(promptById.get(entry.promptId || "")))
    .filter(Boolean)
    .join("\n\n"), [activePromptEntries, promptById]);
  const outputs = useMemo(() => [...new Set(activePromptEntries.flatMap((entry) => promptById.get(entry.promptId || "")?.produces || []))], [activePromptEntries, promptById]);

  const savePrompt = async (prompt: PromptChoice) => {
    const draft = promptDrafts[prompt.id] || editablePromptSource(prompt);
    if (!prompt.path || !prompt.workspaceId || promptDraftValidity[prompt.id] === false) return;
    setSavingPromptId(prompt.id);
    try {
      const document = JSON.parse(draft) as PromptChoice;
      const payload = await request(`/workbench/workspaces/${encodeURIComponent(prompt.workspaceId)}/prompts/${encodeURIComponent(prompt.id)}`, {
        method: "PUT",
        body: JSON.stringify({ path: prompt.path, document }),
      });
      const saved = payload.document as PromptChoice;
      const next = {
        ...saved,
        path: prompt.path,
        source: prompt.source,
        workspaceId: prompt.workspaceId,
      };
      const nextSource = editablePromptSource(next);
      setPrompts((current) => current.map((candidate) => candidate.id === prompt.id ? next : candidate));
      setPromptDrafts((current) => ({ ...current, [prompt.id]: nextSource }));
      setPromptSavedContent((current) => ({ ...current, [prompt.id]: nextSource }));
      setPromptDiskContent((current) => ({ ...current, [prompt.id]: nextSource }));
      setMessage(`Saved Prompt ${prompt.id}.`);
    } catch (reason) {
      setMessage(reason instanceof Error ? reason.message : String(reason));
    } finally {
      setSavingPromptId("");
    }
  };

  const loadPromptDraft = (prompt: PromptChoice) => {
    const source = editablePromptSource(prompt);
    setPromptDrafts((current) => ({ ...current, [prompt.id]: source }));
    setPromptDraftValidity((current) => ({ ...current, [prompt.id]: true }));
    setMessage(`Loaded effective Prompt ${prompt.id} into its editor.`);
  };

  const reloadPrompt = async (prompt: PromptChoice) => {
    const owner = prompt.workspaceId || workspaceId;
    setReloadingPromptId(prompt.id);
    try {
      const payload = await request(`/workbench/workspaces/${encodeURIComponent(owner)}/prompts`);
      const library = payload.promptLibrary && typeof payload.promptLibrary === "object"
        ? payload.promptLibrary as Record<string, unknown>
        : {};
      const hierarchy = library.hierarchy && typeof library.hierarchy === "object"
        ? library.hierarchy as Record<string, unknown>
        : {};
      const refreshed = [payload.prompts, hierarchy.prompts, hierarchy.promptImplementations, hierarchy.promptProfiles]
        .flatMap(documentsFrom)
        .find((candidate) => candidate.id === prompt.id);
      if (!refreshed) throw new Error(`Prompt ${prompt.id} was not found in ${owner}.`);
      const next = { ...refreshed, workspaceId: owner };
      const nextSource = editablePromptSource(next);
      setPrompts((current) => current.map((candidate) => candidate.id === prompt.id ? next : candidate));
      setPromptDrafts((current) => ({ ...current, [prompt.id]: nextSource }));
      setPromptSavedContent((current) => ({ ...current, [prompt.id]: nextSource }));
      setPromptDiskContent((current) => ({ ...current, [prompt.id]: nextSource }));
      setPromptDraftValidity((current) => ({ ...current, [prompt.id]: true }));
      setMessage(`Reloaded Prompt ${prompt.id} from ${owner}.`);
    } catch (reason) {
      setMessage(reason instanceof Error ? reason.message : String(reason));
    } finally {
      setReloadingPromptId("");
    }
  };
  const selectedGroup = useMemo(() => generationOrder.find((entry) => entry.kind === "group" && entry.id === selectedGroupId), [generationOrder, selectedGroupId]);
  const runnableEntries = useMemo(() => selectedGroup?.steps || generationOrder, [generationOrder, selectedGroup]);
  const runnablePromptEntries = useMemo(() => promptEntries(runnableEntries), [runnableEntries]);
  const sequenceImages = useMemo(() => [
    ...(document?.frames || []).map((frame) => ({
      id: frame.id,
      label: frame.label,
      assetPath: frame.assetPath,
      source: `/workbench/workspaces/${encodeURIComponent(workspaceId)}/asset?path=${encodeURIComponent(frame.assetPath)}`,
    })),
    ...uploadedImages.map((image) => ({ id: image.id, label: image.label, assetPath: "", source: image.dataUrl })),
  ], [document?.frames, uploadedImages, workspaceId]);
  const sequenceContext = useMemo(() => (document?.commands || []).map((command, index) =>
    `Image ${index + 1} -> ${command.label || command.command} (${command.command}) -> Image ${index + 2}`,
  ).join("\n"), [document?.commands]);
  const availableData = useMemo<Record<string, unknown>>(() => {
    const sources = sequenceImages.map((image) => image.source);
    const currentImage = sources.at(-1);
    const previousImage = sources.length > 1 ? sources.at(-2) : currentImage;
    const manifest = {
      id: document?.id || "visual_image_diff",
      frames: sequenceImages,
      commands: document?.commands || [],
    };
    return {
      ...(sources.length ? {
        image: currentImage,
        current_image: currentImage,
        previous_image: previousImage,
        parent_image: previousImage,
        before: previousImage,
        after: currentImage,
        images: sources,
        source_images: sources,
        image_sequence: sources,
        image_pair: [previousImage, currentImage],
      } : {}),
      source_manifest: manifest,
      manifest,
      sequence_context: sequenceContext,
      commands: document?.commands || [],
      transition_command: document?.commands.at(-1)?.command || "",
      ...workflowData,
    };
  }, [document?.commands, document?.id, sequenceContext, sequenceImages, workflowData]);

  const rememberWorkflowOutputs = (nextOutputs: Record<string, unknown>) => {
    setWorkflowData((current) => ({ ...current, ...nextOutputs }));
    setMode("outputs", "scroll");
  };

  const readMiddleFlowDataFields = () => {
    setPlannedDataFields(middleFlowDataFields);
    setMode("outputs", "scroll");
    setMessage(`Read ${middleFlowDataFields.length} datafields from ${activePromptEntries.length} CENTER Prompt steps.`);
  };

  const addMissingDataFieldEditors = () => {
    const plan = plannedDataFields.length ? plannedDataFields : middleFlowDataFields;
    const leftColumn = pageDefinition.layout.columns.find((column) => column.id === "left");
    const declared = new Set((leftColumn?.members || []).flatMap((member) => {
      if (typeof member === "string" || member.component !== "VisualDataFieldEditor") return [];
      const name = member.options?.fieldName;
      return typeof name === "string" ? [name] : [];
    }));
    setPlannedDataFields(plan);
    setGeneratedDataFieldNames((current) => [...new Set([
      ...current,
      ...plan.map((field) => field.name).filter((name) => !declared.has(name)),
    ])]);
    setMode("outputs", "scroll");
    setMessage(`Added every missing datafield editor from the CENTER flow (${plan.length} fields discovered).`);
  };

  const renderedPageDefinition = useMemo<WorkflowPageDefinition>(() => {
    if (!generatedDataFieldNames.length) return pageDefinition;
    const planByName = new Map((plannedDataFields.length ? plannedDataFields : middleFlowDataFields)
      .map((field) => [field.name, field]));
    const declaredFieldNames = new Set(pageDefinition.layout.columns
      .find((column) => column.id === "left")?.members.flatMap((member) => {
        if (typeof member === "string" || member.component !== "VisualDataFieldEditor") return [];
        return typeof member.options?.fieldName === "string" ? [member.options.fieldName] : [];
      }) || []);
    const generatedMembers: WorkflowPageMemberDefinition[] = generatedDataFieldNames
      .filter((name) => !declaredFieldNames.has(name))
      .map((name) => {
      const field = planByName.get(name);
      return {
        id: `visual-datafield-${name.replace(/[^A-Za-z0-9_-]+/g, "-")}`,
        label: name,
        component: "VisualDataFieldEditor",
        initialDisplayMode: "strip",
        options: {
          fieldName: name,
          inputPromptIds: field?.inputPromptIds || [],
          outputPromptIds: field?.outputPromptIds || [],
        },
      };
    });
    return {
      ...pageDefinition,
      layout: {
        ...pageDefinition.layout,
        columns: pageDefinition.layout.columns.map((column) => {
          if (column.id !== "left") return column;
          const [first, ...rest] = column.members;
          return { ...column, members: first ? [first, ...generatedMembers, ...rest] : generatedMembers };
        }),
      },
    };
  }, [generatedDataFieldNames, middleFlowDataFields, pageDefinition, plannedDataFields]);

  const updateEntry = (entryId: string, changes: Partial<PromptCompositionEntry>, parentGroupId?: string) => setGenerationOrder((current) => parentGroupId
    ? current.map((entry) => entry.id === parentGroupId ? { ...entry, steps: (entry.steps || []).map((child) => child.id === entryId ? { ...child, ...changes } : child) } : entry)
    : current.map((entry) => entry.id === entryId ? { ...entry, ...changes } : entry));
  const moveEntry = (entryId: string, targetIndex: number, parentGroupId?: string) => setGenerationOrder((current) => {
    const move = (entries: PromptCompositionEntry[]) => {
      const sourceIndex = entries.findIndex((entry) => entry.id === entryId);
      if (sourceIndex < 0 || sourceIndex === targetIndex) return entries;
      const next = [...entries];
      const [moved] = next.splice(sourceIndex, 1);
      next.splice(Math.max(0, Math.min(targetIndex, next.length)), 0, moved);
      return next;
    };
    return parentGroupId ? current.map((entry) => entry.id === parentGroupId ? { ...entry, steps: move(entry.steps || []) } : entry) : move(current);
  });
  const dropPromptOnEntry = (target: PromptCompositionEntry, promptId: string, parentGroupId?: string) => {
    if (!prompts.some((prompt) => prompt.id === promptId)) {
      setMessage(`Cannot add unknown Prompt resource ${promptId}.`);
      return;
    }
    setInspectedPromptId(promptId);
    if (target.kind === "group") {
      setGenerationOrder((current) => current.map((entry) => entry.id === target.id ? { ...entry, steps: [...(entry.steps || []), newPromptEntry(promptId, "dropped")] } : entry));
      setSelectedGroupId(target.id);
      setMessage(`Added ${promptId} to ${target.label || "the selected group"}.`);
      return;
    }
    updateEntry(target.id, { promptId }, parentGroupId);
    setMessage(`Replaced the Prompt at this position with ${promptId}.`);
  };
  const insertPromptAt = (promptId: string, parentGroupId: string, targetIndex: number) => {
    if (!prompts.some((prompt) => prompt.id === promptId)) {
      setMessage(`Cannot insert unknown Prompt resource ${promptId}.`);
      return;
    }
    setGenerationOrder((current) => current.map((entry) => {
      if (entry.id !== parentGroupId || entry.kind !== "group") return entry;
      const next = [...(entry.steps || [])];
      next.splice(Math.max(0, Math.min(targetIndex, next.length)), 0, newPromptEntry(promptId, `graph-insert:${targetIndex}`));
      return { ...entry, steps: next };
    }));
    setSelectedGroupId(parentGroupId);
    setInspectedPromptId(promptId);
    setMessage(`Inserted ${promptId} at graph sequence position ${targetIndex + 1}.`);
  };
  const moveCallAcrossGroups = (entryId: string, sourceGroupId: string, targetGroupId: string, targetIndex: number) => {
    setGenerationOrder((current) => {
      let moved: PromptCompositionEntry | undefined;
      let sourceIndex = -1;
      const withoutSource = current.map((entry) => {
        if (entry.id !== sourceGroupId || entry.kind !== "group") return entry;
        sourceIndex = (entry.steps || []).findIndex((step) => step.id === entryId);
        if (sourceIndex < 0) return entry;
        moved = entry.steps?.[sourceIndex];
        return { ...entry, steps: (entry.steps || []).filter((step) => step.id !== entryId) };
      });
      if (!moved) return current;
      const adjustedTarget = sourceGroupId === targetGroupId && sourceIndex < targetIndex
        ? targetIndex - 1
        : targetIndex;
      return withoutSource.map((entry) => {
        if (entry.id !== targetGroupId || entry.kind !== "group") return entry;
        const next = [...(entry.steps || [])];
        next.splice(Math.max(0, Math.min(adjustedTarget, next.length)), 0, moved as PromptCompositionEntry);
        return { ...entry, steps: next };
      });
    });
    setSelectedGroupId(targetGroupId);
    setMessage(sourceGroupId === targetGroupId
      ? "Reordered the Prompt call on the graph sequence."
      : "Moved the Prompt call into another graph sequence group.");
  };
  const replaceCallAcrossGroups = (entryId: string, sourceGroupId: string, targetEntryId: string, targetGroupId: string) => {
    if (!entryId || !sourceGroupId || !targetEntryId || !targetGroupId || (entryId === targetEntryId && sourceGroupId === targetGroupId)) return;
    setGenerationOrder((current) => {
      const findInGroup = (groupId: string, stepId: string) => {
        const group = current.find((entry) => entry.id === groupId && entry.kind === "group");
        const steps = group?.steps || [];
        const index = steps.findIndex((step) => step.id === stepId);
        return index < 0 ? null : { group, steps, index, step: steps[index] };
      };
      const source = findInGroup(sourceGroupId, entryId);
      const target = findInGroup(targetGroupId, targetEntryId);
      if (!source || !target) return current;
      return current.map((entry) => {
        if (entry.kind !== "group") return entry;
        if (entry.id === sourceGroupId && entry.id === targetGroupId) {
          const next = [...(entry.steps || [])];
          [next[source.index], next[target.index]] = [next[target.index], next[source.index]];
          return { ...entry, steps: next };
        }
        if (entry.id === sourceGroupId) {
          const next = [...(entry.steps || [])];
          next[source.index] = target.step;
          return { ...entry, steps: next };
        }
        if (entry.id === targetGroupId) {
          const next = [...(entry.steps || [])];
          next[target.index] = source.step;
          return { ...entry, steps: next };
        }
        return entry;
      });
    });
    setSelectedGroupId(targetGroupId);
    setMessage(sourceGroupId === targetGroupId
      ? "Swapped the two Prompt calls in this graph sequence group."
      : "Swapped Prompt calls across graph sequence groups.");
  };
  const removeEntry = (entryId: string, parentGroupId?: string) => {
    setGenerationOrder((current) => parentGroupId
      ? current.map((entry) => entry.id === parentGroupId ? { ...entry, steps: (entry.steps || []).filter((child) => child.id !== entryId) } : entry)
      : current.filter((entry) => entry.id !== entryId));
    if (entryId === selectedGroupId) setSelectedGroupId(null);
  };
  const addPrompt = (promptId: string) => {
    setInspectedPromptId(promptId);
    setGenerationOrder((current) => {
      const nextEntry = newPromptEntry(promptId, "added");
      if (!selectedGroupId) return [...current, nextEntry];
      return current.map((entry) => entry.id === selectedGroupId ? { ...entry, steps: [...(entry.steps || []), nextEntry] } : entry);
    });
  };
  const addGroup = () => {
    const id = `${Date.now()}:visual-image-diff-group:${Math.random()}`;
    setGenerationOrder((current) => [...current, { id, kind: "group", visibleToPeers: true, visibleToUpdates: false, steps: [] }]);
    setSelectedGroupId(id);
  };
  const shuffleGroup = (groupId: string) => {
    setSelectedGroupId(groupId);
    setGenerationOrder((current) => current.map((entry) => entry.id === groupId && entry.kind === "group" ? { ...entry, steps: shuffledEntries(entry.steps || []) } : entry));
  };
  const clearGroup = (groupId: string) => {
    setSelectedGroupId(groupId);
    setGenerationOrder((current) => current.map((entry) => entry.id === groupId && entry.kind === "group" ? { ...entry, steps: [] } : entry));
  };
  const copyGroup = (groupId: string) => {
    const sourceIndex = generationOrder.findIndex((entry) => entry.id === groupId && entry.kind === "group");
    if (sourceIndex < 0) return;
    const rootId = `${Date.now()}:visual-image-diff-group-copy:${Math.random()}`;
    const clone = (entry: PromptCompositionEntry, id: string): PromptCompositionEntry => ({
      ...entry,
      id,
      ...(entry.workflowStep ? { workflowStep: { ...entry.workflowStep } } : {}),
      ...(entry.steps ? { steps: entry.steps.map((child, index) => clone(child, `${id}:${index}:${Math.random()}`)) } : {}),
    });
    const copy = clone(generationOrder[sourceIndex], rootId);
    setGenerationOrder((current) => [...current.slice(0, sourceIndex + 1), copy, ...current.slice(sourceIndex + 1)]);
    setSelectedGroupId(rootId);
  };
  const restoreProfileGroup = () => {
    const restored: PromptCompositionEntry[] = profileGroups.length ? profileGroups.map((group, groupIndex): PromptCompositionEntry => ({
      id: `${Date.now()}:restored:${group.id}:${groupIndex}`,
      kind: "group",
      label: group.label,
      transactionId: group.transaction,
      operationId: group.operation,
      implementationId: group.implementation,
      profileId: group.profile,
      continueOnError: group.continueOnError,
      focalGroup: group.focalGroup,
      parentGroup: group.parentGroup,
      colorKey: group.colorKey,
      visibleToPeers: true,
      visibleToUpdates: false,
      steps: group.prompts.map((promptId, index) => newPromptEntry(promptId, `restored:${group.id}:${index}`)),
    })) : [{ id: `${Date.now()}:restored-profile-group`, kind: "group", visibleToPeers: true, visibleToUpdates: false, steps: profileStepIds.map((promptId, index) => newPromptEntry(promptId, `restored:${index}`)) }];
    setGenerationOrder(restored);
    setSelectedGroupId(restored[0]?.id || null);
  };

  const addUploadedImages = async (files: FileList | null) => {
    if (!files?.length) return;
    try {
      const next = await Promise.all([...files].map(readImageFile));
      setUploadedImages((current) => [...current, ...next]);
      setMessage(`${next.length} image${next.length === 1 ? "" : "s"} added to the runnable sequence.`);
    } catch (reason) {
      setRunError(reason instanceof Error ? reason.message : String(reason));
    }
  };

  const runPrompts = async (entries: PromptCompositionEntry[] = runnablePromptEntries, requestedModelId = "") => {
    const runnableEntries = promptEntries(entries);
    const modelId = requestedModelId || entries.find((entry) => entry.modelId)?.modelId || runnableEntries.find((entry) => entry.modelId)?.modelId || runModel;
    const promptParts = runnableEntries
      .map((entry) => promptText(promptById.get(entry.promptId || "")))
      .filter(Boolean);
    if (!modelId) {
      setRunError("Select an enabled model before running the prompt group.");
      return;
    }
    if (!promptParts.length) {
      setRunError("The selected group has no prompt resources to run.");
      return;
    }
    const imageInputs = sequenceImages.map(({ label, source }) => ({ label, source }));
    if (!imageInputs.length) {
      setRunError("Add at least one image before running the visual prompt group.");
      return;
    }
    setRunning(true);
    setRunError("");
    setRunResult(null);
    setSubmittedImageCount(imageInputs.length);
    try {
      const image = await makeImageContactSheet(imageInputs);
      const prompt = [
        "Analyze the labeled image sequence in the attached contact sheet.",
        sequenceContext ? `SEQUENCE\n${sequenceContext}` : "",
        `PROMPT RESOURCES\n${promptParts.join("\n\n")}`,
      ].filter(Boolean).join("\n\n");
      const payload = await request(`/workbench/workspaces/${encodeURIComponent(workspaceId)}/models/${encodeURIComponent(modelId)}/invoke`, {
        method: "POST",
        body: JSON.stringify({ prompt, image, timeoutSeconds: 300 }),
      });
      setRunResult(payload as ModelInvocation);
      setMessage(`${promptParts.length} prompt resources ran against ${imageInputs.length} submitted images with ${modelId}.`);
      setMode("outputs", "scroll");
    } catch (reason) {
      setRunError(reason instanceof Error ? reason.message : String(reason));
    } finally {
      setRunning(false);
    }
  };

  const commandAfter = (frameId: string) => document?.commands.find((command) => command.fromFrameId === frameId);

  const composerControls = () => <div className="english-workflow-generation-controls visual-image-generation-controls">
    <label><span>SELECTED MODEL</span><select aria-label="Visual Image Diff run model" value={selectedGroup?.modelId || runModel} onChange={(event) => {
      setRunModel(event.target.value);
      if (selectedGroup) updateEntry(selectedGroup.id, { modelId: event.target.value });
    }}>{models.filter((model) => model.enabled !== false).map((model) => <option key={model.id} value={model.id}>{modelOptionLabel(model)}</option>)}</select></label>
    <fieldset className="english-workflow-contract-order visual-image-diff-composer visual-image-diff-subaccordion-composer">
      <legend>VISUAL PIPELINE ORDER · NESTED ACCORDION</legend>
      <div className="english-workflow-output-composer">
        <div className="english-workflow-output-composer-row" aria-label="Add visual pipeline steps">
          {prompts.map((prompt) => <button type="button" key={prompt.id} disabled={running} title={`${prompt.classificationId || "Unclassified"} · ${prompt.label || prompt.id}`} onClick={() => addPrompt(prompt.id)}>+ {prompt.buttonName || prompt.label || prompt.id}</button>)}
          <button type="button" className="english-workflow-group-output" disabled={running} title="Create and select an empty simultaneous prompt group" onClick={addGroup}>[+group]</button>
        </div>
        {!prompts.length && <small>No effective Prompt resources declare applicability <code>{STEP_APPLICABILITY}</code>.</small>}
      </div>
      <ThreeStateAccordionStack id="visual-image-diff-uix-pipeline-stack" className="visual-image-diff-uix-pipeline-stack" controlsLabel="PIPELINE SUBACCORDION STACK">
        {generationOrder.map((entry, index) => <CompositionOrderAccordionItem key={entry.id} entry={entry} ordinal={`${index + 1}`} index={index} siblingCount={generationOrder.length} stackId="visual-image-diff-uix-pipeline-stack" selectedGroupId={selectedGroupId} inspectedPromptId={inspectedPrompt?.id || ""} workspaceId={workspaceId} prompts={prompts} models={models} operations={operations} operationImplementations={operationImplementations} availableData={availableData} busy={running} modeFor={subaccordionMode} onMode={setSubaccordionMode} onRunEntry={(entry, _ordinal, parentId) => { const parentModel = parentId ? generationOrder.find((candidate) => candidate.id === parentId)?.modelId : ""; void runPrompts([entry], entry.modelId || parentModel || runModel); }} onInspectPrompt={setInspectedPromptId} onSelectGroup={(id) => setSelectedGroupId((current) => current === id ? null : id)} onShuffleGroup={shuffleGroup} onCopyGroup={copyGroup} onClearGroup={clearGroup} onWorkflowStep={(id, workflowStep) => updateEntry(id, { workflowStep })} onImplementation={(id, implementationId) => updateEntry(id, { implementationId })} onInvocationComplete={rememberWorkflowOutputs} onPeers={(id, value, parentId) => updateEntry(id, { visibleToPeers: value }, parentId)} onUpdates={(id, value, parentId) => updateEntry(id, { visibleToUpdates: value }, parentId)} onPrompt={(id, promptId, parentId) => updateEntry(id, { promptId }, parentId)} onDropPrompt={dropPromptOnEntry} onModel={(id, modelId, parentId) => updateEntry(id, { modelId }, parentId)} onMove={moveEntry} onRemove={removeEntry} />)}
        {!generationOrder.length && <p className="empty">Use [+group] or an inline + step button to compose the ordered prompt call.</p>}
      </ThreeStateAccordionStack>
      <div className="english-workflow-order-actions">
        <button type="button" disabled={running} onClick={restoreProfileGroup}>Restore profile groups</button>
        <button type="button" disabled={running || generationOrder.length < 2} onClick={() => setGenerationOrder((current) => shuffledEntries(current))}>Shuffle order</button>
        <button type="button" disabled={running || !generationOrder.length} onClick={() => { setGenerationOrder([]); setSelectedGroupId(null); }}>Clear order</button>
      </div>
      <small>Groups and Prompt steps are native nested accordion members. Run follows the selected scope; a named Prompt title runs that step as a quick call, while [group] runs only that group.</small>
    </fieldset>
    <button type="button" className="primary" disabled={running || !runnablePromptEntries.length || !runModel} onClick={() => { void runPrompts(); }}>{running ? "Running prompt group…" : selectedGroup ? "▶ Run selected group" : "▶ Run composition"}</button>
    <small>{selectedGroup ? "Runs the selected [group] as one model call." : "Runs the complete composition as one model call."} All sequence images are combined into one labeled contact sheet for the model endpoint.</small>
  </div>;

  const componentRegistry: WorkflowPageComponentRegistry = {
    VisualResourceOutputs: () => ({
      value: Object.keys(workflowData).length ? `${Object.keys(workflowData).length} runtime values` : runResult ? `${submittedImageCount} images · response ready` : `${outputs.length} declared outputs`,
      detail: Object.keys(workflowData).length ? "Real playground outputs available to later workflow steps" : runResult ? `${runResult.modelId || runModel} · ${runResult.latencyMs ?? 0} ms` : "Union of produces declarations from the active group",
      mode: mode("outputs"), onModeChange: (value) => setMode("outputs", value), baseClass: "english-workflow-contract-panel visual-image-diff-outputs", scrollSize: "680px",
      content: <><div className="visual-datafield-planner"><div><b>DATAFIELDS FROM CENTER FLOW</b><span>Read the active Prompt sequence, then add only missing field displayers/editors beneath RESOURCE OUTPUTS.</span></div><div><button type="button" onClick={readMiddleFlowDataFields}>READ MIDDLE FLOW</button><button type="button" className="primary" disabled={!middleFlowDataFields.length} onClick={addMissingDataFieldEditors}>ADD MISSING FIELD EDITORS</button><button type="button" disabled={!generatedDataFieldNames.length} onClick={() => setGeneratedDataFieldNames([])}>REMOVE GENERATED EDITORS</button></div></div>
        <div className="visual-corresponding-data-stacks" aria-label="Data stacks corresponding to authoring stacks">{visualDataStacks.map((stack) => <section key={stack.entry.id} className="visual-corresponding-data-stack" data-stack-key={stack.entry.colorKey || `S${stack.index + 1}`}>
          <VisualStackIdentity entry={stack.entry} index={stack.index} side="data" />
          <ul>{stack.fields.map((field) => {
            const consumes = field.inputPromptIds.filter((id) => stack.promptIds.includes(id));
            const produces = field.outputPromptIds.filter((id) => stack.promptIds.includes(id));
            const direction = consumes.length && produces.length ? "↔" : consumes.length ? "→" : "←";
            return <li key={field.name} data-visual-field={field.name} data-stack-key={stack.entry.colorKey || `S${stack.index + 1}`} data-input-prompt-ids={consumes.join(" ")} data-output-prompt-ids={produces.join(" ")}><code>{field.name}</code><b aria-hidden="true">{direction}</b><span>{produces.length ? `output of ${produces.map((id) => promptById.get(id)?.buttonName || id).join(", ")}` : ""}{produces.length && consumes.length ? " · " : ""}{consumes.length ? `input to ${consumes.map((id) => promptById.get(id)?.buttonName || id).join(", ")}` : ""}</span></li>;
          })}</ul>
        </section>)}</div>
        <details className="visual-datafield-contract-index"><summary>UNGROUPED DATAFIELD CONTRACT INDEX</summary><ul>{(plannedDataFields.length ? plannedDataFields : middleFlowDataFields).map((field) => <li key={field.name}><code>{field.name}</code><span>{field.inputPromptIds.length ? `input to ${field.inputPromptIds.length}` : ""}{field.inputPromptIds.length && field.outputPromptIds.length ? " · " : ""}{field.outputPromptIds.length ? `output of ${field.outputPromptIds.length}` : ""}</span></li>)}</ul></details>
        {Object.keys(workflowData).length > 0 && <section className="visual-image-workflow-data" aria-label="Workflow data available to later steps"><h3>WORKFLOW DATA AVAILABLE TO LATER STEPS</h3>{Object.entries(workflowData).map(([name, value]) => <div key={name}><b>{name}</b><pre>{typeof value === "string" ? value : JSON.stringify(value, null, 2)}</pre></div>)}</section>}
        {running && <div className="visual-image-run-status"><b>Running prompt group</b><span>Preparing and submitting the image sequence…</span></div>}
        {runError && <div className="visual-image-run-error"><b>Invocation failed</b><span>{runError}</span></div>}
        {runResult && <div className="visual-image-run-result"><header><b>MODEL RESPONSE</b><span>{runResult.backendId || "resolved backend"} · {runResult.inputTokens ?? 0}/{runResult.outputTokens ?? 0} tokens</span></header><pre>{runResult.text || JSON.stringify(runResult, null, 2)}</pre></div>}</>,
    }),
    VisualDataFieldEditor: (member) => {
      const fieldName = typeof member.options?.fieldName === "string" ? member.options.fieldName : member.id;
      const inputPromptIds = Array.isArray(member.options?.inputPromptIds) ? member.options.inputPromptIds.map(String) : [];
      const outputPromptIds = Array.isArray(member.options?.outputPromptIds) ? member.options.outputPromptIds.map(String) : [];
      const value = availableData[fieldName];
      const editorValue = value === undefined ? "" : typeof value === "string" ? value : JSON.stringify(value, null, 2);
      return {
        value: value === undefined ? "Empty datafield" : "Value available",
        detail: [inputPromptIds.length ? `input to ${inputPromptIds.length} Prompt${inputPromptIds.length === 1 ? "" : "s"}` : "", outputPromptIds.length ? `output of ${outputPromptIds.length} Prompt${outputPromptIds.length === 1 ? "" : "s"}` : ""].filter(Boolean).join(" · ") || "CENTER flow datafield",
        baseClass: "english-workflow-contract-panel visual-datafield-editor",
        scrollSize: "320px",
        content: <section><div className="operation-abstract-summary"><div><span>DATAFIELD</span><code>{fieldName}</code></div><div><span>INPUT TO</span><code>{inputPromptIds.join(", ") || "None"}</code></div><div><span>OUTPUT OF</span><code>{outputPromptIds.join(", ") || "None"}</code></div><div><span>STATUS</span><code>{value === undefined ? "Not produced" : "Available"}</code></div></div><textarea aria-label={`Edit visual datafield ${fieldName}`} value={editorValue} onChange={(event) => setWorkflowData((current) => ({ ...current, [fieldName]: event.target.value }))} spellCheck={false} placeholder={`Runtime value for ${fieldName}`} /></section>,
      };
    },
    ImageCommandSequence: () => ({
      value: `${(document?.frames.length || 0) + uploadedImages.length} images · ${document?.commands.length || 0} commands`, detail: MANIFEST_PATH,
      mode: mode("sequence"), onModeChange: (value) => setMode("sequence", value), baseClass: "english-workflow-panel visual-image-diff-sequence", scrollSize: "680px",
      content: <><div className="visual-image-input-toolbar"><label><b>ADD IMAGES</b><input type="file" accept="image/*" multiple onChange={(event) => { void addUploadedImages(event.target.files); event.target.value = ""; }} /></label><span>Every listed image is submitted in sequence order.</span><button type="button" disabled={!uploadedImages.length} onClick={() => setUploadedImages([])}>Clear added images</button></div>
        <div className="visual-image-sequence">{document?.frames.map((frame, index) => { const command = commandAfter(frame.id); return <div className="visual-image-sequence-part" key={frame.id}><figure><figcaption><b>{index + 1}</b><span>{frame.label}</span><code>{frame.assetPath}</code></figcaption><img src={`/workbench/workspaces/${encodeURIComponent(workspaceId)}/asset?path=${encodeURIComponent(frame.assetPath)}`} alt={frame.label} /></figure>{command && <div className="visual-image-command"><span>ENGLISH COMMAND</span><strong>{command.label || command.command}</strong><code>{command.command}</code></div>}</div>; })}{uploadedImages.map((image, index) => <div className="visual-image-sequence-part visual-image-uploaded" key={image.id}><figure><figcaption><b>{(document?.frames.length || 0) + index + 1}</b><span>{image.label}</span><code>Added for this run</code></figcaption><img src={image.dataUrl} alt={image.label} /></figure></div>)}</div></>,
    }),
    VisualSequenceContext: () => ({
      value: `${document?.commands.length || 0} transitions`, detail: "Filesystem manifest facts available to authoring and workflow steps",
      mode: mode("context"), onModeChange: (value) => setMode("context", value), baseClass: "english-workflow-contract-panel visual-image-diff-context",
      content: <ol>{document?.commands.map((command) => <li key={`${command.fromFrameId}:${command.toFrameId}`}><code>{command.fromFrameId}</code><strong>{command.label || command.command}</strong><code>{command.toFrameId}</code></li>)}</ol>,
    }),
    VisualPipelineSubaccordion: () => ({
      value: `${generationOrder.length} groups/items · ${promptEntryCount(generationOrder)} prompt steps`, detail: document?.promptProfileId || "Every pipeline item is a nested ThreeStateAccordionMember",
      mode: mode("groupAccordion"), onModeChange: (value) => setMode("groupAccordion", value), baseClass: "english-workflow-panel visual-image-diff-group visual-image-diff-subaccordion-version", scrollSize: "calc(100vh - 250px)", content: composerControls(),
    }),
    SelectedOperationPlayground: () => ({
      value: selectedGroup?.label || selectedGroup?.transactionId || "Select a group", detail: "Real Workflow Item + Operation playground",
      mode: mode("playground"), onModeChange: (value) => setMode("playground", value), baseClass: "english-workflow-panel visual-image-diff-selected-playground", scrollSize: "calc(100vh - 250px)",
      content: selectedGroup ? <VisualImageDiffOperationSurface entry={selectedGroup} title={selectedGroup.label ? `[group] ${selectedGroup.label}` : "[group]"} workspaceId={workspaceId} prompts={prompts} models={models} operations={operations} operationImplementations={operationImplementations} availableData={availableData} onInspectPrompt={setInspectedPromptId} onWorkflowStep={(id, workflowStep) => updateEntry(id, { workflowStep })} onImplementation={(id, implementationId) => updateEntry(id, { implementationId })} onInvocationComplete={rememberWorkflowOutputs} showHeader /> : <p>Select a transaction group to open its filesystem-backed Workflow Item + Operation playground.</p>,
    }),
    ResourceSourceEditor: () => ({
      value: `${pageDefinition.id}.workflow_page.json`, detail: "Resolved three-column page JSON", mode: mode("pageSpecification"), onModeChange: (value) => setMode("pageSpecification", value), baseClass: "english-workflow-contract-panel visual-image-diff-page-source", scrollSize: "520px",
      content: <WorkflowPageSourceEditor workspaceId={workspaceId} pageId={pageDefinition.id} disabled={running} liveDefinition={renderedPageDefinition} onSaved={onPageDefinitionSaved} />,
    }),
    VisualPromptInspector: (member) => {
      const promptId = typeof member.options?.promptId === "string" ? member.options.promptId : "";
      const prompt = prompts.find((candidate) => candidate.id === promptId) || inspectedPrompt;
      const modeKey = `prompt:${member.id}`;
      return {
        value: prompt?.buttonName || prompt?.label || "Prompt unavailable", detail: prompt?.id || promptId || "Individual pipeline Prompt resource", mode: mode(modeKey, member.initialDisplayMode || "scroll"), onModeChange: (value) => setMode(modeKey, value), baseClass: "english-workflow-contract-panel visual-image-diff-prompt-inspector", scrollSize: "520px",
        stripDragData: prompt ? { [VISUAL_PROMPT_DRAG_TYPE]: prompt.id, "text/plain": prompt.id } : undefined,
        content: prompt ? <section className="visual-image-diff-prompt-editor">
          {(() => {
            const draft = promptDrafts[prompt.id] || editablePromptSource(prompt);
            const saved = promptSavedContent[prompt.id] || editablePromptSource(prompt);
            const disk = promptDiskContent[prompt.id] || editablePromptSource(prompt);
            const dirty = draft !== saved;
            const diskChanged = disk !== saved;
            return <>
          <div className="operation-abstract-summary">
            <div><span>PROMPT ID</span><code>{prompt.id}</code></div>
            <div><span>CLASSIFICATION</span><code>{prompt.classificationId || "Unclassified"}</code></div>
            <div><span>APPLICABILITY</span><code>{prompt.applicability?.join(", ") || "None declared"}</code></div>
            <div><span>PRODUCES</span><code>{prompt.produces?.join(", ") || "None declared"}</code></div>
          </div>
          <p>{prompt.description || "Filesystem-backed visual pipeline Prompt resource."}</p>
          <div className="operation-editor-actions">
            <span>{prompt.source || "effective"} · {prompt.path || "Prompt source path unavailable"}</span>
            <button type="button" className="visual-image-diff-drag-prompt" draggable onDragStart={(event) => { event.dataTransfer.effectAllowed = "copy"; event.dataTransfer.setData(VISUAL_PROMPT_DRAG_TYPE, prompt.id); event.dataTransfer.setData("text/plain", prompt.id); }} title="Drag this Prompt onto a group to add it, or onto a Prompt step to replace that step">DRAG PROMPT</button>
            <button type="button" disabled={savingPromptId === prompt.id || reloadingPromptId === prompt.id} onClick={() => loadPromptDraft(prompt)}>Load</button>
            <button type="button" disabled={savingPromptId === prompt.id || reloadingPromptId === prompt.id || !diskChanged} onClick={() => void reloadPrompt(prompt)}>{reloadingPromptId === prompt.id ? "Reloading…" : (diskChanged ? "Reload changes" : "Reload")}</button>
            <button type="button" disabled={savingPromptId === prompt.id || reloadingPromptId === prompt.id} onClick={() => { setPromptDrafts((current) => ({ ...current, [prompt.id]: "" })); setPromptDraftValidity((current) => ({ ...current, [prompt.id]: false })); setMessage(`Cleared the draft for Prompt ${prompt.id}.`); }}>Clear</button>
            <button type="button" className="primary" disabled={savingPromptId === prompt.id || reloadingPromptId === prompt.id || promptDraftValidity[prompt.id] === false || !prompt.path || !prompt.workspaceId || (!dirty && !diskChanged)} onClick={() => void savePrompt(prompt)}>{savingPromptId === prompt.id ? "Saving…" : (diskChanged && !dirty ? "Save Prompt (overwrite disk changes)" : "Save Prompt")}</button>
          </div>
          <div className="english-workflow-editor-meta">
            <span>{dirty ? "Unsaved changes" : "Saved"}</span>
            <span>{diskChanged ? "Disk changed" : "Disk synced"}</span>
          </div>
          <ResourceSourceEditor
            value={draft}
            onChange={(value) => setPromptDrafts((current) => ({ ...current, [prompt.id]: value }))}
            onValidityChange={(valid) => setPromptDraftValidity((current) => ({ ...current, [prompt.id]: valid }))}
            label={`Edit ${prompt.label || prompt.id}`}
          />
        </>;
          })()}
        </section> : <p>The configured filesystem Prompt resource is not available in the effective workspace catalog.</p>,
      };
    },
    ComposedGroupPrompt: () => ({
      value: `${promptEntryCount(generationOrder)} prompt steps`, detail: "Live composition from the selected resource order", mode: mode("composed"), onModeChange: (value) => setMode("composed", value), baseClass: "english-workflow-contract-panel visual-image-diff-composed", scrollSize: "520px", content: <pre>{composedPrompt || "Add a prompt resource with + STEPS."}</pre>,
    }),
  };

  return (
    <WorkflowPageHost
      definition={renderedPageDefinition}
      componentRegistry={componentRegistry}
      pageClassName={`english-workflow-page visual-image-diff-page visual-image-diff-${presentationMode}-mode`}
      columnsClassName="visual-image-diff-columns"
      columnsStyle={columnGridStyle}
      columnsRef={columnsRef}
      columnsOverlay={presentationMode === "graph" ? <VisualPipelineGraph stacks={visualDataStacks} promptById={promptById} prompts={prompts} models={models} generationOrder={generationOrder} selectedGroupId={selectedGroupId} availableData={availableData} busy={running} onSelectGroup={(id) => setSelectedGroupId((current) => current === id ? null : id)} onInspectPrompt={setInspectedPromptId} onPrompt={(id, promptId, parentGroupId) => updateEntry(id, { promptId }, parentGroupId)} onDropPrompt={dropPromptOnEntry} onInsertPrompt={insertPromptAt} onMoveCall={moveCallAcrossGroups} onReplaceCall={replaceCallAcrossGroups} onModel={(id, modelId, parentGroupId) => updateEntry(id, { modelId }, parentGroupId)} onPeers={(id, value, parentGroupId) => updateEntry(id, { visibleToPeers: value }, parentGroupId)} onUpdates={(id, value, parentGroupId) => updateEntry(id, { visibleToUpdates: value }, parentGroupId)} onMove={moveEntry} onRemove={removeEntry} onCopyGroup={copyGroup} onShuffleGroup={shuffleGroup} onClearGroup={clearGroup} onDataField={(name, value) => setWorkflowData((current) => ({ ...current, [name]: value }))} onRunEntry={(entry, parentGroupId) => { const parentModel = parentGroupId ? generationOrder.find((candidate) => candidate.id === parentGroupId)?.modelId : ""; void runPrompts([entry], entry.modelId || parentModel || runModel); }} onAddPrompt={addPrompt} onAddGroup={addGroup} onRestore={restoreProfileGroup} onShuffleOrder={() => setGenerationOrder((current) => shuffledEntries(current))} onClearOrder={() => { setGenerationOrder([]); setSelectedGroupId(null); }} /> : <VisualCorrespondenceOverlay containerRef={columnsRef} version={`${generationOrder.map((entry) => `${entry.id}:${promptEntries(entry.steps || []).map((step) => step.promptId).join(",")}`).join("|")}:${middleFlowDataFields.length}`} />}
      freezeColumnControls
      stackIdForColumn={(column) => `visual-image-diff-${column.id}-stack`}
      header={<header className="english-workflow-titlebar">
        <div><span>VISUAL IMAGE DIFF</span><h1>{document?.label || "VisualImageDiff"}</h1></div>
        <div className="visual-image-diff-presentation-switch" role="group" aria-label="Visual Sequencing presentation"><button type="button" className={presentationMode === "columns" ? "active" : ""} aria-pressed={presentationMode === "columns"} onClick={() => setPresentationMode("columns")}>COLUMNS</button><button type="button" className={presentationMode === "graph" ? "active" : ""} aria-pressed={presentationMode === "graph"} onClick={() => setPresentationMode("graph")}>GRAPH</button></div>
        <div className="english-workflow-runtime-status"><i /><b>{workspaceLabel}</b><span>{message}</span></div>
      </header>}
      renderColumnDivider={(leftColumn) => leftColumn.id === "left" ? <div
          className="visual-image-diff-column-divider"
          role="separator"
          aria-orientation="vertical"
          aria-label="Resize data and authoring columns"
          aria-valuemin={15}
          aria-valuemax={85}
          aria-valuenow={Math.round(columnRatios.left / totalColumnRatio * 100)}
          tabIndex={0}
          onPointerDown={(event) => beginColumnResize("left", event)}
          onDoubleClick={() => setColumnRatios(DEFAULT_VISUAL_COLUMN_RATIOS)}
          onKeyDown={(event) => {
            if (event.key !== "ArrowLeft" && event.key !== "ArrowRight") return;
            event.preventDefault();
            nudgeColumnBoundary("left", event.key === "ArrowLeft" ? -0.25 : 0.25);
          }}
        /> : <div
          className="visual-image-diff-column-divider"
          role="separator"
          aria-orientation="vertical"
          aria-label="Resize authoring and source detail columns"
          aria-valuemin={15}
          aria-valuemax={85}
          aria-valuenow={Math.round((columnRatios.left + columnRatios.center) / totalColumnRatio * 100)}
          tabIndex={0}
          onPointerDown={(event) => beginColumnResize("right", event)}
          onDoubleClick={() => setColumnRatios(DEFAULT_VISUAL_COLUMN_RATIOS)}
          onKeyDown={(event) => {
            if (event.key !== "ArrowLeft" && event.key !== "ArrowRight") return;
            event.preventDefault();
            nudgeColumnBoundary("right", event.key === "ArrowLeft" ? -0.25 : 0.25);
          }}
        />}
      footer={<footer className="english-workflow-statusbar">
        <span><i />Filesystem backed</span><span>{document?.id || "Loading manifest"}</span><span>{generationOrder.length} groups/items · {promptEntryCount(generationOrder)} prompt steps</span><span>{runResult ? `${submittedImageCount} images submitted` : `${outputs.length} outputs`}</span>
      </footer>}
    />
  );
}
