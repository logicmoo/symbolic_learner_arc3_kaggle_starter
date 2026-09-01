import { useCallback, useEffect, useRef, useState, type MouseEvent as ReactMouseEvent, type PointerEvent as ReactPointerEvent, type ReactNode } from "react";
import { pushGlobalStatus } from "../lib/globalStatus";
import { ColoredTagCombobox, type ColoredTagDescription } from "./ColoredTagCombobox";
import { SuperControl } from "./UniversalArtifactEditor";
import { modelCapabilityTags } from "./modelOptionDisplay";
import { RESTART_PENDING_CLEARED_EVENT, RESTART_PENDING_REQUEST_EVENT, usePageProcessActivity } from "../lib/pageProcessActivity";
import "../styles/video_import.css";
import "../styles/video_import_page.css";

/**
 * Video Import v2 — rebuilt from the build prompt in
 * workbench/docs/VIDEO_IMPORT.md (appendix), with the whole design known up
 * front: one typed API layer, one job engine, one stack runner, and a
 * uniform collapsible-section shell for every gallery.
 */

type CaptionCue = { start: number; end: number; text: string; speaker?: string };
type Video = {
  path: string; title: string; duration?: number | null; sizeBytes?: number;
  frameCount?: number; scenes?: Array<{ atSeconds: number }>;
  segments?: Array<{ start: number; end: number; keep: boolean }>;
  lastExtract?: { secondsPerFrame?: number };
  captions?: CaptionCue[];
  captionSource?: string;
};
type Frame = { path: string; index: number; atSeconds?: number; sceneIndex?: number; provenance?: string; characters: string[]; anonymous: number };
type FilterEntry = {
  id: string; title: string; filter: string; description?: string;
  params?: Record<string, unknown>; paramChoices?: Record<string, string[]>;
  lutPath?: string; skillPath?: string; broken?: boolean; excluded?: boolean; votes?: number;
  skill?: boolean; lut?: boolean;
};
type FilterSpec = Record<string, unknown>;
type ChainStep = { entryId: string; params: Record<string, string> };
type JobState = {
  id: string; kind: string; state: "running" | "done" | "error";
  done: number; total: number; elapsedSeconds: number; etaSeconds: number;
  frames?: Array<{ path: string; index: number; atSeconds?: number; sceneIndex?: number; provenance?: string }>;
  markers?: Array<{ atSeconds: number }>;
  gallery?: Array<{ id: string; title: string; path?: string; error?: string; baseId?: string; params?: Record<string, unknown> }>;
  resultPath?: string | null; interrupted?: boolean; error?: string | null; retinters?: string[];
  captions?: CaptionCue[]; captionSource?: string;
};
type GalleryTile = NonNullable<JobState["gallery"]>[number];
type TrailLevel = { label: string; frames: Array<{ original: string; path: string }> };
type Member = {
  framePath: string; frameIndex: number; name: string; cutout: string; box: number[];
  step: number; status: "pending" | "accepted" | "rejected"; probeIndex: number; probeLabel: string;
  route?: MemberExtractionRoute; promptSource?: MemberPromptSource; inputImage?: string; sceneAfter?: string;
  inventoryId?: string; depth?: number; nextPassImage?: string;
  provenance?: string; nextPassProvenance?: string; sceneProvenance?: string;
};
type MemberExtractionRoute = "direct_from_scene" | "from_parent_cutout";
type MemberPromptSource = "baseline" | "llm_rewrite" | "planner" | "outliner";
type MemberExtractionAttempt = {
  route: MemberExtractionRoute;
  promptSource: MemberPromptSource;
  inputImage: string;
  prompt: string;
  status: "extracting" | "extracted" | "accepted" | "rejected" | "not_found" | "failed";
  outputImage?: string;
  error?: string;
};
type MemberInventoryThing = {
  name: string;
  description: string;
  parentName?: string;
  countIndex?: number;
  countTotal?: number;
  visibility?: "visible" | "partially_hidden" | "hidden";
  hiddenReason?: string;
  occludedBy?: string[];
  extractionRoutes?: MemberExtractionRoute[];
  extractionAttempts?: MemberExtractionAttempt[];
  parentReferenceImage?: string;
  promptWriterPrompt?: string;
  promptWriterOutput?: string;
  promptWriterError?: string;
  baselineExtractionPrompt?: string;
  rewrittenExtractionPrompt?: string;
  status: "listed" | "hidden" | "outlining" | "outlined" | "extracting" | "extracted" | "accepted" | "returned" | "not_found" | "failed";
  extractionPrompt?: string;
  outlinePrompt?: string;
  outlineOutput?: string;
  outlineImage?: string;
  outlineDimensions?: { width: number; height: number };
  outlinePolygons?: number[][][];
  outlineHoles?: number[][][];
  outlineBox?: number[];
  outlineError?: string;
  outlineRetryAfter?: number;
  outlineAttempts?: number;
  cutoutInstructions?: string;
  fillInstructions?: Record<string, unknown>;
  inputImage?: string;
  outputImages?: string[];
  error?: string;
  retryAfter?: number;
  attempts?: number;
};
type MemberObjectTreeNode = {
  description: string;
  visibility: "visible" | "partially_hidden" | "hidden";
  hiddenReason?: string;
  occludedBy?: string[];
  countIndex?: number;
  countTotal?: number;
  subObjects: MemberObjectTree;
};
type MemberObjectTree = Record<string, MemberObjectTreeNode>;
type MemberInventory = {
  id: string;
  framePath: string;
  frameIndex: number;
  probeIndex: number;
  probeLabel: string;
  goal?: MemberGoal;
  sourceImage: string;
  sceneDescription: string;
  descriptionPrompt: string;
  descriptionOutput: string;
  modelId: string;
  depth?: number;
  parentInventoryId?: string;
  subjectName?: string;
  describedThings?: MemberInventoryThing[];
  objectsWithSubObjects?: MemberObjectTree;
  decompositionPrompt?: string;
  decompositionOutput?: string;
  decompositionWarning?: string;
  decompositionError?: string;
  orderPrompt?: string;
  orderOutput?: string;
  extractionOrder?: string[];
  orderError?: string;
  retryAfter?: number;
  attempts?: number;
  status: "pending" | "describing" | "prompting" | "decomposing" | "ordering" | "outlining" | "extracting" | "done" | "failed";
  things: MemberInventoryThing[];
};
type ModelChoice = { id: string; name: string; backendId?: string; capabilities?: Record<string, unknown>; inherited?: boolean; origin?: string; enabled: boolean; vision: boolean; imageOutput: boolean };
type MemberGoal = "any" | "faces" | "characters" | "objects" | "text";
type CachedModelResponse = {
  modelId: string;
  prompt: string;
  imagePath: string;
  imageHash: string;
  cachedAt: string;
  payload: Record<string, any>;
};
type TurtleArtifact = {
 sourceImage: string;
 subjectName: string;
 prompt: string;
 rawProgram: string;
 pngPrompt?: string;
 pngProgram?: string;
 programPath?: string;
 renderedImage?: string;
 provenance?: string;
 status: "generating" | "generated" | "drawing" | "rendered" | "failed";
 error?: string;
 failedStage?: "gen" | "png";
 retryAfter?: number;
 attempts?: number;
};
type AltImageZoom = {
  src: string;
  imagePath: string;
  alt: string;
  x: number;
  y: number;
  width: number;
  height: number;
  scale: number;
};
type HoverImageContext = Pick<AltImageZoom, "src" | "imagePath" | "alt" | "x" | "y">;
type WorkflowStageIndicator = {
  label: "D" | "P" | "O" | "E" | "T" | "I";
  value: string;
  state: "waiting" | "active" | "retrying" | "partial" | "complete";
  detail: string;
};
type PipeForkSelections = {
  inventory: "found_objects" | "sub_objects" | "both";
  prompts: "baseline" | "llm_rewrite" | "both";
  routes: "model_planned" | "direct_from_scene" | "from_parent_cutout" | "both";
};
type PipeForkHistoryEntry = {
  runId: string;
  fork: keyof PipeForkSelections;
  label: string;
  selection: string;
  at: string;
  detail: string;
};
type PipeParentView = {
  inventory: "found_objects" | "sub_objects";
  prompts: "baseline" | "llm_rewrite";
  routes: "direct_from_scene" | "from_parent_cutout";
};
type MemberPipelineStage = "hierarchy" | "prompts" | "routes" | "extract";
type RecursiveAutomation = {
  describer: boolean;
  planner: boolean;
  outliner: boolean;
  extractor: boolean;
  turtle: boolean;
  turtlePng: boolean;
  advanceLevels: boolean;
  enlargeSubobjects: boolean;
};
type LlmCallConcurrency = {
  describer: number | null;
  planner: number | null;
  outliner: number | null;
  extractor: number | null;
  turtle: number | null;
  turtlePng: number | null;
};
type LlmCallMetric = { completed: number; totalDurationMs: number };
type LlmCallMetrics = Record<keyof LlmCallConcurrency, LlmCallMetric>;
type PromptSelection = "workspace" | "default";
const hasAlignedOutline = (thing: MemberInventoryThing) => Boolean(
  (thing.outlinePolygons?.length || thing.outlineBox?.length === 4)
  && thing.outlineImage
  && thing.outlineDimensions?.width
  && thing.outlineDimensions?.height
);

const API = "/workbench/video-import";
const MAX_RECURSIVE_OBJECT_DEPTH = 9;
const LLM_RETRY_DELAY_MS = 1000;
const DEFAULT_RECURSIVE_AUTOMATION: RecursiveAutomation = {
  describer: true,
  planner: true,
  outliner: true,
  extractor: true,
  turtle: true,
  turtlePng: true,
  advanceLevels: true,
  enlargeSubobjects: true,
};
const DEFAULT_LLM_CALL_CONCURRENCY: LlmCallConcurrency = {
  describer: null,
  planner: null,
  outliner: null,
  extractor: null,
  turtle: null,
  turtlePng: null,
};
const emptyLlmCallMetrics = (): LlmCallMetrics => ({
  describer: { completed: 0, totalDurationMs: 0 },
  planner: { completed: 0, totalDurationMs: 0 },
  outliner: { completed: 0, totalDurationMs: 0 },
  extractor: { completed: 0, totalDurationMs: 0 },
  turtle: { completed: 0, totalDurationMs: 0 },
  turtlePng: { completed: 0, totalDurationMs: 0 },
});
const formatJobDuration = (durationMs: number) => {
  if (!Number.isFinite(durationMs) || durationMs <= 0) return "—";
  if (durationMs < 1000) return `${Math.round(durationMs)}ms`;
  if (durationMs < 60_000) return `${(durationMs / 1000).toFixed(1)}s`;
  return `${Math.floor(durationMs / 60_000)}m ${Math.round((durationMs % 60_000) / 1000)}s`;
};
const DEFAULT_PIPE_FORKS: PipeForkSelections = {
  inventory: "both",
  prompts: "llm_rewrite",
  routes: "model_planned",
};
const DEFAULT_PIPE_PARENT_VIEW: PipeParentView = {
  inventory: "found_objects",
  prompts: "llm_rewrite",
  routes: "direct_from_scene",
};
const PIPE_FORK_TITLES: Record<keyof PipeForkSelections, string> = {
  inventory: "Object inventory scope",
  prompts: "Extraction prompt source",
  routes: "Extraction image route",
};
const PIPE_FORK_OPTIONS: Record<keyof PipeForkSelections, Array<{ value: string; label: string; detail: string }>> = {
  inventory: [
    { value: "found_objects", label: "Found objects", detail: "Top-level roots only" },
    { value: "sub_objects", label: "Sub-object keys", detail: "Decomposed parts only" },
    { value: "both", label: "Both", detail: "Roots and sub-objects" },
  ],
  prompts: [
    { value: "baseline", label: "Baseline", detail: "Prepared extraction prompt" },
    { value: "llm_rewrite", label: "LLM rewrite", detail: "Model-written prompt" },
    { value: "both", label: "Both", detail: "Try both prompt variants" },
  ],
  routes: [
    { value: "model_planned", label: "Model planned", detail: "Use the ordering model's route" },
    { value: "direct_from_scene", label: "Direct", detail: "Progressively reduced scene" },
    { value: "from_parent_cutout", label: "Parent cutout", detail: "Search inside intact parent" },
    { value: "both", label: "Both", detail: "Try both image routes" },
  ],
};
const PIPE_PATHS: PipeForkSelections[] = (["found_objects", "sub_objects", "both"] as const).flatMap((inventory) =>
  (["baseline", "llm_rewrite", "both"] as const).flatMap((prompts) =>
    (["model_planned", "direct_from_scene", "from_parent_cutout", "both"] as const).map((routes) => ({ inventory, prompts, routes })),
  ),
);
const restorePipeForkSelection = <K extends keyof PipeForkSelections>(
  selections: PipeForkSelections,
  fork: K,
  rawValue: unknown,
) => {
  const value = String(rawValue || "");
  if (PIPE_FORK_OPTIONS[fork].some((option) => option.value === value)) {
    selections[fork] = value as PipeForkSelections[K];
  }
};
const DEFAULT_MEMBER_DESCRIPTION_PROMPT = [
  "SCENE OBJECTS TEXTUAL DESCRIPTION.",
  "{{subjectContext}}",
  "Describe this image, then list only its direct visually separable child objects.",
  "{{goal}}",
  "List every distinct extractable thing you can identify. Do not return polygons or coordinates in this stage.",
  "{{alreadyExtracted}}",
  "Answer ONLY with JSON: {\"description\":\"scene description\",\"things\":[{\"name\":\"short unique name\",\"description\":\"visual identity and location\"}]}",
].join("\n");
const DEFAULT_OBJECT_PROMPT_WRITER = [
  "OBJECT EXTRACTION PROMPT WRITER.",
  "Write a better, precise visual-localization prompt for extracting the named object from the attached image.",
  "Use its appearance, location, parent relationship, boundaries, overlaps, and the scene context to distinguish it from its own sub-objects, neighboring objects, and background.",
  "The prompt must work when the attached extraction image is either the full scene or an independently extracted image of the object's parent.",
  "The generated prompt must tell a vision model to return ONLY {\"name\":\"exact name\",\"polygon\":[[x,y],...]} with 3-20 pixel-coordinate points, allow box only when polygon is impossible, and return exactly NONE when the object is not visible.",
  "Do not perform the extraction now. Return the complete ready-to-run prompt as JSON.",
  "TEXTUAL DESCRIPTION:",
  "{{textualDescription}}",
  "OBJECT NAME: {{objectName}}",
  "OBJECT DESCRIPTION: {{objectDescription}}",
  "PARENT OBJECT: {{parentName}}",
  "VISIBILITY: {{visibility}}",
  "Answer ONLY with JSON: {\"name\":\"{{objectName}}\",\"extraction_prompt\":\"complete ready-to-run extraction prompt\"}",
].join("\n");
const DEFAULT_MEMBER_DECOMPOSITION_PROMPT = [
  "OBJECTS_WITH_SUB_OBJECTS.",
  "Refine the listed objects into a hierarchical inventory of visible, independently localizable things in the attached image.",
  "Keep every original object. Add meaningful visible sub-objects recursively when they can be named, counted, localized, or extracted separately.",
  "Examples include a face's two eyes, nose, mouth, ears, and hair; a car's individual wheels, doors, windows, lights, and mirrors; clothing bows, buttons, gloves on hands, and a reflection visible in a mirror.",
  "Represent repeated countable parts as separate keyed entries with distinct globally unique names, countIndex, and countTotal. Use left/right/front/rear when visible; otherwise use stable numeric suffixes.",
  "Create each sub-object as a key inside its immediate parent's sub_objects object. A sub-object may itself own another sub_objects object.",
  "Sometimes point out a strongly implied but fully hidden part that matters to the parent or count (for example an occluded second wheel). Mark it visibility \"hidden\", explain hidden_reason, and name occluded_by. Never present an inferred hidden part as visible.",
  "Use visibility \"partially_hidden\" for a localized part that is only partly occluded. Do not invent unsupported parts, microscopic detail, arbitrary color patches, or duplicate aliases. Stop when a smaller part is not independently meaningful.",
  "TEXTUAL DESCRIPTION:",
  "{{textualDescription}}",
  "FOUND OBJECTS:",
  "{{objects}}",
  "Answer ONLY with JSON whose top-level key is objects_with_sub_objects. Use this recursive shape:",
  "{\"objects_with_sub_objects\":{\"face\":{\"description\":\"visible face and location\",\"visibility\":\"visible\",\"sub_objects\":{\"left_eye\":{\"description\":\"visible left eye\",\"visibility\":\"visible\",\"countIndex\":1,\"countTotal\":2,\"sub_objects\":{}},\"right_eye\":{\"description\":\"right eye hidden by hair\",\"visibility\":\"hidden\",\"hidden_reason\":\"occluded by hair\",\"occluded_by\":[\"hair\"],\"countIndex\":2,\"countTotal\":2,\"sub_objects\":{}}}}}}",
].join("\n");
const DEFAULT_MEMBER_ORDER_PROMPT = [
  "OBJECT EXTRACTION PLANNER.",
  "Use the textual description and attached image to order extraction of every listed direct child object.",
  "Always remove every sub-object before its parent object so removing a whole does not erase parts that still need extraction.",
  "Remove foreground objects that cover or overlap other objects first. Remove the farthest background objects last.",
  "Use every object name exactly once.",
  "Do not outline objects and do not return polygons, coordinates, masks, or cutout instructions. Outliner handles that separately, one object at a time.",
  "TEXTUAL DESCRIPTION:",
  "{{textualDescription}}",
  "OBJECTS:",
  "{{objects}}",
  "Answer ONLY with JSON: {\"order\":[\"exact object name\",...],\"reasoning\":[\"why this order\",...]}",
].join("\n");
const DEFAULT_MEMBER_OUTLINER_PROMPT = [
  "OBJECT OUTLINER.",
  "Outline exactly ONE object in the attached current scene. Planner has already selected its order position.",
  "Do not outline, include, or remove any other listed object.",
  "TEXTUAL DESCRIPTION:",
  "{{textualDescription}}",
  "PLANNER-SELECTED OBJECT: {{nextObjectName}}",
  "Object description: {{nextObjectDescription}}",
  "Planner position: {{plannerPosition}} of {{plannerTotal}}",
  "OUTLINE SOURCE IMAGE: {{outlineImage}}",
  "PIXEL COORDINATE SPACE: width={{imageWidth}}, height={{imageHeight}}. Use x=0..{{maxX}} and y=0..{{maxY}} only.",
  "Trace the named object's visible silhouette at pixel-edge precision in THIS current image.",
  "Explicitly include only pixels belonging to the named object and exclude adjacent body parts, neighboring objects, shadows, and background.",
  "Preserve disconnected visible parts as separate polygons and enclosed transparent gaps as holes. Respect occluders: trace only the visible contour and never invent hidden pixels.",
  "For parts such as a character's chest, exclude the head, arms, hands, lower body, clothing outside the chest, and background unless truly part of the named object.",
  "Also describe the contour clockwise and as normalized 0..1000 move/line commands in Turtle form for inspection.",
  "Answer ONLY with JSON: {\"name\":\"{{nextObjectName}}\",\"polygons\":[[[x,y],...]],\"holes\":[[[x,y],...]],\"traceClockwise\":[\"start at ...\",\"follow edge ...\",\"return to start\"],\"traceTurtle\":[{\"op\":\"move\",\"x\":0,\"y\":0},{\"op\":\"line\",\"x\":0,\"y\":0}],\"occlusion\":\"...\"} using pixel coordinates in THIS current image.",
  "Use polygon only as a compatibility fallback for one connected part. Use box only for a genuinely rectangular object with exact rectangular boundaries.",
  "If this exact object is no longer visible, answer exactly: NONE",
].join("\n");
const DEFAULT_RECURSIVE_EXTRACTOR_PROMPT = [
  "SCENE OBJECT EXTRACTION AND BACKGROUND RECONSTRUCTION.",
  "Remove exactly ONE object from the attached current image using the exact geometry already produced by Outliner.",
  "TEXTUAL DESCRIPTION:",
  "{{textualDescription}}",
  "PLANNER-SELECTED NEXT OBJECT: {{nextObjectName}}",
  "Object description: {{nextObjectDescription}}",
  "Planner position: {{plannerPosition}} of {{plannerTotal}}",
  "OUTLINER RESULT:",
  "{{outline}}",
  "Do not change the extraction order or outline another object. Outliner owns contour geometry; Extractor owns removal and reconstruction.",
  "Describe what visually continues BEHIND the outlined object: background colors, gradients, lines, texture, and which surrounding edges should continue through the hole.",
  "Answer ONLY with JSON: {\"name\":\"{{nextObjectName}}\",\"backgroundFill\":{\"description\":\"...\",\"colors\":[\"#RRGGBB\"],\"continueEdges\":[\"...\"],\"texture\":\"...\"}}.",
].join("\n");
const DEFAULT_TURTLE_PROMPT = [
  "TURTLE LEAF RENDERER.",
  "The attached image is the terminal object {{subjectName}}. Its recursive Describer found no further sub-objects.",
  "Object description: {{description}}",
  "Write a constrained turtle drawing program that reconstructs this one object.",
  "Use normalized coordinates from 0 to 1000 with origin at the top-left.",
  "Allowed commands: pen, move, line, polyline, polygon, rectangle, ellipse, dot.",
  "Use transparent background unless the object itself requires a background. Use at most 100 commands.",
  "Answer ONLY with JSON: {\"version\":1,\"background\":\"transparent\",\"penColor\":\"#RRGGBB\",\"penWidth\":4,\"commands\":[{\"op\":\"move\",\"x\":0,\"y\":0},...]}",
].join("\n");
const DEFAULT_TURTLE_PNG_PROMPT = [
  "TURTLE PNG DRAW STEP.",
  "The attached image is terminal object {{subjectName}}.",
  "Object description: {{description}}",
  "Review the draft Turtle program below and return the final drawing program that should be rendered to PNG.",
  "Preserve accurate silhouette, colors, holes, and visible internal details. Coordinates are normalized from 0 to 1000 with top-left origin.",
  "Allowed commands: pen, move, line, polyline, polygon, rectangle, ellipse, dot. Use at most 200 commands.",
  "DRAFT TURTLE PROGRAM:",
  "{{draftProgram}}",
  "Answer ONLY with the final JSON object. Do not include Markdown or Python.",
].join("\n");
const renderTurtlePrompt = (template: string, subjectName: string, description: string) => template
  .replaceAll("{{subjectName}}", subjectName)
  .replaceAll("{{description}}", description || "No additional description.");
const renderTurtlePngPrompt = (template: string, subjectName: string, description: string, draftProgram: string) => template
  .replaceAll("{{subjectName}}", subjectName)
  .replaceAll("{{description}}", description || "No additional description.")
  .replaceAll("{{draftProgram}}", draftProgram);
async function runConcurrent<T>(items: T[], concurrency: number, worker: (item: T) => Promise<void>): Promise<void> {
  let cursor = 0;
  const runners = Array.from({ length: Math.min(Math.max(1, concurrency), items.length) }, async () => {
    while (cursor < items.length) {
      const item = items[cursor];
      cursor += 1;
      await worker(item);
    }
  });
  await Promise.all(runners);
}
function cooperativeRetryOrder<T>(items: T[], concurrency: number, isRetry: (item: T) => boolean): T[] {
  const retries = items.filter(isRetry);
  const fresh = items.filter((item) => !isRetry(item));
  const retryReserve = Math.min(2, concurrency, retries.length);
  const freshInitial = Math.min(fresh.length, Math.max(0, concurrency - retryReserve));
  return [
    ...fresh.slice(0, freshInitial),
    ...retries.slice(0, retryReserve),
    ...fresh.slice(freshInitial),
    ...retries.slice(retryReserve),
  ];
}
const MEMBER_INVENTORY_GOALS: Record<MemberGoal, string> = {
  any: "List distinct extractable people, characters, creatures, objects, and text/sign elements.",
  faces: "List each distinct extractable face.",
  characters: "List each distinct extractable person, character, or creature.",
  objects: "List each distinct extractable inanimate object.",
  text: "List each distinct extractable piece of text or signage.",
};
const renderMemberDescriptionPrompt = (template: string, goal: MemberGoal, known: string[], subjectContext = "This is a root input image. List its top-level objects.") => template
  .replaceAll("{{subjectContext}}", subjectContext)
  .replaceAll("{{goal}}", MEMBER_INVENTORY_GOALS[goal])
  .replaceAll("{{alreadyExtracted}}", known.length ? `Do not list things already extracted: ${known.join(", ")}.` : "No things have been extracted yet.");
const renderMemberExtractionPrompt = (textualDescription: string, name: string, description: string) => [
  "SCENE OBJECT VISUAL EXTRACTION.",
  "Use the saved scene-objects textual description together with the attached current image.",
  `SCENE OBJECTS TEXTUAL DESCRIPTION:\n${textualDescription}`,
  `Locate ONLY this listed thing: ${name}.`,
  `Inventory description: ${description || name}.`,
  "Answer ONLY with JSON like {\"name\":\"short name\",\"polygon\":[[x,y],...]} using 3-20 pixel-coordinate points in THIS current image.",
  "A box [x0,y0,x1,y1] is allowed only when a polygon is not possible.",
  "If this exact listed thing is no longer visible, answer exactly: NONE",
].join("\n");
const renderObjectPromptWriter = (template: string, textualDescription: string, thing: MemberInventoryThing) => template
  .replaceAll("{{textualDescription}}", textualDescription)
  .replaceAll("{{objectName}}", thing.name)
  .replaceAll("{{objectDescription}}", thing.description)
  .replaceAll("{{parentName}}", thing.parentName || "none (root object)")
  .replaceAll("{{visibility}}", thing.visibility || "visible");
const renderMemberDecompositionPrompt = (template: string, textualDescription: string, things: MemberInventoryThing[]) => template
  .replaceAll("{{textualDescription}}", textualDescription)
  .replaceAll("{{objects}}", things.map((thing) => `- ${thing.name}: ${thing.description}`).join("\n"));
const renderMemberOrderPrompt = (template: string, textualDescription: string, things: MemberInventoryThing[]) => template
  .replaceAll("{{textualDescription}}", textualDescription)
  .replaceAll("{{objects}}", things.map((thing) => {
    const relation = thing.parentName ? ` [part of ${thing.parentName}]` : " [root object]";
    const count = thing.countTotal ? ` [${thing.countIndex || "?"} of ${thing.countTotal}]` : "";
    return `- ${thing.name}${relation}${count}: ${thing.description}`;
  }).join("\n"));
const renderMemberOutlinerPrompt = (
  template: string,
  textualDescription: string,
  thing: MemberInventoryThing,
  position: number,
  total: number,
  outlineImage: string,
  dimensions: { width: number; height: number },
) => template
  .replaceAll("{{textualDescription}}", textualDescription)
  .replaceAll("{{nextObjectName}}", thing.name)
  .replaceAll("{{nextObjectDescription}}", thing.description)
  .replaceAll("{{plannerPosition}}", String(position))
  .replaceAll("{{plannerTotal}}", String(total))
  .replaceAll("{{outlineImage}}", outlineImage)
  .replaceAll("{{imageWidth}}", String(dimensions.width))
  .replaceAll("{{imageHeight}}", String(dimensions.height))
  .replaceAll("{{maxX}}", String(Math.max(0, dimensions.width - 1)))
  .replaceAll("{{maxY}}", String(Math.max(0, dimensions.height - 1)));
const imageDataDimensions = (source: string) => new Promise<{ width: number; height: number }>((resolve, reject) => {
  const image = new Image();
  image.onload = () => resolve({ width: image.naturalWidth, height: image.naturalHeight });
  image.onerror = () => reject(new Error("could not decode Outliner input dimensions"));
  image.src = source;
});
const renderSharedExtractorPrompt = (template: string, textualDescription: string, thing: MemberInventoryThing, position: number, total: number) => template
  .replaceAll("{{textualDescription}}", textualDescription)
  .replaceAll("{{nextObjectName}}", thing.name)
  .replaceAll("{{nextObjectDescription}}", thing.description)
  .replaceAll("{{outline}}", thing.outlineOutput || thing.cutoutInstructions || "Outliner result is unavailable.")
  .replaceAll("{{cutoutInstructions}}", thing.outlineOutput || thing.cutoutInstructions || "Outliner result is unavailable.")
  .replaceAll("{{plannerPosition}}", String(position))
  .replaceAll("{{plannerTotal}}", String(total));
const normalizeMemberPromptLabels = (value: string) => value
  .replaceAll("STAGE 1 — SCENE INVENTORY.", "SCENE OBJECTS TEXTUAL DESCRIPTION.")
  .replaceAll("STAGE 2 — EXTRACT ONE INVENTORIED THING.", "SCENE OBJECT VISUAL EXTRACTION.")
  .replaceAll("Use the saved Stage 1 textual description", "Use the saved scene-objects textual description")
  .replaceAll("STAGE 1 TEXTUAL OUTPUT:", "SCENE OBJECTS TEXTUAL DESCRIPTION:");
const preferenceSourceLabel = (source: string) => source.replaceAll("_", " ") || "workspace policy";
const MODEL_CAPABILITY_COLORS: Record<string, string> = {
  multimodal: "#c88ce0",
  vision: "#52c7d9",
  "image output": "#ff8bd1",
  summary: "#91c46c",
  audio: "#f3b75d",
  reasoning: "#b79cff",
  tools: "#58d2a9",
  code: "#73a7ff",
  json: "#e3ca63",
  text: "#a8bbc5",
  preferred: "#55e6a5",
  inherited: "#d39bff",
  unavailable: "#d98c8c",
  "no vision": "#e0a458",
  "no audio": "#d98c8c",
};
const videoModelDescription = (
  model: ModelChoice | undefined,
  fallbackId: string,
  effectiveModelId: string,
  preferenceSource: string,
  requiredCapability: "vision" | "audio" = "vision",
): ColoredTagDescription => {
  if (!model) return {
    label: fallbackId,
    groupKey: "unavailable",
    groupLabel: "Unavailable saved selection",
    tags: [{ text: "unavailable", color: MODEL_CAPABILITY_COLORS.unavailable }],
  };
  const tags = modelCapabilityTags({ id: model.id, label: model.name, capabilities: model.capabilities })
    .map((text) => ({ text, color: MODEL_CAPABILITY_COLORS[text] || "#8aa" }));
  if (model.id === effectiveModelId) tags.unshift({ text: "preferred", color: MODEL_CAPABILITY_COLORS.preferred });
  if (model.inherited) tags.push({ text: "inherited", color: MODEL_CAPABILITY_COLORS.inherited });
  if (!model.enabled) tags.push({ text: "unavailable", color: MODEL_CAPABILITY_COLORS.unavailable });
  const compatible = requiredCapability === "audio" ? model.capabilities?.audio === true : model.vision;
  if (model.enabled && !compatible) tags.push({ text: requiredCapability === "audio" ? "no audio" : "no vision", color: MODEL_CAPABILITY_COLORS[requiredCapability === "audio" ? "no audio" : "no vision"] });
  return {
    label: model.name,
    groupKey: model.backendId || model.origin || "models",
    groupLabel: `${model.backendId || model.origin || "Models"}${model.id === effectiveModelId ? ` · preferred by ${preferenceSourceLabel(preferenceSource)}` : ""}`,
    tags,
    disabled: !model.enabled || !compatible,
  };
};
const automaticVideoModelId = (models: ModelChoice[], effectiveModelId: string) => {
  const runnable = models.filter((model) => model.enabled && model.vision);
  const opus48 = runnable.find((model) => /(?:claude[\s/_-]*)?opus[\s/_-]*4[._-]?8/i.test(`${model.id} ${model.name}`));
  if (opus48) return opus48.id;
  return runnable.some((model) => model.id === effectiveModelId) ? effectiveModelId : runnable[0]?.id || "";
};
const automaticImageOutputModelId = (models: ModelChoice[], preferredModelId: string) => {
  const runnable = models.filter((model) => model.enabled && model.imageOutput);
  if (runnable.some((model) => model.id === preferredModelId)) return preferredModelId;
  return runnable.find((model) => /gpt[-_.\s]*5[._-]?3[-_.\s]*codex/i.test(`${model.id} ${model.name}`))?.id
    || runnable[0]?.id
    || "";
};
const automaticAudioModelId = (models: ModelChoice[], preferredModelId: string) => {
  const runnable = models.filter((model) => model.enabled && model.capabilities?.audio === true);
  if (runnable.some((model) => model.id === preferredModelId)) return preferredModelId;
  return runnable.find((model) => /gpt[-_.\s]*4o[-_.\s]*audio/i.test(`${model.id} ${model.name}`))?.id
    || runnable[0]?.id
    || "";
};
const responseCacheHash = (value: string) => {
  let hash = 2166136261;
  for (let index = 0; index < value.length; index++) {
    hash ^= value.charCodeAt(index);
    hash = Math.imul(hash, 16777619);
  }
  return (hash >>> 0).toString(16).padStart(8, "0");
};
const formatDetectedJson = (value: string): { text: string; detected: boolean } => {
  const raw = value.trim();
  if (!raw) return { text: "", detected: false };
  const unfenced = raw.replace(/^```(?:json)?\s*/i, "").replace(/\s*```$/i, "").trim();
  const candidate = unfenced.match(/(?:\{[\s\S]*\}|\[[\s\S]*\])/)?.[0] || unfenced;
  try {
    return { text: JSON.stringify(JSON.parse(candidate), null, 2), detected: true };
  } catch {
    return { text: value, detected: false };
  }
};
const parseMemberDescriptionOutput = (raw: string): { sceneDescription: string; things: MemberInventoryThing[] } => {
  const formatted = formatDetectedJson(raw);
  if (!formatted.detected) return { sceneDescription: raw, things: [] };
  const parsed = JSON.parse(formatted.text) as Record<string, unknown>;
  const sceneDescription = String(parsed.description || parsed.scene || "").trim();
  const seen = new Set<string>();
  const things = (Array.isArray(parsed.things) ? parsed.things : []).map((thing) => {
    const value = typeof thing === "string" ? { name: thing, description: thing } : thing as Record<string, unknown>;
    const name = String(value?.name || "").trim().slice(0, 60);
    const description = String(value?.description || value?.details || value?.name || "").trim().slice(0, 320);
    return {
      name,
      description,
      status: "listed" as const,
    };
  }).filter((thing) => {
    const key = thing.name.toLowerCase();
    if (!key || seen.has(key)) return false;
    seen.add(key);
    return true;
  });
  return { sceneDescription, things };
};
const normalizeMemberObjectTree = (value: unknown, depth = 0): MemberObjectTree => {
  if (!value || typeof value !== "object" || Array.isArray(value) || depth > 8) return {};
  const result: MemberObjectTree = {};
  for (const [rawName, rawNode] of Object.entries(value as Record<string, unknown>)) {
    const name = rawName.trim().slice(0, 60);
    if (!name || !rawNode || typeof rawNode !== "object" || Array.isArray(rawNode)) continue;
    const node = rawNode as Record<string, unknown>;
    const visibilityValue = String(node.visibility || "visible").toLowerCase().replaceAll(" ", "_");
    const visibility: MemberObjectTreeNode["visibility"] = visibilityValue === "hidden"
      ? "hidden"
      : visibilityValue === "partially_hidden" || visibilityValue === "partial"
        ? "partially_hidden"
        : "visible";
    const countIndex = Number(node.countIndex ?? node.count_index);
    const countTotal = Number(node.countTotal ?? node.count_total);
    const occludedByValue = node.occludedBy ?? node.occluded_by;
    result[name] = {
      description: String(node.description || node.details || name).trim().slice(0, 320),
      visibility,
      hiddenReason: String(node.hiddenReason || node.hidden_reason || "").trim().slice(0, 240) || undefined,
      occludedBy: Array.isArray(occludedByValue) ? occludedByValue.map(String).map((item) => item.trim()).filter(Boolean).slice(0, 12) : undefined,
      countIndex: Number.isInteger(countIndex) && countIndex > 0 ? countIndex : undefined,
      countTotal: Number.isInteger(countTotal) && countTotal > 1 ? countTotal : undefined,
      subObjects: normalizeMemberObjectTree(node.subObjects ?? node.sub_objects ?? {}, depth + 1),
    };
  }
  return result;
};
const flattenMemberObjectTree = (tree: MemberObjectTree, parentName?: string): MemberInventoryThing[] =>
  Object.entries(tree).flatMap(([name, node]) => [
    {
      name,
      description: node.description,
      parentName,
      countIndex: node.countIndex,
      countTotal: node.countTotal,
      visibility: node.visibility,
      hiddenReason: node.hiddenReason,
      occludedBy: node.occludedBy,
      status: node.visibility === "hidden" ? "hidden" as const : "listed" as const,
    },
    ...flattenMemberObjectTree(node.subObjects, name),
  ]);

async function api(path: string, body?: unknown): Promise<Record<string, any>> {
  const response = await fetch(path.startsWith("/") ? path : `${API}/${path}`, body === undefined
    ? { headers: { "content-type": "application/json" } }
    : { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(body) });
  const text = await response.text();
  const payload = text ? JSON.parse(text) : {};
  if (!response.ok) {
    const detail = payload.detail;
    const message = typeof detail === "string" ? detail : detail?.message || (detail ? JSON.stringify(detail) : response.statusText);
    throw new Error(String(message));
  }
  return payload;
}

const seconds = (value?: number | null) => {
  if (!value || !Number.isFinite(value)) return "?";
  const total = Math.round(value);
  return total >= 60 ? `${Math.floor(total / 60)}m${String(total % 60).padStart(2, "0")}s` : `${total}s`;
};

function PipeFork({ fork, title, value, disabled, onChange }: {
  fork: keyof PipeForkSelections;
  title: string;
  value: string;
  disabled: boolean;
  onChange: (value: string) => void;
}) {
  return (
    <div className="video-import-pipe-fork" data-pipe-fork={fork}>
      <div className="video-import-pipe-stem"><span /><b>{title}</b></div>
      <div className="video-import-pipe-branches">
        {PIPE_FORK_OPTIONS[fork].map((option) => (
          <button
            type="button"
            key={option.value}
            className={value === option.value ? "is-selected" : ""}
            aria-pressed={value === option.value}
            disabled={disabled}
            onClick={() => onChange(option.value)}
          >
            <span>{option.label}</span>
            <small>{option.detail}</small>
          </button>
        ))}
      </div>
    </div>
  );
}

