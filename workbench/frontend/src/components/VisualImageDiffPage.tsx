import { useEffect, useMemo, useRef, useState } from "react";
import type { CSSProperties, PointerEvent as ReactPointerEvent } from "react";
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
import type { WorkflowPageDefinition } from "./WorkflowPageHost";
import { WorkflowPageSourceEditor } from "./WorkflowPageSourceEditor";
import "../styles/english_workflow.css";
import "../styles/english_workflow_order.css";
import "../styles/visual_image_diff.css";

type VisualFrame = {
  id: string;
  label: string;
  assetPath: string;
};

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
  label?: string;
  description?: string;
  text?: string | string[];
  applicability?: string[];
  buttonName?: string;
  classificationId?: string;
  produces?: string[];
  prompts?: string[];
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
  promptId?: string;
  modelId?: string;
  visibleToPeers: boolean;
  visibleToUpdates: boolean;
  workflowStep?: Record<string, unknown>;
  steps?: PromptCompositionEntry[];
};

type OperationCatalogItem = OperationDef & {
  parents?: string[];
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
    return document.id ? [document] : [];
  });
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
    ? operationImplementations.filter((candidate): candidate is OperationCatalogItem & OperationImplementationDef => Boolean(candidate.implementation && candidate.parents?.includes(operation.id)))
    : [];
  const directImplementation = operation?.implementation && (!entry.implementationId || operation.id === entry.implementationId)
    ? operation as OperationCatalogItem & OperationImplementationDef
    : undefined;
  const selectedImplementation = directImplementation
    || variants.find((candidate) => candidate.id === entry.implementationId)
    || variants.find((candidate) => candidate.id === operation?.preferredChild)
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

