import { useEffect, useState, type ReactNode } from "react";
import {
  WorkflowPageHost,
  type WorkflowPageComponentRegistry,
  type WorkflowPageDefinition,
  type WorkflowPageMemberDefinition,
  type WorkflowPageMemberSurface,
} from "./WorkflowPageHost";
import { LoadTextDocuments } from "./LoadTextDocuments";
import { ResourceSourceEditor } from "./ResourceSourceEditor";
import { WorkflowPageSourceEditor } from "./WorkflowPageSourceEditor";
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
  backendLabel?: string;
  enabled?: boolean;
};

const modelOptionLabel = (model: ModelChoice) =>
  `${model.backendLabel || model.backendId || model.id} · ${model.label || model.id}`;

type PromptChoice = {
  id: string;
  label?: string;
  description?: string;
  kind?: string;
  text?: string | string[];
  enabled?: boolean;
  applicability?: string[];
  buttonName?: string;
  classificationId?: string;
  produces?: string[];
  path?: string;
  source?: string;
  workspaceId?: string;
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
  pageDefinition?: WorkflowPageDefinition;
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
  onOpenPrompts: () => void;
  onPageDefinitionSaved: () => Promise<unknown> | unknown;
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
const GENERATION_OUTPUTS: GenerationOutputName[] = [...CONTRACT_SECTIONS, "group"];
const CONTRACT_SECTION_APPLICABILITY = "english_to_workbench.contract_section";
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

type ContractSectionPrompt = PromptChoice & { buttonName: GenerationOutputName };

function reversedName(value: string) {
  return [...value].reverse().join("");
}

function contractSectionPrompts(
  prompts: PromptChoice[],
  applicability = CONTRACT_SECTION_APPLICABILITY,
): ContractSectionPrompt[] {
  return prompts.flatMap((prompt): ContractSectionPrompt[] => {
    const buttonName = String(prompt.buttonName || "").trim() as GenerationOutputName;
    const applicable = Array.isArray(prompt.applicability)
      && prompt.applicability.includes(applicability);
    if (!applicable || buttonName === "group" || !CONTRACT_SECTIONS.includes(buttonName)) return [];
    return [{ ...prompt, buttonName }];
  }).sort((left, right) => {
    const leftClassification = String(left.classificationId || "\uffff");
    const rightClassification = String(right.classificationId || "\uffff");
    return leftClassification.localeCompare(rightClassification)
      || reversedName(left.buttonName).localeCompare(reversedName(right.buttonName))
      || left.buttonName.localeCompare(right.buttonName)
      || left.id.localeCompare(right.id);
  });
}

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

function GenerationOrderItem({ entry, ordinal, index, siblingCount, parentGroupId, selectedGroupId, busy, prompts, models, onSelectGroup, onRunEntry, onShuffleGroup, onCopyGroup, onClearGroup, onPeers, onUpdates, onPrompt, onModel, onRotate, onRemove }: {
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
  onRunEntry: (entry: GenerationOrderEntry, ordinal: string) => void;
  onShuffleGroup: (id: string) => void;
  onCopyGroup: (id: string) => void;
  onClearGroup: (id: string) => void;
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
    <button type="button" className="english-workflow-output-title" aria-label={isGroup ? `Run group ${ordinal}` : `Quick call ${entry.name} at position ${ordinal}`} title={isGroup ? "Run only this group as one LLM call" : "Run only this generation step as one quick LLM call"} disabled={busy} onClick={() => onRunEntry(entry, ordinal)}>{isGroup ? "[group]" : entry.name}</button>
    <span className="generation-order-flags">
      <span>visible</span>
      <label title="Let later stages of other output types see this value."><input type="checkbox" aria-label={`Share ${entry.name} with peers at position ${ordinal}`} checked={entry.visibleToPeers} disabled={busy} onChange={(event) => onPeers(entry.id, event.target.checked, parentGroupId)} /><span>peers</span></label>
      <label title="Let a later occurrence of this output type see and revise this old value."><input type="checkbox" aria-label={`Share ${entry.name} with updates at position ${ordinal}`} checked={entry.visibleToUpdates} disabled={busy} onChange={(event) => onUpdates(entry.id, event.target.checked, parentGroupId)} /><span>updates</span></label>
    </span>
    <select aria-label={`Prompt at position ${ordinal}`} value={entry.promptId || ""} disabled={busy} onChange={(event) => onPrompt(entry.id, event.target.value, parentGroupId)}><option value="">Default prompt</option>{prompts.map((prompt) => <option key={prompt.id} value={prompt.id}>{prompt.label || prompt.id}</option>)}</select>
    <select aria-label={`Model override at position ${ordinal}`} value={entry.modelId || ""} disabled={busy} onChange={(event) => onModel(entry.id, event.target.value, parentGroupId)}><option value="">Inherited model</option>{models.filter((model) => model.enabled !== false).map((model) => <option key={model.id} value={model.id}>{modelOptionLabel(model)}</option>)}</select>
    <button type="button" aria-label={`Rotate ${entry.name} left at position ${ordinal}`} title={index === 0 ? "Wrap from the beginning to the end" : "Move one position left"} disabled={busy} onClick={() => onRotate(entry.id, -1, parentGroupId)}>←</button>
    <button type="button" aria-label={`Remove ${entry.name} at position ${ordinal}`} title="Remove this occurrence" disabled={busy} onClick={() => onRemove(entry.id, parentGroupId)}>×</button>
    <button type="button" aria-label={`Rotate ${entry.name} right at position ${ordinal}`} title={index === siblingCount - 1 ? "Wrap from the end to the beginning" : "Move one position right"} disabled={busy} onClick={() => onRotate(entry.id, 1, parentGroupId)}>→</button>
    {isGroup && <div className="generation-order-group-contents">{entry.steps?.length ? <ol>{entry.steps.map((child, childIndex) => <GenerationOrderItem key={child.id} entry={child} ordinal={`${ordinal}.${childIndex + 1}`} index={childIndex} siblingCount={entry.steps?.length || 0} parentGroupId={entry.id} selectedGroupId={selectedGroupId} busy={busy} prompts={prompts} models={models} onSelectGroup={onSelectGroup} onRunEntry={onRunEntry} onShuffleGroup={onShuffleGroup} onCopyGroup={onCopyGroup} onClearGroup={onClearGroup} onPeers={onPeers} onUpdates={onUpdates} onPrompt={onPrompt} onModel={onModel} onRotate={onRotate} onRemove={onRemove} />)}</ol> : <p>Empty simultaneous-generation group.</p>}<div className="generation-order-group-actions"><button type="button" className="generation-order-group-picker" aria-label={`Select group ${ordinal} for insertion`} aria-pressed={selected} disabled={busy} onClick={() => onSelectGroup(entry.id)}>{selected ? "SELECTED" : "SELECT"}</button><button type="button" className="generation-order-group-copy" aria-label={`Copy group ${ordinal}`} disabled={busy} onClick={() => onCopyGroup(entry.id)}>COPY</button><button type="button" className="generation-order-group-shuffle" aria-label={`Shuffle group ${ordinal}`} disabled={busy || (entry.steps?.length || 0) < 2} onClick={() => onShuffleGroup(entry.id)}>SHUFFLE</button><button type="button" className="generation-order-group-clear" aria-label={`Clear group ${ordinal}`} disabled={busy || !(entry.steps?.length)} onClick={() => onClearGroup(entry.id)}>CLEAR</button></div></div>}
  </li>;
}

type WorkflowGenerationRuntimeProps = {
  member: WorkflowPageMemberDefinition;
  operation?: OperationDocument;
  operationCatalogCount: number;
  draftStepCount: number;
  phase: GenerationPhase;
  busyAction: string;
  message: string;
  description: string;
  selectedModel: string;
  models: ModelChoice[];
  outputFormat: string;
  prompts: PromptChoice[];
  applicablePrompts: ContractSectionPrompt[];
  generationOrder: GenerationOrderEntry[];
  selectedGroupId: string | null;
  generationOrderPath: string;
  hasContractOperation: boolean;
  hasAnalysisContract: boolean;
  memoryPlanned: boolean;
  onModelChange: (modelId: string) => void;
  onOutputFormatChange: (format: string) => void;
  onAddOutput: (name: GenerationOutputName, promptId?: string) => void;
  onSelectGroup: (groupId: string) => void;
  onRunEntry: (entry: GenerationOrderEntry, ordinal: string) => void;
  onShuffleGroup: (groupId: string) => void;
  onCopyGroup: (groupId: string) => void;
  onClearGroup: (groupId: string) => void;
  onPeers: (entryId: string, visible: boolean, parentGroupId?: string) => void;
  onUpdates: (entryId: string, visible: boolean, parentGroupId?: string) => void;
  onPrompt: (entryId: string, promptId: string, parentGroupId?: string) => void;
  onEntryModel: (entryId: string, modelId: string, parentGroupId?: string) => void;
  onRotate: (entryId: string, direction: -1 | 1, parentGroupId?: string) => void;
  onRemove: (entryId: string, parentGroupId?: string) => void;
  onShuffleOrder: () => void;
  onClearOrder: () => void;
  onAnalyze: () => void;
  onPlan: () => void;
  onGenerate: () => void;
};

export function WorkflowGenerationRuntime({
  member,
  operation,
  operationCatalogCount,
  draftStepCount,
  phase,
  busyAction,
  message,
  description,
  selectedModel,
  models,
  outputFormat,
  prompts,
  applicablePrompts,
  generationOrder,
  selectedGroupId,
  generationOrderPath,
  hasContractOperation,
  hasAnalysisContract,
  memoryPlanned,
  onModelChange,
  onOutputFormatChange,
  onAddOutput,
  onSelectGroup,
  onRunEntry,
  onShuffleGroup,
  onCopyGroup,
  onClearGroup,
  onPeers,
  onUpdates,
  onPrompt,
  onEntryModel,
  onRotate,
  onRemove,
  onShuffleOrder,
  onClearOrder,
  onAnalyze,
  onPlan,
  onGenerate,
}: WorkflowGenerationRuntimeProps) {
  const outputFormats = Array.isArray(member.options?.outputFormats)
    ? member.options.outputFormats.map(String)
    : ["json", "metta"];
  const promptApplicability = String(member.options?.promptApplicability || CONTRACT_SECTION_APPLICABILITY);
  const busy = busyAction !== "";

  return <div className="english-workflow-generation-controls">
    <label><span>SELECTED MODEL</span><select aria-label="English Workflow selected model" value={selectedModel} disabled={busy} onChange={(event) => onModelChange(event.target.value)}><option value="">Use system and Operation resolution</option>{models.filter((model) => model.enabled !== false).map((model) => <option key={model.id} value={model.id}>{modelOptionLabel(model)}</option>)}</select></label>
    <label><span>OUTPUT FORMAT</span><select aria-label="English Workflow output format" value={outputFormat} onChange={(event) => onOutputFormatChange(event.target.value)}>{outputFormats.map((format) => <option key={format} value={format}>{format === "json" ? "Workflow JSON" : format === "metta" ? "MeTTa workflow resource" : format}</option>)}</select></label>
    <fieldset className="english-workflow-contract-order">
      <legend>CONTRACT SECTION ORDER · ONE LLM CALL</legend>
      <div className="english-workflow-output-composer" aria-label="Add outputs to Generation Order">
        <div className="english-workflow-output-composer-row" aria-label="Applicable Prompt resource outputs">
          {applicablePrompts.map((prompt) => <button type="button" key={prompt.id} disabled={busy} title={`${prompt.classificationId || "Unclassified"} · ${prompt.label || prompt.id}`} onClick={() => onAddOutput(prompt.buttonName, prompt.id)}>+ {prompt.buttonName}</button>)}
          {member.options?.allowGroups !== false && <button type="button" className="english-workflow-group-output" disabled={busy} title="Create and select a simultaneous-generation group" onClick={() => onAddOutput("group")}>[+group]</button>}
        </div>
        {!applicablePrompts.length && <small>No effective Prompt resources declare applicability <code>{promptApplicability}</code>.</small>}
      </div>
      <ol>{generationOrder.map((entry, index) => <GenerationOrderItem key={entry.id} entry={entry} ordinal={`${index + 1}`} index={index} siblingCount={generationOrder.length} selectedGroupId={selectedGroupId} busy={busy} prompts={prompts} models={models} onSelectGroup={onSelectGroup} onRunEntry={onRunEntry} onShuffleGroup={onShuffleGroup} onCopyGroup={onCopyGroup} onClearGroup={onClearGroup} onPeers={onPeers} onUpdates={onUpdates} onPrompt={onPrompt} onModel={onEntryModel} onRotate={onRotate} onRemove={onRemove} />)}</ol>
      <div className="english-workflow-order-actions"><button type="button" disabled={busy || generationOrder.length < 2} onClick={onShuffleOrder}>Shuffle order</button><button type="button" disabled={busy || generationOrder.length === 0} onClick={onClearOrder}>Clear order</button></div>
      <small>Analyze follows the full sequence. Any named row title runs that step as a quick call; [group] runs only that group. Prompt and Model Override routing is saved with every occurrence in <code>{generationOrderPath}</code>.</small>
    </fieldset>
    <button type="button" disabled={busy || !description.trim() || !hasContractOperation || !hasGenerativeStep(generationOrder)} onClick={onAnalyze}>{busyAction === "analyze" ? "Analyzing and saving…" : "⌕ Analyze & Save"}</button>
    <button type="button" disabled={busy || !hasAnalysisContract} onClick={onPlan}>▦ Plan Memory &amp; Values</button>
    <button type="button" className="primary" disabled={busy || !operation || !description.trim() || !hasAnalysisContract || !memoryPlanned} onClick={onGenerate}>{busyAction === "generate" ? "Generating…" : "✦ Generate Draft"}</button>
    {message && <div className={phase === "error" ? "english-workflow-message error" : "english-workflow-message"}>{message}</div>}
    <span className="sr-only">{operationCatalogCount} effective Operations; {draftStepCount} preview steps</span>
  </div>;
}

export function GenerateWorkflowPage({
  pageDefinition,
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
  onOpenPrompts,
  onPageDefinitionSaved,
}: Props) {
  const [phase, setPhase] = useState<GenerationPhase>("idle");
  const [selectedModel, setSelectedModel] = useState("");
  const [modelChoices, setModelChoices] = useState<ModelChoice[]>(models);
  const [promptChoices, setPromptChoices] = useState<PromptChoice[]>([]);
  const [selectedPromptId, setSelectedPromptId] = useState("");
  const [selectedPromptSource, setSelectedPromptSource] = useState("");
  const [selectedPromptSourceValid, setSelectedPromptSourceValid] = useState(true);
  const [savingPrompt, setSavingPrompt] = useState(false);
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
  const generationOrderPath = workflow.generation?.generationOrderPath || "docs/WORKFLOW_GENERATION_ORDER.txt";
  const contractOperation = operationCatalog.find((candidate) => candidate.id === "workflow.analyze_generation_contract");
  const availableContractSectionPrompts = contractSectionPrompts(promptChoices);
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
  const addGenerationOutput = (name: GenerationOutputName, promptId?: string) => {
    const id = `${Date.now()}:${Math.random()}`;
    setGenerationOrder((current) => {
      const entry: GenerationOrderEntry = { id, name, visibleToPeers: true, visibleToUpdates: false, promptId: promptId || DEFAULT_PROMPT_BY_OUTPUT[name], ...(name === "group" ? { steps: [] } : {}) };
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
          const raw = record as Record<string, unknown>;
          const prompt = {
            ...(document as PromptChoice),
            path: String(raw.path || ""),
            source: String(raw.source || ""),
            workspaceId: String(raw.workspaceId || workspaceId),
          };
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

  const validateDraft = async () => {
    if (!draft?.steps.length) return;
    setBusyAction("validate");
    setMessage("");
    try {
      const payload = await request("/api/engine/workflows/validate", {
        method: "POST",
        body: JSON.stringify(draft),
      });
      const errors = Array.isArray(payload.errors) ? payload.errors.map(String) : [];
      setValidationErrors(errors);
      setDraftReadyToApply(errors.length === 0);
      setPhase(errors.length ? "generated" : "validated");
      recordGenerationStep("Validate Draft", [
        errors.length ? `${errors.length} Validation Issues` : "Backend Validation Passed",
      ], "/api/engine/workflows/validate");
      setMessage(errors.length ? `Validation found ${errors.length} issues.` : "Backend workflow validation passed.");
    } catch (reason) {
      setPhase("error");
      setMessage(reason instanceof Error ? reason.message : String(reason));
    } finally {
      setBusyAction("");
    }
  };

  const workflowSteps = (candidate: WorkflowDocument | null, empty: ReactNode) =>
    candidate?.steps.length ? (
      <ol className="english-workflow-workflow-steps">
        {candidate.steps.map((step, index) => <li key={step.id}><span>{index + 1}</span><div><b>{step.label || step.id}</b><code>{step.operation || "unresolved Operation"}</code></div></li>)}
      </ol>
    ) : empty;

  const jsonDetail = (value: unknown) => (
    <pre className="english-workflow-resource-source">{JSON.stringify(value, null, 2)}</pre>
  );

  const explicitPromptId = generationOrder
    .flatMap((entry) => [entry, ...(entry.steps || [])])
    .map((entry) => entry.promptId)
    .find(Boolean);
  const selectedPrompt = promptChoices.find((prompt) => prompt.id === selectedPromptId)
    || promptChoices.find((prompt) => prompt.id === explicitPromptId)
    || availableContractSectionPrompts[0];
  const selectedModelRecord = modelChoices.find((model) => model.id === selectedModel);

  useEffect(() => {
    if (!selectedPrompt) return;
    setSelectedPromptId(selectedPrompt.id);
    setSelectedPromptSource(JSON.stringify(selectedPrompt, (key, value) =>
      ["path", "source", "workspaceId"].includes(key) ? undefined : value, 2));
    setSelectedPromptSourceValid(true);
  }, [selectedPrompt?.id]);

  const saveSelectedPrompt = async () => {
    if (!selectedPrompt?.path || !selectedPrompt.workspaceId || !selectedPromptSourceValid) return;
    setSavingPrompt(true);
    try {
      const document = JSON.parse(selectedPromptSource) as PromptChoice;
      const payload = await request(`/api/workspaces/${encodeURIComponent(selectedPrompt.workspaceId)}/prompts/${encodeURIComponent(selectedPrompt.id)}`, {
        method: "PUT",
        body: JSON.stringify({ path: selectedPrompt.path, document }),
      });
      const saved = payload.document as PromptChoice;
      setPromptChoices((current) => current.map((prompt) => prompt.id === selectedPrompt.id ? {
        ...saved,
        path: selectedPrompt.path,
        source: selectedPrompt.source,
        workspaceId: selectedPrompt.workspaceId,
      } : prompt));
      setMessage(`Saved Prompt ${selectedPrompt.id}.`);
    } catch (reason) {
      setMessage(reason instanceof Error ? reason.message : String(reason));
    } finally {
      setSavingPrompt(false);
    }
  };

  const composerSurface = (member: WorkflowPageMemberDefinition): WorkflowPageMemberSurface => ({
    value: operation?.id || "Operation unavailable",
    detail: `${operationCatalog.length} effective Operations`,
    baseClass: "english-workflow-panel english-workflow-generator",
    footer: <><b>{draft?.steps.length || 0} preview steps</b><span>{phase === "error" ? "Generation error" : phase}</span></>,
    content: <WorkflowGenerationRuntime
      member={member}
      operation={operation}
      operationCatalogCount={operationCatalog.length}
      draftStepCount={draft?.steps.length || 0}
      phase={phase}
      busyAction={busyAction}
      message={message}
      description={description}
      selectedModel={selectedModel}
      models={modelChoices}
      outputFormat={outputFormat}
      prompts={promptChoices}
      applicablePrompts={contractSectionPrompts(
        promptChoices,
        String(member.options?.promptApplicability || CONTRACT_SECTION_APPLICABILITY),
      )}
      generationOrder={generationOrder}
      selectedGroupId={selectedGroupId}
      generationOrderPath={generationOrderPath}
      hasContractOperation={Boolean(contractOperation)}
      hasAnalysisContract={Boolean(analysisContract)}
      memoryPlanned={memoryPlanned}
      onModelChange={(modelId) => void changeModel(modelId)}
      onOutputFormatChange={setOutputFormat}
      onAddOutput={(name, promptId) => { addGenerationOutput(name, promptId); if (promptId) setSelectedPromptId(promptId); }}
      onSelectGroup={(id) => setSelectedGroupId((current) => current === id ? null : id)}
      onRunEntry={(entry, ordinal) => void analyze([entry], entry.name === "group" ? `Run Group ${ordinal}` : `Quick Call ${entry.name} ${ordinal}`, entry.modelId || selectedModel)}
      onShuffleGroup={shuffleGenerationGroup}
      onCopyGroup={copyGenerationGroup}
      onClearGroup={clearGenerationGroup}
      onPeers={setGenerationEntryPeers}
      onUpdates={setGenerationEntryUpdates}
      onPrompt={(entryId, promptId, parentGroupId) => { setGenerationEntryPrompt(entryId, promptId, parentGroupId); setSelectedPromptId(promptId); }}
      onEntryModel={setGenerationEntryModel}
      onRotate={rotateGenerationEntry}
      onRemove={removeGenerationEntry}
      onShuffleOrder={() => setGenerationOrder((current) => shuffledGenerationOrder(current))}
      onClearOrder={() => { setGenerationOrder([]); setSelectedGroupId(null); }}
      onAnalyze={() => void analyze()}
      onPlan={plan}
      onGenerate={() => void generate()}
    />,
  });

  const contractSectionSurface = (member: WorkflowPageMemberDefinition): WorkflowPageMemberSurface => {
    const section = String(member.options?.section || member.mode || "summary") as "summary" | "outputs" | "rules";
    const values = section === "summary" ? [contract.summary] : contract[section];
    return {
      value: analysisContract ? `${values.length} generated ${section === "summary" ? "summary" : section}` : String(member.options?.emptyState || "Waiting for analysis"),
      baseClass: "english-workflow-contract-panel",
      scrollSize: "190px",
      content: section === "summary" ? <p>{contract.summary}</p> : <ul>{values.map((item, index) => <li key={`${index}:${item}`}>{item}</li>)}</ul>,
    };
  };

  const registry: WorkflowPageComponentRegistry = {
    LoadTextDocuments: () => ({
      value: workflow.generation?.englishDescriptionPath || "No description resource",
      baseClass: "english-workflow-panel english-workflow-specification",
      content: <LoadTextDocuments workspaceId={workspaceId} defaultFilter=".md|.txt" preferredPath={workflow.generation?.englishDescriptionPath || ""} preferredContent={description} savedPreferredContent={savedDescription} disabled={busyAction !== ""} onPreferredContentChange={onDescriptionChange} onSavePreferredContent={onSaveDescription} onActiveDocumentChange={(content, path) => { if (path === workflow.generation?.englishDescriptionPath) onDescriptionChange(content); }} />,
    }),
    WorkflowResourceEditor: (member) => member.mode === "candidate" ? ({
      value: `${draft?.steps.length || 0} draft steps`,
      detail: validationErrors ? `${validationErrors.length} validation issues` : "Awaiting validation",
      content: <section className="english-workflow-preview"><header><span>PREVIEW: {draft?.steps.length || 0} STEPS</span><button type="button" onClick={onOpenWorkflow}>Open Workflow Editor</button></header>{!includesOutput("workflow") ? <p>Add Workflow or a complete group to Generation Order to display the candidate.</p> : workflowSteps(draft, <p>No steps generated yet.</p>)}{draft && jsonDetail(draft)}</section>,
    }) : ({
      value: `${workflow.steps.length} existing steps`,
      detail: workflowPath,
      content: <><button type="button" onClick={onOpenWorkflow}>Open Rich Workflow Editor</button>{workflowSteps(workflow, <p>No existing workflow steps.</p>)}{jsonDetail(workflow)}</>,
    }),
    WorkflowGenerationComposer: composerSurface,
    GenerationOrderHistory: () => ({
      value: `${generationSteps.length} recorded actions`,
      content: <section className="english-workflow-progress" aria-label="Generation Order"><span>GENERATION ORDER · BUTTON PRESS HISTORY</span>{generationSteps.length ? <ol>{generationSteps.map((step, index) => <li className="complete" key={step.id}><i>{index + 1}</i><div><b>{step.action}</b><span>{step.outputs.join(" · ")}</span><small>{step.detail}</small></div></li>)}</ol> : <p>No generation buttons pressed yet. This list records the actual order and outputs.</p>}</section>,
    }),
    GenerationOrderTrials: () => ({
      value: contractTrials.length ? `${contractTrials.length} one-call trials` : "No trials yet",
      detail: "Compare contract and Workflow quality across generation orders",
      baseClass: "english-workflow-contract-panel",
      scrollSize: "240px",
      content: contractTrials.length ? <ol className="english-workflow-trials">{contractTrials.map((trial) => <li key={trial.id}><b>{trial.score}/100</b><span>{trial.requestedOrder.join(" → ")}</span><small>{trial.requestedSteps.map(generationStepSummary).join(" · ")} · {trial.checklistCount} checks · {trial.memoryCount} memory · {trial.workflowSteps} workflow steps · {trial.validationIssues} validation issues · {trial.modelId}</small></li>)}</ol> : <p>No generation order trials have been run.</p>,
    }),
    GenerationContractSection: contractSectionSurface,
    MemoryValuesPlanner: () => ({
      value: memoryPlanned ? `${displayedValues.length} planned values` : analysisContract ? `${contract.memory.length} analyzed candidates` : "Waiting for analysis",
      baseClass: "english-workflow-contract-panel",
      content: memoryPlanned ? <ul>{displayedValues.map((value) => <li key={value.id}><code>{value.label || value.id}</code><span>{value.datatype || "Any"}</span></li>)}</ul> : analysisContract ? <ul>{contract.memory.map((value) => <li key={value.name}><code>{value.name}</code><span>{value.datatype}</span></li>)}</ul> : <p>Analyze creates candidate memory; Plan Memory &amp; Values turns it into explicit runtime values.</p>,
    }),
    AcceptanceChecklist: () => ({
      value: analysisContract ? `${contract.checklist.length} generated checks` : "Waiting for analysis",
      baseClass: "english-workflow-contract-panel",
      content: <><ul className="english-workflow-checklist">{contract.checklist.map((item, index) => <li key={`${index}:${item}`}><input type="checkbox" checked={phase === "validated"} readOnly /><span>{item}</span></li>)}</ul>{validationErrors && <div className={validationErrors.length ? "contract-validation bad" : "contract-validation good"}>{validationErrors.length ? validationErrors.join("\n") : "Backend workflow validation passed."}</div>}</>,
    }),
    WorkflowValidationControls: () => ({
      value: validationErrors === null ? "Not validated" : validationErrors.length ? `${validationErrors.length} issues` : "Passed",
      content: <div className="english-workflow-apply"><button type="button" disabled={busyAction !== "" || !draft?.steps.length} onClick={() => void validateDraft()}>{busyAction === "validate" ? "Validating…" : "Validate Draft"}</button><small>Runs the backend Workflow validator against the current generated draft.</small></div>,
    }),
    WorkflowApplyControls: () => ({
      value: draftReadyToApply ? "Validated draft ready" : "Waiting for validated draft",
      content: <div className="english-workflow-apply"><button type="button" disabled={busyAction !== "" || !draftReadyToApply || !draft?.steps.length || Boolean(validationErrors?.length)} onClick={() => void apply()}>{busyAction === "apply" ? "Applying…" : "Apply Validated Draft"}</button><small>Experimental contract trials never enable Apply. Only a successfully validated Generate Draft result can be written.</small></div>,
    }),
    ResourceSourceEditor: (member) => ({
      value: `${member.resource?.id || pageDefinition?.id}.workflow_page.json`,
      detail: "Resolved three-column page JSON",
      baseClass: "english-workflow-panel english-workflow-page-source",
      content: pageDefinition ? <WorkflowPageSourceEditor workspaceId={workspaceId} pageId={member.resource?.id || pageDefinition.id} disabled={busyAction !== ""} onSaved={onPageDefinitionSaved} /> : <p>No page specification is loaded.</p>,
    }),
    PromptResourceList: () => ({
      value: `${promptChoices.length} effective Prompts`,
      detail: selectedPrompt?.id || "No Prompt selected",
      baseClass: "english-workflow-contract-panel",
      scrollSize: "260px",
      content: <div className="operation-model-list compact">{promptChoices.map((prompt) => <button type="button" className={`operation-model-option ${prompt.id === selectedPrompt?.id ? "selected" : ""}`} key={prompt.id} onClick={() => setSelectedPromptId(prompt.id)}><span><b>{prompt.label || prompt.id}</b><small>{prompt.id} · {prompt.workspaceId || prompt.source || "effective"}</small></span><em>{prompt.id === selectedPrompt?.id ? "selected" : "inspect"}</em></button>)}</div>,
    }),
    PromptTextSourceEditor: () => ({
      value: selectedPrompt?.id || "No Prompt selected",
      detail: selectedPrompt?.path || "Select a Prompt from the list or center playground",
      baseClass: "english-workflow-panel",
      content: selectedPrompt ? <section><div className="operation-editor-actions"><button type="button" onClick={onOpenPrompts}>Open Rich Prompt Editor</button><button type="button" className="primary" disabled={savingPrompt || !selectedPromptSourceValid} onClick={() => void saveSelectedPrompt()}>{savingPrompt ? "Saving…" : "Save Selected Prompt"}</button></div><ResourceSourceEditor value={selectedPromptSource} onChange={setSelectedPromptSource} onValidityChange={setSelectedPromptSourceValid} label={`Edit ${selectedPrompt.label || selectedPrompt.id} source`} /></section> : <p>Select or add a Prompt in the center playground or Prompt list.</p>,
    }),
    OperationResourceDetail: () => ({ value: operation?.id || contractOperation?.id || "No Operation selected", content: operation || contractOperation ? <><button type="button" onClick={onOpenWorkflow}>Open canonical rich editors</button>{jsonDetail(operation || contractOperation)}</> : <p>No authoring Operation is available.</p> }),
    ModelResourceDetail: () => ({ value: selectedModelRecord ? modelOptionLabel(selectedModelRecord) : "Inherited model", content: selectedModelRecord ? jsonDetail(selectedModelRecord) : <p>The system and Operation model-resolution policy will choose the model.</p> }),
    WorkflowSchemaInspector: () => ({ value: "Workflow + step contract", content: jsonDetail({ kind: "workflow", required: ["id", "steps"], stepRequired: ["id", "label", "kind", "operation", "dependsOn", "inputs", "outputs"], stepOptional: ["parameters", "when", "while", "foreach", "branch", "maxIterations", "metadata"] }) }),
    WorkflowInvocationInspector: () => ({ value: phase, detail: busyAction || "idle", content: jsonDetail({ phase, busyAction: busyAction || null, message, validationErrors, draftReadyToApply, generationSteps }) }),
  };

  if (!pageDefinition) return <div className="studio-empty">Generate Workflow requires a filesystem workflow_page specification.</div>;

  return <WorkflowPageHost
    definition={pageDefinition}
    componentRegistry={registry}
    pageClassName="english-workflow-page"
    header={<header className="english-workflow-titlebar"><div><span>{pageDefinition.label.toUpperCase()}</span><h1>{workflow.label || workflow.id}</h1></div><div className="english-workflow-runtime-status"><span>Runtime: Local</span><i /><b>{operation ? "Authoring Operation Ready" : "Authoring Operation Missing"}</b></div></header>}
    footer={<footer className="english-workflow-statusbar"><span><i /> Workspace: {workspaceLabel}</span><span>Mode: Build</span><span>Workflow: {workflowPath}</span><span>AtomSpace: default</span></footer>}
  />;

}
