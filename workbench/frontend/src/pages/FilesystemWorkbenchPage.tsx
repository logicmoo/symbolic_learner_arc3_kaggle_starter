import {
  lazy,
  Suspense,
  useEffect,
  useMemo,
  useRef,
  useState,
  type CSSProperties,
  type PointerEvent as ReactPointerEvent,
} from "react";
import { createPortal } from "react-dom";
import { ChatDock } from "../components/ChatDock";
import { PddlPlanImportPanel } from "../components/PddlPlanImportPanel";
import {
  HumanInputForm,
  RuntimeHistoryView,
} from "../components/RuntimeHistoryView";
import { jsonValueToMetta } from "../lib/mettaResourceCodec";
import {
  ResourceEnablementBadge,
  enablementClass,
  resolveResourceEnablement,
} from "../components/resourceEnablement";
import { ArtifactTreeBranch } from "../components/ArtifactTreeBranch";
import {
  ThreeStateAccordionControls,
  ThreeStateAccordionMember,
  ThreeStateAccordionStack,
  ThreeStateAccordionStripSummary,
  accordionPanelClass,
  type AccordionDisplayMode,
} from "../components/ThreeStateAccordion";
import { DurableRunLauncher } from "../components/DurableRunLauncher";
import {
  WorkflowPageHost,
  type WorkflowPageDefinition,
} from "../components/WorkflowPageHost";
import { TaskStatusBar } from "../taskRegistry";
import "../styles/workflow_layout.css";

const DataCatalogPanel = lazy(() =>
  import("../components/DataCatalogPanel").then((module) => ({
    default: module.DataCatalogPanel,
  })),
);
const GoalPlanLibraryEditor = lazy(() =>
  import("../components/GoalPlanLibraryEditor").then((module) => ({
    default: module.GoalPlanLibraryEditor,
  })),
);
const LlmModelsEditor = lazy(() =>
  import("../components/LlmModelsEditor").then((module) => ({
    default: module.LlmModelsEditor,
  })),
);
const PromptLibraryEditor = lazy(() =>
  import("../components/PromptLibraryEditor").then((module) => ({
    default: module.PromptLibraryEditor,
  })),
);
const OperationLibraryEditor = lazy(() =>
  import("../components/OperationLibraryEditor").then((module) => ({
    default: module.OperationLibraryEditor,
  })),
);
const OperationPlayground = lazy(() =>
  import("../components/OperationPlayground").then((module) => ({
    default: module.OperationPlayground,
  })),
);
const WorkflowRunnerTodoReference = lazy(() =>
  import("../components/WorkflowRunnerTodoReference").then((module) => ({
    default: module.WorkflowRunnerTodoReference,
  })),
);
const ModelPolicyPage = lazy(() =>
  import("../components/ModelPolicyPage").then((module) => ({
    default: module.ModelPolicyPage,
  })),
);
const PolicyLibraryEditor = lazy(() =>
  import("../components/PolicyLibraryEditor").then((module) => ({
    default: module.PolicyLibraryEditor,
  })),
);
const TopicsResourceEditor = lazy(() =>
  import("../components/TopicsResourceEditor").then((module) => ({
    default: module.TopicsResourceEditor,
  })),
);
const RepositoryDocsPage = lazy(() =>
  import("../components/RepositoryDocsPage").then((module) => ({
    default: module.RepositoryDocsPage,
  })),
);
const WorkspaceSettingsPanel = lazy(() =>
  import("../components/WorkspaceSettingsPanel").then((module) => ({
    default: module.WorkspaceSettingsPanel,
  })),
);
const SourceCodeEditor = lazy(() =>
  import("../components/SourceCodeEditor").then((module) => ({
    default: module.SourceCodeEditor,
  })),
);
const WorkspaceOverview = lazy(() =>
  import("../components/WorkspaceOverview").then((module) => ({
    default: module.WorkspaceOverview,
  })),
);
const GenerateWorkflowPage = lazy(() =>
  import("../components/WorkflowGenerationRuntime").then((module) => ({
    default: module.GenerateWorkflowPage,
  })),
);
const VisualImageDiffPage = lazy(() =>
  import("../components/VisualImageDiffPage").then((module) => ({
    default: module.VisualImageDiffPage,
  })),
);
const Arc3PromptPrologPage = lazy(() =>
  import("../components/Arc3PromptPrologPage").then((module) => ({
    default: module.Arc3PromptPrologPage,
  })),
);
const Arc3B1B2PipelinePage = lazy(() =>
  import("../components/Arc3B1B2PipelinePage").then((module) => ({
    default: module.Arc3B1B2PipelinePage,
  })),
);
const Arc3PlayPage = lazy(() =>
  import("../components/Arc3PlayPage").then((module) => ({
    default: module.Arc3PlayPage,
  })),
);
const Arc3GamesGalleryPage = lazy(() =>
  import("../components/Arc3GamesGalleryPage").then((module) => ({
    default: module.Arc3GamesGalleryPage,
  })),
);
const ChatPage = lazy(() =>
  import("../components/ChatPage").then((module) => ({
    default: module.ChatPage,
  })),
);
const WorkflowPageBuilder = lazy(() =>
  import("../components/WorkflowPageBuilder").then((module) => ({
    default: module.WorkflowPageBuilder,
  })),
);
const KnowledgeDataExplorer = lazy(() =>
  import("../components/KnowledgeDataExplorer").then((module) => ({
    default: module.KnowledgeDataExplorer,
  })),
);
const KnowledgeArtifactExplorer = lazy(() =>
  import("../components/KnowledgeArtifactExplorer").then((module) => ({
    default: module.KnowledgeArtifactExplorer,
  })),
);
const HelpDocumentTabs = lazy(() =>
  import("../components/HelpDocumentTabs").then((module) => ({
    default: module.HelpDocumentTabs,
  })),
);

type Workspace = {
  id: string;
  label: string;
  description: string;
  root: string;
  workspaceType?: "project" | "library";
  hidden?: boolean;
  includes?: Array<{ workspaceId: string; includeInherited: boolean }>;
  effectiveIncludes?: string[];
  countsAvailable?: boolean;
  resourceCountBreakdowns?: Partial<
    Record<
      "workflows" | "operations" | "datatypes" | "representations" | "models" | "prompts",
      {
        total: number;
        local: number;
        inherited: number;
        overridden: number;
      }
    >
  >;
  workflowFileCount: number;
  operationFileCount: number;
  backendFileCount?: number;
  modelFileCount?: number;
  promptFileCount?: number;
  datatypeFileCount?: number;
  representationFileCount?: number;
  concreteDatatypeFileCount?: number;
};
type Step = {
  id: string;
  label?: string;
  description?: string;
  enabled?: boolean;
  kind?: string;
  implementation?: string;
  implementationVariant?: string;
  operation?: string;
  dependsOn?: string[];
  inputs?: Record<string, unknown>;
  outputs?: Record<string, string>;
  parameters?: Record<string, unknown>;
  foreach?: {operation?:string;items:unknown;itemPort?:string;maxItems?:number};
  while?: {operation?:string;condition:unknown;operator?:"truthy"|"not_empty"|"equals"|"less_than";conditionPort?:string;maxIterations:number;targetStepId?:string} | {operation?:string;condition:unknown;operator?:"truthy"|"not_empty"|"equals"|"less_than";conditionPort?:string;maxIterations:number;targetStepId?:string}[];
  probe?: { enabled?: boolean; required?: boolean; blocking?: boolean };
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
type PlanProvenance = {
  origin?: "human" | "pddl" | "llm" | "rules" | "imported";
  planner?: string;
  domain?: string;
  problem?: string;
  sourcePlan?: string;
};
type Workflow = {
  id: string;
  version?: number;
  workspaceId?: string;
  label?: string;
  description?: string;
  enabled?: boolean;
  inputs?: Record<string, string>;
  inputDefaults?: Record<string, unknown>;
  outputs?: Record<string, string>;
  steps: Step[];
  planProvenance?: PlanProvenance;
  generation?: {
    operation?: string;
    englishSpecificationPrompt?: string;
    englishDescriptionPath?: string;
    preferredFormat?: string;
    operationCategories?: string[];
    preflightRequired?: boolean;
  };
};
type PreflightStateValue = {
  kind: "state_value";
  id: string;
  label: string;
  enabled: boolean;
  datatype: string;
  source:
    | { kind: "startup_input"; input: string }
    | { kind: "step_output"; stepId: string; output: string; binding?: string }
    | { kind: "description_inference"; requirement: string };
  preferredRenderer: "metta" | "json";
  treatAsList: boolean;
  allowRedefinition: boolean;
  applicability: string[];
  captureGroupIds?: string[];
  defaultValue?: unknown;
  value?: unknown;
};
type RecordFile<T> = {
  path: string;
  source?: "shared" | "included" | "workspace";
  workspaceId?: string;
  document?: T;
  error?: string;
  resolved?: { enabled?: boolean; backendId?: string; backend?: { label?: string } };
};
type DatatypeContract = string | Record<string, unknown>;
type OperationResource = {
  id: string;
  label?: string;
  description?: string;
  categories?: string[];
  topics?: string[];
  implementation?: string;
  parents?: string[];
  children?: string[];
  preferredChild?: string;
  enabled?: boolean;
  inputs?: Record<string, DatatypeContract>;
  outputs?: Record<string, DatatypeContract>;
  parameters?: Record<string, unknown>;
  modelSelection?: { models?: string[]; strategy?: string };
  example_execute?: {
    action?: string;
    arguments?: Record<
      string,
      {
        datatype?: string;
        label?: string;
        default?: unknown;
        options?: unknown[];
      }
    >;
    parameters?: Record<
      string,
      {
        datatype?: string;
        label?: string;
        default?: unknown;
        options?: unknown[];
      }
    >;
  };
};
type OperationLibrary = {
  operations: RecordFile<OperationResource>[];
  operationImplementations: RecordFile<OperationResource>[];
};
type WorkflowRunnerModel = {
  id: string;
  label?: string;
  backendId?: string;
  backendLabel?: string;
  enabled?: boolean;
  capabilities?: Record<string, unknown>;
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
  workflowPages: RecordFile<WorkflowPageDefinition>[];
  models?: RecordFile<{ id: string; label?: string; enabled?: boolean }>[];
  goals?: RecordFile<Record<string, unknown>>[];
  plans?: RecordFile<Record<string, unknown>>[];
  contexts?: RecordFile<Record<string, unknown>>[];
  systems?: RecordFile<Record<string, unknown>>[];
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
  steps: Array<{
    stepId: string;
    status: string;
    attempt?: number;
    error?: string;
  }>;
  artifacts: Array<{
    id: string;
    stepId?: string;
    name: string;
    datatype?: string;
    payload?: unknown;
    contentHash?: string;
    provenance?: Record<string, unknown>;
    createdAt?: string;
  }>;
  events: Array<{
    id: number | string;
    kind: string;
    stepId?: string;
    createdAt: string;
    payload?: unknown;
  }>;
  logs: Array<{
    id: number | string;
    stream: string;
    message: string;
    createdAt?: string;
  }>;
};
type Capability = { status: string; detail: string };
import { ResourceSourceEditor } from "../components/ResourceSourceEditor";
type View =
  | "overview"
  | "currentWorkflow"
  | "englishWorkflow"
  | "visualImageDiff"
  | "arc3TwoImageProlog"
  | "arc3B1B2Pipeline"
  | "arc3Play"
  | "arc3GamesGallery"
  | "chat"
  | "workflowPageBuilder"
  | "canvas"
  | "editor"
  | "data"
  | "knowledgeData"
  | "knowledgeArtifacts"
  | "artifacts"
  | "evidence"
  | "operations"
  | "topics"
  | "sourceCode"
  | "systems"
  | "llms"
  | "prompts"
  | "policies"
  | "checks"
  | "setup"
  | "processes"
  | "goals"
  | "plans"
  | "goalRuns"
  | "workflowRuns"
  | "execs"
  | "events"
  | "states"
  | "logs"
  | "modelPolicy"
  | "benchmarks"
  | "contexts"
  | "runtimeContexts"
  | "docs";
type BreadcrumbEntry = { view: View; label: string; url: string };
type TopbarSwitch = { key: string; label: string; active?: boolean; onClick: () => void };
const WORKBENCH_VIEWS: Set<View> = new Set([
  "overview",
  "currentWorkflow",
  "englishWorkflow",
  "visualImageDiff",
  "arc3TwoImageProlog",
  "arc3B1B2Pipeline",
  "arc3Play",
  "arc3GamesGallery",
  "chat",
  "workflowPageBuilder",
  "canvas",
  "editor",
  "data",
  "knowledgeData",
  "knowledgeArtifacts",
  "artifacts",
  "evidence",
  "operations",
  "topics",
  "sourceCode",
  "systems",
  "llms",
  "prompts",
  "policies",
  "checks",
  "setup",
  "processes",
  "goals",
  "plans",
  "goalRuns",
  "workflowRuns",
  "execs",
  "events",
  "states",
  "logs",
  "modelPolicy",
  "benchmarks",
  "contexts",
  "runtimeContexts",
  "docs",
]);
const viewFromLocation = (): View | null => {
  const parameters = new URLSearchParams(window.location.search);
  const rawValue = parameters.get("view") || parameters.get("menu");
  if (!rawValue) return parameters.has("state") ? "states" : null;
  const value = rawValue.trim().toLowerCase();
  if (value === "workflows" || value === "workflow") return "currentWorkflow";
  if (value === "english-workflow" || value === "englishworkflow") return "englishWorkflow";
  if (value === "visual-image-diff" || value === "visualimagediff" || value === "image-diff") return "visualImageDiff";
  if (value === "two-image-prolog" || value === "twoimageprolog" || value === "arc3-two-image-prolog") return "arc3TwoImageProlog";
  if (value === "b1-b2-pipeline" || value === "b1b2pipeline" || value === "arc3-b1-b2-pipeline") return "arc3B1B2Pipeline";
  if (value === "play" || value === "arc3-play" || value === "arc3play" || value === "play-record") return "arc3Play";
  if (value === "games" || value === "arc3-games" || value === "arc3games" || value === "games-gallery" || value === "arc3-games-gallery") return "arc3GamesGallery";
  if (value === "workflow-page-builder" || value === "workflowpagebuilder" || value === "page-builder") return "workflowPageBuilder";
  if (value === "workflowv2" || value === "workflows-v2" || value === "workflow-v2") return "canvas";
  if (value === "editor") return "canvas";
  if (value === "backends") return "llms";
  return [...WORKBENCH_VIEWS].find((candidate) => candidate.toLowerCase() === value) || null;
};
const workspaceFromLocation = () =>
  new URLSearchParams(window.location.search).get("workspace")?.trim() || null;
const workflowFromLocation = () =>
  new URLSearchParams(window.location.search).get("workflow")?.trim() || null;
const llmsPageFromLocation = (): "browse" | "discover" | "override" => {
  const value = (
    new URLSearchParams(window.location.search).get("llmsPage") || "browse"
  )
    .trim()
    .toLowerCase();
  return value === "discover" || value === "override" ? value : "browse";
};
const chooserResourceOrder = [
  { key: "workflows", label: "workflows" },
  { key: "operations", label: "operations" },
  { key: "datatypes", label: "datatypes" },
  { key: "representations", label: "representations" },
  { key: "models", label: "model/preset items" },
  { key: "prompts", label: "prompts" },
] as const;
const renderResourceBreakdown = (
  value: { total: number; local: number; inherited: number; overridden: number },
  label: string,
) =>
  (
    <span className="workspace-resource-breakdown">
      <span className="workspace-resource-total">{value.total} {label}</span>
      {" ("}
      <span className="workspace-resource-local" title="Local">
        {value.local}
      </span>
      /
      <span className="workspace-resource-inherited" title="Inherited">
        {value.inherited}
      </span>
      /
      <span className="workspace-resource-overridden" title="Overridden">
        {value.overridden}
      </span>
      )
    </span>
  );
const renderResourceBreakdownLegend = () => (
  <span className="workspace-resource-legend">
    {" ("}
    <span className="workspace-resource-local">local</span>/
    <span className="workspace-resource-inherited">inherited</span>/
    <span className="workspace-resource-overridden">overridden</span>)
  </span>
);
const workflowPageMenuPlacementRank = (
  placement: WorkflowPageDefinition["menuPlacement"],
) => ({ first: 0, middle: 1, last: 2 })[placement || "middle"];
type EngineImplementation = { name: string; [key: string]: unknown };
const WORKBENCH_THEMES = [
  { id: "retro-green", label: "Retro Green" },
  { id: "midnight", label: "Midnight Teal" },
  { id: "forest", label: "Forest" },
  { id: "crimson", label: "Crimson" },
  { id: "retro-amber", label: "Retro Amber" },
  { id: "copper", label: "Copper Terminal" },
  { id: "ultraviolet", label: "Ultraviolet" },
  { id: "arctic", label: "Arctic Blue" },
  { id: "cobalt", label: "Cobalt" },
  { id: "graphite", label: "Graphite" },
  { id: "monokai", label: "Monokai" },
  { id: "dracula", label: "Dracula" },
  { id: "solarized-dark", label: "Solarized Dark" },
  { id: "nord-night", label: "Nord Night" },
  { id: "solarized-light", label: "Solarized Light" },
  { id: "rose-light", label: "Rose Quartz" },
  { id: "peach-light", label: "Peach Paper" },
  { id: "sand-light", label: "Sandstone" },
  { id: "orchid-light", label: "Orchid Mist" },
  { id: "lavender-light", label: "Lavender Paper" },
  { id: "blush-light", label: "Soft Blush" },
  { id: "nord-snow-light", label: "Nord Snow" },
  { id: "sage-light", label: "Soft Sage" },
  { id: "sepia-light", label: "Sepia Paper" },
  { id: "fog-light", label: "Morning Fog" },
  { id: "aqua-light", label: "Aqua Wash" },
  { id: "mint-light", label: "Mint Paper" },
  { id: "blueprint-light", label: "Blueprint Paper" },
  { id: "sky-light", label: "Open Sky" },
  { id: "lemon-light", label: "Lemon Wash" },
  { id: "parchment-light", label: "Parchment" },
  { id: "ocean-light", label: "Ocean Day" },
  { id: "ice-light", label: "Arctic Ice" },
  { id: "azure-mist-light", label: "Azure Mist" },
  { id: "msdn-light", label: "MSDN Light" },
  { id: "visual-studio-light", label: "Visual Studio Blue" },
  { id: "cream-light", label: "Warm Cream" },
  { id: "silver-light", label: "Silver Office" },
  { id: "newsprint-light", label: "Newsprint" },
  { id: "paper-light", label: "Paper White" },
  { id: "github-light", label: "GitHub Light" },
  { id: "windows-light", label: "Windows Classic" },
  { id: "porcelain-light", label: "Porcelain" },
  { id: "contrast-light", label: "High Contrast Light" },
  { id: "high-vis-light", label: "High Visibility" },
] as const;
type WorkbenchTheme = (typeof WORKBENCH_THEMES)[number]["id"];
const isWorkbenchTheme = (value: string | null): value is WorkbenchTheme =>
  WORKBENCH_THEMES.some((theme) => theme.id === value);