function CompositionOrderItem({ entry, ordinal, index, siblingCount, parentGroupId, selectedGroupId, inspectedPromptId, prompts, models, busy, onRunEntry, onInspectPrompt, onSelectGroup, onShuffleGroup, onCopyGroup, onClearGroup, onPeers, onUpdates, onPrompt, onModel, onRotate, onRemove }: {
  entry: PromptCompositionEntry;
  ordinal: string;
  index: number;
  siblingCount: number;
  parentGroupId?: string;
  selectedGroupId: string | null;
  inspectedPromptId: string;
  prompts: PromptChoice[];
  models: ModelChoice[];
  busy: boolean;
  onRunEntry: (entry: PromptCompositionEntry, ordinal: string) => void;
  onInspectPrompt: (promptId: string) => void;
  onSelectGroup: (id: string) => void;
  onShuffleGroup: (id: string) => void;
  onCopyGroup: (id: string) => void;
  onClearGroup: (id: string) => void;
  onPeers: (id: string, value: boolean, parentGroupId?: string) => void;
  onUpdates: (id: string, value: boolean, parentGroupId?: string) => void;
  onPrompt: (id: string, promptId: string, parentGroupId?: string) => void;
  onModel: (id: string, modelId: string, parentGroupId?: string) => void;
  onRotate: (id: string, direction: -1 | 1, parentGroupId?: string) => void;
  onRemove: (id: string, parentGroupId?: string) => void;
}) {
  const isGroup = entry.kind === "group";
  const prompt = prompts.find((candidate) => candidate.id === entry.promptId);
  const title = isGroup ? entry.label ? `[group] ${entry.label}` : "[group]" : prompt?.buttonName || prompt?.label || entry.promptId || "Select prompt";
  const selected = isGroup && selectedGroupId === entry.id;
  const inspected = !isGroup && Boolean(entry.promptId) && inspectedPromptId === entry.promptId;
  const inspect = () => { if (!isGroup && entry.promptId) onInspectPrompt(entry.promptId); };
  return <li className={`${isGroup ? "generation-order-group" : "generation-output-prompt"} ${selected ? "selected" : ""} ${inspected ? "inspected" : ""}`} onPointerDown={inspect} onFocusCapture={inspect}>
    <b>{ordinal}</b>
    <button type="button" className="visual-image-diff-order-title" disabled={busy || (!isGroup && !entry.promptId)} aria-label={`Run ${title} at position ${ordinal}`} title="Run only this visual prompt step" onClick={() => onRunEntry(entry, ordinal)}>{title}</button>
    <span className="generation-order-flags">
      <span>visible</span>
      <label title="Let later prompt types see this value."><input type="checkbox" aria-label={`Share ${title} with peers at position ${ordinal}`} checked={entry.visibleToPeers} onChange={(event) => onPeers(entry.id, event.target.checked, parentGroupId)} /><span>peers</span></label>
      <label title="Let a later occurrence of this prompt type see and update its previous value."><input type="checkbox" aria-label={`Share ${title} with updates at position ${ordinal}`} checked={entry.visibleToUpdates} onChange={(event) => onUpdates(entry.id, event.target.checked, parentGroupId)} /><span>updates</span></label>
    </span>
    <select aria-label={`Prompt at position ${ordinal}`} value={entry.promptId || ""} disabled={isGroup} onChange={(event) => { onPrompt(entry.id, event.target.value, parentGroupId); onInspectPrompt(event.target.value); }}><option value="">Select prompt</option>{prompts.map((choice) => <option key={choice.id} value={choice.id}>{choice.buttonName || choice.label || choice.id}</option>)}</select>
    <select aria-label={`Model override at position ${ordinal}`} value={entry.modelId || ""} onChange={(event) => onModel(entry.id, event.target.value, parentGroupId)}><option value="">Inherited model</option>{models.filter((model) => model.enabled !== false).map((model) => <option key={model.id} value={model.id}>{modelOptionLabel(model)}</option>)}</select>
    <button type="button" aria-label={`Rotate ${title} left at position ${ordinal}`} title={index === 0 ? "Wrap from the beginning to the end" : "Move one position left"} onClick={() => onRotate(entry.id, -1, parentGroupId)}>←</button>
    <button type="button" aria-label={`Remove ${title} at position ${ordinal}`} title="Remove this occurrence" onClick={() => onRemove(entry.id, parentGroupId)}>×</button>
    <button type="button" aria-label={`Rotate ${title} right at position ${ordinal}`} title={index === siblingCount - 1 ? "Wrap from the end to the beginning" : "Move one position right"} onClick={() => onRotate(entry.id, 1, parentGroupId)}>→</button>
    {isGroup && <div className="generation-order-group-contents">
      {entry.transactionId && <small className="visual-image-group-transaction">{entry.transactionId}{entry.profileId ? ` · ${entry.profileId}` : ""}{entry.continueOnError ? " · continue on error" : ""}</small>}
      {entry.steps?.length ? <ol>{entry.steps.map((child, childIndex) => <CompositionOrderItem key={child.id} entry={child} ordinal={`${ordinal}.${childIndex + 1}`} index={childIndex} siblingCount={entry.steps?.length || 0} parentGroupId={entry.id} selectedGroupId={selectedGroupId} inspectedPromptId={inspectedPromptId} prompts={prompts} models={models} busy={busy} onRunEntry={onRunEntry} onInspectPrompt={onInspectPrompt} onSelectGroup={onSelectGroup} onShuffleGroup={onShuffleGroup} onCopyGroup={onCopyGroup} onClearGroup={onClearGroup} onPeers={onPeers} onUpdates={onUpdates} onPrompt={onPrompt} onModel={onModel} onRotate={onRotate} onRemove={onRemove} />)}</ol> : <p>Empty simultaneous prompt group. Select it, then use + STEPS.</p>}
      <div className="generation-order-group-actions">
        <button type="button" className="generation-order-group-picker" aria-label={`Select group ${ordinal} for insertion`} aria-pressed={selected} onClick={() => onSelectGroup(entry.id)}>{selected ? "SELECTED" : "SELECT"}</button>
        <button type="button" className="generation-order-group-copy" aria-label={`Copy group ${ordinal}`} onClick={() => onCopyGroup(entry.id)}>COPY</button>
        <button type="button" className="generation-order-group-shuffle" aria-label={`Shuffle group ${ordinal}`} disabled={(entry.steps?.length || 0) < 2} onClick={() => onShuffleGroup(entry.id)}>SHUFFLE</button>
        <button type="button" className="generation-order-group-clear" aria-label={`Clear group ${ordinal}`} disabled={!entry.steps?.length} onClick={() => onClearGroup(entry.id)}>CLEAR</button>
      </div>
    </div>}
  </li>;
}

