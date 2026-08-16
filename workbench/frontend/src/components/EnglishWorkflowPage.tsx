import { useEffect, useRef, useState } from "react";
import {
  ThreeStateAccordionMember,
  ThreeStateAccordionStack,
  type AccordionDisplayMode,
} from "./ThreeStateAccordion";
import "../styles/english_workflow.css";
import "../styles/english_workflow_order.css";

type WorkflowStep = {
  id: string;
  label?: string;
  operation?: string;
  dependsOn?: string[];
  inputs?: Record<string, unknown>;
  outputs?: Record<string, string>;
};

type WorkflowDocument = {
  id: string;
  label?: string;
  description?: string;
  inputs?: Record<string, string>;
  outputs?: Record<string, string>;
  steps: WorkflowStep[];
  generation?: {
    operation?: string;
    englishDescriptionPath?: string;
    generationOrderPath?: string;
    preferredFormat?: string;
    operationCategories?: string[];
  };
};

type OperationDocument = {
  id: string;
  label?: string;
  description?: string;
  categories?: string[];
  preferredChild?: string;
};

type ModelChoice = {
  id: string;
  label?: string;
  backendId?: string;
  enabled?: boolean;
};

type PromptChoice = {
  id: string;
  label?: string;
  description?: string;
  kind?: string;
  text?: string | string[];
  enabled?: boolean;
};

type DatatypeDocument = {
  id: string;
  kind?: string;
  label?: string;
  description?: string;
  parents?: unknown;
  preferredChild?: string;
  [key: string]: unknown;
};

type MemoryValue = {
  kind?: string;
  id: string;
  label?: string;
  datatype?: string;
  source?: object;
  defaultValue?: unknown;
};

type Props = {
  workspaceId: string;
  workspaceLabel: string;
  workflow: WorkflowDocument;
  workflowPath: string;
  description: string;
  savedDescription: string;
  onDescriptionChange: (value: string) => void;
  onSaveDescription: () => Promise<void> | void;
  operation?: OperationDocument;
  operationCatalog: OperationDocument[];
  models: ModelChoice[];
  memoryValues: MemoryValue[];
  onGenerated: (outputs: Record<string, unknown>) => void;
  onApply: () => Promise<void> | void;
  onOpenWorkflow: () => void;
};

type GenerationPhase = "idle" | "analyzed" | "planned" | "generated" | "validated" | "error";

type GenerationContract = {
  summary: string;
  memory: Array<{ name: string; datatype: string; requirement: string }>;
  checklist: string[];
  outputs: string[];
  rules: string[];
  englishsteps: Array<{ stepId: string; label: string; purpose: string; dependsOn: string[]; controlFlow: string }>;
  steps: Array<Record<string, unknown>>;
  libops: Array<{ operationId: string; label: string; description: string; inputs: Record<string, string>; outputs: Record<string, string> }>;
  matchops: Array<{ requirement: string; operationId: string; status: string; rationale: string }>;
  inventops: Array<{ requirement: string; operationId: string; description: string; inputs: Record<string, string>; outputs: Record<string, string>; constraints: string[]; status: string }>;
  codeops: Array<{ operationId: string; implementationId: string; implementationType: string; description: string; entrypoint: string; inputs: Record<string, string>; outputs: Record<string, string>; constraints: string[]; status: string }>;
  promptops: Array<{ operationId: string; promptId: string; label: string; instructions: string; inputBindings: string[]; outputContract: Record<string, string>; modelRequirements: string[]; status: string }>;
  libdt: Array<{ datatypeId: string; kind: string; label: string; description: string }>;
  matchdt: Array<{ requirement: string; datatypeId: string; representationId: string; concreteDatatypeId: string; status: string; rationale: string }>;
  inventdt: Array<{ requirement: string; datatypeId: string; kind: string; description: string; parents: string[]; constraints: string[]; status: string }>;
  codedt: Array<{ datatypeId: string; representationId: string; concreteDatatypeId: string; encoding: string; validator: string; conversionOperations: string[]; constraints: string[]; status: string }>;
  libwf: Array<{ workflowId: string; label: string; description: string; inputs: Record<string, string>; outputs: Record<string, string> }>;
  matchwf: Array<{ requirement: string; workflowId: string; status: string; rationale: string }>;
  inventwf: Array<{ requirement: string; workflowId: string; description: string; inputs: Record<string, string>; outputs: Record<string, string>; constraints: string[]; status: string }>;
  codewf: Array<{ workflowId: string; stepIds: string[]; operationIds: string[]; datatypeIds: string[]; unresolvedOperations: string[]; unresolvedDatatypes: string[]; status: string }>;
};

type ContractSection = keyof GenerationContract;
type GenerationOutputName = ContractSection | "workflow" | "group";
type GenerationStepRequest = { name: GenerationOutputName; visibility: { peers: boolean; updates: boolean }; promptId?: string; modelId?: string; steps?: GenerationStepRequest[] };
type GenerationOrderEntry = { id: string; name: GenerationOutputName; visibleToPeers: boolean; visibleToUpdates: boolean; promptId?: string; modelId?: string; steps?: GenerationOrderEntry[] };

type ContractTrial = {
  id: string;
  requestedOrder: GenerationOutputName[];
  returnedOrder: GenerationOutputName[];
  requestedSteps: GenerationStepRequest[];
  score: number;
  checklistCount: number;
  memoryCount: number;
  workflowSteps: number;
  validationIssues: number;
  libraryOpsCount: number;
  matchOpsCount: number;
  inventedOpsCount: number;
  codedOpsCount: number;
  promptedOpsCount: number;
  libraryDtCount: number;
  matchDtCount: number;
  inventedDtCount: number;
  codedDtCount: number;
  libraryWfCount: number;
  matchWfCount: number;
  inventedWfCount: number;
  codedWfCount: number;
  englishStepCount: number;
  formalStepCount: number;
  modelId: string;
};

type GenerationStepEvent = {
  id: string;
  action: string;
  outputs: string[];
  detail: string;
};

const CONTRACT_SECTIONS: GenerationOutputName[] = ["summary", "memory", "checklist", "outputs", "rules", "englishsteps", "steps", "workflow", "libops", "matchops", "inventops", "codeops", "promptops", "libdt", "matchdt", "inventdt", "codedt", "libwf", "matchwf", "inventwf", "codewf"];
const CONTRACT_SECTION_ROWS: Array<{ id: string; names: GenerationOutputName[] }> = [
  { id: "contract", names: CONTRACT_SECTIONS.slice(0, 8) },
  { id: "operations", names: CONTRACT_SECTIONS.slice(8, 13) },
  { id: "datatypes", names: CONTRACT_SECTIONS.slice(13, 17) },
  { id: "workflows", names: CONTRACT_SECTIONS.slice(17) },
];
const GENERATION_OUTPUTS: GenerationOutputName[] = [...CONTRACT_SECTIONS, "group"];
const DEFAULT_PROMPT_BY_OUTPUT: Record<GenerationOutputName, string> = {
  summary: "workflow.generation.summary",
  memory: "workflow.generation.memory",
  checklist: "workflow.generation.checklist",
  outputs: "workflow.generation.outputs",
  rules: "workflow.generation.rules",
  englishsteps: "workflow.generation.englishsteps",
  steps: "workflow.generation.steps",
  workflow: "workflow.generation.workflow",
  libops: "workflow.generation.libops",
  matchops: "workflow.generation.matchops",
  inventops: "workflow.generation.inventops",
  codeops: "workflow.generation.codeops",
  promptops: "workflow.generation.promptops",
  libdt: "workflow.generation.libdt",
  matchdt: "workflow.generation.matchdt",
  inventdt: "workflow.generation.inventdt",
  codedt: "workflow.generation.codedt",
  libwf: "workflow.generation.libwf",
  matchwf: "workflow.generation.matchwf",
  inventwf: "workflow.generation.inventwf",
  codewf: "workflow.generation.codewf",
  group: "workflow.analyze_generation_contract",
};

function initialGenerationOrder(): GenerationOrderEntry[] {
  return [];
}

function savedGenerationOrder(value: unknown, prefix = "saved"): GenerationOrderEntry[] | null {
  if (!Array.isArray(value)) return null;
  const entries = value.flatMap((item, index): GenerationOrderEntry[] => {
    if (!item || typeof item !== "object" || Array.isArray(item)) return [];
    const record = item as Record<string, unknown>;
    const name = String(record.name || "") as GenerationOutputName;
    if (!GENERATION_OUTPUTS.includes(name)) return [];
    const steps = name === "group" ? savedGenerationOrder(record.steps || [], `${prefix}:${index}`) : undefined;
    if (name === "group" && steps === null) return [];
    const promptId = String(record.promptId || DEFAULT_PROMPT_BY_OUTPUT[name] || "").trim();
    const modelId = String(record.modelId || "").trim();
    return [{
      id: `${prefix}:${index}:${name}`,
      name,
      visibleToPeers: typeof record.visibleToPeers === "boolean" ? record.visibleToPeers : record.peers !== false,
      visibleToUpdates: record.visibleToUpdates === true || record.updates === true,
      ...(promptId ? { promptId } : {}),
      ...(modelId ? { modelId } : {}),
      ...(steps ? { steps } : {}),
    }];
  });
  return entries.length === value.length ? entries : null;
}