function RecursiveInventoryTreeNode({ inventory, inventories, selectedId, level = 0, onSelect }: {
  inventory: MemberInventory;
  inventories: MemberInventory[];
  selectedId: string;
  level?: number;
  onSelect: (inventory: MemberInventory) => void;
}) {
  const children = inventories.filter((candidate) => candidate.parentInventoryId === inventory.id);
  const described = Boolean(inventory.descriptionOutput);
  const planned = Boolean(inventory.orderOutput) || (described && inventory.things.length === 0);
  const outlined = inventory.things.filter(hasAlignedOutline).length;
  const extracted = inventory.things.filter((thing) => thing.outputImages?.length).length;
  const stoppedThings = inventory.things.filter((thing) => thing.status === "not_found" || thing.status === "failed");
  return (
    <li className="video-import-recursive-tree-node">
      <button type="button" className={selectedId === inventory.id ? "is-selected" : ""} onClick={() => onSelect(inventory)}>
        <i />
        <span>
          <b>{inventory.subjectName || `input image #${inventory.frameIndex}`}</b>
          <small>D {described ? "✓" : "·"} · P {planned ? "✓" : "·"} · O {outlined}/{inventory.things.length} · E {extracted}/{inventory.things.length}</small>
        </span>
      </button>
      {children.length > 0 ? (
        <ul>{children.map((child) => <RecursiveInventoryTreeNode key={child.id} inventory={child} inventories={inventories} selectedId={selectedId} level={level + 1} onSelect={onSelect} />)}</ul>
      ) : stoppedThings.length === 0 ? (
        <div className="video-import-recursive-tree-leaf"><i /><span>TURTLE</span></div>
      ) : null}
      {stoppedThings.map((thing) => <div className="video-import-recursive-tree-leaf is-stopped" key={`stopped:${thing.name}`}><i /><span>{thing.name} · EXTRACTOR STOP</span></div>)}
    </li>
  );
}

function WorkflowGalleryPanel({ title, open, onOpenChange, onClear, children }: {
  title: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onClear?: () => void;
  children: ReactNode;
}) {
  return (
    <details className="video-import-workflow-gallery-panel" open={open} onToggle={(event) => onOpenChange(event.currentTarget.open)}>
      <summary><span>{title}</span>{onClear && <button type="button" onClick={(event) => { event.preventDefault(); event.stopPropagation(); onClear(); }}>× Clear</button>}</summary>
      <div>{children}</div>
    </details>
  );
}

function WorkflowGalleryItem({ src, alt, caption, selected, onSelectedChange, showCheckbox = false, stageIndicators }: {
  src: string;
  alt: string;
  caption: string;
  selected: boolean;
  onSelectedChange?: (selected: boolean) => void;
  showCheckbox?: boolean;
  stageIndicators?: WorkflowStageIndicator[];
}) {
  const toggle = () => onSelectedChange?.(!selected);
  return (
    <figure
      className={selected ? "is-selected" : ""}
      role={onSelectedChange ? "checkbox" : undefined}
      aria-checked={onSelectedChange ? selected : undefined}
      tabIndex={onSelectedChange ? 0 : undefined}
      title="Click for popup · Ctrl-click to select or unselect"
      onClick={onSelectedChange ? (event) => {
        if (event.ctrlKey) toggle();
      } : undefined}
      onKeyDown={(event) => {
        if (!onSelectedChange) return;
        if (event.key !== "Enter" && event.key !== " ") return;
        if (!event.ctrlKey) return;
        event.preventDefault();
        toggle();
      }}
    >
      {showCheckbox && onSelectedChange && <label className="video-import-workflow-gallery-check" onClick={(event) => event.stopPropagation()}>
        <input type="checkbox" checked={selected} onChange={(event) => onSelectedChange(event.target.checked)} />
        <span>select</span>
      </label>}
      <img src={src} alt={alt} />
      {stageIndicators?.length ? (
        <div className="video-import-gallery-stage-strip" aria-label="Recursive workflow progress">
          {stageIndicators.map((indicator) => (
            <span key={indicator.label} className={`is-${indicator.state}`} title={`${indicator.label} · ${indicator.detail}`}>
              <b>{indicator.label}</b><small>{indicator.value}</small>
            </span>
          ))}
        </div>
      ) : null}
      <figcaption>{caption}</figcaption>
    </figure>
  );
}

/** Uniform collapsible section: header, meta, pin, auto-collapse on scroll-away. */
function Section({ id, title, meta, extra, open, pinned, autoCollapse, onToggle, onAutoCollapse, onPin, children }: {
  id: string; title: string; meta?: string; extra?: ReactNode;
  open: boolean; pinned: boolean; autoCollapse: boolean;
  onToggle: () => void; onAutoCollapse: () => void; onPin: () => void; children: ReactNode;
}) {
  const ref = useRef<HTMLElement | null>(null);
  const seen = useRef(false);
  const timer = useRef(0);
  const collapse = useRef(onAutoCollapse);
  collapse.current = onAutoCollapse;
  useEffect(() => {
    const element = ref.current;
    if (!element || !open || !autoCollapse || pinned) return undefined;
    seen.current = false;
    const observer = new IntersectionObserver((entries) => {
      if (entries[0].isIntersecting) { seen.current = true; window.clearTimeout(timer.current); }
      else if (seen.current) { window.clearTimeout(timer.current); timer.current = window.setTimeout(() => collapse.current(), 1200); }
    });
    observer.observe(element);
    return () => { observer.disconnect(); window.clearTimeout(timer.current); };
  }, [open, autoCollapse, pinned]);
  return (
    <section ref={ref} className={`vi2-section${open ? "" : " is-collapsed"}`} data-section={id}>
      <div className="vi2-section-head">
        <button className="vi2-section-toggle" onClick={onToggle}>{open ? "▾" : "▸"} <b>{title}</b></button>
        {meta && <small>{meta}</small>}
        <button className={`vi2-section-pin${pinned ? " is-pinned" : ""}`} title={pinned ? "Unpin" : "Pin: never auto-collapse"} onClick={onPin}>📌</button>
        {extra}
      </div>
      {open && children}
    </section>
  );
}

export type VideoImportChainSummaryStep = { index: number; label: string; detail: string };