const WORKSPACE_RESOURCE_COUNTING_STORAGE_KEY =
  "workbench.workspaceResourceCountingEnabled";

export const NAVIGATION_V2: Array<{
  group: "WORKSPACE" | "WORKFLOWS" | "CAPABILITIES" | "KNOWLEDGE" | "RUNTIME" | "SYSTEM";
  items: Array<{ label: string; view: View; glyph: string }>;
}> = [
  {
    group: "WORKSPACE",
    items: [
      { label: "Overview", view: "overview", glyph: "⌂" },
      { label: "Chat", view: "chat", glyph: "✉" },
      { label: "Goals", view: "goals", glyph: "◎" },
      { label: "Planning", view: "plans", glyph: "◇" },
    ],
  },
  {
    group: "WORKFLOWS",
    items: [
      { label: "Current Workflow", view: "currentWorkflow", glyph: "⌘" },
      { label: "Page Builder", view: "workflowPageBuilder", glyph: "▦" },
    ],
  },
  {
    group: "CAPABILITIES",
    items: [
      { label: "Operations", view: "operations", glyph: "▦" },
      { label: "Topics", view: "topics", glyph: "☷" },
      { label: "Source Code", view: "sourceCode", glyph: "</>" },
      { label: "Systems", view: "systems", glyph: "⚙" },
      { label: "Models", view: "llms", glyph: "✦" },
      { label: "Datatypes", view: "data", glyph: "◆" },
      { label: "Policies", view: "policies", glyph: "P" },
    ],
  },
  {
    group: "KNOWLEDGE",
    items: [
      { label: "Data", view: "knowledgeData", glyph: "◫" },
      { label: "AtomSpaces", view: "contexts", glyph: "⚛" },
      { label: "Artifacts", view: "knowledgeArtifacts", glyph: "▣" },
    ],
  },
  {
    group: "RUNTIME",
    items: [
      { label: "Goal Runs", view: "goalRuns", glyph: "◉" },
      { label: "Executions", view: "execs", glyph: "▶" },
      { label: "Events", view: "events", glyph: "△" },
      { label: "States", view: "states", glyph: "▣" },
      { label: "Logs", view: "logs", glyph: "▤" },
    ],
  },
  {
    group: "SYSTEM",
    items: [
      { label: "Docs", view: "docs", glyph: "?" },
      { label: "Model Policy", view: "modelPolicy", glyph: "⚛" },
      { label: "Benchmarks", view: "benchmarks", glyph: "⌁" },
      { label: "Processes", view: "processes", glyph: "◌" },
      { label: "Settings", view: "setup", glyph: "⚒" },
    ],
  },
];
const viewLabel = (view: View) =>
  NAVIGATION_V2.flatMap((section) => section.items).find(
    (item) => item.view === view,
  )?.label ||
  (
    {
      editor: "Workflow Editor",
      englishWorkflow: "Generate Workflow",
      visualImageDiff: "Visual Sequencing",
      arc3TwoImageProlog: "Two-Image Prolog",
      arc3B1B2Pipeline: "B1 → B2 Pipeline",
      arc3Play: "Play & Record",
      arc3GamesGallery: "ARC3 Games",
      workflowPageBuilder: "Workflow Page Builder",
      workflowRuns: "Workflow Runs",
      evidence: "Evidence & provenance",
      checks: "Checks",
      runtimeContexts: "Runtime Contexts",
    } as Partial<Record<View, string>>
  )[view] ||
  view;

type CaptureGroupPlan={id:string;markerName:string;iteration:number;memberStepIds:string[]};
const inferCaptureGroupPlan=(steps:Step[]):CaptureGroupPlan[]=>{const writes=new Map<string,number[]>();steps.forEach((step,index)=>Object.values(step.outputs||{}).forEach(binding=>{const name=String(binding||"");if(name)writes.set(name,[...(writes.get(name)||[]),index])}));return[...writes].flatMap(([markerName,positions])=>positions.length<2?[]:positions.map((start,offset)=>({id:`${markerName}:${offset+1}`,markerName,iteration:offset+1,memberStepIds:steps.slice(start,positions[offset+1]??steps.length).map(step=>step.id)})))};

function WorkflowPreflightSpline({steps}:{steps:Step[]}){
  const[mode,setMode]=useState<AccordionDisplayMode>("scroll");
  const groups=inferCaptureGroupPlan(steps);
  type ExplicitLoop={stepId:string;targetStepId:string;operation:string;kind:"FOR"|"WHILE";label:string;limit:number;nesting:number};
  const explicitLoops:ExplicitLoop[]=steps.flatMap<ExplicitLoop>(step=>{
    const loops:ExplicitLoop[]=[];
    if(step.foreach)loops.push({stepId:step.id,targetStepId:step.id,operation:step.foreach.operation||"control.for_each",kind:"FOR",label:String(step.foreach.items),limit:step.foreach.maxItems??1000,nesting:0});
    const whileLoops=step.while?(Array.isArray(step.while)?step.while:[step.while]):[];
    whileLoops.forEach((loop,nesting)=>loops.push({stepId:step.id,targetStepId:loop.targetStepId||step.id,operation:loop.operation||"control.while",kind:"WHILE",label:`${String(loop.condition)}${loop.operator?` ${loop.operator}`:""}`,limit:loop.maxIterations,nesting}));
    return loops;
  });
  const dependencies=new Map(steps.map((step,index)=>[step.id,step.dependsOn?.length?step.dependsOn:index?[steps[index-1].id]:[]]));
  const depthCache=new Map<string,number>();
  const depthOf=(id:string,visiting=new Set<string>()):number=>{if(depthCache.has(id))return depthCache.get(id)!;if(visiting.has(id))return 0;const parents=dependencies.get(id)||[];const next=new Set(visiting).add(id);const depth=parents.length?Math.max(...parents.map(parent=>depthOf(parent,next)))+1:0;depthCache.set(id,depth);return depth};
  const layers=new Map<number,Step[]>();
  steps.forEach(step=>{const depth=depthOf(step.id);layers.set(depth,[...(layers.get(depth)||[]),step])});
  const maxDepth=Math.max(0,...layers.keys()),maxRows=Math.max(1,...[...layers.values()].map(layer=>layer.length));
  const width=Math.max(620,(maxDepth+1)*175+100),height=Math.max(165,maxRows*70+75),positions=new Map<string,{x:number;y:number}>();
  layers.forEach((layer,depth)=>layer.forEach((step,row)=>positions.set(step.id,{x:70+depth*175,y:48+row*70})));
  const edges=steps.flatMap(step=>(dependencies.get(step.id)||[]).map(parentId=>({parentId,childId:step.id})));
  return <ThreeStateAccordionMember stackId="center-stack" label="PREFLIGHT SPLINE" value={`${groups.length} inferred groups · ${explicitLoops.length} explicit loops`} detail="Dependency branches, repeated-output capture groups, and bounded loop operations before launch." mode={mode} onChange={setMode} baseClass="workflow-preflight-spline" scrollSize="240px" footer={<span>{steps.length} workflow steps · {groups.length} inferred groups · {explicitLoops.length} explicit loops</span>}>
    <div className="workflow-preflight-spline-scroll"><svg viewBox={`0 0 ${width} ${height}`} style={{minWidth:width,height}}><defs><marker id="preflight-spline-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0L10 5L0 10z"/></marker></defs>{edges.map(edge=>{const from=positions.get(edge.parentId),to=positions.get(edge.childId);if(!from||!to)return null;const middle=(from.x+to.x)/2;return <path key={`${edge.parentId}:${edge.childId}`} className="preflight-spline-edge" d={`M${from.x+38},${from.y}C${middle},${from.y} ${middle},${to.y} ${to.x-38},${to.y}`} markerEnd="url(#preflight-spline-arrow)"/>})}{groups.map(group=>{const start=positions.get(group.memberStepIds[0]),end=positions.get(group.memberStepIds.at(-1)||"");if(!start||!end||start.x===end.x)return null;const arch=12+Math.min(22,group.iteration*5);return <g key={group.id}><path className="preflight-spline-loop" d={`M${end.x},${end.y-26}C${end.x},${arch} ${start.x},${arch} ${start.x},${start.y-26}`} markerEnd="url(#preflight-spline-arrow)"/><text className="preflight-spline-loop-label" x={(start.x+end.x)/2} y={arch-4} textAnchor="middle">{group.markerName} · {group.iteration}</text></g>})}{explicitLoops.map(loop=>{const point=positions.get(loop.stepId),target=positions.get(loop.targetStepId);if(!point||!target)return null;const lift=58+loop.nesting*17,middle=(point.x+target.x)/2;return <g key={`${loop.kind}:${loop.stepId}:${loop.targetStepId}:${loop.nesting}`}><path className={`preflight-spline-explicit-loop ${loop.kind.toLowerCase()}`} d={loop.stepId===loop.targetStepId?`M${point.x+29},${point.y-22}C${point.x+62},${point.y-lift} ${point.x-62},${point.y-lift} ${point.x-29},${point.y-22}`:`M${point.x},${point.y-25}C${middle},${point.y-lift} ${middle},${target.y-lift} ${target.x},${target.y-25}`} markerEnd="url(#preflight-spline-arrow)"/><text className="preflight-spline-explicit-label" x={middle} y={Math.min(point.y,target.y)-lift+15} textAnchor="middle">{loop.kind} · ≤ {loop.limit}</text><title>{`${loop.kind} ${loop.label} · return to ${loop.targetStepId} · bounded to ${loop.limit} iterations`}</title></g>})}{steps.map((step,index)=>{const point=positions.get(step.id)!;const memberships=groups.filter(group=>group.memberStepIds.includes(step.id)),nodeLoops=explicitLoops.filter(loop=>loop.stepId===step.id),explicit=nodeLoops[0];return <g key={step.id} className={`preflight-spline-node ${memberships.length?"grouped":""} ${explicit?"explicit-loop":""}`} transform={`translate(${point.x-38},${point.y-22})`}><rect width="76" height="44" rx="5"/><text x="38" y="17" textAnchor="middle">{explicit?nodeLoops.map(loop=>loop.kind).join("/"):index+1}</text><text x="38" y="32" textAnchor="middle">{step.label||step.id}</text><title>{`${dependencies.get(step.id)?.length?`Depends on: ${dependencies.get(step.id)!.join(", ")}. `:"Root step. "}${nodeLoops.length?`${nodeLoops.map(loop=>`${loop.kind} ${loop.label}, return to ${loop.targetStepId}, bounded to ${loop.limit}`).join("; ")}. `:""}${memberships.length?`Value groups: ${memberships.map(group=>group.id).join(", ")}`:"No inferred value group"}`}</title></g>})}</svg></div>
  </ThreeStateAccordionMember>;
}

async function request(path: string, init?: RequestInit) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json", ...(init?.headers || {}) },
    ...init,
  });
  const payload: unknown = await response.json();
  if (!response.ok) {
    const detail =
      typeof payload === "object" && payload !== null
        ? String(
            (payload as Record<string, unknown>).error ||
              (payload as Record<string, unknown>).detail ||
              response.statusText,
          )
        : response.statusText;
    throw new Error(detail);
  }
  return payload as Record<string, any>;
}
const engine = (path: string, init?: RequestInit) =>
  request(`/api/engine${path}`, init);
const slug = (value: string) =>
  value
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "_")
    .replace(/^_+|_+$/g, "") || "workflow";