function generationRequest(entries: GenerationOrderEntry[]): GenerationStepRequest[] {
  return entries.map(({ name, visibleToPeers, visibleToUpdates, promptId, modelId, steps }) => ({
    name,
    visibility: { peers: visibleToPeers, updates: visibleToUpdates },
    ...(promptId ? { promptId } : {}),
    ...(modelId ? { modelId } : {}),
    ...(name === "group" ? { steps: generationRequest(steps || []) } : {}),
  }));
}

function containsGenerationOutput(entries: GenerationOrderEntry[], name: GenerationOutputName): boolean {
  return entries.some((entry) => entry.name === name || containsGenerationOutput(entry.steps || [], name));
}

function hasGenerativeStep(entries: GenerationOrderEntry[]): boolean {
  return entries.length > 0;
}

function generationStepSummary(step: GenerationStepRequest): string {
  const children = step.steps?.map(generationStepSummary).join(" + ") || "all outputs";
  const routing = `${step.promptId ? ` · prompt:${step.promptId}` : ""}${step.modelId ? ` · model:${step.modelId}` : ""}`;
  const visibility = `visible:${step.visibility.peers ? "peers" : ""}${step.visibility.peers && step.visibility.updates ? "+" : ""}${step.visibility.updates ? "updates" : ""}`;
  return step.name === "group" ? `group[${children}] · ${visibility}${routing}` : `${step.name} · ${visibility}${routing}`;
}

async function request(path: string, init?: RequestInit) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json", ...(init?.headers || {}) },
    ...init,
  });
  const text = await response.text();
  let payload: Record<string, unknown> = {};
  try {
    payload = text ? (JSON.parse(text) as Record<string, unknown>) : {};
  } catch {
    throw new Error(text || response.statusText);
  }
  if (!response.ok) {
    const detail = payload.error || payload.detail || response.statusText;
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  return payload;
}

function parseContract(value: unknown): GenerationContract {
  if (!value || typeof value !== "object" || Array.isArray(value)) throw new Error("The contract Operation did not return generation_contract.");
  const record = value as Record<string, unknown>;
  const strings = (name: ContractSection) => Array.isArray(record[name]) ? (record[name] as unknown[]).map(String).filter(Boolean) : [];
  const memory = Array.isArray(record.memory) ? record.memory.flatMap((item) => {
    if (!item || typeof item !== "object" || Array.isArray(item)) return [];
    const entry = item as Record<string, unknown>;
    const name = String(entry.name || "").trim();
    return name ? [{ name, datatype: String(entry.datatype || "Any"), requirement: String(entry.requirement || "Required by the analyzed English specification.") }] : [];
  }) : [];
  const englishsteps = Array.isArray(record.englishsteps) ? record.englishsteps.flatMap((item, index) => {
    if (typeof item === "string" && item.trim()) return [{ stepId: `step_${index + 1}`, label: item.trim(), purpose: item.trim(), dependsOn: [], controlFlow: "sequence" }];
    if (!item || typeof item !== "object" || Array.isArray(item)) return [];
    const entry = item as Record<string, unknown>;
    const purpose = String(entry.purpose || entry.description || entry.label || "").trim();
    if (!purpose) return [];
    return [{
      stepId: String(entry.stepId || entry.id || `step_${index + 1}`),
      label: String(entry.label || purpose),
      purpose,
      dependsOn: Array.isArray(entry.dependsOn) ? entry.dependsOn.map(String).filter(Boolean) : [],
      controlFlow: String(entry.controlFlow || "sequence"),
    }];
  }) : [];
  const steps = Array.isArray(record.steps) ? record.steps.flatMap((item) => item && typeof item === "object" && !Array.isArray(item) ? [item as Record<string, unknown>] : []) : [];
  const matchops = Array.isArray(record.matchops) ? record.matchops.flatMap((item) => {
    if (typeof item === "string" && item.trim()) return [{ requirement: item.trim(), operationId: "", status: "unresolved", rationale: "" }];
    if (!item || typeof item !== "object" || Array.isArray(item)) return [];
    const entry = item as Record<string, unknown>;
    const requirement = String(entry.requirement || "").trim();
    if (!requirement) return [];
    return [{ requirement, operationId: String(entry.operationId || ""), status: String(entry.status || (entry.operationId ? "matched" : "unresolved")), rationale: String(entry.rationale || "") }];
  }) : [];
  const libops = Array.isArray(record.libops) ? record.libops.flatMap((item) => {
    if (!item || typeof item !== "object" || Array.isArray(item)) return [];
    const entry = item as Record<string, unknown>;
    const operationId = String(entry.operationId || entry.id || "").trim();
    if (!operationId) return [];
    const typedPorts = (value: unknown) => value && typeof value === "object" && !Array.isArray(value)
      ? Object.fromEntries(Object.entries(value as Record<string, unknown>).map(([name, datatype]) => [name, String(datatype)]))
      : {};
    return [{ operationId, label: String(entry.label || operationId), description: String(entry.description || ""), inputs: typedPorts(entry.inputs), outputs: typedPorts(entry.outputs) }];
  }) : [];
  const inventops = Array.isArray(record.inventops) ? record.inventops.flatMap((item) => {
    if (!item || typeof item !== "object" || Array.isArray(item)) return [];
    const entry = item as Record<string, unknown>;
    const requirement = String(entry.requirement || "").trim();
    const operationId = String(entry.operationId || "").trim();
    if (!requirement || !operationId) return [];
    const typedPorts = (value: unknown) => value && typeof value === "object" && !Array.isArray(value)
      ? Object.fromEntries(Object.entries(value as Record<string, unknown>).map(([name, datatype]) => [name, String(datatype)]))
      : {};
    return [{
      requirement,
      operationId,
      description: String(entry.description || ""),
      inputs: typedPorts(entry.inputs),
      outputs: typedPorts(entry.outputs),
      constraints: Array.isArray(entry.constraints) ? entry.constraints.map(String).filter(Boolean) : [],
      status: String(entry.status || "proposed"),
    }];
  }) : [];
  const codeops = Array.isArray(record.codeops) ? record.codeops.flatMap((item) => {
    if (!item || typeof item !== "object" || Array.isArray(item)) return [];
    const entry = item as Record<string, unknown>;
    const operationId = String(entry.operationId || "").trim();
    const implementationId = String(entry.implementationId || "").trim();
    if (!operationId || !implementationId) return [];
    const typedPorts = (value: unknown) => value && typeof value === "object" && !Array.isArray(value)
      ? Object.fromEntries(Object.entries(value as Record<string, unknown>).map(([name, datatype]) => [name, String(datatype)]))
      : {};
    return [{
      operationId,
      implementationId,
      implementationType: String(entry.implementationType || "unselected"),
      description: String(entry.description || ""),
      entrypoint: String(entry.entrypoint || ""),
      inputs: typedPorts(entry.inputs),
      outputs: typedPorts(entry.outputs),
      constraints: Array.isArray(entry.constraints) ? entry.constraints.map(String).filter(Boolean) : [],
      status: String(entry.status || "proposed"),
    }];
  }) : [];
  const promptops = Array.isArray(record.promptops) ? record.promptops.flatMap((item) => {
    if (!item || typeof item !== "object" || Array.isArray(item)) return [];
    const entry = item as Record<string, unknown>;
    const operationId = String(entry.operationId || "").trim();
    const promptId = String(entry.promptId || "").trim();
    if (!operationId || !promptId) return [];
    const outputContract = entry.outputContract && typeof entry.outputContract === "object" && !Array.isArray(entry.outputContract)
      ? Object.fromEntries(Object.entries(entry.outputContract as Record<string, unknown>).map(([name, datatype]) => [name, String(datatype)]))
      : {};
    return [{
      operationId,
      promptId,
      label: String(entry.label || promptId),
      instructions: String(entry.instructions || ""),
      inputBindings: Array.isArray(entry.inputBindings) ? entry.inputBindings.map(String).filter(Boolean) : [],
      outputContract,
      modelRequirements: Array.isArray(entry.modelRequirements) ? entry.modelRequirements.map(String).filter(Boolean) : [],
      status: String(entry.status || "proposed"),
    }];
  }) : [];
  const libdt = Array.isArray(record.libdt) ? record.libdt.flatMap((item) => {
    if (!item || typeof item !== "object" || Array.isArray(item)) return [];
    const entry = item as Record<string, unknown>;
    const datatypeId = String(entry.datatypeId || entry.id || "").trim();
    return datatypeId ? [{ datatypeId, kind: String(entry.kind || "semantic_datatype"), label: String(entry.label || datatypeId), description: String(entry.description || "") }] : [];
  }) : [];
  const matchdt = Array.isArray(record.matchdt) ? record.matchdt.flatMap((item) => {
    if (!item || typeof item !== "object" || Array.isArray(item)) return [];
    const entry = item as Record<string, unknown>;
    const requirement = String(entry.requirement || "").trim();
    if (!requirement) return [];
    const datatypeId = String(entry.datatypeId || "").trim();
    return [{
      requirement,
      datatypeId,
      representationId: String(entry.representationId || ""),
      concreteDatatypeId: String(entry.concreteDatatypeId || ""),
      status: String(entry.status || (datatypeId ? "matched" : "unresolved")),
      rationale: String(entry.rationale || ""),
    }];
  }) : [];
  const inventdt = Array.isArray(record.inventdt) ? record.inventdt.flatMap((item) => {
    if (!item || typeof item !== "object" || Array.isArray(item)) return [];
    const entry = item as Record<string, unknown>;
    const requirement = String(entry.requirement || "").trim();
    const datatypeId = String(entry.datatypeId || "").trim();
    if (!requirement || !datatypeId) return [];
    return [{
      requirement,
      datatypeId,
      kind: String(entry.kind || "semantic_datatype"),
      description: String(entry.description || ""),
      parents: Array.isArray(entry.parents) ? entry.parents.map(String).filter(Boolean) : [],
      constraints: Array.isArray(entry.constraints) ? entry.constraints.map(String).filter(Boolean) : [],
      status: String(entry.status || "proposed"),
    }];
  }) : [];
  const codedt = Array.isArray(record.codedt) ? record.codedt.flatMap((item) => {
    if (!item || typeof item !== "object" || Array.isArray(item)) return [];
    const entry = item as Record<string, unknown>;
    const datatypeId = String(entry.datatypeId || "").trim();
    const representationId = String(entry.representationId || "").trim();
    if (!datatypeId || !representationId) return [];
    return [{
      datatypeId,
      representationId,
      concreteDatatypeId: String(entry.concreteDatatypeId || ""),
      encoding: String(entry.encoding || ""),
      validator: String(entry.validator || ""),
      conversionOperations: Array.isArray(entry.conversionOperations) ? entry.conversionOperations.map(String).filter(Boolean) : [],
      constraints: Array.isArray(entry.constraints) ? entry.constraints.map(String).filter(Boolean) : [],
      status: String(entry.status || "proposed"),
    }];
  }) : [];
  const libwf = Array.isArray(record.libwf) ? record.libwf.flatMap((item) => {
    if (!item || typeof item !== "object" || Array.isArray(item)) return [];
    const entry = item as Record<string, unknown>;
    const workflowId = String(entry.workflowId || entry.id || "").trim();
    if (!workflowId) return [];
    const typedPorts = (value: unknown) => value && typeof value === "object" && !Array.isArray(value)
      ? Object.fromEntries(Object.entries(value as Record<string, unknown>).map(([name, datatype]) => [name, String(datatype)]))
      : {};
    return [{ workflowId, label: String(entry.label || workflowId), description: String(entry.description || ""), inputs: typedPorts(entry.inputs), outputs: typedPorts(entry.outputs) }];
  }) : [];
  const matchwf = Array.isArray(record.matchwf) ? record.matchwf.flatMap((item) => {
    if (!item || typeof item !== "object" || Array.isArray(item)) return [];
    const entry = item as Record<string, unknown>;
    const requirement = String(entry.requirement || "").trim();
    if (!requirement) return [];
    const workflowId = String(entry.workflowId || "").trim();
    return [{ requirement, workflowId, status: String(entry.status || (workflowId ? "matched" : "unresolved")), rationale: String(entry.rationale || "") }];
  }) : [];
  const inventwf = Array.isArray(record.inventwf) ? record.inventwf.flatMap((item) => {
    if (!item || typeof item !== "object" || Array.isArray(item)) return [];
    const entry = item as Record<string, unknown>;
    const requirement = String(entry.requirement || "").trim();
    const workflowId = String(entry.workflowId || "").trim();
    if (!requirement || !workflowId) return [];
    const typedPorts = (value: unknown) => value && typeof value === "object" && !Array.isArray(value)
      ? Object.fromEntries(Object.entries(value as Record<string, unknown>).map(([name, datatype]) => [name, String(datatype)]))
      : {};
    return [{
      requirement,
      workflowId,
      description: String(entry.description || ""),
      inputs: typedPorts(entry.inputs),
      outputs: typedPorts(entry.outputs),
      constraints: Array.isArray(entry.constraints) ? entry.constraints.map(String).filter(Boolean) : [],
      status: String(entry.status || "proposed"),
    }];
  }) : [];
  const codewf = Array.isArray(record.codewf) ? record.codewf.flatMap((item) => {
    if (!item || typeof item !== "object" || Array.isArray(item)) return [];
    const entry = item as Record<string, unknown>;
    const workflowId = String(entry.workflowId || "").trim();
    if (!workflowId) return [];
    const strings = (name: string) => Array.isArray(entry[name]) ? (entry[name] as unknown[]).map(String).filter(Boolean) : [];
    return [{
      workflowId,
      stepIds: strings("stepIds"),
      operationIds: strings("operationIds"),
      datatypeIds: strings("datatypeIds"),
      unresolvedOperations: strings("unresolvedOperations"),
      unresolvedDatatypes: strings("unresolvedDatatypes"),
      status: String(entry.status || "proposed"),
    }];
  }) : [];
  return {
    summary: String(record.summary || "").trim(),
    memory,
    checklist: strings("checklist"),
    outputs: strings("outputs"),
    rules: strings("rules"),
    englishsteps,
    steps,
    libops,
    matchops,
    inventops,
    codeops,
    promptops,
    libdt,
    matchdt,
    inventdt,
    codedt,
    libwf,
    matchwf,
    inventwf,
    codewf,
  };
}