export function VideoImportPage({
  workspaceId,
  onChainSummaryChange,
}: {
  workspaceId: string;
  /** Fires whenever the built-up chain changes, so a host page can render a
   * live "what we've built so far" summary elsewhere (e.g. the right-side
   * panel) without needing to lift the whole chain/filters state up. */
  onChainSummaryChange?: (steps: VideoImportChainSummaryStep[]) => void;
}) {
  const hoveredImageRef = useRef<HTMLImageElement | null>(null);
  const [altImageZoom, setAltImageZoom] = useState<AltImageZoom | null>(null);
  const [pinnedAltImageZoom, setPinnedAltImageZoom] = useState<AltImageZoom | null>(null);
  const [hoverImageContext, setHoverImageContext] = useState<HoverImageContext | null>(null);
  const [pinnedImageContext, setPinnedImageContext] = useState<HoverImageContext | null>(null);
  const imageProvenanceCacheRef = useRef<Record<string, Record<string, unknown>>>({});
  const [activeImageProvenance, setActiveImageProvenance] = useState<Record<string, unknown> | null>(null);
  const imageElementContext = (image: HTMLImageElement) => {
    const rect = image.getBoundingClientRect();
    let imagePath = "";
    try { imagePath = new URL(image.currentSrc, window.location.href).searchParams.get("path") || ""; }
    catch { /* a non-filesystem image has no workbench path */ }
    return { rect, imagePath };
  };
  const imageContextPosition = (rect: DOMRect) => {
    const panelWidth = Math.min(720, Math.max(240, window.innerWidth / 2 - 16));
    const panelHeight = Math.min(520, Math.max(180, window.innerHeight / 2 - 16));
    return {
      x: rect.right + panelWidth <= window.innerWidth ? rect.right + 8 : Math.max(8, rect.left - panelWidth - 8),
      y: Math.max(8, Math.min(rect.top, window.innerHeight - panelHeight - 8)),
    };
  };
  const showAltImageZoom = useCallback((image: HTMLImageElement, x?: number, y?: number) => {
    const { rect, imagePath } = imageElementContext(image);
    if (rect.width <= 0 || rect.height <= 0 || !image.currentSrc) return;
    const contextWidth = Math.min(720, Math.max(160, window.innerWidth / 2 - 16));
    const maximumImageWidth = Math.max(120, Math.min(window.innerWidth / 2 - 16, window.innerWidth - contextWidth - 24));
    const maximumImageHeight = Math.max(120, window.innerHeight / 2 - 16);
    const scale = Math.max(0.25, Math.min(maximumImageWidth / rect.width, maximumImageHeight / rect.height));
    const width = maximumImageWidth;
    const height = maximumImageHeight;
    const desiredX = (x ?? rect.left + rect.width / 2) - width / 2;
    const desiredY = (y ?? rect.top + rect.height / 2) - height / 2;
    setAltImageZoom({
      src: image.currentSrc,
      imagePath,
      alt: image.alt,
      x: Math.max(8, Math.min(window.innerWidth - width - contextWidth - 8, desiredX)),
      y: Math.max(8, Math.min(window.innerHeight - Math.max(height, maximumImageHeight) - 8, desiredY)),
      width,
      height,
      scale,
    });
  }, []);
  const handleImageZoomPointer = (event: ReactPointerEvent<HTMLElement>) => {
    const image = event.target instanceof Element ? event.target.closest("img") as HTMLImageElement | null : null;
    const changedImage = hoveredImageRef.current !== image;
    hoveredImageRef.current = image;
    if (changedImage) {
      if (image?.currentSrc) {
        const { rect, imagePath } = imageElementContext(image);
        const position = imageContextPosition(rect);
        setHoverImageContext({
          src: image.currentSrc,
          imagePath,
          alt: image.alt,
          ...position,
        });
      } else {
        setHoverImageContext(null);
      }
    }
    if (image && event.altKey) showAltImageZoom(image, event.clientX, event.clientY);
    else setAltImageZoom(null);
  };
  const handleImageContextClick = (event: ReactMouseEvent<HTMLElement>) => {
    const target = event.target instanceof Element ? event.target : null;
    if (!target || event.ctrlKey || target.closest(".video-import-workflow-gallery-check")) return;
    const image = (target.closest("img") || target.closest("figure")?.querySelector("img")) as HTMLImageElement | null;
    if (!image?.currentSrc) return;
    if (event.altKey && altImageZoom) {
      setPinnedAltImageZoom(altImageZoom);
      setPinnedImageContext(null);
      return;
    }
    const { rect, imagePath } = imageElementContext(image);
    const position = imageContextPosition(rect);
    setPinnedAltImageZoom(null);
    setPinnedImageContext({
      src: image.currentSrc,
      imagePath,
      alt: image.alt,
      ...position,
    });
  };
  useEffect(() => {
    const keyDown = (event: KeyboardEvent) => {
      if (event.key === "Alt" && hoveredImageRef.current) showAltImageZoom(hoveredImageRef.current);
    };
    const hide = (event: KeyboardEvent) => {
      if (event.key === "Alt") setAltImageZoom(null);
    };
    const blur = () => {
      hoveredImageRef.current = null;
      setAltImageZoom(null);
      setHoverImageContext(null);
    };
    window.addEventListener("keydown", keyDown);
    window.addEventListener("keyup", hide);
    window.addEventListener("blur", blur);
    return () => {
      window.removeEventListener("keydown", keyDown);
      window.removeEventListener("keyup", hide);
      window.removeEventListener("blur", blur);
    };
  }, [showAltImageZoom]);

  // ---- status strip + interrupts ----------------------------------------
  const [log, setLog] = useState<Array<{ at: string; text: string }>>([]);
  const stopRef = useRef(false);
  const activeRunsRef = useRef(0);
  const say = useCallback((text: string) => {
    const at = new Date().toLocaleTimeString([], { hour12: false });
    setLog((current) => [...current.slice(-2), { at, text }]);
    pushGlobalStatus(text, "video-import");
  }, []);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const run = async (label: string, work: () => Promise<string | void>) => {
    if (activeRunsRef.current === 0) stopRef.current = false;
    activeRunsRef.current += 1;
    setBusy(true); setError(""); say(`${label}…`);
    try { const result = await work(); say(result || `${label} done`); }
    catch (reason) { const message = reason instanceof Error ? reason.message : String(reason); setError(message); say(`✗ ${message}`); }
    finally {
      activeRunsRef.current = Math.max(0, activeRunsRef.current - 1);
      if (activeRunsRef.current === 0) setBusy(false);
    }
  };

  // ---- collapsible sections ----------------------------------------------
  // Sections all START collapsed; opening is an explicit act (persisted in
  // the state snapshot via collapsedMap/pinnedMap).
  const [collapsedMap, setCollapsedMap] = useState<Record<string, boolean>>({});
  const [pinnedMap, setPinnedMap] = useState<Record<string, boolean>>({});
  const [autoCollapseOn, setAutoCollapseOn] = useState(true);
  const section = (id: string, title: string, meta?: string, extra?: ReactNode) => ({
    id, title, meta, extra,
    open: collapsedMap[id] === false,
    pinned: !!pinnedMap[id],
    autoCollapse: autoCollapseOn,
    onToggle: () => setCollapsedMap((current) => ({ ...current, [id]: current[id] === false })),
    onAutoCollapse: () => setCollapsedMap((current) => (current[id] === false ? { ...current, [id]: true } : current)),
    onPin: () => setPinnedMap((current) => ({ ...current, [id]: !current[id] })),
  });

  // ---- one job engine -----------------------------------------------------
  const [job, setJob] = useState<JobState | null>(null);
  const [sceneJob, setSceneJob] = useState<JobState | null>(null);
  const [frameExtractionJob, setFrameExtractionJob] = useState<JobState | null>(null);
  const [captionJob, setCaptionJob] = useState<JobState | null>(null);
  usePageProcessActivity(
    "video-import",
    busy || job?.state === "running" || sceneJob?.state === "running" || frameExtractionJob?.state === "running" || captionJob?.state === "running",
    busy ? "Video Import model/image operation" : "Video Import background job",
  );
  const jobDone = useRef<(final: JobState) => void>(() => undefined);
  const pollTimer = useRef(0);
  const concurrentPollTimersRef = useRef(new Map<string, number>());
  const watchJob = (jobId: string, kind: string, onDone: (final: JobState) => void) => {
    window.clearInterval(pollTimer.current);
    jobDone.current = onDone;
    pollTimer.current = window.setInterval(async () => {
      try {
        const payload = (await api(`extract/status?jobId=${encodeURIComponent(jobId)}`)) as unknown as Omit<JobState, "kind">;
        const next = { ...payload, kind } as JobState;
        setJob(next);
        if (payload.state !== "running") {
          window.clearInterval(pollTimer.current);
          if (payload.state === "done") jobDone.current(next);
          else setError(payload.error || `${kind} failed`);
        }
      } catch (reason) {
        window.clearInterval(pollTimer.current);
        setError(reason instanceof Error ? reason.message : String(reason));
      }
    }, 500);
  };
  const watchConcurrentJob = (
    jobId: string,
    kind: "scenes" | "extract" | "captions",
    setCurrentJob: (job: JobState) => void,
    onDone: (final: JobState) => void,
  ) => {
    setCurrentJob({ id: jobId, kind, state: "running", done: 0, total: 1, elapsedSeconds: 0, etaSeconds: 0 });
    const existing = concurrentPollTimersRef.current.get(kind);
    if (existing) window.clearInterval(existing);
    const timer = window.setInterval(async () => {
      try {
        const payload = (await api(`extract/status?jobId=${encodeURIComponent(jobId)}`)) as unknown as Omit<JobState, "kind">;
        const next = { ...payload, kind } as JobState;
        setCurrentJob(next);
        if (payload.state !== "running") {
          window.clearInterval(timer);
          concurrentPollTimersRef.current.delete(kind);
          if (payload.state === "done") onDone(next);
          else setError(payload.error || `${kind} failed`);
        }
      } catch (reason) {
        window.clearInterval(timer);
        concurrentPollTimersRef.current.delete(kind);
        setError(reason instanceof Error ? reason.message : String(reason));
      }
    }, 500);
    concurrentPollTimersRef.current.set(kind, timer);
  };
  useEffect(() => () => {
    for (const timer of concurrentPollTimersRef.current.values()) window.clearInterval(timer);
    concurrentPollTimersRef.current.clear();
  }, []);
  const awaitJob = (jobId: string, kind: string, onTick?: (state: JobState) => void) =>
    new Promise<JobState>((resolve, reject) => {
      const tick = async () => {
        try {
          const payload = (await api(`extract/status?jobId=${encodeURIComponent(jobId)}`)) as unknown as JobState;
          setJob({ ...payload, kind });
          onTick?.(payload);
          if (stopRef.current) void api("extract/cancel", { jobId }).catch(() => undefined);
          if (payload.state === "running") { window.setTimeout(tick, 500); return; }
          if (payload.state === "done") resolve(payload); else reject(new Error(payload.error || `${kind} failed`));
        } catch (reason) { reject(reason instanceof Error ? reason : new Error(String(reason))); }
      };
      void tick();
    });
  const stopEverything = () => {
    stopRef.current = true;
    if (job && job.state === "running") void api("extract/cancel", { jobId: job.id }).catch(() => undefined);
    if (sceneJob?.state === "running") void api("extract/cancel", { jobId: sceneJob.id }).catch(() => undefined);
    if (frameExtractionJob?.state === "running") void api("extract/cancel", { jobId: frameExtractionJob.id }).catch(() => undefined);
    if (captionJob?.state === "running") void api("extract/cancel", { jobId: captionJob.id }).catch(() => undefined);
    if (userPickResolver.current) settleUserPick(null);
    say("■ stop requested — finishing the current step…");
  };
  // Optional downstream invalidation, split in two:
  // - "auto-clear stale data" (default ON): when upstream DATA changes (new
  //   video, re-extract), the derived results below are cleared.
  // - "auto-clear next algorithm" (default OFF): when an upstream chain step
  //   is edited, the LATER chain steps are dropped too. Off = the workflow
  //   below survives edits above.
  const [autoClearData, setAutoClearData] = useState(true);
  const autoClearDataRef = useRef(true);
  useEffect(() => { autoClearDataRef.current = autoClearData; }, [autoClearData]);
  const [autoClearAlgorithm, setAutoClearAlgorithm] = useState(false);
  const autoClearAlgorithmRef = useRef(false);
  useEffect(() => { autoClearAlgorithmRef.current = autoClearAlgorithm; }, [autoClearAlgorithm]);
  // Off by default: the stack should be built up one effect at a time, with
  // each pick explicitly reviewed before the next 77-effect round renders --
  // not several selections cascading in automatically. Turn this ON only
  // when you deliberately want the loop to keep going after each pick.
  const [autoNext77, setAutoNext77] = useState(false);
  const autoNext77Ref = useRef(false);
  useEffect(() => { autoNext77Ref.current = autoNext77; }, [autoNext77]);
  const skipVideoResetRef = useRef(false);
  const prevVideoPathRef = useRef<string | null>(null);

  // ---- library ------------------------------------------------------------
  const [videos, setVideos] = useState<Video[]>([]);
  const [selectedPath, setSelectedPath] = useState("");
  const selected = videos.find((video) => video.path === selectedPath) || null;
  const loadVideos = useCallback(async (pick?: string) => {
    const payload = await api(`videos?workspaceId=${encodeURIComponent(workspaceId)}`);
    const list = (payload.videos as Video[]) || [];
    setVideos(list);
    if (pick) setSelectedPath(pick);
    // Never steal the selection: the restored/live value wins whenever it is
    // still a real video; only an empty or vanished selection falls back.
    else setSelectedPath((current) => (current && list.some((video) => video.path === current) ? current : list[0]?.path || ""));
  }, [workspaceId]);
  const [catalog, setCatalog] = useState<Array<{ title: string; url: string }>>([]);
  const [importables, setImportables] = useState<Array<{ path: string; name: string }>>([]);
  useEffect(() => {
    void loadVideos();
    void api(`catalog?workspaceId=${encodeURIComponent(workspaceId)}`).then((payload) => setCatalog((payload.entries as Array<{ title: string; url: string }>) || [])).catch(() => undefined);
    void api(`importables?workspaceId=${encodeURIComponent(workspaceId)}`).then((payload) => {
      const files = ((payload.files as Array<{ path: string; name?: string }>) || []).map((entry) => ({ path: String(entry.path), name: String(entry.name || entry.path) }));
      setImportables(files);
    }).catch(() => undefined);
    void api(`filters?workspaceId=${encodeURIComponent(workspaceId)}`).then((payload) => { setFilters((payload.filters as FilterEntry[]) || []); setLedger((payload.votes as Record<string, number>) || {}); }).catch(() => undefined);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [workspaceId]);

  // ---- intake -------------------------------------------------------------
  const [source, setSource] = useState("");
  const [nameDraft, setNameDraft] = useState("");
  const [quality, setQuality] = useState("480p");
  const fileInput = useRef<HTMLInputElement | null>(null);
  const importSource = (value?: string) =>
    run("Importing", async () => {
      const raw = (value ?? source).trim();
      if (!raw) return "nothing to import";
      const isUrl = /^https?:\/\//i.test(raw);
      const payload = await api(isUrl ? "download" : "import-file", isUrl
        ? { workspaceId, url: raw, name: nameDraft.trim() || undefined, quality: quality === "python-direct" ? undefined : quality, tool: quality === "python-direct" ? "python-direct" : "yt-dlp" }
        : { workspaceId, path: raw, name: nameDraft.trim() || undefined });
      setSource(""); setNameDraft("");
      await loadVideos(String(payload.path || ""));
      return `imported: ${payload.title}`;
    });
  const upload = (file: File | null) => {
    if (!file) return;
    void run("Uploading", async () => {
      const form = new FormData();
      form.append("workspaceId", workspaceId);
      form.append("file", file, file.name);
      const response = await fetch(`${API}/upload`, { method: "POST", body: form });
      const payload = await response.json();
      if (!response.ok) throw new Error(String(payload.detail || response.statusText));
      await loadVideos(String(payload.path || ""));
      return `uploaded: ${payload.title}`;
    });
  };

  // ---- player + timeline ---------------------------------------------------
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const [playerTime, setPlayerTime] = useState(0);
  const [playerDuration, setPlayerDuration] = useState(0);
  const duration = playerDuration || Number(selected?.duration || 0);
  const [markers, setMarkers] = useState<Array<{ atSeconds: number }>>([]);
  const [captions, setCaptions] = useState<CaptionCue[]>([]);
  const [captionSource, setCaptionSource] = useState("");
  const activeCaption = captions.find((cue) => playerTime >= cue.start && playerTime < cue.end);
  useEffect(() => {
    if (!selected) return;
    setCaptions(selected.captions || []);
    setCaptionSource(selected.captionSource || "");
  }, [selected?.path, selected?.captions, selected?.captionSource]);
  const [segments, setSegments] = useState<Array<{ start: number; end: number; keep: boolean }>>([]);
  const [selection, setSelection] = useState<{ start: number; end: number } | null>(null);
  const railRef = useRef<HTMLDivElement | null>(null);
  const dragRef = useRef<{ startX: number; startT: number; moved: boolean } | null>(null);
  useEffect(() => {
    const previous = prevVideoPathRef.current;
    prevVideoPathRef.current = selectedPath;
    // Only a REAL video change resets (not mount, StrictMode re-runs, or restore).
    if (previous === null || previous === selectedPath) return;
    if (skipVideoResetRef.current) { skipVideoResetRef.current = false; return; }
    if (sceneJob?.state === "running") void api("extract/cancel", { jobId: sceneJob.id }).catch(() => undefined);
    if (frameExtractionJob?.state === "running") void api("extract/cancel", { jobId: frameExtractionJob.id }).catch(() => undefined);
    if (captionJob?.state === "running") void api("extract/cancel", { jobId: captionJob.id }).catch(() => undefined);
    for (const timer of concurrentPollTimersRef.current.values()) window.clearInterval(timer);
    concurrentPollTimersRef.current.clear();
    setMarkers(selected?.scenes || []); setCaptions(selected?.captions || []); setCaptionSource(selected?.captionSource || ""); setSegments(selected?.segments || []); setSelection(null);
    setFrames([]); setPlayerTime(0); setPlayerDuration(0); setJob(null); setSceneJob(null); setFrameExtractionJob(null); setCaptionJob(null); setPicked(null); setKept(null); setMemberInputPaths(new Set()); setSelectedWorkflowGalleryPaths(new Set());
    if (autoClearDataRef.current) { setOutput([]); setTrail([]); setProbes([]); setMembers([]); setMemberInventories([]); setMemberScenes({}); setGallery(null); }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedPath]);
  const pct = (value: number) => (duration ? `${Math.min(100, Math.max(0, (value / duration) * 100))}%` : "0%");
  const railTime = (clientX: number) => {
    const rect = railRef.current?.getBoundingClientRect();
    if (!rect || !duration) return 0;
    return Math.max(0, Math.min(duration, ((clientX - rect.left) / rect.width) * duration));
  };
  const persistMarkers = (next: Array<{ atSeconds: number }>) => {
    setMarkers(next);
    void api("markers", { workspaceId, video: selectedPath, markers: next }).catch(() => undefined);
  };
  const persistSegments = (next: Array<{ start: number; end: number; keep: boolean }>) => {
    setSegments(next);
    void api("segments", { workspaceId, video: selectedPath, segments: next }).catch(() => undefined);
  };
  const activeSegments = segments.length ? segments : (duration ? [{ start: 0, end: duration, keep: true }] : []);

  const detectScenes = () =>
    run("Detecting scenes", async () => {
      // Resume where the last run stopped: start at the last detected marker.
      const resumeAt = markers.length ? Math.max(...markers.map((marker) => marker.atSeconds)) : 0;
      const payload = await api("scenes", { workspaceId, video: selectedPath, startSeconds: resumeAt });
      watchConcurrentJob(String(payload.jobId), "scenes", setSceneJob, (final) => { setMarkers(final.markers || []); say(`scenes: ${(final.markers || []).length} marker(s) (${resumeAt ? `resumed @ ${resumeAt.toFixed(1)}s` : "from the top"})`); });
      return resumeAt ? `scanning for scene changes from ${resumeAt.toFixed(1)}s…` : "scanning for scene changes…";
    });
  const clearSceneDetection = () => {
    if (sceneJob?.state === "running") void api("extract/cancel", { jobId: sceneJob.id }).catch(() => undefined);
    const timer = concurrentPollTimersRef.current.get("scenes");
    if (timer) window.clearInterval(timer);
    concurrentPollTimersRef.current.delete("scenes");
    setSceneJob(null);
    persistMarkers([]);
    say("scene detection cleared; next scan starts from the beginning");
  };
  const generateCaptions = () =>
    run("Generating video captions", async () => {
      const payload = await api("captions", { workspaceId, video: selectedPath, modelId: effectiveCaptionModel, chunkSeconds: 30, concurrency: 4 });
      watchConcurrentJob(String(payload.jobId), "captions", setCaptionJob, (final) => {
        setCaptions(final.captions || []);
        setCaptionSource(final.captionSource || "");
        say(`captions: ${(final.captions || []).length} cue(s) · ${final.captionSource || "unknown source"}`);
      });
      return `captioning ${payload.estimatedChunks || 1} audio chunk(s)…`;
    });
  const clearCaptions = () => {
    if (captionJob?.state === "running") void api("extract/cancel", { jobId: captionJob.id }).catch(() => undefined);
    const timer = concurrentPollTimersRef.current.get("captions");
    if (timer) window.clearInterval(timer);
    concurrentPollTimersRef.current.delete("captions");
    setCaptionJob(null);
    setCaptions([]);
    setCaptionSource("");
    void api("captions/clear", { workspaceId, video: selectedPath }).then(() => say("video captions cleared")).catch((reason) => setError(reason instanceof Error ? reason.message : String(reason)));
  };
  const trimVideo = () =>
    run("Trimming", async () => {
      const payload = await api("trim", { workspaceId, video: selectedPath, segments: activeSegments });
      watchJob(String(payload.jobId), "trim", (final) => { void loadVideos(String(final.resultPath || "")); say("trimmed video ready"); });
      return `re-encoding kept parts…`;
    });
  const selectionToVideo = () =>
    run("Extracting selection", async () => {
      if (!selection) return "drag a selection or click a scene first";
      const payload = await api("trim", { workspaceId, video: selectedPath, segments: [{ ...selection, keep: true }], name: `${selected?.title || "clip"}-${selection.start.toFixed(1)}s` });
      watchJob(String(payload.jobId), "trim", (final) => { void loadVideos(String(final.resultPath || "")); say("selection video ready"); });
      return "re-encoding the selection…";
    });

  // ---- frames (input images) -----------------------------------------------
  const [frames, setFrames] = useState<Frame[]>([]);
  const [picked, setPicked] = useState<string | null>(null);
  const [kept, setKept] = useState<Set<string> | null>(null);
  const [memberInputPaths, setMemberInputPaths] = useState<Set<string>>(new Set());
  const [selectedWorkflowGalleryPaths, setSelectedWorkflowGalleryPaths] = useState<Set<string>>(new Set());
  const selectWorkflowGalleryPath = (path: string, selected: boolean) => {
    setSelectedWorkflowGalleryPaths((current) => {
      const next = new Set(current);
      if (selected) next.add(path); else next.delete(path);
      return next;
    });
  };
  const [mode, setMode] = useState<"interval" | "scenes">("scenes");
  const [everySeconds, setEverySeconds] = useState("2");
  const [perScene, setPerScene] = useState("1");
  const [sceneOffset, setSceneOffset] = useState("0.3");
  const [startScene, setStartScene] = useState("2");
  const [endScene, setEndScene] = useState("");
  const [skipScenes, setSkipScenes] = useState("1");
  const [rangeStart, setRangeStart] = useState("0");
  const [rangeEnd, setRangeEnd] = useState("");
  const [maxFrames, setMaxFrames] = useState("40");
  const extractBody = () => ({
    workspaceId, video: selectedPath, mode,
    everySeconds: Number(everySeconds) || 2, maxFrames: Number(maxFrames) || 40,
    perScene: Number(perScene) || 1, sceneOffsetSeconds: Number(sceneOffset) || 0.3,
    startScene: Math.max(1, Number(startScene) || 1),
    endScene: endScene.trim() ? Number(endScene) : undefined,
    skipScenes: Math.max(0, Number(skipScenes) || 0),
    startSeconds: Number(rangeStart) || 0, endSeconds: rangeEnd.trim() ? Number(rangeEnd) : undefined,
  });
  const criteriaLabel = () =>
    mode === "scenes"
      ? `scene ${startScene || 1}–${endScene || "end"} · skip ${skipScenes || 0} · ×${perScene} +${sceneOffset}s · ${rangeStart || 0}–${rangeEnd || "end"}s · max ${maxFrames}`
      : `every ${everySeconds}s · ${rangeStart || 0}–${rangeEnd || "end"}s · max ${maxFrames}`;
  const acceptFrames = (list: JobState["frames"]) => {
    const next = (list || []).map((frame) => ({ ...frame, characters: [], anonymous: 0 }));
    setFrames(next);
    // The freshly extracted images are the first named gallery in the flow.
    setCollapsedMap((current) => ({ ...current, inputs: false }));
    window.setTimeout(() => document.querySelector('[data-section="inputs"]')?.scrollIntoView({ behavior: "smooth", block: "start" }), 200);
    // Prune selection pointers that no longer exist in the fresh extraction.
    setPicked((current) => (current && next.some((frame) => frame.path === current) ? current : null));
    setKept((current) => {
      if (!current) return null;
      const surviving = new Set([...current].filter((path) => next.some((frame) => frame.path === path)));
      return surviving.size ? surviving : null;
    });
    setMemberInputPaths((current) => new Set([...current].filter((path) => next.some((frame) => frame.path === path))));
    setSelectedWorkflowGalleryPaths(new Set());
    if (autoClearDataRef.current) {
      setOutput([]); setTrail([]); setProbes([]); setMembers([]); setMemberInventories([]); setMemberScenes({});
      say("stale results cleared (fresh extraction) — turn off auto-clear stale data to keep them");
    }
  };
  const clearExtractedFrames = () => {
    setFrames([]);
    setPicked(null);
    setKept(null);
    setMemberInputPaths(new Set());
    setOutput([]);
    setTrail([]);
    setProbes([]);
    setMembers([]);
    setMemberInventories([]);
    setMemberScenes({});
    setTurtleArtifacts({});
    setSelectedWorkflowGalleryPaths(new Set());
    say("Extracted Frame Gallery and dependent generated galleries cleared; source files were preserved");
  };
  const extract = () =>
    run("Extracting frames", async () => {
      const payload = await api("extract", extractBody());
      watchConcurrentJob(String(payload.jobId), "extract", setFrameExtractionJob, (final) => { acceptFrames(final.frames); say(`Extracted Frame Gallery: ${(final.frames || []).length} image(s)${final.interrupted ? " (interrupted)" : ""}`); });
      return `extracting ≈${payload.estimatedFrames} frame(s)…`;
    });
  const extractAndWait = async (): Promise<Frame[]> => {
    const started = await api("extract", extractBody());
    const final = await awaitJob(String(started.jobId), "extract", (state) => say(`extract (top of stack): ${state.done}/${state.total}`));
    const fresh: Frame[] = (final.frames || []).map((frame) => ({ ...frame, characters: [], anonymous: 0 }));
    acceptFrames(final.frames);
    return fresh;
  };
  const grabAtCursor = () =>
    run("Grabbing frame", async () => {
      const payload = await api("frame-at", { workspaceId, video: selectedPath, atSeconds: playerTime });
      const grabbed: Frame = { path: String(payload.path), index: Number(payload.index) || 0, atSeconds: Number(payload.atSeconds), characters: [], anonymous: 0 };
      setFrames((current) => (current.some((frame) => frame.path === grabbed.path) ? current : [...current, grabbed].sort((a, b) => (a.atSeconds ?? 0) - (b.atSeconds ?? 0))));
      setCollapsedMap((current) => ({ ...current, inputs: false }));
      window.setTimeout(() => document.querySelector('[data-section="inputs"]')?.scrollIntoView({ behavior: "smooth", block: "start" }), 200);
      return `added frame @ ${grabbed.atSeconds}s to Extracted Frame Gallery`;
    });

  // group selectors
  const [groupKind, setGroupKind] = useState<"unique" | "spread" | "random" | "like" | "unlike" | "user">("user");
  const [groupCount, setGroupCount] = useState("6");
  const selectGroup = () =>
    run("Selecting group", async () => {
      if (frames.length < 2) return "extract at least 2 frames first";
      if (groupKind === "user") {
        const chosen = await askUserPick(frames.map((frame) => ({ original: frame.path, current: frame.path })), "GROUP — click the item YOU want used");
        if (!chosen || !chosen.length) return "user pick skipped";
        setKept(new Set(chosen));
        if (chosen.length === 1) {
          setPicked(chosen[0]);
          setPreviewSource("selectedframe");
          // THE LOOP: picking one item leads straight to picking its filter —
          // render ALL effects on it and open that gallery next.
          say("next: pick the filter — rendering every effect on your item…");
          window.setTimeout(() => void runGallery({ image: chosen[0] }), 80);
          return `you picked 1 item — the filter gallery is next`;
        }
        return `you picked ${chosen.length} item(s)`;
      }
      const count = Math.max(1, Math.min(frames.length, Number(groupCount) || 6));
      if (groupKind === "spread" || groupKind === "random") {
        const picks = groupKind === "spread"
          ? new Set(Array.from({ length: count }, (_, at) => frames[Math.min(frames.length - 1, Math.round(at * (frames.length / count)))].path))
          : new Set([...frames].sort(() => Math.random() - 0.5).slice(0, count).map((frame) => frame.path));
        setKept(picks);
        return `selected ${picks.size} (${groupKind})`;
      }
      if (groupKind === "like" || groupKind === "unlike") {
        const bySource = new Map(output.map((entry) => [entry.source, entry.path]));
        const pairs = frames.filter((frame) => bySource.has(frame.path)).map((frame) => ({ image: bySource.get(frame.path), original: frame.path }));
        if (!pairs.length) return "run the chain first — this compares OUTPUT to original";
        const payload = await api("select-group", { workspaceId, selector: groupKind === "like" ? "like-original" : "unlike-original", pairs, count });
        setKept(new Set((payload.selected as string[]) || []));
        return `selected ${count} (${groupKind} original)`;
      }
      const payload = await api("select-group", { workspaceId, selector: "unique", images: frames.map((frame) => frame.path), count });
      setKept(new Set((payload.selected as string[]) || []));
      return `selected the ${count} most unique`;
    });

  // ---- let-the-user-decide picker ---------------------------------------------
  // A `select:user` chain step (or the GROUP "user" kind) pauses the pipeline
  // and waits for a click on the item that continues.
  const [userPick, setUserPick] = useState<{ title: string; frames: Array<{ original: string; current: string }>; chosen: Set<string>; multi: boolean } | null>(null);
  const userPickResolver = useRef<((paths: string[] | null) => void) | null>(null);
  const askUserPick = (candidates: Array<{ original: string; current: string }>, title: string) =>
    new Promise<string[] | null>((resolve) => {
      userPickResolver.current = resolve;
      setUserPick({ title, frames: candidates, chosen: new Set<string>(), multi: false });
      // The question must be SEEN: force the section open and bring it into view.
      setCollapsedMap((current) => ({ ...current, userpick: false }));
      window.setTimeout(() => {
        document.querySelector(".video-import-userpick-section")?.scrollIntoView({ behavior: "smooth", block: "center" });
      }, 120);
    });
  const settleUserPick = (paths: string[] | null) => {
    const resolve = userPickResolver.current;
    userPickResolver.current = null;
    setUserPick(null);
    resolve?.(paths);
  };

  // ---- filters, votes, chain ------------------------------------------------
  const [filters, setFilters] = useState<FilterEntry[]>([]);
  const [ledger, setLedger] = useState<Record<string, number>>({});
  const [filterId, setFilterId] = useState("");
  const [filterParams, setFilterParams] = useState<Record<string, string>>({});
  const active = filters.find((entry) => entry.id === filterId) || null;
  const pickFilter = (id: string) => {
    setFilterId(id);
    const entry = filters.find((candidate) => candidate.id === id);
    setFilterParams(entry ? Object.fromEntries(Object.entries(entry.params || {}).map(([key, value]) => [key, String(value)])) : {});
    say(entry ? `picked: ${entry.title}` : "no filter picked — ▦ runs the gallery");
  };
  const specFor = (entry: FilterEntry, raw: Record<string, string>): FilterSpec => {
    const params = Object.fromEntries(Object.entries(raw).map(([key, value]) => [key, /^-?\d+(\.\d+)?$/.test(value) ? Number(value) : value]));
    return { label: entry.title, filter: entry.filter, params, colors: params.colors, scale: params.scale, ...(entry.lutPath ? { lutPath: entry.lutPath } : {}), ...(entry.skillPath ? { skillPath: entry.skillPath } : {}) };
  };
  const [chain, setChain] = useState<ChainStep[]>([]);
  useEffect(() => {
    if (!onChainSummaryChange) return;
    onChainSummaryChange(
      chain.map((step, index) => {
        const entry = filters.find((candidate) => candidate.id === step.entryId) || null;
        const label = step.entryId.startsWith("select:")
          ? `selector: ${step.entryId.slice("select:".length)}`
          : entry?.title || step.entryId || "<none>";
        const detail = Object.entries(step.params)
          .filter(([, value]) => value !== "")
          .map(([key, value]) => `${key}: ${value}`)
          .join(", ");
        return { index: index + 1, label, detail };
      }),
    );
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [chain, filters]);
  const [candidateCount, setCandidateCount] = useState("6");
  const [fullSelectors, setFullSelectors] = useState(false);
  const refreshFilters = (payload: Record<string, any>) => {
    setFilters((payload.filters as FilterEntry[]) || []);
    if (payload.votes) setLedger(payload.votes as Record<string, number>);
  };
  const vote = (ids: string[], delta: number) =>
    run(delta > 0 ? "Upvoting" : "Downvoting", async () => {
      if (!ids.length) return "nothing to credit";
      let payload: Record<string, any> | null = null;
      for (const id of ids) payload = await api("filters/vote", { workspaceId, filterId: id, delta });
      if (payload) refreshFilters(payload);
      setLedger((current) => { const next = { ...current }; for (const id of ids) next[id] = (next[id] || 0) + delta; return next; });
      return `${delta > 0 ? "▲" : "▼"} credited to ${ids.join(", ")}`;
    });
  const setDisabled = (id: string, disabled: boolean) =>
    run(disabled ? "Disabling filter" : "Re-enabling filter", async () => {
      const payload = await api("filters/disable", { workspaceId, filterId: id, disabled });
      refreshFilters(payload);
      return disabled ? `disabled ${id} (extreme downvote)` : `re-enabled ${id}`;
    });
  const scanRetinters = () =>
    run("Scanning for retinters", async () => {
      const payload = await api("filters/classify-retinters", { workspaceId });
      watchJob(String(payload.jobId), "retinter", (final) => {
        void api(`filters?workspaceId=${encodeURIComponent(workspaceId)}`).then(refreshFilters).catch(() => undefined);
        say(`retinter scan: ${(final.retinters || []).length} flagged`);
      });
      return `classifying ${payload.count} filter(s)…`;
    });

  // ---- gallery ---------------------------------------------------------------
  const [gallery, setGallery] = useState<GalleryTile[] | null>(null);
  const [galleryScope, setGalleryScope] = useState<"included" | "excluded" | "all">("included");
  const [previewSource, setPreviewSource] = useState<"testcard" | "playerframe" | "firstframe" | "selectedframe">("testcard");
  const previewBody = (): Record<string, unknown> => {
    const body: Record<string, unknown> = { workspaceId };
    if (previewSource === "selectedframe") {
      // Resolution order: explicitly picked item → your GROUP pick → last frame.
      const keptPick = kept && kept.size ? [...kept][kept.size - 1] : null;
      const base = picked || keptPick || (frames.length ? frames[frames.length - 1].path : null);
      if (base) body.image = base;
    }
    else if (previewSource === "playerframe" && selectedPath) { body.video = selectedPath; body.atSeconds = playerTime; }
    else if (previewSource === "firstframe" && frames.length) body.image = frames[0].path;
    return body;
  };
  const runGallery = (options?: { filterId?: string; image?: string }) =>
    run(options?.filterId ? "Rendering permutations" : "Rendering gallery", async () => {
      const body: Record<string, unknown> = { ...previewBody(), ...(options?.image ? { image: options.image } : {}) };
      say(`gallery base: ${typeof body.image === "string" ? String(body.image).split("/").pop() : body.video ? "player frame" : "test card"}`);
      const payload = await api("filter-gallery", { ...body, ...(options?.filterId ? { filterId: options.filterId } : { scope: galleryScope }) });
      setGallery(null);
      watchJob(String(payload.jobId), "gallery", (final) => {
        setGallery(final.gallery || []);
        // The filter gallery is the next step — open it and bring it into view.
        setCollapsedMap((current) => ({ ...current, gallery: false }));
        window.setTimeout(() => document.querySelector(".video-import-gallery")?.scrollIntoView({ behavior: "smooth", block: "start" }), 200);
        say(`gallery: ${(final.gallery || []).length} tile(s)${final.interrupted ? " (interrupted)" : ""} — click one to add it to the chain`);
      });
      return `rendering ${payload.count} output(s)…`;
    });
  const [beforeAfter, setBeforeAfter] = useState<{ before: string; after: string; label: string } | null>(null);
  const previewOne = () =>
    run("Previewing", async () => {
      const specs = chainSpecs();
      if (!specs.length) return "pick a filter or arm a chain step first";
      const payload = await api("filter-preview", { ...previewBody(), chain: specs });
      setBeforeAfter({ before: String(payload.before), after: String(payload.after), label: String(payload.filter) });
      return `previewed ${payload.filter}`;
    });

  // ---- the stack ---------------------------------------------------------------
  const [output, setOutput] = useState<Array<{ source: string; path: string }>>([]);
  const lastRunOutputsRef = useRef<Array<{ source: string; path: string }>>([]);
  const [outputMode, setOutputMode] = useState<"preview" | "full" | null>(null);
  const [outputLabel, setOutputLabel] = useState("");
  const [appliedIds, setAppliedIds] = useState<string[]>([]);
  const [trail, setTrail] = useState<TrailLevel[]>([]);
  const chainSpecs = (): FilterSpec[] => {
    const steps = chain.length ? chain : (active ? [{ entryId: filterId, params: filterParams }] : []);
    return steps
      .filter((step) => step.entryId && !step.entryId.startsWith("select:"))
      .map((step) => { const entry = filters.find((candidate) => candidate.id === step.entryId); return entry ? specFor(entry, step.params) : null; })
      .filter((spec): spec is FilterSpec => spec !== null);
  };
  const runStack = async (full: boolean, chainOverride?: ChainStep[]): Promise<string> => {
    let sourceFrames = frames;
    if (!sourceFrames.length) {
      if (!selectedPath) return "pick a video first";
      say(`top of stack: extract (${criteriaLabel()})`);
      sourceFrames = await extractAndWait();
      if (!sourceFrames.length) return "extraction produced no frames";
    }
    // GROUP "user" is a NOP at full-run time for now: everything passes
    // through, and you curate later (Select group / ✂ Keep only) when YOU
    // decide. Explicit select:user chain steps still pause and ask.
    if (full && groupKind === "user" && !kept?.size) say("GROUP: let-user-decide is a nop here — all frames pass (curate later)");
    // Preview candidates: first group selection > picked item > spread N.
    let candidates = sourceFrames;
    if (!full) {
      const wanted = Math.max(1, Number(candidateCount) || 6);
      if (kept?.size) candidates = sourceFrames.filter((frame) => kept.has(frame.path));
      else if (picked && sourceFrames.some((frame) => frame.path === picked)) candidates = sourceFrames.filter((frame) => frame.path === picked);
      else if (sourceFrames.length > wanted) {
        const keep = new Set(Array.from({ length: wanted }, (_, at) => Math.min(sourceFrames.length - 1, Math.round(at * (sourceFrames.length / wanted)))));
        candidates = sourceFrames.filter((_, index) => keep.has(index));
      }
      say(`preview candidates: ${candidates.length}`);
    }
    let working = candidates.map((frame) => ({ original: frame.path, current: frame.path }));
    const levels: TrailLevel[] = [{ label: full ? "input (all frames)" : "input (candidates)", frames: working.map((item) => ({ original: item.original, path: item.current })) }];
    const snapshot = (label: string) => levels.push({ label, frames: working.map((item) => ({ original: item.original, path: item.current })) });
    const steps = chainOverride?.length ? chainOverride : chain.length ? chain : (active ? [{ entryId: filterId, params: filterParams }] : []);
    if (!steps.length) return "pick a filter or arm a chain step first";
    const labels: string[] = [];
    const ids: string[] = [];
    let pending: FilterSpec[] = [];
    let applied = 0;
    const flush = async () => {
      if (!pending.length || !working.length) { pending = []; return; }
      const payload = await api("filter", { workspaceId, chain: pending, applyTo: "frames", frames: working.map((item) => item.current) });
      const bySource = new Map(((payload.frames as Array<{ source: string; path: string }>) || []).map((entry) => [entry.source, entry.path]));
      working = working.map((item) => ({ ...item, current: bySource.get(item.current) || item.current }));
      applied += pending.length; pending = [];
    };
    for (const step of steps) {
      if (stopRef.current) break;
      if (!step.entryId) continue;
      if (step.entryId.startsWith("select:")) {
        if (full && !fullSelectors) { say(`selector ${step.entryId.slice(7)}: preview-only (toggle to include)`); continue; }
        const kind = step.entryId.slice(7);
        if (kind === "user") {
          await flush();
          say("YOUR PICK: click the item that continues…");
          const chosen = await askUserPick(working.map((item) => ({ ...item })), "SELECT — let user decide which item is used");
          if (stopRef.current) break;
          if (chosen && chosen.length) {
            const keep = new Set(chosen);
            working = working.filter((item) => keep.has(item.current));
          } else say("user pick skipped — keeping all");
          labels.push(`select:user=${working.length}`); ids.push("select:user");
          snapshot(`you picked → ${working.length}`);
          continue;
        }
        const n = Number(step.params.n);
        if (!Number.isFinite(n) || n < 1 || n >= working.length) { say(`selector ${kind}: no-op`); continue; }
        await flush();
        const count = Math.round(n);
        if (kind === "spread") {
          const keep = new Set(Array.from({ length: count }, (_, at) => working[Math.min(working.length - 1, Math.round(at * (working.length / count)))].original));
          working = working.filter((item) => keep.has(item.original));
        } else if (kind === "random") {
          const keep = new Set([...working].sort(() => Math.random() - 0.5).slice(0, count).map((item) => item.original));
          working = working.filter((item) => keep.has(item.original));
        } else if (kind === "unique") {
          const payload = await api("select-group", { workspaceId, selector: "unique", images: working.map((item) => item.current), count });
          const keep = new Set((payload.selected as string[]) || []);
          working = working.filter((item) => keep.has(item.current));
        } else {
          const payload = await api("select-group", { workspaceId, selector: kind === "like" ? "like-original" : "unlike-original", pairs: working.map((item) => ({ image: item.current, original: item.original })), count });
          const keep = new Set((payload.selected as string[]) || []);
          working = working.filter((item) => keep.has(item.original));
        }
        labels.push(`select:${kind}=${working.length}`); ids.push(`select:${kind}`);
        snapshot(`selector ${kind} → ${working.length}`);
      } else {
        const entry = filters.find((candidate) => candidate.id === step.entryId);
        if (!entry) continue;
        pending.push(specFor(entry, step.params));
        labels.push(entry.title); ids.push(entry.id);
        if (!full) { await flush(); snapshot(entry.title); }
      }
    }
    await flush();
    if (!applied && !labels.some((label) => label.startsWith("select:"))) return "chain is all no-ops";
    // Implicit final step: sort most-changed-first, never eliminate.
    if (applied && working.length > 1) {
      try {
        const payload = await api("select-group", { workspaceId, selector: "unlike-original", pairs: working.map((item) => ({ image: item.current, original: item.original })), count: working.length });
        const order = new Map(((payload.selected as string[]) || []).map((original, at) => [original, at]));
        working = [...working].sort((left, right) => (order.get(left.original) ?? 0) - (order.get(right.original) ?? 0));
      } catch { /* cosmetic */ }
    }
    snapshot(full ? "FULL output" : "output (sorted)");
    const results = working.map((item) => ({ source: item.original, path: item.current }));
    lastRunOutputsRef.current = results;
    setOutput(results);
    setOutputMode(full ? "full" : "preview");
    setOutputLabel(labels.join(" → "));
    setAppliedIds([...new Set(ids)]);
    setTrail(levels);
    setProbes([]);
    // The results are the next thing to look at — open OUTPUT and show it.
    setCollapsedMap((current) => ({ ...current, output: false }));
    window.setTimeout(() => document.querySelector(".video-import-output")?.scrollIntoView({ behavior: "smooth", block: "start" }), 200);
    return full
      ? `FULL run: ${applied} filter step(s) over ${working.length} frame(s)`
      : `preview: ${applied} filter step(s), ${working.length} candidate(s) (sorted, none eliminated)`;
  };

  // ---- probes + members ----------------------------------------------------------
  const [probes, setProbes] = useState<number[]>([]);
  const [members, setMembers] = useState<Member[]>([]);
  const [memberInventories, setMemberInventories] = useState<MemberInventory[]>([]);
  const [memberScenes, setMemberScenes] = useState<Record<string, string>>({});
  const [memberDescriptionPrompt, setMemberDescriptionPrompt] = useState(DEFAULT_MEMBER_DESCRIPTION_PROMPT);
  const [objectPromptWriter, setObjectPromptWriter] = useState(DEFAULT_OBJECT_PROMPT_WRITER);
  const [memberDecompositionPrompt, setMemberDecompositionPrompt] = useState(DEFAULT_MEMBER_DECOMPOSITION_PROMPT);
  const [memberOrderPrompt, setMemberOrderPrompt] = useState(DEFAULT_MEMBER_ORDER_PROMPT);
  const [memberOutlinerPrompt, setMemberOutlinerPrompt] = useState(DEFAULT_MEMBER_OUTLINER_PROMPT);
  const [memberExtractorPrompt, setMemberExtractorPrompt] = useState(DEFAULT_RECURSIVE_EXTRACTOR_PROMPT);
  const [turtlePrompt, setTurtlePrompt] = useState(DEFAULT_TURTLE_PROMPT);
  const [turtlePngPrompt, setTurtlePngPrompt] = useState(DEFAULT_TURTLE_PNG_PROMPT);
  const [describerPromptSelection, setDescriberPromptSelection] = useState<PromptSelection>("workspace");
  const [plannerPromptSelection, setPlannerPromptSelection] = useState<PromptSelection>("workspace");
  const [outlinerPromptSelection, setOutlinerPromptSelection] = useState<PromptSelection>("workspace");
  const [extractorPromptSelection, setExtractorPromptSelection] = useState<PromptSelection>("workspace");
  const [turtlePromptSelection, setTurtlePromptSelection] = useState<PromptSelection>("workspace");
  const [turtlePngPromptSelection, setTurtlePngPromptSelection] = useState<PromptSelection>("workspace");
  const [expandedCallPrompt, setExpandedCallPrompt] = useState<keyof LlmCallConcurrency | null>(null);
  const [turtleArtifacts, setTurtleArtifacts] = useState<Record<string, TurtleArtifact>>({});
  const [models, setModels] = useState<ModelChoice[]>([]);
  const [memberModel, setMemberModel] = useState("");
  const [allCallsModel, setAllCallsModel] = useState("");
  const [describerModel, setDescriberModel] = useState("");
  const [plannerModel, setPlannerModel] = useState("");
  const [outlinerModel, setOutlinerModel] = useState("");
  const [extractorModel, setExtractorModel] = useState("");
  const [turtleModel, setTurtleModel] = useState("");
  const [turtlePngModel, setTurtlePngModel] = useState("");
  const [captionModel, setCaptionModel] = useState("");
  const [modelResponseCache, setModelResponseCache] = useState<Record<string, CachedModelResponse>>({});
  const modelResponseCacheRef = useRef<Record<string, CachedModelResponse>>({});
  const [inheritedModelId, setInheritedModelId] = useState("");
  const [modelPreferenceSource, setModelPreferenceSource] = useState("");
  const inheritedModelRef = useRef("");
  const memberModelTouchedRef = useRef(false);
  const allCallsModelTouchedRef = useRef(false);
  const describerModelTouchedRef = useRef(false);
  const plannerModelTouchedRef = useRef(false);
  const outlinerModelTouchedRef = useRef(false);
  const extractorModelTouchedRef = useRef(false);
  const turtleModelTouchedRef = useRef(false);
  const turtlePngModelTouchedRef = useRef(false);
  const [memberGoal, setMemberGoal] = useState<MemberGoal>("any");
  const [memberFill, setMemberFill] = useState<"inpaint" | "median" | "blur" | "hole">("inpaint");
  const [selectedRecursiveInventoryId, setSelectedRecursiveInventoryId] = useState("");
  const [collapsedLeftGalleries, setCollapsedLeftGalleries] = useState<Record<string, boolean>>({});
  const [recursiveAutomation, setRecursiveAutomation] = useState<RecursiveAutomation>(DEFAULT_RECURSIVE_AUTOMATION);
  const [llmCallConcurrency, setLlmCallConcurrency] = useState<LlmCallConcurrency>(DEFAULT_LLM_CALL_CONCURRENCY);
  const [llmCallMetrics, setLlmCallMetrics] = useState<LlmCallMetrics>(emptyLlmCallMetrics);
  const [totalLlmConcurrency, setTotalLlmConcurrency] = useState(8);
  const [retryClock, setRetryClock] = useState(Date.now());
  const retryTimerRef = useRef(0);
  const automaticDescriptionClaimsRef = useRef(new Set<string>());
  const [manualWorkerHold, setManualWorkerHold] = useState(false);
  const [restartPendingSignal, setRestartPendingSignal] = useState(false);
  const restartPendingSignalRef = useRef(false);
  restartPendingSignalRef.current = restartPendingSignal;
  const workersHeld = manualWorkerHold || restartPendingSignal;
  const workersHeldRef = useRef(false);
  workersHeldRef.current = workersHeld;
  useEffect(() => {
    const pause = () => setRestartPendingSignal(true);
    const clear = (event: Event) => {
      const reason = String((event as CustomEvent<{ reason?: string }>).detail?.reason || "");
      if (reason !== "restart-started") setRestartPendingSignal(false);
    };
    window.addEventListener(RESTART_PENDING_REQUEST_EVENT, pause);
    window.addEventListener(RESTART_PENDING_CLEARED_EVENT, clear);
    return () => {
      window.removeEventListener(RESTART_PENDING_REQUEST_EVENT, pause);
      window.removeEventListener(RESTART_PENDING_CLEARED_EVENT, clear);
    };
  }, []);
  const effectiveDescriberModel = describerModel || allCallsModel;
  const effectivePlannerModel = plannerModel || allCallsModel;
  const effectiveOutlinerModel = outlinerModel || allCallsModel;
  const effectiveExtractorModel = extractorModel || allCallsModel;
  const effectiveImageOutputModel = automaticImageOutputModelId(models, effectiveExtractorModel);
  const effectiveCaptionModel = automaticAudioModelId(models, captionModel);
  const effectiveTurtleModel = turtleModel || allCallsModel;
  const effectiveTurtlePngModel = turtlePngModel || allCallsModel;
  const selectedDescriptionPrompt = describerPromptSelection === "default" ? DEFAULT_MEMBER_DESCRIPTION_PROMPT : memberDescriptionPrompt;
  const selectedPlannerPrompt = plannerPromptSelection === "default" ? DEFAULT_MEMBER_ORDER_PROMPT : memberOrderPrompt;
  const selectedOutlinerPrompt = outlinerPromptSelection === "default" ? DEFAULT_MEMBER_OUTLINER_PROMPT : memberOutlinerPrompt;
  const selectedExtractorPrompt = extractorPromptSelection === "default" ? DEFAULT_RECURSIVE_EXTRACTOR_PROMPT : memberExtractorPrompt;
  const selectedTurtlePrompt = turtlePromptSelection === "default" ? DEFAULT_TURTLE_PROMPT : turtlePrompt;
  const selectedTurtlePngPrompt = turtlePngPromptSelection === "default" ? DEFAULT_TURTLE_PNG_PROMPT : turtlePngPrompt;
  const videoModelIds = models.map((model) => model.id);
  const describeVideoModel = (id: string) => videoModelDescription(
    models.find((model) => model.id === id),
    id,
    inheritedModelId,
    modelPreferenceSource,
  );
  const describeAudioModel = (id: string) => videoModelDescription(
    models.find((model) => model.id === id),
    id,
    inheritedModelId,
    modelPreferenceSource,
    "audio",
  );
  const expandedPrompt = expandedCallPrompt === "describer"
    ? { label: "DESCRIBER", value: selectedDescriptionPrompt }
    : expandedCallPrompt === "planner"
      ? { label: "PLANNER", value: selectedPlannerPrompt }
      : expandedCallPrompt === "outliner"
        ? { label: "OUTLINER", value: selectedOutlinerPrompt }
        : expandedCallPrompt === "extractor"
          ? { label: "EXTRACTOR", value: selectedExtractorPrompt }
          : expandedCallPrompt === "turtle"
            ? { label: "TURTLE GEN", value: selectedTurtlePrompt }
            : expandedCallPrompt === "turtlePng"
              ? { label: "TURTLE PNG", value: selectedTurtlePngPrompt }
              : null;
  const updateExpandedPrompt = (value: string) => {
    if (expandedCallPrompt === "describer") { setDescriberPromptSelection("workspace"); setMemberDescriptionPrompt(value); }
    else if (expandedCallPrompt === "planner") { setPlannerPromptSelection("workspace"); setMemberOrderPrompt(value); }
    else if (expandedCallPrompt === "outliner") { setOutlinerPromptSelection("workspace"); setMemberOutlinerPrompt(value); }
    else if (expandedCallPrompt === "extractor") { setExtractorPromptSelection("workspace"); setMemberExtractorPrompt(value); }
    else if (expandedCallPrompt === "turtle") { setTurtlePromptSelection("workspace"); setTurtlePrompt(value); }
    else if (expandedCallPrompt === "turtlePng") { setTurtlePngPromptSelection("workspace"); setTurtlePngPrompt(value); }
  };
  const toggleRecursiveAutomation = (key: keyof RecursiveAutomation) => {
    setRecursiveAutomation((current) => ({ ...current, [key]: !current[key] }));
  };
  const setCallConcurrency = (type: keyof LlmCallConcurrency, value: number | null) => {
    setLlmCallConcurrency((current) => ({ ...current, [type]: value === null ? null : Math.max(1, Math.min(50, Math.round(value) || 1)) }));
  };
  const effectiveCallConcurrency = (type: keyof LlmCallConcurrency) => {
    return Math.min(totalLlmConcurrency, llmCallConcurrency[type] ?? totalLlmConcurrency);
  };
  const llmSchedulerLimitsRef = useRef({ total: totalLlmConcurrency, byType: llmCallConcurrency });
  llmSchedulerLimitsRef.current = { total: totalLlmConcurrency, byType: llmCallConcurrency };
  const llmSchedulerRef = useRef<{
    active: number;
    byType: Record<keyof LlmCallConcurrency, number>;
    waiters: Array<{ type: keyof LlmCallConcurrency; resolve: (release: () => void) => void }>;
  }>({
    active: 0,
    byType: { describer: 0, planner: 0, outliner: 0, extractor: 0, turtle: 0, turtlePng: 0 },
    waiters: [],
  });
  const [llmSchedulerVersion, setLlmSchedulerVersion] = useState(0);
  const pumpLlmScheduler = () => {
    if (workersHeldRef.current) return;
    const scheduler = llmSchedulerRef.current;
    const limits = llmSchedulerLimitsRef.current;
    while (scheduler.active < limits.total && scheduler.waiters.length) {
      let waiterIndex = -1;
      let bestUtilization = Number.POSITIVE_INFINITY;
      scheduler.waiters.forEach((waiter, index) => {
        const configured = limits.byType[waiter.type];
        const typeLimit = Math.min(limits.total, configured ?? limits.total);
        if (scheduler.byType[waiter.type] >= typeLimit) return;
        const utilization = scheduler.byType[waiter.type] / typeLimit;
        if (utilization < bestUtilization) {
          waiterIndex = index;
          bestUtilization = utilization;
        }
      });
      if (waiterIndex < 0) break;
      const [waiter] = scheduler.waiters.splice(waiterIndex, 1);
      scheduler.active += 1;
      scheduler.byType[waiter.type] += 1;
      setLlmSchedulerVersion((version) => version + 1);
      let released = false;
      waiter.resolve(() => {
        if (released) return;
        released = true;
        scheduler.active = Math.max(0, scheduler.active - 1);
        scheduler.byType[waiter.type] = Math.max(0, scheduler.byType[waiter.type] - 1);
        setLlmSchedulerVersion((version) => version + 1);
        pumpLlmScheduler();
      });
    }
  };
  const acquireLlmSlot = (type: keyof LlmCallConcurrency) => new Promise<() => void>((resolve) => {
    llmSchedulerRef.current.waiters.push({ type, resolve });
    setLlmSchedulerVersion((version) => version + 1);
    pumpLlmScheduler();
  });
  useEffect(() => {
    if (!workersHeld) pumpLlmScheduler();
  }, [llmCallConcurrency, totalLlmConcurrency, workersHeld]);
  const retryReady = (retryAfter?: number) => !retryAfter || retryAfter <= retryClock;
  const scheduleRetry = () => {
    window.clearTimeout(retryTimerRef.current);
    retryTimerRef.current = window.setTimeout(() => setRetryClock(Date.now()), LLM_RETRY_DELAY_MS + 50);
  };
  useEffect(() => () => window.clearTimeout(retryTimerRef.current), []);
  const setLeftGalleryOpen = (id: string, open: boolean) => {
    setCollapsedLeftGalleries((current) => current[id] === !open ? current : { ...current, [id]: !open });
  };
  const clearSelectedImages = () => {
    const selectedPaths = new Set(memberInputPaths);
    const affectedInventories = memberInventories.filter((inventory) => selectedPaths.has(inventory.framePath));
    const affectedInventoryIds = new Set(affectedInventories.map((inventory) => inventory.id));
    const affectedMembers = members.filter((member) => selectedPaths.has(member.framePath));
    const affectedImagePaths = new Set([
      ...selectedPaths,
      ...affectedInventories.flatMap((inventory) => [
        inventory.sourceImage,
        memberScenes[inventory.id] || "",
        ...inventory.things.flatMap((thing) => [
          thing.inputImage || "",
          thing.outlineImage || "",
          ...(thing.outputImages || []),
        ]),
      ]),
      ...affectedMembers.flatMap((member) => [member.cutout, member.nextPassImage || "", member.sceneAfter || ""]),
    ].filter(Boolean));
    setMemberInputPaths(new Set());
    setMemberInventories((current) => current.filter((inventory) => !affectedInventoryIds.has(inventory.id)));
    setMembers((current) => current.filter((member) => !selectedPaths.has(member.framePath)));
    setMemberScenes((current) => Object.fromEntries(Object.entries(current).filter(([inventoryId]) => !affectedInventoryIds.has(inventoryId))));
    setTurtleArtifacts((current) => Object.fromEntries(Object.entries(current).filter(([, artifact]) => !affectedImagePaths.has(artifact.sourceImage))));
    setSelectedWorkflowGalleryPaths((current) => new Set([...current].filter((path) => !affectedImagePaths.has(path))));
    setSelectedRecursiveInventoryId((current) => affectedInventoryIds.has(current) ? "" : current);
    const remainingCache = Object.fromEntries(Object.entries(modelResponseCacheRef.current).filter(([, entry]) => !affectedImagePaths.has(entry.imagePath)));
    modelResponseCacheRef.current = remainingCache;
    setModelResponseCache(remainingCache);
    for (const path of affectedImagePaths) delete imageProvenanceCacheRef.current[path];
    setActiveImageProvenance(null);
    setPinnedImageContext((current) => current && affectedImagePaths.has(current.imagePath) ? null : current);
    setPinnedAltImageZoom((current) => current && affectedImagePaths.has(current.imagePath) ? null : current);
    setHoverImageContext((current) => current && affectedImagePaths.has(current.imagePath) ? null : current);
    setAltImageZoom((current) => current && affectedImagePaths.has(current.imagePath) ? null : current);
    say(`cleared ${selectedPaths.size} selected image(s) and their recursive metadata`);
  };
  const clearRecursiveLevel = (depth: number) => {
    const removedMembers = members.filter((member) => (member.depth || 0) >= depth);
    const removedInventories = memberInventories.filter((inventory) => (inventory.depth || 0) > depth);
    const impactedInventorySources = new Set(memberInventories.filter((inventory) => (inventory.depth || 0) >= depth).map((inventory) => inventory.sourceImage));
    const removedTurtleArtifacts = Object.values(turtleArtifacts).filter((artifact) => impactedInventorySources.has(artifact.sourceImage));
    const removedPaths = new Set([
      ...removedMembers.flatMap((member) => [member.cutout, member.nextPassImage || ""]),
      ...removedInventories.map((inventory) => inventory.sourceImage),
      ...removedTurtleArtifacts.flatMap((artifact) => [artifact.sourceImage, artifact.renderedImage || ""]),
    ].filter(Boolean));
    setMembers((current) => current.filter((member) => (member.depth || 0) < depth));
    setMemberInventories((current) => current
      .filter((inventory) => (inventory.depth || 0) <= depth)
      .map((inventory) => (inventory.depth || 0) !== depth ? inventory : {
        ...inventory,
        status: "done",
        things: inventory.things.map((thing) => ({
          name: thing.name,
          description: thing.description,
          parentName: thing.parentName,
          countIndex: thing.countIndex,
          countTotal: thing.countTotal,
          visibility: thing.visibility,
          hiddenReason: thing.hiddenReason,
          occludedBy: thing.occludedBy,
          status: "listed",
        })),
      }));
    const retainedInventoryIds = new Set(memberInventories.filter((inventory) => (inventory.depth || 0) < depth).map((inventory) => inventory.id));
    setMemberScenes((current) => Object.fromEntries(Object.entries(current).filter(([inventoryId]) => retainedInventoryIds.has(inventoryId))));
    setTurtleArtifacts((current) => Object.fromEntries(Object.entries(current).filter(([sourceImage]) => !impactedInventorySources.has(sourceImage))));
    setSelectedWorkflowGalleryPaths((current) => new Set([...current].filter((path) => !removedPaths.has(path))));
    say(`Level ${depth} generated objects/backgrounds cleared; automation can regenerate this level and its descendants`);
  };
  const clearTurtleTerminations = () => {
    const renderedPaths = new Set(Object.values(turtleArtifacts).map((artifact) => artifact.renderedImage).filter((path): path is string => Boolean(path)));
    setTurtleArtifacts({});
    setSelectedWorkflowGalleryPaths((current) => new Set([...current].filter((path) => !renderedPaths.has(path))));
    say("Turtle termination gallery cleared; leaf programs and renders are queued for regeneration");
  };
  const [pipeForkSelections, setPipeForkSelections] = useState<PipeForkSelections>(DEFAULT_PIPE_FORKS);
  const [pipeForkHistory, setPipeForkHistory] = useState<PipeForkHistoryEntry[]>([]);
  const [selectedPipeFork, setSelectedPipeFork] = useState<keyof PipeForkSelections>("inventory");
  const [pipePathView, setPipePathView] = useState(false);
  const [pipeParentView, setPipeParentView] = useState<PipeParentView>(DEFAULT_PIPE_PARENT_VIEW);
  const selectPipeFork = <K extends keyof PipeForkSelections>(fork: K, value: string) => {
    setPipeForkSelections((current) => {
      const next = { ...current };
      restorePipeForkSelection(next, fork, value);
      return next;
    });
  };
  const selectPipeParentView = (fork: keyof PipeForkSelections, value: string) => {
    setPipeParentView((current) => {
      if (fork === "inventory" && (value === "found_objects" || value === "sub_objects")) return { ...current, inventory: value };
      if (fork === "prompts" && (value === "baseline" || value === "llm_rewrite")) return { ...current, prompts: value };
      if (fork === "routes" && (value === "direct_from_scene" || value === "from_parent_cutout")) return { ...current, routes: value };
      return current;
    });
  };
  const pipePathIndex = Math.max(0, PIPE_PATHS.findIndex((path) =>
    path.inventory === pipeForkSelections.inventory
    && path.prompts === pipeForkSelections.prompts
    && path.routes === pipeForkSelections.routes));
  const cyclePipePath = (direction: -1 | 1) => {
    const nextIndex = (pipePathIndex + direction + PIPE_PATHS.length) % PIPE_PATHS.length;
    setPipeForkSelections(PIPE_PATHS[nextIndex]);
    setPipePathView(true);
  };

  // ---- runtime state snapshot -------------------------------------------------
  // Everything on this page is path-based (real files on disk), so a JSON
  // snapshot of the pointers restores the EXACT working state after any
  // reload/rebuild. Auto-saved (debounced) per workspace; restored on mount.
  const snapshotKey = `videoImport:state:${workspaceId}`;
  const legacySnapshotKey = `vi2:state:${workspaceId}`;
  const restoredRef = useRef(false);
  const restoreStartedRef = useRef(false);
  const userTouchedRef = useRef(false);
  const buildSnapshot = () => ({
    v: 1,
    at: new Date().toISOString(),
    selectedPath, playerTime, markers, captions, captionSource, segments, mode, everySeconds, perScene, sceneOffset, startScene, endScene, skipScenes, rangeStart, rangeEnd, maxFrames,
    frames, picked, kept: kept ? [...kept] : null, memberInputPaths: [...memberInputPaths], selectedWorkflowGalleryPaths: [...selectedWorkflowGalleryPaths], previewSource, galleryScope,
    filterId, filterParams, chain, candidateCount, fullSelectors,
    gallery, output, outputMode, outputLabel, appliedIds, trail, probes,
    members, memberInventories, memberScenes, memberDescriptionPrompt, objectPromptWriter, memberDecompositionPrompt, memberOrderPrompt, memberOutlinerPrompt, memberExtractorPrompt, turtlePrompt, turtlePngPrompt, turtleArtifacts, memberGoal, memberFill,
    allCallsModel, describerModel, plannerModel, outlinerModel, extractorModel, turtleModel, turtlePngModel, captionModel,
    describerPromptSelection, plannerPromptSelection, outlinerPromptSelection, extractorPromptSelection, turtlePromptSelection, turtlePngPromptSelection,
    pipeForkSelections, pipeForkHistory, selectedPipeFork, pipeParentView, selectedRecursiveInventoryId, collapsedLeftGalleries, recursiveAutomation, llmCallConcurrency, llmCallMetrics, totalLlmConcurrency, manualWorkerHold,
    modelResponseCache,
    autoClearData, autoClearAlgorithm, autoNext77,
    collapsedMap, pinnedMap,
  });
  // Apply a snapshot object to the live page (used by mount-restore and the
  // JSON CONFIG editor). Returns false if the object is not a v1 snapshot.
  const applySnapshot = (s: any): boolean => {
    if (!s || typeof s !== "object" || s.v !== 1) return false;
    if (s.selectedPath) { skipVideoResetRef.current = true; setSelectedPath(String(s.selectedPath)); }
    if (typeof s.playerTime === "number") setPlayerTime(s.playerTime);
    if (Array.isArray(s.markers)) setMarkers(s.markers);
    if (Array.isArray(s.captions)) setCaptions(s.captions);
    if (typeof s.captionSource === "string") setCaptionSource(s.captionSource);
    if (Array.isArray(s.segments)) setSegments(s.segments);
    if (s.mode === "interval" || s.mode === "scenes") setMode(s.mode);
    if (typeof s.everySeconds === "string") setEverySeconds(s.everySeconds);
    if (typeof s.perScene === "string") setPerScene(s.perScene);
    if (typeof s.sceneOffset === "string") setSceneOffset(s.sceneOffset);
    if (typeof s.startScene === "string") setStartScene(s.startScene);
    if (typeof s.endScene === "string") setEndScene(s.endScene);
    if (typeof s.skipScenes === "string") setSkipScenes(s.skipScenes);
    if (typeof s.rangeStart === "string") setRangeStart(s.rangeStart);
    if (typeof s.rangeEnd === "string") setRangeEnd(s.rangeEnd);
    if (typeof s.maxFrames === "string") setMaxFrames(s.maxFrames);
    if (Array.isArray(s.frames)) setFrames(s.frames);
    if (typeof s.picked === "string") setPicked(s.picked);
    if (Array.isArray(s.kept) && s.kept.length) setKept(new Set(s.kept.map(String)));
    if (Array.isArray(s.memberInputPaths)) {
      const restoredFramePaths = new Set(Array.isArray(s.frames) ? s.frames.map((frame: Frame) => frame.path) : []);
      setMemberInputPaths(new Set(s.memberInputPaths.map(String).filter((path: string) => restoredFramePaths.has(path))));
    }
    if (Array.isArray(s.selectedWorkflowGalleryPaths)) setSelectedWorkflowGalleryPaths(new Set(s.selectedWorkflowGalleryPaths.map(String)));
    if (s.previewSource) setPreviewSource(s.previewSource);
    if (s.galleryScope) setGalleryScope(s.galleryScope);
    if (typeof s.filterId === "string") setFilterId(s.filterId);
    if (s.filterParams && typeof s.filterParams === "object") setFilterParams(s.filterParams);
    if (Array.isArray(s.chain)) {
      setChain(s.chain.map((step: ChainStep) => (
        step.entryId === "select:user" ? { ...step, params: {} } : step
      )));
    }
    if (typeof s.candidateCount === "string") setCandidateCount(s.candidateCount);
    if (typeof s.fullSelectors === "boolean") setFullSelectors(s.fullSelectors);
    if (Array.isArray(s.gallery)) setGallery(s.gallery);
    if (Array.isArray(s.output)) setOutput(s.output);
    if (s.outputMode === "preview" || s.outputMode === "full") setOutputMode(s.outputMode);
    if (typeof s.outputLabel === "string") setOutputLabel(s.outputLabel);
    if (Array.isArray(s.appliedIds)) setAppliedIds(s.appliedIds);
    if (Array.isArray(s.trail)) setTrail(s.trail);
    if (Array.isArray(s.probes)) setProbes(s.probes);
    if (Array.isArray(s.members)) setMembers(s.members.filter((member: Member) => member.probeIndex < 0));
    if (Array.isArray(s.memberInventories)) setMemberInventories(s.memberInventories.map((inventory: MemberInventory) => ({
      ...inventory,
      status: (["describing", "ordering", "outlining", "extracting"] as MemberInventory["status"][]).includes(inventory.status)
        ? inventory.descriptionOutput ? "done" : "pending"
        : inventory.status,
      descriptionPrompt: normalizeMemberPromptLabels(String(inventory.descriptionPrompt || "")),
      describedThings: Array.isArray(inventory.describedThings) ? inventory.describedThings.map((thing) => ({
        ...thing,
        extractionPrompt: normalizeMemberPromptLabels(String(thing.extractionPrompt || "")),
      })) : undefined,
      things: Array.isArray(inventory.things) ? inventory.things.map((thing) => ({
        ...thing,
        status: thing.status === "outlining"
          ? hasAlignedOutline(thing) ? "outlined" : "listed"
          : thing.status === "extracting"
            ? thing.outputImages?.length ? "extracted" : hasAlignedOutline(thing) ? "outlined" : "listed"
            : thing.status,
        extractionPrompt: normalizeMemberPromptLabels(String(thing.extractionPrompt || "")),
      })) : [],
    })).filter((inventory: MemberInventory) => inventory.probeIndex < 0));
    if (s.memberScenes && typeof s.memberScenes === "object") {
      setMemberScenes(Object.fromEntries(
        Object.entries(s.memberScenes)
          .filter(([key, value]) => key.startsWith("input:") && typeof value === "string")
          .map(([key, value]) => [key, String(value)]),
      ));
    }
    if (typeof s.memberDescriptionPrompt === "string") setMemberDescriptionPrompt(normalizeMemberPromptLabels(s.memberDescriptionPrompt));
    if (typeof s.objectPromptWriter === "string") setObjectPromptWriter(s.objectPromptWriter);
    else if (typeof s.topLevelPromptWriter === "string") setObjectPromptWriter(s.topLevelPromptWriter);
    if (typeof s.memberDecompositionPrompt === "string") setMemberDecompositionPrompt(s.memberDecompositionPrompt);
    if (typeof s.memberOrderPrompt === "string" && !s.memberOrderPrompt.includes("cutoutInstructions")) setMemberOrderPrompt(s.memberOrderPrompt);
    else if (typeof s.memberOrderPrompt === "string") setMemberOrderPrompt(DEFAULT_MEMBER_ORDER_PROMPT);
    if (typeof s.memberOutlinerPrompt === "string" && s.memberOutlinerPrompt.includes("{{nextObjectName}}")) setMemberOutlinerPrompt(s.memberOutlinerPrompt);
    if (typeof s.memberExtractorPrompt === "string") {
      setMemberExtractorPrompt(s.memberExtractorPrompt.includes("{{outline}}") ? s.memberExtractorPrompt : DEFAULT_RECURSIVE_EXTRACTOR_PROMPT);
    }
    if (typeof s.turtlePrompt === "string" && s.turtlePrompt.includes("{{subjectName}}")) setTurtlePrompt(s.turtlePrompt);
    else if (typeof s.turtlePrompt === "string") setTurtlePrompt(DEFAULT_TURTLE_PROMPT);
    if (typeof s.turtlePngPrompt === "string" && s.turtlePngPrompt.includes("{{draftProgram}}")) setTurtlePngPrompt(s.turtlePngPrompt);
    if (s.turtleArtifacts && typeof s.turtleArtifacts === "object") setTurtleArtifacts(s.turtleArtifacts);
    if (typeof s.allCallsModel === "string") { allCallsModelTouchedRef.current = true; setAllCallsModel(s.allCallsModel); }
    if (typeof s.describerModel === "string") { describerModelTouchedRef.current = true; setDescriberModel(s.describerModel); }
    if (typeof s.plannerModel === "string") { plannerModelTouchedRef.current = true; setPlannerModel(s.plannerModel); }
    if (typeof s.outlinerModel === "string") { outlinerModelTouchedRef.current = true; setOutlinerModel(s.outlinerModel); }
    if (typeof s.extractorModel === "string") { extractorModelTouchedRef.current = true; setExtractorModel(s.extractorModel); }
    if (typeof s.turtleModel === "string") { turtleModelTouchedRef.current = true; setTurtleModel(s.turtleModel); }
    if (typeof s.turtlePngModel === "string") { turtlePngModelTouchedRef.current = true; setTurtlePngModel(s.turtlePngModel); }
    if (typeof s.captionModel === "string") setCaptionModel(s.captionModel);
    if (s.memberGoal) setMemberGoal(s.memberGoal);
    if (s.memberFill) setMemberFill(s.memberFill);
    if (s.pipeForkSelections && typeof s.pipeForkSelections === "object") {
      const restoredForks = { ...DEFAULT_PIPE_FORKS };
      (Object.keys(DEFAULT_PIPE_FORKS) as Array<keyof PipeForkSelections>).forEach((fork) => {
        restorePipeForkSelection(restoredForks, fork, s.pipeForkSelections[fork]);
      });
      setPipeForkSelections(restoredForks);
    }
    if (Array.isArray(s.pipeForkHistory)) setPipeForkHistory(s.pipeForkHistory.slice(-120));
    if (s.selectedPipeFork === "inventory" || s.selectedPipeFork === "prompts" || s.selectedPipeFork === "routes") setSelectedPipeFork(s.selectedPipeFork);
    if (s.pipeParentView && typeof s.pipeParentView === "object") {
      setPipeParentView({
        inventory: s.pipeParentView.inventory === "sub_objects" ? "sub_objects" : "found_objects",
        prompts: s.pipeParentView.prompts === "baseline" ? "baseline" : "llm_rewrite",
        routes: s.pipeParentView.routes === "from_parent_cutout" ? "from_parent_cutout" : "direct_from_scene",
      });
    }
    if (typeof s.selectedRecursiveInventoryId === "string") setSelectedRecursiveInventoryId(s.selectedRecursiveInventoryId);
    if (s.collapsedLeftGalleries && typeof s.collapsedLeftGalleries === "object") setCollapsedLeftGalleries(s.collapsedLeftGalleries);
    if (s.recursiveAutomation && typeof s.recursiveAutomation === "object") {
      setRecursiveAutomation({
        describer: s.recursiveAutomation.describer === true,
        planner: s.recursiveAutomation.planner === true,
        outliner: s.recursiveAutomation.outliner !== false,
        extractor: s.recursiveAutomation.extractor === true,
        turtle: s.recursiveAutomation.turtle !== false,
        turtlePng: s.recursiveAutomation.turtlePng !== false,
        advanceLevels: s.recursiveAutomation.advanceLevels !== false,
        enlargeSubobjects: s.recursiveAutomation.enlargeSubobjects !== false,
      });
    }
    if (s.llmCallConcurrency && typeof s.llmCallConcurrency === "object") {
      const restoredConcurrency = (value: unknown): number | null => value == null || value === ""
        ? null
        : Math.max(1, Math.min(50, Math.round(Number(value) || 1)));
      setLlmCallConcurrency({
        describer: restoredConcurrency(s.llmCallConcurrency.describer),
        planner: restoredConcurrency(s.llmCallConcurrency.planner),
        outliner: restoredConcurrency(s.llmCallConcurrency.outliner),
        extractor: restoredConcurrency(s.llmCallConcurrency.extractor),
        turtle: restoredConcurrency(s.llmCallConcurrency.turtle),
        turtlePng: restoredConcurrency(s.llmCallConcurrency.turtlePng),
      });
    } else if (typeof s.llmConcurrency === "number") {
      const restored = Math.max(1, Math.min(50, Math.round(s.llmConcurrency)));
      setLlmCallConcurrency({ describer: restored, planner: restored, outliner: restored, extractor: restored, turtle: restored, turtlePng: restored });
    }
    if (s.llmCallMetrics && typeof s.llmCallMetrics === "object") {
      const restoredMetrics = emptyLlmCallMetrics();
      for (const type of Object.keys(restoredMetrics) as Array<keyof LlmCallMetrics>) {
        const metric = s.llmCallMetrics[type];
        if (!metric || typeof metric !== "object") continue;
        restoredMetrics[type] = {
          completed: Math.max(0, Math.round(Number(metric.completed) || 0)),
          totalDurationMs: Math.max(0, Number(metric.totalDurationMs) || 0),
        };
      }
      setLlmCallMetrics(restoredMetrics);
    }
    if (typeof s.totalLlmConcurrency === "number") setTotalLlmConcurrency(Math.max(1, Math.min(50, Math.round(s.totalLlmConcurrency))));
    if (typeof s.manualWorkerHold === "boolean") setManualWorkerHold(s.manualWorkerHold);
    if (s.describerPromptSelection === "workspace" || s.describerPromptSelection === "default") setDescriberPromptSelection(s.describerPromptSelection);
    if (s.plannerPromptSelection === "workspace" || s.plannerPromptSelection === "default") setPlannerPromptSelection(s.plannerPromptSelection);
    if (s.outlinerPromptSelection === "workspace" || s.outlinerPromptSelection === "default") setOutlinerPromptSelection(s.outlinerPromptSelection);
    if (s.extractorPromptSelection === "workspace" || s.extractorPromptSelection === "default") setExtractorPromptSelection(s.extractorPromptSelection);
    if (s.turtlePromptSelection === "workspace" || s.turtlePromptSelection === "default") setTurtlePromptSelection(s.turtlePromptSelection);
    if (s.turtlePngPromptSelection === "workspace" || s.turtlePngPromptSelection === "default") setTurtlePngPromptSelection(s.turtlePngPromptSelection);
    const restoredModelCache = s.modelResponseCache && typeof s.modelResponseCache === "object" ? s.modelResponseCache : {};
    modelResponseCacheRef.current = restoredModelCache;
    setModelResponseCache(restoredModelCache);
    if (typeof s.autoClearData === "boolean") setAutoClearData(s.autoClearData);
    else if (typeof s.autoClear === "boolean") setAutoClearData(s.autoClear);
    if (typeof s.autoClearAlgorithm === "boolean") setAutoClearAlgorithm(s.autoClearAlgorithm);
    if (typeof s.autoNext77 === "boolean") setAutoNext77(s.autoNext77);
    if (s.collapsedMap && typeof s.collapsedMap === "object") setCollapsedMap(s.collapsedMap);
    if (s.pinnedMap && typeof s.pinnedMap === "object") setPinnedMap(s.pinnedMap);
    setAutomaticSchedulerTick((tick) => tick + 1);
    return true;
  };
  useEffect(() => {
    if (restoreStartedRef.current) return;
    restoreStartedRef.current = true;
    void (async () => {
      // The image repository's own state file is the source of truth; the
      // browser copy is a fast fallback. The NEWEST snapshot wins — a fresh
      // "just switched video" state must beat an older, richer one.
      const stamp = (s: any) => { const t = Date.parse(String(s?.at || "")); return Number.isFinite(t) ? t : 0; };
      let fsState: any = null;
      try {
        const payload = await api(`page-state?workspaceId=${encodeURIComponent(workspaceId)}`);
        if (payload.state && typeof payload.state === "object" && !payload.state.forgotten) fsState = payload.state;
      } catch { /* backend down — fall back to the browser copy */ }
      let lsState: any = null;
      try {
        const raw = localStorage.getItem(snapshotKey) || localStorage.getItem(legacySnapshotKey);
        if (raw) lsState = JSON.parse(raw);
      } catch { lsState = null; }
      const s = !fsState ? lsState : !lsState ? fsState : stamp(fsState) >= stamp(lsState) ? fsState : lsState;
      try {
        // If the user already touched the page while we were fetching, their
        // actions win — never re-select the restored video over their click.
        if (userTouchedRef.current) { say("state restore skipped — you were already working"); }
        else if (s && applySnapshot(s)) say(`⟳ restored your state (${s === fsState ? "image repository" : "browser"}) — ${(s.frames || []).length} frame(s), ${(s.chain || []).length} chain step(s), ${(s.output || []).length} output(s)`);
      } catch { /* a corrupt snapshot is ignored, never fatal */ }
      restoredRef.current = true; // saving may begin only now
    })();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  useEffect(() => {
    if (!restoredRef.current) return;
    const timer = setTimeout(() => {
      const state = buildSnapshot();
      try { localStorage.setItem(snapshotKey, JSON.stringify(state)); } catch { /* quota */ }
      // Mirror into the image repository so the state lives beside the images.
      void api("page-state", { workspaceId, state }).catch(() => undefined);
    }, 900);
    return () => clearTimeout(timer);
  });
  // Flush on unmount so switching pages right after a change never loses it.
  const buildSnapshotRef = useRef(buildSnapshot);
  buildSnapshotRef.current = buildSnapshot;
  useEffect(() => () => {
    if (!restoredRef.current) return;
    const state = buildSnapshotRef.current();
    try { localStorage.setItem(snapshotKey, JSON.stringify(state)); } catch { /* quota */ }
    try { navigator.sendBeacon?.(`${API}/page-state`, new Blob([JSON.stringify({ workspaceId, state })], { type: "application/json" })); } catch { /* best effort */ }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  const copyStateJson = () => {
    const text = JSON.stringify(buildSnapshot(), null, 2);
    void navigator.clipboard?.writeText(text).then(() => say("state JSON copied to clipboard")).catch(() => say("copy failed — state JSON logged to console"));
    console.log("[vi2 state]", text);
  };
  const saveExpandedPrompt = async () => {
    if (!expandedCallPrompt) return;
    try {
      const state = buildSnapshot();
      await api("page-state", { workspaceId, state });
      try { localStorage.setItem(snapshotKey, JSON.stringify(state)); } catch { /* browser mirror is optional */ }
      say(`${expandedPrompt?.label || "call"} prompt saved to the image repository`);
    } catch (reason) {
      const message = reason instanceof Error ? reason.message : String(reason);
      setError(message);
      say(`✗ prompt save failed: ${message}`);
    }
  };
  const reloadExpandedPrompt = async () => {
    if (!expandedCallPrompt) return;
    try {
      const payload = await api(`page-state?workspaceId=${encodeURIComponent(workspaceId)}`);
      const state = payload.state;
      if (!state || typeof state !== "object" || state.forgotten) throw new Error("no saved Video Import state is available");
      if (expandedCallPrompt === "describer") {
        setMemberDescriptionPrompt(typeof state.memberDescriptionPrompt === "string" ? state.memberDescriptionPrompt : DEFAULT_MEMBER_DESCRIPTION_PROMPT);
        setDescriberPromptSelection(state.describerPromptSelection === "default" ? "default" : "workspace");
      } else if (expandedCallPrompt === "planner") {
        setMemberOrderPrompt(typeof state.memberOrderPrompt === "string" ? state.memberOrderPrompt : DEFAULT_MEMBER_ORDER_PROMPT);
        setPlannerPromptSelection(state.plannerPromptSelection === "default" ? "default" : "workspace");
      } else if (expandedCallPrompt === "outliner") {
        setMemberOutlinerPrompt(typeof state.memberOutlinerPrompt === "string" ? state.memberOutlinerPrompt : DEFAULT_MEMBER_OUTLINER_PROMPT);
        setOutlinerPromptSelection(state.outlinerPromptSelection === "default" ? "default" : "workspace");
      } else if (expandedCallPrompt === "extractor") {
        setMemberExtractorPrompt(typeof state.memberExtractorPrompt === "string" ? state.memberExtractorPrompt : DEFAULT_RECURSIVE_EXTRACTOR_PROMPT);
        setExtractorPromptSelection(state.extractorPromptSelection === "default" ? "default" : "workspace");
      } else if (expandedCallPrompt === "turtle") {
        setTurtlePrompt(typeof state.turtlePrompt === "string" && state.turtlePrompt.includes("{{subjectName}}") ? state.turtlePrompt : DEFAULT_TURTLE_PROMPT);
        setTurtlePromptSelection(state.turtlePromptSelection === "default" ? "default" : "workspace");
      } else {
        setTurtlePngPrompt(typeof state.turtlePngPrompt === "string" && state.turtlePngPrompt.includes("{{draftProgram}}") ? state.turtlePngPrompt : DEFAULT_TURTLE_PNG_PROMPT);
        setTurtlePngPromptSelection(state.turtlePngPromptSelection === "default" ? "default" : "workspace");
      }
      say(`${expandedPrompt?.label || "call"} prompt reloaded from the image repository`);
    } catch (reason) {
      const message = reason instanceof Error ? reason.message : String(reason);
      setError(message);
      say(`✗ prompt reload failed: ${message}`);
    }
  };
  const forgetState = () => {
    try { localStorage.removeItem(snapshotKey); localStorage.removeItem(legacySnapshotKey); } catch { /* ignore */ }
    void api("page-state", { workspaceId, state: { v: 1, forgotten: true } }).catch(() => undefined);
    say("saved state forgotten — next load starts clean");
  };
  // JSON CONFIG editor draft: null = tracking the live config. Edits apply to
  // the flow LIVE as soon as the JSON parses (debounced).
  const [configDraft, setConfigDraft] = useState<string | null>(null);
  const [configValid, setConfigValid] = useState(true);
  useEffect(() => {
    if (configDraft === null) { setConfigValid(true); return; }
    const timer = setTimeout(() => {
      try {
        const parsed = JSON.parse(configDraft);
        const ok = applySnapshot(parsed);
        setConfigValid(ok);
        if (ok) say("config edit applied to the flow");
      } catch { setConfigValid(false); }
    }, 500);
    return () => clearTimeout(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [configDraft]);
  const applyConfigDraft = () => {
    if (configDraft === null) { say("config unchanged"); return; }
    try {
      const parsed = JSON.parse(configDraft);
      if (!applySnapshot(parsed)) { setError("not a v1 config object (needs \"v\": 1)"); return; }
      setConfigDraft(null);
      say("config applied — page state now matches the JSON");
    } catch (reason) { setError(`config JSON invalid: ${reason instanceof Error ? reason.message : String(reason)}`); }
  };
  // Manual workflow edits mark the results below them stale (optional clearing).
  const clearStaleResults = (reason: string) => {
    setOutput([]); setOutputMode(null); setOutputLabel(""); setAppliedIds([]);
    setTrail([]); setProbes([]); setMembers([]); setMemberInventories([]); setMemberScenes({});
    say(`stale results cleared (${reason})`);
  };
  const editChain = (mutate: (current: ChainStep[]) => ChainStep[], truncateAt?: number) => {
    setChain((current) => {
      let next = mutate(current);
      if (autoClearAlgorithmRef.current && truncateAt !== undefined && next.length > truncateAt) {
        next = next.slice(0, truncateAt);
        say(`later algorithm steps dropped (edited above; ${next.length} step(s) kept)`);
      }
      return next;
    });
    if (autoClearDataRef.current && (output.length || trail.length || members.length)) clearStaleResults("chain edited");
  };
  useEffect(() => {
    let cancelled = false;
    inheritedModelRef.current = "";
    memberModelTouchedRef.current = false;
    allCallsModelTouchedRef.current = false;
    describerModelTouchedRef.current = false;
    plannerModelTouchedRef.current = false;
    outlinerModelTouchedRef.current = false;
    extractorModelTouchedRef.current = false;
    turtleModelTouchedRef.current = false;
    turtlePngModelTouchedRef.current = false;
    setModels([]);
    setMemberModel("");
    setAllCallsModel("");
    setDescriberModel("");
    setPlannerModel("");
    setOutlinerModel("");
    setExtractorModel("");
    setTurtleModel("");
    setTurtlePngModel("");
    setInheritedModelId("");
    setModelPreferenceSource("");
    const mergeModels = (incoming: ModelChoice[]) => {
      setModels((current) => {
        const byId = new Map(current.map((model) => [model.id, model]));
        for (const model of incoming) {
          const previous = byId.get(model.id);
          byId.set(model.id, {
            ...previous,
            ...model,
            inherited: model.inherited ?? previous?.inherited,
            origin: model.origin || previous?.origin,
            enabled: previous?.enabled === true || model.enabled,
            vision: previous?.vision === true || model.vision,
            imageOutput: previous?.imageOutput === true || model.imageOutput,
          });
        }
        const inherited = inheritedModelRef.current;
        if (!inherited || !byId.has(inherited)) return [...byId.values()];
        const inheritedChoice = byId.get(inherited)!;
        return [inheritedChoice, ...[...byId.values()].filter((model) => model.id !== inherited)];
      });
    };
    void api(`/workbench/workspaces/${encodeURIComponent(workspaceId)}/model-selection?include_models=false`).then((payload) => {
      if (cancelled) return;
      const inherited = String((payload.effective?.models as unknown[])?.[0] || "");
      inheritedModelRef.current = inherited;
      setInheritedModelId(inherited);
      setModelPreferenceSource(String(payload.source || ""));
    }).catch(() => undefined);
    const enumeratePolicyModels = () => {
      void api(`/workbench/workspaces/${encodeURIComponent(workspaceId)}/model-policy`).then((payload) => {
        if (cancelled) return;
        const registry = (payload.registry || {}) as Record<string, any>;
        const list = ((registry.models as Array<Record<string, any>>) || [])
          .map((model) => ({
            id: String(model.modelResourceId || model.id || ""),
            name: String(model.name || model.modelId || model.id),
            backendId: String(model.backendId || model.vendorId || ""),
            capabilities: (model.capabilities || {}) as Record<string, unknown>,
            enabled: model.effective?.runtime === true,
            vision: model.capabilities?.vision === true || model.capabilities?.multimodal === true,
            imageOutput: model.capabilities?.imageOutput === true || model.capabilities?.imageGeneration === true,
          }))
          .filter((model) => model.id);
        mergeModels(list);
        const automatic = automaticVideoModelId(list, inheritedModelRef.current);
        if (!memberModelTouchedRef.current) setMemberModel(automatic);
        if (!allCallsModelTouchedRef.current) setAllCallsModel(automatic);
      }).catch(() => undefined);
    };
    void api(`/workbench/workspaces/${encodeURIComponent(workspaceId)}/model-selection?include_disabled_models=true`).then((payload) => {
      if (cancelled) return;
      const inheritedChoices = ((payload.models as Array<Record<string, any>>) || [])
        .map((model) => ({
          id: String(model.id || ""),
          name: String(model.label || model.id || ""),
          inherited: model.inherited === true,
          origin: String(model.workspaceId || model.source || ""),
          backendId: String(model.backendId || ""),
          capabilities: (model.capabilities || {}) as Record<string, unknown>,
          enabled: model.enabled === true,
          vision: model.capabilities?.vision === true || model.capabilities?.multimodal === true,
          imageOutput: model.capabilities?.imageOutput === true || model.capabilities?.imageGeneration === true,
        }))
        .filter((model) => model.id);
      mergeModels(inheritedChoices);
      const effective = inheritedModelRef.current || String((payload.effective?.models as unknown[])?.[0] || "");
      if (effective && !inheritedModelRef.current) {
        inheritedModelRef.current = effective;
        setInheritedModelId(effective);
      }
      const automatic = automaticVideoModelId(inheritedChoices, effective);
      if (!memberModelTouchedRef.current) setMemberModel(automatic);
      if (!allCallsModelTouchedRef.current) setAllCallsModel(automatic);
    }).catch(() => undefined).finally(() => {
      if (!cancelled) enumeratePolicyModels();
    });
    return () => { cancelled = true; };
  }, [workspaceId]);
  const isRunnableVisionModel = (modelId: string) => models.some((model) => model.id === modelId && model.enabled && model.vision);
  const asDataUrl = async (path: string): Promise<string | null> => {
    try {
      const response = await fetch(`/workbench/workspaces/${encodeURIComponent(workspaceId)}/asset?path=${encodeURIComponent(path)}`, { cache: "no-store" });
      if (!response.ok) return null;
      const blob = await response.blob();
      return await new Promise<string>((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(String(reader.result || ""));
        reader.onerror = () => reject(new Error("could not read frame"));
        reader.readAsDataURL(blob);
      });
    } catch {
      return null;
    }
  };
  const invokeCachedModel = async (
    modelId: string,
    prompt: string,
    imagePath: string,
    image: string,
    timeoutSeconds: number,
    bypassCache = false,
    callType: keyof LlmCallConcurrency = "extractor",
  ): Promise<Record<string, any>> => {
    if (workersHeldRef.current) throw new Error(restartPendingSignalRef.current ? "Restart pending; new LLM work is paused." : "Workers held; new LLM work is paused.");
    const imageHash = responseCacheHash(image);
    const key = responseCacheHash(`${modelId}\u0000${prompt}\u0000${imageHash}`);
    const cached = modelResponseCacheRef.current[key];
    if (!bypassCache && cached && cached.modelId === modelId && cached.prompt === prompt && cached.imageHash === imageHash && cached.payload && typeof cached.payload === "object") {
      say(`↻ cached model response · ${modelId} · ${imagePath.split("/").pop()}`);
      return cached.payload;
    }
    const release = await acquireLlmSlot(callType);
    if (workersHeldRef.current) {
      release();
      throw new Error(restartPendingSignalRef.current ? "Restart pending; queued LLM work was paused before launch." : "Workers held; queued LLM work was paused before launch.");
    }
    let payload: Record<string, any>;
    const startedAt = performance.now();
    try {
      payload = await api(`/workbench/workspaces/${encodeURIComponent(workspaceId)}/models/${encodeURIComponent(modelId)}/invoke`, {
        prompt,
        image,
        timeoutSeconds,
      });
    } finally {
      const durationMs = performance.now() - startedAt;
      setLlmCallMetrics((current) => ({
        ...current,
        [callType]: {
          completed: current[callType].completed + 1,
          totalDurationMs: current[callType].totalDurationMs + durationMs,
        },
      }));
      release();
    }
    const entry: CachedModelResponse = {
      modelId,
      prompt,
      imagePath,
      imageHash,
      cachedAt: new Date().toISOString(),
      payload,
    };
    const next = { ...modelResponseCacheRef.current, [key]: entry };
    modelResponseCacheRef.current = next;
    setModelResponseCache(next);
    return payload;
  };
  const asset = (path: string) => `/workbench/workspaces/${encodeURIComponent(workspaceId)}/asset?path=${encodeURIComponent(path)}`;
  const updateMemberInventory = (id: string, update: (inventory: MemberInventory) => MemberInventory) => {
    setMemberInventories((current) => current.map((inventory) => (inventory.id === id ? update(inventory) : inventory)));
  };
  const storeMemberInventory = (inventory: MemberInventory) => {
    setMemberInventories((current) => [...current.filter((existing) => existing.id !== inventory.id), inventory]);
  };
  const updateInventoryThing = (id: string, thingIndex: number, patch: Partial<MemberInventoryThing>) => {
    updateMemberInventory(id, (inventory) => ({
      ...inventory,
      things: inventory.things.map((thing, index) => (index === thingIndex ? { ...thing, ...patch } : thing)),
    }));
  };
  const describeRecursiveInventory = async (initial: MemberInventory): Promise<MemberInventory | null> => {
    const descriptionPrompt = initial.descriptionPrompt || renderMemberDescriptionPrompt(
      selectedDescriptionPrompt,
      memberGoal,
      [],
      `This image is the extracted object "${initial.subjectName}". Describe it and list only its direct visible constituent sub-objects. Do not relist "${initial.subjectName}" itself. If it has no visually separable children, return an empty things array.`,
    );
    const describing = { ...initial, descriptionPrompt, status: "describing" as const };
    storeMemberInventory(describing);
    const image = await asDataUrl(initial.sourceImage);
    if (!image) {
      const failed = { ...describing, sceneDescription: `Could not load extracted object image: ${initial.sourceImage}`, status: "failed" as const, retryAfter: Date.now() + LLM_RETRY_DELAY_MS, attempts: (initial.attempts || 0) + 1 };
      storeMemberInventory(failed);
      scheduleRetry();
      return null;
    }
    try {
      const payload = await invokeCachedModel(effectiveDescriberModel, descriptionPrompt, initial.sourceImage, image, 120, initial.status === "failed", "describer");
      const descriptionOutput = typeof payload.text === "string" ? payload.text.trim() : "";
      const parsed = parseMemberDescriptionOutput(descriptionOutput);
      const things = parsed.things.filter((thing) => thing.name.toLowerCase() !== initial.subjectName?.toLowerCase());
      const completed: MemberInventory = {
        ...describing,
        sceneDescription: parsed.sceneDescription || descriptionOutput || `Extracted object ${initial.subjectName}`,
        descriptionOutput,
        describedThings: things,
        things,
        status: "done",
      };
      storeMemberInventory(completed);
      say(`D${initial.depth || 0} ${initial.subjectName}: ${things.length} direct child object(s)`);
      return completed;
    } catch (reason) {
      const message = reason instanceof Error ? reason.message : String(reason);
      const failed = { ...describing, sceneDescription: message, descriptionOutput: `ERROR: ${message}`, status: "failed" as const, retryAfter: Date.now() + LLM_RETRY_DELAY_MS, attempts: (initial.attempts || 0) + 1 };
      storeMemberInventory(failed);
      scheduleRetry();
      say(`✗ describer ${initial.subjectName}: ${message}`);
      return null;
    }
  };
  const describeMemberScenes = (onlyMissing = false) =>
    run("Describing scene objects", async () => {
      if (!isRunnableVisionModel(effectiveDescriberModel)) return "pick an enabled Describer vision model first";
      if (!frames.length) return "extract frames first";
      const selectedInputFrames = frames.filter((frame) => memberInputPaths.has(frame.path));
      if (!selectedInputFrames.length) return "multi-select at least one Extracted Frame Gallery image as an LLM input";
      const inputFrames = onlyMissing
        ? selectedInputFrames.filter((frame) => {
            const existing = memberInventories.find((inventory) => inventory.id === `input:${frame.path}`);
            return !automaticDescriptionClaimsRef.current.has(`root:${frame.path}`)
              && (!existing || (existing.status === "failed" ? retryReady(existing.retryAfter) : !existing.descriptionOutput));
          })
        : selectedInputFrames;
        const pendingChildren = memberInventories.filter((inventory) =>
          inventory.parentInventoryId
          && (!onlyMissing || !automaticDescriptionClaimsRef.current.has(`child:${inventory.id}`))
          && (inventory.status === "pending" || (inventory.status === "failed" && retryReady(inventory.retryAfter)))
        );
      const descriptionTasks = [
        ...inputFrames.map((frame) => ({
          kind: "root" as const,
          frame,
          claimKey: `root:${frame.path}`,
          retry: memberInventories.find((inventory) => inventory.id === `input:${frame.path}`)?.status === "failed",
        })),
        ...pendingChildren.map((inventory) => ({ kind: "child" as const, inventory, claimKey: `child:${inventory.id}`, retry: inventory.status === "failed" })),
      ];
      const descriptionConcurrency = effectiveCallConcurrency("describer");
      const orderedDescriptionTasks = cooperativeRetryOrder(descriptionTasks, descriptionConcurrency, (task) => task.retry);
      const queuedDescriptionTasks = orderedDescriptionTasks;
      if (onlyMissing) {
       for (const task of queuedDescriptionTasks) automaticDescriptionClaimsRef.current.add(task.claimKey);
      }
      let listed = 0;
      await runConcurrent(queuedDescriptionTasks, descriptionConcurrency, async (task) => {
       try {
         if (task.kind === "child") {
            if (stopRef.current) return;
            const described = await describeRecursiveInventory(task.inventory);
            if (described) listed += described.things.length;
            return;
          }
          const frame = task.frame;
          if (stopRef.current) return;
          const probeIndex = -1;
          const probeLabel = "input image";
          const known = new Set(members.filter((member) => member.framePath === frame.path && member.probeIndex === probeIndex && member.status !== "rejected").map((member) => member.name.toLowerCase()));
          const sceneKey = `input:${frame.path}`;
          const scenePath = frame.path;
          const inventoryId = sceneKey;
          const previousInventory = memberInventories.find((inventory) => inventory.id === inventoryId);
          const initialInventory: MemberInventory = {
            ...previousInventory,
            id: inventoryId,
            framePath: frame.path,
            frameIndex: frame.index,
            probeIndex,
            probeLabel,
            goal: memberGoal,
            sourceImage: scenePath,
            sceneDescription: "",
            descriptionPrompt: "",
            descriptionOutput: "",
            modelId: effectiveDescriberModel,
            depth: 0,
            subjectName: `input_${frame.index}`,
            status: "describing",
            things: previousInventory?.things || [],
          };
          setMemberInventories((current) => [...current.filter((inventory) => inventory.id !== inventoryId), initialInventory]);
          say(`① describe input image #${frame.index}`);
          const inventoryImage = await asDataUrl(scenePath);
          if (!inventoryImage) {
            const message = `Could not load input image: ${scenePath}`;
            updateMemberInventory(inventoryId, (inventory) => ({ ...inventory, sceneDescription: message, descriptionOutput: `ERROR: ${message}`, status: "failed", retryAfter: Date.now() + LLM_RETRY_DELAY_MS, attempts: (inventory.attempts || 0) + 1 }));
            scheduleRetry();
            say(`✗ ${message}`);
            return;
          }
          const inventoryPrompt = renderMemberDescriptionPrompt(
            selectedDescriptionPrompt,
            memberGoal,
            [...known],
            "This is a root input image. Describe the scene and list its top-level visually separable objects.",
          );
          updateMemberInventory(inventoryId, (inventory) => ({ ...inventory, descriptionPrompt: inventoryPrompt }));
          let inventoryPayload: Record<string, any>;
          try {
            inventoryPayload = await invokeCachedModel(effectiveDescriberModel, inventoryPrompt, scenePath, inventoryImage, 120, previousInventory?.status === "failed", "describer");
          } catch (reason) {
            const message = reason instanceof Error ? reason.message : String(reason);
            updateMemberInventory(inventoryId, (inventory) => ({ ...inventory, sceneDescription: message, descriptionOutput: `ERROR: ${message}`, status: "failed", retryAfter: Date.now() + LLM_RETRY_DELAY_MS, attempts: (inventory.attempts || 0) + 1 }));
            scheduleRetry();
            say(`✗ scene inventory failed: ${message}`);
            return;
          }
          const inventoryRaw = typeof inventoryPayload.text === "string" ? inventoryPayload.text.trim() : "";
          updateMemberInventory(inventoryId, (inventory) => ({ ...inventory, descriptionOutput: inventoryRaw }));
          const inventoryMatch = inventoryRaw.match(/\{[\s\S]*\}/);
          let sceneDescription = ""; let things: MemberInventoryThing[] = [];
          if (inventoryMatch) {
            try {
              const parsed = JSON.parse(inventoryMatch[0]);
              sceneDescription = String(parsed.description || parsed.scene || "").trim();
              const seen = new Set<string>();
              things = (Array.isArray(parsed.things) ? parsed.things : [])
                .map((thing: unknown) => {
                  const value = typeof thing === "string" ? { name: thing, description: thing } : thing as Record<string, unknown>;
                  const name = String(value?.name || "").trim().slice(0, 40);
                  const description = String(value?.description || value?.details || value?.name || "").trim().slice(0, 240);
                  return {
                    name,
                    description,
                    status: "listed" as const,
                  };
                })
                .filter((thing: MemberInventoryThing) => {
                  const key = thing.name.toLowerCase();
                  if (!key || known.has(key) || seen.has(key)) return false;
                  seen.add(key);
                  return true;
                });
            } catch { /* the failed inventory is shown below */ }
          }
          if (!things.length) {
            updateMemberInventory(inventoryId, (inventory) => ({
              ...inventory,
              sceneDescription: sceneDescription || inventoryRaw || "No extractable things were listed.",
              status: inventoryMatch ? "done" : "failed",
            }));
            return;
          }
          const previousThings = new Map((previousInventory?.things || []).map((thing) => [thing.name.toLowerCase(), thing]));
          things = things.map((thing) => {
            const previous = previousThings.get(thing.name.toLowerCase());
            return previous ? {
              ...thing,
              status: previous.status,
              inputImage: previous.inputImage,
              outputImages: previous.outputImages,
              extractionAttempts: previous.extractionAttempts,
              outlinePrompt: previous.outlinePrompt,
              outlineOutput: previous.outlineOutput,
              outlineImage: previous.outlineImage,
              outlineDimensions: previous.outlineDimensions,
              outlinePolygons: previous.outlinePolygons,
              outlineHoles: previous.outlineHoles,
              outlineBox: previous.outlineBox,
              outlineError: previous.outlineError,
              outlineRetryAfter: previous.outlineRetryAfter,
              outlineAttempts: previous.outlineAttempts,
              error: previous.error,
            } : thing;
          });
          listed += things.length;
          setMemberInventories((current) => current.map((inventory) => inventory.id === inventoryId ? {
            ...inventory,
            sceneDescription,
            status: "done",
            describedThings: things,
            things,
          } : inventory));
          say(`① [input image] #${frame.index}: ${things.length} thing(s) listed`);
       } finally {
         if (onlyMissing) automaticDescriptionClaimsRef.current.delete(task.claimKey);
       }
      });
      return stopRef.current
        ? `Textual description stopped after listing ${listed} thing(s)`
        : `Describer complete: ${listed} thing(s) across ${inputFrames.length} input image(s) and ${pendingChildren.length} extracted object(s)`;
    });
  const describeRecursiveSubject = async (
    parent: MemberInventory,
    subjectName: string,
    sourceImage: string,
    depth: number,
    describeNow = true,
  ): Promise<MemberInventory | null> => {
    const inventoryId = `${parent.id}/${responseCacheHash(`${subjectName}\u0000${sourceImage}`)}`;
    const subjectContext = `This image is the extracted object "${subjectName}". Describe it and list only its direct visible constituent sub-objects. Do not relist "${subjectName}" itself. If it has no visually separable children, return an empty things array.`;
    const descriptionPrompt = renderMemberDescriptionPrompt(selectedDescriptionPrompt, memberGoal, [], subjectContext);
    const existing = memberInventories.find((inventory) => inventory.id === inventoryId);
    if (existing && existing.status !== "pending") return existing;
    const initial: MemberInventory = existing || {
     id: inventoryId,
     framePath: parent.framePath,
     frameIndex: parent.frameIndex,
     probeIndex: -1,
     probeLabel: `depth ${depth} · ${subjectName}`,
     goal: memberGoal,
     sourceImage,
     sceneDescription: "",
     descriptionPrompt,
     descriptionOutput: "",
     modelId: effectiveDescriberModel,
     depth,
     parentInventoryId: parent.id,
     subjectName,
     status: "pending",
     things: [],
    };
    storeMemberInventory(initial);
    return describeNow ? describeRecursiveInventory(initial) : initial;
  };
  const planRecursiveInventory = async (inventory: MemberInventory, force = false): Promise<MemberInventory | null> => {
    if (!inventory.things.length) return { ...inventory, status: "done" };
    if (!force && inventory.extractionOrder?.length) return inventory;
    if (!force && inventory.status === "failed" && !retryReady(inventory.retryAfter)) return null;
    const orderPrompt = renderMemberOrderPrompt(selectedPlannerPrompt, inventory.descriptionOutput || inventory.sceneDescription, inventory.things);
    const planning = { ...inventory, orderPrompt, status: "ordering" as const };
    storeMemberInventory(planning);
    const image = await asDataUrl(inventory.sourceImage);
    if (!image) {
     const failed = { ...planning, orderError: `Could not load planner input image: ${inventory.sourceImage}`, status: "failed" as const, retryAfter: Date.now() + LLM_RETRY_DELAY_MS, attempts: (inventory.attempts || 0) + 1 };
     storeMemberInventory(failed);
     scheduleRetry();
     return null;
    }
    try {
     const payload = await invokeCachedModel(effectivePlannerModel, orderPrompt, inventory.sourceImage, image, 120, inventory.status === "failed", "planner");
     const orderOutput = typeof payload.text === "string" ? payload.text.trim() : "";
     const formatted = formatDetectedJson(orderOutput);
     const parsed = formatted.detected ? JSON.parse(formatted.text) as Record<string, unknown> : {};
     const requestedOrder = Array.isArray(parsed.order) ? parsed.order.map(String) : [];
     const byName = new Map(inventory.things.map((thing) => [thing.name.toLowerCase(), thing]));
     const orderedNames = requestedOrder
       .map((name) => byName.get(name.toLowerCase())?.name || "")
       .filter((name, index, names) => Boolean(name) && names.indexOf(name) === index);
     if (!orderedNames.length) {
       const failed = { ...planning, orderOutput, orderError: "Planner returned no recognized object order.", status: "failed" as const, retryAfter: Date.now() + LLM_RETRY_DELAY_MS, attempts: (inventory.attempts || 0) + 1 };
       storeMemberInventory(failed);
       scheduleRetry();
       return null;
     }
     const omitted = inventory.things.map((thing) => thing.name).filter((name) => !orderedNames.includes(name));
     const extractionOrder = [...orderedNames, ...omitted];
     const completed: MemberInventory = {
       ...planning,
       orderOutput,
       extractionOrder,
       orderError: omitted.length ? `Planner omitted ${omitted.length} object(s) from order; appended last.` : undefined,
       status: "done",
     };
     storeMemberInventory(completed);
     say(`P${inventory.depth || 0} ${inventory.subjectName || "input"}: ordered ${inventory.things.length} extraction(s)`);
     return completed;
    } catch (reason) {
     const message = reason instanceof Error ? reason.message : String(reason);
     const failed = { ...planning, orderError: message, status: "failed" as const, retryAfter: Date.now() + LLM_RETRY_DELAY_MS, attempts: (inventory.attempts || 0) + 1 };
     storeMemberInventory(failed);
     scheduleRetry();
     say(`✗ planner ${inventory.subjectName || "input"}: ${message}`);
     return null;
    }
  };
  const runRecursivePlanner = (onlyMissing = false) =>
    run("Planning recursive object extraction", async () => {
     if (!isRunnableVisionModel(effectivePlannerModel)) return "pick an enabled Planner vision model first";
     const inventories = memberInventories.filter((inventory) =>
       inventory.things.length > 0
       && (!onlyMissing || (!inventory.extractionOrder?.length && (inventory.status !== "failed" || retryReady(inventory.retryAfter))))
     );
     if (!inventories.length) return "call the Describer on input images first";
     let planned = 0;
     const plannerConcurrency = effectiveCallConcurrency("planner");
     const orderedInventories = cooperativeRetryOrder(inventories, plannerConcurrency, (inventory) => inventory.status === "failed");
     await runConcurrent(orderedInventories, plannerConcurrency, async (inventory) => {
       if (stopRef.current) return;
       if (await planRecursiveInventory(inventory, !onlyMissing)) planned += 1;
     });
     return `Planner complete: ${planned} object image(s) planned`;
    });
  const nextUnextractedThing = (inventory: MemberInventory) => {
    const order = inventory.extractionOrder || [];
    for (let position = 0; position < order.length; position += 1) {
     const thingIndex = inventory.things.findIndex((thing) => thing.name === order[position]);
     if (thingIndex >= 0 && !inventory.things[thingIndex].outputImages?.length) {
       return { thing: inventory.things[thingIndex], thingIndex, position };
     }
    }
    return null;
  };
  const inventoryOutlinesReady = (inventory: MemberInventory) => {
    const pending = inventory.things.filter((thing) => !thing.outputImages?.length);
    return pending.length > 0 && pending.every(hasAlignedOutline);
  };
  const outlineRecursiveThing = async (inventory: MemberInventory, thingIndex: number, force = false): Promise<boolean> => {
    const thing = inventory.things[thingIndex];
    if (!thing || thing.outputImages?.length) return false;
    if (!force && hasAlignedOutline(thing)) return false;
    if (!force && !retryReady(thing.outlineRetryAfter)) return false;
    const position = Math.max(0, inventory.extractionOrder?.indexOf(thing.name) ?? thingIndex);
    const scenePath = inventory.sourceImage;
    updateInventoryThing(inventory.id, thingIndex, { status: "outlining", inputImage: scenePath });
    const image = await asDataUrl(scenePath);
    if (!image) {
     updateInventoryThing(inventory.id, thingIndex, {
       status: "listed",
       outlineError: `Could not load Outliner input image: ${scenePath}`,
       outlineRetryAfter: Date.now() + LLM_RETRY_DELAY_MS,
       outlineAttempts: (thing.outlineAttempts || 0) + 1,
     });
     scheduleRetry();
     return false;
    }
    try {
     const outlineDimensions = await imageDataDimensions(image);
     const outlinePrompt = renderMemberOutlinerPrompt(
       selectedOutlinerPrompt,
       inventory.descriptionOutput || inventory.sceneDescription,
       thing,
       position + 1,
       inventory.extractionOrder?.length || inventory.things.length,
       scenePath,
       outlineDimensions,
     );
     updateInventoryThing(inventory.id, thingIndex, { outlinePrompt, outlineImage: scenePath, outlineDimensions });
     const payload = await invokeCachedModel(
       effectiveOutlinerModel,
       outlinePrompt,
       scenePath,
       image,
       120,
       Boolean(thing.outlineError),
       "outliner",
     );
     const outlineOutput = typeof payload.text === "string" ? payload.text.trim() : "";
     if (/^\s*none[.!]?\s*$/i.test(outlineOutput)) {
       updateInventoryThing(inventory.id, thingIndex, {
         status: "not_found",
         outlineOutput,
         outlineError: "Outliner could not locate this object.",
         outlineRetryAfter: Date.now() + LLM_RETRY_DELAY_MS,
         outlineAttempts: (thing.outlineAttempts || 0) + 1,
       });
       scheduleRetry();
       return false;
     }
     const geometry = outlineOutput.match(/\{[\s\S]*\}/);
     let polygons: number[][][] = [];
     let holes: number[][][] = [];
     let box: number[] | undefined;
     if (geometry) {
       const parsed = JSON.parse(geometry[0]) as Record<string, unknown>;
       polygons = Array.isArray(parsed.polygons)
         ? parsed.polygons.filter((candidate: unknown) => Array.isArray(candidate) && candidate.length >= 3) as number[][][]
         : [];
       holes = Array.isArray(parsed.holes)
         ? parsed.holes.filter((candidate: unknown) => Array.isArray(candidate) && candidate.length >= 3) as number[][][]
         : [];
       if (!polygons.length && Array.isArray(parsed.polygon) && parsed.polygon.length >= 3) polygons = [parsed.polygon as number[][]];
       if (Array.isArray(parsed.box) && parsed.box.length === 4) box = parsed.box.map(Number);
     }
     if (!polygons.length && !box) throw new Error("Outliner returned no usable precise polygons or box.");
     updateInventoryThing(inventory.id, thingIndex, {
       status: "outlined",
       outlinePrompt,
       outlineOutput,
       outlineImage: scenePath,
       outlineDimensions,
       outlinePolygons: polygons,
       outlineHoles: holes,
       outlineBox: box,
       cutoutInstructions: outlineOutput,
       outlineError: undefined,
       outlineRetryAfter: undefined,
     });
     say(`O${inventory.depth || 0} ${thing.name}: outlined Planner position ${position + 1}`);
     return true;
    } catch (reason) {
     const message = reason instanceof Error ? reason.message : String(reason);
     updateInventoryThing(inventory.id, thingIndex, {
       status: "listed",
       outlineError: message,
       outlineRetryAfter: Date.now() + LLM_RETRY_DELAY_MS,
       outlineAttempts: (thing.outlineAttempts || 0) + 1,
     });
     scheduleRetry();
     say(`✗ Outliner ${thing.name}: ${message}`);
     return false;
    }
  };
  const runRecursiveOutliner = (onlyMissing = false) =>
    run("Outlining planned objects independently", async () => {
     if (!isRunnableVisionModel(effectiveOutlinerModel)) return "pick an enabled Outliner vision model first";
     const candidates = memberInventories.flatMap((inventory) => inventory.extractionOrder?.length
       ? inventory.things.map((thing, thingIndex) => ({ inventory, thing, thingIndex })).filter(({ thing }) => {
         if (thing.outputImages?.length) return false;
         const ready = hasAlignedOutline(thing);
         return !onlyMissing || (!ready && retryReady(thing.outlineRetryAfter));
       })
       : []);
     if (!candidates.length) return "call Planner first or all planned objects are already outlined";
     let outlined = 0;
     const outlinerConcurrency = effectiveCallConcurrency("outliner");
     const orderedCandidates = cooperativeRetryOrder(
       candidates,
       outlinerConcurrency,
       ({ thing }) => Boolean(thing.outlineError),
     );
     await runConcurrent(orderedCandidates, outlinerConcurrency, async ({ inventory, thingIndex }) => {
       if (stopRef.current) return;
       if (await outlineRecursiveThing(inventory, thingIndex, !onlyMissing)) outlined += 1;
     });
     return `Outliner complete: ${outlined} single-object outline(s)`;
    });
  const runRecursiveExtractor = (automatic = false) =>
    run("Running recursive extraction and background reconstruction", async () => {
     if (!isRunnableVisionModel(effectiveExtractorModel)) return "pick an enabled Extractor vision model first";
     const inputPaths = new Set([...memberInputPaths]);
     const roots = memberInventories.filter((inventory) => !inventory.parentInventoryId && inputPaths.has(inventory.framePath));
     if (!roots.length) return "call the Describer on input images first";
     const queue = automatic
       ? cooperativeRetryOrder(
         memberInventories.filter((inventory) => {
           return Boolean(inventory.extractionOrder?.length && inventoryOutlinesReady(inventory));
         }),
         effectiveCallConcurrency("extractor"),
         (inventory) => inventory.things.some((thing) => (thing.status === "failed" || thing.status === "not_found") && retryReady(thing.retryAfter)),
       )
       : roots.filter((inventory) => {
         return Boolean(inventory.extractionOrder?.length && inventoryOutlinesReady(inventory));
       });
     const queuedInventoryIds = new Set(queue.map((inventory) => inventory.id));
     const scenes = { ...memberScenes };
     let extracted = 0;
     let step = members.length + 1;
     const processInventory = async (sourceInventory: MemberInventory) => {
       if (stopRef.current) return;
       const inventory = sourceInventory;
       if (!inventory || !inventory.things.length) return;
       let scenePath = scenes[inventory.id] || inventory.sourceImage;
       let things = inventory.things.map((thing) => ({ ...thing }));
       const order = inventory.extractionOrder?.length ? inventory.extractionOrder : things.map((thing) => thing.name);
       storeMemberInventory({ ...inventory, status: "extracting", things });
       for (let orderIndex = 0; orderIndex < order.length; orderIndex++) {
         if (stopRef.current) break;
         const name = order[orderIndex];
         const thingIndex = things.findIndex((thing) => thing.name === name);
         if (thingIndex < 0) continue;
         if (things[thingIndex].outputImages?.length) {
           const existingChild = memberInventories.find((candidate) => candidate.parentInventoryId === inventory.id && candidate.subjectName === things[thingIndex].name);
           const extractedMember = members.find((member) => member.inventoryId === inventory.id && member.name === things[thingIndex].name);
           let child: MemberInventory | null | undefined = existingChild;
           if (!child && recursiveAutomation.advanceLevels && (inventory.depth || 0) < MAX_RECURSIVE_OBJECT_DEPTH) {
             child = await describeRecursiveSubject(
               inventory,
               things[thingIndex].name,
               extractedMember?.nextPassImage || things[thingIndex].outputImages![0],
               (inventory.depth || 0) + 1,
               !automatic,
             );
           }
           if (!automatic && child?.status === "pending") child = await describeRecursiveInventory(child);
           if (!automatic && child?.things.length && !queuedInventoryIds.has(child.id)) {
             queue.push(child);
             queuedInventoryIds.add(child.id);
           }
           continue;
         }
         const thing = things[thingIndex];
         if ((thing.status === "failed" || thing.status === "not_found") && !retryReady(thing.retryAfter)) continue;
         if (!hasAlignedOutline(thing)) break;
         const prompt = renderSharedExtractorPrompt(selectedExtractorPrompt, inventory.descriptionOutput || inventory.sceneDescription, thing, orderIndex + 1, order.length);
         const image = await asDataUrl(scenePath);
         if (!image) {
           things[thingIndex] = { ...thing, status: "failed", error: `Could not load extractor input: ${scenePath}`, retryAfter: Date.now() + LLM_RETRY_DELAY_MS, attempts: (thing.attempts || 0) + 1 };
           scheduleRetry();
           continue;
         }
         things[thingIndex] = { ...thing, status: "extracting", inputImage: scenePath };
         storeMemberInventory({ ...inventory, status: "extracting", things });
         let raw = "";
         try {
           const payload = await invokeCachedModel(effectiveExtractorModel, prompt, scenePath, image, 120, thing.status === "failed" || thing.status === "not_found", "extractor");
           raw = typeof payload.text === "string" ? payload.text.trim() : "";
         } catch (reason) {
           const message = reason instanceof Error ? reason.message : String(reason);
           things[thingIndex] = { ...things[thingIndex], status: "failed", error: message, retryAfter: Date.now() + LLM_RETRY_DELAY_MS, attempts: (thing.attempts || 0) + 1 };
           scheduleRetry();
           continue;
         }
         const geometry = raw.match(/\{[\s\S]*\}/);
         let fillInstructions: Record<string, unknown> = {};
         if (geometry) {
           try {
             const parsed = JSON.parse(geometry[0]);
             fillInstructions = parsed.backgroundFill && typeof parsed.backgroundFill === "object" ? parsed.backgroundFill : {};
           } catch { /* reported below */ }
         }
         if (!Object.keys(fillInstructions).length) {
           things[thingIndex] = { ...things[thingIndex], status: "failed", error: "Extractor returned no usable backgroundFill reconstruction plan.", retryAfter: Date.now() + LLM_RETRY_DELAY_MS, attempts: (thing.attempts || 0) + 1 };
           scheduleRetry();
           continue;
         }
         try {
           const currentStep = step;
           step += 1;
           const cut = await api("member-cut", {
             workspaceId,
             image: scenePath,
             outlineSourceImage: thing.outlineImage,
             outlineSourceDimensions: thing.outlineDimensions,
             polygons: thing.outlinePolygons || [],
             holes: thing.outlineHoles || [],
             box: thing.outlineBox,
             name: thing.name,
             step: currentStep,
             fill: memberFill,
             fillInstructions,
             imageGenerationModelId: effectiveImageOutputModel,
             enlargeForNextPass: recursiveAutomation.enlargeSubobjects,
           });
           const cutout = String(cut.cutout);
           const nextPassImage = String(cut.nextPassImage || cutout);
           const cutBox = (cut.box as number[]) || thing.outlineBox || [0, 0, 0, 0];
           scenePath = String(cut.scene);
           scenes[inventory.id] = scenePath;
           setMemberScenes({ ...scenes });
           things[thingIndex] = {
             ...things[thingIndex],
             status: "extracted",
             outputImages: [cutout],
             extractionAttempts: [{ route: "direct_from_scene", promptSource: "outliner", inputImage: things[thingIndex].inputImage || inventory.sourceImage, prompt, status: "extracted", outputImage: cutout }],
             error: undefined,
             retryAfter: undefined,
             fillInstructions,
           };
           setMembers((current) => [...current, {
             framePath: inventory.framePath,
             frameIndex: inventory.frameIndex,
             name: thing.name,
             cutout,
             box: cutBox,
             step: currentStep,
             status: "pending",
             probeIndex: -1,
             probeLabel: inventory.probeLabel,
             route: "direct_from_scene",
             promptSource: "outliner",
             inputImage: things[thingIndex].inputImage,
             sceneAfter: scenePath,
             inventoryId: inventory.id,
             depth: inventory.depth || 0,
             nextPassImage,
             provenance: String(cut.cutoutProvenance || ""),
             nextPassProvenance: String(cut.nextPassProvenance || ""),
             sceneProvenance: String(cut.sceneProvenance || ""),
           }]);
           extracted += 1;
           storeMemberInventory({ ...inventory, status: "extracting", things });
           if (recursiveAutomation.advanceLevels && (inventory.depth || 0) < MAX_RECURSIVE_OBJECT_DEPTH) {
             const child = await describeRecursiveSubject(inventory, thing.name, nextPassImage, (inventory.depth || 0) + 1, !automatic);
             if (!automatic && child?.things.length && !queuedInventoryIds.has(child.id)) {
               queue.push(child);
               queuedInventoryIds.add(child.id);
             }
           }
           break;
         } catch (reason) {
           const message = reason instanceof Error ? reason.message : String(reason);
           things[thingIndex] = { ...things[thingIndex], status: "failed", error: message, retryAfter: Date.now() + LLM_RETRY_DELAY_MS, attempts: (thing.attempts || 0) + 1 };
           scheduleRetry();
         }
       }
       storeMemberInventory({ ...inventory, status: "done", things });
     };
     if (automatic) {
       await runConcurrent([...queue], effectiveCallConcurrency("extractor"), processInventory);
     } else {
       while (queue.length && !stopRef.current) {
         const sourceInventory = queue.shift();
         if (sourceInventory) await processInventory(sourceInventory);
       }
     }
     return stopRef.current
       ? `Recursive extraction stopped after ${extracted} object(s)`
       : `Recursive Extractor complete: ${extracted} outlined object(s); Outliner advances one object only after each extraction`;
    });
  const extractMemberImages = (through: MemberPipelineStage = "extract") =>
    run(`Calling scene-object ${through} workflow`, async () => {
      if (!isRunnableVisionModel(memberModel)) return "pick an enabled vision-capable model first";
      const inputPaths = new Set(frames.map((frame) => frame.path));
      const inputInventories = memberInventories.filter((inventory) => inventory.probeIndex < 0 && inputPaths.has(inventory.framePath));
      if (!inputInventories.length) return "run Scene Objects Textual Description for the input images first";
      const queued = inputInventories.filter((inventory) => (inventory.describedThings || inventory.things).length);
      if (!queued.length) return "the input images contain no described objects to decompose";
      const pipeRunId = `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 7)}`;
      const activePipeForks = { ...pipeForkSelections };
      const recordPipeFork = (fork: keyof PipeForkSelections, detail: string) => {
        const selection = activePipeForks[fork];
        const label = PIPE_FORK_OPTIONS[fork].find((option) => option.value === selection)?.label || selection;
        const entry: PipeForkHistoryEntry = {
          runId: pipeRunId,
          fork,
          label,
          selection,
          at: new Date().toISOString(),
          detail,
        };
        setPipeForkHistory((current) => [...current.slice(-119), entry]);
      };
      const scenes = { ...memberScenes };
      let extracted = 0;
      for (const inventory of queued) {
        if (stopRef.current) break;
        const sceneKey = inventory.id;
        let scenePath = scenes[sceneKey] || inventory.sourceImage;
        if (!scenePath) {
          updateMemberInventory(inventory.id, (current) => ({ ...current, status: "failed" }));
          say(`✗ ${inventory.probeLabel}: input image is missing; rerun Scene Objects Textual Description`);
          continue;
        }
        const textualDescription = inventory.descriptionOutput || inventory.sceneDescription;
        let describedThings = (inventory.describedThings?.length ? inventory.describedThings : inventory.things).map((thing) => ({ ...thing }));
        const decompositionImage = await asDataUrl(inventory.sourceImage);
        if (!decompositionImage) {
          const message = "Could not load the input image for object decomposition.";
          updateMemberInventory(inventory.id, (current) => ({ ...current, status: "failed", decompositionError: message }));
          say(`✗ ${message}`);
          continue;
        }
        const decompositionPrompt = renderMemberDecompositionPrompt(memberDecompositionPrompt, textualDescription, describedThings);
        updateMemberInventory(inventory.id, (current) => ({ ...current, status: "decomposing", decompositionPrompt, decompositionError: undefined }));
        let decompositionPayload: Record<string, any>;
        try {
          decompositionPayload = await invokeCachedModel(memberModel, decompositionPrompt, inventory.sourceImage, decompositionImage, 120);
        } catch (reason) {
          const message = reason instanceof Error ? reason.message : String(reason);
          updateMemberInventory(inventory.id, (current) => ({ ...current, status: "failed", decompositionPrompt, decompositionError: message }));
          say(`✗ object decomposition: ${message}`);
          continue;
        }
        const decompositionOutput = typeof decompositionPayload.text === "string" ? decompositionPayload.text.trim() : "";
        const formattedDecomposition = formatDetectedJson(decompositionOutput);
        let decomposedTree: MemberObjectTree = {};
        if (formattedDecomposition.detected) {
          const parsed = JSON.parse(formattedDecomposition.text) as Record<string, unknown>;
          decomposedTree = normalizeMemberObjectTree(parsed.objects_with_sub_objects);
        }
        const decompositionWarnings: string[] = [];
        if (!Object.keys(decomposedTree).length) {
          const message = "The model returned no usable objects_with_sub_objects object.";
          updateMemberInventory(inventory.id, (current) => ({ ...current, status: "failed", decompositionPrompt, decompositionOutput, decompositionError: message }));
          say(`✗ ${message}`);
          continue;
        }
        const rootNameLookup = new Map(Object.keys(decomposedTree).map((name) => [name.toLowerCase(), name]));
        const objectsWithSubObjects: MemberObjectTree = {};
        const omittedOriginals: MemberInventoryThing[] = [];
        for (const original of describedThings) {
          const returnedName = rootNameLookup.get(original.name.toLowerCase());
          if (returnedName) objectsWithSubObjects[original.name] = decomposedTree[returnedName];
          else {
            omittedOriginals.push(original);
            objectsWithSubObjects[original.name] = {
              description: original.description,
              visibility: "visible",
              subObjects: {},
            };
          }
        }
        for (const [name, node] of Object.entries(decomposedTree)) {
          if (!rootNameLookup.has(name.toLowerCase()) || !describedThings.some((thing) => thing.name.toLowerCase() === name.toLowerCase())) {
            objectsWithSubObjects[name] = node;
          }
        }
        if (omittedOriginals.length) {
          decompositionWarnings.push(`The model omitted ${omittedOriginals.length} original object(s); they were restored as roots.`);
        }
        const seenNames = new Set<string>();
        let workingThings = flattenMemberObjectTree(objectsWithSubObjects).filter((thing) => {
          const key = thing.name.toLowerCase();
          if (!seenNames.has(key)) {
            seenNames.add(key);
            return true;
          }
          decompositionWarnings.push(`Ignored duplicate globally named object "${thing.name}".`);
          return false;
        });
        const previousByName = new Map(inventory.things.map((thing) => [thing.name.toLowerCase(), thing]));
        workingThings = workingThings.map((thing) => {
          const previous = previousByName.get(thing.name.toLowerCase());
          const baselineExtractionPrompt = previous?.baselineExtractionPrompt || renderMemberExtractionPrompt(textualDescription, thing.name, thing.description);
          return {
            ...thing,
            status: thing.visibility === "hidden" ? "hidden" : previous?.status === "hidden" ? "listed" : previous?.status || "listed",
            baselineExtractionPrompt,
            rewrittenExtractionPrompt: previous?.rewrittenExtractionPrompt,
            extractionPrompt: previous?.rewrittenExtractionPrompt || previous?.extractionPrompt || baselineExtractionPrompt,
            inputImage: previous?.inputImage,
            outputImages: previous?.outputImages,
            extractionRoutes: previous?.extractionRoutes,
            extractionAttempts: previous?.extractionAttempts,
            parentReferenceImage: previous?.parentReferenceImage,
            promptWriterPrompt: previous?.promptWriterPrompt,
            promptWriterOutput: previous?.promptWriterOutput,
            promptWriterError: previous?.promptWriterError,
            error: previous?.error,
          };
        });
        const decompositionWarning = decompositionWarnings.length ? decompositionWarnings.join(" ") : undefined;
        updateMemberInventory(inventory.id, (current) => ({
          ...current,
          status: "prompting",
          describedThings,
          objectsWithSubObjects,
          decompositionPrompt,
          decompositionOutput,
          decompositionWarning,
          decompositionError: undefined,
          things: workingThings,
        }));
        const hiddenCount = workingThings.filter((thing) => thing.visibility === "hidden").length;
        say(`◫ [${inventory.probeLabel}] objects_with_sub_objects: ${describedThings.length} root(s), ${workingThings.length} total, ${hiddenCount} hidden`);
        const inSelectedInventoryPipe = (thing: MemberInventoryThing) => activePipeForks.inventory === "both"
          || (activePipeForks.inventory === "found_objects" ? !thing.parentName : Boolean(thing.parentName));
        const selectedThingRows = workingThings
          .map((thing, index) => ({ thing, index }))
          .filter(({ thing }) => thing.visibility !== "hidden" && inSelectedInventoryPipe(thing));
        recordPipeFork("inventory", `${inventory.probeLabel}: ${selectedThingRows.length} of ${workingThings.length} hierarchy entries continue`);
        if (through === "hierarchy") {
          updateMemberInventory(inventory.id, (current) => ({ ...current, status: "done", things: workingThings }));
          continue;
        }
        const promptTargets = activePipeForks.prompts === "baseline" ? [] : selectedThingRows;
        say(`✎ [${inventory.probeLabel}] writing ${promptTargets.length} object extraction prompt(s)`);
        for (const { index: thingIndex } of promptTargets) {
          if (stopRef.current) break;
          const thing = workingThings[thingIndex];
          const writerPrompt = renderObjectPromptWriter(objectPromptWriter, textualDescription, thing);
          let writerOutput = "";
          let generatedPrompt = "";
          let writerError = "";
          try {
            const payload = await invokeCachedModel(memberModel, writerPrompt, inventory.sourceImage, decompositionImage, 120);
            writerOutput = typeof payload.text === "string" ? payload.text.trim() : "";
            const formatted = formatDetectedJson(writerOutput);
            if (formatted.detected) {
              const parsed = JSON.parse(formatted.text) as Record<string, unknown>;
              const returnedName = String(parsed.name || thing.name).trim();
              if (returnedName.toLowerCase() !== thing.name.toLowerCase()) {
                writerError = `Prompt writer returned name "${returnedName}" instead of "${thing.name}".`;
              } else {
                generatedPrompt = String(parsed.extraction_prompt || parsed.extractionPrompt || "").trim();
              }
            }
            if (!generatedPrompt && !writerError) writerError = "Prompt writer returned no extraction_prompt.";
          } catch (reason) {
            writerError = reason instanceof Error ? reason.message : String(reason);
          }
          workingThings[thingIndex] = {
            ...thing,
            rewrittenExtractionPrompt: generatedPrompt || undefined,
            extractionPrompt: generatedPrompt || thing.baselineExtractionPrompt || renderMemberExtractionPrompt(textualDescription, thing.name, thing.description),
            promptWriterPrompt: writerPrompt,
            promptWriterOutput: writerOutput,
            promptWriterError: writerError || undefined,
          };
          updateMemberInventory(inventory.id, (current) => ({ ...current, things: workingThings }));
          say(`${generatedPrompt ? "✎" : "△"} [${inventory.probeLabel}] object prompt: ${thing.name}${writerError ? ` · ${writerError}` : ""}`);
        }
        if (stopRef.current) break;
        recordPipeFork("prompts", `${inventory.probeLabel}: ${promptTargets.filter(({ index }) => Boolean(workingThings[index].rewrittenExtractionPrompt)).length} LLM rewrite(s), ${selectedThingRows.length} baseline prompt(s) available`);
        if (through === "prompts") {
          updateMemberInventory(inventory.id, (current) => ({ ...current, status: "done", things: workingThings }));
          continue;
        }
        updateMemberInventory(inventory.id, (current) => ({ ...current, status: "ordering", things: workingThings }));

        const extractionCandidates = workingThings.map((thing, index) => ({ thing, index })).filter(({ thing }) => thing.visibility !== "hidden" && inSelectedInventoryPipe(thing));
        if (!extractionCandidates.length) {
          updateMemberInventory(inventory.id, (current) => ({ ...current, status: "done" }));
          say(`◫ [${inventory.probeLabel}] no visible objects remain to extract`);
          continue;
        }
        const orderPrompt = renderMemberOrderPrompt(memberOrderPrompt, textualDescription, extractionCandidates.map(({ thing }) => thing));
        const orderImage = await asDataUrl(scenePath);
        if (!orderImage) {
          updateMemberInventory(inventory.id, (current) => ({ ...current, status: "failed", orderPrompt, orderError: "Could not load the input image for extraction ordering." }));
          continue;
        }
        let orderPayload: Record<string, any>;
        try {
          orderPayload = await invokeCachedModel(memberModel, orderPrompt, scenePath, orderImage, 120);
        } catch (reason) {
          const message = reason instanceof Error ? reason.message : String(reason);
          updateMemberInventory(inventory.id, (current) => ({ ...current, status: "failed", orderPrompt, orderError: message }));
          say(`✗ extraction order: ${message}`);
          continue;
        }
        const orderOutput = typeof orderPayload.text === "string" ? orderPayload.text.trim() : "";
        const formattedOrder = formatDetectedJson(orderOutput);
        let requestedOrder: unknown[] = [];
        let requestedMethods: Record<string, unknown> = {};
        if (formattedOrder.detected) {
          try {
            const parsed = JSON.parse(formattedOrder.text);
            requestedOrder = Array.isArray(parsed.order) ? parsed.order : [];
            requestedMethods = parsed.methods && typeof parsed.methods === "object" && !Array.isArray(parsed.methods) ? parsed.methods : {};
          } catch { /* handled as an invalid order below */ }
        }
        const byName = new Map(extractionCandidates.map(({ thing, index }) => [thing.name.toLowerCase(), index]));
        const orderedIndices: number[] = [];
        const unknownOrderNames: string[] = [];
        for (const value of requestedOrder) {
          const requestedName = String(typeof value === "string" ? value : (value as Record<string, unknown>)?.name || "").trim();
          const index = byName.get(requestedName.toLowerCase());
          if (index !== undefined) {
            if (!orderedIndices.includes(index)) orderedIndices.push(index);
          } else if (requestedName) {
            unknownOrderNames.push(requestedName);
          }
        }
        if (!orderedIndices.length) {
          const message = "Ordering model returned no recognized object names.";
          updateMemberInventory(inventory.id, (current) => ({ ...current, status: "failed", orderPrompt, orderOutput, orderError: message }));
          say(`✗ ${message}`);
          continue;
        }
        const omittedIndices = extractionCandidates.map(({ index }) => index).filter((index) => !orderedIndices.includes(index));
        const extractionIndices = [...orderedIndices, ...omittedIndices];
        let correctedParentOrder = false;
        for (let pass = 0; pass < extractionIndices.length; pass++) {
          for (let childPosition = 0; childPosition < extractionIndices.length; childPosition++) {
            const childIndex = extractionIndices[childPosition];
            const parentName = workingThings[childIndex].parentName;
            const parentIndex = parentName ? byName.get(parentName.toLowerCase()) : undefined;
            if (parentIndex === undefined) continue;
            const parentPosition = extractionIndices.indexOf(parentIndex);
            if (parentPosition >= 0 && parentPosition < childPosition) {
              extractionIndices.splice(childPosition, 1);
              extractionIndices.splice(parentPosition, 0, childIndex);
              correctedParentOrder = true;
            }
          }
        }
        const orderWarnings = [
          unknownOrderNames.length ? `Ignored unknown object name(s): ${unknownOrderNames.join(", ")}.` : "",
          omittedIndices.length ? `Ordering omitted ${omittedIndices.length} object(s); appended them last.` : "",
          correctedParentOrder ? "Corrected the returned order so every sub-object is extracted before its parent." : "",
        ].filter(Boolean);
        const extractionOrder = extractionIndices.map((index) => workingThings[index].name);
        const requestedMethodsByName = new Map(Object.entries(requestedMethods).map(([name, methods]) => [name.toLowerCase(), methods]));
        workingThings = workingThings.map((thing) => {
          if (thing.visibility === "hidden") return { ...thing, extractionRoutes: [] };
          if (!inSelectedInventoryPipe(thing)) return { ...thing, extractionRoutes: [] };
          const rawMethods = requestedMethodsByName.get(thing.name.toLowerCase());
          const methodValues = (Array.isArray(rawMethods) ? rawMethods : rawMethods ? [rawMethods] : [])
            .map(String)
            .filter((method): method is MemberExtractionRoute => method === "direct_from_scene" || method === "from_parent_cutout");
          const requestedRoutes = [...new Set(methodValues)];
          if (!thing.parentName) {
            if (requestedRoutes.includes("from_parent_cutout")) orderWarnings.push(`Root object ${thing.name} cannot use from_parent_cutout; using direct_from_scene.`);
            return { ...thing, extractionRoutes: ["direct_from_scene"] };
          }
          if (activePipeForks.routes === "direct_from_scene") return { ...thing, extractionRoutes: ["direct_from_scene"] };
          if (activePipeForks.routes === "from_parent_cutout") return { ...thing, extractionRoutes: ["from_parent_cutout"] };
          if (activePipeForks.routes === "both") return { ...thing, extractionRoutes: ["direct_from_scene", "from_parent_cutout"] };
          return { ...thing, extractionRoutes: requestedRoutes.length ? requestedRoutes : ["direct_from_scene", "from_parent_cutout"] };
        });
        recordPipeFork("routes", `${inventory.probeLabel}: ${extractionCandidates.length} object(s) entered ${PIPE_FORK_OPTIONS.routes.find((option) => option.value === activePipeForks.routes)?.label || activePipeForks.routes}`);
        const orderError = orderWarnings.length ? orderWarnings.join(" ") : undefined;
        updateMemberInventory(inventory.id, (current) => ({ ...current, status: "extracting", orderPrompt, orderOutput, extractionOrder, orderError, things: workingThings }));
        say(`↕ [${inventory.probeLabel}] extraction order: ${extractionOrder.join(" → ")}`);
        if (through === "routes") {
          updateMemberInventory(inventory.id, (current) => ({ ...current, status: "done" }));
          continue;
        }
        const allByName = new Map(workingThings.map((thing, index) => [thing.name.toLowerCase(), index]));
        const activePromptSources: MemberPromptSource[] = activePipeForks.prompts === "both"
          ? ["baseline", "llm_rewrite"]
          : [activePipeForks.prompts];
        let step = members.filter((member) => member.framePath === inventory.framePath && member.probeIndex === inventory.probeIndex).length + 1;
        const patchWorkingThing = (thingIndex: number, patch: Partial<MemberInventoryThing>) => {
          workingThings[thingIndex] = { ...workingThings[thingIndex], ...patch };
          updateInventoryThing(inventory.id, thingIndex, patch);
        };
        const recordAttempt = (thingIndex: number, attempt: MemberExtractionAttempt) => {
          const attempts = [
            ...(workingThings[thingIndex].extractionAttempts || []).filter((existing) => existing.route !== attempt.route || existing.promptSource !== attempt.promptSource || existing.inputImage !== attempt.inputImage),
            attempt,
          ];
          patchWorkingThing(thingIndex, { extractionAttempts: attempts });
        };
        const locateAndCut = async (
          thingIndex: number,
          inputPath: string,
          route: MemberExtractionRoute,
          promptSource: MemberPromptSource,
          routeContext: string,
          trackAttempt: boolean,
          outputName: string,
        ): Promise<{ cutout: string; scene: string; box: number[]; prompt: string } | null> => {
          const thing = workingThings[thingIndex];
          const sourcePrompt = promptSource === "llm_rewrite" ? thing.rewrittenExtractionPrompt : thing.baselineExtractionPrompt;
          if (!sourcePrompt) {
            const message = `${promptSource.replaceAll("_", " ")} prompt is unavailable for ${thing.name}.`;
            if (trackAttempt) recordAttempt(thingIndex, { route, promptSource, inputImage: inputPath, prompt: "", status: "failed", error: message });
            say(`✗ ${message}`);
            return null;
          }
          const basePrompt = normalizeMemberPromptLabels(sourcePrompt);
          const prompt = `${basePrompt}\nEXTRACTION ROUTE: ${route}.\n${routeContext}`;
          if (trackAttempt) {
            recordAttempt(thingIndex, { route, promptSource, inputImage: inputPath, prompt, status: "extracting" });
            patchWorkingThing(thingIndex, { status: "extracting", inputImage: inputPath, error: undefined });
          }
          const image = await asDataUrl(inputPath);
          if (!image) {
            const message = `Could not load extraction input: ${inputPath}`;
            if (trackAttempt) recordAttempt(thingIndex, { route, promptSource, inputImage: inputPath, prompt, status: "failed", error: message });
            return null;
          }
          let payload: Record<string, any>;
          try {
            payload = await invokeCachedModel(memberModel, prompt, inputPath, image, 120);
          } catch (reason) {
            const message = reason instanceof Error ? reason.message : String(reason);
            if (trackAttempt) recordAttempt(thingIndex, { route, promptSource, inputImage: inputPath, prompt, status: "failed", error: message });
            say(`✗ ${thing.name} · ${route}: ${message}`);
            return null;
          }
          const raw = typeof payload.text === "string" ? payload.text.trim() : "";
          if (/^\s*none[.!]?\s*$/i.test(raw)) {
            if (trackAttempt) recordAttempt(thingIndex, { route, promptSource, inputImage: inputPath, prompt, status: "not_found", error: "The model could not locate this listed thing by this route." });
            return null;
          }
          const match = raw.match(/\{[\s\S]*\}/);
          let polygon: number[][] | null = null;
          let box: number[] | null = null;
          if (match) {
            try {
              const parsed = JSON.parse(match[0]);
              polygon = Array.isArray(parsed.polygon) && parsed.polygon.length >= 3 ? parsed.polygon : null;
              box = Array.isArray(parsed.box) && parsed.box.length === 4 ? parsed.box.map(Number) : null;
            } catch { /* reported as an unusable geometry response below */ }
          }
          if (!polygon && !box) {
            if (trackAttempt) recordAttempt(thingIndex, { route, promptSource, inputImage: inputPath, prompt, status: "failed", error: "The model returned no usable polygon or box." });
            return null;
          }
          try {
            const cut = await api("member-cut", { workspaceId, image: inputPath, polygon, box, name: outputName, step, fill: memberFill });
            step += 1;
            const result = {
              cutout: String(cut.cutout),
              scene: String(cut.scene),
              box: (cut.box as number[]) || box || [0, 0, 0, 0],
              prompt,
            };
            if (trackAttempt) recordAttempt(thingIndex, { route, promptSource, inputImage: inputPath, prompt, status: "extracted", outputImage: result.cutout });
            return result;
          } catch (reason) {
            const message = reason instanceof Error ? reason.message : String(reason);
            if (trackAttempt) recordAttempt(thingIndex, { route, promptSource, inputImage: inputPath, prompt, status: "failed", error: message });
            say(`✗ ${thing.name} · ${route}: ${message}`);
            return null;
          }
        };
        const registerRouteOutput = (thingIndex: number, route: MemberExtractionRoute, promptSource: MemberPromptSource, inputPath: string, cut: { cutout: string; scene: string; box: number[] }) => {
          const thing = workingThings[thingIndex];
          const outputImages = [...new Set([...(thing.outputImages || []), cut.cutout])];
          patchWorkingThing(thingIndex, { status: "extracted", inputImage: inputPath, outputImages, error: undefined });
          setMembers((current) => current.some((member) => member.cutout === cut.cutout) ? current : [...current, {
            framePath: inventory.framePath,
            frameIndex: inventory.frameIndex,
            name: thing.name,
            cutout: cut.cutout,
            box: cut.box,
            step: step - 1,
            status: "pending",
            probeIndex: inventory.probeIndex,
            probeLabel: inventory.probeLabel,
            route,
            promptSource,
            inputImage: inputPath,
            sceneAfter: cut.scene,
          }]);
          extracted += 1;
          say(`✂ [${inventory.probeLabel}] ${thing.name} via ${route} · ${promptSource}`);
        };

        say(`② [${inventory.probeLabel}] direct-from-scene pass`);
        for (const thingIndex of extractionIndices) {
          if (stopRef.current) break;
          const thing = workingThings[thingIndex];
          if (!thing.extractionRoutes?.includes("direct_from_scene")) continue;
          const inputPath = scenePath;
          let nextScenePath = "";
          for (const promptSource of activePromptSources) {
            if (workingThings[thingIndex].extractionAttempts?.some((attempt) => attempt.route === "direct_from_scene" && attempt.promptSource === promptSource && (attempt.status === "extracted" || attempt.status === "accepted"))) continue;
            const cut = await locateAndCut(
              thingIndex,
              inputPath,
              "direct_from_scene",
              promptSource,
              "Locate the object in the current progressively reduced full-scene image. Coordinates are relative to this scene.",
              true,
              `${thing.name}_${promptSource}`,
            );
            if (!cut) continue;
            if (!nextScenePath) nextScenePath = cut.scene;
            registerRouteOutput(thingIndex, "direct_from_scene", promptSource, inputPath, cut);
          }
          if (nextScenePath) {
            scenePath = nextScenePath;
            scenes[sceneKey] = scenePath;
            setMemberScenes({ ...scenes });
          }
        }

        const parentReferences = new Map<string, string>();
        const ensureParentReference = async (thingIndex: number): Promise<string | null> => {
          const thing = workingThings[thingIndex];
          const key = thing.name.toLowerCase();
          const knownReference = parentReferences.get(key);
          if (knownReference) return knownReference;
          if (thing.parentReferenceImage && await asDataUrl(thing.parentReferenceImage)) {
            parentReferences.set(key, thing.parentReferenceImage);
            return thing.parentReferenceImage;
          }
          let inputPath = inventory.sourceImage;
          if (thing.parentName) {
            const parentIndex = allByName.get(thing.parentName.toLowerCase());
            if (parentIndex === undefined) return null;
            const parentReference = await ensureParentReference(parentIndex);
            if (!parentReference) return null;
            inputPath = parentReference;
          }
          const route: MemberExtractionRoute = thing.parentName ? "from_parent_cutout" : "direct_from_scene";
          const referencePromptSource: MemberPromptSource = thing.rewrittenExtractionPrompt && activePromptSources.includes("llm_rewrite") ? "llm_rewrite" : "baseline";
          const cut = await locateAndCut(
            thingIndex,
            inputPath,
            route,
            referencePromptSource,
            "REFERENCE PASS: extract an intact image of this parent object for locating its keyed sub-objects. Do not use a previously reduced scene.",
            false,
            `${thing.name}_for_sub_objects`,
          );
          if (!cut) return null;
          parentReferences.set(key, cut.cutout);
          patchWorkingThing(thingIndex, { parentReferenceImage: cut.cutout });
          return cut.cutout;
        };

        say(`③ [${inventory.probeLabel}] from-parent-cutout pass`);
        const parentRouteScenes = new Map<string, string>();
        for (const thingIndex of extractionIndices) {
          if (stopRef.current) break;
          const thing = workingThings[thingIndex];
          if (!thing.parentName || !thing.extractionRoutes?.includes("from_parent_cutout")) continue;
          if (thing.extractionAttempts?.some((attempt) => attempt.route === "from_parent_cutout" && (attempt.status === "extracted" || attempt.status === "accepted"))) continue;
          const parentIndex = allByName.get(thing.parentName.toLowerCase());
          if (parentIndex === undefined) continue;
          const parentReference = await ensureParentReference(parentIndex);
          if (!parentReference) {
            const message = `Could not create the ${thing.parentName} reference image required for parent-cutout extraction.`;
            recordAttempt(thingIndex, { route: "from_parent_cutout", promptSource: activePromptSources[0], inputImage: inventory.sourceImage, prompt: "", status: "failed", error: message });
            continue;
          }
          const parentKey = thing.parentName.toLowerCase();
          const inputPath = parentRouteScenes.get(parentKey) || parentReference;
          let nextParentScene = "";
          for (const promptSource of activePromptSources) {
            if (workingThings[thingIndex].extractionAttempts?.some((attempt) => attempt.route === "from_parent_cutout" && attempt.promptSource === promptSource && (attempt.status === "extracted" || attempt.status === "accepted"))) continue;
            const cut = await locateAndCut(
              thingIndex,
              inputPath,
              "from_parent_cutout",
              promptSource,
              `The attached image is an independently extracted image of parent "${thing.parentName}". Locate only its keyed sub-object "${thing.name}"; coordinates are relative to this parent image.`,
              true,
              `${thing.name}_${promptSource}`,
            );
            if (!cut) continue;
            if (!nextParentScene) nextParentScene = cut.scene;
            registerRouteOutput(thingIndex, "from_parent_cutout", promptSource, inputPath, cut);
          }
          if (nextParentScene) parentRouteScenes.set(parentKey, nextParentScene);
        }
        recordPipeFork("routes", `${inventory.probeLabel}: ${extracted} output variant(s) created so far in run ${pipeRunId}`);
        workingThings = workingThings.map((thing) => {
          if (thing.visibility === "hidden") return { ...thing, status: "hidden" };
          if (!inSelectedInventoryPipe(thing)) return { ...thing, status: "listed", error: undefined };
          if (thing.outputImages?.length) return { ...thing, status: thing.status === "accepted" ? "accepted" : "extracted", error: undefined };
          const attempts = thing.extractionAttempts || [];
          const notFound = attempts.length > 0 && attempts.every((attempt) => attempt.status === "not_found");
          return {
            ...thing,
            status: thing.status === "returned" ? "returned" : notFound ? "not_found" : "failed",
            error: attempts.find((attempt) => attempt.error)?.error || (thing.status === "returned" ? undefined : "No configured extraction route produced an image."),
          };
        });
        updateMemberInventory(inventory.id, (current) => ({ ...current, status: "done", things: workingThings }));
      }
      return stopRef.current
        ? `Scene object ${through} workflow stopped after creating ${extracted} image(s)`
        : `Scene object ${through} workflow complete across ${queued.length} input image(s)${through === "extract" ? ` · ${extracted} output image(s)` : ""}`;
    });
  const acceptMember = (at: number) => {
    const member = members[at];
    if (!member || member.status !== "pending") return;
    setFrames((current) => current.map((frame) => (frame.path === member.framePath && !frame.characters.some((existing) => existing.toLowerCase() === member.name.toLowerCase()) ? { ...frame, characters: [...frame.characters, member.name] } : frame)));
    setMembers((current) => current.map((entry, index) => (index === at ? { ...entry, status: "accepted" } : entry)));
    setMemberInventories((current) => current.map((inventory) => (member.inventoryId ? inventory.id === member.inventoryId : inventory.framePath === member.framePath && inventory.probeIndex === member.probeIndex) ? {
      ...inventory,
      things: inventory.things.map((thing) => thing.name.toLowerCase() === member.name.toLowerCase() ? {
        ...thing,
        status: "accepted",
        extractionAttempts: thing.extractionAttempts?.map((attempt) => attempt.outputImage === member.cutout ? { ...attempt, status: "accepted" } : attempt),
      } : thing),
    } : inventory));
    say(`✓ ${member.name}`);
  };
  const rejectMember = (at: number) =>
    run("Returning member", async () => {
      const member = members[at];
      if (!member || member.status === "rejected") return "already returned";
      const sceneKey = member.inventoryId || `${member.probeIndex}:${member.framePath}`;
      const scene = member.route === "from_parent_cutout" ? member.sceneAfter : memberScenes[sceneKey];
      if (scene) {
        const payload = await api("member-return", { workspaceId, scene, cutout: member.cutout, box: member.box });
        if (member.route !== "from_parent_cutout") setMemberScenes((current) => ({ ...current, [sceneKey]: String(payload.scene) }));
      }
      setFrames((current) => current.map((frame) => (frame.path === member.framePath ? { ...frame, characters: frame.characters.filter((existing) => existing.toLowerCase() !== member.name.toLowerCase()) } : frame)));
      setMembers((current) => current.map((entry, index) => (index === at ? { ...entry, status: "rejected" } : entry)));
      setMemberInventories((current) => current.map((inventory) => (member.inventoryId ? inventory.id === member.inventoryId : inventory.framePath === member.framePath && inventory.probeIndex === member.probeIndex) ? {
        ...inventory,
        things: inventory.things.map((thing) => {
          if (thing.name.toLowerCase() !== member.name.toLowerCase()) return thing;
          const outputImages = (thing.outputImages || []).filter((image) => image !== member.cutout);
          return {
            ...thing,
            status: outputImages.length ? "extracted" : "returned",
            outputImages,
            extractionAttempts: thing.extractionAttempts?.map((attempt) => attempt.outputImage === member.cutout ? { ...attempt, status: "rejected" } : attempt),
          };
        }),
      } : inventory));
      return `returned ${member.name} to the scene`;
    });

  // ---- turtle + materialize --------------------------------------------------------
  const [gameId, setGameId] = useState("video-cast-2");
  const turtleLeafCandidates = memberInventories
    .filter((inventory) =>
      Boolean(inventory.parentInventoryId)
      && Boolean(inventory.descriptionOutput)
      && inventory.status === "done"
      && (inventory.things.length === 0 || (inventory.depth || 0) >= MAX_RECURSIVE_OBJECT_DEPTH)
    )
    .map((inventory) => ({
      inventoryId: inventory.id,
      depth: inventory.depth || 0,
      sourceImage: inventory.sourceImage,
      subjectName: inventory.subjectName || `object_${inventory.frameIndex}`,
      description: inventory.sceneDescription,
    }));
  const clearPreTurtleLeaves = () => {
    if (!turtleLeafCandidates.length) return;
    const regenerationDepth = Math.max(0, Math.min(...turtleLeafCandidates.map((candidate) => candidate.depth)) - 1);
    clearRecursiveLevel(regenerationDepth);
    say(`Pre-Turtle leaves cleared; regeneration restarts at extraction level ${regenerationDepth}`);
  };
  const generateTurtlePrograms = (onlyMissing = false) =>
    run("Generating Turtle leaf programs", async () => {
      if (!isRunnableVisionModel(effectiveTurtleModel)) return "pick an enabled Turtle Gen vision model first";
      const candidates = turtleLeafCandidates.filter((candidate) => {
        if (!onlyMissing) return true;
        const artifact = turtleArtifacts[candidate.sourceImage];
        return !artifact || (artifact.status === "failed" && artifact.failedStage === "gen" && retryReady(artifact.retryAfter));
      });
      if (!candidates.length) return onlyMissing ? "no pending Turtle leaves" : "no described leaf object images yet";
      let generated = 0;
      const turtleConcurrency = effectiveCallConcurrency("turtle");
      const orderedCandidates = cooperativeRetryOrder(candidates, turtleConcurrency, (candidate) => turtleArtifacts[candidate.sourceImage]?.failedStage === "gen");
      await runConcurrent(orderedCandidates, turtleConcurrency, async (candidate) => {
        if (stopRef.current) return;
        const prompt = renderTurtlePrompt(selectedTurtlePrompt, candidate.subjectName, candidate.description);
        const previous = turtleArtifacts[candidate.sourceImage];
        const initial: TurtleArtifact = {
          sourceImage: candidate.sourceImage,
          subjectName: candidate.subjectName,
          prompt,
          rawProgram: "",
          status: "generating",
          attempts: previous?.attempts || 0,
        };
        setTurtleArtifacts((current) => ({ ...current, [candidate.sourceImage]: initial }));
        say(`🐢 ${candidate.subjectName}`);
        try {
          const image = await asDataUrl(candidate.sourceImage);
          if (!image) throw new Error(`Could not load Turtle input: ${candidate.sourceImage}`);
          const payload = await invokeCachedModel(effectiveTurtleModel, prompt, candidate.sourceImage, image, 180, previous?.status === "failed", "turtle");
          const rawProgram = typeof payload.text === "string" ? payload.text.trim() : JSON.stringify(payload);
          setTurtleArtifacts((current) => ({
            ...current,
            [candidate.sourceImage]: {
              ...initial,
              rawProgram,
              status: "generated",
              error: undefined,
              failedStage: undefined,
              retryAfter: undefined,
            },
          }));
          generated += 1;
        } catch (reason) {
          const error = reason instanceof Error ? reason.message : String(reason);
          setTurtleArtifacts((current) => ({ ...current, [candidate.sourceImage]: { ...initial, status: "failed", failedStage: "gen", error, retryAfter: Date.now() + LLM_RETRY_DELAY_MS, attempts: (initial.attempts || 0) + 1 } }));
          scheduleRetry();
          say(`✗ Turtle Gen ${candidate.subjectName}: ${error}`);
        }
      });
      return `Turtle Gen complete: ${generated} leaf program(s)`;
    });
  const drawTurtlePngs = (onlyMissing = false) =>
    run("Drawing Turtle PNG leaves", async () => {
      if (!isRunnableVisionModel(effectiveTurtlePngModel)) return "pick an enabled Turtle PNG vision model first";
      const candidates = turtleLeafCandidates
        .map((candidate) => ({ candidate, artifact: turtleArtifacts[candidate.sourceImage] }))
        .filter(({ artifact }) => artifact?.rawProgram && (!onlyMissing || artifact.status === "generated" || (artifact.status === "failed" && artifact.failedStage === "png" && retryReady(artifact.retryAfter))))
        .map(({ candidate, artifact }) => ({ candidate, artifact: artifact! }));
      if (!candidates.length) return onlyMissing ? "no generated Turtle programs are waiting for PNG" : "generate Turtle leaf programs first";
      let rendered = 0;
      const turtlePngConcurrency = effectiveCallConcurrency("turtlePng");
      const orderedCandidates = cooperativeRetryOrder(candidates, turtlePngConcurrency, ({ artifact }) => artifact.failedStage === "png");
      await runConcurrent(orderedCandidates, turtlePngConcurrency, async ({ candidate, artifact }) => {
        if (stopRef.current) return;
        const pngPrompt = renderTurtlePngPrompt(selectedTurtlePngPrompt, candidate.subjectName, candidate.description, artifact.rawProgram);
        setTurtleArtifacts((current) => ({ ...current, [candidate.sourceImage]: { ...artifact, pngPrompt, status: "drawing" } }));
        try {
          const image = await asDataUrl(candidate.sourceImage);
          if (!image) throw new Error(`Could not load Turtle PNG input: ${candidate.sourceImage}`);
          const payload = await invokeCachedModel(effectiveTurtlePngModel, pngPrompt, candidate.sourceImage, image, 180, artifact.status === "failed", "turtlePng");
          const pngProgram = typeof payload.text === "string" ? payload.text.trim() : JSON.stringify(payload);
          const result = await api("turtle-render", {
            workspaceId,
            sourceImage: candidate.sourceImage,
            subjectName: candidate.subjectName,
            modelId: effectiveTurtlePngModel,
            prompt: pngPrompt,
            program: pngProgram,
          });
          setTurtleArtifacts((current) => ({
            ...current,
            [candidate.sourceImage]: {
              ...artifact,
              pngPrompt,
              pngProgram,
              programPath: String(result.programPath || ""),
              renderedImage: String(result.renderedImage || ""),
              provenance: String(result.provenance || ""),
              status: "rendered",
              error: undefined,
              failedStage: undefined,
              retryAfter: undefined,
            },
          }));
          rendered += 1;
        } catch (reason) {
          const error = reason instanceof Error ? reason.message : String(reason);
          setTurtleArtifacts((current) => ({ ...current, [candidate.sourceImage]: { ...artifact, pngPrompt, status: "failed", failedStage: "png", error, retryAfter: Date.now() + LLM_RETRY_DELAY_MS, attempts: (artifact.attempts || 0) + 1 } }));
          scheduleRetry();
          say(`✗ Turtle PNG ${candidate.subjectName}: ${error}`);
        }
      });
      return `Turtle PNG complete: ${rendered} terminal image(s)`;
    });
  const materialize = () =>
    run("Materializing recording", async () => {
      const bySource = new Map(output.map((entry) => [entry.source, entry.path]));
      const payload = await api("materialize", { workspaceId, gameId, frames: frames.map((frame) => ({ ...frame, path: bySource.get(frame.path) || frame.path })) });
      const directory = String(payload.gameDirectory || gameId);
      window.setTimeout(() => { window.location.href = `/?workspace=${encodeURIComponent(workspaceId)}&view=arc3-play&game=${encodeURIComponent(directory)}`; }, 600);
      return `recording ready: ${payload.levelDir} — opening Play & Record`;
    });

  const automaticStagesRunningRef = useRef(new Set<keyof LlmCallConcurrency>());
  const [automaticSchedulerTick, setAutomaticSchedulerTick] = useState(0);
  useEffect(() => {
    if (!restoredRef.current || workersHeld) return;
    const selectedRootsNeedDescription = frames.some((frame) => {
     if (!memberInputPaths.has(frame.path)) return false;
     if (automaticDescriptionClaimsRef.current.has(`root:${frame.path}`)) return false;
     const inventory = memberInventories.find((candidate) => candidate.id === `input:${frame.path}`);
     return !inventory || (inventory.status === "failed" ? retryReady(inventory.retryAfter) : !inventory.descriptionOutput);
    });
    const childNeedsDescription = memberInventories.some((inventory) =>
     inventory.parentInventoryId
     && !automaticDescriptionClaimsRef.current.has(`child:${inventory.id}`)
     && (inventory.status === "pending" || (inventory.status === "failed" && retryReady(inventory.retryAfter)))
    );
    const inventoryNeedsPlan = memberInventories.some((inventory) =>
     (inventory.status === "done" || (inventory.status === "failed" && retryReady(inventory.retryAfter)))
     && inventory.things.length > 0
     && !inventory.extractionOrder?.length
    );
    const inventoryNeedsOutline = memberInventories.some((inventory) =>
     Boolean(inventory.extractionOrder?.length)
     && inventory.things.some((thing) =>
       !thing.outputImages?.length
       && !hasAlignedOutline(thing)
       && retryReady(thing.outlineRetryAfter)
     )
    );
    const inventoryNeedsExtraction = memberInventories.some((inventory) =>
     Boolean(inventory.extractionOrder?.length)
     && inventoryOutlinesReady(inventory)
     && Boolean(nextUnextractedThing(inventory) && retryReady(nextUnextractedThing(inventory)?.thing.retryAfter))
    );
    const leafNeedsTurtleGen = turtleLeafCandidates.some((candidate) => {
      const artifact = turtleArtifacts[candidate.sourceImage];
      return !artifact || (artifact.status === "failed" && artifact.failedStage === "gen" && retryReady(artifact.retryAfter));
    });
    const leafNeedsTurtlePng = turtleLeafCandidates.some((candidate) => {
      const artifact = turtleArtifacts[candidate.sourceImage];
      return artifact?.status === "generated" || (artifact?.status === "failed" && artifact.failedStage === "png" && retryReady(artifact.retryAfter));
    });
    const launch = (type: keyof LlmCallConcurrency, task: () => Promise<void>) => {
     const allowsOverlappingRefill = type === "describer";
     if (!allowsOverlappingRefill && automaticStagesRunningRef.current.has(type)) return;
     if (!allowsOverlappingRefill) automaticStagesRunningRef.current.add(type);
     void task().finally(() => {
       if (!allowsOverlappingRefill) automaticStagesRunningRef.current.delete(type);
       setAutomaticSchedulerTick((tick) => tick + 1);
     });
    };
    if (recursiveAutomation.describer && isRunnableVisionModel(effectiveDescriberModel) && (selectedRootsNeedDescription || childNeedsDescription)) {
     launch("describer", () => describeMemberScenes(true));
    }
    if (recursiveAutomation.planner && isRunnableVisionModel(effectivePlannerModel) && inventoryNeedsPlan) {
     launch("planner", () => runRecursivePlanner(true));
    }
    if (recursiveAutomation.outliner && isRunnableVisionModel(effectiveOutlinerModel) && inventoryNeedsOutline) {
     launch("outliner", () => runRecursiveOutliner(true));
    }
    if (recursiveAutomation.extractor && isRunnableVisionModel(effectiveExtractorModel) && inventoryNeedsExtraction) {
     launch("extractor", () => runRecursiveExtractor(true));
    }
    if (recursiveAutomation.turtle && isRunnableVisionModel(effectiveTurtleModel) && leafNeedsTurtleGen) {
     launch("turtle", () => generateTurtlePrograms(true));
    }
    if (recursiveAutomation.turtlePng && isRunnableVisionModel(effectiveTurtlePngModel) && leafNeedsTurtlePng) {
     launch("turtlePng", () => drawTurtlePngs(true));
    }
  }, [
    automaticSchedulerTick,
    frames,
    memberInputPaths,
    memberInventories,
    models,
    effectiveDescriberModel,
    effectiveExtractorModel,
    effectiveOutlinerModel,
    effectivePlannerModel,
    effectiveTurtleModel,
    effectiveTurtlePngModel,
    recursiveAutomation.advanceLevels,
    recursiveAutomation.describer,
    recursiveAutomation.extractor,
    recursiveAutomation.outliner,
    recursiveAutomation.planner,
    recursiveAutomation.turtle,
    recursiveAutomation.turtlePng,
    retryClock,
    workersHeld,
    turtleArtifacts,
  ]);

  const visibleJobs = [sceneJob, frameExtractionJob, captionJob, job].filter((candidate): candidate is JobState => Boolean(candidate));
  const anyBackgroundJobRunning = visibleJobs.some((candidate) => candidate.state === "running");
  const jobProgress = (candidate: JobState) => candidate.total > 0
    ? Math.min(100, Math.round((candidate.done / candidate.total) * 100))
    : 0;
  const selectorScore = (kind: string) => { const score = ledger[`select:${kind}`] || 0; return score ? ` (${score > 0 ? "+" : ""}${score})` : ""; };
  const recursiveRootInventories = memberInventories
    .filter((inventory) => !inventory.parentInventoryId)
    .sort((left, right) => left.frameIndex - right.frameIndex || left.id.localeCompare(right.id));
  const orderedMemberInventories = [...memberInventories].sort((left, right) =>
    left.frameIndex - right.frameIndex
    || (left.depth || 0) - (right.depth || 0)
    || left.id.localeCompare(right.id)
  );
  const selectedRootInventories = frames
    .filter((frame) => memberInputPaths.has(frame.path))
    .map((frame) => memberInventories.find((inventory) => inventory.id === `input:${frame.path}`));
  const undiscoveredSelectedRoots = selectedRootInventories.filter((inventory) => !inventory).length;
  const futureImageObligations = memberInventories.filter((inventory) => !inventory.descriptionOutput).length + undiscoveredSelectedRoots;
  const schedulerPending = (type: keyof LlmCallConcurrency) =>
    llmSchedulerRef.current.waiters.filter((waiter) => waiter.type === type).length;
  const llmStageProgress: Record<keyof LlmCallConcurrency, { pending: number; completed: number }> = {
    describer: {
      pending: schedulerPending("describer") + undiscoveredSelectedRoots + memberInventories.filter((inventory) =>
        !inventory.descriptionOutput && inventory.status !== "describing" && inventory.status !== "ordering"
      ).length,
      completed: memberInventories.filter((inventory) =>
        Boolean(inventory.descriptionOutput) && !inventory.descriptionOutput.startsWith("ERROR:")
      ).length,
    },
    planner: {
      pending: schedulerPending("planner") + futureImageObligations + memberInventories.filter((inventory) =>
        Boolean(inventory.descriptionOutput)
        && inventory.things.length > 0
        && !inventory.extractionOrder?.length
        && inventory.status !== "ordering"
      ).length,
      completed: memberInventories.filter((inventory) => Boolean(inventory.orderOutput)).length,
    },
    outliner: {
      pending: schedulerPending("outliner") + futureImageObligations + memberInventories.reduce((count, inventory) => {
        if (!inventory.descriptionOutput || inventory.things.length === 0) return count;
        if (!inventory.extractionOrder?.length) return count + 1;
        return count + inventory.things.filter((thing) =>
          !thing.outputImages?.length && !hasAlignedOutline(thing) && thing.status !== "outlining"
        ).length;
      }, 0),
      completed: memberInventories.reduce((count, inventory) =>
        count + inventory.things.filter(hasAlignedOutline).length, 0),
    },
    extractor: {
      pending: schedulerPending("extractor") + futureImageObligations + memberInventories.reduce((count, inventory) => {
        if (!inventory.descriptionOutput || inventory.things.length === 0) return count;
        return count + inventory.things.filter((thing) =>
          !thing.outputImages?.length && thing.status !== "extracting"
        ).length;
      }, 0),
      completed: memberInventories.reduce((count, inventory) =>
        count + inventory.things.filter((thing) => Boolean(thing.outputImages?.length)).length, 0),
    },
    turtle: {
      pending: schedulerPending("turtle") + turtleLeafCandidates.filter((candidate) => {
        const artifact = turtleArtifacts[candidate.sourceImage];
        return !artifact || (artifact.status !== "generating" && artifact.status === "failed" && artifact.failedStage === "gen");
      }).length,
      completed: Object.values(turtleArtifacts).filter((artifact) => Boolean(artifact.rawProgram)).length,
    },
    turtlePng: {
      pending: schedulerPending("turtlePng") + Object.values(turtleArtifacts).filter((artifact) =>
        Boolean(artifact.rawProgram) && !artifact.renderedImage && artifact.status !== "drawing"
      ).length,
      completed: Object.values(turtleArtifacts).filter((artifact) => Boolean(artifact.renderedImage)).length,
    },
  };
  const selectedImageStageIndicators = (frame: Frame): WorkflowStageIndicator[] => {
    const inventory = memberInventories.find((candidate) => candidate.id === `input:${frame.path}`);
    if (!inventory) {
      const describing = automaticDescriptionClaimsRef.current.has(`root:${frame.path}`);
      return [
        { label: "D", value: describing ? "…" : "·", state: describing ? "active" : "waiting", detail: describing ? "Describer active" : "waiting for Describer" },
        { label: "P", value: "·", state: "waiting", detail: "waiting for Describer" },
        { label: "O", value: "0/0", state: "waiting", detail: "waiting for Planner" },
        { label: "E", value: "0/0", state: "waiting", detail: "waiting for aligned outlines" },
        { label: "T", value: "0/0", state: "waiting", detail: "waiting for terminal leaves" },
        { label: "I", value: "0/0", state: "waiting", detail: "waiting for Turtle programs" },
      ];
    }
    const described = Boolean(inventory.descriptionOutput) && !inventory.descriptionOutput.startsWith("ERROR:");
    const leaf = described && inventory.things.length === 0;
    const outlined = inventory.things.filter(hasAlignedOutline).length;
    const extracted = inventory.things.filter((thing) => thing.outputImages?.length).length;
    const outlineActive = inventory.things.some((thing) => thing.status === "outlining");
    const outlineRetrying = inventory.things.some((thing) => Boolean(thing.outlineError));
    const extractionActive = inventory.things.some((thing) => thing.status === "extracting");
    const extractionRetrying = inventory.things.some((thing) => thing.status === "failed" || thing.status === "not_found");
    const rootLeaves = turtleLeafCandidates.filter((candidate) =>
      memberInventories.find((candidateInventory) => candidateInventory.id === candidate.inventoryId)?.framePath === frame.path
    );
    const generatedTurtles = rootLeaves.filter((candidate) => {
      const artifact = turtleArtifacts[candidate.sourceImage];
      return artifact && artifact.status !== "generating" && !(artifact.status === "failed" && artifact.failedStage === "gen");
    }).length;
    const renderedImages = rootLeaves.filter((candidate) => turtleArtifacts[candidate.sourceImage]?.status === "rendered").length;
    const turtleActive = rootLeaves.some((candidate) => turtleArtifacts[candidate.sourceImage]?.status === "generating");
    const turtleRetrying = rootLeaves.some((candidate) => {
      const artifact = turtleArtifacts[candidate.sourceImage];
      return artifact?.status === "failed" && artifact.failedStage === "gen";
    });
    const imageActive = rootLeaves.some((candidate) => turtleArtifacts[candidate.sourceImage]?.status === "drawing");
    const imageRetrying = rootLeaves.some((candidate) => {
      const artifact = turtleArtifacts[candidate.sourceImage];
      return artifact?.status === "failed" && artifact.failedStage === "png";
    });
    const dState: WorkflowStageIndicator["state"] = inventory.status === "describing"
      ? "active"
      : described
        ? "complete"
        : inventory.status === "failed"
          ? "retrying"
          : "waiting";
    const pState: WorkflowStageIndicator["state"] = inventory.status === "ordering"
      ? "active"
      : inventory.orderOutput || leaf
        ? "complete"
        : inventory.orderError
          ? "retrying"
          : "waiting";
    const oState: WorkflowStageIndicator["state"] = leaf || (inventory.things.length > 0 && outlined === inventory.things.length)
      ? "complete"
      : outlineActive
        ? "active"
        : outlineRetrying
          ? "retrying"
          : outlined > 0
            ? "partial"
            : "waiting";
    const eState: WorkflowStageIndicator["state"] = leaf || (inventory.things.length > 0 && extracted === inventory.things.length)
      ? "complete"
      : extractionActive
        ? "active"
        : extractionRetrying
          ? "retrying"
          : extracted > 0
            ? "partial"
            : "waiting";
    const tState: WorkflowStageIndicator["state"] = rootLeaves.length > 0 && generatedTurtles === rootLeaves.length
      ? "complete"
      : turtleActive
        ? "active"
        : turtleRetrying
          ? "retrying"
          : generatedTurtles > 0
            ? "partial"
            : "waiting";
    const iState: WorkflowStageIndicator["state"] = rootLeaves.length > 0 && renderedImages === rootLeaves.length
      ? "complete"
      : imageActive
        ? "active"
        : imageRetrying
          ? "retrying"
          : renderedImages > 0
            ? "partial"
            : "waiting";
    return [
      { label: "D", value: described ? String(inventory.things.length) : dState === "active" ? "…" : dState === "retrying" ? "!" : "·", state: dState, detail: dState === "complete" ? `${inventory.things.length} object(s) described` : dState === "retrying" ? inventory.sceneDescription || "Describer retrying" : dState === "active" ? "Describer active" : "waiting for Describer" },
      { label: "P", value: inventory.orderOutput ? String(inventory.extractionOrder?.length || 0) : pState === "active" ? "…" : pState === "retrying" ? "!" : "·", state: pState, detail: pState === "complete" ? leaf ? "not needed for leaf" : `${inventory.extractionOrder?.length || 0} object(s) ordered` : pState === "retrying" ? inventory.orderError || "Planner retrying" : pState === "active" ? "Planner active" : "waiting for described objects" },
      { label: "O", value: `${outlined}/${inventory.things.length}`, state: oState, detail: leaf ? "not needed for leaf" : `${outlined}/${inventory.things.length} aligned outline(s)${outlineRetrying ? " · retries pending" : ""}` },
      { label: "E", value: `${extracted}/${inventory.things.length}`, state: eState, detail: leaf ? "not needed for leaf" : `${extracted}/${inventory.things.length} object(s) extracted${extractionRetrying ? " · retries pending" : ""}` },
      { label: "T", value: `${generatedTurtles}/${rootLeaves.length}`, state: tState, detail: `${generatedTurtles}/${rootLeaves.length} terminal Turtle program(s)${turtleRetrying ? " · retries pending" : ""}` },
      { label: "I", value: `${renderedImages}/${rootLeaves.length}`, state: iState, detail: `${renderedImages}/${rootLeaves.length} terminal image(s) rendered${imageRetrying ? " · retries pending" : ""}` },
    ];
  };
  const selectedRecursiveInventory = memberInventories.find((inventory) => inventory.id === selectedRecursiveInventoryId) || recursiveRootInventories[0] || null;
  const revealRecursiveOutput = (inventoryId: string, sectionId: "memberDescription" | "members", targetPrefix: string) => {
    setCollapsedMap((current) => ({ ...current, [sectionId]: false }));
    const reveal = () => document.getElementById(`${targetPrefix}-${responseCacheHash(inventoryId)}`)?.scrollIntoView({ behavior: "smooth", block: "start" });
    window.setTimeout(reveal, 100);
    window.setTimeout(reveal, 350);
  };
  const recursiveGalleryDepths = [...new Set([0, ...memberInventories.map((inventory) => inventory.depth || 0), ...members.map((member) => member.depth || 0)])].sort((left, right) => left - right);
  const visibleAltImageZoom = pinnedAltImageZoom || altImageZoom;
  const activeImageContext = visibleAltImageZoom || pinnedImageContext || hoverImageContext;
  const activeImageMember = activeImageContext
    ? members.find((member) => member.cutout === activeImageContext.imagePath || member.nextPassImage === activeImageContext.imagePath)
    : undefined;
  const directImageInventory = activeImageContext
    ? memberInventories.find((inventory) =>
        inventory.sourceImage === activeImageContext.imagePath
        || inventory.framePath === activeImageContext.imagePath
        || memberScenes[inventory.id] === activeImageContext.imagePath
      )
    : undefined;
  const childImageInventory = activeImageMember?.inventoryId
    ? memberInventories.find((inventory) => inventory.parentInventoryId === activeImageMember.inventoryId && inventory.subjectName === activeImageMember.name)
    : undefined;
  const activeImageInventory = directImageInventory || childImageInventory;
  const activeImageParentThing = activeImageMember?.inventoryId
    ? memberInventories.find((inventory) => inventory.id === activeImageMember.inventoryId)?.things.find((thing) => thing.name === activeImageMember.name)
    : undefined;
  const activeImageParentDescription = activeImageParentThing?.description || "";
  const activeImageDescription = activeImageInventory?.sceneDescription || "";
  const activeImageDescriberOutput = activeImageInventory?.descriptionOutput || "";
  const activeImagePlannerOutput = activeImageInventory?.orderOutput || "";
  const activeImageOutlinerOutputs = activeImageInventory?.things
    .filter((thing) => thing.outlineOutput || thing.outlineError)
    .map((thing) => ({ name: thing.name, output: thing.outlineOutput, error: thing.outlineError })) || [];
  const activeImagePlannerStatus = activeImagePlannerOutput
    ? "output ready"
    : activeImageInventory?.orderError
      ? `retrying · ${activeImageInventory.orderError}`
      : activeImageInventory?.descriptionOutput
        ? activeImageInventory.things.length ? "queued" : "not required for a leaf with no sub-objects"
        : "waiting for Describer";
  const activeImageProvenancePath = activeImageContext?.imagePath
    ? activeImageContext.imagePath.replace(/\.[^./]+$/, ".provenance.json")
    : "";
  const activeTurtleArtifact = activeImageContext
    ? Object.values(turtleArtifacts).find((artifact) =>
        artifact.sourceImage === activeImageContext.imagePath
        || artifact.renderedImage === activeImageContext.imagePath
        || (activeImageMember && artifact.sourceImage === (activeImageMember.nextPassImage || activeImageMember.cutout))
      )
    : undefined;
  const renderedTurtleArtifacts = Object.values(turtleArtifacts).filter((artifact) => artifact.status === "rendered" && artifact.renderedImage);
  useEffect(() => {
    const imagePath = activeImageContext?.imagePath;
    if (!imagePath) {
      setActiveImageProvenance(null);
      return;
    }
    const cached = imageProvenanceCacheRef.current[imagePath];
    if (cached) {
      setActiveImageProvenance(cached);
      return;
    }
    let cancelled = false;
    setActiveImageProvenance(null);
    void api(`image-provenance?workspaceId=${encodeURIComponent(workspaceId)}&image=${encodeURIComponent(imagePath)}`).then((payload) => {
      if (cancelled) return;
      imageProvenanceCacheRef.current[imagePath] = payload;
      setActiveImageProvenance(payload);
    }).catch(() => {
      if (!cancelled) setActiveImageProvenance({ error: "Provenance JSON is not available for this image." });
    });
    return () => { cancelled = true; };
  }, [activeImageContext?.imagePath, workspaceId]);

  // ---- render -----------------------------------------------------------------------
  return (
    <section className="resource-view video-import-page vi2" onClickCapture={handleImageContextClick} onPointerMove={handleImageZoomPointer} onPointerLeave={() => { hoveredImageRef.current = null; setAltImageZoom(null); setHoverImageContext(null); }}>
      <div className="resource-heading">
        <div>
          <span>KNOWLEDGE INTAKE · GENERATION 2</span>
          <h1>Video Import 2</h1>
          <p>Rebuilt from its own build prompt (see the help tab appendix): import → timeline → the preview stack for building filter chains → probes and entity strips → materialize. Every gallery collapses, every step interrupts.</p>
        </div>
      </div>

      <div className="video-import-activity" role="status" aria-live="polite">
        <div className="video-import-activity-controls">
          <span className={`video-import-activity-dot${busy || anyBackgroundJobRunning ? " is-busy" : ""}`} />
          <b>STATUS</b>
          <label className="video-import-toggle">
            <input type="checkbox" checked={autoCollapseOn} onChange={(event) => setAutoCollapseOn(event.target.checked)} />
            auto-collapse
          </label>
          <label className="video-import-toggle" title="When upstream DATA changes (new video, re-extract), clear the now-stale results below. The workflow itself is never cleared.">
            <input type="checkbox" checked={autoClearData} onChange={(event) => setAutoClearData(event.target.checked)} />
            auto-clear stale data
          </label>
          <label className="video-import-toggle" title="When a chain step is edited, also drop the LATER algorithm steps. Off: the workflow below survives edits above.">
            <input type="checkbox" checked={autoClearAlgorithm} onChange={(event) => setAutoClearAlgorithm(event.target.checked)} />
            auto-clear next algorithm
          </label>
          <label className="video-import-toggle" title="After each effect pick, automatically render all effects on the new output — the loop continues until you turn this off or hit ■ Stop.">
            <input type="checkbox" checked={autoNext77} onChange={(event) => setAutoNext77(event.target.checked)} />
            auto next 77
          </label>
          <button title="Copy the exact page state as JSON" disabled={false} onClick={copyStateJson}>⤓ state</button>
          <button title="Forget the saved state — next load starts clean" onClick={forgetState}>⟲ forget</button>
        </div>
        <div className="video-import-activity-lower">
          <div className="video-import-activity-lines">
            {log.map((line, index) => (
              <span key={`${line.at}-${index}`} className={index === log.length - 1 ? "is-current" : ""}><code>{line.at}</code> {line.text}</span>
            ))}
          </div>
          <button className="video-import-stop" disabled={!busy && !anyBackgroundJobRunning} onClick={stopEverything}>■ Stop</button>
        </div>
      </div>
      {error && <div className="backend-error"><b>Video import error</b><span>{error}</span></div>}
      {visibleJobs.length > 0 && <section className="video-import-media-job-queue">
        <header><b>MEDIA JOB QUEUE</b><small>{visibleJobs.filter((visibleJob) => visibleJob.state === "running").length} active · {visibleJobs.length} visible</small></header>
        {visibleJobs.map((visibleJob) => {
          const progress = jobProgress(visibleJob);
          return (
            <div key={`${visibleJob.kind}:${visibleJob.id}`} className="video-import-progress" role="progressbar" aria-label={`${visibleJob.kind} progress`} aria-valuenow={progress} aria-valuemin={0} aria-valuemax={100}>
              <div className="video-import-progress-track"><div className="video-import-progress-fill" style={{ width: `${visibleJob.state === "done" ? 100 : progress}%` }} /></div>
              <small>
                {visibleJob.state === "running" && `${visibleJob.kind}: ${visibleJob.done}/${visibleJob.total} · ETA ${visibleJob.etaSeconds}s`}
                {visibleJob.state === "done" && `${visibleJob.kind} done in ${visibleJob.elapsedSeconds}s${visibleJob.interrupted ? " (interrupted)" : ""}`}
                {visibleJob.state === "error" && `${visibleJob.kind} failed: ${visibleJob.error}`}
              </small>
            </div>
          );
        })}
      </section>}

      <Section {...section("config", "JSON CONFIG", `the page's exact state as editable JSON${configDraft === null ? " · live" : configValid ? " · editing (applies live)" : " · INVALID JSON — keep typing"}`,
        <>
          <button disabled={busy || configDraft === null} title="Force-apply now and resume tracking the live config" onClick={applyConfigDraft}>⏎ Apply</button>
          <button disabled={configDraft === null} title="Discard edits and track the live config again" onClick={() => setConfigDraft(null)}>↻ live</button>
          <button title="Copy the config JSON" onClick={copyStateJson}>⤓ copy</button>
        </>)}>
        <div className="vi2-body video-import-config-super">
          <SuperControl
            appearance="embedded"
            className="video-import-config-editor-super"
            control={{
              kind: "standard",
              workspaceId,
              source: configDraft ?? JSON.stringify(buildSnapshot(), null, 2),
              sourceScope: "runtime",
              path: `runtime/videoImport/${workspaceId}.config.json`,
              title: "Video Import — page config",
              dirty: configDraft !== null,
              secondary: false,
              busy,
              resource: (() => {
                let doc: Record<string, unknown> = {};
                if (configDraft === null) doc = buildSnapshot() as unknown as Record<string, unknown>;
                else { try { doc = JSON.parse(configDraft) as Record<string, unknown>; } catch { doc = {}; } }
                return { ...doc, kind: "video_import_config", id: `videoImport.${workspaceId}` } as { kind: string; id: string };
              })(),
              initialControlId: "file",
              onChange: (value) => setConfigDraft(value),
              onSave: applyConfigDraft,
              saveLabel: configValid ? "⏎ Apply to flow" : "… invalid JSON",
              actions: [
                { id: "live", label: "↻ track live", disabled: configDraft === null, onInvoke: () => setConfigDraft(null) },
                { id: "copy", label: "⤓ copy", onInvoke: copyStateJson },
                { id: "forget", label: "⟲ forget saved", onInvoke: forgetState },
              ],
            }}
          />
        </div>
      </Section>

      <Section {...section("intake", "INTAKE", `${videos.length} video(s) in the library`)}>
        <div className="vi2-body">
          <div className="video-import-row">
            <select className="video-import-catalog" value="" disabled={busy} onChange={(event) => { const entry = catalog[Number(event.target.value)]; if (entry) { setSource(entry.url); setNameDraft(entry.title); } }}>
              <option value="">catalog… ({catalog.length})</option>
              {catalog.map((entry, index) => (<option key={`${entry.url}-${index}`} value={index}>{entry.title}</option>))}
            </select>
            <select className="video-import-catalog" value="" disabled={busy} onChange={(event) => { if (event.target.value) void importSource(event.target.value); }}>
              <option value="">importables… ({importables.length})</option>
              {importables.map((file) => (<option key={file.path} value={file.path}>{file.name}</option>))}
            </select>
            <input value={source} placeholder="https://… or a movie path you have the rights to" disabled={busy} onChange={(event) => setSource(event.target.value)} />
            <input className="video-import-name" value={nameDraft} placeholder="name (optional)" disabled={busy} onChange={(event) => setNameDraft(event.target.value)} />
            <select value={quality} disabled={busy} onChange={(event) => setQuality(event.target.value)}>
              <option value="480p">480p lo-fi</option>
              <option value="720p">720p</option>
              <option value="1080p">1080p</option>
              <option value="best">best</option>
              <option value="python-direct">🛠 python direct</option>
            </select>
            <button disabled={busy || !source.trim()} onClick={() => void importSource()}>Download / Import</button>
            <input ref={fileInput} type="file" accept="video/*" style={{ display: "none" }} onChange={(event) => { upload(event.target.files?.[0] || null); event.target.value = ""; }} />
            <button disabled={busy} onClick={() => fileInput.current?.click()}>⇪ Upload…</button>
          </div>
          <div className="video-import-list" role="list">
            {videos.map((video) => (
              <button key={video.path} className={`video-import-item${video.path === selectedPath ? " is-selected" : ""}`} role="listitem" onClick={() => { userTouchedRef.current = true; setSelectedPath(video.path); }}>
                <b>{video.title}</b>
                <code>{video.path}</code>
                <small>{seconds(video.duration)} · {Math.round((video.sizeBytes || 0) / (1024 * 1024))} MB · {video.frameCount || 0} frame(s){video.scenes?.length ? ` · ${video.scenes.length} scene(s)` : ""}</small>
              </button>
            ))}
          </div>
        </div>
      </Section>

      {selected && (
        <Section {...section("player", "PLAYER / TIMELINE", `${selected.title} · ${seconds(duration)}`)}>
          <div className="vi2-body video-import-player">
            <div className="video-import-captioned-media">
              <video
                ref={videoRef}
                key={selected.path}
                controls
                preload="metadata"
                src={`${API}/stream?workspaceId=${encodeURIComponent(workspaceId)}&path=${encodeURIComponent(selected.path)}`}
                onTimeUpdate={(event) => setPlayerTime((event.target as HTMLVideoElement).currentTime)}
                onLoadedMetadata={(event) => setPlayerDuration((event.target as HTMLVideoElement).duration || 0)}
              />
              {activeCaption && <div className="video-import-active-caption">{activeCaption.speaker && <b>{activeCaption.speaker}</b>}<span>{activeCaption.text}</span></div>}
            </div>
            <div
              ref={railRef}
              className="video-import-rail"
              onPointerDown={(event) => { dragRef.current = { startX: event.clientX, startT: railTime(event.clientX), moved: false }; }}
              onPointerMove={(event) => {
                if (!dragRef.current || event.buttons !== 1) return;
                const now = railTime(event.clientX);
                if (Math.abs(event.clientX - dragRef.current.startX) > 4) {
                  dragRef.current.moved = true;
                  setSelection({ start: Math.min(dragRef.current.startT, now), end: Math.max(dragRef.current.startT, now) });
                }
              }}
              onPointerUp={(event) => {
                if (dragRef.current && !dragRef.current.moved && videoRef.current) videoRef.current.currentTime = railTime(event.clientX);
                dragRef.current = null;
              }}
            >
              {selection && <div className="video-import-rail-selection" style={{ left: pct(selection.start), width: `calc(${pct(selection.end)} - ${pct(selection.start)})` }} />}
              {markers.map((marker) => (
                <button key={marker.atSeconds} className="video-import-rail-marker" style={{ left: pct(marker.atSeconds) }} title={`scene @ ${marker.atSeconds}s (click to remove)`} onClick={(event) => { event.stopPropagation(); persistMarkers(markers.filter((entry) => entry !== marker)); }} />
              ))}
              <div className="video-import-rail-playhead" style={{ left: pct(playerTime) }} />
            </div>
            {markers.length > 0 && (
              <div className="video-import-scenelane">
                {[0, ...markers.map((marker) => marker.atSeconds), duration].slice(0, -1).map((start, index, bounds) => {
                  const end = [...markers.map((marker) => marker.atSeconds), duration][index];
                  return <button key={index} className="video-import-scene" style={{ left: pct(start), width: `calc(${pct(end)} - ${pct(start)})` }} title={`scene ${index}`} onClick={() => setSelection({ start, end })} />;
                })}
              </div>
            )}
            {activeSegments.length > 0 && (
              <div className="video-import-segmentlane">
                {activeSegments.map((segment, index) => (
                  <button key={index} className={`video-import-segment${segment.keep ? "" : " is-dropped"}`} style={{ left: pct(segment.start), width: `calc(${pct(segment.end)} - ${pct(segment.start)})` }} onClick={() => persistSegments(activeSegments.map((entry, at) => (at === index ? { ...entry, keep: !entry.keep } : entry)))}>
                    {segment.keep ? "keep" : "✕"}
                  </button>
                ))}
              </div>
            )}
            <div className="video-import-timeline">
              <small>t = {playerTime.toFixed(1)}s</small>
              <button disabled={busy || !duration} onClick={() => persistMarkers([...markers, { atSeconds: Math.round(playerTime * 100) / 100 }].sort((a, b) => a.atSeconds - b.atSeconds))}>◈ Mark</button>
              <button disabled={busy || !duration} onClick={() => void grabAtCursor()}>⤵ Frame at cursor</button>
              <button disabled={!selectedPath || sceneJob?.state === "running" || job?.state === "running"} onClick={() => void detectScenes()}>✨ Detect scenes</button>
              <button disabled={!markers.length && sceneJob?.state !== "running"} onClick={clearSceneDetection}>× Clear scenes</button>
              <label>captions model
                <ColoredTagCombobox value={effectiveCaptionModel} ids={videoModelIds} ariaLabel="Video captions model" describe={describeAudioModel} disabled={captionJob?.state === "running"} onChange={setCaptionModel} />
              </label>
              <button disabled={captionJob?.state === "running"} onClick={() => void generateCaptions()}>CC Generate captions</button>
              <button disabled={!captions.length && captionJob?.state !== "running"} onClick={clearCaptions}>× Clear captions</button>
              <small>{captions.length} cue(s){captionSource ? ` · ${captionSource}` : ""}</small>
              <button disabled={busy || !duration} onClick={() => { const at = playerTime; persistSegments(activeSegments.flatMap((segment) => (at > segment.start && at < segment.end ? [{ ...segment, end: at }, { ...segment, start: at }] : [segment]))); }}>✂ Split at cursor</button>
              <button disabled={busy || job?.state === "running" || activeSegments.every((segment) => segment.keep)} onClick={() => void trimVideo()}>⟿ Trim video</button>
              <button disabled={busy || job?.state === "running" || !selection} onClick={() => void selectionToVideo()}>⤢ Selection → video</button>
              {selection && <small>selection {selection.start.toFixed(1)}–{selection.end.toFixed(1)}s <button disabled={busy} onClick={() => { setRangeStart(selection.start.toFixed(1)); setRangeEnd(selection.end.toFixed(1)); }}>→ window</button></small>}
            </div>
            <div className="video-import-timeline">
              <b title="The extract-frames-from-video criteria — the top of every stack run">EXTRACT</b>
              <select value={mode} disabled={busy} onChange={(event) => setMode(event.target.value as typeof mode)}>
                <option value="interval">every N seconds</option>
                <option value="scenes">per scene</option>
              </select>
              {mode === "interval"
                ? <label>every <input type="number" min={0.1} step={0.5} value={everySeconds} disabled={busy} onChange={(event) => setEverySeconds(event.target.value)} /> s</label>
                : <>
                  <label>images/scene <input type="number" min={1} max={20} value={perScene} disabled={busy} onChange={(event) => setPerScene(event.target.value)} /></label>
                  <label>offset <input type="number" min={0} step={0.1} value={sceneOffset} disabled={busy} onChange={(event) => setSceneOffset(event.target.value)} /> s</label>
                  <label>start scene <input type="number" min={1} step={1} value={startScene} disabled={busy} onChange={(event) => setStartScene(event.target.value)} /></label>
                  <label>end scene <input type="number" min={1} step={1} value={endScene} placeholder="end" disabled={busy} onChange={(event) => setEndScene(event.target.value)} /></label>
                  <label>skip <input type="number" min={0} step={1} value={skipScenes} disabled={busy} onChange={(event) => setSkipScenes(event.target.value)} /> scene(s)</label>
                </>}
              <label>start time <input type="number" min={0} step={0.1} value={rangeStart} disabled={busy} onChange={(event) => setRangeStart(event.target.value)} /> s</label>
              <label>end time <input type="number" min={0} step={0.1} value={rangeEnd} placeholder="end" disabled={busy} onChange={(event) => setRangeEnd(event.target.value)} /> s</label>
              <label>max <input type="number" min={1} max={600} value={maxFrames} disabled={busy} onChange={(event) => setMaxFrames(event.target.value)} /></label>
              <button disabled={frameExtractionJob?.state === "running" || job?.state === "running" || (mode === "scenes" && !markers.length)} onClick={() => void extract()}>Extract frames</button>
            </div>
          </div>
        </Section>
      )}

      {userPick && (
        <div className="video-import-userpick-section">
          <Section {...section("userpick", "❓ USER PICK GALLERY", `${userPick.title} · ${userPick.multi ? (userPick.chosen.size ? `${userPick.chosen.size} of ${userPick.frames.length} selected` : `multi-select — click tiles, then keep/remove`) : `${userPick.frames.length} candidate(s) — click ONE to use it`}`, <button onClick={() => settleUserPick(null)}>✕ skip</button>)}>
            <div className="vi2-body video-import-frames video-import-userpick">
              {userPick.frames.map((item) => {
                const on = userPick.chosen.has(item.current);
                return (
                  <article key={item.current} className={`video-import-frame is-plain is-user-pickable${on ? " is-group-pick" : ""}`}>
                    <img src={asset(item.current)} alt="candidate" loading="lazy" title={userPick.multi ? (on ? "selected — click to unselect" : "click to select") : "click: use THIS one"} onClick={() => {
                      if (!userPick.multi) { settleUserPick([item.current]); return; }
                      setUserPick((current) => {
                        if (!current) return current;
                        const chosen = new Set(current.chosen);
                        if (chosen.has(item.current)) chosen.delete(item.current); else chosen.add(item.current);
                        return { ...current, chosen };
                      });
                    }} />
                    <header><small>{userPick.multi ? (on ? "✓ selected" : "click to select") : "click to use this one"}</small></header>
                  </article>
                );
              })}
            </div>
            <div className="vi2-body video-import-userpick-actions">
              <label className="video-import-toggle" title="Off: clicking a tile uses that ONE item immediately. On: clicks select multiple tiles for keep/remove curation.">
                <input type="checkbox" checked={userPick.multi} onChange={(event) => setUserPick((current) => current ? { ...current, multi: event.target.checked, chosen: event.target.checked ? current.chosen : new Set() } : current)} />
                multi-select
              </label>
              <button disabled={!userPick.chosen.size} title="Continue with ONLY the selected items" onClick={() => settleUserPick([...userPick.chosen])}>✓ keep chosen ({userPick.chosen.size})</button>
              <button disabled={!userPick.chosen.size} title="DELETE the selected items — everything else continues" onClick={() => settleUserPick(userPick.frames.map((item) => item.current).filter((path) => !userPick.chosen.has(path)))}>🗑 remove chosen ({userPick.chosen.size})</button>
              <button title="Pass every item through unchanged" onClick={() => settleUserPick(userPick.frames.map((item) => item.current))}>use ALL</button>
              <button title="Auto-select the all-black frames (then 🗑 remove chosen)" onClick={() => void (async () => {
                try {
                  const payload = await api("select-degenerate", { workspaceId, images: userPick.frames.map((item) => item.current), kind: "black" });
                  const found = new Set((payload.selected as string[]) || []);
                  setUserPick((current) => current ? { ...current, multi: true, chosen: new Set([...current.chosen, ...found]) } : current);
                  say(`◼ ${found.size} all-black frame(s) selected`);
                } catch (reason) { say(`✗ ${reason instanceof Error ? reason.message : String(reason)}`); }
              })()}>◼ + all-black</button>
              <button title="Auto-select flat/solid-color frames (then 🗑 remove chosen)" onClick={() => void (async () => {
                try {
                  const payload = await api("select-degenerate", { workspaceId, images: userPick.frames.map((item) => item.current), kind: "flat" });
                  const found = new Set((payload.selected as string[]) || []);
                  setUserPick((current) => current ? { ...current, multi: true, chosen: new Set([...current.chosen, ...found]) } : current);
                  say(`▭ ${found.size} flat frame(s) selected`);
                } catch (reason) { say(`✗ ${reason instanceof Error ? reason.message : String(reason)}`); }
              })()}>▭ + flat/solid</button>
              <button disabled={!userPick.chosen.size} title="Clear the selection" onClick={() => setUserPick((current) => current ? { ...current, chosen: new Set() } : current)}>○ none</button>
              <button onClick={() => settleUserPick(null)}>✕ skip (keep all, no vote)</button>
            </div>
          </Section>
        </div>
      )}

      {frames.length > 0 && (
        <Section {...section("inputs", "EXTRACTED FRAME GALLERY", `${frames.length} image(s) · ${memberInputPaths.size} explicitly selected for recursive LLM input`, <button disabled={busy || job?.state === "running"} onClick={clearExtractedFrames}>× Clear extracted frames</button>)}>
          <div className="vi2-body video-import-frames video-import-extracted-gallery" role="list" aria-label="Extracted Frame Gallery">
            {frames.map((frame) => (
              <article key={frame.path} role="listitem" className={`video-import-frame is-plain${picked === frame.path ? " is-input-pick" : ""}${kept?.has(frame.path) ? " is-group-pick" : ""}${memberInputPaths.has(frame.path) ? " is-member-input" : ""}`}>
                <img
                  src={asset(frame.path)}
                  alt={`frame ${frame.index}`}
                  loading="lazy"
                  onClick={() => { const next = picked === frame.path ? null : frame.path; setPicked(next); if (next) setPreviewSource("selectedframe"); say(next ? `input item: #${frame.index}` : "input item cleared"); }}
                />
                <label className="video-import-member-input-check" title="Only checked images enter the recursive Describer → Planner → Outliner → Extractor workflow.">
                  <input type="checkbox" checked={memberInputPaths.has(frame.path)} onChange={(event) => setMemberInputPaths((current) => { const next = new Set(current); if (event.target.checked) next.add(frame.path); else next.delete(frame.path); return next; })} />
                  <span>LLM input</span>
                </label>
                <div className="video-import-frame-votes">
                  <button disabled={busy} title="Keeper (joins the group selection)" onClick={() => setKept((current) => { const next = new Set(current || []); next.add(frame.path); return next; })}>▲</button>
                  <button disabled={busy} title="Drop from candidates" onClick={() => { setFrames((current) => current.filter((candidate) => candidate.path !== frame.path)); setMemberInputPaths((current) => { const next = new Set(current); next.delete(frame.path); return next; }); if (picked === frame.path) setPicked(null); }}>▼</button>
                </div>
                <header>
                  <b>#{frame.index}</b>
                  {frame.atSeconds !== undefined && <small>{frame.atSeconds}s</small>}
                  {frame.sceneIndex !== undefined && <small>scene {frame.sceneIndex}</small>}
                  <small>{frame.path.includes("frame_at_") ? "⤵ cursor" : "extract"}</small>
                  {frame.characters.length > 0 && <small title={frame.characters.join(", ")}>👥 {frame.characters.length}</small>}
                </header>
              </article>
            ))}
          </div>
          <div className="vi2-body video-import-member-input-actions">
            <b>RECURSIVE LLM INPUTS</b>
            <span>{memberInputPaths.size} of {frames.length} selected</span>
            <button disabled={memberInputPaths.size === frames.length} onClick={() => setMemberInputPaths(new Set(frames.map((frame) => frame.path)))}>Select all</button>
            <button disabled={!memberInputPaths.size} onClick={() => setMemberInputPaths(new Set())}>Select none</button>
          </div>
          {frames.length > 1 && (
            <div className="vi2-body video-import-groupbar">
              <b>GROUP</b>
              <select value={groupKind} disabled={busy} onChange={(event) => setGroupKind(event.target.value as typeof groupKind)}>
                <option value="user">Let USER decide which item is used{selectorScore("user")}</option>
                <option value="unique">N most unique{selectorScore("unique")}</option>
                <option value="spread">N evenly spread{selectorScore("spread")}</option>
                <option value="random">N random{selectorScore("random")}</option>
                <option value="like">N most like original{selectorScore("like")}</option>
                <option value="unlike">N most unlike original{selectorScore("unlike")}</option>
              </select>
              {groupKind !== "user" && (
                <label>N <input type="number" min={1} max={frames.length} value={groupCount} disabled={busy} onChange={(event) => setGroupCount(event.target.value)} /></label>
              )}
              <button disabled={busy} onClick={() => void selectGroup()}>Select group</button>
              {kept && <><small>{kept.size} selected — feeds the chain preview</small><button disabled={busy} onClick={() => { setFrames((current) => current.filter((frame) => kept.has(frame.path))); setKept(null); }}>✂ Keep only</button><button disabled={busy} onClick={() => setKept(null)}>× Clear</button></>}
            </div>
          )}
        </Section>
      )}

      {selected && (
        <Section {...section("prepass", "PREPASS / STACK", `${filters.filter((entry) => !entry.excluded && !entry.broken).length} active filter(s) · chain ${chain.length} step(s)`)}>
          <div className="vi2-body">
            <div className="video-import-timeline video-import-prepass">
              <select aria-label="Prepass filter" value={filterId} disabled={busy} onChange={(event) => pickFilter(event.target.value)}>
                <option value="">— pick a filter (or run ▦ first) —</option>
                {filters.map((entry) => (
                  <option key={entry.id} value={entry.id} disabled={entry.broken || entry.excluded}>
                    {entry.excluded ? "🚫 " : entry.skill ? "🛠 " : entry.lut ? "🎨 " : ""}{entry.title}
                  </option>
                ))}
              </select>
              {Object.entries(filterParams).map(([key, value]) => {
                const choices = active?.paramChoices?.[key];
                return (
                  <label key={key}>{key}
                    {choices?.length
                      ? <select className="video-import-param" value={value} disabled={busy} onChange={(event) => setFilterParams((current) => ({ ...current, [key]: event.target.value }))}>{choices.map((choice) => <option key={choice} value={choice}>{choice}</option>)}</select>
                      : <input className="video-import-param" value={value} disabled={busy} onChange={(event) => setFilterParams((current) => ({ ...current, [key]: event.target.value }))} />}
                  </label>
                );
              })}
              <select value={previewSource} disabled={busy} onChange={(event) => setPreviewSource(event.target.value as typeof previewSource)}>
                <option value="testcard">preview: test card</option>
                <option value="playerframe">preview: frame @ player</option>
                <option value="firstframe">preview: first frame</option>
                <option value="selectedframe">preview: selected input</option>
              </select>
              <button disabled={busy || (!active && !chain.length)} onClick={() => void previewOne()}>👁 Preview</button>
              <select value={galleryScope} disabled={busy} onChange={(event) => setGalleryScope(event.target.value as typeof galleryScope)}>
                <option value="included">run included ({filters.filter((entry) => !entry.excluded && !entry.broken).length})</option>
                <option value="excluded">run excluded ({filters.filter((entry) => entry.excluded).length})</option>
                <option value="all">run all ({filters.filter((entry) => !entry.broken).length})</option>
              </select>
              <button disabled={busy || job?.state === "running"} onClick={() => void runGallery()}>▦ Apply all filters</button>
              <button disabled={busy || job?.state === "running" || !active} onClick={() => void runGallery({ filterId })}>⚙ Permutations</button>
              <button disabled={busy || job?.state === "running"} onClick={() => void scanRetinters()}>🚫 Find retinters</button>
              <button disabled={busy} onClick={() => setChain((current) => [...current, { entryId: "", params: {} }])}>＋ Chain</button>
              <button disabled={busy || job?.state === "running" || !selectedPath || (!active && !chain.length)} onClick={() => void run("Previewing chain", () => runStack(false))}>⇓ Preview chain</button>
              <button disabled={busy || job?.state === "running" || !selectedPath || (!active && !chain.length)} onClick={() => void run("Applying to ALL frames", () => runStack(true))}>⏵ Apply to ALL frames</button>
              <label className="video-import-toggle">
                <input type="checkbox" checked={fullSelectors} disabled={busy} onChange={(event) => setFullSelectors(event.target.checked)} />
                selectors in full run
              </label>
            </div>
            {chain.length > 0 && (
              <div className="video-import-chain" role="list">
                <div className="video-import-chain-step is-extract-step">
                  <b>0.</b>
                  <span>EXTRACT · {criteriaLabel()}</span>
                  <label>preview candidates <input className="video-import-param" type="number" min={1} value={candidateCount} disabled={busy} onChange={(event) => setCandidateCount(event.target.value)} /></label>
                  <span className="video-import-chain-none">
                    {kept?.size ? `feeding: ${kept.size} group-selected (preview only)` : picked ? "feeding: the picked input item (preview only)" : frames.length ? `${frames.length} frame(s) extracted` : "runs first when the chain executes"}
                  </span>
                </div>
                {chain.map((step, index) => {
                  const entry = filters.find((candidate) => candidate.id === step.entryId) || null;
                  const isSelector = step.entryId.startsWith("select:");
                  // "select:user" pauses the pipeline and asks YOU to click one
                  // image (see the "YOUR PICK" section) -- it's not a count, so
                  // it never takes an N parameter like the other selectors do.
                  // That picked image also becomes the base the next 77-effect
                  // gallery renders from; if you don't like how an effect
                  // treated it, keep exploring the gallery or re-run this step
                  // to pick a different image instead.
                  const isUserSelector = step.entryId === "select:user";
                  return (
                    <div key={index} className="video-import-chain-step" role="listitem">
                      <b>{index + 1}.</b>
                      <select
                        value={step.entryId}
                        disabled={busy}
                        onChange={(event) => {
                          const id = event.target.value;
                          if (id.startsWith("select:")) {
                            const params: Record<string, string> = id === "select:user" ? {} : { n: "" };
                            editChain((current) => current.map((existing, at) => (at === index ? { entryId: id, params } : existing)), index + 1);
                            return;
                          }
                          const pickedEntry = filters.find((candidate) => candidate.id === id);
                          editChain((current) => current.map((existing, at) => (at === index ? { entryId: id, params: Object.fromEntries(Object.entries(pickedEntry?.params || {}).map(([key, value]) => [key, String(value)])) } : existing)), index + 1);
                        }}
                      >
                        <option value="">&lt;none&gt;</option>
                        <optgroup label="— group selectors —">
                          <option value="select:user">selector: let USER decide which item is used{selectorScore("user")}</option>
                          <option value="select:unique">selector: N most unique{selectorScore("unique")}</option>
                          <option value="select:spread">selector: N evenly spread{selectorScore("spread")}</option>
                          <option value="select:random">selector: N random{selectorScore("random")}</option>
                          <option value="select:like">selector: N most like original{selectorScore("like")}</option>
                          <option value="select:unlike">selector: N most unlike original{selectorScore("unlike")}</option>
                        </optgroup>
                        {filters.map((candidate) => (
                          <option key={candidate.id} value={candidate.id} disabled={candidate.broken || candidate.excluded}>
                            {candidate.excluded ? "🚫 " : candidate.skill ? "🛠 " : candidate.lut ? "🎨 " : ""}{candidate.title}
                          </option>
                        ))}
                      </select>
                      {isUserSelector && (
                        <span className="video-import-chain-none">pauses and asks you to pick one image</span>
                      )}
                      {isSelector && !isUserSelector && (
                        <>
                          <label>N <input className="video-import-param" type="number" min={1} placeholder="all" value={step.params.n || ""} disabled={busy} onChange={(event) => editChain((current) => current.map((existing, at) => (at === index ? { ...existing, params: { ...existing.params, n: event.target.value } } : existing)))} /></label>
                          {!(Number(step.params.n) >= 1) && <span className="video-import-chain-none">no-op until N is set</span>}
                        </>
                      )}
                      {entry && Object.entries(step.params).map(([key, value]) => {
                        const choices = entry.paramChoices?.[key];
                        return (
                          <label key={key}>{key}
                            {choices?.length
                              ? <select className="video-import-param" value={value} disabled={busy} onChange={(event) => editChain((current) => current.map((existing, at) => (at === index ? { ...existing, params: { ...existing.params, [key]: event.target.value } } : existing)))}>{choices.map((choice) => <option key={choice} value={choice}>{choice}</option>)}</select>
                              : <input className="video-import-param" value={value} disabled={busy} onChange={(event) => editChain((current) => current.map((existing, at) => (at === index ? { ...existing, params: { ...existing.params, [key]: event.target.value } } : existing)))} />}
                          </label>
                        );
                      })}
                      {!entry && !isSelector && <span className="video-import-chain-none">no-op</span>}
                      <button disabled={busy} onClick={() => editChain((current) => current.filter((_, at) => at !== index), index)}>×</button>
                    </div>
                  );
                })}
              </div>
            )}
            {beforeAfter && (
              <div className="video-import-preview">
                <figure><img src={asset(beforeAfter.before)} alt="before" /><figcaption>before</figcaption></figure>
                <span className="video-import-preview-arrow">→</span>
                <figure><img src={asset(beforeAfter.after)} alt="after" /><figcaption>after · {beforeAfter.label}</figcaption></figure>
                <button onClick={() => setBeforeAfter(null)}>×</button>
              </div>
            )}
          </div>
        </Section>
      )}

      {gallery && (
        <Section {...section("gallery", "FILTER EFFECT GALLERY", `${gallery.filter((tile) => tile.path).length} tile(s) · click = add to chain + apply to ALL frames`, (
          <>
            <button
              disabled={busy}
              title="None of these 77 look good — dismiss the gallery and go adjust how frames are extracted instead"
              onClick={() => {
                setGallery(null);
                setCollapsedMap((current) => ({ ...current, player: false }));
                window.setTimeout(() => {
                  document.querySelector('[data-section="player"]')?.scrollIntoView({ behavior: "smooth", block: "center" });
                }, 120);
              }}
            >
              ↑ none good · extract again
            </button>
            <button disabled={busy} onClick={() => setGallery(null)}>× Clear</button>
          </>
        ))}>
          <div className="vi2-body video-import-gallery" role="list">
            {[...gallery]
              .sort((left, right) => ((filters.find((entry) => entry.id === (right.baseId || right.id))?.votes || 0) - (filters.find((entry) => entry.id === (left.baseId || left.id))?.votes || 0)))
              .map((tile) => {
                const baseId = tile.baseId || tile.id;
                const registered = filters.find((entry) => entry.id === baseId);
                const disabled = !!registered?.excluded;
                const score = registered?.votes || 0;
                return (
                  <div key={tile.id} className={`video-import-gallery-tile${filterId === baseId ? " is-picked" : ""}${disabled ? " is-disabled" : ""}`} role="listitem">
                    {tile.path
                      ? <img src={asset(tile.path)} alt={tile.title} loading="lazy" onClick={() => {
                          if (busy || disabled || !registered) return;
                          pickFilter(baseId);
                          const stepParams = Object.fromEntries(Object.entries(tile.params || registered.params || {}).map(([key, value]) => [key, String(value)]));
                          if (tile.params) setFilterParams(stepParams);
                          // The loop: each gallery pick appends to the chain, the whole
                          // chain re-applies to ALL extracted frames, and then the NEXT
                          // 77 effects render on the OUTPUT of your item — and so on.
                          const nextChain = [...chain, { entryId: baseId, params: stepParams }];
                          setChain(nextChain);
                          const baseSource = picked;
                          void run("Applying chain to ALL frames", async () => {
                            const message = await runStack(true, nextChain);
                            const outputs = lastRunOutputsRef.current;
                            const nextBase = (baseSource && outputs.find((entry) => entry.source === baseSource)) || outputs[0];
                            if (nextBase && !stopRef.current && autoNext77Ref.current) {
                              say("…and the next 77: rendering every effect on the new output");
                              window.setTimeout(() => void runGallery({ image: nextBase.path }), 120);
                            } else if (nextBase && !autoNext77Ref.current) {
                              say("auto next 77 is off — click an output frame when you want the next round");
                            }
                            return message;
                          });
                        }} />
                      : <span className="video-import-gallery-error">✗</span>}
                    <small>{tile.title}</small>
                    <div className="video-import-gallery-votebar">
                      <button disabled={busy || !registered} onClick={() => void vote([baseId], 1)}>▲</button>
                      <span className={score > 0 ? "is-up" : score < 0 ? "is-down" : ""}>{score}</span>
                      <button disabled={busy || !registered} onClick={() => void vote([baseId], -1)}>▼</button>
                      <button className="video-import-gallery-toggle" disabled={busy || !registered} onClick={() => void setDisabled(baseId, !disabled)}>{disabled ? "↩ enable" : "🚫 disable"}</button>
                    </div>
                  </div>
                );
              })}
          </div>
        </Section>
      )}

      {output.length > 0 && (
        <Section {...section("output", `PROCESSED OUTPUT GALLERY${outputMode === "full" ? " · FULL RUN" : " · PREVIEW"}`, `${output.length} frame(s)${outputLabel ? ` · via ${outputLabel}` : ""} · click a frame = new base, ALL effects run on it`, <button disabled={busy} onClick={() => setOutput([])}>× Clear</button>)}>
          <div className="vi2-body video-import-frames video-import-output">
            {output.map((frame) => (
              <article key={frame.path} className="video-import-frame is-plain">
                <img src={asset(frame.path)} alt="output" loading="lazy" title={`${frame.path} — click: run ALL effects on this`} onClick={() => {
                  if (busy) return;
                  setPicked(frame.path);
                  setPreviewSource("selectedframe");
                  say("new gallery base: this output frame");
                  void runGallery({ image: frame.path });
                }} />
                <div className="video-import-frame-votes">
                  <button disabled={busy || !appliedIds.length} title={`credit: ${appliedIds.join(", ")}`} onClick={() => void vote(appliedIds, 1)}>▲</button>
                  <button disabled={busy || !appliedIds.length} title={`credit: ${appliedIds.join(", ")}`} onClick={() => void vote(appliedIds, -1)}>▼</button>
                </div>
                <header><small title={frame.path}>{outputLabel || frame.path.split("/").pop()}</small></header>
              </article>
            ))}
          </div>
        </Section>
      )}

      {trail.length > 0 && (
        <Section {...section("trail", "PROCESSING TRAIL GALLERY", `${trail.length} level(s) · marked levels: ${probes.length ? probes.join(", ") : "none"}`)}>
          <div className="vi2-body video-import-trail" role="list">
            {trail.map((level, index) => {
              const probed = probes.includes(index);
              return (
                <label key={index} className={`video-import-trail-level${probed ? " is-probed" : ""}`}>
                  <input type="checkbox" checked={probed} disabled={busy} onChange={(event) => setProbes((current) => event.target.checked ? [...current.filter((probe) => probe !== index), index].sort((a, b) => a - b) : current.filter((probe) => probe !== index))} />
                  <b>{index}. {level.label}</b>
                  <div className="video-import-trail-thumbs">{level.frames.slice(0, 4).map((item) => <img key={item.path} src={asset(item.path)} alt="" loading="lazy" />)}</div>
                  <small>{level.frames.length} frame(s){probed ? " · ✓ marked for inspection" : " · not marked"}</small>
                </label>
              );
            })}
          </div>
        </Section>
      )}

      {selected && (
        <Section {...section("memberDescription", "SCENE OBJECTS TEXTUAL DESCRIPTION", `${memberInventories.length} scene description(s) · ${memberInventories.reduce((count, inventory) => count + (inventory.describedThings || inventory.things).length, 0)} thing(s) listed`)}>
          <div className="vi2-body">
                <div className="video-import-timeline video-import-members">
                  <select value={memberGoal} disabled={busy} onChange={(event) => setMemberGoal(event.target.value as typeof memberGoal)}>
                    <option value="any">find any members</option>
                    <option value="faces">find faces</option>
                    <option value="characters">find characters</option>
                    <option value="objects">find objects</option>
                    <option value="text">find text/signs</option>
                  </select>
                </div>
                <label className="video-import-member-model-selector">
                  <span>DESCRIBER MODEL</span>
                  <ColoredTagCombobox value={describerModel} ids={videoModelIds} ariaLabel="Scene objects description model" allowNone noneLabel={`<use global · ${allCallsModel || "none"}>`} describe={describeVideoModel} disabled={busy} onChange={(value) => { describerModelTouchedRef.current = true; setDescriberModel(value); }} />
                </label>
                {models.length > 0 && !models.some((model) => model.enabled) && <div className="demo-notice"><b>No enabled vision-capable model</b><span>{models.length} inherited vision model(s) were found but are unavailable. Enable their backend in Models before sending input images.</span></div>}
                <details className="video-import-member-prompt-disclosure">
                  <summary>DESCRIPTION PROMPT</summary>
                  <label className="video-import-member-prompt-editor">
                    <span>EDIT PROMPT</span>
                    <textarea value={memberDescriptionPrompt} disabled={busy} onChange={(event) => { setDescriberPromptSelection("workspace"); setMemberDescriptionPrompt(event.target.value); }} spellCheck={false} />
                    <small>Available placeholders: {"{{goal}}"} and {"{{alreadyExtracted}}"}</small>
                  </label>
                </details>
                <div className="video-import-member-prompt-actions">
                  <button className="primary" disabled={busy || !isRunnableVisionModel(effectiveDescriberModel) || !memberInputPaths.size} onClick={() => void describeMemberScenes()}>Call LLM · Describe selected input images</button>
                </div>
              <div className="video-import-member-runner">
                <header className="video-import-member-runner-heading">
                  <span>PROMPT + TEXT OUTPUT</span>
                  <b>{effectiveDescriberModel || "No model selected"}</b>
                  <small>Creates textual scene descriptions and inventories only. It never starts image extraction.</small>
                </header>
                {!memberInventories.length && <div className="studio-empty">Run the textual description to inspect each exact prompt and raw model output here.</div>}
                {orderedMemberInventories.map((inventory) => (
                  <article id={`recursive-inventory-${responseCacheHash(inventory.id)}`} className={`video-import-member-run ${inventory.status}`} key={inventory.id}>
                    <header><b>input image · frame #{inventory.frameIndex}</b><span>{inventory.probeLabel}</span><em>{inventory.status}</em></header>
                    <section>
                      {inventory.sourceImage && <figure className="video-import-member-input-image"><img src={asset(inventory.sourceImage)} alt={`Input image ${inventory.frameIndex}`} loading="lazy" /><figcaption>INPUT IMAGE SENT TO MODEL · {inventory.sourceImage}</figcaption></figure>}
                      <p>{inventory.sceneDescription || "Waiting for the scene description…"}</p>
                      <details><summary>Exact textual-description prompt</summary><pre>{normalizeMemberPromptLabels(inventory.descriptionPrompt || renderMemberDescriptionPrompt(selectedDescriptionPrompt, inventory.goal || memberGoal, []))}</pre></details>
                      <details open>
                        <summary>{formatDetectedJson(inventory.descriptionOutput).detected ? "Textual-description output · JSON formatted" : "Exact textual-description output"}</summary>
                        <pre>{formatDetectedJson(inventory.descriptionOutput).text || "Waiting for the model response…"}</pre>
                        {formatDetectedJson(inventory.descriptionOutput).detected && <details><summary>Raw model output</summary><pre>{inventory.descriptionOutput}</pre></details>}
                      </details>
                    </section>
                  </article>
                ))}
              </div>
          </div>
        </Section>
      )}

      <div className="video-import-scene-object-workspace">
      <div className="video-import-recursive-automation" role="toolbar" aria-label="Recursive extraction automation">
        <div className="video-import-llm-global-row">
          <b>ALL LLM CALLS <small key={llmSchedulerVersion}>{llmSchedulerRef.current.active}/{totalLlmConcurrency} active · {llmSchedulerRef.current.waiters.length} queued</small><small>Warm workers fan out ready jobs across the configured capacity.</small>{restartPendingSignal && <em>RESTART PENDING · DRAINING</em>}</b>
          <label>model
            <ColoredTagCombobox
              value={allCallsModel}
              ids={videoModelIds}
              ariaLabel="All Video Import calls model"
              allowNone
              noneLabel={models.length ? "<no global model>" : "no enabled vision models"}
              describe={describeVideoModel}
              onChange={(value) => { allCallsModelTouchedRef.current = true; setAllCallsModel(value); }}
            />
          </label>
          <label>total max processes
            <select value={totalLlmConcurrency} onChange={(event) => setTotalLlmConcurrency(Number(event.target.value))}>
              {Array.from({ length: 50 }, (_, index) => index + 1).map((value) => <option key={value} value={value}>{value}</option>)}
            </select>
          </label>
          <button
            type="button"
            className={`video-import-worker-hold${workersHeld ? " is-held" : ""}`}
            aria-pressed={workersHeld}
            title={restartPendingSignal ? "Restart pending is draining active workers." : "Pause new worker admissions before restarting an LLM server; active calls finish."}
            onClick={() => {
              if (restartPendingSignal) {
                say("restart pending owns the worker hold");
                return;
              }
              setManualWorkerHold((held) => !held);
            }}
          >
            {workersHeld ? "▶ WORKERS HELD / DRAINING" : "■ HOLD / DRAIN WORKERS"}
          </button>
        </div>
        <div className="video-import-llm-call-rows">
          {([
            ["describer", "D · DESCRIBER", recursiveAutomation.describer, describerModel, setDescriberModel, describerModelTouchedRef, llmCallConcurrency.describer, describerPromptSelection, setDescriberPromptSelection],
            ["planner", "P · PLANNER", recursiveAutomation.planner, plannerModel, setPlannerModel, plannerModelTouchedRef, llmCallConcurrency.planner, plannerPromptSelection, setPlannerPromptSelection],
            ["outliner", "O · OUTLINER", recursiveAutomation.outliner, outlinerModel, setOutlinerModel, outlinerModelTouchedRef, llmCallConcurrency.outliner, outlinerPromptSelection, setOutlinerPromptSelection],
            ["extractor", "E · EXTRACTOR", recursiveAutomation.extractor, extractorModel, setExtractorModel, extractorModelTouchedRef, llmCallConcurrency.extractor, extractorPromptSelection, setExtractorPromptSelection],
            ["turtle", "T · TURTLE GEN", recursiveAutomation.turtle, turtleModel, setTurtleModel, turtleModelTouchedRef, llmCallConcurrency.turtle, turtlePromptSelection, setTurtlePromptSelection],
            ["turtlePng", "PNG · TURTLE PNG", recursiveAutomation.turtlePng, turtlePngModel, setTurtlePngModel, turtlePngModelTouchedRef, llmCallConcurrency.turtlePng, turtlePngPromptSelection, setTurtlePngPromptSelection],
          ] as const).map(([type, label, enabled, model, setModel, touchedRef, concurrency, promptSelection, setPromptSelection]) => {
            const metric = llmCallMetrics[type];
            const progress = llmStageProgress[type];
            const completed = Math.max(progress.completed, metric.completed);
            const averageMs = metric.completed ? metric.totalDurationMs / metric.completed : 0;
            return (
            <div className="video-import-llm-call-row" key={type}>
              <button
                type="button"
                className={`${enabled ? "is-on" : ""}${llmSchedulerRef.current.byType[type] ? " has-workers" : ""}`}
                aria-pressed={enabled}
                onClick={() => toggleRecursiveAutomation(type)}
              >
                <span>{label}</span>
                <small>{enabled ? "ON" : "OFF"}</small>
                <em>{llmSchedulerRef.current.byType[type]} ACTIVE WORKER{llmSchedulerRef.current.byType[type] === 1 ? "" : "S"}</em>
              </button>
              <div className="video-import-llm-call-metrics" aria-label={`${label} job metrics`}>
                <span title="All known pipeline obligations waiting for this stage, including work not yet admitted to a worker."><b>{progress.pending}</b><small>PENDING</small></span>
                <span><b>{completed}</b><small>COMPLETED</small></span>
                <span title={metric.completed ? `${Math.round(averageMs)}ms average across ${metric.completed} completed job(s)` : "No completed jobs yet"}><b>{formatJobDuration(averageMs)}</b><small>AVG / JOB</small></span>
              </div>
              <label>model
                <ColoredTagCombobox
                  value={model}
                  ids={videoModelIds}
                  ariaLabel={`${label} model`}
                  allowNone
                  noneLabel={`<use global${allCallsModel ? ` · ${allCallsModel}` : ""}>`}
                  describe={describeVideoModel}
                  onOpen={() => setExpandedCallPrompt(type)}
                  onChange={(value) => { touchedRef.current = true; setModel(value); setExpandedCallPrompt(type); }}
                />
              </label>
              <label>max processes
                <select value={concurrency ?? ""} onFocus={() => setExpandedCallPrompt(type)} onPointerDown={() => setExpandedCallPrompt(type)} onChange={(event) => { setCallConcurrency(type, event.target.value ? Number(event.target.value) : null); setExpandedCallPrompt(type); }}>
                  <option value="">&lt;use full global capacity&gt;</option>
                  {Array.from({ length: 50 }, (_, index) => index + 1).map((value) => <option key={value} value={value}>{value}</option>)}
                </select>
              </label>
              <label>prompt
                <select
                  value={promptSelection}
                  onFocus={() => setExpandedCallPrompt(type)}
                  onPointerDown={() => setExpandedCallPrompt(type)}
                  onChange={(event) => { setPromptSelection(event.target.value as PromptSelection); setExpandedCallPrompt(type); }}
                >
                  <option value="workspace">workspace-edited {type} prompt</option>
                  <option value="default">built-in default {type} prompt</option>
                </select>
              </label>
            </div>
            );
          })}
        </div>
        <div className="video-import-automation-options">
          <button type="button" className={recursiveAutomation.advanceLevels ? "is-on" : ""} aria-pressed={recursiveAutomation.advanceLevels} onClick={() => toggleRecursiveAutomation("advanceLevels")}>Next recursion levels {recursiveAutomation.advanceLevels ? "ON" : "OFF"}</button>
          <button type="button" className={recursiveAutomation.enlargeSubobjects ? "is-on" : ""} aria-pressed={recursiveAutomation.enlargeSubobjects} onClick={() => toggleRecursiveAutomation("enlargeSubobjects")}>Enlarge subobjects {recursiveAutomation.enlargeSubobjects ? "ON" : "OFF"}</button>
          <button type="button" disabled={!selectedRecursiveInventory} onClick={() => selectedRecursiveInventory && revealRecursiveOutput(selectedRecursiveInventory.id, "members", "recursive-output")}>↓ Planner output</button>
          {selectedRecursiveInventory && <small className="video-import-planner-jump-status">{selectedRecursiveInventory.subjectName}: {selectedRecursiveInventory.orderOutput ? "Planner output ready" : selectedRecursiveInventory.orderError ? `Planner retrying · ${selectedRecursiveInventory.orderError}` : selectedRecursiveInventory.descriptionOutput ? "Planner queued" : "waiting for Describer output"}</small>}
        </div>
      </div>
      {expandedPrompt && (
        <label className="video-import-controller-prompt">
          <span>
            <b>{expandedPrompt.label} PROMPT</b>
            <small>Fully exposed from the controller prompt selector.</small>
            <button type="button" onClick={() => void reloadExpandedPrompt()}>↻ Reload prompt</button>
            <button type="button" onClick={() => void saveExpandedPrompt()}>💾 Save prompt</button>
            <button type="button" onClick={() => setExpandedCallPrompt(null)}>× Close</button>
          </span>
          <textarea value={expandedPrompt.value} onChange={(event) => updateExpandedPrompt(event.target.value)} spellCheck={false} />
        </label>
      )}
      <section className="video-import-pipe-board" aria-label="Video Import pipeline forks">
        <div className="video-import-pipe-column">
          <header>
            <span>WORKFLOW GALLERIES</span>
            <b>Selected inputs and extracted objects</b>
            <small>Only explicitly checked input images enter the workflow.</small>
          </header>
          <div className="video-import-workflow-galleries">
            <WorkflowGalleryPanel title={`EXTRACTED IMAGES · ${frames.length}`} open={!collapsedLeftGalleries.extractedImages} onOpenChange={(open) => setLeftGalleryOpen("extractedImages", open)} onClear={clearExtractedFrames}>
              <div className="video-import-workflow-gallery-images">{frames.map((frame) => <WorkflowGalleryItem key={frame.path} src={asset(frame.path)} alt={`extracted image ${frame.index}`} caption={`frame #${frame.index}`} selected={memberInputPaths.has(frame.path)} onSelectedChange={(selected) => setMemberInputPaths((current) => { const next = new Set(current); if (selected) next.add(frame.path); else next.delete(frame.path); return next; })} />)}</div>
              {!frames.length && <small>Extracted Frame Gallery images appear here.</small>}
            </WorkflowGalleryPanel>
            <WorkflowGalleryPanel title={`SELECTED IMAGES · ${memberInputPaths.size}`} open={!collapsedLeftGalleries.selectedImages} onOpenChange={(open) => setLeftGalleryOpen("selectedImages", open)} onClear={clearSelectedImages}>
              <div className="video-import-workflow-gallery-images">{frames.filter((frame) => memberInputPaths.has(frame.path)).map((frame) => <WorkflowGalleryItem key={frame.path} src={asset(frame.path)} alt={`selected input ${frame.index}`} caption={`input #${frame.index}`} selected stageIndicators={selectedImageStageIndicators(frame)} onSelectedChange={(selected) => setMemberInputPaths((current) => { const next = new Set(current); if (selected) next.add(frame.path); else next.delete(frame.path); return next; })} />)}</div>
              {!memberInputPaths.size && <small>Select images in the Extracted Frame Gallery.</small>}
            </WorkflowGalleryPanel>
            {recursiveGalleryDepths.map((depth) => {
              const levelMembers = members.filter((member) => (member.depth || 0) === depth);
              const levelBackgrounds = memberInventories
                .filter((inventory) => (inventory.depth || 0) === depth && memberScenes[inventory.id])
                .map((inventory) => ({ inventory, path: memberScenes[inventory.id] }));
              return [
                <WorkflowGalleryPanel key={`objects:${depth}`} title={`LEVEL ${depth} · EXTRACTED OBJECTS · ${levelMembers.length}`} open={!collapsedLeftGalleries[`objects:${depth}`]} onOpenChange={(open) => setLeftGalleryOpen(`objects:${depth}`, open)} onClear={() => clearRecursiveLevel(depth)}>
                  <div className="video-import-workflow-gallery-images">{levelMembers.map((member) => <WorkflowGalleryItem key={`${member.inventoryId}:${member.cutout}`} src={asset(member.cutout)} alt={member.name} caption={member.name} selected={selectedWorkflowGalleryPaths.has(member.cutout)} onSelectedChange={(selected) => selectWorkflowGalleryPath(member.cutout, selected)} />)}</div>
                  {!levelMembers.length && <small>No extracted objects at this level yet.</small>}
                </WorkflowGalleryPanel>,
                <WorkflowGalleryPanel key={`backgrounds:${depth}`} title={`LEVEL ${depth} · LEFTOVER BACKGROUNDS · ${levelBackgrounds.length}`} open={!collapsedLeftGalleries[`backgrounds:${depth}`]} onOpenChange={(open) => setLeftGalleryOpen(`backgrounds:${depth}`, open)} onClear={() => clearRecursiveLevel(depth)}>
                  <div className="video-import-workflow-gallery-images">{levelBackgrounds.map(({ inventory, path }) => <WorkflowGalleryItem key={`${inventory.id}:${path}`} src={asset(path)} alt={`leftover background ${inventory.subjectName || depth}`} caption={inventory.subjectName || `input #${inventory.frameIndex}`} selected={selectedWorkflowGalleryPaths.has(path)} onSelectedChange={(selected) => selectWorkflowGalleryPath(path, selected)} />)}</div>
                  {!levelBackgrounds.length && <small>No leftover backgrounds at this level yet.</small>}
                </WorkflowGalleryPanel>,
              ];
            })}
            <WorkflowGalleryPanel title={`PRE-TURTLE LEAVES · ${turtleLeafCandidates.length}`} open={!collapsedLeftGalleries.preTurtleLeaves} onOpenChange={(open) => setLeftGalleryOpen("preTurtleLeaves", open)} onClear={clearPreTurtleLeaves}>
              <div className="video-import-workflow-gallery-images">{turtleLeafCandidates.map((candidate) => <WorkflowGalleryItem key={candidate.inventoryId} src={asset(candidate.sourceImage)} alt={`${candidate.subjectName} pre-Turtle leaf`} caption={`${candidate.subjectName} · depth ${candidate.depth}`} selected={selectedWorkflowGalleryPaths.has(candidate.sourceImage)} onSelectedChange={(selected) => selectWorkflowGalleryPath(candidate.sourceImage, selected)} />)}</div>
              {!turtleLeafCandidates.length && <small>Described object images with no further sub-objects appear here before Turtle.</small>}
            </WorkflowGalleryPanel>
            <WorkflowGalleryPanel title={`TURTLE OUTPUT · ${renderedTurtleArtifacts.length}`} open={!collapsedLeftGalleries.turtleTerminations} onOpenChange={(open) => setLeftGalleryOpen("turtleTerminations", open)} onClear={clearTurtleTerminations}>
              <div className="video-import-workflow-gallery-images">{renderedTurtleArtifacts.map((artifact) => <WorkflowGalleryItem key={artifact.sourceImage} src={asset(artifact.renderedImage!)} alt={`${artifact.subjectName} turtle render`} caption={`${artifact.subjectName} · terminal`} selected={selectedWorkflowGalleryPaths.has(artifact.renderedImage!)} onSelectedChange={(selected) => selectWorkflowGalleryPath(artifact.renderedImage!, selected)} />)}</div>
              {!renderedTurtleArtifacts.length && <small>Leaf Turtle renders appear here as terminal object images.</small>}
            </WorkflowGalleryPanel>
          </div>
        </div>
        <div className="video-import-pipe-editor">
          <header><span>RECURSIVE OBJECT FLOW</span><b>Describer → Planner → Outliner → Extractor</b><small>Every extracted object becomes the input to another cycle. Leaves end at Turtle.</small></header>
          <nav className="video-import-pipe-spline" aria-label="Recursive object workflow tree">
            <div className="video-import-recursive-cycle-legend"><i>D</i><span>DESCRIBER</span><i>P</i><span>PLANNER</span><i>O</i><span>OUTLINER</span><i>E</i><span>EXTRACTOR</span></div>
            {recursiveRootInventories.length ? (
              <ul className="video-import-recursive-tree">
                {recursiveRootInventories.map((inventory) => (
                  <RecursiveInventoryTreeNode
                    key={inventory.id}
                    inventory={inventory}
                    inventories={memberInventories}
                    selectedId={selectedRecursiveInventory?.id || ""}
                    onSelect={(selectedInventory) => {
                      setSelectedRecursiveInventoryId(selectedInventory.id);
                      window.setTimeout(() => document.getElementById(`recursive-inventory-${responseCacheHash(selectedInventory.id)}`)?.scrollIntoView({ behavior: "smooth", block: "center" }), 50);
                    }}
                  />
                ))}
              </ul>
            ) : (
              <div className="video-import-recursive-tree-empty">
                <i /><span>INPUT IMAGE</span><b>↓ D → P → O → E</b><i /><span>EXTRACTED OBJECT</span><b>↓ D → P → O → E</b><i /><span>TURTLE LEAF</span>
              </div>
            )}
          </nav>
          <div className="video-import-recursive-cycle-inspector">
          <header><span>RECURSIVE CYCLE INSPECTOR</span><b>{selectedRecursiveInventory?.subjectName || "Input image"}</b></header>
          {selectedRecursiveInventory ? (
            <>
              <figure className="video-import-member-input-image"><img src={asset(selectedRecursiveInventory.sourceImage)} alt={selectedRecursiveInventory.subjectName || "input image"} /><figcaption>depth {selectedRecursiveInventory.depth || 0} · {selectedRecursiveInventory.things.length} direct child object(s)</figcaption></figure>
              <div className="video-import-recursive-cycle-status">
                <button type="button" onClick={() => revealRecursiveOutput(selectedRecursiveInventory.id, "memberDescription", "recursive-inventory")}><i>D</i><span><b>DESCRIBER</b><small>{selectedRecursiveInventory.descriptionOutput ? "complete" : "waiting"}</small></span></button>
                <button type="button" onClick={() => revealRecursiveOutput(selectedRecursiveInventory.id, "members", "recursive-output")}><i>P</i><span><b>PLANNER</b><small>{selectedRecursiveInventory.orderOutput ? "complete" : selectedRecursiveInventory.orderError ? "retrying after error" : selectedRecursiveInventory.descriptionOutput ? "queued" : "waiting for Describer"}</small></span></button>
                <button type="button" onClick={() => revealRecursiveOutput(selectedRecursiveInventory.id, "members", "recursive-output")}><i>O</i><span><b>OUTLINER</b><small>{selectedRecursiveInventory.things.filter(hasAlignedOutline).length}/{selectedRecursiveInventory.things.length} outlined</small></span></button>
                <button type="button" onClick={() => revealRecursiveOutput(selectedRecursiveInventory.id, "members", "recursive-output")}><i>E</i><span><b>EXTRACTOR</b><small>{selectedRecursiveInventory.things.filter((thing) => thing.outputImages?.length).length}/{selectedRecursiveInventory.things.length} extracted</small></span></button>
              </div>
            </>
          ) : <p className="hint">Call the Describer to create the root object cycle.</p>}
          </div>
        </div>
      </section>

      {selected && (
        <Section {...section("members", "SCENE OBJECT VISUALS · RECURSIVE DESCRIBER / PLANNER / OUTLINER / EXTRACTOR", `${memberInventories.length} object node(s) · ${members.length} extracted image(s)`)}>
          <div className="vi2-body">
                <div className="video-import-timeline video-import-members">
                 <label>Planner model
                   <ColoredTagCombobox value={plannerModel} ids={videoModelIds} ariaLabel="Scene object Planner model" allowNone noneLabel={`<use global · ${allCallsModel || "none"}>`} describe={describeVideoModel} disabled={busy} onChange={(value) => { plannerModelTouchedRef.current = true; setPlannerModel(value); }} />
                 </label>
                 <label>Outliner model
                   <ColoredTagCombobox value={outlinerModel} ids={videoModelIds} ariaLabel="Scene object Outliner model" allowNone noneLabel={`<use global · ${allCallsModel || "none"}>`} describe={describeVideoModel} disabled={busy} onChange={(value) => { outlinerModelTouchedRef.current = true; setOutlinerModel(value); }} />
                 </label>
                 <label>Extractor model
                   <ColoredTagCombobox value={extractorModel} ids={videoModelIds} ariaLabel="Scene object Extractor model" allowNone noneLabel={`<use global · ${allCallsModel || "none"}>`} describe={describeVideoModel} disabled={busy} onChange={(value) => { extractorModelTouchedRef.current = true; setExtractorModel(value); }} />
                   <small>{effectiveImageOutputModel ? `masked image editing via ${effectiveImageOutputModel}` : "local inpaint fallback · no enabled model advertises image output"}</small>
                 </label>
                 <select value={memberFill} disabled={busy} onChange={(event) => setMemberFill(event.target.value as typeof memberFill)}>
                   <option value="inpaint">remove: content-aware inpaint</option>
                   <option value="median">remove: median inpaint</option>
                    <option value="blur">remove: blur fill</option>
                    <option value="hole">remove: transparent hole</option>
                  </select>
                </div>
                <details className="video-import-member-prompt-disclosure">
                  <summary>PLANNER PROMPT</summary>
                  <label className="video-import-member-prompt-editor">
                    <span>EDIT PROMPT</span>
                    <textarea value={memberOrderPrompt} disabled={busy} onChange={(event) => { setPlannerPromptSelection("workspace"); setMemberOrderPrompt(event.target.value); }} spellCheck={false} />
                    <small>Available placeholders: {"{{textualDescription}}"} and {"{{objects}}"}. Planner orders direct children; it does not generate prompts.</small>
                  </label>
                </details>
                <div className="video-import-member-prompt-actions">
                  <button disabled={busy || !isRunnableVisionModel(effectivePlannerModel) || !memberInventories.some((inventory) => inventory.things.length)} onClick={() => void runRecursivePlanner()}>Call LLM · Planner</button>
                </div>
                <details className="video-import-member-prompt-disclosure">
                  <summary>OUTLINER PROMPT</summary>
                  <label className="video-import-member-prompt-editor">
                    <span>EDIT PROMPT</span>
                    <textarea value={memberOutlinerPrompt} disabled={busy} onChange={(event) => { setOutlinerPromptSelection("workspace"); setMemberOutlinerPrompt(event.target.value); }} spellCheck={false} />
                    <small>One object per call. Placeholders: {"{{textualDescription}}"}, {"{{nextObjectName}}"}, {"{{nextObjectDescription}}"}, {"{{plannerPosition}}"}, and {"{{plannerTotal}}"}. Calls may proceed independently without waiting for extraction.</small>
                  </label>
                </details>
                <div className="video-import-member-prompt-actions">
                  <button disabled={busy || !isRunnableVisionModel(effectiveOutlinerModel) || !memberInventories.some((inventory) => inventory.extractionOrder?.length)} onClick={() => void runRecursiveOutliner()}>Call LLM · Outliner</button>
                </div>
                <details className="video-import-member-prompt-disclosure">
                  <summary>EXTRACTOR PROMPT</summary>
                  <label className="video-import-member-prompt-editor">
                    <span>EDIT PROMPT</span>
                    <textarea value={memberExtractorPrompt} disabled={busy} onChange={(event) => { setExtractorPromptSelection("workspace"); setMemberExtractorPrompt(event.target.value); }} spellCheck={false} />
                    <small>One shared reconstruction template. Placeholders: {"{{textualDescription}}"}, {"{{nextObjectName}}"}, {"{{nextObjectDescription}}"}, {"{{outline}}"}, {"{{plannerPosition}}"}, and {"{{plannerTotal}}"}. Outliner owns geometry; Extractor owns cutting and background reconstruction.</small>
                  </label>
                </details>
                <div className="video-import-member-prompt-actions">
                  <button className="primary" disabled={busy || !isRunnableVisionModel(effectiveExtractorModel) || !memberInventories.some((inventory) => inventory.things.length)} onClick={() => void runRecursiveExtractor()}>Call LLM · Recursive Extractor</button>
                </div>
              <div className="video-import-member-runner">
                <header className="video-import-member-runner-heading">
                  <span>PROMPTS + IMAGE OUTPUTS</span>
                  <b>P {effectivePlannerModel || "none"} · O {effectiveOutlinerModel || "none"} · E {effectiveExtractorModel || "none"}</b>
                  <small>Each input follows Describer → Planner → Outliner → Extractor. Outliner handles one object per call without waiting for other outlines or extraction.</small>
                </header>
                {!memberInventories.length && <div className="studio-empty">Scene Description & Inventory must run first.</div>}
                {orderedMemberInventories.map((inventory) => (
                  <article id={`recursive-output-${responseCacheHash(inventory.id)}`} className={`video-import-member-run ${inventory.status}`} key={inventory.id}>
                    <header><b>depth {inventory.depth || 0} · {inventory.subjectName || `input image #${inventory.frameIndex}`}</b><span>{inventory.parentInventoryId ? `child of ${inventory.parentInventoryId}` : "root input image"}</span><em>{inventory.status}</em></header>
                    <section>
                      <span>DESCRIBER</span>
                      {inventory.sourceImage && <figure className="video-import-member-input-image"><img src={asset(inventory.sourceImage)} alt={inventory.subjectName || "input image"} loading="lazy" /><figcaption>DESCRIBER INPUT IMAGE · {inventory.sourceImage}</figcaption></figure>}
                      <p>{inventory.sceneDescription || "Waiting for description."}</p>
                      <details><summary>Exact Describer prompt</summary><pre>{inventory.descriptionPrompt}</pre></details>
                      <details open>
                        <summary>{formatDetectedJson(inventory.descriptionOutput || "").detected ? "Describer output · JSON formatted" : "Exact Describer output"}</summary>
                        <pre>{formatDetectedJson(inventory.descriptionOutput || "").text || "Call the Describer for this image."}</pre>
                      </details>
                      <small>{inventory.things.length} direct child object(s)</small>
                    </section>
                    <section>
                      <span>PLANNER</span>
                      <details><summary>Exact Planner prompt</summary><pre>{inventory.orderPrompt || renderMemberOrderPrompt(selectedPlannerPrompt, inventory.descriptionOutput || inventory.sceneDescription, inventory.things)}</pre></details>
                      <details open>
                        <summary>{formatDetectedJson(inventory.orderOutput || "").detected ? "Planner output · JSON formatted" : "Exact Planner output"}</summary>
                        <pre>{formatDetectedJson(inventory.orderOutput || "").text || "Call the Planner for this object image."}</pre>
                        {inventory.orderOutput && formatDetectedJson(inventory.orderOutput).detected && <details><summary>Raw ordering output</summary><pre>{inventory.orderOutput}</pre></details>}
                      </details>
                      {inventory.extractionOrder?.length ? <p>Planned extraction order: {inventory.extractionOrder.join(" → ")}</p> : null}
                      {inventory.orderError && <small>{inventory.orderError}</small>}
                    </section>
                    <section>
                      <span>OUTLINER · {inventory.things.filter(hasAlignedOutline).length}/{inventory.things.length} OUTLINE(S)</span>
                      {!inventory.things.length && <small>No planned objects to outline.</small>}
                      {inventory.things.map((thing, thingIndex) => (
                        <details className={`video-import-member-call is-${thing.status}`} key={`outline:${thing.name}:${thingIndex}`} open={thing.status === "outlining"}>
                          <summary><b>{(inventory.extractionOrder?.indexOf(thing.name) ?? thingIndex) + 1}. {thing.name}</b><em>{thing.outlineOutput ? "outlined" : thing.outlineError ? "retrying" : "waiting"}</em></summary>
                          <p>{thing.description}</p>
                          {thing.outlinePrompt && <details><summary>Exact Outliner prompt</summary><pre>{thing.outlinePrompt}</pre></details>}
                          {thing.outlineOutput && <details open><summary>Exact Outliner output</summary><pre>{formatDetectedJson(thing.outlineOutput).text}</pre></details>}
                          {thing.outlineError && <small>{thing.outlineError}</small>}
                        </details>
                      ))}
                    </section>
                    <section>
                      <span>EXTRACTOR · {inventory.things.reduce((count, thing) => count + (thing.outputImages?.length || 0), 0)} OUTPUT IMAGE(S)</span>
                      {!inventory.things.length && <small>No extractable things listed.</small>}
                      {inventory.things.map((thing, thingIndex) => (
                        <details className={`video-import-member-call is-${thing.status}`} key={`${thing.name}:${thingIndex}`}>
                          <summary><b>{thingIndex + 1}. {thing.name}</b><em>{thing.status.replace("_", " ")}</em></summary>
                          <p>{thing.description}</p>
                          <details><summary>Planner-selected next-object data</summary><pre>{JSON.stringify({ name: thing.name, description: thing.description, plannerPosition: (inventory.extractionOrder?.indexOf(thing.name) ?? -1) + 1, plannerTotal: inventory.extractionOrder?.length || inventory.things.length }, null, 2)}</pre></details>
                          {thing.extractionAttempts?.map((attempt, attemptIndex) => (
                            <details key={`${attempt.route}:${attempt.inputImage}:${attemptIndex}`}>
                              <summary>{attempt.route.replaceAll("_", " ")} · {(attempt.promptSource || "legacy prompt").replaceAll("_", " ")} · {attempt.status.replaceAll("_", " ")}</summary>
                              {attempt.inputImage && <figure className="video-import-member-input-image"><img src={asset(attempt.inputImage)} alt={`${thing.name} ${attempt.route} input`} loading="lazy" /><figcaption>EXACT ROUTE INPUT IMAGE · {attempt.inputImage}</figcaption></figure>}
                              {attempt.outputImage && <div className="video-import-member-call-images"><figure><img src={asset(attempt.outputImage)} alt={`${thing.name} ${attempt.route} output`} loading="lazy" /><figcaption>{thing.name} · {attempt.route.replaceAll("_", " ")} · {(attempt.promptSource || "legacy prompt").replaceAll("_", " ")}</figcaption></figure></div>}
                              {attempt.error && <small>{attempt.error}</small>}
                            </details>
                          ))}
                          {!thing.extractionAttempts?.length && <pre>{normalizeMemberPromptLabels(thing.extractionPrompt || renderMemberExtractionPrompt(inventory.descriptionOutput || inventory.sceneDescription, thing.name, thing.description))}</pre>}
                          {thing.error && <small>{thing.error}</small>}
                        </details>
                      ))}
                    </section>
                  </article>
                ))}
              </div>
              {members.length > 0 && (
                <section className="video-import-extracted-object-strips">
                  <header><b>VERTICAL STRIPS OF EXTRACTED OBJECTS</b><small>One strip per input image; each card retains its recursive depth and parent inventory.</small></header>
                  <div className="video-import-member-strips" role="list">
                    {[...new Set(members.map((member) => member.framePath))].map((framePath) => {
                      const strip = members.map((member, at) => ({ member, at })).filter(({ member }) => member.framePath === framePath);
                      return (
                        <div key={framePath} className="video-import-member-strip" role="listitem">
                          <header><b>input image · frame #{strip[0]?.member.frameIndex}</b><small>{strip.length} image(s) · {strip.filter(({ member }) => member.status === "pending").length} pending · {strip.filter(({ member }) => member.status === "accepted").length} ✓ · {strip.filter(({ member }) => member.status === "rejected").length} ✗</small></header>
                          {strip.map(({ member, at }) => (
                            <article key={`${member.cutout}-${at}`} className={`video-import-member is-${member.status}`}>
                              <img src={asset(member.cutout)} alt={member.name} loading="lazy" />
                              <header><b>{member.name}</b><small>#{member.frameIndex} · depth {member.depth || 0} · pass {member.step} · {member.promptSource?.replaceAll("_", " ") || "legacy prompt"}</small></header>
                              <div className="video-import-member-actions"><button disabled={busy || member.status !== "pending"} onClick={() => acceptMember(at)}>✓</button><button disabled={busy || member.status === "rejected"} onClick={() => void rejectMember(at)}>✗ return</button><small>{member.status}</small></div>
                            </article>
                          ))}
                          {Object.entries(memberScenes).filter(([key]) => key === `input:${framePath}`).map(([key, scenePath]) => <article key={key} className="video-import-member is-scene"><img src={asset(scenePath)} alt="scene now" loading="lazy" /><header><b>scene now</b></header></article>)}
                        </div>
                      );
                    })}
                  </div>
                </section>
              )}
          </div>
        </Section>
      )}

      {selected && (
        <Section {...section("finish", "TURTLE / IMPORT GAME", `${output.length ? "OUTPUT frames feed the finish" : "input frames feed the finish"}`)}>
          <div className="vi2-body video-import-timeline">
            <b>TURTLE GEN</b>
            <label>model
              <ColoredTagCombobox value={turtleModel} ids={videoModelIds} ariaLabel="Turtle Gen model" allowNone noneLabel={`<use global · ${allCallsModel || "none"}>`} describe={describeVideoModel} disabled={busy} onChange={(value) => { turtleModelTouchedRef.current = true; setTurtleModel(value); }} />
            </label>
            <details className="video-import-member-prompt-disclosure">
              <summary>TURTLE PROMPT</summary>
              <label className="video-import-member-prompt-editor">
                <span>EDIT PROMPT</span>
                <textarea value={turtlePrompt} disabled={busy} onChange={(event) => { setTurtlePromptSelection("workspace"); setTurtlePrompt(event.target.value); }} spellCheck={false} />
              </label>
            </details>
            <button disabled={busy || !isRunnableVisionModel(effectiveTurtleModel) || !turtleLeafCandidates.length} onClick={() => void generateTurtlePrograms()}>Call LLM · Turtle Gen</button>
            <b>TURTLE PNG</b>
            <label>model
              <ColoredTagCombobox value={turtlePngModel} ids={videoModelIds} ariaLabel="Turtle PNG model" allowNone noneLabel={`<use global · ${allCallsModel || "none"}>`} describe={describeVideoModel} disabled={busy} onChange={(value) => { turtlePngModelTouchedRef.current = true; setTurtlePngModel(value); }} />
            </label>
            <details className="video-import-member-prompt-disclosure">
              <summary>TURTLE PNG PROMPT</summary>
              <label className="video-import-member-prompt-editor">
                <span>EDIT PROMPT</span>
                <textarea value={turtlePngPrompt} disabled={busy} onChange={(event) => { setTurtlePngPromptSelection("workspace"); setTurtlePngPrompt(event.target.value); }} spellCheck={false} />
              </label>
            </details>
            <button disabled={busy || !isRunnableVisionModel(effectiveTurtlePngModel) || !Object.values(turtleArtifacts).some((artifact) => artifact.status === "generated")} onClick={() => void drawTurtlePngs()}>Call LLM · Turtle PNG</button>
            <b>IMPORT GAME</b>
            <label>game id <input type="text" value={gameId} disabled={busy} onChange={(event) => setGameId(event.target.value)} /></label>
            <button disabled={busy || !frames.length || !gameId.trim()} onClick={() => void materialize()}>Materialize as recording</button>
          </div>
        </Section>
      )}
      </div>
      {visibleAltImageZoom && (
        <div
          className={`video-import-alt-image-zoom${pinnedAltImageZoom ? " is-pinned" : ""}`}
          style={{ left: visibleAltImageZoom.x, top: visibleAltImageZoom.y }}
          aria-hidden={pinnedAltImageZoom ? undefined : "true"}
        >
          <div className="video-import-alt-image-zoom-image" style={{ width: visibleAltImageZoom.width, height: visibleAltImageZoom.height }}>
            <img src={visibleAltImageZoom.src} alt={visibleAltImageZoom.alt} />
            <span>ALT · {visibleAltImageZoom.scale.toFixed(1)}×</span>
          </div>
          <aside>
            <header><b>{activeImageInventory?.subjectName || activeImageMember?.name || visibleAltImageZoom.alt || "IMAGE"}</b><small>{visibleAltImageZoom.imagePath || "No filesystem image path"}</small>{pinnedAltImageZoom && <button type="button" onClick={() => setPinnedAltImageZoom(null)}>× Close</button>}</header>
            <section>
              <strong>PARENT OBJECT DESCRIPTION</strong>
              <p>{activeImageParentDescription || "This image has no parent extraction-object description."}</p>
            </section>
            <section>
              <strong>IMAGE DESCRIBER</strong>
              <p>{activeImageDescription || "The Describer has not analyzed this image yet."}</p>
              {activeImageDescriberOutput && <pre>{formatDetectedJson(activeImageDescriberOutput).text}</pre>}
            </section>
            <section><strong>PLANNER · {activeImagePlannerStatus}</strong><pre>{activeImagePlannerOutput ? formatDetectedJson(activeImagePlannerOutput).text : activeImagePlannerStatus}</pre></section>
            <section><strong>OUTLINER · {activeImageOutlinerOutputs.length} OBJECT(S)</strong><pre>{activeImageOutlinerOutputs.length ? JSON.stringify(activeImageOutlinerOutputs, null, 2) : "No one-object outlines yet."}</pre></section>
            <section>
              <strong>OBJECTS · {activeImageInventory?.things.length || 0}</strong>
              {activeImageInventory?.things.length
                ? <ol>{activeImageInventory.things.map((thing, index) => <li key={`${thing.name}:${index}`}><b>{thing.name}</b><span>{thing.description}</span><em>{thing.status.replace("_", " ")}</em></li>)}</ol>
                : <p>No object list has been made for this image yet.</p>}
            </section>
            {activeImageProvenancePath && <section><strong>PROVENANCE JSON · {activeImageProvenancePath}</strong><pre>{activeImageProvenance ? JSON.stringify(activeImageProvenance, null, 2) : "Loading provenance…"}</pre></section>}
            {activeTurtleArtifact && <section><strong>TURTLE GEN · {activeTurtleArtifact.status}</strong><pre>{formatDetectedJson(activeTurtleArtifact.rawProgram || activeTurtleArtifact.error || "Generating…").text}</pre>{activeTurtleArtifact.pngProgram && <><strong>TURTLE PNG DRAW PROGRAM</strong><pre>{formatDetectedJson(activeTurtleArtifact.pngProgram).text}</pre></>}{activeTurtleArtifact.renderedImage && <figure><img src={asset(activeTurtleArtifact.renderedImage)} alt={`${activeTurtleArtifact.subjectName} Turtle render`} /><figcaption>TERMINAL TURTLE RENDER · {activeTurtleArtifact.renderedImage}</figcaption></figure>}</section>}
          </aside>
        </div>
      )}
      {(pinnedImageContext || hoverImageContext) && !visibleAltImageZoom && (
        <aside className={`video-import-image-hover-context${pinnedImageContext ? " is-pinned" : ""}`} style={{ left: (pinnedImageContext || hoverImageContext)!.x, top: (pinnedImageContext || hoverImageContext)!.y }} aria-hidden={pinnedImageContext ? undefined : "true"}>
          <header><b>IMAGE CONTEXT</b><small>{activeImageInventory?.subjectName || activeImageMember?.name || (pinnedImageContext || hoverImageContext)!.alt || "image"}</small>{pinnedImageContext && <button type="button" onClick={() => setPinnedImageContext(null)}>× Close</button>}</header>
          <section><strong>PARENT OBJECT DESCRIPTION</strong><p>{activeImageParentDescription || "No parent extraction-object description."}</p></section>
          <section><strong>LAST IMAGE DESCRIBER OUTPUT</strong><pre>{formatDetectedJson(activeImageDescriberOutput || "The Describer has not analyzed this image yet.").text}</pre></section>
          <section><strong>PLANNER · {activeImagePlannerStatus}</strong><pre>{activeImagePlannerOutput ? formatDetectedJson(activeImagePlannerOutput).text : activeImagePlannerStatus}</pre></section>
          <section><strong>OUTLINER · {activeImageOutlinerOutputs.length} OBJECT(S)</strong><pre>{activeImageOutlinerOutputs.length ? JSON.stringify(activeImageOutlinerOutputs, null, 2) : "No one-object outlines yet."}</pre></section>
          {activeImageProvenancePath && <section><strong>PROVENANCE JSON · {activeImageProvenancePath}</strong><pre>{activeImageProvenance ? JSON.stringify(activeImageProvenance, null, 2) : "Loading provenance…"}</pre></section>}
          {activeTurtleArtifact && <section><strong>TURTLE GEN · {activeTurtleArtifact.status}</strong><pre>{formatDetectedJson(activeTurtleArtifact.rawProgram || activeTurtleArtifact.error || "Generating…").text}</pre>{activeTurtleArtifact.pngProgram && <><strong>TURTLE PNG DRAW PROGRAM</strong><pre>{formatDetectedJson(activeTurtleArtifact.pngProgram).text}</pre></>}{activeTurtleArtifact.renderedImage && <img className="video-import-hover-turtle-render" src={asset(activeTurtleArtifact.renderedImage)} alt={`${activeTurtleArtifact.subjectName} Turtle render`} />}</section>}
        </aside>
      )}
    </section>
  );
}