export function FilesystemWorkbenchPage() {
  const [llmsTopMenuMode, setLlmsTopMenuMode] = useState<
    "browse" | "discover" | "override"
  >(() => llmsPageFromLocation());
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]),
    [workspace, setWorkspace] = useState<Workspace | null>(null),
    [snapshot, setSnapshot] = useState<Snapshot | null>(null),
    [view, setViewState] = useState<View>(() => viewFromLocation() || "canvas");
  const [viewTrail, setViewTrail] = useState<BreadcrumbEntry[]>(() => {
    const initial = viewFromLocation() || "canvas";
    return [
      { view: initial, label: viewLabel(initial), url: window.location.href },
    ];
  });
  const [viewTrailIndex, setViewTrailIndex] = useState(0);
  const breadcrumbNavigation = useRef(false);
  const loadingWorkspaceId = useRef<string | null>(null);
  const currentWorkspaceId = useRef<string | null>(null);
  const setView = (
    next: View,
    options?: { llmsPage?: "browse" | "discover" | "override" },
  ) => {
    setViewState(next);
    if (next === "states") {
      setWorkflowPaneFocus("runs");
      setWorkflowEditorPercent(33.333);
    }
    if (next === "llms") {
      const menu = options?.llmsPage || llmsTopMenuMode;
      setLlmsTopMenuMode(menu);
    }
    const url = new URL(window.location.href);
    url.searchParams.set("view", next === "canvas" ? "workflows" : next);
    if (next === "llms")
      url.searchParams.set("llmsPage", options?.llmsPage || llmsTopMenuMode);
    else url.searchParams.delete("llmsPage");
    url.searchParams.delete("menu");
    url.searchParams.delete("resource");
    if (next !== "sourceCode") url.searchParams.delete("sourceLanguage");
    if (next !== "states") url.searchParams.delete("state");
    window.history.replaceState(
      null,
      "",
      `${url.pathname}${url.search}${url.hash}`,
    );
  };
  const openRuntimeResource = (
    kind: "operation" | "model" | "datatype" | "goal" | "plan" | "context",
    id: string,
  ) => {
    const next: View =
      kind === "operation"
        ? "operations"
        : kind === "model"
          ? "llms"
          : kind === "goal"
            ? "goals"
            : kind === "plan"
              ? "plans"
              : kind === "context"
                ? "contexts"
                : "data";
    setViewState(next);
    if (next === "llms") setLlmsTopMenuMode("browse");
    const url = new URL(window.location.href);
    url.searchParams.set("view", next);
    if (next === "llms") url.searchParams.set("llmsPage", "browse");
    else url.searchParams.delete("llmsPage");
    url.searchParams.set("resource", id);
    url.searchParams.delete("state");
    window.history.replaceState(
      null,
      "",
      `${url.pathname}${url.search}${url.hash}`,
    );
  };
  const [workflowPath, setWorkflowPath] = useState(""),
    [workflowSource, setWorkflowSource] = useState(""),
    [runInputs, setRunInputs] = useState("{}"),
    [selectedStepId, setSelectedStepId] = useState<string | null>(null),
    [humanValues, setHumanValues] = useState<Record<string, unknown>>({}),
    [humanDraftLoaded, setHumanDraftLoaded] = useState(false),
    [humanDraftStatus, setHumanDraftStatus] = useState("");
  const [preflightStateOverrides, setPreflightStateOverrides] = useState<
    Record<string, Partial<PreflightStateValue>>
  >({});
  const [generatedMemoryValues, setGeneratedMemoryValues] = useState<PreflightStateValue[]>([]);
  useEffect(() => setGeneratedMemoryValues([]), [workspace?.id]);
  const [workflowStepDisplayModes, setWorkflowStepDisplayModes] = useState<Record<string, AccordionDisplayMode>>({});
  const [resourceBrowserDisplayMode, setResourceBrowserDisplayMode] = useState<AccordionDisplayMode>("scroll");
  const [workflowAuthoringSubDisplayModes, setWorkflowAuthoringSubDisplayModes] = useState<Record<string, AccordionDisplayMode>>({});
  const [workflowReferenceDisplayMode, setWorkflowReferenceDisplayMode] = useState<AccordionDisplayMode>("strip");
  const [workflowEnglishDescription, setWorkflowEnglishDescription] = useState("");
  const [workflowEnglishDescriptionSaved, setWorkflowEnglishDescriptionSaved] = useState("");
  const [selectedStageDisplayMode, setSelectedStageDisplayMode] = useState<AccordionDisplayMode>("scroll");
  const [workflowColumnsStackDisplayMode, setWorkflowColumnsStackDisplayMode] = useState<AccordionDisplayMode>("scroll");
  const [workflowLeftColumnDisplayMode, setWorkflowLeftColumnDisplayMode] = useState<AccordionDisplayMode>("scroll");
  const [workflowRightColumnDisplayMode, setWorkflowRightColumnDisplayMode] = useState<AccordionDisplayMode>("scroll");
  const toggleSelectedStageDisplayMode = () =>
    setSelectedStageDisplayMode((mode) => mode === "strip" ? "scroll" : "strip");
  const [workflowPaneFocus, setWorkflowPaneFocus] = useState<"editor" | "runs">(
    () =>
      ["workflowRuns", "states"].includes(viewFromLocation() || "")
        ? "runs"
        : "editor",
  );
  const [workflowEditorPercent, setWorkflowEditorPercent] = useState(() =>
    ["workflowRuns", "states"].includes(viewFromLocation() || "")
      ? 33.333
      : 66.667,
  );
  const [workflowColumnsHost, setWorkflowColumnsHost] = useState<HTMLDivElement | null>(null);
  const [takeoverShellPanel, setTakeoverShellPanel] = useState<
    "resource" | "docs" | null
  >(null);
  useEffect(() => {
    if (view !== "workflowRuns") return;
    setWorkflowPaneFocus("runs");
    setView("canvas");
  }, [view]);
  useEffect(() => {
    if (breadcrumbNavigation.current) {
      breadcrumbNavigation.current = false;
      return;
    }
    setViewTrail((current) => {
      if (current[viewTrailIndex]?.view === view) return current;
      const next = [
        ...current.slice(0, viewTrailIndex + 1),
        { view, label: viewLabel(view), url: window.location.href },
      ];
      setViewTrailIndex(next.length - 1);
      return next;
    });
  }, [view]);
  useEffect(() => {
    const record = (event: Event) => {
      const detail = (event as CustomEvent<{ label?: string }>).detail;
      const label = detail?.label?.trim();
      if (!label) return;
      const entry = { view, label, url: window.location.href };
      setViewTrail((current) => {
        const active = current[viewTrailIndex];
        if (active?.url === entry.url && active.label === entry.label)
          return current;
        const next = [...current.slice(0, viewTrailIndex + 1), entry];
        setViewTrailIndex(next.length - 1);
        return next;
      });
    };
    window.addEventListener("workbench:navigation", record);
    return () => window.removeEventListener("workbench:navigation", record);
  }, [view, viewTrailIndex]);
  useEffect(() => {
    if (workspace) {
      setViewTrail([
        { view, label: viewLabel(view), url: window.location.href },
      ]);
      setViewTrailIndex(0);
    }
  }, [workspace?.id]);
  const [run, setRun] = useState<Run | null>(null),
    [selectedArtifactId, setSelectedArtifactId] = useState<string | null>(null),
    [validation, setValidation] = useState<string[] | null>(null),
    [capabilities, setCapabilities] = useState<Record<string, Capability>>({}),
    [implementations, setImplementations] = useState<EngineImplementation[]>(
      [],
    ),
    [busy, setBusy] = useState(false),
    [error, setError] = useState<string | null>(null);
  useEffect(() => {
    const terminalIds = (run?.steps || []).filter((step) => ["completed", "failed", "skipped", "cancelled"].includes(step.status)).map((step) => step.stepId);
    if (!terminalIds.length) return;
    setWorkflowStepDisplayModes((current) => {
      const next = { ...current };
      for (const id of terminalIds) next[id] = "strip";
      return next;
    });
  }, [run?.steps]);
  const [operationLibrary, setOperationLibrary] = useState<OperationLibrary>({
    operations: [],
    operationImplementations: [],
  });
  const [workflowRunnerModels, setWorkflowRunnerModels] = useState<WorkflowRunnerModel[]>([]);
  const [playgroundContext, setPlaygroundContext] = useState<
    Record<string, unknown>
  >({});
  const [collapsedPlaygrounds, setCollapsedPlaygrounds] = useState<
    Record<string, boolean>
  >({});
  const [completedPlaygrounds, setCompletedPlaygrounds] = useState<
    Record<string, boolean>
  >({});
  const [restarting, setRestarting] = useState(false);
  const [theme, setTheme] = useState<WorkbenchTheme>(() => {
    const saved = localStorage.getItem("workbench.theme");
    return isWorkbenchTheme(saved) ? saved : "midnight";
  });
  const [workspaceResourceCountingEnabled, setWorkspaceResourceCountingEnabled] =
    useState(() => {
      const saved = localStorage.getItem(
        WORKSPACE_RESOURCE_COUNTING_STORAGE_KEY,
      );
      if (saved === null) return false;
      return saved !== "false";
    });
  const [newWorkspaceLabel, setNewWorkspaceLabel] = useState("");
  const [newWorkspaceTemplateId, setNewWorkspaceTemplateId] =
    useState("default");
  const [insertOperationId, setInsertOperationId] = useState(
    "gallery.curate_resource",
  );
  const [resourceBrowserWidth, setResourceBrowserWidth] = useState(() =>
    Math.max(
      180,
      Math.min(
        520,
        Number(localStorage.getItem("workbench.resourceBrowserWidth")) || 250,
      ),
    ),
  );
  const [inspectorWidth, setInspectorWidth] = useState(() =>
    Math.max(
      240,
      Number(localStorage.getItem("workbench.inspectorWidth")) || 310,
    ),
  );
  const [docsFilter, setDocsFilter] = useState("");
  const workflow = useMemo<Workflow | null>(() => {
    try {
      return workflowSource ? (JSON.parse(workflowSource) as Workflow) : null;
    } catch {
      return null;
    }
  }, [workflowSource]);
  const workflowPageDefinitions = useMemo(
    () =>
      (snapshot?.workflowPages || []).flatMap((record) =>
        record.document ? [record.document] : [],
      ),
    [snapshot?.workflowPages],
  );
  const workflowPageForView = workflowPageDefinitions.find(
    (definition) => definition.routeView === view,
  );
  const b1b2PageDefinitionForPlay = workflowPageDefinitions.find(
    (definition) => definition.routeView === "arc3B1B2Pipeline",
  );
  const workflowNavigationEntries = useMemo(
    () =>
      workflowPageDefinitions
        .map((definition) => ({
          id: definition.id,
          label: definition.label,
          glyph: definition.glyph || "✧",
          menuPlacement: definition.menuPlacement || "middle",
          order: definition.order ?? 1000,
          definition,
        }))
        .sort(
          (left, right) =>
            workflowPageMenuPlacementRank(left.menuPlacement) -
              workflowPageMenuPlacementRank(right.menuPlacement) ||
            left.order - right.order ||
            left.label.localeCompare(right.label),
        ),
    [workflowPageDefinitions],
  );
  const workflowPageTopbarViews = useMemo(
    () =>
      new Set(
        workflowNavigationEntries
          .map((entry) => entry.definition.routeView as View)
          .filter((candidate) => WORKBENCH_VIEWS.has(candidate)),
      ),
    [workflowNavigationEntries],
  );
  const workflowTopbarActive =
    view === "canvas" ||
    view === "states" ||
    view === "editor" ||
    view === "artifacts" ||
    view === "evidence" ||
    view === "checks" ||
    workflowPageTopbarViews.has(view);
  const sectionTopbarItems = useMemo(() => {
    const section = NAVIGATION_V2.find((entry) =>
      entry.items.some((item) => item.view === view),
    );
    return section?.items || [];
  }, [view]);
  const orderedSectionTopbarItems = useMemo(() => {
    if (!sectionTopbarItems.length) return [];
    const current = sectionTopbarItems.find((item) => item.view === view);
    const others = sectionTopbarItems.filter((item) => item.view !== view);
    return current ? [current, ...others] : sectionTopbarItems;
  }, [sectionTopbarItems, view]);
  const openOverviewShortcut = (anchorId: "overview-top" | "overview-counts" | "overview-inheritance") => {
    setView("overview");
    const url = new URL(window.location.href);
    url.hash = anchorId;
    window.history.replaceState(null, "", `${url.pathname}${url.search}${url.hash}`);
    window.setTimeout(() => {
      document.getElementById(anchorId)?.scrollIntoView({ behavior: "smooth", block: "start" });
    }, 0);
  };
  const pageTopbarSwitches = useMemo<TopbarSwitch[]>(() => {
    if (view === "overview") {
      return [
        { key: "overview", label: "Overview", active: true, onClick: () => openOverviewShortcut("overview-top") },
        { key: "overview-counts", label: "Counts", onClick: () => openOverviewShortcut("overview-counts") },
        { key: "overview-inheritance", label: "Inheritance", onClick: () => openOverviewShortcut("overview-inheritance") },
        { key: "overview-workflows", label: "Open Workflow", onClick: () => setView("currentWorkflow") },
      ];
    }
    return orderedSectionTopbarItems.map((item) => ({
      key: `section-topbar:${item.view}`,
      label: item.label,
      active: item.view === view,
      onClick: () => setView(item.view),
    }));
  }, [view, orderedSectionTopbarItems]);
  const setLeftColumnAccordionMode = (mode: AccordionDisplayMode) => {
    setWorkflowLeftColumnDisplayMode(mode);
    setSelectedStageDisplayMode(mode);
    setWorkflowStepDisplayModes(
      Object.fromEntries((workflow?.steps || []).map((step) => [step.id, mode])),
    );
  };
  const setRightColumnAccordionMode = (mode: AccordionDisplayMode) => {
    setWorkflowRightColumnDisplayMode(mode);
  };
  const parsedRunInputs = useMemo<Record<string, unknown>>(() => {
    try {
      return JSON.parse(runInputs) as Record<string, unknown>;
    } catch {
      return {};
    }
  }, [runInputs]);
  const runInputsValid = useMemo(() => {
    try {
      const value = JSON.parse(runInputs);
      return Boolean(
        value && typeof value === "object" && !Array.isArray(value),
      );
    } catch {
      return false;
    }
  }, [runInputs]);
  const preflightStateValues = useMemo<PreflightStateValue[]>(() => {
    const inferDatatype = (value: unknown, declared?: string) =>
      declared ||
      (Array.isArray(value)
        ? "list"
        : value === null
          ? "null"
          : typeof value === "object"
            ? "object"
            : typeof value);
    const startup = Object.entries(parsedRunInputs).filter(([input])=>input!=="workspace_root").map(([input, value]) => ({
      kind: "state_value" as const,
      id: `startup_${slug(input)}`,
      label: input.replace(/_/g, " "),
      enabled: true,
      datatype: inferDatatype(value, workflow?.inputs?.[input]),
      source: { kind: "startup_input" as const, input },
      preferredRenderer: "json" as const,
      treatAsList: Array.isArray(value),
      allowRedefinition: false,
      applicability: ["startup", "always"],
      defaultValue: workflow?.inputDefaults?.[input],
      value,
    }));
    const steps = workflow?.steps || [];
    const capturePlan=inferCaptureGroupPlan(steps);
    const outputs = steps.flatMap((step) =>
      Object.entries(step.outputs || {}).map(([output, binding]) => ({
        kind: "state_value" as const,
        id: `${slug(step.id)}_${slug(String(binding || output))}`,
        label: String(binding || output).replace(/_/g, " "),
        enabled: true,
        datatype: "unknown",
        source: {
          kind: "step_output" as const,
          stepId: step.id,
          output,
          binding,
        },
        preferredRenderer: "metta" as const,
        treatAsList: false,
        allowRedefinition: true,
        applicability: ["steps", "chapter", "game", "postMortem"],
        captureGroupIds: capturePlan.filter(group=>group.memberStepIds.includes(step.id)).map(group=>group.id),
      })),
    );
    return [...startup, ...outputs];
  }, [parsedRunInputs, workflow]);
  const effectivePreflightStateValues = useMemo(
    () =>
      (generatedMemoryValues.length ? generatedMemoryValues : preflightStateValues).map((value) => ({
        ...value,
        ...preflightStateOverrides[value.id],
      })),
    [generatedMemoryValues, preflightStateOverrides, preflightStateValues],
  );
  const updatePreflightStateValue = (
    id: string,
    patch: Partial<PreflightStateValue>,
  ) =>
    setPreflightStateOverrides((current) => ({
      ...current,
      [id]: { ...current[id], ...patch },
    }));
  const setRunInput = (name: string, value: unknown) =>
    setRunInputs(
      JSON.stringify({ ...parsedRunInputs, [name]: value }, null, 2),
    );
  const selectedStep =
    workflow?.steps.find((step) => step.id === selectedStepId) || null;
  const selectedRuntime =
    run?.steps.find((step) => step.stepId === selectedStepId) || null;
  const selectedArtifact =
    run?.artifacts.find((item) => item.id === selectedArtifactId) ||
    run?.artifacts[0] ||
    null;
  const enabledModelCount = workspace?.modelFileCount || 0;

  useEffect(() => {
    let cancelled = false;
    let detailedTimer = 0;
    void request("/api/workspaces")
      .then((payload) => {
        if (cancelled) return;
        const next = (payload.workspaces || []) as Workspace[];
        setWorkspaces((current) => {
          if (!workspaceResourceCountingEnabled) return next;
          return current.some((item) => item.countsAvailable) ? current : next;
        });
      })
      .catch((reason) => {
        if (!cancelled) setError(String(reason));
      });
    if (workspaceResourceCountingEnabled) {
      // Defer heavy count hydration so URL-driven workspace/view restore is not blocked.
      detailedTimer = window.setTimeout(() => {
        void request("/api/workspaces?detailed=true")
          .then((payload) => {
            if (cancelled) return;
            setWorkspaces((payload.workspaces || []) as Workspace[]);
          })
          .catch(() => undefined);
      }, 1200);
    }
    return () => {
      cancelled = true;
      window.clearTimeout(detailedTimer);
    };
  }, [workspaceResourceCountingEnabled]);
  useEffect(() => {
    if (workspace)
      setPlaygroundContext((current) => ({
        ...current,
        ...(workflow?.inputDefaults || {}),
        workspace_root: workspace.root,
      }));
  }, [
    workspace?.root,
    workflow?.id,
    JSON.stringify(workflow?.inputDefaults || {}),
  ]);
  useEffect(() => {
    setCollapsedPlaygrounds({});
    setCompletedPlaygrounds({});
  }, [workflowPath]);
  useEffect(() => {
    const path = workflow?.generation?.englishDescriptionPath;
    if (!workspace || !path) {
      setWorkflowEnglishDescription("");
      setWorkflowEnglishDescriptionSaved("");
      return;
    }
    let cancelled = false;
    void request(`/api/workspaces/${encodeURIComponent(workspace.id)}/file?path=${encodeURIComponent(path)}`)
      .then((payload) => {
        if (cancelled) return;
        const content = String((payload.file as Record<string, unknown>).content || "");
        setWorkflowEnglishDescription(content);
        setWorkflowEnglishDescriptionSaved(content);
      })
      .catch((reason) => { if (!cancelled) setError(String(reason)); });
    return () => { cancelled = true; };
  }, [workspace?.id, workflow?.id, workflow?.generation?.englishDescriptionPath]);
  useEffect(() => {
    if (
      view !== "englishWorkflow" ||
      !workspace ||
      !workflow ||
      workflow?.generation?.englishDescriptionPath
    )
      return;
    let cancelled = false;
    void request(
      `/api/workspaces/${encodeURIComponent(workspace.id)}/snapshot?scope=shell`,
    )
      .then((payload) => {
        if (cancelled) return;
        const next = payload as unknown as Snapshot;
        setWorkspace(next.workspace);
        setSnapshot(next);
        const selected =
          next.workflows.find((row) => row.path === workflowPath) ||
          next.workflows.find((row) => row.document?.id === workflow.id);
        if (selected?.document?.generation?.englishDescriptionPath)
          setWorkflowSource(JSON.stringify(selected.document, null, 2));
      })
      .catch((reason) => {
        if (!cancelled) setError(String(reason));
      });
    return () => {
      cancelled = true;
    };
  }, [
    view,
    workspace?.id,
    workflow?.id,
    workflow?.generation?.englishDescriptionPath,
    workflowPath,
  ]);
  useEffect(() => {
    if (!run || ["completed", "failed", "cancelled"].includes(run.status))
      return;
    const timer = window.setInterval(
      () =>
        void engine(`/runs/${run.id}`)
          .then((payload) => setRun(payload.run as Run))
          .catch((reason) => setError(String(reason))),
      1000,
    );
    return () => window.clearInterval(timer);
  }, [run?.id, run?.status]);
  const perform = async (work: () => Promise<void>) => {
    setBusy(true);
    setError(null);
    try {
      await work();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : String(reason));
    } finally {
      setBusy(false);
    }
  };
  const refreshSnapshot = async () => {
    if (!workspace) return null;
    const next = (await request(
      `/api/workspaces/${encodeURIComponent(workspace.id)}/snapshot?scope=shell`,
    )) as unknown as Snapshot;
    setWorkspace(next.workspace);
    setSnapshot(next);
    return next;
  };
  const loadWorkspaceById = (workspaceId: string) =>
    perform(async () => {
      const [snapshotPayload, implementationPayload, operationPayload, modelPayload] =
        await Promise.all([
          request(
            `/api/workspaces/${encodeURIComponent(workspaceId)}/snapshot?scope=shell`,
          ),
          engine("/implementations"),
          request(`/api/workspaces/${encodeURIComponent(workspaceId)}/operations`),
          request(`/api/workspaces/${encodeURIComponent(workspaceId)}/models`),
        ]);
      const next = snapshotPayload as unknown as Snapshot;
      setWorkspace(next.workspace);
      currentWorkspaceId.current = next.workspace.id;
      const workspaceUrl = new URL(window.location.href);
      workspaceUrl.searchParams.set("workspace", next.workspace.id);
      window.history.replaceState(
        null,
        "",
        `${workspaceUrl.pathname}${workspaceUrl.search}${workspaceUrl.hash}`,
      );
      setSnapshot(next);
      setImplementations(
        (implementationPayload.implementations || []) as EngineImplementation[],
      );
      setOperationLibrary({
        operations: (operationPayload.operations ||
          []) as RecordFile<OperationResource>[],
        operationImplementations: (operationPayload.operationImplementations ||
          []) as RecordFile<OperationResource>[],
      });
      setWorkflowRunnerModels(
        (modelPayload.models || []).flatMap((record: RecordFile<{ id: string; label?: string; enabled?: boolean; capabilities?: Record<string, unknown> }>) =>
          record.document && record.resolved?.enabled !== false && record.document.enabled !== false
            ? [{
                id: record.document.id,
                label: record.document.label,
                backendId: record.resolved?.backendId,
                backendLabel: record.resolved?.backend?.label,
                enabled: true,
                capabilities: record.document.capabilities,
              }]
            : [],
        ),
      );
      const requestedWorkflow = workflowFromLocation();
      const first =
        next.workflows.find(
          (row) =>
            row.document &&
            (row.path === requestedWorkflow ||
              row.document.id === requestedWorkflow),
        ) || next.workflows.find((row) => row.document);
      const restoredView = viewFromLocation();
      if (first?.document) {
        setWorkflowPath(first.path);
        setWorkflowSource(JSON.stringify(first.document, null, 2));
        setRunInputs(
          JSON.stringify(
            {
              ...first.document.inputDefaults,
              workspace_root: next.workspace.root,
            },
            null,
            2,
          ),
        );
        setSelectedStepId(first.document.steps[0]?.id || null);
        setViewState(restoredView || "canvas");
      } else {
        setWorkflowPath("");
        setWorkflowSource("");
        setRunInputs("{}");
        setSelectedStepId(null);
        setViewState(restoredView || "data");
      }
      setRun(null);
      setSelectedArtifactId(null);
      setValidation(null);
      void engine("/capabilities")
        .then((payload) =>
          setCapabilities(
            (payload.capabilities || {}) as Record<string, Capability>,
          ),
        )
        .catch(() => undefined);
      void request("/api/workspaces")
        .then((payload) =>
          setWorkspaces((current) =>
            workspaceResourceCountingEnabled &&
            current.some((item) => item.countsAvailable)
              ? current
              : ((payload.workspaces || []) as Workspace[]),
          ),
        )
        .catch(() => undefined);
      if (workspaceResourceCountingEnabled) {
        void request("/api/workspaces?detailed=true")
          .then((payload) =>
            setWorkspaces((payload.workspaces || []) as Workspace[]),
          )
          .catch(() => undefined);
      }
    });
  const loadWorkspace = (item: Workspace) => loadWorkspaceById(item.id);
  const loadRequestedWorkspace = () => {
    const requested = workspaceFromLocation();
    if (
      !requested ||
      requested === currentWorkspaceId.current ||
      loadingWorkspaceId.current !== null
    )
      return;
    const match = workspaces.find((item) => item.id === requested);
    if (!match && workspaces.length) return;
    loadingWorkspaceId.current = requested;
    void loadWorkspaceById(match?.id || requested).finally(() => {
      if (loadingWorkspaceId.current === requested)
        loadingWorkspaceId.current = null;
      if (workspaceFromLocation() !== currentWorkspaceId.current)
        loadRequestedWorkspace();
    });
  };
  useEffect(() => {
    loadRequestedWorkspace();
  }, [workspaces, workspace?.id]);
  const showWorkspaceChooser = () => {
    const url = new URL(window.location.href);
    [
      "workspace",
      "resource",
      "run",
      "goalRun",
      "runStep",
      "runEvent",
      "runtimeRecord",
      "state",
    ].forEach((parameter) => url.searchParams.delete(parameter));
    window.history.replaceState(
      null,
      "",
      `${url.pathname}${url.search}${url.hash}`,
    );
    setWorkspace(null);
    currentWorkspaceId.current = null;
    setSnapshot(null);
    setRun(null);
  };
  const createWorkspace = () =>
    perform(async () => {
      const label = newWorkspaceLabel.trim();
      if (!label) throw new Error("Enter a workspace name");
      const payload = await request("/api/workspaces", {
        method: "POST",
        body: JSON.stringify({
          label,
          templateWorkspaceId: newWorkspaceTemplateId,
        }),
      });
      const created = payload.workspace as Workspace;
      setWorkspaces((current) =>
        [...current.filter((item) => item.root !== created.root), created].sort(
          (a, b) => a.label.localeCompare(b.label),
        ),
      );
      setNewWorkspaceLabel("");
      setNewWorkspaceTemplateId("default");
      await loadWorkspace(created);
    });
  const openWorkflow = (path: string) =>
    perform(async () => {
      if (!workspace || !path) return;
      const selectedRecord = snapshot?.workflows.find(
        (row) => row.path === path,
      );
      const url = new URL(window.location.href);
      url.searchParams.set(
        "workflow",
        selectedRecord?.document?.id || path,
      );
      window.history.replaceState(
        null,
        "",
        `${url.pathname}${url.search}${url.hash}`,
      );
      const inherited = snapshot?.workflows.find(
        (row) => row.path === path && row.workspaceId !== workspace.id,
      );
      if (inherited?.document) {
        setWorkflowPath(path);
        setWorkflowSource(JSON.stringify(inherited.document, null, 2));
        setValidation(null);
        setSelectedStepId(inherited.document.steps[0]?.id || null);
        return;
      }
      const payload = await request(
        `/api/workspaces/${encodeURIComponent(workspace.id)}/file?path=${encodeURIComponent(path)}`,
      );
      const content = String(
        (payload.file as Record<string, unknown>).content || "",
      );
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
  const saveWorkflow = () =>
    perform(async () => {
      if (!workspace || !workflow)
        throw new Error("Select a valid workflow document first");
      const path = workflowPath || `design/workflows/${slug(workflow.id)}.json`;
      await request(
        `/api/workspaces/${encodeURIComponent(workspace.id)}/file`,
        {
          method: "PUT",
          body: JSON.stringify({
            path,
            content: JSON.stringify(workflow, null, 2),
          }),
        },
      );
      setWorkflowPath(path);
      await refreshSnapshot();
    });
  const saveWorkflowEnglishDescription = () =>
    perform(async () => {
      const path = workflow?.generation?.englishDescriptionPath;
      if (!workspace || !path) throw new Error("This workflow does not declare an editable English description path");
      await request(`/api/workspaces/${encodeURIComponent(workspace.id)}/file`, {
        method: "PUT",
        body: JSON.stringify({ path, content: workflowEnglishDescription }),
      });
      setWorkflowEnglishDescriptionSaved(workflowEnglishDescription);
    });
  const updatePlanProvenance = (changes: Partial<PlanProvenance>) => {
    if (!workflow) return;
    setWorkflowSource(
      JSON.stringify(
        {
          ...workflow,
          planProvenance: {
            origin: "human",
            ...(workflow.planProvenance || {}),
            ...changes,
          },
        },
        null,
        2,
      ),
    );
  };
  const validateWorkflow = () =>
    perform(async () => {
      if (!workflow) throw new Error("Invalid workflow resource");
      const payload = await engine("/workflows/validate", {
        method: "POST",
        body: JSON.stringify(workflow),
      });
      setValidation((payload.errors || []) as string[]);
    });
  const startRun = () =>
    perform(async () => {
      if (!workflow || !workspace) throw new Error("Invalid workflow resource");
      const definition = { ...workflow, workspaceId: workspace.id };
      delete definition.version;
      const saved = (
        await engine("/workflows", {
          method: "POST",
          body: JSON.stringify(definition),
        })
      ).workflow as Workflow;
      const content = JSON.stringify(saved, null, 2);
      setWorkflowSource(content);
      const path = workflowPath || `design/workflows/${slug(saved.id)}.json`;
      await request(
        `/api/workspaces/${encodeURIComponent(workspace.id)}/file`,
        { method: "PUT", body: JSON.stringify({ path, content }) },
      );
      setWorkflowPath(path);
      const payload = await engine("/runs", {
        method: "POST",
        body: JSON.stringify({
          workspaceId: workspace.id,
          workflowId: saved.id,
          version: saved.version,
          inputs: JSON.parse(runInputs),
          stateValues: effectivePreflightStateValues,
        }),
      });
      setRun(payload.run as Run);
      setSelectedArtifactId(null);
      setCollapsedPlaygrounds({});
    });
  const startAutomaticRun = () => {
    let values: Record<string, unknown>;
    try {
      values = JSON.parse(runInputs) as Record<string, unknown>;
    } catch {
      setError(
        "Run inputs must be valid JSON before automatic play can start.",
      );
      return;
    }
    const automaticInputs = { ...values, mode: "automatic" };
    setRunInputs(JSON.stringify(automaticInputs, null, 2));
    void perform(async () => {
      if (!workflow || !workspace) throw new Error("Invalid workflow resource");
      const definition = { ...workflow, workspaceId: workspace.id };
      delete definition.version;
      const saved = (
        await engine("/workflows", {
          method: "POST",
          body: JSON.stringify(definition),
        })
      ).workflow as Workflow;
      const payload = await engine("/runs", {
        method: "POST",
        body: JSON.stringify({
          workspaceId: workspace.id,
          workflowId: saved.id,
          version: saved.version,
          inputs: automaticInputs,
          stateValues: effectivePreflightStateValues,
        }),
      });
      setRun(payload.run as Run);
      setSelectedArtifactId(null);
      setCollapsedPlaygrounds({});
    });
  };
  const command = (name: string) =>
    perform(async () => {
      if (!run) return;
      const payload = await engine(`/runs/${run.id}/commands`, {
        method: "POST",
        body: JSON.stringify({ command: name }),
      });
      setRun(payload.run as Run);
    });
  const selectRelativeStep = (offset: number) => {
    if (!workflow || !selectedStepId) return;
    const index = workflow.steps.findIndex(
      (step) => step.id === selectedStepId,
    );
    const target =
      workflow.steps[
        Math.max(0, Math.min(workflow.steps.length - 1, index + offset))
      ];
    if (!target) return;
    setSelectedStepId(target.id);
    window.setTimeout(
      () =>
        document
          .getElementById(`workflow-playground-${target.id}`)
          ?.scrollIntoView({ behavior: "smooth", block: "start" }),
      0,
    );
  };
  const stepWorkflow = () => {
    if (view !== "canvas" && view !== "editor") {
      setError("Workflow Step controls are only available in Workflow Editor.");
      return;
    }
    if (!selectedStepId) return;
    const playground = document.getElementById(
      `workflow-playground-${selectedStepId}`,
    );
    const button = playground?.querySelector<HTMLButtonElement>(
      ".operation-execute-step",
    );
    if (!button) {
      setError(
        "This selected workflow node does not expose a directly runnable Operation.",
      );
      return;
    }
    if (button.disabled) {
      setError(button.title || "This step is waiting for its upstream inputs.");
      playground?.scrollIntoView({ behavior: "smooth", block: "center" });
      return;
    }
    button.click();
  };
  const restartServers = async () => {
    if (
      !window.confirm(
        `Restart the UI and API servers${run?.status === "running" ? "? The active workflow run may be interrupted." : "?"}`,
      )
    )
      return;
    setRestarting(true);
    setError(null);
    try {
      const accepted = await request("/api/system/restart", {
        method: "POST",
        body: "{}",
      });
      const previous = String(accepted.instanceId || "");
      for (let attempt = 0; attempt < 80; attempt += 1) {
        await new Promise((resolve) => window.setTimeout(resolve, 250));
        try {
          const response = await fetch("/api/health", { cache: "no-store" });
          if (response.ok) {
            const health = (await response.json()) as { instanceId?: string };
            if (health.instanceId && health.instanceId !== previous) {
              window.location.reload();
              return;
            }
          }
        } catch {
          /* The servers are expected to be briefly unavailable. */
        }
      }
      throw new Error(
        "The servers did not return within 20 seconds. Check their command windows.",
      );
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : String(reason));
      setRestarting(false);
    }
  };
  const submitHuman = () =>
    perform(async () => {
      if (!run || !selectedStepId) return;
      const payload = await engine(
        `/runs/${run.id}/steps/${selectedStepId}/input`,
        { method: "POST", body: JSON.stringify(humanValues) },
      );
      setRun(payload.run as Run);
      setHumanDraftLoaded(false);
      setHumanDraftStatus("");
    });
  const selectRuntimeRun = (nextRun: Run) => {
    void perform(async () => {
      const payload = await engine(
        `/workflows/${encodeURIComponent(nextRun.workflowId)}?version=${nextRun.workflowVersion}`,
      );
      const frozen = payload.workflow as Workflow;
      const record = snapshot?.workflows.find(
        (row) => row.document?.id === nextRun.workflowId,
      );
      const active =
        nextRun.steps.find((step) =>
          ["waiting", "running", "failed"].includes(step.status),
        ) ||
        [...nextRun.steps]
          .reverse()
          .find((step) => step.status === "completed");
      setWorkflowPath(record?.path || "");
      setWorkflowSource(JSON.stringify(frozen, null, 2));
      setRun(nextRun);
      setSelectedArtifactId(null);
      setSelectedStepId(active?.stepId || frozen.steps[0]?.id || null);
    });
  };
  const beginInspectorResize = (event: ReactPointerEvent<HTMLDivElement>) => {
    event.preventDefault();
    const move = (pointer: PointerEvent) =>
      setInspectorWidth(
        Math.max(
          240,
          Math.min(
            window.innerWidth * 0.6,
            window.innerWidth - pointer.clientX,
          ),
        ),
      );
    const stop = () => {
      window.removeEventListener("pointermove", move);
      window.removeEventListener("pointerup", stop);
      document.body.classList.remove("resizing-panel");
    };
    document.body.classList.add("resizing-panel");
    window.addEventListener("pointermove", move);
    window.addEventListener("pointerup", stop);
  };
  const beginResourceBrowserResize = (
    event: ReactPointerEvent<HTMLDivElement>,
  ) => {
    event.preventDefault();
    const startX = event.clientX,
      startWidth = resourceBrowserWidth;
    const move = (pointer: PointerEvent) =>
      setResourceBrowserWidth(
        Math.max(180, Math.min(520, startWidth + pointer.clientX - startX)),
      );
    const stop = () => {
      window.removeEventListener("pointermove", move);
      window.removeEventListener("pointerup", stop);
      document.body.classList.remove("resizing-panel");
    };
    document.body.classList.add("resizing-panel");
    window.addEventListener("pointermove", move);
    window.addEventListener("pointerup", stop);
  };
  const hasActiveTextSelection = () => {
    const selection = window.getSelection();
    return Boolean(selection && !selection.isCollapsed && selection.toString());
  };
  useEffect(() => {
    localStorage.setItem(
      "workbench.resourceBrowserWidth",
      String(Math.round(resourceBrowserWidth)),
    );
    document.documentElement.style.setProperty(
      "--resource-browser-width",
      `${resourceBrowserWidth}px`,
    );
  }, [resourceBrowserWidth]);
  useEffect(() => {
    localStorage.setItem(
      "workbench.inspectorWidth",
      String(Math.round(inspectorWidth)),
    );
  }, [inspectorWidth]);
  useEffect(() => {
    if (view !== "canvas" && view !== "states") return;
    const bindings: Array<[HTMLElement | null, () => void, string]> = [
      [
        document.querySelector<HTMLElement>(".stages-panel .panel-label span"),
        () => setResourceBrowserWidth((width) => (width <= 36 ? 250 : 36)),
        "Resource Browser",
      ],
      [
        document.querySelector<HTMLElement>(".inspector-head > span"),
        () => setInspectorWidth((width) => (width <= 36 ? 310 : 36)),
        "Documentation",
      ],
    ];
    const cleanups = bindings.flatMap(([element, toggle, label]) => {
      if (!element) return [];
      element.setAttribute("role", "button");
      element.setAttribute("tabindex", "0");
      element.setAttribute("title", `Minimize or restore ${label}`);
      const click = () => toggle();
      const key = (event: KeyboardEvent) => {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          toggle();
        }
      };
      element.addEventListener("click", click);
      element.addEventListener("keydown", key);
      return [
        () => {
          element.removeEventListener("click", click);
          element.removeEventListener("keydown", key);
        },
      ];
    });
    return () => cleanups.forEach((cleanup) => cleanup());
  }, [view, resourceBrowserWidth, inspectorWidth]);
  useEffect(() => {
    const states: Array<[string, boolean]> = [
      [".resource-browser-frame-controls", resourceBrowserWidth <= 36],
      [".documentation-frame-controls", inspectorWidth <= 36],
    ];
    states.forEach(([selector, minimized]) =>
      document
        .querySelector(selector)
        ?.classList.toggle("restore-only", minimized),
    );
  }, [view, resourceBrowserWidth, inspectorWidth]);
  useEffect(() => {
    if (view !== "canvas") return;
    const activate = (target: EventTarget | null) => {
      const element = target instanceof Element ? target : null;
      if (element?.closest(".stages-panel .panel-label span")) {
        setResourceBrowserWidth((width) => (width <= 36 ? 250 : 36));
        return true;
      }
      if (element?.closest(".inspector-head > span")) {
        setInspectorWidth((width) => (width <= 36 ? 310 : 36));
        return true;
      }
      return false;
    };
    const click = (event: MouseEvent) => {
      if (activate(event.target)) event.stopPropagation();
    };
    document.addEventListener("click", click, true);
    return () => document.removeEventListener("click", click, true);
  }, [view]);
  useEffect(() => {
    document.documentElement.dataset.workbenchTheme = theme;
    localStorage.setItem("workbench.theme", theme);
  }, [theme]);
  useEffect(() => {
    localStorage.setItem(
      WORKSPACE_RESOURCE_COUNTING_STORAGE_KEY,
      workspaceResourceCountingEnabled ? "true" : "false",
    );
  }, [workspaceResourceCountingEnabled]);
  useEffect(() => {
    const takeoverEnabled = view === "canvas";
    document.body.classList.toggle(
      "shell-takeover-resource",
      takeoverEnabled && takeoverShellPanel === "resource",
    );
    document.body.classList.toggle(
      "shell-takeover-docs",
      takeoverEnabled && takeoverShellPanel === "docs",
    );
    return () => {
      document.body.classList.remove(
        "shell-takeover-resource",
        "shell-takeover-docs",
      );
    };
  }, [takeoverShellPanel, view]);
  useEffect(() => {
    if (view !== "canvas") setTakeoverShellPanel(null);
  }, [view]);
  useEffect(() => {
    if (takeoverShellPanel === "resource" && resourceBrowserWidth > 36)
      setTakeoverShellPanel(null);
    if (takeoverShellPanel === "docs" && inspectorWidth > 36)
      setTakeoverShellPanel(null);
  }, [takeoverShellPanel, resourceBrowserWidth, inspectorWidth]);
  useEffect(() => {
    const openDocs = (event: Event) => {
      setDocsFilter(String((event as CustomEvent).detail || ""));
      setView("docs");
    };
    window.addEventListener("workbench:open-docs", openDocs);
    return () => window.removeEventListener("workbench:open-docs", openDocs);
  }, []);
  useEffect(() => {
    const restoreLocation = () => {
      setViewState(viewFromLocation() || "canvas");
      setLlmsTopMenuMode(llmsPageFromLocation());
      loadRequestedWorkspace();
    };
    window.addEventListener("popstate", restoreLocation);
    return () => window.removeEventListener("popstate", restoreLocation);
  }, [workspaces, workspace?.id]);
  useEffect(() => {
    if (view !== "overview") return;
    const url = new URL(window.location.href);
    const parametersToRemove = [
      "run",
      "goalRun",
      "runStep",
      "runEvent",
      "runtimeRecord",
      "state",
      ...(url.searchParams.get("menu") === "overview" ? ["view"] : []),
    ];
    const changed = parametersToRemove.some((parameter) => {
      const present = url.searchParams.has(parameter);
      url.searchParams.delete(parameter);
      return present;
    });
    if (changed)
      window.history.replaceState(
        null,
        "",
        `${url.pathname}${url.search}${url.hash}`,
      );
  }, [view]);
  useEffect(() => {
    document.body.classList.toggle("docs-focused", view === "docs");
    return () => document.body.classList.remove("docs-focused");
  }, [view]);
  useEffect(() => {
    if (view !== "states") return;
    const timer = window.setTimeout(
      () =>
        document
          .querySelector<HTMLElement>(".detected-memory-controls")
          ?.scrollIntoView({ block: "start" }),
      0,
    );
    return () => window.clearTimeout(timer);
  }, [view, run?.id]);
  useEffect(() => {
    if (!run || !selectedStepId || selectedRuntime?.status !== "waiting") {
      setHumanDraftLoaded(false);
      setHumanDraftStatus("");
      return;
    }
    setHumanDraftLoaded(false);
    setHumanDraftStatus("Loading saved draft…");
    void engine(`/runs/${run.id}/steps/${selectedStepId}/draft`)
      .then((payload) => {
        setHumanValues(
          (payload.draft?.values || {}) as Record<string, unknown>,
        );
        setHumanDraftLoaded(true);
        setHumanDraftStatus(
          payload.draft?.updatedAt
            ? `Draft restored · ${String(payload.draft.updatedAt).replace("T", " ").slice(0, 19)}`
            : "Draft autosave ready",
        );
      })
      .catch((reason) => {
        setHumanDraftLoaded(true);
        setHumanDraftStatus(`Draft unavailable · ${String(reason)}`);
      });
  }, [run?.id, selectedStepId, selectedRuntime?.status]);
  useEffect(() => {
    if (
      !run ||
      !selectedStepId ||
      selectedRuntime?.status !== "waiting" ||
      !humanDraftLoaded
    )
      return;
    setHumanDraftStatus("Saving draft…");
    const timer = window.setTimeout(() => {
      void engine(`/runs/${run.id}/steps/${selectedStepId}/draft`, {
        method: "PUT",
        body: JSON.stringify(humanValues),
      })
        .then((payload) =>
          setHumanDraftStatus(
            `Draft saved · ${String(payload.draft?.updatedAt || "")
              .replace("T", " ")
              .slice(0, 19)}`,
          ),
        )
        .catch((reason) =>
          setHumanDraftStatus(`Draft save failed · ${String(reason)}`),
        );
    }, 500);
    return () => window.clearTimeout(timer);
  }, [
    humanValues,
    humanDraftLoaded,
    run?.id,
    selectedStepId,
    selectedRuntime?.status,
  ]);

  if (!workspace) {
    const visibleWorkspaces = workspaces.filter((item) => !item.hidden);
    return (
      <main className="workbench-shell">
        <section className="workspace-gate">
          <div className="brand-lockup">
            <span className="brand-mark">M</span>
            <div>
              <b>MeTTa Symbolic Learner Workbench</b>
              <small>Choose a filesystem workspace</small>
            </div>
          </div>
          {!workspaceResourceCountingEnabled && (
            <div className="demo-notice">
              <b>WORKSPACE RESOURCE COUNTING DISABLED</b>
              <span>
                Detailed local/inherited/overridden counts are off in Settings.
              </span>
            </div>
          )}
          <div className="workspace-count-actions">
            <button
              type="button"
              className="workspace-count-enumerate"
              disabled={busy}
              title="Scan every workspace and tally its local/inherited/overridden resource counts"
              onClick={() => {
                if (!workspaceResourceCountingEnabled) {
                  setWorkspaceResourceCountingEnabled(true);
                }
                void request("/api/workspaces?detailed=true")
                  .then((payload) =>
                    setWorkspaces((payload.workspaces || []) as Workspace[]),
                  )
                  .catch((reason) => setError(String(reason)));
              }}
            >
              {workspaceResourceCountingEnabled
                ? "Recount resource counts"
                : "Enumerate resource counts"}
            </button>
          </div>
          <div className="workspace-picker-grid">
            <form
              className="workspace-card create-workspace-card"
              onSubmit={(event) => {
                event.preventDefault();
                void createWorkspace();
              }}
            >
              <span className="workspace-kind">NEW FILESYSTEM WORKSPACE</span>
              <h2>Create A New Workspace</h2>
              <p>
                Copy the current files and inclusion settings from an existing
                workspace.
              </p>
              <input
                aria-label="New workspace name"
                placeholder="Workspace name"
                value={newWorkspaceLabel}
                onChange={(event) => setNewWorkspaceLabel(event.target.value)}
              />
              <label>
                Copy from
                <select
                  aria-label="Workspace template"
                  value={newWorkspaceTemplateId}
                  onChange={(event) =>
                    setNewWorkspaceTemplateId(event.target.value)
                  }
                >
                  {visibleWorkspaces.map((item) => (
                    <option key={item.root} value={item.id}>
                      {item.label}
                      {item.id === "default" ? " (recommended)" : ""}
                    </option>
                  ))}
                </select>
              </label>
              <button
                type="submit"
                disabled={busy || !newWorkspaceLabel.trim()}
              >
                Create Workspace
              </button>
              <small>
                Default is preselected. The new workspace becomes an independent
                copy.
              </small>
            </form>
            {visibleWorkspaces.map((item) => (
              <article
                className={`workspace-card ${item.workspaceType === "library" ? "shared-workspace-card" : ""} ${item.id === "default" ? "default-workspace-card" : ""}`}
                key={item.root}
                role="button"
                tabIndex={0}
                onClick={() => {
                  if (hasActiveTextSelection()) return;
                  loadWorkspace(item);
                }}
                onKeyDown={(event) => {
                  if (event.key !== "Enter" && event.key !== " ") return;
                  event.preventDefault();
                  loadWorkspace(item);
                }}
              >
                <span className="workspace-kind">
                  {item.workspaceType === "library"
                    ? "RESOURCE LIBRARY"
                    : item.id === "default"
                      ? "EDITABLE STARTER TEMPLATE"
                      : "FILESYSTEM WORKSPACE"}
                </span>
                <h2>{item.label}</h2>
                <p>{item.description || "Filesystem workspace"}</p>
                <strong>
                  {workspaceResourceCountingEnabled
                    ? item.countsAvailable
                    ? (() => {
                        const breakdowns = item.resourceCountBreakdowns || {};
                        const summary = chooserResourceOrder.reduce<
                          Array<{
                            key: (typeof chooserResourceOrder)[number]["key"];
                            label: (typeof chooserResourceOrder)[number]["label"];
                            value: {
                              total: number;
                              local: number;
                              inherited: number;
                              overridden: number;
                            };
                          }>
                        >((entries, { key, label }) => {
                          const value = breakdowns[key];
                          if (value) entries.push({ key, label, value });
                          return entries;
                        }, []);
                        return summary.length ? (
                          <>
                            {summary.map((entry, index) => (
                              <span key={entry.key}>
                                {index > 0 ? " · " : ""}
                                {renderResourceBreakdown(entry.value, entry.label)}
                              </span>
                            ))}
                            {renderResourceBreakdownLegend()}
                          </>
                        ) : (
                          `${item.workflowFileCount} workflows · ${item.operationFileCount || 0} operations · ${item.datatypeFileCount || 0} datatypes · ${item.representationFileCount || 0} representations · ${item.modelFileCount || 0} model/preset items · ${item.promptFileCount || 0} prompts`
                        );
                      })()
                    : "Calculating local/inherited/overridden totals with the worker pool..."
                    : "Detailed resource counting disabled in Settings"}
                </strong>
                <small>{item.root}</small>
              </article>
            ))}
          </div>
          {error && (
            <div className="backend-error">
              <b>Error</b>
              <span>{error}</span>
              <button onClick={() => setError(null)}>×</button>
            </div>
          )}
        </section>
      </main>
    );
  }

  const currentStepNumber = Math.max(
    1,
    run
      ? run.steps.findIndex((item) => item.stepId === selectedStepId) + 1
      : (workflow?.steps.findIndex((item) => item.id === selectedStepId) ?? 0) +
          1,
  );
  const operationById = new Map(
    operationLibrary.operations.flatMap((record) =>
      record.document ? [[record.document.id, record] as const] : [],
    ),
  );
  const workflowAuthoringOperationIds = [
    workflow?.generation?.operation || "workflow.populate_from_english",
    "workflow.plan_memory_values",
    "workflow.preflight",
    "workflow.validate",
    "workflow.repair",
    "workflow.resolve_implementations",
  ];
  const workflowAuthoringOperations = [...new Set(workflowAuthoringOperationIds)]
    .map((id) => operationById.get(id)?.document)
    .filter((operation): operation is OperationResource => Boolean(operation));
  const englishWorkflowOperation = workflowAuthoringOperations.find(
    (operation) => operation.id === (workflow?.generation?.operation || "workflow.populate_from_english"),
  );
  const acceptEnglishWorkflowOutputs = (outputs: Record<string, unknown>) => {
    if (!workflow) return;
    const returnedPlan = outputs.new_memory_values_plan && typeof outputs.new_memory_values_plan === "object" && !Array.isArray(outputs.new_memory_values_plan)
      ? outputs.new_memory_values_plan as { values?: unknown[] }
      : null;
    if (!Array.isArray(returnedPlan?.values)) {
      setError("Authoring output is missing the combined new_memory_values_plan.values array.");
      return;
    }
    setGeneratedMemoryValues(returnedPlan.values.filter((value): value is PreflightStateValue => Boolean(value && typeof value === "object" && !Array.isArray(value) && (value as { id?: unknown }).id)));
    const generated = outputs.workflow && typeof outputs.workflow === "object" && !Array.isArray(outputs.workflow)
      ? outputs.workflow as Record<string, unknown>
      : outputs;
    if (!generated || typeof generated !== "object" || Array.isArray(generated) || !Array.isArray(generated.steps)) return;
    const draft = { ...workflow, ...generated, generation: workflow.generation };
    setWorkflowSource(JSON.stringify(draft, null, 2));
    setSelectedStepId(draft.steps[0] && typeof draft.steps[0] === "object" ? String((draft.steps[0] as Record<string, unknown>).id || "") : null);
    setValidation(null);
  };
  const implementationsByOperation = new Map<
    string,
    RecordFile<OperationResource>[]
  >();
  for (const record of operationLibrary.operationImplementations) {
    for (const parentId of record.document?.parents || []) {
      const rows = implementationsByOperation.get(parentId) || [];
      rows.push(record);
      implementationsByOperation.set(parentId, rows);
    }
  }
  const insertOperationStep = () => {
    if (!workflow) return;
    const operation = operationById.get(insertOperationId)?.document;
    if (!operation) return;
    const selectedIndex = Math.max(
      -1,
      workflow.steps.findIndex((step) => step.id === selectedStepId),
    );
    const insertIndex = selectedIndex + 1;
    const upstream =
      selectedIndex >= 0 ? workflow.steps[selectedIndex] : undefined;
    const upstreamAlias = upstream
      ? Object.values(upstream.outputs || {})[0]
      : undefined;
    const baseId = slug(operation.id);
    let id = baseId;
    let suffix = 2;
    while (workflow.steps.some((step) => step.id === id)) {
      id = `${baseId}_${suffix++}`;
    }
    const inputNames = Object.keys(operation.inputs || {});
    const inputs = Object.fromEntries(
      inputNames.map((name, index) => [
        name,
        index === 0 && upstreamAlias ? `$${upstreamAlias}` : `$${name}`,
      ]),
    );
    const outputName = Object.keys(operation.outputs || {})[0] || "result";
    const step: Step = {
      id,
      label: operation.label || operation.id,
      kind: "operation",
      operation: operation.id,
      dependsOn: upstream ? [upstream.id] : [],
      inputs,
      outputs: { [outputName]: `${id}_${outputName}` },
      parameters: operation.parameters,
    };
    const steps = [...workflow.steps];
    steps.splice(insertIndex, 0, step);
    setWorkflowSource(JSON.stringify({ ...workflow, steps }, null, 2));
    setSelectedStepId(id);
    setView("canvas");
  };
  const workflowResourceBrowser = (workflow?.steps || []).map((item, index) => {
    const status =
      run?.steps.find((step) => step.stepId === item.id)?.status || "defined";
    const active = selectedStepId === item.id;
    const itemEnablement = resolveResourceEnablement(
      item,
      resolveResourceEnablement(workflow),
    );
    const operationRecord = item.operation
      ? operationById.get(item.operation)
      : undefined;
    const operation = operationRecord?.document;
    const variants = operation
      ? implementationsByOperation.get(operation.id) || []
      : [];
    const stepKind = item.probe
      ? item.probe.required
        ? "REQUIRED PROBE"
        : "OPTIONAL PROBE"
      : item.kind || "OPERATION";
    const stepButton = (
      <button
        className={`stage-button ${enablementClass(itemEnablement)} ${active ? "active" : ""} ${status === "completed" ? "done" : ""}`}
        onClick={() => {
          setSelectedStepId(item.id);
          setView("canvas");
        }}
      >
        <span className="stage-number">{index + 1}</span>
        <span className="stage-line" />
        <span
          className={`stage-icon ${item.kind === "human" ? "amber" : index % 3 === 1 ? "violet" : "cyan"}`}
        >
          {status === "completed"
            ? "✓"
            : status === "skipped"
              ? "○"
              : index + 1}
        </span>
        <div>
          <small>
            {stepKind} · <ResourceEnablementBadge state={itemEnablement} />
          </small>
          <b>{item.label || item.id}</b>
        </div>
        {item.kind === "workflow" && <span className="nested-badge">↳</span>}
      </button>
    );
    if (!operation)
      return (
        <ArtifactTreeBranch
          key={item.id}
          label={item.label || item.id}
          header={stepButton}
          className="operation-tree-group workflow-resource-step"
          childrenClassName="operation-tree-children"
          summaryValue={status}
        />
      );
    const operationButton = (
      <button
        className="operation-tree-row operation-parent"
        onClick={() => openRuntimeResource("operation", operation.id)}
      >
        <span className="operation-kind-badge">OP</span>
        <span>
          <b>{operation.label || operation.id}</b>
          <small>{operation.description || operation.id}</small>
        </span>
        <em>{variants.length} implementations</em>
      </button>
    );
    return (
      <ArtifactTreeBranch
        key={item.id}
        label={item.label || item.id}
        header={stepButton}
        className="operation-tree-group workflow-resource-step"
        childrenClassName="operation-tree-children"
        summaryValue={status}
      >
        <ArtifactTreeBranch
          label={operation.label || operation.id}
          header={operationButton}
          className="operation-tree-group workflow-operation-resource"
          childrenClassName="operation-tree-children"
        >
          {variants.map((record) => {
            const variant = record.document!;
            return (
              <button
                key={variant.id}
                className="operation-tree-row operation-child"
                data-tree-search={JSON.stringify(variant)}
                onClick={() => openRuntimeResource("operation", variant.id)}
              >
                <span
                  className={`operation-kind-badge ${variant.implementation?.startsWith("llm") ? "llm" : ""}`}
                >
                  {variant.implementation?.startsWith("llm") ? "LLM" : "IMPL"}
                </span>
                <span>
                  <b>{variant.label || variant.id}</b>
                  <small>
                    {variant.description ||
                      variant.implementation ||
                      variant.id}
                  </small>
                </span>
                <em>
                  {operation.preferredChild === variant.id
                    ? "preferred"
                    : "alternative"}
                </em>
              </button>
            );
          })}
        </ArtifactTreeBranch>
      </ArtifactTreeBranch>
    );
  });
  const selectedOperation = selectedStep?.operation
    ? operationById.get(selectedStep.operation)?.document
    : undefined;
  const unresolvedWorkflowSteps = (workflow?.steps || []).filter(
    (step) => step.operation && !operationById.has(step.operation),
  );
  const selectedOperationVariants = (
    selectedOperation
      ? implementationsByOperation.get(selectedOperation.id) || []
      : []
  ).flatMap((record) =>
    record.document?.implementation
      ? [{ ...record.document, implementation: record.document.implementation }]
      : [],
  );
  const setStepImplementationVariant = (
    stepId: string,
    implementationVariant: string,
  ) => {
    if (!workflow) return;
    setWorkflowSource(
      JSON.stringify(
        {
          ...workflow,
          steps: workflow.steps.map((step) =>
            step.id === stepId ? { ...step, implementationVariant } : step,
          ),
        },
        null,
        2,
      ),
    );
  };
  const resolvePlaygroundValue = (value: unknown): unknown => {
    if (typeof value !== "string" || !value.startsWith("$")) return value;
    const [root, ...path] = value.slice(1).split(".");
    let resolved = playgroundContext[root];
    for (const part of path) {
      if (!resolved || typeof resolved !== "object") return undefined;
      resolved = (resolved as Record<string, unknown>)[part];
    }
    return resolved;
  };
  const workflowPlaygrounds = (workflow?.steps || []).flatMap((step, index) => {
    const operation = step.operation
      ? operationById.get(step.operation)?.document
      : undefined;
    if (!operation) return [];
    const variants = (
      implementationsByOperation.get(operation.id) || []
    ).flatMap((record) =>
      record.document?.implementation
        ? [
            {
              ...record.document,
              implementation: record.document.implementation,
            },
          ]
        : [],
    );
    const runtime = run?.steps.find((item) => item.stepId === step.id);
    const upstreamAliases = new Set(
      (workflow?.steps || [])
        .slice(0, index)
        .flatMap((candidate) => Object.values(candidate.outputs || {})),
    );
    const requiredUpstreamInputs = Object.entries(step.inputs || {}).flatMap(
      ([name, value]) =>
        typeof value === "string" &&
        value.startsWith("$") &&
        upstreamAliases.has(value.slice(1).split(".")[0])
          ? [name]
          : [],
    );
    const resolvedInputs = Object.fromEntries(
      Object.entries(step.inputs || {}).flatMap(([name, value]) => {
        const resolved = resolvePlaygroundValue(value);
        return resolved === undefined ? [] : [[name, resolved]];
      }),
    );
    return [
      <ThreeStateAccordionMember
        id={`workflow-playground-${step.id}`}
        key={step.id}
        stackId="left-stack"
        label={`WORKFLOW STEP ${index + 1}`}
        value={step.label || step.id}
        detail={`${runtime?.status || (completedPlaygrounds[step.id] ? "completed" : "not run")} · ${operation.label || operation.id}`}
        mode={workflowStepDisplayModes[step.id] || "scroll"}
        onChange={(nextMode) => setWorkflowStepDisplayModes((current) => ({ ...current, [step.id]: nextMode }))}
        baseClass={`${selectedStepId === step.id ? "workflow-step-playground selected" : "workflow-step-playground"}`}
        scrollSize="620px"
        itemHeader={<button
          className="workflow-step-playground-heading"
          onClick={() => setSelectedStepId(step.id)}
        >
          <span>
            STEP {index + 1} OF {workflow?.steps.length || 0}
          </span>
          <b>{step.label || step.id}</b>
          <small>
            {runtime?.status ||
              (completedPlaygrounds[step.id] ? "completed" : "not run")}{" "}
            · {operation.label || operation.id}
          </small>
        </button>}
        footer={<><b>{runtime?.status || (completedPlaygrounds[step.id] ? "completed" : "not run")}</b><span>{operation.label || operation.id}</span></>}
      >
        <OperationPlayground
          workspaceId={workspace.id}
          operation={operation}
          variants={variants}
          workflowStep={step as unknown as Record<string, unknown>}
          onWorkflowStepChange={(next) => {
            if (!workflow) return;
            setWorkflowSource(
              JSON.stringify(
                {
                  ...workflow,
                  steps: workflow.steps.map((candidate) =>
                    candidate.id === step.id
                      ? (next as unknown as Step)
                      : candidate,
                  ),
                },
                null,
                2,
              ),
            );
          }}
          selectedImplementationVariant={step.implementationVariant}
          onImplementationVariantChange={(variant) =>
            setStepImplementationVariant(step.id, variant)
          }
          inputValues={resolvedInputs}
          expectedInputNames={requiredUpstreamInputs}
          collapsed={Boolean(collapsedPlaygrounds[step.id])}
          onCollapsedChange={(collapsed) =>
            setCollapsedPlaygrounds((current) => ({
              ...current,
              [step.id]: collapsed,
            }))
          }
          onInvocationComplete={(outputs) => {
            setCompletedPlaygrounds((current) => ({
              ...current,
              [step.id]: true,
            }));
            const aliases = Object.fromEntries(
              Object.entries(step.outputs || {}).map(([outputName, alias]) => [
                alias,
                outputs[outputName],
              ]),
            );
            setPlaygroundContext((current) => ({
              ...current,
              ...outputs,
              ...aliases,
            }));
            const next = workflow?.steps[index + 1];
            if (next) {
              setSelectedStepId(next.id);
              window.setTimeout(
                () =>
                  document
                    .getElementById(`workflow-playground-${next.id}`)
                    ?.scrollIntoView({ behavior: "smooth", block: "start" }),
                0,
              );
            }
          }}
        />
      </ThreeStateAccordionMember>,
    ];
  });
  const artifactFocused =
    view === "goals" ||
    view === "plans" ||
    view === "data" ||
    view === "llms" ||
    view === "systems" ||
    view === "operations" ||
    view === "sourceCode" ||
    view === "knowledgeArtifacts" ||
    view === "prompts" ||
    view === "policies" ||
    view === "contexts";
  const workflowCombinedView = view === "canvas" || view === "states";
  const relationshipView =
    workflowCombinedView ||
    view === "editor" ||
    artifactFocused ||
    !artifactFocused;
  const workflowBrowserActive =
    workflowCombinedView || view === "editor" || view === "workflowRuns";
  const browserKind =
    view === "docs"
      ? "documentation"
      : view === "states"
        ? "canvas"
        : view === "goalRuns" ||
            view === "execs" ||
            view === "events" ||
            view === "logs" ||
            view === "runtimeContexts"
          ? "runtime"
          : view;
  const contextBrowserFiles = (snapshot?.files || [])
    .filter((file) =>
      browserKind === "documentation"
        ? /\.md$/i.test(file.path)
        : browserKind === "runtime"
          ? /runtime|run|event|state|log|context/i.test(file.path)
          : file.path
              .toLowerCase()
              .includes(
                String(browserKind).toLowerCase().replace("data", "datatype"),
              ),
    )
    .slice(0, 120);
  const contextBrowserTitle =
    view === "docs"
      ? "Help topics"
      : browserKind === "runtime"
        ? "Runtime records"
        : `${NAVIGATION_V2.flatMap((section) => section.items).find((item) => item.view === view)?.label || "Workspace"} resources`;
  const navSelected = (target: View) =>
    target === "canvas"
      ? view === "canvas" ||
        view === "editor" ||
        view === "workflowRuns"
      : target === view;
  const returnToBreadcrumb = (entry: BreadcrumbEntry, index: number) => {
    breadcrumbNavigation.current = true;
    setViewTrailIndex(index);
    window.history.replaceState(null, "", entry.url);
    setViewState(entry.view);
    window.dispatchEvent(new PopStateEvent("popstate"));
  };
  const jumpTo = (selector: string) =>
    document
      .querySelector<HTMLElement>(selector)
      ?.scrollIntoView({ behavior: "smooth", block: "start" });

  return (
    <main className="workbench" data-view={view}>
      <header className="topbar">
        <div className="brand">
          <span className="brand-mark">M</span>
          <div>
            <strong>MeTTaSymbolicLearnerWorkbench</strong>
            <small>NEUROSYMBOLIC EXPERIMENT DESKTOP</small>
          </div>
        </div>
        <div className="automated-runner-tools">
          <span className="pulse" />
          <b>AUTOMATED RUNNER</b>
          <label>
            <span>MODE</span>
            <select
              aria-label="Runner mode"
              value={String(parsedRunInputs.mode || "automatic")}
              onChange={(event) => setRunInput("mode", event.target.value)}
            >
              <option value="interactive">Interactive</option>
              <option value="automatic">Automatic</option>
            </select>
          </label>
          <label>
            <span>MOVES</span>
            <input
              aria-label="Runner move limit"
              type="number"
              min="0"
              value={Number(parsedRunInputs.move_limit ?? 10)}
              onChange={(event) =>
                setRunInput("move_limit", Number(event.target.value))
              }
            />
          </label>
          <label>
            <span>SECONDS</span>
            <input
              aria-label="Runner seconds per game"
              type="number"
              min="0"
              value={Number(parsedRunInputs.seconds_per_game ?? 60)}
              onChange={(event) =>
                setRunInput("seconds_per_game", Number(event.target.value))
              }
            />
          </label>
          <label>
            <span>GAMES</span>
            <input
              aria-label="Runner maximum games"
              type="number"
              min="1"
              placeholder="ALL"
              value={
                parsedRunInputs.max_games == null
                  ? ""
                  : Number(parsedRunInputs.max_games)
              }
              onChange={(event) =>
                setRunInput(
                  "max_games",
                  event.target.value === "" ? null : Number(event.target.value),
                )
              }
            />
          </label>
          <label>
            <span>SEED</span>
            <input
              aria-label="Runner seed"
              type="number"
              value={Number(parsedRunInputs.seed ?? 0)}
              onChange={(event) =>
                setRunInput("seed", Number(event.target.value))
              }
            />
          </label>
          <button
            type="button"
            title="Run only the selected workflow Operation"
            disabled={busy || !selectedStep?.operation}
            onClick={stepWorkflow}
          >
            ▶ Step
          </button>
        </div>
        <div className="toolbar">
          <button
            className="server-restart-button"
            title="Restart UI and API servers"
            disabled={restarting}
            onClick={restartServers}
          >
            {restarting ? "Restarting…" : "↻ Restart"}
          </button>
          <button
            className="icon-button"
            title="Pause automated runner"
            disabled={busy || run?.status !== "running"}
            onClick={() => command("pause")}
          >
            Ⅱ
          </button>
          <button
            className="icon-button"
            title="Stop automated runner"
            disabled={
              busy ||
              !run ||
              ["completed", "failed", "cancelled"].includes(run.status)
            }
            onClick={() => command("cancel")}
          >
            □
          </button>
          <button
            className="run-button workflow-cascade-button"
            title="Run the complete workflow using the runner settings"
            disabled={busy || !workflow}
            onClick={startRun}
          >
            <span>▶</span>Run cascade
          </button>
          <button
            className="run-button automatic-run-button"
            title="Play every remaining ARC game automatically using the move and time limits"
            disabled={
              busy ||
              !workflow ||
              Boolean(
                run &&
                  !["completed", "failed", "cancelled"].includes(run.status),
              )
            }
            onClick={startAutomaticRun}
          >
            <span>▶▶</span>Auto-play all
          </button>
        </div>
      </header>
      {error && (
        <div className="backend-error">
          <b>Error</b>
          <span>{error}</span>
          <button onClick={() => setError(null)}>×</button>
        </div>
      )}
      <nav
        className="page-breadcrumb-trail"
        aria-label="Visited workbench pages"
      >
        {viewTrail.map((entry, index) => (
          <span key={`${entry.url}-${entry.label}-${index}`}>
            {index > 0 && <i aria-hidden="true">›</i>}
            <button
              className={index === viewTrailIndex ? "current" : ""}
              disabled={index === viewTrailIndex}
              onClick={() => returnToBreadcrumb(entry, index)}
            >
              {entry.label}
            </button>
          </span>
        ))}
      </nav>
      <TaskStatusBar />
      <section
        className={`workspace ${relationshipView ? "artifact-focused" : ""} ${view === "modelPolicy" ? "policy-focused" : ""}`}
        style={{ "--inspector-width": `${inspectorWidth}px` } as CSSProperties}
      >
        <aside className="rail navigation-v2">
          {NAVIGATION_V2.map((section) => (
            <div className="rail-section" key={section.group}>
              <span>{section.group}</span>
              {section.group === "WORKFLOWS" &&
                workflowNavigationEntries.map((entry) => {
                  const target = WORKBENCH_VIEWS.has(
                    entry.definition.routeView as View,
                  )
                    ? (entry.definition.routeView as View)
                    : null;
                  return (
                    <button
                      key={`workflow-page:${entry.id}`}
                      data-workflow-page-resource={entry.id}
                      data-workflow-page-placement={entry.menuPlacement}
                      className={`rail-icon ${target === view ? "selected" : ""}`}
                      disabled={!target}
                      onClick={() => target && setView(target)}
                    >
                      <span>{entry.glyph}</span>
                      <small>{entry.label}</small>
                    </button>
                  );
                })}
              {section.items.map((item) => (
                <button
                  key={item.label}
                  data-navigation-label={item.label}
                  className={`rail-icon ${navSelected(item.view) ? "selected" : ""}`}
                  onClick={() => setView(item.view)}
                >
                  <span>{item.glyph}</span>
                  <small>{item.label}</small>
                </button>
              ))}
            </div>
          ))}
          <div className="rail-bottom">
            <button
              className="rail-icon"
              onClick={showWorkspaceChooser}
              title="Switch workspace"
            >
              <span>↩</span>
              <small>Switch Workspace</small>
            </button>
          </div>
        </aside>
        <aside className="stages-panel">
          <div className="panel-label">
            <span>RESOURCE BROWSER</span>
            <button onClick={() => setView("editor")}>•••</button>
          </div>
          <section className={accordionPanelClass("resource-browser-contents", resourceBrowserDisplayMode)}>
          <ThreeStateAccordionControls label="Resource Browser Contents" mode={resourceBrowserDisplayMode} onChange={setResourceBrowserDisplayMode} />
          <ThreeStateAccordionStripSummary title="RESOURCE BROWSER CONTENTS" value={`${workflow?.steps.length || 0} workflow steps`} onOpen={() => setResourceBrowserDisplayMode("scroll")} />
          <div className="workflow-title">
            <b>{workflow?.label || workflow?.id || workspace.label}</b>
            <small>
              {workflow?.description ||
                `${workspace.label} filesystem workflow`}
            </small>
          </div>
          <div className="stage-list workflow-resource-browser">
            {workflowResourceBrowser}
            {!workflow && (
              <div className="studio-empty">
                No workflow file in this workspace.
              </div>
            )}
          </div>
          <div className="run-health">
            <div>
              <span>RUN HEALTH</span>
              <b>{run?.status || "ready"}</b>
            </div>
            <div className="health-bar">
              <i
                style={{
                  width: workflow?.steps.length
                    ? `${Math.round(((run?.steps.filter((step) => step.status === "completed").length || 0) / workflow.steps.length) * 100)}%`
                    : "0%",
                }}
              />
            </div>
            <small>
              {run
                ? `${run.steps.filter((step) => step.status === "completed").length} steps complete · ${run.events.length} durable events`
                : "No active run"}
            </small>
          </div>
          </section>
        </aside>
        <section
          className={`main-stage workflow-columns-${workflowColumnsStackDisplayMode} workflow-left-column-${workflowLeftColumnDisplayMode} workflow-right-column-${workflowRightColumnDisplayMode}`}
          style={
            {
              "--workflow-editor-percent": `${workflowEditorPercent}%`,
              "--workflow-runs-percent": `${100 - workflowEditorPercent}%`,
            } as CSSProperties
          }
        >
          <nav className="view-tabs">
            {view === "llms" ? (
              <>
                <button
                  className={llmsTopMenuMode === "browse" ? "active" : ""}
                  onClick={() => {
                    setLlmsTopMenuMode("browse");
                    setView("llms", { llmsPage: "browse" });
                  }}
                >
                  Browse Models
                </button>
                <button
                  className={llmsTopMenuMode === "discover" ? "active" : ""}
                  onClick={() => {
                    setLlmsTopMenuMode("discover");
                    setView("llms", { llmsPage: "discover" });
                  }}
                >
                  Discover Public Properties
                </button>
                <button
                  className={llmsTopMenuMode === "override" ? "active" : ""}
                  onClick={() => {
                    setLlmsTopMenuMode("override");
                    setView("llms", { llmsPage: "override" });
                  }}
                >
                  Override
                </button>
              </>
            ) : workflowTopbarActive ? (
              <>
                <button
                  className={`workflow-focus-tab ${workflowCombinedView && workflowPaneFocus === "editor" ? "active" : ""}`}
                  onClick={() => {
                    setWorkflowPaneFocus("editor");
                    setWorkflowEditorPercent(66.667);
                    setView("canvas");
                  }}
                >
                  Workflow Editor
                </button>
                <button
                  className={`workflow-focus-tab ${workflowCombinedView && workflowPaneFocus === "runs" ? "active" : ""}`}
                  onClick={() => {
                    setWorkflowPaneFocus("runs");
                    setWorkflowEditorPercent(33.333);
                    setView("canvas");
                  }}
                >
                  Workflow Runs
                </button>
                {workflowNavigationEntries.map(({ definition }) => {
                  const target = WORKBENCH_VIEWS.has(definition.routeView as View)
                    ? (definition.routeView as View)
                    : null;
                  return target ? (
                    <button
                      key={definition.id}
                      data-workflow-page-resource={definition.id}
                      className={view === target ? "active" : ""}
                      onClick={() => setView(target)}
                    >
                      {definition.label}
                    </button>
                  ) : null;
                })}
                <button
                  className={view === "artifacts" ? "active" : ""}
                  onClick={() => setView("artifacts")}
                >
                  Artifact explorer <span>{run?.artifacts.length || 0}</span>
                </button>
                <button
                  className={view === "evidence" ? "active" : ""}
                  onClick={() => setView("evidence")}
                >
                  Evidence & provenance <span>{run?.events.length || 0}</span>
                </button>
                <button
                  className={view === "checks" ? "active" : ""}
                  onClick={() => setView("checks")}
                >
                  Checks
                </button>
              </>
            ) : (
              pageTopbarSwitches.map((item) => (
                <button
                  key={item.key}
                  className={item.active ? "active" : ""}
                  onClick={item.onClick}
                >
                  {item.label}
                </button>
              ))
            )}
          </nav>
          {workflowCombinedView&&<ThreeStateAccordionStack id="center-stack" controlsLabel="CENTER STACK">
          {workflow&&englishWorkflowOperation&&(()=>{
            const operation=englishWorkflowOperation;
            const subMode=(name:string)=>workflowAuthoringSubDisplayModes[`${operation.id}:${name}`]||"scroll";
            const setSubMode=(name:string,next:AccordionDisplayMode)=>setWorkflowAuthoringSubDisplayModes(current=>({...current,[`${operation.id}:${name}`]:next}));
            return <>
                  <ThreeStateAccordionMember stackId="center-stack" initialIndex={0} label="ENGLISH SPECIFICATION EDITOR" value={workflow.generation?.englishDescriptionPath||"No description path"} mode={subMode("description")} onChange={(next)=>setSubMode("description",next)} baseClass="workflow-authoring-suboperation" scrollSize="260px">
                    {workflow.generation?.englishDescriptionPath&&<div className="workflow-english-description-editor"><div><span>ENGLISH WORKFLOW DESCRIPTION</span><code>{workflow.generation.englishDescriptionPath}</code><small>{workflowEnglishDescription!==workflowEnglishDescriptionSaved?"Unsaved changes":"Saved filesystem resource"}</small></div><textarea aria-label="Editable English workflow description" value={workflowEnglishDescription} onChange={(event)=>setWorkflowEnglishDescription(event.target.value)} spellCheck/><button type="button" disabled={busy||workflowEnglishDescription===workflowEnglishDescriptionSaved} onClick={saveWorkflowEnglishDescription}>Save English Description</button></div>}
                  </ThreeStateAccordionMember>
                  <ThreeStateAccordionMember stackId="center-stack" initialIndex={1} label="MEMORY / VALUE PLAN" value={`${effectivePreflightStateValues.length} inferred runtime ${effectivePreflightStateValues.length===1?"value":"values"}`} mode={subMode("memory")} onChange={(next)=>setSubMode("memory",next)} baseClass="workflow-authoring-suboperation" scrollSize="300px">
                    <div className="workflow-inferred-values-intro"><b>{effectivePreflightStateValues.length} inferred runtime {effectivePreflightStateValues.length===1?"value":"values"}</b><span>These come from current startup inputs and generated step outputs—not from the English description.</span>{!workflow.steps.length&&<small>No draft steps exist yet, so description-derived value proposals have not been generated.</small>}</div>
                    <div className="workflow-inferred-values-stack">
                      {effectivePreflightStateValues.map((stateValue)=>{
                        const declared=stateValue.source.kind==="startup_input"&&Boolean(workflow.inputs?.[stateValue.source.input]);
                        const origin=stateValue.source.kind==="startup_input"?(declared?"declared workflow input":"inferred startup input"):stateValue.source.kind==="step_output"?"inferred step output":"inferred from English specification";
                        const source=stateValue.source.kind==="startup_input"?stateValue.source.input:stateValue.source.kind==="step_output"?`${stateValue.source.stepId}.${stateValue.source.output}${stateValue.source.binding?` → ${stateValue.source.binding}`:""}`:stateValue.source.requirement;
                        const displayedValue=stateValue.value!==undefined?JSON.stringify(stateValue.value):stateValue.defaultValue!==undefined?JSON.stringify(stateValue.defaultValue):"not available before execution";
                        return <article key={stateValue.id} className="workflow-inferred-value"><dl><dt>Name</dt><dd><code>{stateValue.label||stateValue.id}</code></dd><dt>Origin</dt><dd>{origin}</dd><dt>Source</dt><dd><code>{source}</code></dd><dt>Datatype</dt><dd>{stateValue.datatype}</dd><dt>Current/default value</dt><dd><code>{displayedValue}</code></dd></dl></article>;
                      })}
                    </div>
                  </ThreeStateAccordionMember>
                  <ThreeStateAccordionMember stackId="center-stack" initialIndex={2} label="GENERATE DRAFT" value={operation.id} detail="Rich operation runner" mode={subMode("runner")} onChange={(next)=>setSubMode("runner",next)} baseClass="workflow-authoring-operation" scrollSize="720px">
                    <OperationPlayground
                      workspaceId={workspace.id}
                      operation={operation}
                      variants={(implementationsByOperation.get(operation.id)||[]).flatMap((record)=>record.document?.implementation?[record.document as OperationResource&{implementation:string}]:[])}
                      models={workflowRunnerModels}
                      inputValues={{
                        english_specification:workflowEnglishDescription,
                        effective_operation_catalog:operationLibrary.operations.flatMap((record)=>{
                          const document=record.document;
                          if(!document)return[];
                          const requiredCategories=workflow.generation?.operationCategories||[];
                          if(!requiredCategories.length)return[document];
                          const topics=document.topics||document.categories||[];
                          return requiredCategories.some(required=>topics.some(topic=>topic===required||topic.startsWith(`${required}/`)))?[document]:[];
                        }),
                        workflow_schema:{kind:"workflow",required:["id","steps"],stepRequired:["id","label","kind","operation","dependsOn","inputs","outputs"],stepOptional:["parameters","when","while","foreach","branch","maxIterations","metadata"]},
                        memory_values_plan:{values:effectivePreflightStateValues},
                        existing_workflow:workflow,
                        validation_errors:validation||[],
                      }}
                      expectedInputNames={["english_specification","effective_operation_catalog","workflow_schema"]}
                      onInvocationComplete={acceptEnglishWorkflowOutputs}
                    />
                  </ThreeStateAccordionMember>
                  <ThreeStateAccordionMember stackId="center-stack" initialIndex={3} label="VALIDATION RESULTS" value={validation===null?"Not validated":validation.length?`${validation.length} errors`:"Valid"} mode={subMode("validation")} onChange={(next)=>setSubMode("validation",next)} baseClass="workflow-authoring-suboperation" scrollSize="150px"><div className="workflow-authoring-operation-controls"><button type="button" onClick={validateWorkflow}>Validate Draft</button><span>{validation===null?"Validation has not run.":validation.length?validation.join(" · "):"The current workflow is valid."}</span></div></ThreeStateAccordionMember>
                  <ThreeStateAccordionMember stackId="center-stack" initialIndex={4} label="APPLY TO WORKFLOW" value={workflow.steps.length?`${workflow.steps.length} steps ready`:"Waiting for draft"} mode={subMode("apply")} onChange={(next)=>setSubMode("apply",next)} baseClass="workflow-authoring-suboperation" scrollSize="130px"><div className="workflow-authoring-operation-controls"><button type="button" disabled={busy||!workflow.steps.length} onClick={saveWorkflow}>Apply and Save Workflow</button><span>Writes the accepted draft to the workflow filesystem resource.</span></div></ThreeStateAccordionMember>
            </>;
          })()}
          {workflowCombinedView&&workflow&&<WorkflowPreflightSpline steps={workflow.steps}/>}
          {workflowCombinedView && (
            <ThreeStateAccordionMember
              stackId="center-stack"
              label="LEFT + RIGHT"
              mode={workflowColumnsStackDisplayMode}
              onChange={setWorkflowColumnsStackDisplayMode}
              baseClass="workflow-columns-stack-member"
              scrollSize="900px"
              itemHeader={<div className="workflow-column-control-groups">
                <span className="workflow-column-control-description"><b>LEFT / RIGHT</b><small>Independent column sizing</small></span>
                <div className="workflow-column-control-group">
                  <b>LEFT</b>
                  <ThreeStateAccordionControls label="Left Column" mode={workflowLeftColumnDisplayMode} onChange={setLeftColumnAccordionMode} />
                </div>
                <div className="workflow-column-control-group">
                  <b>RIGHT</b>
                  <ThreeStateAccordionControls label="Right Column" mode={workflowRightColumnDisplayMode} onChange={setRightColumnAccordionMode} />
                </div>
              </div>}
              footer={null}
            >
              <div
                ref={setWorkflowColumnsHost}
                className={`workflow-columns-host main-stage workflow-columns-${workflowColumnsStackDisplayMode} workflow-left-column-${workflowLeftColumnDisplayMode} workflow-right-column-${workflowRightColumnDisplayMode}`}
                style={{
                  "--workflow-editor-percent": `${workflowEditorPercent}%`,
                  "--workflow-runs-percent": `${100 - workflowEditorPercent}%`,
                } as CSSProperties}
              />
            </ThreeStateAccordionMember>
          )}
          {workflowCombinedView&&<Suspense fallback={<div className="studio-empty">Loading runner design reference…</div>}><WorkflowRunnerTodoReference displayMode={workflowReferenceDisplayMode} onDisplayModeChange={setWorkflowReferenceDisplayMode}/></Suspense>}
          </ThreeStateAccordionStack>}
          <Suspense
            fallback={<div className="studio-empty">Loading editor…</div>}
          >
            {workflowCombinedView && workflowColumnsHost && createPortal(
              <section className="canvas-view">
                <ThreeStateAccordionStack id="left-stack" className="canvas-left-accordion-stack">
                <ThreeStateAccordionMember
                  stackId="left-stack"
                  label={`STAGE ${currentStepNumber} OF ${workflow?.steps.length || 0}`}
                  value={selectedStep?.label || selectedStep?.id || "Select a workflow step"}
                  detail={selectedRuntime?.status || (completedPlaygrounds[selectedStepId || ""] ? "completed" : "defined")}
                  mode={selectedStageDisplayMode}
                  onChange={setSelectedStageDisplayMode}
                  baseClass="selected-stage-accordion"
                  scrollSize="360px"
                  footer={<><b>{selectedRuntime?.status || (completedPlaygrounds[selectedStepId || ""] ? "completed" : "defined")}</b><span>{selectedStep?.operation || selectedStep?.kind || "operation"}</span></>}
                >
                <div className="canvas-heading">
                  <div>
                    <span
                      role="button"
                      tabIndex={0}
                      title="Collapse or restore this stage"
                      onClick={toggleSelectedStageDisplayMode}
                      onKeyDown={(event) => {
                        if (event.key === "Enter" || event.key === " ") {
                          event.preventDefault();
                          toggleSelectedStageDisplayMode();
                        }
                      }}
                    >
                      STAGE {currentStepNumber} OF {workflow?.steps.length || 0}
                    </span>
                    <h1
                      role="button"
                      tabIndex={0}
                      title="Collapse or restore this stage"
                      onClick={toggleSelectedStageDisplayMode}
                      onKeyDown={(event) => {
                        if (event.key === "Enter" || event.key === " ") {
                          event.preventDefault();
                          toggleSelectedStageDisplayMode();
                        }
                      }}
                    >
                      {selectedStep?.label ||
                        selectedStep?.id ||
                        "Select a workflow step"}
                    </h1>
                    <p>
                      {selectedStep?.description ||
                        selectedStep?.implementation ||
                        selectedStep?.operation ||
                        "This view is populated from the selected filesystem workflow."}
                    </p>
                  </div>
                  <div className="canvas-step-controls">
                    <div
                      className={`stage-state ${selectedRuntime?.status || completedPlaygrounds[selectedStepId || ""] ? "completed" : "active"}`}
                    >
                      {(selectedRuntime?.status ||
                      completedPlaygrounds[selectedStepId || ""]
                        ? "completed"
                        : "defined"
                      ).toUpperCase()}
                    </div>
                    <button
                      type="button"
                      title="Select the previous workflow step"
                      disabled={busy || currentStepNumber <= 1}
                      onClick={() => selectRelativeStep(-1)}
                    >
                      ◀ Previous
                    </button>
                    <button
                      type="button"
                      className="run-button workflow-step-button"
                      title="Run only this selected Operation with the inputs displayed below"
                      disabled={busy || !workflow || !selectedStep?.operation}
                      onClick={stepWorkflow}
                    >
                      ▶ Run this step
                    </button>
                    <button
                      type="button"
                      title="Select the next workflow step"
                      disabled={
                        busy ||
                        currentStepNumber >= (workflow?.steps.length || 0)
                      }
                      onClick={() => selectRelativeStep(1)}
                    >
                      Next ▶
                    </button>
                  </div>
                </div>
                {selectedStep ? (
                  <div className="stage-story">
                    <div className="subworkflow-head">
                      <span>
                        {selectedStep.kind === "human" ? "HUMAN" : "STEP"}
                      </span>
                      <b>
                        {selectedStep.implementation ||
                          selectedStep.operation ||
                          selectedStep.kind ||
                          "operation"}
                      </b>
                      <small>
                        {selectedStep.dependsOn?.length
                          ? `depends on ${selectedStep.dependsOn.join(", ")}`
                          : "no explicit dependencies"}
                      </small>
                    </div>
                    <div className="detail-note">
                      <b>Inputs</b>
                      <span>
                        <code>
                          {jsonValueToMetta(selectedStep.inputs || {})}
                        </code>
                      </span>
                    </div>
                    <div className="detail-note">
                      <b>Outputs</b>
                      <span>
                        <code>
                          {jsonValueToMetta(selectedStep.outputs || {})}
                        </code>
                      </span>
                    </div>
                    {selectedRuntime?.status === "waiting" && (
                      <div className="human-pause">
                        <div className="pause-ring">Ⅱ</div>
                        <b>Waiting for human input</b>
                        <small className="human-draft-status">
                          {humanDraftStatus}
                        </small>
                        <HumanInputForm
                          step={selectedStep}
                          busy={busy}
                          draft={humanValues}
                          onDraft={setHumanValues}
                          onSubmit={() => void submitHuman()}
                        />
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="stage-story">
                    <div className="studio-empty">
                      Choose a workflow or use the Data, Models, Prompts,
                      Operations, Checks, and Setup pages.
                    </div>
                  </div>
                )}
                </ThreeStateAccordionMember>
                <div className="workflow-playground-stack three-state-accordion-stack-members">
                  {workflowPlaygrounds}
                </div>
                </ThreeStateAccordionStack>
              </section>,
              workflowColumnsHost,
            )}
            {view === "editor" && (
              <section className="editor-surface">
                <div className="studio-view">
                  <div className="studio-topline">
                    <div>
                      <span>WORKFLOW STUDIO</span>
                      <h1>
                        {workflow?.label || workflow?.id || "No workflow"}
                      </h1>
                      <p>Live filesystem resource from {workspace.root}</p>
                    </div>
                    <div className="studio-actions">
                      <button onClick={validateWorkflow} disabled={!workflow}>
                        Validate
                      </button>
                      <button onClick={saveWorkflow} disabled={!workflow}>
                        Save file
                      </button>
                      <button
                        className="primary"
                        onClick={startRun}
                        disabled={!workflow || busy}
                      >
                        Run
                      </button>
                    </div>
                  </div>
                  <div className="workflow-insert-operation">
                    <label>
                      <span>INSERT OPERATION AFTER SELECTED STEP</span>
                      <select
                        value={insertOperationId}
                        onChange={(event) =>
                          setInsertOperationId(event.target.value)
                        }
                      >
                        {operationLibrary.operations.flatMap((record) =>
                          record.document
                            ? [
                                <option
                                  key={record.document.id}
                                  value={record.document.id}
                                >
                                  {record.document.label || record.document.id}
                                </option>,
                              ]
                            : [],
                        )}
                      </select>
                    </label>
                    <button
                      type="button"
                      onClick={insertOperationStep}
                      disabled={!workflow || !insertOperationId}
                    >
                      + Insert resource
                    </button>
                    <small>
                      The new node is a real filesystem Operation. Its first
                      input is bound to the selected upstream step output and
                      remains editable in the workflow source/playground.
                    </small>
                  </div>
                  {snapshot?.workflows.length ? (
                    <select
                      value={workflowPath}
                      onChange={(event) => openWorkflow(event.target.value)}
                    >
                      {snapshot.workflows.map((row) => (
                        <option key={row.path} value={row.path}>
                          {row.document?.label || row.document?.id || row.path}
                        </option>
                      ))}
                    </select>
                  ) : null}
                  <div className="plan-provenance-editor">
                    <div className="llm-subhead">
                      <div>
                        <span>EXECUTABLE PLAN PROVENANCE</span>
                        <b>Workflow origin for human and PDDL tooling</b>
                        <small>
                          A PDDL plan is stored as this same Workflow; these
                          fields preserve how its grounded steps were produced.
                        </small>
                      </div>
                    </div>
                    <div className="workflow-fields">
                      <label>
                        <span>ORIGIN</span>
                        <select
                          value={workflow?.planProvenance?.origin || "human"}
                          disabled={!workflow}
                          onChange={(event) =>
                            updatePlanProvenance({
                              origin: event.target
                                .value as PlanProvenance["origin"],
                            })
                          }
                        >
                          <option value="human">Human authored</option>
                          <option value="pddl">PDDL planner</option>
                          <option value="llm">LLM generated</option>
                          <option value="rules">Rule generated</option>
                          <option value="imported">Imported</option>
                        </select>
                      </label>
                      <label>
                        <span>PLANNER / GENERATOR</span>
                        <input
                          value={workflow?.planProvenance?.planner || ""}
                          disabled={!workflow}
                          onChange={(event) =>
                            updatePlanProvenance({
                              planner: event.target.value,
                            })
                          }
                        />
                      </label>
                      {workflow?.planProvenance?.origin === "pddl" && (
                        <>
                          <label>
                            <span>PDDL DOMAIN</span>
                            <input
                              value={workflow.planProvenance.domain || ""}
                              onChange={(event) =>
                                updatePlanProvenance({
                                  domain: event.target.value,
                                })
                              }
                            />
                          </label>
                          <label>
                            <span>PDDL PROBLEM</span>
                            <input
                              value={workflow.planProvenance.problem || ""}
                              onChange={(event) =>
                                updatePlanProvenance({
                                  problem: event.target.value,
                                })
                              }
                            />
                          </label>
                          <label className="wide">
                            <span>ORIGINAL GROUNDED PLAN</span>
                            <textarea
                              value={workflow.planProvenance.sourcePlan || ""}
                              placeholder="(move robot room-a room-b)"
                              onChange={(event) =>
                                updatePlanProvenance({
                                  sourcePlan: event.target.value,
                                })
                              }
                            />
                          </label>
                        </>
                      )}
                    </div>
                  </div>
                  <ResourceSourceEditor
                    value={workflowSource}
                    onChange={setWorkflowSource}
                    label="Edit this workflow resource directly"
                  />
                  <div className="workflow-fields">
                    <label className="wide">
                      <span>RUN INPUTS</span>
                      <textarea
                        value={runInputs}
                        onChange={(event) => setRunInputs(event.target.value)}
                      />
                    </label>
                  </div>
                  {validation && (
                    <div
                      className={
                        validation.length ? "validation bad" : "validation good"
                      }
                    >
                      {validation.length
                        ? validation.join("\n")
                        : "Validated by backend"}
                    </div>
                  )}
                </div>
              </section>
            )}
            {view === "editor" && workflow && (
              <PddlPlanImportPanel
                workspaceId={workspace.id}
                workflow={workflow}
                onImported={(imported) => {
                  setWorkflowSource(JSON.stringify(imported, null, 2));
                  setSelectedStepId(imported.steps[0]?.id || null);
                  setValidation(null);
                }}
              />
            )}
            {view === "overview" && (
              <section className="resource-view workspace-overview-host">
                <WorkspaceOverview
                  workspaceId={workspace.id}
                  label={workspace.label}
                  description={workspace.description}
                  inheritedWorkspaces={(workspace.effectiveIncludes || []).map(
                    (id) => {
                      const item = workspaces.find(
                        (candidate) => candidate.id === id,
                      );
                      return {
                        id,
                        label: item?.label || id,
                        description: item?.description,
                      };
                    },
                  )}
                  summary={{
                    workflows: snapshot?.workflows.length || 0,
                    goals: snapshot?.goals?.length || 0,
                    operations: workspace.operationFileCount || 0,
                    datatypes: workspace.datatypeFileCount || 0,
                    representations: workspace.representationFileCount || 0,
                    models: workspace.modelFileCount || 0,
                    files: snapshot?.files.length || 0,
                  }}
                  onOpenWorkflow={
                    snapshot?.workflows.length
                      ? () => setView("canvas")
                      : undefined
                  }
                />
                <WorkspaceSettingsPanel
                  workspace={workspace}
                  workspaces={workspaces}
                  fileCount={snapshot?.files.length || 0}
                  implementationCount={implementations.length}
                  workspaceResourceCountingEnabled={
                    workspaceResourceCountingEnabled
                  }
                  onWorkspaceResourceCountingEnabledChange={
                    setWorkspaceResourceCountingEnabled
                  }
                  mode="workspace"
                  onSwitch={showWorkspaceChooser}
                  onSaved={refreshSnapshot}
                />
              </section>
            )}
            {view === "workflowPageBuilder" && (
              <WorkflowPageBuilder initialDefinition={workflowNavigationEntries[0]?.definition} />
            )}
            {view === "chat" && (
              <Suspense fallback={<div className="studio-empty">Loading chat…</div>}>
                <ChatPage />
              </Suspense>
            )}
            {workflowPageForView && (
              workflowPageForView.renderer === "workflow_generation_runtime" ? workflow ? (
                <GenerateWorkflowPage
                  pageDefinition={workflowPageForView}
                  workspaceId={workspace.id}
                  workspaceLabel={workspace.label}
                  workflow={workflow}
                  workflowPath={workflowPath}
                  description={workflowEnglishDescription}
                  savedDescription={workflowEnglishDescriptionSaved}
                  onDescriptionChange={setWorkflowEnglishDescription}
                  onSaveDescription={saveWorkflowEnglishDescription}
                  operation={englishWorkflowOperation}
                  operationCatalog={operationLibrary.operations.flatMap((record) => record.document ? [record.document] : [])}
                  models={workflowRunnerModels}
                  memoryValues={effectivePreflightStateValues}
                  onGenerated={acceptEnglishWorkflowOutputs}
                  onApply={saveWorkflow}
                  onOpenWorkflow={() => setView("currentWorkflow")}
                  onOpenPrompts={() => setView("prompts")}
                  onPageDefinitionSaved={refreshSnapshot}
                />
              ) : (
                <div className="studio-empty">Select or create a Workflow resource for Generate Workflow to revise.</div>
              ) : workflowPageForView.renderer === "visual_image_diff" ? (
                <VisualImageDiffPage
                  pageDefinition={workflowPageForView}
                  workspaceId={workspace.id}
                  workspaceLabel={workspace.label}
                  models={workflowRunnerModels}
                  operations={operationLibrary.operations.flatMap((record) => record.document ? [record.document] : [])}
                  operationImplementations={operationLibrary.operationImplementations.flatMap((record) => record.document ? [record.document] : [])}
                  onPageDefinitionSaved={refreshSnapshot}
                />
              ) : workflowPageForView.renderer === "arc3_play" ? (
                <Arc3PlayPage
                  pageDefinition={workflowPageForView}
                  workspaceId={workspace.id}
                  workspaceLabel={workspace.label}
                  b1b2PageDefinition={b1b2PageDefinitionForPlay}
                  b1b2Models={workflowRunnerModels}
                  b1b2Files={snapshot?.files || []}
                  onB1B2PageDefinitionSaved={refreshSnapshot}
                />
              ) : workflowPageForView.renderer === "arc3_games_gallery" ? (
                <Arc3GamesGalleryPage
                  pageDefinition={workflowPageForView}
                  workspaceId={workspace.id}
                  workspaceLabel={workspace.label}
                  onPlayGame={(gameShortId) => {
                    setView("arc3Play");
                    const url = new URL(window.location.href);
                    url.searchParams.set("game", gameShortId);
                    window.history.replaceState(null, "", `${url.pathname}${url.search}${url.hash}`);
                  }}
                />
              ) : workflowPageForView.renderer === "arc3_b1_b2_pipeline" ? (
                <Arc3B1B2PipelinePage
                  pageDefinition={workflowPageForView}
                  workspaceId={workspace.id}
                  workspaceLabel={workspace.label}
                  models={workflowRunnerModels}
                  files={snapshot?.files || []}
                  onPageDefinitionSaved={refreshSnapshot}
                />
              ) : workflowPageForView.renderer === "arc3_prompt_prolog" ? (
                <Arc3PromptPrologPage
                  pageDefinition={workflowPageForView}
                  workspaceId={workspace.id}
                  workspaceLabel={workspace.label}
                  models={workflowRunnerModels}
                  files={snapshot?.files || []}
                  onPageDefinitionSaved={refreshSnapshot}
                />
              ) : <WorkflowPageHost definition={workflowPageForView} renderers={{}} />
            )}
            {view === "data" && <DataCatalogPanel workspaceId={workspace.id} />}
            {view === "knowledgeData" && (
              <KnowledgeDataExplorer workspaceId={workspace.id} files={snapshot?.files || []} onChanged={refreshSnapshot} />
            )}
            {view === "knowledgeArtifacts" && (
              <KnowledgeArtifactExplorer workspaceId={workspace.id} files={snapshot?.files || []} />
            )}
            {view === "artifacts" && (
              <section className="artifact-view">
                <div className="artifact-table">
                  <div className="table-head">
                    <span>ARTIFACT</span>
                    <span>TYPE</span>
                    <span>STEP</span>
                    <span>CREATED</span>
                    <span />
                  </div>
                  {run?.artifacts.length ? (
                    run.artifacts.map((item) => (
                      <button
                        key={item.id}
                        className={
                          selectedArtifact?.id === item.id ? "selected" : ""
                        }
                        onClick={() => setSelectedArtifactId(item.id)}
                      >
                        <span>
                          <i className="cyan" />
                          {item.name}
                        </span>
                        <span>{item.datatype || "artifact"}</span>
                        <span>{item.stepId || "workflow input"}</span>
                        <span>{item.createdAt?.slice(11, 19) || "—"}</span>
                        <span>›</span>
                      </button>
                    ))
                  ) : (
                    <div className="studio-empty">
                      Run a workflow to create persisted artifacts.
                    </div>
                  )}
                </div>
                <aside className="artifact-detail">
                  {selectedArtifact ? (
                    <>
                      <span className="detail-eyebrow">ARTIFACT DETAIL</span>
                      <h2>{selectedArtifact.name}</h2>
                      <dl>
                        <div>
                          <dt>Produced by step</dt>
                          <dd>{selectedArtifact.stepId || "workflow input"}</dd>
                        </div>
                        <div>
                          <dt>Content hash</dt>
                          <dd>
                            {selectedArtifact.contentHash || "unavailable"}
                          </dd>
                        </div>
                      </dl>
                      <h3>Payload</h3>
                      <pre>{jsonValueToMetta(selectedArtifact.payload)}</pre>
                      <h3>Provenance</h3>
                      <pre>
                        {jsonValueToMetta(selectedArtifact.provenance || {})}
                      </pre>
                    </>
                  ) : (
                    <div className="studio-empty">No artifact selected.</div>
                  )}
                </aside>
              </section>
            )}
            {view === "evidence" && (
              <section className="evidence-view">
                <div className="evidence-summary">
                  <span>RUN EVIDENCE</span>
                  <strong>
                    {run?.events.length || 0}
                    <small> events</small>
                  </strong>
                  <p>Persisted workflow-engine evidence.</p>
                </div>
                <div className="lineage">
                  {run?.events.length ? (
                    run.events.map((event, index) => (
                      <div className="lineage-node" key={String(event.id)}>
                        <span>{index + 1}</span>
                        <b>{event.kind}</b>
                        <small>
                          {event.stepId || "workflow"} · {event.createdAt}
                        </small>
                      </div>
                    ))
                  ) : (
                    <p>Run a workflow to generate evidence.</p>
                  )}
                </div>
              </section>
            )}
            {view === "goals" && (
              <GoalPlanLibraryEditor workspaceId={workspace.id} family="goal" />
            )}
            {view === "plans" && (
              <GoalPlanLibraryEditor workspaceId={workspace.id} family="plan" />
            )}
            {view === "goalRuns" && (
              <RuntimeHistoryView
                mode="goalRuns"
                workspaceId={workspace.id}
                goals={snapshot?.goals}
                plans={snapshot?.plans}
                contexts={snapshot?.contexts}
                workflows={snapshot?.workflows}
                onSelectRun={selectRuntimeRun}
                onOpenResource={openRuntimeResource}
              />
            )}
            {workflowCombinedView && workflowColumnsHost && createPortal(
              <div
                className="workflow-pane-divider"
                role="separator"
                aria-label="Resize Workflow Editor and Workflow Runs"
                aria-orientation="vertical"
                aria-valuemin={20}
                aria-valuemax={80}
                aria-valuenow={Math.round(workflowEditorPercent)}
                tabIndex={0}
                onPointerDown={(event) => {
                  event.currentTarget.setPointerCapture(event.pointerId);
                }}
                onPointerMove={(event) => {
                  if (!event.currentTarget.hasPointerCapture(event.pointerId))
                    return;
                  const bounds =
                    event.currentTarget.parentElement!.getBoundingClientRect();
                  const percent = Math.max(
                    20,
                    Math.min(
                      80,
                      ((event.clientX - bounds.left) / bounds.width) * 100,
                    ),
                  );
                  setWorkflowEditorPercent(percent);
                  setWorkflowPaneFocus(percent >= 50 ? "editor" : "runs");
                }}
                onPointerUp={(event) =>
                  event.currentTarget.releasePointerCapture(event.pointerId)
                }
                onKeyDown={(event) => {
                  if (event.key !== "ArrowLeft" && event.key !== "ArrowRight")
                    return;
                  event.preventDefault();
                  const percent = Math.max(
                    20,
                    Math.min(
                      80,
                      workflowEditorPercent +
                        (event.key === "ArrowRight" ? 2 : -2),
                    ),
                  );
                  setWorkflowEditorPercent(percent);
                  setWorkflowPaneFocus(percent >= 50 ? "editor" : "runs");
                }}
              >
                <span />
              </div>,
              workflowColumnsHost,
            )}
            {workflowCombinedView && workflowColumnsHost && createPortal(
              <RuntimeHistoryView
                mode={view === "states" ? "states" : "workflowRuns"}
                showDesignReference={false}
                leftColumnDisplayMode={workflowLeftColumnDisplayMode}
                rightColumnDisplayMode={workflowRightColumnDisplayMode}
                runLauncher={
                  <DurableRunLauncher
                    blocked={!runInputsValid || unresolvedWorkflowSteps.length > 0 || Boolean(validation?.length)}
                    status={!runInputsValid ? "INVALID INPUT JSON" : unresolvedWorkflowSteps.length ? `${unresolvedWorkflowSteps.length} UNRESOLVED STEPS` : validation?.length ? `${validation.length} VALIDATION ISSUES` : "READY"}
                    statusDetail={run?.status ? `Current run: ${run.status}` : "No active run"}
                    fields={
                      <>
                        <label className="durable-run-launcher-wide"><span>WORKFLOW</span><select value={workflowPath} onChange={(event) => openWorkflow(event.target.value)}>{snapshot?.workflows.map((row) => <option key={row.path} value={row.path}>{row.document?.label || row.document?.id || row.path}</option>)}</select><small>{workflow?.id || "No workflow selected"} · {workflow?.steps.length || 0} steps</small></label>
                        <label><span>MODE</span><select value={String(parsedRunInputs.mode || "interactive")} onChange={(event) => setRunInput("mode", event.target.value)}><option value="interactive">Interactive</option><option value="automatic">Automatic</option></select></label>
                        <label><span>MOVE LIMIT</span><input type="number" min="0" value={Number(parsedRunInputs.move_limit ?? 10)} onChange={(event) => setRunInput("move_limit", Number(event.target.value))} /></label>
                        <label><span>SECONDS / GAME</span><input type="number" min="0" value={Number(parsedRunInputs.seconds_per_game ?? 60)} onChange={(event) => setRunInput("seconds_per_game", Number(event.target.value))} /></label>
                        <label><span>MAX GAMES</span><input type="number" min="1" placeholder="All" value={parsedRunInputs.max_games == null ? "" : Number(parsedRunInputs.max_games)} onChange={(event) => setRunInput("max_games", event.target.value === "" ? null : Number(event.target.value))} /></label>
                        <label><span>SEED</span><input type="number" value={Number(parsedRunInputs.seed ?? 0)} onChange={(event) => setRunInput("seed", Number(event.target.value))} /></label>
                        <label className="durable-run-launcher-wide"><span>WORKFLOW INPUTS · JSON</span><textarea value={runInputs} onChange={(event) => setRunInputs(event.target.value)} aria-invalid={!runInputsValid} /><small>{runInputsValid ? "Valid input object" : "Enter one valid JSON object."}</small></label>
                      </>
                    }
                    actions={
                      <>
                        <button onClick={validateWorkflow} disabled={busy || !workflow}>Validate</button>
                        <button onClick={saveWorkflow} disabled={busy || !workflow}>Save Workflow</button>
                        <button onClick={stepWorkflow} disabled={busy || !selectedStep?.operation || !runInputsValid}>Run Selected Step</button>
                        <button className="primary" onClick={startRun} disabled={busy || !workflow || !runInputsValid || unresolvedWorkflowSteps.length > 0}>Run Workflow</button>
                        <button className="primary automatic" onClick={startAutomaticRun} disabled={busy || !workflow || !runInputsValid || unresolvedWorkflowSteps.length > 0}>Run All Games</button>
                      </>
                    }
                  />
                }
                workspaceId={workspace.id}
                preflightStateValues={effectivePreflightStateValues}
                onSelectRun={selectRuntimeRun}
                onOpenResource={openRuntimeResource}
              />,
              workflowColumnsHost,
            )}
            {workflowCombinedView && workflowColumnsHost && workflowColumnsStackDisplayMode !== "strip" && createPortal(
              <footer className="workflow-columns-stack-footer">
                <b>LEFT / RIGHT COLUMNS</b>
                <span>Left {workflowLeftColumnDisplayMode} · Right {workflowRightColumnDisplayMode}</span>
              </footer>,
              workflowColumnsHost,
            )}
            {view === "execs" && (
              <RuntimeHistoryView
                mode="execs"
                workspaceId={workspace.id}
                onSelectRun={selectRuntimeRun}
                onOpenResource={openRuntimeResource}
              />
            )}
            {view === "events" && (
              <RuntimeHistoryView
                mode="events"
                workspaceId={workspace.id}
                onSelectRun={selectRuntimeRun}
                onOpenResource={openRuntimeResource}
              />
            )}
            {view === "runtimeContexts" && (
              <RuntimeHistoryView
                mode="runtimeContexts"
                workspaceId={workspace.id}
                onSelectRun={selectRuntimeRun}
                onOpenResource={openRuntimeResource}
              />
            )}
            {view === "logs" && (
              <RuntimeHistoryView
                mode="logs"
                workspaceId={workspace.id}
                onSelectRun={selectRuntimeRun}
                onOpenResource={openRuntimeResource}
              />
            )}
            {view === "modelPolicy" && (
              <ModelPolicyPage
                workspaceId={workspace.id}
                onOpenModels={() => setView("llms")}
              />
            )}
            {view === "docs" && (
              <RepositoryDocsPage initialFilter={docsFilter} />
            )}
            {view === "benchmarks" && (
              <ModelPolicyPage
                workspaceId={workspace.id}
                onOpenModels={() => setView("llms")}
                mode="benchmarks"
              />
            )}
            {view === "contexts" && (
              <GoalPlanLibraryEditor
                workspaceId={workspace.id}
                family="context"
              />
            )}
            {view === "operations" && (
              <OperationLibraryEditor workspaceId={workspace.id} />
            )}{" "}
            {view === "sourceCode" && (
              <SourceCodeEditor workspaceId={workspace.id} />
            )}{" "}
            {view === "topics" && (
              <TopicsResourceEditor workspaceId={workspace.id} />
            )}{" "}
            {view === "policies" && (
              <PolicyLibraryEditor workspaceId={workspace.id} />
            )}{" "}
            {view === "systems" && (
              <LlmModelsEditor
                workspaceId={workspace.id}
                catalogMode="systems"
              />
            )}{" "}
            {view === "llms" && (
              <LlmModelsEditor
                workspaceId={workspace.id}
                catalogMode="models"
                topMenuMode={llmsTopMenuMode}
              />
            )}{" "}
            {view === "prompts" && (
              <PromptLibraryEditor workspaceId={workspace.id} />
            )}
            {view === "checks" && (
              <section className="resource-view">
                <div className="resource-heading">
                  <div>
                    <span>VALIDATION</span>
                    <h1>Checks & diagnostics</h1>
                    <p>
                      Workflow validation and runtime capability probes are
                      computed by the backend.
                    </p>
                  </div>
                  <button onClick={validateWorkflow} disabled={!workflow}>
                    Run validation
                  </button>
                </div>
                <div className="checks-summary">
                  <div className="check-score">
                    {validation === null ? "—" : validation.length ? "!" : "✓"}
                    <small>
                      {validation === null
                        ? "idle"
                        : validation.length
                          ? "issues"
                          : "pass"}
                    </small>
                    <span>WORKFLOW CHECK</span>
                  </div>
                  <div className="check-list">
                    {Object.entries(capabilities).map(([name, value]) => (
                      <div key={name}>
                        <span>
                          {value.status === "implemented"
                            ? "✓"
                            : value.status === "partial"
                              ? "◐"
                              : "·"}
                        </span>
                        <b>{name}</b>
                        <small>{value.detail}</small>
                        <em>{value.status}</em>
                      </div>
                    ))}
                  </div>
                </div>
              </section>
            )}
            {view === "processes" && (
              <WorkspaceSettingsPanel
                workspace={workspace}
                workspaces={workspaces}
                fileCount={snapshot?.files.length || 0}
                implementationCount={implementations.length}
                workspaceResourceCountingEnabled={
                  workspaceResourceCountingEnabled
                }
                onWorkspaceResourceCountingEnabledChange={
                  setWorkspaceResourceCountingEnabled
                }
                mode="processes"
                onSwitch={showWorkspaceChooser}
                onSaved={refreshSnapshot}
              />
            )}{" "}
            {view === "setup" && (
              <WorkspaceSettingsPanel
                workspace={workspace}
                workspaces={workspaces}
                fileCount={snapshot?.files.length || 0}
                implementationCount={implementations.length}
                workspaceResourceCountingEnabled={
                  workspaceResourceCountingEnabled
                }
                onWorkspaceResourceCountingEnabledChange={
                  setWorkspaceResourceCountingEnabled
                }
                onSwitch={showWorkspaceChooser}
                onSaved={refreshSnapshot}
              />
            )}
          </Suspense>
        </section>
        <div className="topbar-panel-restore-stack">
          <div className="topbar-global-actions" data-stack-scope="global">
            <button
              type="button"
              className="topbar-panel-restore"
              disabled={restarting}
              onClick={restartServers}
            >
              {restarting ? "Restarting…" : "Restart App"}
            </button>
            <button
              type="button"
              className="topbar-panel-restore"
              onClick={showWorkspaceChooser}
            >
              Switch Workspace
            </button>
            <button
              type="button"
              className="topbar-panel-restore"
              onClick={() => {
                setResourceBrowserWidth(250);
                setInspectorWidth(310);
                setWorkflowEditorPercent(66.667);
                setWorkflowPaneFocus("editor");
              }}
            >
              Reset layouts
            </button>
            <label className="topbar-theme-switch">
              <span>Theme</span>
              <select
                aria-label="Workbench theme"
                value={theme}
                onChange={(event) =>
                  setTheme(event.target.value as WorkbenchTheme)
                }
              >
                {WORKBENCH_THEMES.map((option) => (
                  <option key={option.id} value={option.id}>
                    {option.label}
                  </option>
                ))}
              </select>
            </label>
          </div>
          <div className="topbar-view-actions" data-stack-scope="view">
            {resourceBrowserWidth <= 36 && (
              <button
                type="button"
                className="topbar-panel-restore"
                onClick={() => setResourceBrowserWidth(250)}
              >
                Restore Resource Browser
              </button>
            )}
            {inspectorWidth <= 36 && (
              <button
                type="button"
                className="topbar-panel-restore"
                onClick={() => setInspectorWidth(310)}
              >
                Restore Documentation
              </button>
            )}
          </div>
        </div>
        <div
          className="shell-panel-controls resource-browser-frame-controls panel-frame-controls"
          role="group"
          aria-label="Resource Browser panel controls"
        >
          <button
            type="button"
            title="Minimize Resource Browser"
            onClick={() => {
              setTakeoverShellPanel(null);
              setResourceBrowserWidth(36);
            }}
          >
            −
          </button>
          <button
            type="button"
            title="Restore Resource Browser"
            onClick={() => {
              setTakeoverShellPanel(null);
              setResourceBrowserWidth(250);
            }}
          >
            *
          </button>
          <button
            type="button"
            title="Display all Resource Browser content"
            onClick={() => {
              setTakeoverShellPanel(null);
              setResourceBrowserWidth(520);
            }}
          >
            +
          </button>
          <button
            type="button"
            title="Resource Browser takes over the middle workspace"
            onClick={() => {
              setResourceBrowserWidth(36);
              setTakeoverShellPanel("resource");
            }}
          >
            [ـ]
          </button>
        </div>
        <div
          className="resource-browser-resizer"
          role="separator"
          aria-label="Resize Resource Browser"
          aria-orientation="vertical"
          aria-valuemin={36}
          aria-valuemax={520}
          aria-valuenow={Math.round(resourceBrowserWidth)}
          tabIndex={0}
          onPointerDown={beginResourceBrowserResize}
          onDoubleClick={() => setResourceBrowserWidth(250)}
        />
        <div
          className="shell-panel-controls documentation-frame-controls panel-frame-controls"
          role="group"
          aria-label="Documentation panel controls"
        >
          <button
            type="button"
            title="Minimize Documentation"
            onClick={() => {
              setTakeoverShellPanel(null);
              setInspectorWidth(36);
            }}
          >
            −
          </button>
          <button
            type="button"
            title="Restore Documentation"
            onClick={() => {
              setTakeoverShellPanel(null);
              setInspectorWidth(310);
            }}
          >
            *
          </button>
          <button
            type="button"
            title="Display all Documentation content"
            onClick={() => {
              setTakeoverShellPanel(null);
              setInspectorWidth(Math.round(window.innerWidth * 0.6));
            }}
          >
            +
          </button>
          <button
            type="button"
            title="Documentation takes over the middle workspace"
            onClick={() => {
              setInspectorWidth(36);
              setTakeoverShellPanel("docs");
            }}
          >
            [ـ]
          </button>
        </div>
        <div
          className="inspector-resizer"
          role="separator"
          aria-label="Resize Documentation"
          aria-orientation="vertical"
          aria-valuemin={36}
          aria-valuemax={Math.round(window.innerWidth * 0.6)}
          aria-valuenow={Math.round(inspectorWidth)}
          tabIndex={0}
          onPointerDown={beginInspectorResize}
          onDoubleClick={() => setInspectorWidth(310)}
        />
        <aside className="inspector">
          <div className="inspector-head">
            <span>{relationshipView ? "DOCUMENTATION" : "LIVE INSPECTOR"}</span>
            <div>
              <span className="live-dot" />{" "}
              {relationshipView ? "shared markdown" : "real data"}
            </div>
          </div>
          {relationshipView ? (
            <Suspense
              fallback={
                <div className="studio-empty">Loading documentation…</div>
              }
            >
              <HelpDocumentTabs
                preferred={
                  view === "goals"
                    ? "goals"
                    : view === "plans"
                      ? "plans"
                      : view === "data"
                        ? "datatypeGuide"
                        : view === "knowledgeData"
                          ? "data"
                          : view === "knowledgeArtifacts"
                            ? "artifacts"
                            : view === "llms"
                          ? "llms"
                          : view === "systems"
                            ? "systems"
                            : view === "operations"
                              ? "operations"
                              : view === "topics"
                                ? "topics"
                              : view === "policies"
                                ? "policies"
                                : view === "modelPolicy"
                                  ? "policies"
                                  : view === "benchmarks"
                                    ? "benchmarks"
                                : view === "contexts"
                                  ? "contexts"
                                  : view === "sourceCode"
                                    ? "sourceCode"
                                    : view === "prompts"
                                      ? "prompts"
                                    : "overview"
                }
                context={
                  view === "goals"
                    ? JSON.stringify(
                        {
                          goalResources: snapshot?.goals?.length || 0,
                          workspace: workspace.id,
                        },
                        null,
                        2,
                      )
                    : view === "plans"
                      ? JSON.stringify(
                          {
                            planningStrategies: snapshot?.plans?.length || 0,
                            workspace: workspace.id,
                          },
                          null,
                          2,
                        )
                      : view === "contexts"
                        ? JSON.stringify(
                            {
                              atomspaceResources: snapshot?.contexts?.length || 0,
                              workspace: workspace.id,
                            },
                            null,
                            2,
                          )
                        : view === "systems"
                          ? JSON.stringify(
                              {
                                systemResources: snapshot?.systems?.length || 0,
                                workspace: workspace.id,
                              },
                              null,
                              2,
                            )
                          : view === "data"
                            ? JSON.stringify(
                                {
                                  datatypes: workspace.datatypeFileCount || 0,
                                  representations:
                                    workspace.representationFileCount || 0,
                                },
                                null,
                                2,
                              )
                            : undefined
                }
              />
            </Suspense>
          ) : selectedStep ? (
            <>
              <div className="inspect-section">
                <div className="section-title">
                  <span>STEP</span>
                  <b>{selectedRuntime?.status || "defined"}</b>
                </div>
                <pre className="mini-code">
                  {jsonValueToMetta({
                    inputs: selectedStep.inputs || {},
                    outputs: selectedStep.outputs || {},
                  })}
                </pre>
              </div>
            </>
          ) : (
            <div className="inspect-section">
              <pre className="mini-code">
                {jsonValueToMetta({
                  id: workspace.id,
                  root: workspace.root,
                  files: snapshot?.files.length || 0,
                })}
              </pre>
            </div>
          )}
        </aside>
      </section>
      <footer>
        <span>
          <i className="online" /> Backend connected
        </span>
        <span>
          {workspace.id === "shared" ? "Shared library" : workspace.id}
        </span>
        <span>
          {workspace.datatypeFileCount || 0} datatypes ·{" "}
          {workspace.representationFileCount || 0} representations
        </span>
        <span>{enabledModelCount} enabled models/presets</span>
        <span>{workspace.promptFileCount || 0} prompts</span>
        <span className="footer-right">filesystem workspace</span>
      </footer>
      <ChatDock onOpenFullPage={() => setView("chat")} />
    </main>
  );
}