function contractScore(contract: GenerationContract, candidate: WorkflowDocument | null, validationIssues: number) {
  return Math.round(
    (contract.summary ? 15 : 0)
    + Math.min(contract.memory.length, 4) * 5
    + Math.min(contract.checklist.length, 6) * 5
    + Math.min(contract.outputs.length, 2) * 5
    + Math.min(contract.rules.length, 2) * 5
    + (candidate?.steps.length ? 5 : 0)
    + (candidate?.steps.length && validationIssues === 0 ? 10 : 0),
  );
}

function shuffledGenerationOrder(entries: GenerationOrderEntry[]) {
  const result = [...entries];
  for (let index = result.length - 1; index > 0; index -= 1) {
    const swapIndex = Math.floor(Math.random() * (index + 1));
    [result[index], result[swapIndex]] = [result[swapIndex], result[index]];
  }
  return result;
}

function plannedMemoryValues(contract: GenerationContract): MemoryValue[] {
  return contract.memory.map((memory) => ({
    kind: "state_value",
    id: memory.name,
    label: memory.name.replace(/_/g, " "),
    datatype: memory.datatype,
    source: { kind: "description_inference", requirement: memory.requirement },
    enabled: true,
    preferredRenderer: "json",
    treatAsList: memory.datatype === "list",
    allowRedefinition: true,
    applicability: ["workflow", "steps"],
  }));
}

function modeMap(names: string[]) {
  return Object.fromEntries(names.map((name) => [name, "scroll" as AccordionDisplayMode]));
}