function CompositionOrderAccordionItem({ entry, ordinal, index, siblingCount, stackId, parentGroupId, selectedGroupId, inspectedPromptId, workspaceId, prompts, models, operations, operationImplementations, availableData, busy, modeFor, onMode, onRunEntry, onInspectPrompt, onSelectGroup, onShuffleGroup, onCopyGroup, onClearGroup, onWorkflowStep, onImplementation, onInvocationComplete, onPeers, onUpdates, onPrompt, onModel, onRotate, onRemove }: {
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
  onRunEntry: (entry: PromptCompositionEntry, ordinal: string) => void;
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
  onModel: (id: string, modelId: string, parentGroupId?: string) => void;
  onRotate: (id: string, direction: -1 | 1, parentGroupId?: string) => void;
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
      <button type="button" disabled={busy} onClick={() => onRunEntry(entry, ordinal)}>RUN GROUP</button>
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
    stripContent={(cycleMode) => <div className={`visual-image-diff-subaccordion-strip-control ${isGroup ? "group" : "prompt"}`} onPointerDown={inspect} onFocusCapture={inspect}>
      <button type="button" className="visual-image-diff-subaccordion-strip-ordinal" aria-label={`Cycle accordion size for ${title} at position ${ordinal}`} title="Cycle this accordion through strip, scrolling, and full states" onClick={cycleMode}>{ordinal}</button>
      <button type="button" className="visual-image-diff-order-title" disabled={busy || (!isGroup && !entry.promptId)} aria-label={`Run ${title} at position ${ordinal} from compact strip`} title="Run only this visual prompt step" onClick={() => onRunEntry(entry, ordinal)}>{title}</button>
      <span className="generation-order-flags">
        <span>visible</span>
        <label title="Let later prompt types see this value."><input type="checkbox" aria-label={`Share ${title} with peers at position ${ordinal} in compact strip`} checked={entry.visibleToPeers} onChange={(event) => onPeers(entry.id, event.target.checked, parentGroupId)} /><span>peers</span></label>
        <label title="Let a later occurrence of this prompt type see and update its previous value."><input type="checkbox" aria-label={`Share ${title} with updates at position ${ordinal} in compact strip`} checked={entry.visibleToUpdates} onChange={(event) => onUpdates(entry.id, event.target.checked, parentGroupId)} /><span>updates</span></label>
      </span>
      <select aria-label={`Prompt at position ${ordinal} in compact strip`} value={entry.promptId || ""} disabled={isGroup} onChange={(event) => { onPrompt(entry.id, event.target.value, parentGroupId); onInspectPrompt(event.target.value); }}>
        {isGroup ? <option value="">Simultaneous group</option> : <><option value="">Select prompt</option>{prompts.map((choice) => <option key={choice.id} value={choice.id}>{choice.buttonName || choice.label || choice.id}</option>)}</>}
      </select>
      <select aria-label={`Model override at position ${ordinal} in compact strip`} value={entry.modelId || ""} onChange={(event) => onModel(entry.id, event.target.value, parentGroupId)}><option value="">Inherited model</option>{models.filter((model) => model.enabled !== false).map((model) => <option key={model.id} value={model.id}>{modelOptionLabel(model)}</option>)}</select>
      <button type="button" aria-label={`Rotate ${title} left at position ${ordinal} in compact strip`} title={index === 0 ? "Wrap from the beginning to the end" : "Move one position left"} onClick={() => onRotate(entry.id, -1, parentGroupId)}>←</button>
      <button type="button" aria-label={`Remove ${title} at position ${ordinal} in compact strip`} title="Remove this occurrence" onClick={() => onRemove(entry.id, parentGroupId)}>×</button>
      <button type="button" aria-label={`Rotate ${title} right at position ${ordinal} in compact strip`} title={index === siblingCount - 1 ? "Wrap from the end to the beginning" : "Move one position right"} onClick={() => onRotate(entry.id, 1, parentGroupId)}>→</button>
    </div>}
  >
    {isGroup && <div className="visual-image-diff-subaccordion-group-body">
      {entry.steps?.length ? <ThreeStateAccordionStack id={childStackId} className="visual-image-diff-uix-nested-stack" controlsLabel={`${ordinal} · NESTED PROMPT STACK`}>
        {entry.steps.map((child, childIndex) => <CompositionOrderAccordionItem key={child.id} entry={child} ordinal={`${ordinal}.${childIndex + 1}`} index={childIndex} siblingCount={entry.steps?.length || 0} stackId={childStackId} parentGroupId={entry.id} selectedGroupId={selectedGroupId} inspectedPromptId={inspectedPromptId} workspaceId={workspaceId} prompts={prompts} models={models} operations={operations} operationImplementations={operationImplementations} availableData={availableData} busy={busy} modeFor={modeFor} onMode={onMode} onRunEntry={onRunEntry} onInspectPrompt={onInspectPrompt} onSelectGroup={onSelectGroup} onShuffleGroup={onShuffleGroup} onCopyGroup={onCopyGroup} onClearGroup={onClearGroup} onWorkflowStep={onWorkflowStep} onImplementation={onImplementation} onInvocationComplete={onInvocationComplete} onPeers={onPeers} onUpdates={onUpdates} onPrompt={onPrompt} onModel={onModel} onRotate={onRotate} onRemove={onRemove} />)}
      </ThreeStateAccordionStack> : <p>Empty simultaneous prompt group. Select it, then use an inline + step button.</p>}
    </div>}
  </ThreeStateAccordionMember>;
}

export function VisualImageDiffPage({ pageDefinition, workspaceId, workspaceLabel, models, operations, operationImplementations, onPageDefinitionSaved }: Props) {
  const [document, setDocument] = useState<VisualImageDiffDocument | null>(null);
  const [prompts, setPrompts] = useState<PromptChoice[]>([]);
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
  const [subaccordionModes, setSubaccordionModes] = useState<Record<string, AccordionDisplayMode>>({});
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
  const mode = (key: string) => modes[key] || "scroll";
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
    setModes((current) => current.prompt === "scroll" ? current : { ...current, prompt: "scroll" });
    const frame = window.requestAnimationFrame(() => {
      const panel = window.document.querySelector<HTMLElement>(".visual-image-diff-prompt-inspector");
      panel?.scrollIntoView({ behavior: "smooth", block: "start", inline: "nearest" });
    });
    return () => window.cancelAnimationFrame(frame);
  }, [inspectedPromptId]);

  useEffect(() => {
    let cancelled = false;
    setWorkflowData({});
    setMessage("Loading filesystem resources…");
    Promise.all([
      request(`/api/workspaces/${encodeURIComponent(workspaceId)}/file?path=${encodeURIComponent(MANIFEST_PATH)}`),
      request(`/api/workspaces/${encodeURIComponent(workspaceId)}/prompts`),
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
      const nextPrompts = [...choices.values()];
      const profile = choices.get(nextDocument.promptProfileId);
      const classifiedSteps = nextPrompts
        .filter((prompt) => prompt.applicability?.includes(STEP_APPLICABILITY))
        .sort((left, right) => String(left.classificationId || "￿").localeCompare(String(right.classificationId || "￿")));
      setDocument(nextDocument);
      setPrompts(classifiedSteps);
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

  const promptById = useMemo(() => new Map(prompts.map((prompt) => [prompt.id, prompt])), [prompts]);
  const activePromptEntries = useMemo(() => promptEntries(generationOrder), [generationOrder]);
  const inspectedPrompt = useMemo(() => promptById.get(inspectedPromptId)
    || promptById.get(activePromptEntries[0]?.promptId || "")
    || prompts[0], [activePromptEntries, inspectedPromptId, promptById, prompts]);
  const composedPrompt = useMemo(() => activePromptEntries
    .map((entry) => promptText(promptById.get(entry.promptId || "")))
    .filter(Boolean)
    .join("\n\n"), [activePromptEntries, promptById]);
  const outputs = useMemo(() => [...new Set(activePromptEntries.flatMap((entry) => promptById.get(entry.promptId || "")?.produces || []))], [activePromptEntries, promptById]);
  const selectedGroup = useMemo(() => generationOrder.find((entry) => entry.kind === "group" && entry.id === selectedGroupId), [generationOrder, selectedGroupId]);
  const runnableEntries = useMemo(() => selectedGroup?.steps || generationOrder, [generationOrder, selectedGroup]);
  const runnablePromptEntries = useMemo(() => promptEntries(runnableEntries), [runnableEntries]);
  const sequenceImages = useMemo(() => [
    ...(document?.frames || []).map((frame) => ({
      id: frame.id,
      label: frame.label,
      assetPath: frame.assetPath,
      source: `/api/workspaces/${encodeURIComponent(workspaceId)}/asset?path=${encodeURIComponent(frame.assetPath)}`,
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
      } : {}),
      source_manifest: manifest,
      manifest,
      sequence_context: sequenceContext,
      commands: document?.commands || [],
      ...workflowData,
    };
  }, [document?.commands, document?.id, sequenceContext, sequenceImages, workflowData]);

  const rememberWorkflowOutputs = (nextOutputs: Record<string, unknown>) => {
    setWorkflowData((current) => ({ ...current, ...nextOutputs }));
    setMode("outputs", "scroll");
  };

  const updateEntry = (entryId: string, changes: Partial<PromptCompositionEntry>, parentGroupId?: string) => setGenerationOrder((current) => parentGroupId
    ? current.map((entry) => entry.id === parentGroupId ? { ...entry, steps: (entry.steps || []).map((child) => child.id === entryId ? { ...child, ...changes } : child) } : entry)
    : current.map((entry) => entry.id === entryId ? { ...entry, ...changes } : entry));
  const rotateEntry = (entryId: string, direction: -1 | 1, parentGroupId?: string) => setGenerationOrder((current) => {
    const rotate = (entries: PromptCompositionEntry[]) => {
      const source = entries.findIndex((entry) => entry.id === entryId);
      if (source < 0 || entries.length < 2) return entries;
      const target = (source + direction + entries.length) % entries.length;
      const next = [...entries];
      const [entry] = next.splice(source, 1);
      next.splice(target, 0, entry);
      return next;
    };
    return parentGroupId ? current.map((entry) => entry.id === parentGroupId ? { ...entry, steps: rotate(entry.steps || []) } : entry) : rotate(current);
  });
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
      const payload = await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/models/${encodeURIComponent(modelId)}/invoke`, {
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

  return (
    <section className="english-workflow-page visual-image-diff-page" aria-label="Visual Image Diff">
      <header className="english-workflow-titlebar">
        <div><span>VISUAL IMAGE DIFF</span><h1>{document?.label || "VisualImageDiff"}</h1></div>
        <div className="english-workflow-runtime-status"><i /><b>{workspaceLabel}</b><span>{message}</span></div>
      </header>

      <div ref={columnsRef} className="english-workflow-columns visual-image-diff-columns" style={columnGridStyle}>
        <ThreeStateAccordionStack id="visual-image-diff-left-stack" className="english-workflow-column" controlsLabel="LEFT STACK · DATA" freezeControls>
          <ThreeStateAccordionMember
            stackId="visual-image-diff-left-stack"
            label="RESOURCE OUTPUTS"
            value={Object.keys(workflowData).length ? `${Object.keys(workflowData).length} runtime values` : runResult ? `${submittedImageCount} images · response ready` : `${outputs.length} declared outputs`}
            detail={Object.keys(workflowData).length ? "Real playground outputs available to later workflow steps" : runResult ? `${runResult.modelId || runModel} · ${runResult.latencyMs ?? 0} ms` : "Union of produces declarations from the active group"}
            mode={mode("outputs")}
            onChange={(value) => setMode("outputs", value)}
            baseClass="english-workflow-contract-panel visual-image-diff-outputs"
            scrollSize="680px"
          >
            <ul>{outputs.map((output) => <li key={output}><code>{output}</code></li>)}</ul>
            {Object.keys(workflowData).length > 0 && <section className="visual-image-workflow-data" aria-label="Workflow data available to later steps">
              <h3>WORKFLOW DATA AVAILABLE TO LATER STEPS</h3>
              {Object.entries(workflowData).map(([name, value]) => <div key={name}><b>{name}</b><pre>{typeof value === "string" ? value : JSON.stringify(value, null, 2)}</pre></div>)}
            </section>}
            {running && <div className="visual-image-run-status"><b>Running prompt group</b><span>Preparing and submitting the image sequence…</span></div>}
            {runError && <div className="visual-image-run-error"><b>Invocation failed</b><span>{runError}</span></div>}
            {runResult && <div className="visual-image-run-result">
              <header><b>MODEL RESPONSE</b><span>{runResult.backendId || "resolved backend"} · {runResult.inputTokens ?? 0}/{runResult.outputTokens ?? 0} tokens</span></header>
              <pre>{runResult.text || JSON.stringify(runResult, null, 2)}</pre>
            </div>}
          </ThreeStateAccordionMember>
          <ThreeStateAccordionMember
            stackId="visual-image-diff-left-stack"
            label="IMAGE + COMMAND SEQUENCE"
            value={`${(document?.frames.length || 0) + uploadedImages.length} images · ${document?.commands.length || 0} commands`}
            detail={MANIFEST_PATH}
            mode={mode("sequence")}
            onChange={(value) => setMode("sequence", value)}
            baseClass="english-workflow-panel visual-image-diff-sequence"
            scrollSize="680px"
          >
            <div className="visual-image-input-toolbar">
              <label>
                <b>ADD IMAGES</b>
                <input type="file" accept="image/*" multiple onChange={(event) => { void addUploadedImages(event.target.files); event.target.value = ""; }} />
              </label>
              <span>Every listed image is submitted in sequence order.</span>
              <button type="button" disabled={!uploadedImages.length} onClick={() => setUploadedImages([])}>Clear added images</button>
            </div>
            <div className="visual-image-sequence">
              {document?.frames.map((frame, index) => {
                const command = commandAfter(frame.id);
                return <div className="visual-image-sequence-part" key={frame.id}>
                  <figure>
                    <figcaption><b>{index + 1}</b><span>{frame.label}</span><code>{frame.assetPath}</code></figcaption>
                    <img src={`/api/workspaces/${encodeURIComponent(workspaceId)}/asset?path=${encodeURIComponent(frame.assetPath)}`} alt={frame.label} />
                  </figure>
                  {command && <div className="visual-image-command"><span>ENGLISH COMMAND</span><strong>{command.label || command.command}</strong><code>{command.command}</code></div>}
                </div>;
              })}
              {uploadedImages.map((image, index) => <div className="visual-image-sequence-part visual-image-uploaded" key={image.id}>
                <figure>
                  <figcaption><b>{(document?.frames.length || 0) + index + 1}</b><span>{image.label}</span><code>Added for this run</code></figcaption>
                  <img src={image.dataUrl} alt={image.label} />
                </figure>
              </div>)}
            </div>
          </ThreeStateAccordionMember>
          <ThreeStateAccordionMember
            stackId="visual-image-diff-left-stack"
            label="SEQUENCE CONTEXT"
            value={`${document?.commands.length || 0} transitions`}
            detail="Filesystem manifest facts available to authoring and workflow steps"
            mode={mode("context")}
            onChange={(value) => setMode("context", value)}
            baseClass="english-workflow-contract-panel visual-image-diff-context"
          >
            <ol>{document?.commands.map((command) => <li key={`${command.fromFrameId}:${command.toFrameId}`}><code>{command.fromFrameId}</code><strong>{command.label || command.command}</strong><code>{command.toFrameId}</code></li>)}</ol>
          </ThreeStateAccordionMember>
        </ThreeStateAccordionStack>

        <div
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
        />

        <ThreeStateAccordionStack id="visual-image-diff-center-stack" className="english-workflow-column" controlsLabel="CENTER STACK · AUTHORING" freezeControls>
          <ThreeStateAccordionMember
            stackId="visual-image-diff-center-stack"
            label="GENERATE VISUAL DIFF"
            value={`${generationOrder.length} groups/items · ${promptEntryCount(generationOrder)} prompt steps`}
            detail={document?.promptProfileId || "Waiting for prompt profile"}
            mode={mode("group")}
            onChange={(value) => setMode("group", value)}
            baseClass="english-workflow-panel visual-image-diff-group"
            scrollSize="calc(100vh - 250px)"
          >
            <div className="english-workflow-generation-controls visual-image-generation-controls">
              <label><span>SELECTED MODEL</span><select aria-label="Visual Image Diff run model" value={selectedGroup?.modelId || runModel} onChange={(event) => {
                setRunModel(event.target.value);
                if (selectedGroup) updateEntry(selectedGroup.id, { modelId: event.target.value });
              }}>{models.filter((model) => model.enabled !== false).map((model) => <option key={model.id} value={model.id}>{modelOptionLabel(model)}</option>)}</select></label>
              <fieldset className="english-workflow-contract-order visual-image-diff-composer">
                <legend>VISUAL PIPELINE ORDER · ONE OR GROUPED LLM CALL</legend>
                <div className="english-workflow-output-composer">
                  <div className="english-workflow-output-composer-row" aria-label="Add visual pipeline steps">
                    {prompts.map((prompt) => <button type="button" key={prompt.id} disabled={running} title={`${prompt.classificationId || "Unclassified"} · ${prompt.label || prompt.id}`} onClick={() => addPrompt(prompt.id)}>+ {prompt.buttonName || prompt.label || prompt.id}</button>)}
                    <button type="button" className="english-workflow-group-output" disabled={running} title="Create and select an empty simultaneous prompt group" onClick={addGroup}>[+group]</button>
                  </div>
                  {!prompts.length && <small>No effective Prompt resources declare applicability <code>{STEP_APPLICABILITY}</code>.</small>}
                </div>
                <ol className="visual-image-group-list">
                  {generationOrder.map((entry, index) => <CompositionOrderItem key={entry.id} entry={entry} ordinal={`${index + 1}`} index={index} siblingCount={generationOrder.length} selectedGroupId={selectedGroupId} inspectedPromptId={inspectedPrompt?.id || ""} prompts={prompts} models={models} busy={running} onRunEntry={(entry) => { void runPrompts([entry], entry.modelId || runModel); }} onInspectPrompt={setInspectedPromptId} onSelectGroup={(id) => setSelectedGroupId((current) => current === id ? null : id)} onShuffleGroup={shuffleGroup} onCopyGroup={copyGroup} onClearGroup={clearGroup} onPeers={(id, value, parentId) => updateEntry(id, { visibleToPeers: value }, parentId)} onUpdates={(id, value, parentId) => updateEntry(id, { visibleToUpdates: value }, parentId)} onPrompt={(id, promptId, parentId) => updateEntry(id, { promptId }, parentId)} onModel={(id, modelId, parentId) => updateEntry(id, { modelId }, parentId)} onRotate={rotateEntry} onRemove={removeEntry} />)}
                  {!generationOrder.length && <li className="empty">Use [+group] or an inline + step button to compose the ordered prompt call.</li>}
                </ol>
                <div className="english-workflow-order-actions">
                  <button type="button" disabled={running} onClick={restoreProfileGroup}>Restore five profile groups</button>
                  <button type="button" disabled={running || generationOrder.length < 2} onClick={() => setGenerationOrder((current) => shuffledEntries(current))}>Shuffle order</button>
                  <button type="button" disabled={running || !generationOrder.length} onClick={() => { setGenerationOrder([]); setSelectedGroupId(null); }}>Clear order</button>
                </div>
                {selectedGroup && <VisualImageDiffOperationSurface
                  entry={selectedGroup}
                  title={selectedGroup.label ? `[group] ${selectedGroup.label}` : "[group]"}
                  workspaceId={workspaceId}
                  prompts={prompts}
                  models={models}
                  operations={operations}
                  operationImplementations={operationImplementations}
                  availableData={availableData}
                  onInspectPrompt={setInspectedPromptId}
                  onWorkflowStep={(id, workflowStep) => updateEntry(id, { workflowStep })}
                  onImplementation={(id, implementationId) => updateEntry(id, { implementationId })}
                  onInvocationComplete={rememberWorkflowOutputs}
                  showHeader
                />}
                <small>Run follows the selected scope. Any named row title runs that step as a quick call; [group] runs only that group. Prompt, model, peers, and updates routing stays attached to every occurrence.</small>
              </fieldset>
              <button type="button" className="primary" disabled={running || !runnablePromptEntries.length || !runModel} onClick={() => { void runPrompts(); }}>{running ? "Running prompt group…" : selectedGroup ? "▶ Run selected group" : "▶ Run composition"}</button>
              <small>{selectedGroup ? "Runs the selected [group] as one model call." : "Runs the complete composition as one model call."} All sequence images are combined into one labeled contact sheet for the model endpoint.</small>
            </div>
          </ThreeStateAccordionMember>
          <ThreeStateAccordionMember
            stackId="visual-image-diff-center-stack"
            label="GENERATE VISUAL DIFF · SUBACCORDION UIX"
            value={`${generationOrder.length} groups/items · ${promptEntryCount(generationOrder)} prompt steps`}
            detail="UIX comparison · every pipeline item is a ThreeStateAccordionMember"
            mode={mode("groupAccordion")}
            onChange={(value) => setMode("groupAccordion", value)}
            baseClass="english-workflow-panel visual-image-diff-group visual-image-diff-subaccordion-version"
            scrollSize="calc(100vh - 250px)"
          >
            <div className="english-workflow-generation-controls visual-image-generation-controls">
              <label><span>SELECTED MODEL</span><select aria-label="Visual Image Diff subaccordion run model" value={selectedGroup?.modelId || runModel} onChange={(event) => {
                setRunModel(event.target.value);
                if (selectedGroup) updateEntry(selectedGroup.id, { modelId: event.target.value });
              }}>{models.filter((model) => model.enabled !== false).map((model) => <option key={model.id} value={model.id}>{modelOptionLabel(model)}</option>)}</select></label>
              <fieldset className="english-workflow-contract-order visual-image-diff-composer visual-image-diff-subaccordion-composer">
                <legend>VISUAL PIPELINE ORDER · SUBACCORDION UIX</legend>
                <div className="english-workflow-output-composer">
                  <div className="english-workflow-output-composer-row" aria-label="Add visual pipeline steps in subaccordion version">
                    {prompts.map((prompt) => <button type="button" key={prompt.id} disabled={running} title={`${prompt.classificationId || "Unclassified"} · ${prompt.label || prompt.id}`} onClick={() => addPrompt(prompt.id)}>+ {prompt.buttonName || prompt.label || prompt.id}</button>)}
                    <button type="button" className="english-workflow-group-output" disabled={running} title="Create and select an empty simultaneous prompt group" onClick={addGroup}>[+group]</button>
                  </div>
                  {!prompts.length && <small>No effective Prompt resources declare applicability <code>{STEP_APPLICABILITY}</code>.</small>}
                </div>
                <ThreeStateAccordionStack id="visual-image-diff-uix-pipeline-stack" className="visual-image-diff-uix-pipeline-stack" controlsLabel="PIPELINE SUBACCORDION STACK">
                  {generationOrder.map((entry, index) => <CompositionOrderAccordionItem key={entry.id} entry={entry} ordinal={`${index + 1}`} index={index} siblingCount={generationOrder.length} stackId="visual-image-diff-uix-pipeline-stack" selectedGroupId={selectedGroupId} inspectedPromptId={inspectedPrompt?.id || ""} workspaceId={workspaceId} prompts={prompts} models={models} operations={operations} operationImplementations={operationImplementations} availableData={availableData} busy={running} modeFor={subaccordionMode} onMode={setSubaccordionMode} onRunEntry={(entry) => { void runPrompts([entry], entry.modelId || runModel); }} onInspectPrompt={setInspectedPromptId} onSelectGroup={(id) => setSelectedGroupId((current) => current === id ? null : id)} onShuffleGroup={shuffleGroup} onCopyGroup={copyGroup} onClearGroup={clearGroup} onWorkflowStep={(id, workflowStep) => updateEntry(id, { workflowStep })} onImplementation={(id, implementationId) => updateEntry(id, { implementationId })} onInvocationComplete={rememberWorkflowOutputs} onPeers={(id, value, parentId) => updateEntry(id, { visibleToPeers: value }, parentId)} onUpdates={(id, value, parentId) => updateEntry(id, { visibleToUpdates: value }, parentId)} onPrompt={(id, promptId, parentId) => updateEntry(id, { promptId }, parentId)} onModel={(id, modelId, parentId) => updateEntry(id, { modelId }, parentId)} onRotate={rotateEntry} onRemove={removeEntry} />)}
                  {!generationOrder.length && <p className="empty">Use [+group] or an inline + step button to compose the ordered prompt call.</p>}
                </ThreeStateAccordionStack>
                <div className="english-workflow-order-actions">
                  <button type="button" disabled={running} onClick={restoreProfileGroup}>Restore five profile groups</button>
                  <button type="button" disabled={running || generationOrder.length < 2} onClick={() => setGenerationOrder((current) => shuffledEntries(current))}>Shuffle order</button>
                  <button type="button" disabled={running || !generationOrder.length} onClick={() => { setGenerationOrder([]); setSelectedGroupId(null); }}>Clear order</button>
                </div>
                <small>This UIX version edits the same live composition as the original above. Only the list presentation changes: groups and Prompt steps are native nested accordion members.</small>
              </fieldset>
              <button type="button" className="primary" disabled={running || !runnablePromptEntries.length || !runModel} onClick={() => { void runPrompts(); }}>{running ? "Running prompt group…" : selectedGroup ? "▶ Run selected group · SUBACCORDION" : "▶ Run composition · SUBACCORDION"}</button>
              <small>{selectedGroup ? "Runs the selected [group] as one model call." : "Runs the complete composition as one model call."} All sequence images are combined into one labeled contact sheet for the model endpoint.</small>
            </div>
          </ThreeStateAccordionMember>
        </ThreeStateAccordionStack>

        <div
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
        />

        <ThreeStateAccordionStack id="visual-image-diff-right-stack" className="english-workflow-column english-workflow-contract" controlsLabel="RIGHT STACK · SOURCE DETAILS" freezeControls>
          <ThreeStateAccordionMember
            stackId="visual-image-diff-right-stack"
            label="CURRENT PAGE SPECIFICATION"
            value={`${pageDefinition.id}.workflow_page.json`}
            detail="Resolved three-column page JSON"
            mode={mode("pageSpecification")}
            onChange={(value) => setMode("pageSpecification", value)}
            baseClass="english-workflow-contract-panel visual-image-diff-page-source"
            scrollSize="520px"
          >
            <WorkflowPageSourceEditor workspaceId={workspaceId} pageId={pageDefinition.id} disabled={running} onSaved={onPageDefinitionSaved} />
          </ThreeStateAccordionMember>
          <ThreeStateAccordionMember
            stackId="visual-image-diff-right-stack"
            label="PROMPT CONTENT"
            value={inspectedPrompt?.buttonName || inspectedPrompt?.label || "Touch a prompt step"}
            detail={inspectedPrompt?.id || "Individual pipeline Prompt resource"}
            mode={mode("prompt")}
            onChange={(value) => setMode("prompt", value)}
            baseClass="english-workflow-contract-panel visual-image-diff-prompt-inspector"
            scrollSize="520px"
          >
            {inspectedPrompt ? <section>
              <dl>
                <div><dt>PROMPT ID</dt><dd><code>{inspectedPrompt.id}</code></dd></div>
                <div><dt>LABEL</dt><dd>{inspectedPrompt.label || inspectedPrompt.buttonName || inspectedPrompt.id}</dd></div>
                <div><dt>CLASSIFICATION</dt><dd><code>{inspectedPrompt.classificationId || "Unclassified"}</code></dd></div>
                <div><dt>APPLICABILITY</dt><dd>{inspectedPrompt.applicability?.length ? inspectedPrompt.applicability.map((value) => <code key={value}>{value}</code>) : <span>None declared</span>}</dd></div>
                <div><dt>PRODUCES</dt><dd>{inspectedPrompt.produces?.length ? inspectedPrompt.produces.map((value) => <code key={value}>{value}</code>) : <span>None declared</span>}</dd></div>
              </dl>
              <pre aria-label="Selected visual prompt contents">{promptText(inspectedPrompt) || "This Prompt resource does not declare text."}</pre>
            </section> : <p>Touch an individual pipeline prompt row to inspect its complete filesystem-backed contents.</p>}
          </ThreeStateAccordionMember>
          <ThreeStateAccordionMember
            stackId="visual-image-diff-right-stack"
            label="COMPOSED GROUP PROMPT"
            value={`${promptEntryCount(generationOrder)} prompt steps`}
            detail="Live composition from the selected resource order"
            mode={mode("composed")}
            onChange={(value) => setMode("composed", value)}
            baseClass="english-workflow-contract-panel visual-image-diff-composed"
            scrollSize="520px"
          >
            <pre>{composedPrompt || "Add a prompt resource with + STEPS."}</pre>
          </ThreeStateAccordionMember>
        </ThreeStateAccordionStack>
      </div>

      <footer className="english-workflow-statusbar">
        <span><i />Filesystem backed</span><span>{document?.id || "Loading manifest"}</span><span>{generationOrder.length} groups/items · {promptEntryCount(generationOrder)} prompt steps</span><span>{runResult ? `${submittedImageCount} images submitted` : `${outputs.length} outputs`}</span>
      </footer>
    </section>
  );
}