function GenerationOrderItem({ entry, ordinal, index, siblingCount, parentGroupId, selectedGroupId, busy, prompts, models, onSelectGroup, onRunGroup, onShuffleGroup, onCopyGroup, onClearGroup, onAdd, onPeers, onUpdates, onPrompt, onModel, onRotate, onRemove }: {
  entry: GenerationOrderEntry;
  ordinal: string;
  index: number;
  siblingCount: number;
  parentGroupId?: string;
  selectedGroupId: string | null;
  busy: boolean;
  prompts: PromptChoice[];
  models: ModelChoice[];
  onSelectGroup: (id: string) => void;
  onRunGroup: (entry: GenerationOrderEntry, ordinal: string) => void;
  onShuffleGroup: (id: string) => void;
  onCopyGroup: (id: string) => void;
  onClearGroup: (id: string) => void;
  onAdd: (name: GenerationOutputName) => void;
  onPeers: (id: string, visibleToPeers: boolean, parentGroupId?: string) => void;
  onUpdates: (id: string, visibleToUpdates: boolean, parentGroupId?: string) => void;
  onPrompt: (id: string, promptId: string, parentGroupId?: string) => void;
  onModel: (id: string, modelId: string, parentGroupId?: string) => void;
  onRotate: (id: string, direction: -1 | 1, parentGroupId?: string) => void;
  onRemove: (id: string, parentGroupId?: string) => void;
}) {
  const isGroup = entry.name === "group";
  const selected = isGroup && selectedGroupId === entry.id;
  return <li className={`generation-output-${entry.name} ${isGroup ? "generation-order-group" : ""} ${selected ? "selected" : ""}`}>
    <b>{ordinal}</b>
    <button type="button" className="english-workflow-output-title" aria-label={isGroup ? `Run group ${ordinal}` : `Add another ${entry.name}`} title={isGroup ? "Run only this group as one LLM call" : "Append another occurrence to the selected group or top level"} disabled={busy} onClick={() => isGroup ? onRunGroup(entry, ordinal) : onAdd(entry.name)}>{isGroup ? "[group]" : entry.name}</button>
    <span className="generation-order-flags">
      <span>visible</span>
      <label title="Let later stages of other output types see this value."><input type="checkbox" aria-label={`Share ${entry.name} with peers at position ${ordinal}`} checked={entry.visibleToPeers} disabled={busy} onChange={(event) => onPeers(entry.id, event.target.checked, parentGroupId)} /><span>peers</span></label>
      <label title="Let a later occurrence of this output type see and revise this old value."><input type="checkbox" aria-label={`Share ${entry.name} with updates at position ${ordinal}`} checked={entry.visibleToUpdates} disabled={busy} onChange={(event) => onUpdates(entry.id, event.target.checked, parentGroupId)} /><span>updates</span></label>
    </span>
    <select aria-label={`Prompt at position ${ordinal}`} value={entry.promptId || ""} disabled={busy} onChange={(event) => onPrompt(entry.id, event.target.value, parentGroupId)}><option value="">Default prompt</option>{prompts.map((prompt) => <option key={prompt.id} value={prompt.id}>{prompt.label || prompt.id}</option>)}</select>
    <select aria-label={`Model override at position ${ordinal}`} value={entry.modelId || ""} disabled={busy} onChange={(event) => onModel(entry.id, event.target.value, parentGroupId)}><option value="">Inherited model</option>{models.filter((model) => model.enabled !== false).map((model) => <option key={model.id} value={model.id}>{model.label || model.id}</option>)}</select>
    <button type="button" aria-label={`Rotate ${entry.name} left at position ${ordinal}`} title={index === 0 ? "Wrap from the beginning to the end" : "Move one position left"} disabled={busy} onClick={() => onRotate(entry.id, -1, parentGroupId)}>←</button>
    <button type="button" aria-label={`Remove ${entry.name} at position ${ordinal}`} title="Remove this occurrence" disabled={busy} onClick={() => onRemove(entry.id, parentGroupId)}>×</button>
    <button type="button" aria-label={`Rotate ${entry.name} right at position ${ordinal}`} title={index === siblingCount - 1 ? "Wrap from the end to the beginning" : "Move one position right"} disabled={busy} onClick={() => onRotate(entry.id, 1, parentGroupId)}>→</button>
    {isGroup && <div className="generation-order-group-contents">{entry.steps?.length ? <ol>{entry.steps.map((child, childIndex) => <GenerationOrderItem key={child.id} entry={child} ordinal={`${ordinal}.${childIndex + 1}`} index={childIndex} siblingCount={entry.steps?.length || 0} parentGroupId={entry.id} selectedGroupId={selectedGroupId} busy={busy} prompts={prompts} models={models} onSelectGroup={onSelectGroup} onRunGroup={onRunGroup} onShuffleGroup={onShuffleGroup} onCopyGroup={onCopyGroup} onClearGroup={onClearGroup} onAdd={onAdd} onPeers={onPeers} onUpdates={onUpdates} onPrompt={onPrompt} onModel={onModel} onRotate={onRotate} onRemove={onRemove} />)}</ol> : <p>Empty simultaneous-generation group.</p>}<div className="generation-order-group-actions"><button type="button" className="generation-order-group-picker" aria-label={`Select group ${ordinal} for insertion`} aria-pressed={selected} disabled={busy} onClick={() => onSelectGroup(entry.id)}>{selected ? "SELECTED" : "SELECT"}</button><button type="button" className="generation-order-group-copy" aria-label={`Copy group ${ordinal}`} disabled={busy} onClick={() => onCopyGroup(entry.id)}>COPY</button><button type="button" className="generation-order-group-shuffle" aria-label={`Shuffle group ${ordinal}`} disabled={busy || (entry.steps?.length || 0) < 2} onClick={() => onShuffleGroup(entry.id)}>SHUFFLE</button><button type="button" className="generation-order-group-clear" aria-label={`Clear group ${ordinal}`} disabled={busy || !(entry.steps?.length)} onClick={() => onClearGroup(entry.id)}>CLEAR</button></div></div>}
  </li>;
}

export function EnglishWorkflowPage({
  workspaceId,
  workspaceLabel,
  workflow,
  workflowPath,
  description,
  savedDescription,
  onDescriptionChange,
  onSaveDescription,
  operation,
  operationCatalog,
  models,
  memoryValues,
  onGenerated,
  onApply,
  onOpenWorkflow,
}: Props) {
  const [phase, setPhase] = useState<GenerationPhase>("idle");
  const [selectedModel, setSelectedModel] = useState("");
  const [modelChoices, setModelChoices] = useState<ModelChoice[]>(models);
  const [promptChoices, setPromptChoices] = useState<PromptChoice[]>([]);
  const [datatypeCatalog, setDatatypeCatalog] = useState<DatatypeDocument[]>([]);
  const [workflowCatalog, setWorkflowCatalog] = useState<WorkflowDocument[]>([]);
  const [outputFormat, setOutputFormat] = useState(workflow.generation?.preferredFormat || "json");
  const [analysisContract, setAnalysisContract] = useState<GenerationContract | null>(null);
  const [generationOrder, setGenerationOrder] = useState<GenerationOrderEntry[]>(() => initialGenerationOrder());
  const [selectedGroupId, setSelectedGroupId] = useState<string | null>(null);
  const [contractTrials, setContractTrials] = useState<ContractTrial[]>([]);
  const [generationSteps, setGenerationSteps] = useState<GenerationStepEvent[]>([]);
  const [memoryPlanned, setMemoryPlanned] = useState(false);
  const [plannedValues, setPlannedValues] = useState<MemoryValue[]>([]);
  const [draft, setDraft] = useState<WorkflowDocument | null>(workflow.steps.length ? workflow : null);
  const [draftReadyToApply, setDraftReadyToApply] = useState(false);
  const [validationErrors, setValidationErrors] = useState<string[] | null>(null);
  const [busyAction, setBusyAction] = useState("");
  const [message, setMessage] = useState("");
  const [modes, setModes] = useState<Record<string, AccordionDisplayMode>>(() => modeMap([
    "specification", "generator", "trials", "summary", "memory", "checklist", "outputs", "rules",
  ]));
  const lineNumberRef = useRef<HTMLPreElement | null>(null);
  const generationOrderPath = workflow.generation?.generationOrderPath || "docs/WORKFLOW_GENERATION_ORDER.txt";
  const contractOperation = operationCatalog.find((candidate) => candidate.id === "workflow.analyze_generation_contract");
  const contract = analysisContract || {
    summary: "Analyze the English specification to produce the generation contract.",
    memory: [],
    checklist: [],
    outputs: [],
    rules: [],
    englishsteps: [],
    steps: [],
    libops: [],
    matchops: [],
    inventops: [],
    codeops: [],
    promptops: [],
    libdt: [],
    matchdt: [],
    inventdt: [],
    codedt: [],
    libwf: [],
    matchwf: [],
    inventwf: [],
    codewf: [],
  };
  const displayedValues = plannedValues.length ? plannedValues : memoryValues;
  const descriptionLines = Math.max(1, description.split(/\r?\n/).length);
  const setMode = (name: string, mode: AccordionDisplayMode) => setModes((current) => ({ ...current, [name]: mode }));
  const recordGenerationStep = (action: string, outputs: string[], detail: string) => setGenerationSteps((current) => [
    ...current,
    { id: `${Date.now()}:${current.length}`, action, outputs, detail },
  ]);
  const rotateGenerationEntry = (entryId: string, direction: -1 | 1, parentGroupId?: string) => setGenerationOrder((current) => {
    const rotate = (entries: GenerationOrderEntry[]) => {
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
  const shuffleGenerationGroup = (groupId: string) => {
    setSelectedGroupId(groupId);
    setGenerationOrder((current) => {
      const shuffle = (entries: GenerationOrderEntry[]): GenerationOrderEntry[] => entries.map((entry) => {
        if (entry.id === groupId && entry.name === "group") return { ...entry, steps: shuffledGenerationOrder(entry.steps || []) };
        return entry.steps?.length ? { ...entry, steps: shuffle(entry.steps) } : entry;
      });
      return shuffle(current);
    });
  };
  const copyGenerationGroup = (groupId: string) => {
    const sourceIndex = generationOrder.findIndex((entry) => entry.id === groupId && entry.name === "group");
    if (sourceIndex < 0) return;
    const copyRootId = `${Date.now()}:group-copy:${Math.random()}`;
    const clone = (entry: GenerationOrderEntry, path: string): GenerationOrderEntry => ({
      ...entry,
      id: path,
      ...(entry.steps ? { steps: entry.steps.map((child, index) => clone(child, `${path}:${index}:${Math.random()}`)) } : {}),
    });
    const copy = clone(generationOrder[sourceIndex], copyRootId);
    const next = [...generationOrder];
    next.splice(sourceIndex + 1, 0, copy);
    setGenerationOrder(next);
    setSelectedGroupId(copyRootId);
  };
  const clearGenerationGroup = (groupId: string) => {
    setSelectedGroupId(groupId);
    setGenerationOrder((current) => current.map((entry) => entry.id === groupId && entry.name === "group" ? { ...entry, steps: [] } : entry));
  };
  const removeGenerationEntry = (entryId: string, parentGroupId?: string) => {
    setGenerationOrder((current) => parentGroupId
      ? current.map((entry) => entry.id === parentGroupId ? { ...entry, steps: (entry.steps || []).filter((child) => child.id !== entryId) } : entry)
      : current.filter((entry) => entry.id !== entryId));
    if (entryId === selectedGroupId) setSelectedGroupId(null);
  };
  const updateGenerationEntry = (entryId: string, changes: Partial<GenerationOrderEntry>, parentGroupId?: string) => setGenerationOrder((current) => parentGroupId
    ? current.map((entry) => entry.id === parentGroupId ? { ...entry, steps: (entry.steps || []).map((child) => child.id === entryId ? { ...child, ...changes } : child) } : entry)
    : current.map((entry) => entry.id === entryId ? { ...entry, ...changes } : entry));
  const setGenerationEntryPeers = (entryId: string, visibleToPeers: boolean, parentGroupId?: string) => updateGenerationEntry(entryId, { visibleToPeers }, parentGroupId);
  const setGenerationEntryUpdates = (entryId: string, visibleToUpdates: boolean, parentGroupId?: string) => updateGenerationEntry(entryId, { visibleToUpdates }, parentGroupId);
  const setGenerationEntryPrompt = (entryId: string, promptId: string, parentGroupId?: string) => updateGenerationEntry(entryId, { promptId }, parentGroupId);
  const setGenerationEntryModel = (entryId: string, modelId: string, parentGroupId?: string) => updateGenerationEntry(entryId, { modelId }, parentGroupId);
  const addGenerationOutput = (name: GenerationOutputName) => {
    const id = `${Date.now()}:${Math.random()}`;
    setGenerationOrder((current) => {
      const entry: GenerationOrderEntry = { id, name, visibleToPeers: true, visibleToUpdates: false, promptId: DEFAULT_PROMPT_BY_OUTPUT[name], ...(name === "group" ? { steps: [] } : {}) };
      if (name !== "group" && selectedGroupId) {
        return current.map((candidate) => candidate.id === selectedGroupId ? { ...candidate, steps: [...(candidate.steps || []), entry] } : candidate);
      }
      return [...current, entry];
    });
    if (name === "group") setSelectedGroupId(id);
  };
  const includesOutput = (name: GenerationOutputName) => containsGenerationOutput(generationOrder, name) || containsGenerationOutput(generationOrder, "group");

  useEffect(() => {
    setModelChoices(models);
  }, [models]);

  useEffect(() => {
    let cancelled = false;
    void request(`/api/workspaces/${encodeURIComponent(workspaceId)}/prompts`)
      .then((payload) => {
        if (cancelled) return;
        const library = payload.promptLibrary && typeof payload.promptLibrary === "object" ? payload.promptLibrary as Record<string, unknown> : {};
        const hierarchy = library.hierarchy && typeof library.hierarchy === "object" ? library.hierarchy as Record<string, unknown> : {};
        const records = [payload.prompts, hierarchy.prompts, hierarchy.promptImplementations, hierarchy.promptProfiles]
          .flatMap((value) => Array.isArray(value) ? value : []);
        const choices = new Map<string, PromptChoice>();
        records.forEach((record) => {
          if (!record || typeof record !== "object" || Array.isArray(record)) return;
          const document = (record as Record<string, unknown>).document;
          if (!document || typeof document !== "object" || Array.isArray(document)) return;
          const prompt = document as PromptChoice;
          if (prompt.id && prompt.enabled !== false) choices.set(prompt.id, prompt);
        });
        setPromptChoices([...choices.values()].sort((left, right) => (left.label || left.id).localeCompare(right.label || right.id)));
      })
      .catch((reason) => { if (!cancelled) setMessage(reason instanceof Error ? reason.message : String(reason)); });
    return () => { cancelled = true; };
  }, [workspaceId]);

  useEffect(() => {
    let cancelled = false;
    void Promise.all([
      request(`/api/workspaces/${encodeURIComponent(workspaceId)}/datatypes`),
      request(`/api/workspaces/${encodeURIComponent(workspaceId)}/representations`),
      request(`/api/workspaces/${encodeURIComponent(workspaceId)}/concrete-datatypes`),
      request(`/api/workspaces/${encodeURIComponent(workspaceId)}/snapshot?scope=shell`),
    ]).then(([semantic, representations, concrete, snapshot]) => {
      if (cancelled) return;
      const records = [semantic.datatypes, representations.representations, concrete.concreteDatatypes]
        .flatMap((value) => Array.isArray(value) ? value : []);
      const choices = new Map<string, DatatypeDocument>();
      records.forEach((record) => {
        if (!record || typeof record !== "object" || Array.isArray(record)) return;
        const raw = record as Record<string, unknown>;
        const document = raw.document && typeof raw.document === "object" && !Array.isArray(raw.document)
          ? raw.document as DatatypeDocument
          : raw as DatatypeDocument;
        if (document.id) choices.set(`${document.kind || "datatype"}:${document.id}`, document);
      });
      setDatatypeCatalog([...choices.values()]);
      const workflows = Array.isArray(snapshot.workflows) ? snapshot.workflows.flatMap((record) => {
        if (!record || typeof record !== "object" || Array.isArray(record)) return [];
        const raw = record as Record<string, unknown>;
        const document = raw.document && typeof raw.document === "object" && !Array.isArray(raw.document)
          ? raw.document as WorkflowDocument
          : raw as WorkflowDocument;
        return document.id ? [document] : [];
      }) : [];
      setWorkflowCatalog(workflows);
    }).catch((reason) => { if (!cancelled) setMessage(reason instanceof Error ? reason.message : String(reason)); });
    return () => { cancelled = true; };
  }, [workspaceId]);

  useEffect(() => {
    let cancelled = false;
    setGenerationOrder(initialGenerationOrder());
    void request(`/api/workspaces/${encodeURIComponent(workspaceId)}/file?path=${encodeURIComponent(generationOrderPath)}`)
      .then((payload) => {
        if (cancelled) return;
        const file = payload.file && typeof payload.file === "object" ? payload.file as Record<string, unknown> : {};
        const document = JSON.parse(String(file.content || "{}")) as Record<string, unknown>;
        const restored = savedGenerationOrder(document.generationSteps);
        if (restored) setGenerationOrder(restored);
      })
      .catch(() => undefined);
    return () => { cancelled = true; };
  }, [workspaceId, workflow.id, generationOrderPath]);

  useEffect(() => {
    setAnalysisContract(null);
    setMemoryPlanned(false);
    setPlannedValues([]);
    setValidationErrors(null);
    setGenerationSteps([]);
    setDraftReadyToApply(false);
    setPhase("idle");
  }, [description]);

  useEffect(() => {
    let cancelled = false;
    void request(`/api/workspaces/${encodeURIComponent(workspaceId)}/model-selection`)
      .then((payload) => {
        if (cancelled) return;
        const available = Array.isArray(payload.models) ? payload.models as ModelChoice[] : models;
        const document = payload.document && typeof payload.document === "object" ? payload.document as Record<string, unknown> : {};
        const effective = payload.effective && typeof payload.effective === "object" ? payload.effective as { models?: unknown[] } : {};
        setModelChoices(available);
        setSelectedModel(String(document.overrideModelId || effective.models?.[0] || available[0]?.id || ""));
      })
      .catch((reason) => { if (!cancelled) setMessage(reason instanceof Error ? reason.message : String(reason)); });
    return () => { cancelled = true; };
  }, [workspaceId]);

  const changeModel = async (modelId: string) => {
    setSelectedModel(modelId);
    setBusyAction("model");
    setMessage("");
    try {
      await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/model-selection`, {
        method: "PUT",
        body: JSON.stringify({ overrideModelId: modelId }),
      });
      setMessage(modelId ? "Workspace generation model saved." : "Workspace model override cleared.");
    } catch (reason) {
      setMessage(reason instanceof Error ? reason.message : String(reason));
    } finally {
      setBusyAction("");
    }
  };

  const analyze = async (entries: GenerationOrderEntry[] = generationOrder, runLabel = "Analyze Specification", modelOverride = "") => {
    if (!contractOperation) {
      setPhase("error");
      setMessage("The workflow.analyze_generation_contract Operation is not available in this workspace.");
      return;
    }
    const groupRun = entries.length === 1 && entries[0].name === "group";
    const invocationModel = modelOverride || selectedModel;
    setBusyAction(groupRun ? `group:${entries[0].id}` : "analyze");
    setMessage("");
    try {
      const requestedSteps = generationRequest(entries);
      const payload = await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/operations/${encodeURIComponent(contractOperation.id)}/invoke`, {
        method: "POST",
        body: JSON.stringify({
          ...(invocationModel ? { modelSelection: { models: [invocationModel], strategy: "single" } } : {}),
          inputs: {
            english_specification: description,
            generation_steps: requestedSteps,
            existing_generation_contract: analysisContract || {},
            existing_workflow: draft || workflow,
            existing_memory_values_plan: { values: memoryValues },
            effective_operation_catalog: operationCatalog,
            effective_datatype_catalog: datatypeCatalog,
            effective_workflow_catalog: workflowCatalog,
            effective_prompt_catalog: promptChoices,
            workflow_schema: {
              kind: "workflow",
              required: ["id", "steps"],
              stepRequired: ["id", "label", "kind", "operation", "dependsOn", "inputs", "outputs"],
            },
          },
          parameters: {},
        }),
      });
      const outputs = payload.outputs && typeof payload.outputs === "object" ? payload.outputs as Record<string, unknown> : {};
      const rawContract = outputs.generation_contract;
      const nextContract = parseContract(rawContract);
      const candidate = outputs.workflow && typeof outputs.workflow === "object" && !Array.isArray(outputs.workflow) && Array.isArray((outputs.workflow as { steps?: unknown }).steps)
        ? outputs.workflow as WorkflowDocument
        : null;
      let candidateErrors = ["Candidate Workflow missing from the one-call response."];
      if (candidate) {
        const validationPayload = await request("/api/engine/workflows/validate", {
          method: "POST",
          body: JSON.stringify(candidate),
        });
        candidateErrors = Array.isArray(validationPayload.errors) ? validationPayload.errors.map(String) : [];
        setDraft(candidate);
      }
      const candidateValidationIssues = candidateErrors.length;
      const returnedOrder = rawContract && typeof rawContract === "object" && !Array.isArray(rawContract)
        ? Object.keys(rawContract).filter((name): name is GenerationOutputName => CONTRACT_SECTIONS.includes(name as GenerationOutputName))
        : [];
      const orderUsed = Array.isArray(outputs.order_used)
        ? outputs.order_used.map(String).filter((name): name is GenerationOutputName => GENERATION_OUTPUTS.includes(name as GenerationOutputName))
        : returnedOrder;
      const score = contractScore(nextContract, candidate, candidateValidationIssues);
      const trial: ContractTrial = {
        id: `${Date.now()}`,
        requestedOrder: requestedSteps.map((entry) => entry.name),
        returnedOrder: orderUsed.length ? orderUsed : returnedOrder,
        requestedSteps,
        score,
        checklistCount: nextContract.checklist.length,
        memoryCount: nextContract.memory.length,
        workflowSteps: candidate?.steps.length || 0,
        validationIssues: candidateValidationIssues,
        libraryOpsCount: nextContract.libops.length,
        matchOpsCount: nextContract.matchops.length,
        inventedOpsCount: nextContract.inventops.length,
        codedOpsCount: nextContract.codeops.length,
        promptedOpsCount: nextContract.promptops.length,
        libraryDtCount: nextContract.libdt.length,
        matchDtCount: nextContract.matchdt.length,
        inventedDtCount: nextContract.inventdt.length,
        codedDtCount: nextContract.codedt.length,
        libraryWfCount: nextContract.libwf.length,
        matchWfCount: nextContract.matchwf.length,
        inventedWfCount: nextContract.inventwf.length,
        codedWfCount: nextContract.codewf.length,
        englishStepCount: nextContract.englishsteps.length,
        formalStepCount: nextContract.steps.length,
        modelId: invocationModel || "resolved policy model",
      };
      setAnalysisContract(nextContract);
      setContractTrials((current) => [trial, ...current].slice(0, 12));
      setMemoryPlanned(false);
      setPlannedValues([]);
      setDraftReadyToApply(false);
      setPhase("analyzed");
      setValidationErrors(candidateErrors);
      recordGenerationStep(runLabel, [
        ...requestedSteps.map(({ name }) => name === "group" ? "Complete Contract + Workflow Group" : name === "summary" ? "Task Summary" : name === "memory" ? `${nextContract.memory.length} Memory Candidates` : name === "checklist" ? `${nextContract.checklist.length} Acceptance Checks` : name === "outputs" ? `${nextContract.outputs.length} Output Requirements` : name === "rules" ? `${nextContract.rules.length} Validation Rules` : name === "englishsteps" ? `${nextContract.englishsteps.length} English Steps` : name === "steps" ? `${nextContract.steps.length} Formal Steps` : name === "libops" ? `${nextContract.libops.length} Library Operations` : name === "matchops" ? `${nextContract.matchops.length} Operation Matches` : name === "inventops" ? `${nextContract.inventops.length} Invented Operation Proposals` : name === "codeops" ? `${nextContract.codeops.length} Operation Implementation Proposals` : name === "promptops" ? `${nextContract.promptops.length} Operation Prompt Proposals` : name === "libdt" ? `${nextContract.libdt.length} Library Datatypes` : name === "matchdt" ? `${nextContract.matchdt.length} Datatype Matches` : name === "inventdt" ? `${nextContract.inventdt.length} Invented Datatype Proposals` : name === "codedt" ? `${nextContract.codedt.length} Datatype Representation Proposals` : name === "libwf" ? `${nextContract.libwf.length} Library Workflows` : name === "matchwf" ? `${nextContract.matchwf.length} Workflow Matches` : name === "inventwf" ? `${nextContract.inventwf.length} Invented Workflow Proposals` : name === "codewf" ? `${nextContract.codewf.length} Workflow Build Reports` : candidate ? `${candidate.steps.length} Workflow Steps` : "Workflow Candidate Missing"),
      ], `${invocationModel || "resolved policy model"} · ${requestedSteps.map((entry) => entry.name).join(" → ")} · saved to ${generationOrderPath}`);
      await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/file`, {
        method: "PUT",
        body: JSON.stringify({
          path: generationOrderPath,
          content: JSON.stringify({
            workflowId: workflow.id,
            analyzedAt: new Date().toISOString(),
            modelId: trial.modelId,
            generationSteps: generationRequest(generationOrder),
            lastRunSteps: requestedSteps,
            orderUsed: trial.returnedOrder,
            generationContract: nextContract,
            workflow: candidate,
            validationErrors: candidateErrors,
            score,
          }, null, 2),
        }),
      });
      setMessage(`${groupRun ? `${runLabel} used` : "One LLM call followed"} ${requestedSteps.length} ordered ${requestedSteps.length === 1 ? "step" : "steps"} and saved the full composer to ${generationOrderPath}; contract score ${score}/100.`);
    } catch (reason) {
      setPhase("error");
      setMessage(reason instanceof Error ? reason.message : String(reason));
    } finally {
      setBusyAction("");
    }
  };

  const plan = () => {
    if (!analysisContract) return;
    const nextContract = analysisContract;
    const values = plannedMemoryValues(nextContract);
    const memoryChecks = values.map((value) => `Declare ${value.id} as ${value.datatype || "Any"} workflow memory before execution.`);
    setAnalysisContract({
      ...nextContract,
      checklist: [...nextContract.checklist, ...memoryChecks.filter((check) => !nextContract.checklist.includes(check))],
    });
    setPlannedValues(values);
    setMemoryPlanned(true);
    setDraftReadyToApply(false);
    setPhase("planned");
    setValidationErrors(null);
    recordGenerationStep("Plan Memory & Values", [
      `${values.length} Runtime Values`,
      `${memoryChecks.length} Memory Acceptance Checks`,
    ], "Expanded the analyzed contract without invoking workflow generation.");
    setMessage(`Planned ${values.length} description-backed memory values.`);
  };

  const generate = async () => {
    if (!operation) {
      setPhase("error");
      setMessage("The workflow.populate_from_english Operation is not available in this workspace.");
      return;
    }
    setBusyAction("generate");
    setMessage("");
    setValidationErrors(null);
    setDraftReadyToApply(false);
    try {
      const requiredCategories = workflow.generation?.operationCategories || [];
      const effectiveCatalog = operationCatalog.filter((candidate) =>
        !requiredCategories.length || requiredCategories.some((required) =>
          (candidate.categories || []).some((category) => category === required || category.startsWith(`${required}/`)),
        ),
      );
      const payload = await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/operations/${encodeURIComponent(operation.id)}/invoke`, {
        method: "POST",
        body: JSON.stringify({
          ...(selectedModel ? { modelSelection: { models: [selectedModel], strategy: "single" } } : {}),
          inputs: {
            english_specification: description,
            effective_operation_catalog: effectiveCatalog,
            workflow_schema: {
              kind: "workflow",
              required: ["id", "steps"],
              stepRequired: ["id", "label", "kind", "operation", "dependsOn", "inputs", "outputs"],
              stepOptional: ["parameters", "when", "while", "foreach", "branch", "maxIterations", "metadata"],
            },
            memory_values_plan: { values: plannedValues.length ? plannedValues : memoryValues },
            existing_workflow: workflow,
            validation_errors: validationErrors || [],
            output_format: outputFormat,
          },
          parameters: {},
        }),
      });
      const outputs = payload.outputs && typeof payload.outputs === "object" ? payload.outputs as Record<string, unknown> : {};
      const generatedWorkflow = outputs.workflow && typeof outputs.workflow === "object" && !Array.isArray(outputs.workflow)
        ? outputs.workflow as WorkflowDocument
        : null;
      if (!generatedWorkflow || !Array.isArray(generatedWorkflow.steps)) {
        throw new Error("The authoring Operation did not return outputs.workflow.steps.");
      }
      const returnedPlan = outputs.new_memory_values_plan && typeof outputs.new_memory_values_plan === "object"
        ? outputs.new_memory_values_plan as { values?: unknown[] }
        : null;
      if (!Array.isArray(returnedPlan?.values)) {
        throw new Error("The authoring Operation did not return new_memory_values_plan.values.");
      }
      const knownOperationIds = new Set(effectiveCatalog.map((candidate) => candidate.id));
      const normalizedWorkflow = {
        ...generatedWorkflow,
        steps: generatedWorkflow.steps.map((step) => {
          const operationId = String(step.operation || "");
          const withoutInventedNamespace = operationId.startsWith("workflow.") ? operationId.slice("workflow.".length) : operationId;
          return !knownOperationIds.has(operationId) && knownOperationIds.has(withoutInventedNamespace)
            ? { ...step, operation: withoutInventedNamespace }
            : step;
        }),
      };
      setDraft(normalizedWorkflow);
      setPlannedValues(returnedPlan.values.filter((value): value is MemoryValue => Boolean(value && typeof value === "object" && !Array.isArray(value) && (value as { id?: unknown }).id)));
      onGenerated({ ...outputs, workflow: normalizedWorkflow });
      setPhase("generated");
      recordGenerationStep("Generate Draft", [
        `${normalizedWorkflow.steps.length} Workflow Steps`,
        `${returnedPlan.values.length} Combined Memory Values`,
      ], `${selectedModel || "resolved policy model"} · ${outputFormat}`);
      setMessage(`Generated ${normalizedWorkflow.steps.length} workflow steps. Validating the returned draft…`);
      const validationPayload = await request("/api/engine/workflows/validate", {
        method: "POST",
        body: JSON.stringify(normalizedWorkflow),
      });
      const errors = Array.isArray(validationPayload.errors) ? validationPayload.errors.map(String) : [];
      setValidationErrors(errors);
      setDraftReadyToApply(errors.length === 0);
      setPhase(errors.length ? "generated" : "validated");
      recordGenerationStep("Validate Draft", [errors.length ? `${errors.length} Validation Issues` : "Backend Validation Passed"], "/api/engine/workflows/validate");
      setMessage(errors.length ? `Draft generated with ${errors.length} validation issues.` : "Draft generated and validated. Review it before applying.");
    } catch (reason) {
      setPhase("error");
      setMessage(reason instanceof Error ? reason.message : String(reason));
    } finally {
      setBusyAction("");
    }
  };

  const apply = async () => {
    setBusyAction("apply");
    setMessage("");
    try {
      await onApply();
      recordGenerationStep("Apply Validated Draft", ["Workflow Filesystem Resource Saved"], workflowPath);
      setMessage(`Applied the accepted draft to ${workflowPath}.`);
    } catch (reason) {
      setMessage(reason instanceof Error ? reason.message : String(reason));
    } finally {
      setBusyAction("");
    }
  };

  return (
    <section className="english-workflow-page" aria-label="English Workflow">
      <header className="english-workflow-titlebar">
        <div>
          <span>ENGLISH WORKFLOW</span>
          <h1>{workflow.label || workflow.id}</h1>
        </div>
        <div className="english-workflow-runtime-status">
          <span>Runtime: Local</span>
          <i />
          <b>{operation ? "Authoring Operation Ready" : "Authoring Operation Missing"}</b>
        </div>
      </header>

      <div className="english-workflow-columns">
        <ThreeStateAccordionStack id="english-workflow-left-stack" className="english-workflow-column" controlsLabel="ENGLISH SPECIFICATION STACK">
          <ThreeStateAccordionMember stackId="english-workflow-left-stack" label="ENGLISH SPECIFICATION" value={workflow.generation?.englishDescriptionPath || "No description resource"} mode={modes.specification} onChange={(mode) => setMode("specification", mode)} baseClass="english-workflow-panel english-workflow-specification" scrollSize="calc(100vh - 250px)" footer={<><b>Ln {descriptionLines}</b><span>{description === savedDescription ? "Saved" : "Unsaved changes"}</span></>}>
            <div className="english-workflow-editor-meta">
              <code>{workflow.generation?.englishDescriptionPath}</code>
              <button type="button" disabled={busyAction !== "" || description === savedDescription} onClick={() => void onSaveDescription()}>Save English</button>
            </div>
            <div className="english-workflow-editor">
              <pre ref={lineNumberRef} aria-hidden="true">{Array.from({ length: descriptionLines }, (_, index) => index + 1).join("\n")}</pre>
              <textarea aria-label="English workflow specification" value={description} onChange={(event) => onDescriptionChange(event.target.value)} onScroll={(event) => { if (lineNumberRef.current) lineNumberRef.current.scrollTop = event.currentTarget.scrollTop; }} spellCheck />
            </div>
          </ThreeStateAccordionMember>
        </ThreeStateAccordionStack>

        <ThreeStateAccordionStack id="english-workflow-center-stack" className="english-workflow-column" controlsLabel="GENERATE WORKFLOW STACK">
          <ThreeStateAccordionMember stackId="english-workflow-center-stack" label="GENERATE WORKFLOW" value={operation?.id || "Operation unavailable"} detail={`${operationCatalog.length} effective Operations`} mode={modes.generator} onChange={(mode) => setMode("generator", mode)} baseClass="english-workflow-panel english-workflow-generator" scrollSize="calc(100vh - 250px)" footer={<><b>{draft?.steps.length || 0} preview steps</b><span>{phase === "error" ? "Generation error" : phase}</span></>}>
            <div className="english-workflow-generation-controls">
              <label><span>SELECTED MODEL</span><select aria-label="English Workflow selected model" value={selectedModel} disabled={busyAction !== ""} onChange={(event) => void changeModel(event.target.value)}><option value="">Use system and Operation resolution</option>{modelChoices.filter((model) => model.enabled !== false).map((model) => <option key={model.id} value={model.id}>{model.label || model.id}{model.backendId ? ` · ${model.backendId}` : ""}</option>)}</select></label>
              <label><span>OUTPUT FORMAT</span><select aria-label="English Workflow output format" value={outputFormat} onChange={(event) => setOutputFormat(event.target.value)}><option value="json">Workflow JSON</option><option value="metta">MeTTa workflow resource</option></select></label>
              <fieldset className="english-workflow-contract-order">
                <legend>CONTRACT SECTION ORDER · ONE LLM CALL</legend>
                <div className="english-workflow-output-composer" aria-label="Add outputs to Generation Order">{CONTRACT_SECTION_ROWS.map((row, rowIndex) => <div key={row.id} className={`english-workflow-output-composer-row generation-${row.id}-buttons`} aria-label={`Add ${row.id} outputs`}>{row.names.map((name) => <button type="button" key={name} disabled={busyAction !== ""} onClick={() => addGenerationOutput(name)}>+ {name}</button>)}{rowIndex === 0 && <button type="button" className="english-workflow-group-output" disabled={busyAction !== ""} title="Create and select a simultaneous-generation group" onClick={() => addGenerationOutput("group")}>[+group]</button>}</div>)}</div>
                <ol>{generationOrder.map((entry, index) => <GenerationOrderItem key={entry.id} entry={entry} ordinal={`${index + 1}`} index={index} siblingCount={generationOrder.length} selectedGroupId={selectedGroupId} busy={busyAction !== ""} prompts={promptChoices} models={modelChoices} onSelectGroup={(id) => setSelectedGroupId((current) => current === id ? null : id)} onRunGroup={(group, ordinal) => void analyze([group], `Run Group ${ordinal}`, group.modelId || selectedModel)} onShuffleGroup={shuffleGenerationGroup} onCopyGroup={copyGenerationGroup} onClearGroup={clearGenerationGroup} onAdd={addGenerationOutput} onPeers={setGenerationEntryPeers} onUpdates={setGenerationEntryUpdates} onPrompt={setGenerationEntryPrompt} onModel={setGenerationEntryModel} onRotate={rotateGenerationEntry} onRemove={removeGenerationEntry} />)}</ol>
                <div className="english-workflow-order-actions"><button type="button" disabled={busyAction !== "" || generationOrder.length < 2} onClick={() => setGenerationOrder((current) => shuffledGenerationOrder(current))}>Shuffle order</button><button type="button" disabled={busyAction !== "" || generationOrder.length === 0} onClick={() => { setGenerationOrder([]); setSelectedGroupId(null); }}>Clear order</button></div>
                <small>Analyze follows the full sequence. A row title [group] runs only that group. Prompt and Model Override routing is saved with every occurrence in <code>{generationOrderPath}</code>.</small>
              </fieldset>
              <button type="button" disabled={busyAction !== "" || !description.trim() || !contractOperation || !hasGenerativeStep(generationOrder)} onClick={() => void analyze()}>{busyAction === "analyze" ? "Analyzing and saving…" : "⌕ Analyze & Save"}</button>
              <button type="button" disabled={busyAction !== "" || !analysisContract} onClick={plan}>▦ Plan Memory &amp; Values</button>
              <button type="button" className="primary" disabled={busyAction !== "" || !operation || !description.trim() || !analysisContract || !memoryPlanned} onClick={() => void generate()}>{busyAction === "generate" ? "Generating…" : "✦ Generate Draft"}</button>
            </div>
            <section className="english-workflow-progress" aria-label="Generation Order">
              <span>GENERATION ORDER · BUTTON PRESS HISTORY</span>
              {generationSteps.length ? <ol>{generationSteps.map((step, index) => <li className="complete" key={step.id}><i>{index + 1}</i><div><b>{step.action}</b><span>{step.outputs.join(" · ")}</span><small>{step.detail}</small></div></li>)}</ol> : <p>No generation buttons pressed yet. This list records the actual order and outputs.</p>}
            </section>
            <section className="english-workflow-preview">
              <header><span>PREVIEW: {draft?.steps.length || 0} STEPS</span><button type="button" onClick={onOpenWorkflow}>Open Workflow Editor</button></header>
              {!includesOutput("workflow") ? <p>Add Workflow or a complete group to Generation Order to display the candidate.</p> : draft?.steps.length ? <ol>{draft.steps.map((step, index) => <li key={step.id}><span>{index + 1}</span><div><b>{step.label || step.id}</b><code>{step.operation || "unresolved Operation"}</code></div></li>)}</ol> : <p>No steps generated yet.</p>}
            </section>
            <div className="english-workflow-apply"><button type="button" disabled={busyAction !== "" || !draftReadyToApply || !draft?.steps.length || Boolean(validationErrors?.length)} onClick={() => void apply()}>{busyAction === "apply" ? "Applying…" : "Apply Validated Draft"}</button><small>Experimental contract trials never enable Apply. Only a successfully validated Generate Draft result can be written.</small></div>
            {message && <div className={phase === "error" ? "english-workflow-message error" : "english-workflow-message"}>{message}</div>}
          </ThreeStateAccordionMember>
        </ThreeStateAccordionStack>

        <ThreeStateAccordionStack id="english-workflow-right-stack" className="english-workflow-column english-workflow-contract" controlsLabel="GENERATION CONTRACT STACK">
          <ThreeStateAccordionMember stackId="english-workflow-right-stack" initialIndex={0} label="ORDER TRIALS" value={contractTrials.length ? `${contractTrials.length} one-call trials` : "No trials yet"} detail="Compare contract and Workflow quality across generation orders" mode={modes.trials} onChange={(mode) => setMode("trials", mode)} baseClass="english-workflow-contract-panel" scrollSize="210px">{contractTrials.length ? <ol className="english-workflow-trials">{contractTrials.map((trial) => <li key={trial.id}><b>{trial.score}/100</b><span>{trial.requestedOrder.join(" → ")}</span><small>{trial.requestedSteps.map(generationStepSummary).join(" · ")} · {trial.checklistCount} checks · {trial.memoryCount} memory · {trial.englishStepCount} English steps · {trial.formalStepCount} formal steps · {trial.libraryOpsCount} library operations · {trial.matchOpsCount} operation matches · {trial.inventedOpsCount} invented operation proposals · {trial.codedOpsCount} implementation proposals · {trial.promptedOpsCount} operation prompt proposals · {trial.libraryDtCount} library datatypes · {trial.matchDtCount} datatype matches · {trial.inventedDtCount} invented datatype proposals · {trial.codedDtCount} datatype representation proposals · {trial.libraryWfCount} library workflows · {trial.matchWfCount} workflow matches · {trial.inventedWfCount} invented workflow proposals · {trial.codedWfCount} workflow build reports · {trial.workflowSteps} workflow steps · {trial.validationIssues} validation issues · {trial.modelId}{trial.returnedOrder.join("|") !== trial.requestedOrder.join("|") ? ` · returned ${trial.returnedOrder.join(" → ")}` : " · order honored"}</small></li>)}</ol> : <p>Click output titles to compose Generation Order. Names may repeat, visibility controls choose whether current values are exposed to peers or future updates, and [+group] creates and selects a simultaneous output group.</p>}</ThreeStateAccordionMember>
          {includesOutput("summary") && <ThreeStateAccordionMember stackId="english-workflow-right-stack" initialIndex={1} label="TASK SUMMARY" value={analysisContract ? "Generated by Analyze" : "Waiting for analysis"} mode={modes.summary} onChange={(mode) => setMode("summary", mode)} baseClass="english-workflow-contract-panel" scrollSize="150px"><p>{contract.summary}</p></ThreeStateAccordionMember>}
          {includesOutput("memory") && <ThreeStateAccordionMember stackId="english-workflow-right-stack" initialIndex={2} label="REQUIRED MEMORY" value={memoryPlanned ? `${displayedValues.length} planned values` : analysisContract ? `${contract.memory.length} analyzed candidates` : "Waiting for analysis"} mode={modes.memory} onChange={(mode) => setMode("memory", mode)} baseClass="english-workflow-contract-panel" scrollSize="190px">{memoryPlanned ? <ul>{displayedValues.map((value) => <li key={value.id}><code>{value.label || value.id}</code><span>{value.datatype || "Any"}</span></li>)}</ul> : analysisContract ? <ul>{contract.memory.map((value) => <li key={value.name}><code>{value.name}</code><span>{value.datatype}</span></li>)}</ul> : <p>Analyze generates candidate memory in the one-call contract. Plan Memory &amp; Values then turns those candidates into explicit runtime values.</p>}</ThreeStateAccordionMember>}
          {includesOutput("checklist") && <ThreeStateAccordionMember stackId="english-workflow-right-stack" initialIndex={3} label="ACCEPTANCE CHECKLIST" value={analysisContract ? `${contract.checklist.length} generated checks` : "Waiting for analysis"} mode={modes.checklist} onChange={(mode) => setMode("checklist", mode)} baseClass="english-workflow-contract-panel" scrollSize="260px"><ul className="english-workflow-checklist">{contract.checklist.map((item, index) => <li key={`${index}:${item}`}><input type="checkbox" checked={phase === "validated"} readOnly /><span>{item}</span></li>)}</ul>{validationErrors && <div className={validationErrors.length ? "contract-validation bad" : "contract-validation good"}>{validationErrors.length ? validationErrors.join("\n") : "Backend workflow validation passed."}</div>}</ThreeStateAccordionMember>}
          {includesOutput("outputs") && <ThreeStateAccordionMember stackId="english-workflow-right-stack" initialIndex={4} label="OUTPUT REQUIREMENTS" value={analysisContract ? `${contract.outputs.length} generated requirements` : "Waiting for analysis"} mode={modes.outputs} onChange={(mode) => setMode("outputs", mode)} baseClass="english-workflow-contract-panel" scrollSize="170px"><ul>{contract.outputs.map((item, index) => <li key={`${index}:${item}`}>{item}</li>)}</ul></ThreeStateAccordionMember>}
          {includesOutput("rules") && <ThreeStateAccordionMember stackId="english-workflow-right-stack" initialIndex={5} label="VALIDATION RULES" value={analysisContract ? `${contract.rules.length} generated rules` : "Waiting for analysis"} mode={modes.rules} onChange={(mode) => setMode("rules", mode)} baseClass="english-workflow-contract-panel" scrollSize="170px"><ul>{contract.rules.map((item, index) => <li key={`${index}:${item}`}>{item}</li>)}</ul></ThreeStateAccordionMember>}
        </ThreeStateAccordionStack>
      </div>

      <footer className="english-workflow-statusbar"><span><i /> Workspace: {workspaceLabel}</span><span>Mode: Build</span><span>Workflow: {workflowPath}</span><span>AtomSpace: default</span></footer>
    </section>
  );
}
