import { useEffect, useLayoutEffect, useMemo, useRef, useState, type CSSProperties, type ReactNode } from "react";
import { WorkflowPageHost, type WorkflowPageComponentRegistry, type WorkflowPageDefinition } from "./WorkflowPageHost";
import { WorkflowPageSourceEditor } from "./WorkflowPageSourceEditor";
import { ThreeStateAccordionMember, ThreeStateAccordionStack, type AccordionDisplayMode } from "./ThreeStateAccordion";
import "../styles/arc3_prompt_prolog.css";

type ModelChoice = {
  id: string;
  label?: string;
  backendId?: string;
  backendLabel?: string;
  enabled?: boolean;
  capabilities?: Record<string, unknown>;
};

type Props = {
  pageDefinition: WorkflowPageDefinition;
  workspaceId: string;
  workspaceLabel: string;
  models: ModelChoice[];
  files: Array<{
    path: string;
    name: string;
    suffix: string;
    modified: number;
  }>;
  onPageDefinitionSaved: () => Promise<unknown> | unknown;
};

type WorkspaceFileRecord = {
  path: string;
  name: string;
  suffix: string;
  modified: number;
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

type ParsedPrologPayload = {
  new_identities?: unknown[];
  initial_identities?: unknown[];
  current_identities?: unknown[];
  regenerated_identities?: unknown[];
  current_hypotheses?: unknown[];
  currnet_hypotheses?: unknown[];
  action_history?: unknown[];
  objects_pl?: string;
  differences_pl?: string;
  similarities_pl?: string;
  turtle_from_image_pl?: string;
  rules_pl?: string;
  objects_english?: string;
  differences_english?: string;
  rules_english?: string;
  exit_value?: unknown;
};

type PromptExitValue = "llm_error" | "next_iteration" | "loop_complete" | "loop_overbudgeted" | "unran";
type RunnerRunMode = "primary" | "loop" | "until_exit";

type IdentityCandidate = {
  id: string;
  type?: string;
  sub_type?: string;
  bounding_box?: [number, number, number, number];
};

type ValidationIssue = {
  id: string;
  code: string;
  detail: string;
};

type PassValidationResult = {
  accepted: boolean;
  newCount: number;
  issues: ValidationIssue[];
};

type ImageValidationFrame = {
  width: number;
  height: number;
  rgba: Uint8ClampedArray;
};

type RemovalArtifacts = {
  objectImage: string;
  backgroundImage: string;
  accepted: boolean;
  issues: string[];
};

type ValidatorAssessment = {
  approved: boolean;
  issues: string[];
  exitValue: PromptExitValue;
};

type ImageSelection = {
  name: string;
  dataUrl: string;
};

type StackKey = "A" | "B" | "C";

type AnalysisItem = {
  key: string;
  label: string;
  value: string;
};

type ImageAnalysis = {
  subimages: AnalysisItem[];
  textFiles: AnalysisItem[];
  updatedAt: string;
};

type StackSetup = {
  id: string;
  label: string;
  command: string;
  note?: string;
  beforeImage: ImageSelection | null;
  afterImage: ImageSelection;
  objectImages?: ImageSelection[];
  groupImages?: ImageSelection[];
  subImages?: ImageSelection[];
  unknownFiles?: ImageSelection[];
  plFiles?: ImageSelection[];
  engFiles?: ImageSelection[];
  jsonFiles?: ImageSelection[];
  mettaFiles?: ImageSelection[];
  promptFiles?: ImageSelection[];
  stateDir?: string;
  stateFile?: string;
  stateJson?: string;
  analysis?: ImageAnalysis;
};

type SetupCollectionField =
  | "objectImages"
  | "groupImages"
  | "subImages"
  | "unknownFiles"
  | "plFiles"
  | "engFiles"
  | "jsonFiles"
  | "mettaFiles"
  | "promptFiles";

type RunnerState = {
  selectedModelId: string;
  validatorModelId: string;
  setupIndex: number;
  filesSourceSelection: string;
  filesSourceIds: string[];
  generationSeq: number;
  promptText: string;
  primaryPromptName: string;
  validatorPromptText: string;
  validatorPromptName: string;
  promptMode: "loop" | "validator";
  autoLoopMaxIterations: number;
  autoLoopMaxSeconds: number;
  maxPrimarySeconds: number;
  running: boolean;
  currentRunMode: RunnerRunMode | "";
  message: string;
  error: string;
  result: ModelInvocation | null;
  parsed: ParsedPrologPayload | null;
  rawResponse: string;
  debugLogPath: string;
  debugLog: string;
  removedIdentityId: string;
  removedObjectImage: string;
  removedBackgroundImage: string;
  loopImageWithCircles: string;
  removalValidationSummary: string;
};

type StackColumnState = {
  key: StackKey;
  columnModelSelection: string;
  desc1: string;
  desc2: string;
  beforeImage: ImageSelection | null;
  afterImage: ImageSelection | null;
  setups: StackSetup[];
  runners: RunnerState[];
  selectedImageIndex?: number;
};

type OutputHistoryEntry = {
  id: string;
  generationSeq: number;
  runnerId: string;
  createdAt: string;
  parsed: ParsedPrologPayload | null;
  rawResponse: string;
};

type ModelCapabilities = {
  multimodal: boolean;
  vision: boolean;
  summary: boolean;
  audio: boolean;
  reasoning: boolean;
  tools: boolean;
  code: boolean;
  json: boolean;
  text: boolean;
};

class RequestFailure extends Error {
  debugLogPath?: string;
  constructor(message: string, debugLogPath?: string) {
    super(message);
    this.debugLogPath = debugLogPath;
  }
}

const DESCRIPTIVE_ID_RULE =
  "Every object id must be a descriptive snake_case name that encodes the object's position/location and orientation (top/bottom, left/right, north/south/east/west, front/rear, corner/edge/center) together with its color, shape, and role — for example players_top_hud, northern_most_exit, left_rear_tile, right_rear_tile, bottom_center_gate, or blue_star_trigger — and never an opaque, generic, or numeric id such as obj_1, object_7, or region_a.";
const COMBINED_PROMPT_PARTS = [
  "Analyze the current ARC3 state and return exactly one valid JSON object. Do not return Markdown or commentary. Required keys are: current_identities, current_hypotheses, action_history, objects_pl, differences_pl, similarities_pl, turtle_from_image_pl, rules_pl, objects_english, differences_english, and rules_english. Optional key: exit_value.",
  "",
  "IMAGE ANALYSIS WORKFLOW: Process one image at a time. Default flow: first analyze the parent image alone and extract its full object inventory, then analyze the current image alone and extract its full object inventory, then perform cross-image correspondence and transition analysis. Level_1 override: for primary object extraction, use the first/root image as the canonical object baseline, then map later frames to that baseline and only add truly new objects when needed.",
  "",
  "OUTPUT TYPES: current_identities must be a JSON array of objects that includes id, type, and label, and lifecycle-tracking metadata including first_appeared_step and last_disappeared_step. Each id must be a friendly, human-readable snake_case name that describes the object by color, shape, and role (for example blue_star_trigger, green_fortress, or bottom_center_gate), never an opaque or numeric ID. For each identity, include a compact ascii_depiction_lines field as a JSON array of strings, where each string is one visual line of the ASCII sketch. Extract and maintain no fewer than 10 identities per analyzed game scene. It may also include appeared_steps, disappeared_steps, occluded_steps, transformed_steps, and short tracking notes. current_hypotheses must be a JSON array carrying forward active hypotheses and their lightweight tracking metadata across steps. action_history must be a JSON array carrying forward per-step action outcome records, where each entry states what was expected to happen, what actually happened, what was surprising, and what was not expected in the game scene. Put all action-level future intent in action_history, including predicted outcomes, predicted destinations/positions, and planned next-state changes. When observed, action_history must explicitly record whether glyph alignment changed and whether top-exit escape became possible. Each action_history entry must also include scene_ascii_lines and change_ascii_lines arrays that sketch the current scene and the step change in ASCII art.",
  "",
  "ENCODING CONTRACT: Every *_pl value must be a JSON string containing plain SWI-Prolog source. Escape newlines, quotation marks, backslashes, and control characters exactly as strict JSON requires. The decoded string must be Prolog source text only, with no Markdown fences.",
  "",
  "COORDINATE CONTRACT: Reason exclusively in the logical ARC grid, normally 64x64 cells, rather than enlarged PNG display pixels. Use zero-based coordinates. x increases to the right and y increases downward. Never report 512x512 display-pixel geometry when the underlying board is 64x64. Describe exact cells, compact cell runs, logical bounding boxes, and connected components.",
  "",
  "IDENTITY CONTRACT: object_registry.pl is the canonical identity source. Reuse every established friendly ID exactly. current_identities must represent the maintained current identity set for this state and may be supplied as prior input via INPUT_FILES; if supplied, update and return it rather than discarding it. Use a two-pass identity workflow: first try to extract and re-ground all objects already represented in current_identities from the parent/current images, then account for the remaining image content and add any missing meaningful objects into current_identities. For level_1, treat identities grounded from the first/root image as the baseline catalog and preferentially reuse them in later frames. Track both pre-existing and newly observed identities in current_identities (do not split identities into separate new or initial lists). Every meaningful object visible in the analyzed images must be explicitly discussed and assigned an identity record in current_identities (new or reused as appropriate), with a minimum of 10 identities per scene. Do not remove entries from current_identities as steps progress; retain all previously tracked identities even if currently absent. Each identity should preserve first_appeared_step and be updated with last_disappeared_step when it is no longer visible. current_identities should retain small history hints about object lifecycle (such as which steps they appeared, disappeared, were occluded, or transformed) to aid future re-identification. Also track object-group behavior: when multiple objects move together or rotate together, preserve persistent group relationships and note co-motion/co-rotation evidence and step ranges in current_identities metadata. Proactively form meaningful object groups (for example trigger+mechanism, glyph-pair, corridor+exit) and persist them as group identities. Every object id must be a friendly, descriptive snake_case name built from the object's color, shape, and role, such as blue_star_trigger, and never an opaque or numeric ID such as obj_1, object_7, or region_a. Do not repeat established object_identity/3 declarations in objects_pl.",
  "",
  "NAMING CONTRACT: " + DESCRIPTIVE_ID_RULE,
  "",
  "BOUNDING BOX CONTRACT: Every identity must include a bounding_box (key bounding_box; bbox is accepted as an alias) expressed as [x1, y1, x2, y2] — the top-left and bottom-right corners, with x2 > x1 and y2 > y1 — in the same coordinate space you use elsewhere. An object form {x1, y1, x2, y2} or {x, y, width, height} is also accepted. Do not emit degenerate or zero-area boxes.",
  "",
  "LEVEL_1 FIRST-PASS MINIMUM: On level_1, first-pass extraction must include at least these canonical identities from action_trees/ls20/level_1_v2/object_registry.pl before second-pass discovery: blue_black_player, bottom_center_gate, bottom_status_panel, bottom_status_track, cyan_status_blocks, fortress_inner_courtyard, fortress_left_wing, fortress_lower_bridge, fortress_main_body, fortress_right_wing, fortress_upper_stem, gate_burgundy_panel, gate_gray_header, green_fortress, green_status_block, left_boundary_wall, lower_left_burgundy_glyph, lower_left_symbol_card, lower_right_green_target, player_black_core, player_blue_tail, upper_burgundy_glyph, upper_chamber_frame, upper_chamber_interior, upper_left_green_target, yellow_playfield.",
  "",
  "OBJECT EXTRACTION: objects_pl must describe the current state comprehensively but nonredundantly. Detect meaningful connected color regions and useful block-level structures, including blocks, rectangles, bars, line segments, glyphs, holes, enclosures, borders, HUD elements, status indicators, compound objects, and meaningful sub-objects. Perform extraction per image independently first (parent then current) so no object in either image is skipped; then emit the current-state object facts. For level_1, prioritize extracting the full object inventory from the first/root image and treat later image extraction as reconciliation against that baseline. Extraction order must mirror identity workflow: (1) recover and validate objects already in current_identities, then (2) cover unmatched regions and objects in the rest of each image, and add those new objects to current_identities before returning. Objects that are detected in the images must be reflected in both objects_pl and current_identities. Identify likely multi-object assemblies and coupled motion patterns (objects translating or rotating together), represent those relationships explicitly, and create persistent group identities when evidence is strong. Do not treat every individual cell as a separate object unless the cell has an independent semantic role.",
  "",
  "For each object, emit object/3 and all applicable facts selected from: color/2, colors/2, bbox/5, size/3, area/2, shape/2, orientation/2, component_of/2, contains/2, inside/2, adjacent/2, touches/2, overlaps/2, aligned_with/3, symmetry/2, role/2, and confidence/2. Represent object geometry primarily with per-object turtle_program/2 traces instead of occupied_cells/2 or cell_runs/2. Use occupied_cells/2 or cell_runs/2 only when needed as compact supporting evidence that cannot be cleanly expressed in turtle motion alone. Preserve exact topology, connectivity, cavities, holes, borders, and enclosure relationships. Do not replace irregular geometry with oversized rectangles merely to shorten the output.",
  "",
  "objects_pl contains only current-state facts and turtle_program/2 facts associated with canonical objects. It must not contain object_identity/3 declarations, parent-transition facts, cross-state correspondences, or rule hypotheses.",
  "",
  "TURTLE RECONSTRUCTION: Prefer object-wise turtle_program/2 output derived from objects_pl, with one program per canonical object so identity-to-geometry mapping stays explicit. A whole-image reconstruction may be included only as supplemental context when it adds clarity, but it must not replace per-object programs. Start each object program with exactly one absolute set_pos/2, plus set_angle/1, set_color/1, and set_width/1. After that single set_pos/2, all drawing and repositioning must use relative penup/pendown plus fwd/1 and rot/1 only; do not call set_pos/2 again in that object program. set_color/1 and set_width/1 may be used multiple times during relative motion when the object requires color or stroke-width changes. Use set_width/1 values 1 through 4 logical cells. Prefer the largest exact pen width up to 4, so one width-4 stroke is preferred over four parallel width-1 strokes when both paint exactly the same cells.",
  "",
  "Do not generate rect/4, rectangle/4, fill/1, block/4, draw_cells/1, direct four-coordinate box commands, or long lists of independent cell placements. Do not describe a rectangle merely by its x, y, width, and height in a Turtle program. Draw rectangle borders by moving and rotating around their perimeter. Draw solid rectangles and other filled regions as motion-based scan lines, using set_width/1 where exact, with penup repositioning only between disconnected scan strokes. Preserve holes by tracing around or scanning around them rather than painting an oversized block. Each per-object turtle_program/2 must follow these same movement-based rules.",
  "",
  "TRANSITIONS: differences_pl must contain direct parent-to-current observations only. Represent applicable changes such as unchanged, moved, appeared, disappeared, recolored, resized, reshaped, split, merged, opened, closed, consumed, created, destroyed, overwritten, or HUD/status changes. Every claimed transition must include concrete coordinate, color, geometry, or cell-set evidence. When a parent exists and changed cells can be stated clearly, include a compact executable changed-cell patch as diff_turtle_patch/2 (using penup, pendown, set_pos, set_color, set_width, fwd, rot) that covers cleared, recolored, added, and removed cells. Do not infer a game rule in differences_pl.",
  "",
  "INTERACTION CAUSALITY: Detect direct object interactions between parent and current images. If player_entity touches/intersects an object (for example plus_sign) and another object rotates in the same step, emit explicit contact and causal candidates with evidence. Required facts when observed: touched(player_entity, plus_sign). rotated(target_object, degrees(Delta), direction(CW_or_CCW)). caused_by(rotation_event_id, contact(player_entity, plus_sign)).",
  "",
  "EVIDENCE GATE: Only assert caused_by/2 when timing and geometry align (contact appears before/at rotation, orientation delta is non-zero, and no stronger alternative cause is present). Otherwise keep it as hypothetical_rule with confidence.",
  "",
  "GLYPH ALIGNMENT AND EXIT: When rotation aligns two glyph-like markers, emit alignment and escape-state changes explicitly. Required facts when observed: aligned(glyph_a, glyph_b). alignment_changed_to_open(alignment_event_id, top_exit). escape_possible(player_entity, top_exit). If alignment is uncertain, keep it in hypothetical_rule/3 with confidence and evidence notes.",
  "",
  "CORRESPONDENCES: similarities_pl must contain parent-to-current object correspondences only. Record persistent-object matches, similarity scores, matched properties, changed properties, and supporting evidence. Do not force a correspondence when appearance or disappearance is better supported. Reuse canonical IDs from object_registry.pl.",
  "",
  "RULE ANALYSIS: rules_pl must separate observed_rule/2, hypothetical_rule/3, evidence/3, supported_by/2, contradicted_by/2, and confidence/2. observed_rule/2 is reserved for directly established transition regularities. hypothetical_rule/3 must clearly identify assumptions or unresolved alternatives. Evidence must cite concrete state or transition facts rather than restating the hypothesis. Do not promote a hypothesis to an observed rule from a single ambiguous coincidence. Maintain as many plausible hypotheses as possible across steps instead of collapsing early to one explanation; only retire a hypothesis when concrete contradictory evidence is present.",
  "",
  "ENGLISH SUMMARIES: objects_english, differences_english, and rules_english must each be concise plain-English summaries for humans, with exactly one item per line (newline-separated, no paragraph blocks). They should correspond to objects_pl, differences_pl, and rules_pl respectively, and must describe game-state content only (no workflow/process narration about prompts, files, tools, or submission mechanics). Avoid vague filler statements; every line must include at least one concrete in-game observation (specific object, action, relation, location, or change). Emit real newline-separated lines, not literal backslash-n text. When contact-triggered rotation is detected, explicitly mention 'player touched plus_sign' and 'rotation followed'. When glyph alignment opens the exit, explicitly mention that top escape became possible.",
  "",
  "FILE SEPARATION: Put maintained current identity set (including baseline and newly observed identities) and lightweight lifecycle tracking metadata only in current_identities; step-carried hypothesis memory only in current_hypotheses; step-carried action expectation/outcome/surprise records and all 'what/where things are going to be' projections only in action_history; current-state facts only in objects_pl; direct transition facts only in differences_pl (including diff_turtle_patch/2 when parent exists); cross-state correspondences only in similarities_pl; per-object drawing code only in turtle_from_image_pl (derived from objects_pl objects, not a full-frame draw); rule hypotheses, rule evidence, support links, contradictions, and rule confidence only in rules_pl; object summary prose only in objects_english; transition summary prose only in differences_english; and rule summary prose only in rules_english. Use these key names exactly.",
  "",
  "ROOT STATE: When the current state has no parent, differences_pl and similarities_pl must be empty strings (therefore no diff_turtle_patch/2 on root). rules_pl may still contain current-state hypotheses only when they are explicitly marked hypothetical and do not claim parent-transition evidence.",
  "",
  "LOOP CONTROL: Optional exit_value tells the runner what to do next. Allowed values are llm_error, next_iteration, loop_complete, loop_overbudgeted, and unran. Use next_iteration when more discovery/reconciliation work remains, loop_complete when no meaningful uncircled object remains, llm_error when output quality is broken, loop_overbudgeted when budget is exceeded, and unran when execution could not be completed.",
  "",
  "QUALITY CONTROL: Before returning, verify that the result parses as strict JSON, contains all eleven required keys (plus optional exit_value only), uses no Markdown fences, uses only friendly descriptive snake_case object IDs like blue_star_trigger and no opaque or numeric IDs, uses only logical grid coordinates, and contains syntactically plausible SWI-Prolog source in every nonempty *_pl string with correct JSON escaping.",
];

const COMBINED_PROMPT = COMBINED_PROMPT_PARTS.join("\n");
const GAP_DISCOVERY_PASS_PROMPT = [
  "PASS-N GAP DISCOVERY:",
  "Use image #3 as debug_overlay_image. Every drawn box+label in image #3 is already-claimed coverage.",
  "Find meaningful entities not already covered by those boxes, or separable sub-objects not represented yet.",
  "Prioritize boundary/wall anomalies, distinct color segments, UI/status residues, and repeated motifs that should become groups.",
  "Do not duplicate existing IDs, and assign each newly discovered entity a friendly snake_case id like blue_star_trigger. Add sub_type and tight bounding_box for every newly discovered entity.",
  "Emit bounding_box as [x1, y1, x2, y2] top-left and bottom-right corners (x2 > x1, y2 > y1).",
  DESCRIPTIVE_ID_RULE,
  "Return full current_identities updated in place; new additions must include why_new evidence.",
  "If no meaningful uncovered region remains, add no new identities.",
  "Set exit_value=loop_complete when no meaningful uncovered region remains; otherwise exit_value=next_iteration.",
].join("\n");
const DEFAULT_VALIDATOR_PROMPT = [
  "Validate the candidate extraction JSON.",
  "Return strict JSON only: {\"approved\": boolean, \"exit_value\": \"llm_error|next_iteration|loop_complete|loop_overbudgeted|unran\", \"issues\": [\"...\"]}.",
  "Reject when identity ids duplicate, bbox is missing/invalid/out-of-bounds, or new identity count is unreasonable.",
  "Reject when any identity id is not descriptive: ids must encode position/location and orientation (top/bottom, left/right, north/south/east/west, front/rear, corner/edge/center) along with color, shape, and role (for example players_top_hud, northern_most_exit, left_rear_tile), and must never be opaque, generic, or numeric such as obj_1, object_7, or region_a.",
  "Use exit_value=next_iteration when rejecting due to fixable issues.",
  "Use exit_value=loop_complete when approved and no uncircled objects remain; otherwise use next_iteration.",
  "Keep issues short and concrete.",
].join("\n");
const REMOVAL_DISCOVERY_PASS_PROMPT = [
  "remove_smallest_object:",
  "INPUT: the upstream GUESSER runner supplies current_identities plus its prolog/english files via INPUT_FILES; treat GUESSER's current_identities as the authoritative catalog of objects present in the image.",
  "Goal: update supplied current_identities in place and remove the best removable object set from the current image.",
  "SEED FROM GUESSER: first take the identities GUESSER found and try to remove each of them from the current (before) image, working through GUESSER's identified objects as your removal worklist before discovering anything new.",
  "Only after GUESSER's identities have been handled, act like the standard removal pass below and search for any removable objects GUESSER missed.",
  "OBJECT SEARCH ORDER (look for these first):",
  "1) Leaf objects that are isolated, simple, and non-container (no nested identities inside their bounds).",
  "2) Among those leaf objects, find a similar set by shape/color/size/type/proximity.",
  "3) If no similar set is strong enough, fall back to the single smallest valid leaf object by area/pixel footprint.",
  "Container and composite hard gates: never remove a parent/container/group object while removable leaf objects exist.",
  "A valid removable candidate must NOT contain any other identity/object and must not be a merged composite blob.",
  "Special corridor rule: if an object looks like a corridor/maze shell, remove only the shell/walls and leave interior objects/content behind.",
  "Try to remove an array of similar objects in one pass whenever the similarity evidence is clear.",
  "When removing multiple objects in one pass, output each removed image separately as removed_object_1, removed_object_2, ... removed_object_n in ascending numeric order.",
  "Keep removed_object_image as a compatibility alias (use combined removed set, or removed_object_1 when only one object is removed).",
  "Return image_without_object as the original image with all selected removed_object_n pixels removed.",
  "Always carry BOTH images forward for downstream processing: image_without_object and removed_object_image.",
  "Mark each removed identity as not visible/removed in current_identities and preserve all other identities unless direct evidence requires change.",
  "Keep every identity's bounding_box as [x1, y1, x2, y2] top-left and bottom-right corners (x2 > x1, y2 > y1).",
  DESCRIPTIVE_ID_RULE,
  "Set exit_value=next_iteration when one or more valid objects are removed, loop_complete when no valid removable leaf object(s) remain, llm_error on failure.",
].join("\n");
const REGENERATED_IDENTITIES_PROMPT = [
  "regenerated_identities_from_many_objects:",
  "Treat each many_objects_n image as a real source of object candidates, then merge all recovered entities into regenerated_identities.",
  "Run that process across ALL provided INPUT_FILES, not just one selected pair.",
  "B2 priority: output should be mostly a high-level current_identities result (coarse, stable, semantically meaningful identities rather than tiny fragments).",
  "Prefer fewer, stronger identity records with clear roles/relationships over low-level micro-segmentation.",
  "Keep non-identity fields concise/supporting, but still valid per required contract keys.",
  "Return full current_identities and also return regenerated_identities as the same merged identity array for downstream handoff.",
  COMBINED_PROMPT,
].join("\n\n");
const LEGACY_ROOT_GETTER_PROMPT = [
  "legacy_root_getter:",
  "Emulate the old legacy root getter behavior: recover the root/baseline object catalog first, then reconcile downstream images against that baseline.",
  "Prioritize broad, stable identity coverage over narrow per-pass edits.",
  COMBINED_PROMPT,
].join("\n\n");
const VALIDATION_REPAIR_PROMPT = [
  "VALIDATION-REPAIR MODE:",
  "You must correct only the validation failures listed in VALIDATION_ERRORS.",
  "Return strict JSON with the same required keys and a corrected full current_identities list.",
  "Do not invent extra prose. Do not drop valid prior identities.",
  "If a proposed identity fails validation, either fix bbox/type/sub_type or remove that invalid addition.",
  "Rename any non-descriptive id to a descriptive snake_case name that encodes position/location and orientation plus color/shape/role (for example players_top_hud, northern_most_exit, left_rear_tile); never leave an opaque, generic, or numeric id such as obj_1, object_7, or region_a.",
].join("\n");
const DEFAULT_BEFORE_PATH = "action_trees/ls20/level_1/image.png";
const DEFAULT_AFTER_PATH = "action_trees/ls20/level_1/LEFT/image.png";
const STACK_COLUMNS: Array<{ key: StackKey; label: string }> = [
  { key: "A", label: "A" },
  { key: "B", label: "B" },
];
const DEFAULT_TIMEOUT_SECONDS = 180;
const B1_B2_PIPELINE_TIMEOUT_SECONDS = 1800;
function stackColumnsForRoute(routeView: string): Array<{ key: StackKey; label: string }> {
  if (routeView === "arc3B1B2Pipeline") {
    return [{ key: "B", label: "B" }];
  }
  return STACK_COLUMNS;
}
function isB1B2PipelineRoute(routeView: string): boolean {
  return routeView === "arc3B1B2Pipeline";
}
const B1B2_RUNNER_NAMES = ["GUESSER", "REMOVER", "REGENERATOR"];
function runnerDisplayOrdinal(routeView: string, stackKey: StackKey, runnerIndex: number): number {
  if (isB1B2PipelineRoute(routeView) && stackKey === "B") return runnerIndex;
  return runnerIndex + 1;
}
function runnerDisplayId(routeView: string, stackKey: StackKey, runnerIndex: number): string {
  if (isB1B2PipelineRoute(routeView) && stackKey === "B" && runnerIndex < B1B2_RUNNER_NAMES.length) {
    return B1B2_RUNNER_NAMES[runnerIndex];
  }
  return `${stackKey}${runnerDisplayOrdinal(routeView, stackKey, runnerIndex)}`;
}
function runnerRole(routeView: string, stackKey: StackKey, runnerIndex: number): "extraction" | "removal" | "regenerated" | "default" {
  if (isB1B2PipelineRoute(routeView) && stackKey === "B") {
    if (runnerIndex === 0) return "extraction";
    if (runnerIndex === 1) return "removal";
    if (runnerIndex === 2) return "regenerated";
  } else {
    if (stackKey === "B" && runnerIndex === 0) return "removal";
    if (stackKey === "B" && runnerIndex === 1) return "regenerated";
  }
  return "default";
}
function defaultRunnerCountForRoute(routeView: string): number {
  return isB1B2PipelineRoute(routeView) ? 3 : 3;
}
function defaultSetupIndexForRunner(routeView: string, stackKey: StackKey, runnerIndex: number): number {
  const role = runnerRole(routeView, stackKey, runnerIndex);
  if (role === "removal") return 0; // Setup1 single image
  return 0;
}
function defaultInputFilesSourceIdsForRunner(routeView: string, stackKey: StackKey, runnerIndex: number): string[] {
  if (isB1B2PipelineRoute(routeView) && runnerRole(routeView, stackKey, runnerIndex) === "removal") {
    return ["runner:GUESSER"];
  }
  return ["ALL-Setup1"];
}
function shouldUseDescendSetups(routeView: string, stackKey: StackKey): boolean {
  return stackKey === "A" || (isB1B2PipelineRoute(routeView) && stackKey === "B");
}
function defaultTimeoutSecondsForRoute(routeView: string): number {
  return routeView === "arc3B1B2Pipeline" ? B1_B2_PIPELINE_TIMEOUT_SECONDS : DEFAULT_TIMEOUT_SECONDS;
}
const PAGE_MODEL_SENTINEL = "__page_model__";
const COLUMN_MODEL_SENTINEL = "__column_model__";
const RUNNER_WORKSPACE_MODEL_SENTINEL = "__runner_workspace_model__";
const RUNNER_WORKBENCH_MODEL_SENTINEL = "__runner_workbench_model__";
const RUNNER_VALIDATOR_DISABLED = "__runner_validator_disabled__";
const RUNNER_VALIDATOR_PRIMARY_MODEL = "__runner_validator_primary_model__";
const VALIDATOR_PROMPT_DISABLED = "__validator_prompt_disabled__";
const AUTO_GAP_MAX_PASSES = 30;
const AUTO_VALIDATION_REPAIR_ATTEMPTS = 2;
const BASELINE_MAX_NEW_IDENTITIES = 12;
const GAP_PASS_MAX_NEW_IDENTITIES = 2;
const ALL_FIELDS_ABOVE_SOURCE = "<All Column Fields Above>";
const ALL_FIELDS_OTHER_AC_SOURCE = "<All Fields Once from other Column A-C>";
const ALL_FIELDS_OTHER_CA_SOURCE = "<All Fields Once from other Column C-A>";
const ALL_SETUP_SOURCE_PREFIX = "ALL-Setup";
const IMAGE_SUFFIXES = new Set([".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".svg"]);
const TEXT_SUFFIXES = new Set([".txt", ".json", ".md", ".yaml", ".yml", ".csv", ".log", ".metta", ".pl"]);
const repositoryAssetUrl = (path: string) =>
  `/api/repository/asset?path=${encodeURIComponent(path)}`;
const workspaceAssetUrl = (workspaceId: string, path: string) =>
  `/api/workspaces/${encodeURIComponent(workspaceId)}/asset?path=${encodeURIComponent(path)}`;
const defaultImagePair = (stackKey?: StackKey) => {
  const beforePath = DEFAULT_BEFORE_PATH;
  const afterPath = stackKey === "A" ? DEFAULT_BEFORE_PATH : DEFAULT_AFTER_PATH;
  return {
    before: {
      name: beforePath,
      dataUrl: repositoryAssetUrl(beforePath),
    },
    after: {
      name: afterPath,
      dataUrl: repositoryAssetUrl(afterPath),
    },
  };
};

function defaultSetups(stackKey: StackKey): StackSetup[] {
  const pair = defaultImagePair(stackKey);
  return [{
    id: `${stackKey}-setup-1`,
    label: "Setup1",
    command: "level_1",
    note: "default",
    beforeImage: stackKey === "A" ? null : pair.before,
    afterImage: pair.after,
  }];
}

function normalizeAssetPath(value: string): string {
  return value.trim().replace(/\\/g, "/");
}

function setupCommandFromPath(path: string): string {
  const normalized = normalizeAssetPath(path);
  if (!normalized) return "";
  const segments = normalized.split("/").filter(Boolean);
  if (segments.length < 2) return "";
  const command = segments[segments.length - 2] || "";
  if (/^level_/i.test(command)) return command;
  return command.toUpperCase();
}

function imageSelectionFromPath(workspaceId: string, path: string, fallback?: ImageSelection): ImageSelection {
  const normalized = normalizeAssetPath(path);
  if (!normalized) return fallback || { name: "", dataUrl: "" };
  if (normalized.startsWith("data:image/") || normalized.startsWith("http://") || normalized.startsWith("https://")) {
    return { name: normalized, dataUrl: normalized };
  }
  if (normalized.startsWith("data/") || normalized.startsWith("knowledge/data/")) {
    return { name: normalized, dataUrl: workspaceAssetUrl(workspaceId, normalized) };
  }
  return { name: normalized, dataUrl: repositoryAssetUrl(normalized) };
}

function level1PathDepth(path: string): number {
  const normalized = normalizeAssetPath(path).toLowerCase();
  const prefix = "data/level_1";
  if (!normalized.startsWith(prefix)) return 0;
  const remainder = normalized.slice(prefix.length).replace(/^\/+/, "");
  if (!remainder) return 0;
  const directory = remainder.includes("/") ? remainder.slice(0, remainder.lastIndexOf("/")) : "";
  if (!directory) return 0;
  return directory.split("/").filter(Boolean).length;
}

function parentImagePath(path: string): string {
  const normalized = normalizeAssetPath(path);
  if (!normalized) return "";
  const slash = normalized.lastIndexOf("/");
  if (slash <= 0) return "";
  const fileName = normalized.slice(slash + 1);
  const directory = normalized.slice(0, slash);
  const parentSlash = directory.lastIndexOf("/");
  if (parentSlash <= 0) return "";
  const parentDirectory = directory.slice(0, parentSlash);
  const candidate = `${parentDirectory}/${fileName}`;
  if (candidate === normalized) return "";
  return candidate;
}

function stackADescendSetupsFromFiles(workspaceId: string, files: WorkspaceFileRecord[]): StackSetup[] {
  const imageCandidates = files
    .filter((file) => IMAGE_SUFFIXES.has((file.suffix || "").toLowerCase()))
    .map((file) => file.path.replace(/\\/g, "/"))
    .filter((path) => /^data\/level_1(?:\/[^/]+)*\/image\.(png|jpg|jpeg|webp|bmp|gif)$/i.test(path))
    .sort((left, right) => {
      const depthLeft = level1PathDepth(left);
      const depthRight = level1PathDepth(right);
      return depthLeft - depthRight || left.localeCompare(right);
    });
  if (!imageCandidates.length) return [];
  // Keep one setup per descend directory and prefer png/jpg first if multiple image.* files exist.
  const pathScore = (path: string) => {
    const lower = path.toLowerCase();
    if (lower.endsWith(".png")) return 0;
    if (lower.endsWith(".jpg")) return 1;
    if (lower.endsWith(".jpeg")) return 2;
    return 3;
  };
  const byDirectory = new Map<string, string>();
  for (const path of imageCandidates) {
    const directory = path.slice(0, Math.max(0, path.lastIndexOf("/")));
    const existing = byDirectory.get(directory);
    if (!existing || pathScore(path) < pathScore(existing) || (pathScore(path) === pathScore(existing) && path.localeCompare(existing) < 0)) {
      byDirectory.set(directory, path);
    }
  }
  const selectedPaths = Array.from(byDirectory.values()).sort((left, right) => {
    const depthLeft = level1PathDepth(left);
    const depthRight = level1PathDepth(right);
    return depthLeft - depthRight || left.localeCompare(right);
  });
  return selectedPaths.map((path, index) => {
    const depth = level1PathDepth(path);
    const directory = path.slice(0, Math.max(0, path.lastIndexOf("/")));
    const parentDirectory = directory.includes("/") ? directory.slice(0, directory.lastIndexOf("/")) : "";
    const beforePath = byDirectory.get(parentDirectory) || selectedPaths[index - 1] || "";
    const beforeSelection: ImageSelection | null = beforePath
      ? {
        name: beforePath,
        dataUrl: workspaceAssetUrl(workspaceId, beforePath),
      }
      : null;
    const afterSelection: ImageSelection = {
      name: path,
      dataUrl: workspaceAssetUrl(workspaceId, path),
    };
    return {
      id: `A-setup-${index + 1}`,
      label: `Setup${index + 1}`,
      command: setupCommandFromPath(path),
      note: depth ? `depth ${depth}` : "root",
      beforeImage: beforeSelection,
      afterImage: afterSelection,
    };
  });
}

const CAPABILITY_KEYS: Array<keyof ModelCapabilities> = [
  "multimodal",
  "vision",
  "summary",
  "audio",
  "reasoning",
  "tools",
  "code",
  "json",
  "text",
];

const normalizedModelName = (model: ModelChoice) =>
  `${model.id} ${(model.label || "")}`.toLowerCase();

// Web-verified exceptions for popular models. Everything else relies on backend-declared capabilities.
const MODEL_CAPABILITY_OVERRIDES: Array<{
  match: (model: ModelChoice) => boolean;
  capabilities: Partial<ModelCapabilities>;
}> = [
  {
    // Source: https://ai.google.dev/gemma/docs/capabilities/vision/image
    // "Gemma 3 and later models" support image understanding.
    match: (model) => /gemma[-_/](3|4)([^0-9]|$)/.test(normalizedModelName(model)),
    capabilities: { vision: true, multimodal: true, text: true, reasoning: true },
  },
  {
    // Source: https://platform.claude.com/docs/en/build-with-claude/vision
    // Claude 3+ family accepts image content blocks in API requests.
    match: (model) => {
      const name = normalizedModelName(model);
      return /claude[-_/](3|3\.5|3\.7|4|5)/.test(name)
        || /claude[-_/](haiku|sonnet|opus)/.test(name);
    },
    capabilities: { vision: true, multimodal: true, text: true },
  },
];

const normalizedCapabilities = (model: ModelChoice): ModelCapabilities => {
  const raw = (model.capabilities || {}) as Record<string, unknown>;
  const base: ModelCapabilities = {
    multimodal: raw.multimodal === true,
    vision: raw.vision === true,
    summary: raw.summary === true,
    audio: raw.audio === true,
    reasoning: raw.reasoning === true,
    tools: raw.tools === true,
    code: raw.code === true,
    json: raw.json === true,
    text: raw.text === true,
  };
  const override = MODEL_CAPABILITY_OVERRIDES.find((rule) => rule.match(model));
  return override ? { ...base, ...override.capabilities } : base;
};

const capabilityTags = (model: ModelChoice): string[] => {
  const capabilities = normalizedCapabilities(model);
  return CAPABILITY_KEYS.filter((key) => capabilities[key]);
};

const modelOptionLabel = (model: ModelChoice) => {
  const tags = capabilityTags(model);
  const tagSuffix = tags.length ? ` [${tags.join(", ")}]` : "";
  return `${model.backendLabel || model.backendId || model.id} · ${model.label || model.id}${tagSuffix}`;
};

const runnerModelSelectionLabel = (value: string) => {
  if (value === COLUMN_MODEL_SENTINEL) return "Column Model";
  if (value === RUNNER_WORKSPACE_MODEL_SENTINEL) return "Workspace Model";
  if (value === RUNNER_WORKBENCH_MODEL_SENTINEL) return "Workbench Model";
  if (value === RUNNER_VALIDATOR_PRIMARY_MODEL) return "Runner Model";
  if (value === RUNNER_VALIDATOR_DISABLED) return "Disabled";
  return value || "none";
};

const effectiveModelSummary = (modelId: string, models: ModelChoice[]): string => {
  if (!modelId) return "none";
  const model = models.find((item) => item.id === modelId);
  if (!model) return modelId;
  const backend = model.backendId || model.backendLabel || "backend";
  return `${backend}/${model.id}`;
};

async function readImageFile(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result || ""));
    reader.onerror = () => reject(reader.error || new Error(`Could not read ${file.name}`));
    reader.readAsDataURL(file);
  });
}

function resolveFilesSource(
  filesSourceId: string,
  runners: Array<{ id: string; stackKey: StackKey; parsed: ParsedPrologPayload | null; rawResponse: string; generationSeq: number }>,
  currentStackKey: StackKey,
  history: OutputHistoryEntry[],
): { label: string; content: string } | null {
  if (!filesSourceId || filesSourceId === "none") return null;
  if (filesSourceId === "latest:this") {
    const latest = [...runners]
      .filter((runner) => runner.stackKey === currentStackKey && runner.generationSeq > 0 && (runner.parsed || runner.rawResponse))
      .sort((left, right) => right.generationSeq - left.generationSeq)[0];
    if (!latest) return null;
    const content = latest.parsed
      ? JSON.stringify(latest.parsed, null, 2)
      : latest.rawResponse;
    if (!content) return null;
    return { label: `Latest generated files (stack ${currentStackKey}: ${latest.id})`, content };
  }
  if (filesSourceId === "latest:any") {
    const latest = [...runners]
      .filter((runner) => runner.generationSeq > 0 && (runner.parsed || runner.rawResponse))
      .sort((left, right) => right.generationSeq - left.generationSeq)[0];
    if (!latest) return null;
    const content = latest.parsed
      ? JSON.stringify(latest.parsed, null, 2)
      : latest.rawResponse;
    if (!content) return null;
    return { label: `Latest generated files (${latest.id})`, content };
  }
  if (filesSourceId.startsWith("latest:stack:")) {
    const stackKey = filesSourceId.slice("latest:stack:".length) as StackKey;
    const latest = [...runners]
      .filter((runner) => runner.stackKey === stackKey && runner.generationSeq > 0 && (runner.parsed || runner.rawResponse))
      .sort((left, right) => right.generationSeq - left.generationSeq)[0];
    if (!latest) return null;
    const content = latest.parsed
      ? JSON.stringify(latest.parsed, null, 2)
      : latest.rawResponse;
    if (!content) return null;
    return { label: `Latest generated files (stack ${stackKey}: ${latest.id})`, content };
  }
  if (filesSourceId.startsWith("runner:")) {
    const runnerId = filesSourceId.slice("runner:".length);
    const runner = runners.find((candidate) => candidate.id === runnerId);
    if (!runner) return null;
    const content = runner.parsed
      ? JSON.stringify(runner.parsed, null, 2)
      : runner.rawResponse;
    if (!content) return null;
    return { label: `Files ${runnerId}`, content };
  }
  if (filesSourceId.startsWith("file:")) {
    const remainder = filesSourceId.slice("file:".length);
    const separator = remainder.indexOf(":");
    if (separator <= 0) return null;
    const runnerId = remainder.slice(0, separator);
    const key = remainder.slice(separator + 1);
    const runner = runners.find((candidate) => candidate.id === runnerId);
    if (!runner?.parsed) return null;
    const record = runner.parsed as unknown as Record<string, unknown>;
    if (!Object.prototype.hasOwnProperty.call(record, key)) return null;
    const value = record[key];
    const content = typeof value === "string" ? value : JSON.stringify(value ?? null, null, 2);
    return { label: `Files ${runnerId}.${key}`, content };
  }
  if (filesSourceId.startsWith("history:")) {
    const historyId = filesSourceId.slice("history:".length);
    const entry = history.find((candidate) => candidate.id === historyId);
    if (!entry) return null;
    const content = entry.parsed
      ? JSON.stringify(entry.parsed, null, 2)
      : entry.rawResponse;
    if (!content) return null;
    return { label: `History ${entry.id} (${entry.runnerId})`, content };
  }
  if (filesSourceId.startsWith("history-file:")) {
    const remainder = filesSourceId.slice("history-file:".length);
    const separator = remainder.indexOf(":");
    if (separator <= 0) return null;
    const historyId = remainder.slice(0, separator);
    const key = remainder.slice(separator + 1);
    const entry = history.find((candidate) => candidate.id === historyId);
    if (!entry?.parsed) return null;
    const record = entry.parsed as unknown as Record<string, unknown>;
    if (!Object.prototype.hasOwnProperty.call(record, key)) return null;
    const value = record[key];
    const content = typeof value === "string" ? value : JSON.stringify(value ?? null, null, 2);
    return { label: `History ${entry.id}.${key}`, content };
  }
  return null;
}

function resolveReferenceToken(
  token: string,
  currentStackKey: StackKey,
  stacks: StackColumnState[],
  currentRunner?: RunnerState,
): { label: string; content: string } | null {
  const trimmed = token.trim();
  if (!trimmed) return null;
  const setupFileMatch = /^setup-file:([^:]+):(.+)$/i.exec(trimmed);
  if (setupFileMatch) {
    const setupId = setupFileMatch[1];
    const fileKey = setupFileMatch[2];
    for (const stack of stacks) {
      const setup = (stack.setups || []).find((candidate) => candidate.id === setupId);
      if (!setup?.analysis) continue;
      const item = [...setup.analysis.subimages, ...setup.analysis.textFiles]
        .find((file) => file.key === fileKey);
      if (item) {
        return { label: `${setup.label || setupId} / ${item.label}`, content: item.value };
      }
    }
    return null;
  }
  const columnTextMatch = /^([ABCX])_(generated|command)$/i.exec(trimmed);
  if (columnTextMatch) {
    const stackToken = columnTextMatch[1].toUpperCase();
    const stackKey = (stackToken === "X" ? currentStackKey : stackToken) as StackKey;
    const stack = stacks.find((candidate) => candidate.key === stackKey);
    if (!stack) return null;
    const field = columnTextMatch[2].toLowerCase() === "generated" ? "Generated" : "Command";
    const content = field === "Generated" ? stack.desc1 : stack.desc2;
    return {
      label: `${trimmed} -> ${field.toUpperCase()}`,
      content,
    };
  }
  const promptMatch = /^([ABCX])(?:_([0-9]+))?_prompt$/i.exec(trimmed);
  if (promptMatch) {
    const stackToken = promptMatch[1].toUpperCase();
    const stackKey = (stackToken === "X" ? currentStackKey : stackToken) as StackKey;
    const promptIndex = Math.max(1, Number.parseInt(promptMatch[2] || "1", 10)) - 1;
    const runnerNumber = promptIndex + 1;
    const stack = stacks.find((candidate) => candidate.key === stackKey);
    const runner = stack?.runners[promptIndex];
    if (!runner) return null;
    return {
      label: `${trimmed} -> PROMPT`,
      content: runner.promptText || "",
    };
  }
  const legacyPromptMatch = /^([ABCX])_prompt([0-9]+)$/i.exec(trimmed);
  if (legacyPromptMatch) {
    const stackToken = legacyPromptMatch[1].toUpperCase();
    const stackKey = (stackToken === "X" ? currentStackKey : stackToken) as StackKey;
    const promptIndex = Math.max(1, Number.parseInt(legacyPromptMatch[2] || "1", 10)) - 1;
    const runnerNumber = promptIndex + 1;
    const stack = stacks.find((candidate) => candidate.key === stackKey);
    const runner = stack?.runners[promptIndex];
    if (!runner) return null;
    return {
      label: `${trimmed} -> PROMPT`,
      content: runner.promptText || "",
    };
  }
  const setupFieldMatch = /^([ABCX])(?:_SETUP([0-9]+))?_(label|command|note|before_path|after_path|before_image|after_image)$/i.exec(trimmed);
  if (setupFieldMatch) {
    const stackToken = setupFieldMatch[1].toUpperCase();
    const stackKey = (stackToken === "X" ? currentStackKey : stackToken) as StackKey;
    const stack = stacks.find((candidate) => candidate.key === stackKey);
    if (!stack) return null;
    const setups = stack.setups?.length ? stack.setups : defaultSetups(stackKey);
    const setupIndex = setupFieldMatch[2]
      ? Math.max(0, Number.parseInt(setupFieldMatch[2], 10) - 1)
      : Math.max(0, currentRunner?.setupIndex || 0);
    const setup = setups[Math.min(setups.length - 1, setupIndex)];
    if (!setup) return null;
    const field = setupFieldMatch[3].toLowerCase();
    if (field === "label") {
      return { label: `${trimmed} -> SETUP LABEL`, content: setup.label || "" };
    }
    if (field === "command") {
      return { label: `${trimmed} -> SETUP COMMAND`, content: setup.command || "" };
    }
    if (field === "note") {
      return { label: `${trimmed} -> SETUP NOTE`, content: setup.note || "" };
    }
    if (field === "before_path") {
      return { label: `${trimmed} -> SETUP BEFORE PATH`, content: setup.beforeImage?.name || "null" };
    }
    if (field === "after_path") {
      return { label: `${trimmed} -> SETUP AFTER PATH`, content: setup.afterImage.name };
    }
    if (field === "before_image") {
      return {
        label: `${trimmed} -> SETUP BEFORE IMAGE`,
        content: setup.beforeImage
          ? JSON.stringify({ name: setup.beforeImage.name, dataUrl: setup.beforeImage.dataUrl }, null, 2)
          : "null",
      };
    }
    return {
      label: `${trimmed} -> SETUP AFTER IMAGE`,
      content: JSON.stringify({ name: setup.afterImage.name, dataUrl: setup.afterImage.dataUrl }, null, 2),
    };
  }
  const match = /^([ABCX])(?:([0-9]+))?\.(image1|image2)$/i.exec(trimmed);
  if (!match) return null;
  const stackToken = match[1].toUpperCase();
  const stackKey = (stackToken === "X" ? currentStackKey : stackToken) as StackKey;
  const stack = stacks.find((candidate) => candidate.key === stackKey);
  if (!stack) return null;
  const slot = match[3].toLowerCase() === "image1" ? "before" : "after";
  const runnerSuffix = match[2] ? ` (runner ${stackKey}${match[2]})` : "";
  const image = slot === "before" ? stack.beforeImage : stack.afterImage;
  const description = slot === "before" ? stack.desc1 : stack.desc2;
  return {
    label: `${trimmed} -> ${imageFieldLabel(slot)}${runnerSuffix}`,
    content: [
      `Reference token: ${trimmed}`,
      `Resolved stack: ${stackKey}${runnerSuffix}`,
      `Resolved image slot: ${imageFieldLabel(slot)}`,
      `Description: ${description}`,
      `Image: ${image ? image.name : "not loaded"}`,
    ].join("\n"),
  };
}

function resolveFilesSources(
  filesSourceIds: string[],
  runners: Array<{ id: string; stackKey: StackKey; parsed: ParsedPrologPayload | null; rawResponse: string; generationSeq: number }>,
  currentStackKey: StackKey,
  history: OutputHistoryEntry[],
  stacks: StackColumnState[],
  currentRunner?: RunnerState,
): Array<{ id: string; label: string; content: string }> {
  const expandSourceId = (sourceId: string): string[] => {
    const setupBundleMatch = /^ALL-Setup([0-9]+)$/i.exec(sourceId.trim());
    if (!setupBundleMatch) return [sourceId];
    const setupOrdinal = Math.max(1, Number.parseInt(setupBundleMatch[1] || "1", 10));
    return [
      `X_SETUP${setupOrdinal}_LABEL`,
      `X_SETUP${setupOrdinal}_COMMAND`,
      `X_SETUP${setupOrdinal}_NOTE`,
      `X_SETUP${setupOrdinal}_BEFORE_PATH`,
      `X_SETUP${setupOrdinal}_AFTER_PATH`,
      `X_SETUP${setupOrdinal}_BEFORE_IMAGE`,
      `X_SETUP${setupOrdinal}_AFTER_IMAGE`,
    ];
  };
  const unique = Array.from(new Set((filesSourceIds || []).flatMap(expandSourceId).filter((item) => item
    && item !== "none"
    && item !== ALL_FIELDS_ABOVE_SOURCE
    && item !== ALL_FIELDS_OTHER_AC_SOURCE
    && item !== ALL_FIELDS_OTHER_CA_SOURCE)));
  return unique
    .map((id) => {
      const resolved = resolveFilesSource(id, runners, currentStackKey, history)
        || resolveReferenceToken(id, currentStackKey, stacks, currentRunner);
      return resolved ? { id, ...resolved } : null;
    })
    .filter((item): item is { id: string; label: string; content: string } => Boolean(item));
}

function dedupeSourceOptions(options: Array<{ value: string; label: string }>): Array<{ value: string; label: string }> {
  const seen = new Set<string>();
  const result: Array<{ value: string; label: string }> = [];
  for (const option of options) {
    if (!option.value || seen.has(option.value)) continue;
    seen.add(option.value);
    result.push(option);
  }
  return result;
}

function dedupeStringList(values: string[]): string[] {
  const seen = new Set<string>();
  const output: string[] = [];
  for (const value of values) {
    if (!value || seen.has(value)) continue;
    seen.add(value);
    output.push(value);
  }
  return output;
}

function isGeneratedToken(value: string): boolean {
  const trimmed = value.trim();
  return /^(?:[ABC](?:_[0-9]+)?_)?GENERATED$/i.test(trimmed)
    || /^(?:[ABCX])_GENERATED$/i.test(trimmed);
}

function displayFieldToken(value: string): string {
  const trimmed = value.trim();
  if (/^ALL-Setup[0-9]+$/i.test(trimmed)) return trimmed;
  const setupFile = /^setup-file:[^:]+:(.+)$/i.exec(trimmed);
  if (setupFile) return `SETUP_FILE ${setupFile[1]}`;
  const prompt = /^(?:[ABC](?:_[0-9]+)?_)?PROMPT$/i.exec(trimmed)
    || /^(?:[ABCX])_PROMPT[0-9]+$/i.exec(trimmed)
    || /^(?:[ABCX])(?:_([0-9]+))?_PROMPT$/i.exec(trimmed);
  if (prompt) return "PROMPT";
  const generated = /^(?:[ABC](?:_[0-9]+)?_)?GENERATED$/i.exec(trimmed)
    || /^(?:[ABCX])_GENERATED$/i.exec(trimmed);
  if (generated) return "GENERATED";
  const command = /^(?:[ABC](?:_[0-9]+)?_)?COMMAND$/i.exec(trimmed)
    || /^(?:[ABCX])_COMMAND$/i.exec(trimmed);
  if (command) return "COMMAND";
  const setupField = /^(?:[ABCX])(?:_SETUP[0-9]+)?_(LABEL|COMMAND|NOTE|BEFORE_PATH|AFTER_PATH|BEFORE_IMAGE|AFTER_IMAGE)$/i.exec(trimmed);
  if (setupField) return `SETUP_${setupField[1].toUpperCase()}`;
  if (/^(?:[ABCX](?:[0-9]+)?\.)?IMAGE1$/i.test(trimmed)) return "PARENT_IMAGE";
  if (/^(?:[ABCX](?:[0-9]+)?\.)?IMAGE2$/i.test(trimmed)) return "CURRENT_IMAGE";
  return trimmed;
}

async function loadImage(source: string): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const image = new Image();
    image.onload = () => resolve(image);
    image.onerror = () => reject(new Error("Could not load submitted image."));
    image.src = source;
  });
}

async function pairSheet(before: { label: string; source: string }, after: { label: string; source: string }): Promise<string> {
  const [left, right] = await Promise.all([loadImage(before.source), loadImage(after.source)]);
  const canvas = window.document.createElement("canvas");
  canvas.width = 1024;
  canvas.height = 560;
  const context = canvas.getContext("2d");
  if (!context) throw new Error("This browser could not prepare the image pair sheet.");
  context.fillStyle = "#061118";
  context.fillRect(0, 0, canvas.width, canvas.height);
  context.fillStyle = "#4ee8dc";
  context.font = "18px ui-monospace, monospace";
  const drawCell = (image: HTMLImageElement, x: number, label: string) => {
    const frameTop = 34;
    const frameWidth = 492;
    const frameHeight = 512;
    const scale = Math.min(frameWidth / image.naturalWidth, frameHeight / image.naturalHeight);
    const width = Math.max(1, Math.round(image.naturalWidth * scale));
    const height = Math.max(1, Math.round(image.naturalHeight * scale));
    context.fillText(label, x + 8, 22);
    context.imageSmoothingEnabled = false;
    context.drawImage(image, x + Math.floor((frameWidth - width) / 2), frameTop + Math.floor((frameHeight - height) / 2), width, height);
  };
  drawCell(left, 12, `1. ${before.label}`);
  drawCell(right, 520, `2. ${after.label}`);
  return canvas.toDataURL("image/png");
}

function coerceIdentityBoundingBox(box: unknown): [number, number, number, number] | null {
  let a: unknown;
  let b: unknown;
  let c: unknown;
  let d: unknown;
  let cornerHint = false;
  if (Array.isArray(box) && box.length === 4) {
    [a, b, c, d] = box;
  } else if (box && typeof box === "object") {
    const record = box as Record<string, unknown>;
    const hasCorner = record.x2 !== undefined || record.y2 !== undefined
      || record.right !== undefined || record.bottom !== undefined;
    if (hasCorner) {
      a = record.x1 ?? record.left ?? record.x;
      b = record.y1 ?? record.top ?? record.y;
      c = record.x2 ?? record.right;
      d = record.y2 ?? record.bottom;
      cornerHint = true;
    } else {
      a = record.x ?? record.left;
      b = record.y ?? record.top;
      c = record.w ?? record.width;
      d = record.h ?? record.height;
    }
  } else {
    return null;
  }
  const na = Number(a);
  const nb = Number(b);
  const nc = Number(c);
  const nd = Number(d);
  if (![na, nb, nc, nd].every((value) => Number.isFinite(value))) return null;
  // Corner form [x1, y1, x2, y2] is detected when the last pair is a valid
  // bottom-right corner (strictly greater than the top-left); convert to
  // the canonical [x, y, width, height] the rest of the pipeline expects.
  const corners = cornerHint || (nc > na && nd > nb);
  const width = corners ? nc - na : nc;
  const height = corners ? nd - nb : nd;
  return [na, nb, width, height];
}

function asIdentityCandidates(payload: ParsedPrologPayload | null | undefined): IdentityCandidate[] {
  if (!payload || !Array.isArray(payload.current_identities)) return [];
  return payload.current_identities
    .map<IdentityCandidate | null>((item) => {
      if (!item || typeof item !== "object") return null;
      const record = item as Record<string, unknown>;
      const id = String(record.id || "").trim();
      if (!id) return null;
      const type = typeof record.type === "string" ? record.type : undefined;
      const sub_type = typeof record.sub_type === "string" ? record.sub_type : undefined;
      const rawBox = record.bounding_box ?? record.bbox ?? record.box;
      const normalizedBox = coerceIdentityBoundingBox(rawBox);
      if (!normalizedBox) return { id, type, sub_type };
      return {
        id,
        type,
        sub_type,
        bounding_box: normalizedBox,
      };
    })
    .filter((item): item is IdentityCandidate => Boolean(item));
}

function normalizeBboxToPixels(
  bbox: [number, number, number, number],
  imageWidth: number,
  imageHeight: number,
): { left: number; top: number; width: number; height: number } | null {
  const [x, y, width, height] = bbox;
  if (!Number.isFinite(x) || !Number.isFinite(y) || !Number.isFinite(width) || !Number.isFinite(height)) return null;
  if (width <= 0 || height <= 0) return null;
  const gridScaleX = imageWidth >= 64 ? imageWidth / 64 : 1;
  const gridScaleY = imageHeight >= 64 ? imageHeight / 64 : 1;
  const logicalGridRenderable = gridScaleX >= 2 && gridScaleY >= 2;
  const logicalGridBox = logicalGridRenderable && Math.max(x + width, y + height) <= 80;
  const scaleX = logicalGridBox ? gridScaleX : 1;
  const scaleY = logicalGridBox ? gridScaleY : 1;
  const left = Math.round(x * scaleX);
  const top = Math.round(y * scaleY);
  const boxWidth = Math.max(1, Math.round(width * scaleX));
  const boxHeight = Math.max(1, Math.round(height * scaleY));
  return { left, top, width: boxWidth, height: boxHeight };
}

function identityTypeBucket(candidate: IdentityCandidate): "group" | "global" | "normal" {
  const tag = `${candidate.type || ""} ${candidate.sub_type || ""}`.toLowerCase();
  if (tag.includes("group")) return "group";
  if (tag.includes("background") || tag.includes("playfield") || tag.includes("boundary") || tag.includes("wall")) return "global";
  return "normal";
}

async function buildImageValidationFrame(source: string): Promise<ImageValidationFrame> {
  const image = await loadImage(source);
  const canvas = window.document.createElement("canvas");
  canvas.width = image.naturalWidth;
  canvas.height = image.naturalHeight;
  const context = canvas.getContext("2d");
  if (!context) throw new Error("This browser could not prepare image validation.");
  context.drawImage(image, 0, 0);
  const imageData = context.getImageData(0, 0, canvas.width, canvas.height);
  return { width: canvas.width, height: canvas.height, rgba: imageData.data };
}

function dominantColorRatio(
  frame: ImageValidationFrame,
  left: number,
  top: number,
  width: number,
  height: number,
): number {
  const right = Math.min(frame.width, left + width);
  const bottom = Math.min(frame.height, top + height);
  if (right <= left || bottom <= top) return 0;
  const stepX = Math.max(1, Math.floor((right - left) / 40));
  const stepY = Math.max(1, Math.floor((bottom - top) / 40));
  const counts = new Map<string, number>();
  let total = 0;
  for (let y = top; y < bottom; y += stepY) {
    for (let x = left; x < right; x += stepX) {
      const index = (y * frame.width + x) * 4;
      const r = frame.rgba[index] >> 4;
      const g = frame.rgba[index + 1] >> 4;
      const b = frame.rgba[index + 2] >> 4;
      const key = `${r}:${g}:${b}`;
      counts.set(key, (counts.get(key) || 0) + 1);
      total += 1;
    }
  }
  if (total <= 0) return 0;
  let dominant = 0;
  counts.forEach((count) => {
    if (count > dominant) dominant = count;
  });
  return dominant / total;
}

function validatePassOutput(
  previous: ParsedPrologPayload | null | undefined,
  next: ParsedPrologPayload | null | undefined,
  frame: ImageValidationFrame,
  mode: "baseline" | "gap",
): PassValidationResult {
  const issues: ValidationIssue[] = [];
  if (!next || !Array.isArray(next.current_identities)) {
    return { accepted: false, newCount: 0, issues: [{ id: "*", code: "missing_current_identities", detail: "current_identities is missing or not an array." }] };
  }
  const previousIds = identityIdSet(previous);
  const all = asIdentityCandidates(next);
  const duplicates = new Set<string>();
  const seen = new Set<string>();
  for (const identity of all) {
    if (seen.has(identity.id)) duplicates.add(identity.id);
    seen.add(identity.id);
  }
  duplicates.forEach((id) => {
    issues.push({ id, code: "duplicate_id", detail: "Duplicate identity id in current_identities." });
  });
  const newOnly = all.filter((identity) => !previousIds.has(identity.id));
  const maxAllowed = mode === "gap" ? GAP_PASS_MAX_NEW_IDENTITIES : BASELINE_MAX_NEW_IDENTITIES;
  if (newOnly.length > maxAllowed) {
    issues.push({
      id: "*",
      code: "too_many_new_identities",
      detail: `Pass produced ${newOnly.length} new identities; max allowed for ${mode} pass is ${maxAllowed}.`,
    });
  }
  for (const identity of all) {
    if (!identity.bounding_box) {
      issues.push({ id: identity.id, code: "missing_bbox", detail: "Every identity must include bounding_box." });
      continue;
    }
    const pixelBox = normalizeBboxToPixels(identity.bounding_box, frame.width, frame.height);
    if (!pixelBox) {
      issues.push({ id: identity.id, code: "invalid_bbox", detail: "bounding_box must be numeric with positive width/height." });
      continue;
    }
    const outOfBounds = pixelBox.left < 0
      || pixelBox.top < 0
      || pixelBox.left + pixelBox.width > frame.width
      || pixelBox.top + pixelBox.height > frame.height;
    if (outOfBounds) {
      issues.push({
        id: identity.id,
        code: "bbox_out_of_bounds",
        detail: `Projected bbox is outside image bounds ${frame.width}x${frame.height}.`,
      });
    }
    if (!previousIds.has(identity.id)) {
      if (!identity.type || !identity.sub_type) {
        issues.push({ id: identity.id, code: "missing_type_or_sub_type", detail: "New identities must include type and sub_type." });
      }
      const bucket = identityTypeBucket(identity);
      if (bucket === "normal") {
        const area = pixelBox.width * pixelBox.height;
        if (area > frame.width * frame.height * 0.35) {
          issues.push({ id: identity.id, code: "bbox_too_large", detail: "New normal identity bbox is too large for a single object." });
        }
        const support = dominantColorRatio(frame, pixelBox.left, pixelBox.top, pixelBox.width, pixelBox.height);
        if (support < 0.09) {
          issues.push({
            id: identity.id,
            code: "low_pixel_support",
            detail: `Dominant-color support ${support.toFixed(2)} is too low; tighten or reposition bbox.`,
          });
        }
      }
    }
  }
  return { accepted: issues.length === 0, newCount: newOnly.length, issues };
}

function newIdentityCandidates(
  previous: ParsedPrologPayload | null | undefined,
  next: ParsedPrologPayload | null | undefined,
): IdentityCandidate[] {
  const priorIds = identityIdSet(previous);
  return asIdentityCandidates(next).filter((identity) => !priorIds.has(identity.id));
}

function pickRemovableIdentity(
  previous: ParsedPrologPayload | null | undefined,
  next: ParsedPrologPayload | null | undefined,
): IdentityCandidate | null {
  const candidates = newIdentityCandidates(previous, next)
    .filter((identity) => identity.bounding_box && identityTypeBucket(identity) === "normal");
  return candidates[0] || null;
}

function dominantBorderColor(
  frame: ImageValidationFrame,
  left: number,
  top: number,
  width: number,
  height: number,
): [number, number, number, number] {
  const right = Math.min(frame.width - 1, left + width);
  const bottom = Math.min(frame.height - 1, top + height);
  const counts = new Map<string, number>();
  const push = (x: number, y: number) => {
    if (x < 0 || y < 0 || x >= frame.width || y >= frame.height) return;
    const index = (y * frame.width + x) * 4;
    const key = `${frame.rgba[index]},${frame.rgba[index + 1]},${frame.rgba[index + 2]},${frame.rgba[index + 3]}`;
    counts.set(key, (counts.get(key) || 0) + 1);
  };
  for (let x = left - 1; x <= right + 1; x += 1) {
    push(x, top - 1);
    push(x, bottom + 1);
  }
  for (let y = top - 1; y <= bottom + 1; y += 1) {
    push(left - 1, y);
    push(right + 1, y);
  }
  if (!counts.size) return [0, 0, 0, 255];
  let topKey = "";
  let topCount = -1;
  counts.forEach((count, key) => {
    if (count > topCount) {
      topCount = count;
      topKey = key;
    }
  });
  const parts = topKey.split(",").map((item) => Number(item));
  return [
    Number.isFinite(parts[0]) ? parts[0] : 0,
    Number.isFinite(parts[1]) ? parts[1] : 0,
    Number.isFinite(parts[2]) ? parts[2] : 0,
    Number.isFinite(parts[3]) ? parts[3] : 255,
  ];
}

async function generateRemovalArtifacts(
  source: string,
  identity: IdentityCandidate,
): Promise<RemovalArtifacts> {
  if (!identity.bounding_box) {
    return {
      objectImage: "",
      backgroundImage: "",
      accepted: false,
      issues: ["missing bounding_box on selected removable identity"],
    };
  }
  const frame = await buildImageValidationFrame(source);
  const projected = normalizeBboxToPixels(identity.bounding_box, frame.width, frame.height);
  if (!projected) {
    return {
      objectImage: "",
      backgroundImage: "",
      accepted: false,
      issues: ["invalid removable bounding_box projection"],
    };
  }
  const objectCanvas = window.document.createElement("canvas");
  objectCanvas.width = frame.width;
  objectCanvas.height = frame.height;
  const objectContext = objectCanvas.getContext("2d");
  const backgroundCanvas = window.document.createElement("canvas");
  backgroundCanvas.width = frame.width;
  backgroundCanvas.height = frame.height;
  const backgroundContext = backgroundCanvas.getContext("2d");
  if (!objectContext || !backgroundContext) {
    return {
      objectImage: "",
      backgroundImage: "",
      accepted: false,
      issues: ["could not create canvas contexts for removal artifacts"],
    };
  }
  const originalData = new ImageData(new Uint8ClampedArray(frame.rgba), frame.width, frame.height);
  const objectData = new ImageData(frame.width, frame.height);
  const backgroundData = new ImageData(new Uint8ClampedArray(frame.rgba), frame.width, frame.height);
  const fill = dominantBorderColor(frame, projected.left, projected.top, projected.width, projected.height);
  let changedInside = 0;
  let insideTotal = 0;
  let changedOutside = 0;
  let outsideTotal = 0;
  let objectVisible = 0;
  for (let y = 0; y < frame.height; y += 1) {
    for (let x = 0; x < frame.width; x += 1) {
      const index = (y * frame.width + x) * 4;
      const inside = x >= projected.left
        && y >= projected.top
        && x < projected.left + projected.width
        && y < projected.top + projected.height;
      if (inside) {
        insideTotal += 1;
        objectData.data[index] = frame.rgba[index];
        objectData.data[index + 1] = frame.rgba[index + 1];
        objectData.data[index + 2] = frame.rgba[index + 2];
        objectData.data[index + 3] = frame.rgba[index + 3];
        if (frame.rgba[index + 3] > 0) objectVisible += 1;
        backgroundData.data[index] = fill[0];
        backgroundData.data[index + 1] = fill[1];
        backgroundData.data[index + 2] = fill[2];
        backgroundData.data[index + 3] = fill[3];
        if (backgroundData.data[index] !== frame.rgba[index]
          || backgroundData.data[index + 1] !== frame.rgba[index + 1]
          || backgroundData.data[index + 2] !== frame.rgba[index + 2]
          || backgroundData.data[index + 3] !== frame.rgba[index + 3]) {
          changedInside += 1;
        }
      } else {
        outsideTotal += 1;
        objectData.data[index] = 0;
        objectData.data[index + 1] = 0;
        objectData.data[index + 2] = 0;
        objectData.data[index + 3] = 0;
        if (backgroundData.data[index] !== frame.rgba[index]
          || backgroundData.data[index + 1] !== frame.rgba[index + 1]
          || backgroundData.data[index + 2] !== frame.rgba[index + 2]
          || backgroundData.data[index + 3] !== frame.rgba[index + 3]) {
          changedOutside += 1;
        }
      }
    }
  }
  objectContext.putImageData(objectData, 0, 0);
  backgroundContext.putImageData(backgroundData, 0, 0);
  const insideRatio = insideTotal > 0 ? changedInside / insideTotal : 0;
  const outsideRatio = outsideTotal > 0 ? changedOutside / outsideTotal : 0;
  const visibilityRatio = insideTotal > 0 ? objectVisible / insideTotal : 0;
  const issues: string[] = [];
  if (insideRatio < 0.12) issues.push(`inside change ratio too low (${insideRatio.toFixed(3)})`);
  if (outsideRatio > 0.01) issues.push(`outside change ratio too high (${outsideRatio.toFixed(3)})`);
  if (visibilityRatio < 0.03) issues.push(`object visibility ratio too low (${visibilityRatio.toFixed(3)})`);
  return {
    objectImage: objectCanvas.toDataURL("image/png"),
    backgroundImage: backgroundCanvas.toDataURL("image/png"),
    accepted: issues.length === 0,
    issues,
  };
}

function identityIdSet(payload: ParsedPrologPayload | null | undefined): Set<string> {
  return new Set(asIdentityCandidates(payload).map((item) => item.id));
}

async function createIdentityOverlay(source: string, identities: IdentityCandidate[]): Promise<string> {
  const image = await loadImage(source);
  const canvas = window.document.createElement("canvas");
  canvas.width = image.naturalWidth;
  canvas.height = image.naturalHeight;
  const context = canvas.getContext("2d");
  if (!context) throw new Error("This browser could not prepare the debug overlay image.");
  context.drawImage(image, 0, 0);
  const boxes = identities.filter((item) => item.bounding_box);
  const fontPx = Math.max(10, Math.round(Math.min(image.naturalWidth, image.naturalHeight) / 35));
  context.imageSmoothingEnabled = false;
  context.lineWidth = Math.max(1.5, Math.round(Math.min(image.naturalWidth, image.naturalHeight) / 220));
  context.strokeStyle = "#ff4fd8";
  context.fillStyle = "#ff4fd8";
  context.font = `${fontPx}px ui-monospace, monospace`;
  for (const identity of boxes) {
    const [x, y, width, height] = identity.bounding_box || [0, 0, 0, 0];
    const projected = normalizeBboxToPixels([x, y, width, height], image.naturalWidth, image.naturalHeight);
    if (!projected) continue;
    const left = projected.left;
    const top = projected.top;
    const rectWidth = projected.width;
    const rectHeight = projected.height;
    context.strokeRect(left, top, rectWidth, rectHeight);
    const label = identity.id;
    const textWidth = context.measureText(label).width;
    const labelX = Math.max(0, Math.min(canvas.width - Math.ceil(textWidth) - 8, left));
    const labelY = Math.max(fontPx + 6, top - 4);
    context.fillRect(labelX - 3, labelY - fontPx - 3, Math.ceil(textWidth) + 6, fontPx + 4);
    context.fillStyle = "#08131a";
    context.fillText(label, labelX, labelY - 2);
    context.fillStyle = "#ff4fd8";
  }
  return canvas.toDataURL("image/png");
}

async function triSheet(
  before: { label: string; source: string },
  after: { label: string; source: string },
  overlay: { label: string; source: string },
): Promise<string> {
  const [left, middle, right] = await Promise.all([
    loadImage(before.source),
    loadImage(after.source),
    loadImage(overlay.source),
  ]);
  const canvas = window.document.createElement("canvas");
  canvas.width = 1536;
  canvas.height = 560;
  const context = canvas.getContext("2d");
  if (!context) throw new Error("This browser could not prepare the three-image sheet.");
  context.fillStyle = "#061118";
  context.fillRect(0, 0, canvas.width, canvas.height);
  context.fillStyle = "#4ee8dc";
  context.font = "18px ui-monospace, monospace";
  const drawCell = (image: HTMLImageElement, x: number, label: string) => {
    const frameTop = 34;
    const frameWidth = 492;
    const frameHeight = 512;
    const scale = Math.min(frameWidth / image.naturalWidth, frameHeight / image.naturalHeight);
    const width = Math.max(1, Math.round(image.naturalWidth * scale));
    const height = Math.max(1, Math.round(image.naturalHeight * scale));
    context.fillText(label, x + 8, 22);
    context.imageSmoothingEnabled = false;
    context.drawImage(image, x + Math.floor((frameWidth - width) / 2), frameTop + Math.floor((frameHeight - height) / 2), width, height);
  };
  drawCell(left, 12, `1. ${before.label}`);
  drawCell(middle, 520, `2. ${after.label}`);
  drawCell(right, 1028, `3. ${overlay.label}`);
  return canvas.toDataURL("image/png");
}

function mergeIdentityList(primary: unknown[], secondary: unknown[]): unknown[] {
  const map = new Map<string, unknown>();
  const push = (item: unknown) => {
    if (!item || typeof item !== "object") return;
    const record = item as Record<string, unknown>;
    const id = String(record.id || "").trim();
    if (!id) return;
    map.set(id, item);
  };
  secondary.forEach(push);
  primary.forEach(push);
  return Array.from(map.values());
}

function normalizeParsedPayload(payload: ParsedPrologPayload, previous?: ParsedPrologPayload | null): ParsedPrologPayload {
  const normalized = { ...payload };
  const priorCurrent = Array.isArray(previous?.current_identities)
    ? previous.current_identities
    : [];
  const priorHypotheses = Array.isArray(previous?.current_hypotheses)
    ? previous.current_hypotheses
    : Array.isArray(previous?.currnet_hypotheses)
      ? previous.currnet_hypotheses
    : [];
  const current = Array.isArray(normalized.current_identities)
    ? normalized.current_identities
    : [];
  const initial = Array.isArray(normalized.initial_identities)
    ? normalized.initial_identities
    : [];
  const proposed = Array.isArray(normalized.new_identities)
    ? normalized.new_identities
    : [];
  const hypotheses = Array.isArray(normalized.current_hypotheses)
    ? normalized.current_hypotheses
    : Array.isArray(normalized.currnet_hypotheses)
      ? normalized.currnet_hypotheses
    : [];
  const priorHistory = Array.isArray(previous?.action_history)
    ? previous.action_history
    : [];
  const history = Array.isArray(normalized.action_history)
    ? normalized.action_history
    : [];
  const mergedCurrent = mergeIdentityList(
    mergeIdentityList(
      mergeIdentityList(current, initial),
      proposed,
    ),
    priorCurrent,
  );
  normalized.current_identities = mergedCurrent;
  normalized.current_hypotheses = hypotheses.length ? mergeIdentityList(hypotheses, priorHypotheses) : priorHypotheses;
  normalized.action_history = history.length ? [...priorHistory, ...history] : priorHistory;
  delete normalized.currnet_hypotheses;
  delete normalized.initial_identities;
  delete normalized.new_identities;
  return normalized;
}

function tryParseResponse(raw: string): ParsedPrologPayload | null {
  const trimmed = raw.trim();
  if (!trimmed) return null;
  const attempts = [trimmed];
  if (trimmed.startsWith("```")) {
    const stripped = trimmed.replace(/^```[a-zA-Z]*\s*/, "").replace(/\s*```$/, "");
    attempts.push(stripped.trim());
  }
  for (const candidate of attempts) {
    try {
      const parsed = JSON.parse(candidate) as ParsedPrologPayload;
      if (parsed && typeof parsed === "object") return normalizeParsedPayload(parsed);
    } catch {
      // keep trying
    }
  }
  return null;
}

function normalizeExitValue(value: unknown, fallback: PromptExitValue = "next_iteration"): PromptExitValue {
  const normalized = String(value || "").trim().toLowerCase();
  if (normalized === "loop_complete" || normalized === "converged" || normalized === "stop" || normalized === "done" || normalized === "complete") return "loop_complete";
  if (normalized === "next_iteration" || normalized === "continue" || normalized === "next" || normalized === "repair" || normalized === "reject" || normalized === "retry" || normalized === "fix") return "next_iteration";
  if (normalized === "llm_error") return "llm_error";
  if (normalized === "loop_overbudgeted" || normalized === "overbudget" || normalized === "timeout") return "loop_overbudgeted";
  if (normalized === "unran") return "unran";
  return fallback;
}

function tryParseValidatorAssessment(raw: string): ValidatorAssessment | null {
  const trimmed = raw.trim();
  if (!trimmed) return null;
  const attempts = [trimmed];
  if (trimmed.startsWith("```")) {
    const stripped = trimmed.replace(/^```[a-zA-Z]*\s*/, "").replace(/\s*```$/, "");
    attempts.push(stripped.trim());
  }
  for (const candidate of attempts) {
    try {
      const parsed = JSON.parse(candidate) as Record<string, unknown>;
      const approved = parsed.approved === true;
      const issues = Array.isArray(parsed.issues)
        ? parsed.issues.map((item) => String(item || "").trim()).filter(Boolean)
        : [];
      const exitValue = normalizeExitValue(parsed.exit_value, "next_iteration");
      return { approved, issues, exitValue };
    } catch {
      // keep trying
    }
  }
  return null;
}

const PREFERRED_OUTPUT_KEYS = [
  "current_identities",
  "current_hypotheses",
  "action_history",
  "objects_pl",
  "differences_pl",
  "similarities_pl",
  "turtle_from_image_pl",
  "rules_pl",
  "objects_english",
  "differences_english",
  "rules_english",
];

function outputFileName(key: string): string {
  if (key === "current_identities") return "current_identities.json";
  if (key === "current_hypotheses") return "current_hypotheses.json";
  if (key === "action_history") return "action_history.json";
  if (key.endsWith("_pl")) return `${key.slice(0, -3)}.pl`;
  if (key.endsWith("_english")) return `${key.slice(0, -8)}.english`;
  return key;
}

function outputFileRows(parsed: ParsedPrologPayload | null | undefined): Array<{ key: string; label: string; content: string }> {
  if (!parsed || typeof parsed !== "object") return [];
  const record = parsed as unknown as Record<string, unknown>;
  const keys = Object.keys(record);
  if (!keys.length) return [];
  const preferred = PREFERRED_OUTPUT_KEYS.filter((key) => Object.prototype.hasOwnProperty.call(record, key));
  const extras = keys.filter((key) => !PREFERRED_OUTPUT_KEYS.includes(key));
  const ordered = [...preferred, ...extras];
  return ordered.map((key) => {
    const value = record[key];
    return {
      key,
      label: outputFileName(key),
      content: typeof value === "string" ? value : JSON.stringify(value ?? null, null, 2),
    };
  });
}

function canonicalFieldName(value: string): string {
  return value.trim().toUpperCase().replace(/[^A-Z0-9_]+/g, "_").replace(/^_+|_+$/g, "");
}

function parseDataFieldBaseName(baseName: string): { column?: StackKey; field: string; runnerNumber?: number } | null {
  const normalized = canonicalFieldName(baseName);
  if (!normalized) return null;
  const newColumnRunner = /^([ABC])_([0-9]+)_(.+)$/.exec(normalized);
  if (newColumnRunner) {
    return {
      column: newColumnRunner[1] as StackKey,
      runnerNumber: Number.parseInt(newColumnRunner[2], 10),
      field: newColumnRunner[3],
    };
  }
  const newGlobalRunner = /^([0-9]+)_(.+)$/.exec(normalized);
  if (newGlobalRunner) {
    return {
      runnerNumber: Number.parseInt(newGlobalRunner[1], 10),
      field: newGlobalRunner[2],
    };
  }
  const withColumn = /^([ABC])_(.+)$/.exec(normalized);
  if (withColumn) {
    return {
      column: withColumn[1] as StackKey,
      field: withColumn[2],
    };
  }
  // Backward-compat fallback: FIELD_1 or PROMPT1 style.
  const legacyFieldRunner = /^(.+)_([0-9]+)$/.exec(normalized);
  if (legacyFieldRunner) {
    return {
      field: legacyFieldRunner[1],
      runnerNumber: Number.parseInt(legacyFieldRunner[2], 10),
    };
  }
  const legacyPrompt = /^(PROMPT)([0-9]+)$/.exec(normalized);
  if (legacyPrompt) {
    return {
      field: legacyPrompt[1],
      runnerNumber: Number.parseInt(legacyPrompt[2], 10),
    };
  }
  return { field: normalized };
}

function isDataFilePath(path: string): boolean {
  const normalized = path.replace(/\\/g, "/").toLowerCase();
  return normalized.startsWith("data/") || normalized.startsWith("knowledge/data/");
}

function dataFieldFilePath(
  files: WorkspaceFileRecord[],
  stackKey: StackKey,
  fieldName: string,
  runnerNumber?: number,
): string | null {
  const targetField = canonicalFieldName(fieldName);
  const candidates = files
    .filter((file) => isDataFilePath(file.path))
    .map((file) => {
      const base = (file.name || "").replace(/\.[^.]+$/, "");
      const parsed = parseDataFieldBaseName(base);
      return parsed ? { file, parsed } : null;
    })
    .filter((item): item is { file: Props["files"][number]; parsed: { column?: StackKey; field: string; runnerNumber?: number } } => Boolean(item))
    .filter((item) => item.parsed.field === targetField)
    .filter((item) => {
      if (runnerNumber === undefined) return item.parsed.runnerNumber === undefined;
      return item.parsed.runnerNumber === undefined || item.parsed.runnerNumber === runnerNumber;
    })
    .map((item) => {
      const sameColumn = item.parsed.column === stackKey;
      const globalColumn = item.parsed.column === undefined;
      const sameRunner = runnerNumber !== undefined && item.parsed.runnerNumber === runnerNumber;
      const genericRunner = item.parsed.runnerNumber === undefined;
      const rank = runnerNumber === undefined
        ? (sameColumn ? 0 : globalColumn ? 1 : 9)
        : (sameColumn && sameRunner ? 0
          : sameColumn && genericRunner ? 1
            : globalColumn && sameRunner ? 2
              : globalColumn && genericRunner ? 3
                : 9);
      return { ...item, rank };
    })
    .filter((item) => item.rank < 9)
    .sort((left, right) => left.rank - right.rank || (right.file.modified || 0) - (left.file.modified || 0));
  return candidates[0]?.file.path || null;
}

function autoImageFromWorkspaceData(
  workspaceId: string,
  files: WorkspaceFileRecord[],
  stackKey: StackKey,
  slot: "before" | "after",
): ImageSelection | null {
  const preferredField = slot === "before" ? "PARENT_IMAGE" : "CURRENT_IMAGE";
  const legacyField = slot === "before" ? "Image1" : "Image2";
  const path = dataFieldFilePath(files, stackKey, preferredField)
    || dataFieldFilePath(files, stackKey, legacyField);
  if (!path) return null;
  const file = files.find((candidate) => candidate.path === path);
  if (!file || !IMAGE_SUFFIXES.has((file.suffix || "").toLowerCase())) return null;
  return {
    name: file.path,
    dataUrl: workspaceAssetUrl(workspaceId, file.path),
  };
}

async function readWorkspaceTextDataField(
  workspaceId: string,
  files: WorkspaceFileRecord[],
  stackKey: StackKey,
  fieldName: string,
  runnerNumber?: number,
): Promise<string | null> {
  const path = dataFieldFilePath(files, stackKey, fieldName, runnerNumber);
  if (!path) return null;
  const file = files.find((candidate) => candidate.path === path);
  if (!file || !TEXT_SUFFIXES.has((file.suffix || "").toLowerCase())) return null;
  try {
    const response = await fetch(workspaceAssetUrl(workspaceId, file.path), { cache: "no-store" });
    if (!response.ok) return null;
    return await response.text();
  } catch {
    return null;
  }
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
    if (typeof detail === "string") throw new RequestFailure(detail);
    const detailObject = detail && typeof detail === "object" ? detail as Record<string, unknown> : {};
    const message = typeof detailObject.message === "string"
      ? detailObject.message
      : JSON.stringify(detailObject);
    const debugLogPath = typeof detailObject.debugLogPath === "string"
      ? detailObject.debugLogPath
      : undefined;
    throw new RequestFailure(message, debugLogPath);
  }
  return payload;
}

function defaultRunnerPrompt(routeView: string, stackKey: StackKey, runnerIndex: number): string {
  const role = runnerRole(routeView, stackKey, runnerIndex);
  if (role === "extraction") return COMBINED_PROMPT;
  if (role === "removal") return REMOVAL_DISCOVERY_PASS_PROMPT;
  if (role === "regenerated") return REGENERATED_IDENTITIES_PROMPT;
  if (runnerIndex === 0) return COMBINED_PROMPT;
  return [
    `Independent pass for Stack ${runnerDisplayId(routeView, stackKey, runnerIndex)}.`,
    "Do not assume or reuse another stack's output.",
    COMBINED_PROMPT,
  ].join("\n\n");
}

function primaryPromptName(routeView: string, stackKey: StackKey, runnerIndex: number): string {
  const role = runnerRole(routeView, stackKey, runnerIndex);
  if (role === "extraction") return "generate_prolog_and_english";
  if (role === "removal") return "remove_smallest_object";
  if (role === "regenerated") return "regenerated_identities_from_many_objects";
  if (stackKey === "A" && runnerIndex === 0) return "circle_one_identity_at_a_time";
  return `stack_${stackKey.toLowerCase()}${runnerDisplayOrdinal(routeView, stackKey, runnerIndex)}_identity_pass`;
}

function validatorPromptName(routeView: string, stackKey: StackKey, runnerIndex: number): string {
  const role = runnerRole(routeView, stackKey, runnerIndex);
  if (role === "removal") return "no_objects";
  return "no_uncircled_objects";
}

function validatorPromptDisplayName(routeView: string, stackKey: StackKey, runnerIndex: number, name: string): string {
  if (name === VALIDATOR_PROMPT_DISABLED) return "disabled";
  return name || validatorPromptName(routeView, stackKey, runnerIndex);
}

function isRemovalDiscoveryRunner(routeView: string, stackKey: StackKey, runnerIndex: number): boolean {
  return runnerRole(routeView, stackKey, runnerIndex) === "removal";
}

function isRegeneratedIdentitiesRunner(routeView: string, stackKey: StackKey, runnerIndex: number): boolean {
  return runnerRole(routeView, stackKey, runnerIndex) === "regenerated";
}

function manyObjectImagesFromRunner(runner: RunnerState): Array<{ key: string; label: string; value: string }> {
  const images: Array<{ key: string; label: string; value: string }> = [];
  if (runner.removedObjectImage) {
    images.push({ key: "many_objects_1", label: "many_objects_1", value: runner.removedObjectImage });
  }
  if (runner.removedBackgroundImage) {
    images.push({ key: "many_objects_2", label: "many_objects_2", value: runner.removedBackgroundImage });
  }
  if (!images.length && runner.loopImageWithCircles) {
    images.push({ key: "many_objects_1", label: "many_objects_1", value: runner.loopImageWithCircles });
  }
  return images;
}

function migrateRunnerPromptText(routeView: string, stackKey: StackKey, runnerIndex: number, promptText: string): string {
  const trimmed = String(promptText || "").trim();
  const fallback = defaultRunnerPrompt(routeView, stackKey, runnerIndex);
  if (!trimmed) return fallback;
  if (isRemovalDiscoveryRunner(routeView, stackKey, runnerIndex) && trimmed === COMBINED_PROMPT) return REMOVAL_DISCOVERY_PASS_PROMPT;
  if (isRegeneratedIdentitiesRunner(routeView, stackKey, runnerIndex) && trimmed === COMBINED_PROMPT) return REGENERATED_IDENTITIES_PROMPT;
  return promptText;
}

function initialSelectedOutputId(pageDefinition: WorkflowPageDefinition): string {
  return pageDefinition.routeView === "arc3B1B2Pipeline" ? "GUESSER" : "A1";
}

function defaultInputFilesSourceIds(): string[] {
  return ["ALL-Setup1"];
}

function initialRunnerState(routeView: string, stackKey: StackKey, runnerIndex: number, selectedModelId: string, defaultTimeoutSeconds: number): RunnerState {
  const initialFilesSourceIds = defaultInputFilesSourceIdsForRunner(routeView, stackKey, runnerIndex);
  return {
    selectedModelId: selectedModelId || COLUMN_MODEL_SENTINEL,
    validatorModelId: RUNNER_VALIDATOR_PRIMARY_MODEL,
    setupIndex: defaultSetupIndexForRunner(routeView, stackKey, runnerIndex),
    filesSourceSelection: initialFilesSourceIds[0],
    filesSourceIds: initialFilesSourceIds,
    generationSeq: 0,
    promptText: defaultRunnerPrompt(routeView, stackKey, runnerIndex),
    primaryPromptName: primaryPromptName(routeView, stackKey, runnerIndex),
    validatorPromptText: DEFAULT_VALIDATOR_PROMPT,
    validatorPromptName: validatorPromptName(routeView, stackKey, runnerIndex),
    promptMode: "loop",
    autoLoopMaxIterations: AUTO_GAP_MAX_PASSES,
    autoLoopMaxSeconds: defaultTimeoutSeconds,
    maxPrimarySeconds: defaultTimeoutSeconds,
    running: false,
    currentRunMode: "",
    message: "Ready.",
    error: "",
    result: null,
    parsed: null,
    rawResponse: "",
    debugLogPath: "",
    debugLog: "",
    removedIdentityId: "",
    removedObjectImage: "",
    removedBackgroundImage: "",
    loopImageWithCircles: "",
    removalValidationSummary: "",
  };
}

function initialStackColumnState(routeView: string, stackKey: StackKey, columnModelSelection: string, defaultTimeoutSeconds: number): StackColumnState {
  const setups = defaultSetups(stackKey);
  const defaults = setups[0];
  const runnerModelSelection = COLUMN_MODEL_SENTINEL;
  const runnerCount = defaultRunnerCountForRoute(routeView);
  return {
    key: stackKey,
    columnModelSelection,
    desc1: defaultDesc1(),
    desc2: defaultDesc2(),
    beforeImage: defaults.beforeImage,
    afterImage: defaults.afterImage,
    setups,
    runners: Array.from({ length: runnerCount }, (_, index) =>
      initialRunnerState(routeView, stackKey, index, runnerModelSelection, defaultTimeoutSeconds)),
  };
}

function defaultColumnModelSelection(): string {
  return PAGE_MODEL_SENTINEL;
}

function imageFieldLabel(slot: "before" | "after") {
  return slot === "before" ? "PARENT_IMAGE" : "CURRENT_IMAGE";
}

function defaultDesc1() {
  return "MOVE";
}

function defaultDesc2() {
  return "ACTION-UP";
}

export function Arc3B1B2PipelinePage({ pageDefinition, workspaceId, workspaceLabel, models, files, onPageDefinitionSaved }: Props) {
  const activeStackColumns = useMemo(
    () => stackColumnsForRoute(pageDefinition.routeView),
    [pageDefinition.routeView],
  );
  const defaultTimeoutSeconds = useMemo(
    () => defaultTimeoutSecondsForRoute(pageDefinition.routeView),
    [pageDefinition.routeView],
  );
  const enabledModels = useMemo(() => models.filter((model) => model.enabled !== false), [models]);
  const visionModels = useMemo(
    () => enabledModels.filter((model) => {
      const capabilities = normalizedCapabilities(model);
      return capabilities.vision;
    }),
    [enabledModels],
  );
  const preferredModelId = enabledModels.find((model) => /gemma[-_/]4([^0-9]|$)/.test(normalizedModelName(model)))?.id || "";
  const defaultModelId = enabledModels[0]?.id || "";
  const [stackColumns, setStackColumns] = useState<StackColumnState[]>(
    () => activeStackColumns.map((column) => ({
      ...initialStackColumnState(
        pageDefinition.routeView,
        column.key,
        defaultColumnModelSelection(),
        defaultTimeoutSeconds,
      ),
    })),
  );
  const [selectedOutputId, setSelectedOutputId] = useState(() => initialSelectedOutputId(pageDefinition));
  const [outputHistory, setOutputHistory] = useState<OutputHistoryEntry[]>([]);
  const [accordionModes, setAccordionModes] = useState<Record<string, AccordionDisplayMode>>({});
  const [setupAccordionOpen, setSetupAccordionOpen] = useState<Record<StackKey, number>>({
    A: 0,
    B: 0,
    C: 0,
  });
  const [pageModelId, setPageModelId] = useState("");
  const [workspaceRunnerModelId, setWorkspaceRunnerModelId] = useState("");
  const [workbenchRunnerModelId, setWorkbenchRunnerModelId] = useState("");
  const [modelSelectionMessage, setModelSelectionMessage] = useState("");
  const [scanDataBusy, setScanDataBusy] = useState(false);
  const [replaceGuesserOnFinish, setReplaceGuesserOnFinish] = useState(false);
  const [openBrowseKey, setOpenBrowseKey] = useState<string | null>(null);
  const [openEditorKey, setOpenEditorKey] = useState<string | null>(null);
  const [editorText, setEditorText] = useState("");
  const [editorName, setEditorName] = useState("");
  const [editorBusy, setEditorBusy] = useState(false);
  const [editorError, setEditorError] = useState("");
  const [groupOpen, setGroupOpen] = useState<Record<string, boolean>>({});
  const controllersRef = useRef<Record<string, AbortController | null>>({});
  const stackColumnsRef = useRef(stackColumns);
  stackColumnsRef.current = stackColumns;
  const columnsElRef = useRef<HTMLDivElement | null>(null);
  const [columnTemplate, setColumnTemplate] = useState<string | null>(null);
  const [resizerLefts, setResizerLefts] = useState<number[]>([]);
  const [resizerHeight, setResizerHeight] = useState(0);
  useLayoutEffect(() => {
    const el = columnsElRef.current;
    if (!el) return;
    const measure = () => {
      const columnEls = Array.from(el.children).filter(
        (child): child is HTMLElement => child instanceof HTMLElement && child.classList.contains("english-workflow-column"),
      );
      if (columnEls.length < 2) {
        setResizerLefts([]);
        return;
      }
      const gap = parseFloat(getComputedStyle(el).columnGap || "0") || 0;
      const lefts: number[] = [];
      for (let index = 0; index < columnEls.length - 1; index += 1) {
        lefts.push(columnEls[index].offsetLeft + columnEls[index].offsetWidth + gap / 2);
      }
      setResizerLefts(lefts);
      setResizerHeight(el.scrollHeight);
    };
    measure();
    const observer = new ResizeObserver(measure);
    observer.observe(el);
    window.addEventListener("resize", measure);
    return () => {
      observer.disconnect();
      window.removeEventListener("resize", measure);
    };
  }, [columnTemplate, stackColumns]);
  const startColumnResize = (index: number, event: { clientX: number; preventDefault: () => void }) => {
    event.preventDefault();
    const el = columnsElRef.current;
    if (!el) return;
    const columnEls = Array.from(el.children).filter(
      (child): child is HTMLElement => child instanceof HTMLElement && child.classList.contains("english-workflow-column"),
    );
    if (columnEls.length < 2 || index >= columnEls.length - 1) return;
    const widths = columnEls.map((column) => column.getBoundingClientRect().width);
    const startX = event.clientX;
    const minWidth = 220;
    const leftWidth = widths[index];
    const rightWidth = widths[index + 1];
    const onMove = (moveEvent: PointerEvent) => {
      let delta = moveEvent.clientX - startX;
      delta = Math.max(-(leftWidth - minWidth), Math.min(rightWidth - minWidth, delta));
      const next = widths.map((width, position) => {
        if (position === index) return leftWidth + delta;
        if (position === index + 1) return rightWidth - delta;
        return width;
      });
      setColumnTemplate(next.map((width) => `${Math.round(width)}px`).join(" "));
    };
    const onUp = () => {
      document.removeEventListener("pointermove", onMove);
      document.removeEventListener("pointerup", onUp);
      document.body.style.cursor = "";
      document.body.style.userSelect = "";
    };
    document.body.style.cursor = "col-resize";
    document.body.style.userSelect = "none";
    document.addEventListener("pointermove", onMove);
    document.addEventListener("pointerup", onUp);
  };
  const generationSeqRef = useRef(0);
  const anyRunning = stackColumns.some((stack) => stack.runners.some((runner) => runner.running));
  useEffect(() => {
    const nextKeys = activeStackColumns.map((column) => column.key).join(",");
    const currentKeys = stackColumns.map((column) => column.key).join(",");
    if (nextKeys === currentKeys) return;
    setStackColumns(
      activeStackColumns.map((column) => ({
        ...initialStackColumnState(
          pageDefinition.routeView,
          column.key,
          defaultColumnModelSelection(),
          defaultTimeoutSeconds,
        ),
      })),
    );
  }, [activeStackColumns, stackColumns, defaultTimeoutSeconds, pageDefinition.routeView]);

  const isEnabledModel = (modelId: string) => enabledModels.some((model) => model.id === modelId);
  const resolveWorkspaceRunnerModelId = () => {
    if (workspaceRunnerModelId && isEnabledModel(workspaceRunnerModelId)) return workspaceRunnerModelId;
    return defaultModelId;
  };
  const resolveWorkbenchRunnerModelId = () => {
    if (workbenchRunnerModelId && isEnabledModel(workbenchRunnerModelId)) return workbenchRunnerModelId;
    return resolveWorkspaceRunnerModelId() || defaultModelId;
  };
  const resolvePageModelId = () => {
    if (pageModelId === RUNNER_WORKSPACE_MODEL_SENTINEL) return resolveWorkspaceRunnerModelId();
    if (pageModelId === RUNNER_WORKBENCH_MODEL_SENTINEL) return resolveWorkbenchRunnerModelId();
    if (pageModelId && isEnabledModel(pageModelId)) return pageModelId;
    return resolveWorkspaceRunnerModelId();
  };
  const resolveColumnModelId = (stack: StackColumnState): string => {
    const candidate = stack.columnModelSelection === PAGE_MODEL_SENTINEL
      ? resolvePageModelId()
      : stack.columnModelSelection;
    return isEnabledModel(candidate) ? candidate : resolvePageModelId();
  };
  const isRunnerModelSentinel = (value: string) => value === COLUMN_MODEL_SENTINEL
    || value === RUNNER_WORKSPACE_MODEL_SENTINEL
    || value === RUNNER_WORKBENCH_MODEL_SENTINEL;
  const resolveRunnerModelId = (stack: StackColumnState, runner: RunnerState): string => {
    if (runner.selectedModelId === COLUMN_MODEL_SENTINEL) return resolveColumnModelId(stack);
    if (runner.selectedModelId === RUNNER_WORKSPACE_MODEL_SENTINEL) return resolveWorkspaceRunnerModelId();
    if (runner.selectedModelId === RUNNER_WORKBENCH_MODEL_SENTINEL) return resolveWorkbenchRunnerModelId();
    return isEnabledModel(runner.selectedModelId)
      ? runner.selectedModelId
      : resolveColumnModelId(stack);
  };
  const resolveValidatorModelId = (stack: StackColumnState, runner: RunnerState): string => {
    if (runner.validatorModelId === RUNNER_VALIDATOR_DISABLED) return "";
    if (runner.validatorModelId === RUNNER_VALIDATOR_PRIMARY_MODEL) return resolveRunnerModelId(stack, runner);
    if (runner.validatorModelId === COLUMN_MODEL_SENTINEL) return resolveColumnModelId(stack);
    if (runner.validatorModelId === RUNNER_WORKSPACE_MODEL_SENTINEL) return resolveWorkspaceRunnerModelId();
    if (runner.validatorModelId === RUNNER_WORKBENCH_MODEL_SENTINEL) return resolveWorkbenchRunnerModelId();
    return isEnabledModel(runner.validatorModelId)
      ? runner.validatorModelId
      : resolveRunnerModelId(stack, runner);
  };

  useEffect(() => {
    setPageModelId(preferredModelId || defaultModelId);
    setWorkspaceRunnerModelId(defaultModelId);
    setWorkbenchRunnerModelId(defaultModelId);
    if (!workspaceId) return;
    let canceled = false;
    const loadModelSelection = async () => {
      try {
        const payload = await request(`/workspaces/${encodeURIComponent(workspaceId)}/model-selection`);
        const document = (payload.document || {}) as Record<string, unknown>;
        const system = (payload.system || {}) as Record<string, unknown>;
        const workspaceChoice = String(document.overrideModelId || "").trim();
        const workbenchChoice = String(system.fallbackModelId || "").trim();
        const resolvedWorkspace = preferredModelId
          || (isEnabledModel(workspaceChoice) ? workspaceChoice : defaultModelId);
        const resolvedWorkbench = isEnabledModel(workbenchChoice) ? workbenchChoice : resolvedWorkspace;
        if (!canceled) {
          setPageModelId(resolvedWorkspace);
          setWorkspaceRunnerModelId(resolvedWorkspace);
          setWorkbenchRunnerModelId(resolvedWorkbench);
          setModelSelectionMessage("");
        }
      } catch (reason) {
        if (!canceled) {
          setPageModelId(preferredModelId || defaultModelId);
          setWorkspaceRunnerModelId(defaultModelId);
          setWorkbenchRunnerModelId(defaultModelId);
          setModelSelectionMessage(`Model policy defaults unavailable: ${reason instanceof Error ? reason.message : String(reason)}`);
        }
      }
    };
    void loadModelSelection();
    return () => {
      canceled = true;
    };
  }, [workspaceId, defaultModelId, enabledModels]);

  useEffect(() => {
    setStackColumns((previous) => previous.map((stack) => {
      const defaults = defaultSetups(stack.key)[0];
      const stackASetups = shouldUseDescendSetups(pageDefinition.routeView, stack.key)
        ? stackADescendSetupsFromFiles(workspaceId, files)
        : [];
      const normalizedSetups = stackASetups.length
        ? stackASetups
        : (stack.setups?.length ? stack.setups : defaultSetups(stack.key));
      const routeRunnerCount = isB1B2PipelineRoute(pageDefinition.routeView)
        ? defaultRunnerCountForRoute(pageDefinition.routeView)
        : null;
      const normalizedRunners = (() => {
        if (routeRunnerCount === null) return stack.runners;
        const trimmed = stack.runners.slice(0, routeRunnerCount);
        if (trimmed.length >= routeRunnerCount) return trimmed;
        return [
          ...trimmed,
          ...Array.from(
            { length: routeRunnerCount - trimmed.length },
            (_, offset) =>
              initialRunnerState(
                pageDefinition.routeView,
                stack.key,
                trimmed.length + offset,
                COLUMN_MODEL_SENTINEL,
                defaultTimeoutSeconds,
              ),
          ),
        ];
      })();
      const autoBefore = autoImageFromWorkspaceData(workspaceId, files, stack.key, "before");
      const autoAfter = autoImageFromWorkspaceData(workspaceId, files, stack.key, "after");
      const fallbackColumnModelSelection = defaultColumnModelSelection();
      const normalizedColumnModelSelection = stack.columnModelSelection === PAGE_MODEL_SENTINEL
        || enabledModels.some((model) => model.id === stack.columnModelSelection)
        ? stack.columnModelSelection
        : fallbackColumnModelSelection;
      return {
        ...stack,
        columnModelSelection: normalizedColumnModelSelection,
        desc1: stack.desc1 || defaultDesc1(),
        desc2: stack.desc2 || defaultDesc2(),
        beforeImage: autoBefore || normalizedSetups[0]?.beforeImage || defaults.beforeImage,
        afterImage: autoAfter || normalizedSetups[0]?.afterImage || defaults.afterImage,
        setups: normalizedSetups,
        runners: normalizedRunners.map((runner, runnerIndex) => ({
          ...runner,
          selectedModelId: isRunnerModelSentinel(runner.selectedModelId)
            || isEnabledModel(runner.selectedModelId)
            ? runner.selectedModelId
            : COLUMN_MODEL_SENTINEL,
          validatorModelId: runner.validatorModelId === RUNNER_VALIDATOR_DISABLED
            || runner.validatorModelId === RUNNER_VALIDATOR_PRIMARY_MODEL
            || isRunnerModelSentinel(runner.validatorModelId)
            || isEnabledModel(runner.validatorModelId)
            ? runner.validatorModelId
            : RUNNER_VALIDATOR_PRIMARY_MODEL,
          filesSourceIds: runner.filesSourceIds?.length
            ? runner.filesSourceIds.filter((sourceId) => !isGeneratedToken(sourceId))
            : defaultInputFilesSourceIdsForRunner(pageDefinition.routeView, stack.key, runnerIndex),
          filesSourceSelection: runner.filesSourceSelection
            || runner.filesSourceIds?.[0]
            || defaultInputFilesSourceIdsForRunner(pageDefinition.routeView, stack.key, runnerIndex)[0],
          promptText: migrateRunnerPromptText(pageDefinition.routeView, stack.key, runnerIndex, runner.promptText),
          primaryPromptName: String((runner as unknown as Record<string, unknown>).primaryPromptName || "").trim() || primaryPromptName(pageDefinition.routeView, stack.key, runnerIndex),
          validatorPromptText: runner.validatorPromptText || DEFAULT_VALIDATOR_PROMPT,
          validatorPromptName: String((runner as unknown as Record<string, unknown>).validatorPromptName || "").trim() || validatorPromptName(pageDefinition.routeView, stack.key, runnerIndex),
          promptMode: String((runner as unknown as Record<string, unknown>).promptMode || "").trim() === "validator" ? "validator" : "loop",
          autoLoopMaxIterations: Number.isFinite(runner.autoLoopMaxIterations) && runner.autoLoopMaxIterations > 0
            ? Math.max(1, Math.floor(runner.autoLoopMaxIterations))
            : AUTO_GAP_MAX_PASSES,
          autoLoopMaxSeconds: Number.isFinite(runner.autoLoopMaxSeconds) && runner.autoLoopMaxSeconds > 0
            ? Math.max(10, Math.floor(runner.autoLoopMaxSeconds))
            : defaultTimeoutSeconds,
          maxPrimarySeconds: Number.isFinite((runner as unknown as Record<string, unknown>).maxPrimarySeconds as number) && (runner as unknown as Record<string, unknown>).maxPrimarySeconds as number > 0
            ? Math.max(10, Math.floor(Number((runner as unknown as Record<string, unknown>).maxPrimarySeconds)))
            : defaultTimeoutSeconds,
          setupIndex: Math.max(
            0,
            Math.min(
              isB1B2PipelineRoute(pageDefinition.routeView)
                ? defaultSetupIndexForRunner(pageDefinition.routeView, stack.key, runnerIndex)
                : (runner.setupIndex || 0),
              Math.max(0, normalizedSetups.length - 1),
            ),
          ),
          running: false,
          currentRunMode: "",
          message: "Ready.",
          error: "",
        })),
      };
    }));
    Object.values(controllersRef.current).forEach((controller) => controller?.abort());
    controllersRef.current = {};
    generationSeqRef.current = 0;
    setOutputHistory([]);
  }, [workspaceId, defaultModelId, enabledModels, files, activeStackColumns, defaultTimeoutSeconds, pageDefinition.routeView]);

  useEffect(() => {
    if (!workspaceId) return;
    let canceled = false;
    const loadColumnTextFields = async () => {
      const updates = await Promise.all(activeStackColumns.map(async (column) => ({
        key: column.key,
        generated: await readWorkspaceTextDataField(workspaceId, files, column.key, "Generated"),
        command: await readWorkspaceTextDataField(workspaceId, files, column.key, "Command"),
        prompts: await Promise.all(
          Array.from({ length: 12 }, (_, index) =>
            readWorkspaceTextDataField(workspaceId, files, column.key, "Prompt", index + 1),
          ),
        ),
      })));
      if (canceled) return;
      if (!updates.some((item) => item.generated !== null || item.command !== null || item.prompts.some((value) => value !== null))) return;
      setStackColumns((previous) => previous.map((stack) => {
        const update = updates.find((candidate) => candidate.key === stack.key);
        if (!update) return stack;
        return {
          ...stack,
          desc1: update.generated ?? stack.desc1,
          desc2: update.command ?? stack.desc2,
          runners: stack.runners.map((runner, index) => ({
            ...runner,
            promptText: update.prompts[index] ?? runner.promptText,
          })),
        };
      }));
    };
    void loadColumnTextFields();
    return () => {
      canceled = true;
    };
  }, [workspaceId, files]);

  useEffect(() => () => {
    Object.values(controllersRef.current).forEach((controller) => controller?.abort());
  }, []);

  const setStackState = (stackIndex: number, updater: (stack: StackColumnState) => StackColumnState) => {
    setStackColumns((previous) => previous.map((stack, index) => (
      index === stackIndex ? updater(stack) : stack
    )));
  };

  const setRunnerState = (stackIndex: number, runnerIndex: number, updater: (runner: RunnerState) => RunnerState) => {
    setStackState(stackIndex, (stack) => ({
      ...stack,
      runners: stack.runners.map((runner, index) => (
        index === runnerIndex ? updater(runner) : runner
      )),
    }));
  };

  const incrementRunnerSetup = (stackIndex: number, runnerIndex: number) => {
    setStackState(stackIndex, (stack) => {
      const setups = stack.setups?.length ? stack.setups : defaultSetups(stack.key);
      const lastIndex = Math.max(0, setups.length - 1);
      return {
        ...stack,
        runners: stack.runners.map((runner, index) => {
          if (index !== runnerIndex) return runner;
          const current = Math.max(0, Math.min(runner.setupIndex || 0, lastIndex));
          return {
            ...runner,
            setupIndex: Math.min(lastIndex, current + 1),
          };
        }),
      };
    });
  };

  const selectImage = (stackIndex: number, imageIndex: number) => {
    const currentStack = stackColumns[stackIndex];
    const currentSetups = currentStack?.setups?.length
      ? currentStack.setups
      : (currentStack ? defaultSetups(currentStack.key) : []);
    const selectedClamped = Math.max(0, Math.min(imageIndex, Math.max(0, currentSetups.length - 1)));
    const setupModeKeys = currentSetups.map((setup) => `image-${setup.id}`);
    const selectedModeKey = currentSetups[selectedClamped] ? `image-${currentSetups[selectedClamped].id}` : null;

    setStackState(stackIndex, (stack) => {
      const setups = stack.setups?.length ? stack.setups : defaultSetups(stack.key);
      const clamped = Math.max(0, Math.min(imageIndex, Math.max(0, setups.length - 1)));
      return {
        ...stack,
        selectedImageIndex: clamped,
        runners: stack.runners.map((runner) => ({ ...runner, setupIndex: clamped })),
      };
    });

    // Switching setups collapses every image in column 1 to a strip and expands
    // only the newly selected setup, then scrolls it into view.
    if (setupModeKeys.length) {
      setAccordionModes((current) => {
        const next = { ...current };
        for (const key of setupModeKeys) next[key] = "strip";
        if (selectedModeKey) next[selectedModeKey] = "full";
        return next;
      });
    }
    if (selectedModeKey && typeof window !== "undefined") {
      const targetKey = selectedModeKey;
      window.requestAnimationFrame(() => window.requestAnimationFrame(() => {
        const escaped = typeof CSS !== "undefined" && CSS.escape ? CSS.escape(targetKey) : targetKey;
        const memberEl = document.querySelector(`[data-accordion-member="${escaped}"]`);
        if (memberEl && typeof memberEl.scrollIntoView === "function") {
          memberEl.scrollIntoView({ behavior: "smooth", block: "nearest" });
        }
      }));
    }
  };

  const setImagePath = (stackIndex: number, imageIndex: number, path: string) => {
    setStackState(stackIndex, (stack) => {
      const setups = stack.setups?.length ? [...stack.setups] : defaultSetups(stack.key);
      const current = setups[imageIndex];
      if (!current) return stack;
      const nextImage = imageSelectionFromPath(workspaceId, path, current.afterImage);
      setups[imageIndex] = {
        ...current,
        afterImage: nextImage,
        command: setupCommandFromPath(nextImage.name) || current.command,
      };
      const active = stack.selectedImageIndex ?? 0;
      return {
        ...stack,
        setups,
        afterImage: imageIndex === active ? nextImage : stack.afterImage,
      };
    });
  };

  const setBeforeImagePath = (stackIndex: number, imageIndex: number, path: string) => {
    setStackState(stackIndex, (stack) => {
      const setups = stack.setups?.length ? [...stack.setups] : defaultSetups(stack.key);
      const current = setups[imageIndex];
      if (!current) return stack;
      const nextImage = path.trim()
        ? imageSelectionFromPath(workspaceId, path, current.beforeImage || undefined)
        : null;
      setups[imageIndex] = { ...current, beforeImage: nextImage };
      const active = stack.selectedImageIndex ?? 0;
      return {
        ...stack,
        setups,
        beforeImage: imageIndex === active ? nextImage : stack.beforeImage,
      };
    });
  };

  const setSetupCommand = (stackIndex: number, imageIndex: number, command: string) => {
    setStackState(stackIndex, (stack) => {
      const setups = stack.setups?.length ? [...stack.setups] : defaultSetups(stack.key);
      const current = setups[imageIndex];
      if (!current) return stack;
      setups[imageIndex] = { ...current, command };
      return { ...stack, setups };
    });
  };

  const appendSetupEntryPath = (stackIndex: number, imageIndex: number, field: SetupCollectionField, path: string) => {
    const trimmed = path.trim();
    if (!trimmed) return;
    setStackState(stackIndex, (stack) => {
      const setups = stack.setups?.length ? [...stack.setups] : defaultSetups(stack.key);
      const current = setups[imageIndex];
      if (!current) return stack;
      const entries = [...(current[field] || []), imageSelectionFromPath(workspaceId, trimmed, { name: "", dataUrl: "" })];
      setups[imageIndex] = { ...current, [field]: entries };
      return { ...stack, setups };
    });
  };

  const setSetupEntryPath = (stackIndex: number, imageIndex: number, field: SetupCollectionField, entryIndex: number, path: string) => {
    setStackState(stackIndex, (stack) => {
      const setups = stack.setups?.length ? [...stack.setups] : defaultSetups(stack.key);
      const current = setups[imageIndex];
      if (!current) return stack;
      const entries = [...(current[field] || [])];
      const existing = entries[entryIndex];
      if (!existing) return stack;
      entries[entryIndex] = path.trim()
        ? imageSelectionFromPath(workspaceId, path, existing)
        : { name: "", dataUrl: "" };
      setups[imageIndex] = { ...current, [field]: entries };
      return { ...stack, setups };
    });
  };

  const removeSetupEntry = (stackIndex: number, imageIndex: number, field: SetupCollectionField, entryIndex: number) => {
    setStackState(stackIndex, (stack) => {
      const setups = stack.setups?.length ? [...stack.setups] : defaultSetups(stack.key);
      const current = setups[imageIndex];
      if (!current) return stack;
      const entries = (current[field] || []).filter((_, index) => index !== entryIndex);
      setups[imageIndex] = { ...current, [field]: entries };
      return { ...stack, setups };
    });
  };

  const setSetupStateField = (stackIndex: number, imageIndex: number, field: "stateDir" | "stateFile" | "stateJson", value: string) => {
    setStackState(stackIndex, (stack) => {
      const setups = stack.setups?.length ? [...stack.setups] : defaultSetups(stack.key);
      const current = setups[imageIndex];
      if (!current) return stack;
      setups[imageIndex] = { ...current, [field]: value };
      return { ...stack, setups };
    });
  };

  const loadSetupStateJson = async (stackIndex: number, imageIndex: number, dir: string, fileName: string) => {
    const cleanDir = normalizeAssetPath(dir).replace(/\/+$/, "");
    const cleanFile = normalizeAssetPath(fileName).replace(/^\/+/, "");
    const rel = cleanDir ? `${cleanDir}/${cleanFile}` : cleanFile;
    if (!cleanFile) return;
    try {
      const response = await fetch(workspaceAssetUrl(workspaceId, rel), { cache: "no-store" });
      if (!response.ok) {
        setSetupStateField(stackIndex, imageIndex, "stateJson", `// Could not load ${rel} (${response.status})`);
        return;
      }
      setSetupStateField(stackIndex, imageIndex, "stateJson", await response.text());
    } catch (reason) {
      setSetupStateField(stackIndex, imageIndex, "stateJson", `// Could not load ${rel}: ${reason instanceof Error ? reason.message : String(reason)}`);
    }
  };

  const saveSetupStateJson = async (fileName: string, content: string) => {
    const suggested = (normalizeAssetPath(fileName).split("/").pop() || "state.json") || "state.json";
    const picker = (window as unknown as {
      showSaveFilePicker?: (options: {
        suggestedName?: string;
        types?: Array<{ description?: string; accept: Record<string, string[]> }>;
      }) => Promise<{ createWritable: () => Promise<{ write: (data: string) => Promise<void>; close: () => Promise<void> }> }>;
    }).showSaveFilePicker;
    if (typeof picker === "function") {
      try {
        const handle = await picker({
          suggestedName: suggested,
          types: [{ description: "JSON", accept: { "application/json": [".json"] } }],
        });
        const writable = await handle.createWritable();
        await writable.write(content);
        await writable.close();
        return;
      } catch (reason) {
        if (reason instanceof DOMException && reason.name === "AbortError") return;
      }
    }
    const blob = new Blob([content], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = suggested;
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    URL.revokeObjectURL(url);
  };

  const downloadTextFallback = (fileName: string, content: string) => {
    const suggested = (normalizeAssetPath(fileName).split("/").pop() || "file.txt") || "file.txt";
    const blob = new Blob([content], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = suggested;
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    URL.revokeObjectURL(url);
  };

  const saveTextFileAs = async (fileName: string, content: string) => {
    const suggested = (normalizeAssetPath(fileName).split("/").pop() || "file.txt") || "file.txt";
    const picker = (window as unknown as {
      showSaveFilePicker?: (options: { suggestedName?: string }) => Promise<{
        createWritable: () => Promise<{ write: (data: string) => Promise<void>; close: () => Promise<void> }>;
      }>;
    }).showSaveFilePicker;
    if (typeof picker === "function") {
      try {
        const handle = await picker({ suggestedName: suggested });
        const writable = await handle.createWritable();
        await writable.write(content);
        await writable.close();
        return;
      } catch (reason) {
        if (reason instanceof DOMException && reason.name === "AbortError") return;
      }
    }
    downloadTextFallback(suggested, content);
  };

  const saveEntryFileAs = async (path: string) => {
    const rel = normalizeAssetPath(path).replace(/^\/+/, "");
    if (!rel) return;
    let content = "";
    if (workspaceId) {
      try {
        const response = await fetch(workspaceAssetUrl(workspaceId, rel), { cache: "no-store" });
        if (response.ok) content = await response.text();
      } catch {
        // Save whatever we could read (possibly empty) rather than blocking.
      }
    }
    await saveTextFileAs(rel, content);
  };

  const saveDataFile = async (path: string, content: string): Promise<boolean> => {
    const clean = normalizeAssetPath(path).replace(/^\/+/, "");
    if (!clean) {
      setEditorError("A file path is required.");
      return false;
    }
    if (!workspaceId) {
      setEditorError("No workspace is loaded; downloaded a local copy instead.");
      downloadTextFallback(clean, content);
      return false;
    }
    try {
      await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/data-file`, {
        method: "PUT",
        body: JSON.stringify({ path: clean, content }),
      });
      setEditorError("");
      return true;
    } catch (reason) {
      // The server refuses suffixes outside DATA_FILE_SUFFIXES (and may be offline);
      // fall back to a client-side download so the edit is never lost.
      setEditorError(`${reason instanceof Error ? reason.message : String(reason)} — downloaded a local copy instead.`);
      downloadTextFallback(clean, content);
      return false;
    }
  };

  const scanSetupStatePath = async (stackIndex: number, imageIndex: number, fallbackDir: string) => {
    // Read the PATH from the latest committed state (via ref) so a scan performed
    // immediately after editing PATH uses the new value, not a stale render's closure.
    const liveSetup = stackColumnsRef.current?.[stackIndex]?.setups?.[imageIndex];
    const prefix = normalizeAssetPath(liveSetup?.stateDir ?? fallbackDir).replace(/\/+$/, "");
    let records: WorkspaceFileRecord[] = files;
    if (workspaceId) {
      try {
        const payload = await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/data/files`);
        const listed = Array.isArray(payload.files) ? payload.files : [];
        const valid = listed.filter((item): item is WorkspaceFileRecord => Boolean(item)
          && typeof (item as Record<string, unknown>).path === "string"
          && typeof (item as Record<string, unknown>).name === "string"
          && typeof (item as Record<string, unknown>).suffix === "string"
          && typeof (item as Record<string, unknown>).modified === "number");
        if (valid.length) records = valid;
      } catch {
        // Fall back to the files prop when the data listing endpoint is unavailable.
      }
    }
    const scoped = records.filter((file) => {
      const candidate = normalizeAssetPath(file.path);
      if (!prefix) return !candidate.includes("/");
      if (!candidate.startsWith(`${prefix}/`)) return false;
      return !candidate.slice(prefix.length + 1).includes("/");
    });
    const results: Record<string, string[]> = {
      obj_images: [],
      grp_images: [],
      sub_images: [],
      pl_files: [],
      eng_files: [],
      json_files: [],
      metta_files: [],
      prompt_files: [],
      unknown_files: [],
    };
    for (const file of scoped) {
      const candidate = normalizeAssetPath(file.path);
      const suffix = (file.suffix || "").toLowerCase();
      const name = (file.name || "").toLowerCase();
      if (IMAGE_SUFFIXES.has(suffix)) {
        if (name.startsWith("obj")) results.obj_images.push(candidate);
        else if (name.startsWith("grp")) results.grp_images.push(candidate);
        else results.sub_images.push(candidate);
      } else if (suffix === ".pl") results.pl_files.push(candidate);
      else if (suffix === ".json") results.json_files.push(candidate);
      else if (suffix === ".metta") results.metta_files.push(candidate);
      else if (suffix === ".prompt") results.prompt_files.push(candidate);
      else if (name.includes("eng")) results.eng_files.push(candidate);
      else results.unknown_files.push(candidate);
    }
    for (const key of Object.keys(results)) results[key].sort();
    setStackState(stackIndex, (stack) => {
      const setups = stack.setups?.length ? [...stack.setups] : defaultSetups(stack.key);
      const current = setups[imageIndex];
      if (!current) return stack;
      let base: Record<string, unknown> = {};
      const existing = (current.stateJson ?? "").trim();
      if (existing) {
        try {
          const parsed = JSON.parse(existing);
          if (parsed && typeof parsed === "object" && !Array.isArray(parsed)) base = parsed as Record<string, unknown>;
        } catch {
          // Replace unparseable editor contents with a fresh scan document.
        }
      }
      base.scan = { path: prefix, results };
      const toEntries = (paths: string[]) => paths.map((path) => imageSelectionFromPath(workspaceId, path, { name: path, dataUrl: "" }));
      setups[imageIndex] = {
        ...current,
        stateJson: `${JSON.stringify(base, null, 2)}\n`,
        objectImages: toEntries(results.obj_images),
        groupImages: toEntries(results.grp_images),
        subImages: toEntries(results.sub_images),
        plFiles: toEntries(results.pl_files),
        engFiles: toEntries(results.eng_files),
        jsonFiles: toEntries(results.json_files),
        mettaFiles: toEntries(results.metta_files),
        promptFiles: toEntries(results.prompt_files),
        unknownFiles: toEntries(results.unknown_files),
      };
      return { ...stack, setups };
    });
  };

  const captureImageAnalysis = (stackIndex: number, runnerIndex: number, imageIndex: number) => {
    setStackState(stackIndex, (stack) => {
      const runner = stack.runners[runnerIndex];
      if (!runner) return stack;
      const setups = stack.setups?.length ? [...stack.setups] : defaultSetups(stack.key);
      const current = setups[imageIndex];
      if (!current) return stack;
      const mergeByKey = (existing: AnalysisItem[], incoming: AnalysisItem[]): AnalysisItem[] => {
        const map = new Map(existing.map((item) => [item.key, item] as const));
        incoming.forEach((item) => { if (item.value) map.set(item.key, item); });
        return Array.from(map.values());
      };
      const nextSubimages: AnalysisItem[] = [];
      manyObjectImagesFromRunner(runner).forEach((item) => nextSubimages.push({ key: item.key, label: item.label, value: item.value }));
      if (runner.removedObjectImage) nextSubimages.push({ key: "image_of_object_removed", label: "image_of_object_removed", value: runner.removedObjectImage });
      if (runner.removedBackgroundImage) nextSubimages.push({ key: "image_without_object", label: "image_without_object", value: runner.removedBackgroundImage });
      if (runner.loopImageWithCircles) nextSubimages.push({ key: "image_with_circles", label: "image_with_circles", value: runner.loopImageWithCircles });
      const nextTextFiles: AnalysisItem[] = outputFileRows(runner.parsed).map((row) => ({ key: row.key, label: row.label, value: row.content }));
      if (runner.rawResponse) nextTextFiles.push({ key: "raw_response", label: "raw_response", value: runner.rawResponse });
      if (runner.debugLog) nextTextFiles.push({ key: "debug_log", label: "debug_log", value: runner.debugLog });
      const priorAnalysis = current.analysis;
      setups[imageIndex] = {
        ...current,
        analysis: {
          subimages: mergeByKey(priorAnalysis?.subimages || [], nextSubimages),
          textFiles: mergeByKey(priorAnalysis?.textFiles || [], nextTextFiles),
          updatedAt: new Date().toISOString(),
        },
      };
      return { ...stack, setups };
    });
  };

  const setImage = async (stackIndex: number, slot: "before" | "after", file: File | null) => {
    if (!file) return;
    try {
      const dataUrl = await readImageFile(file);
      setStackState(stackIndex, (stack) => ({
        ...stack,
        beforeImage: slot === "before" ? { name: file.name, dataUrl } : stack.beforeImage,
        afterImage: slot === "after" ? { name: file.name, dataUrl } : stack.afterImage,
        setups: (() => {
          const prior = stack.setups?.length ? stack.setups : defaultSetups(stack.key);
          const first = prior[0];
          if (!first) return prior;
          const updatedFirst: StackSetup = {
            ...first,
            beforeImage: slot === "before" ? { name: file.name, dataUrl } : first.beforeImage,
            afterImage: slot === "after" ? { name: file.name, dataUrl } : first.afterImage,
          };
          return [updatedFirst, ...prior.slice(1)];
        })(),
        runners: stack.runners.map((runner) => ({ ...runner, error: "" })),
      }));
    } catch (reason) {
      setRunnerState(stackIndex, 0, (runner) => ({ ...runner, error: reason instanceof Error ? reason.message : String(reason) }));
    }
  };

  const loadDebugLog = async (stackIndex: number, runnerIndex: number, path: string) => {
    setRunnerState(stackIndex, runnerIndex, (runner) => ({
      ...runner,
      debugLogPath: path,
      debugLog: "Loading invocation trace...",
    }));
    try {
      const payload = await request(
        `/api/workspaces/${encodeURIComponent(workspaceId)}/models/debug-log?path=${encodeURIComponent(path)}`,
      );
      setRunnerState(stackIndex, runnerIndex, (runner) => ({
        ...runner,
        debugLog: typeof payload.content === "string" ? payload.content : JSON.stringify(payload, null, 2),
      }));
    } catch (reason) {
      setRunnerState(stackIndex, runnerIndex, (runner) => ({
        ...runner,
        debugLog: `Debug trace could not be loaded: ${reason instanceof Error ? reason.message : String(reason)}`,
      }));
    }
  };

  const cancelPrompt = (stackIndex: number, runnerIndex: number) => {
    const stack = stackColumns[stackIndex];
    if (!stack) return;
    const runnerId = runnerDisplayId(pageDefinition.routeView, stack.key, runnerIndex);
    const controller = controllersRef.current[runnerId];
    if (!controller) return;
    controller.abort();
    controllersRef.current[runnerId] = null;
  };

  const runPrompt = async (stackIndex: number, runnerIndex: number, runMode: RunnerRunMode = "primary") => {
    const stack = stackColumns[stackIndex];
    const runner = stack?.runners[runnerIndex];
    if (!stack || !runner) return;
    const stackSetups = stack.setups?.length ? stack.setups : defaultSetups(stack.key);
    const activeSetupIndex = Math.max(0, Math.min(runner.setupIndex || 0, Math.max(0, stackSetups.length - 1)));
    const activeSetup = stackSetups[activeSetupIndex];
    const role = runnerRole(pageDefinition.routeView, stack.key, runnerIndex);
    const removalLoopRunner = isRemovalDiscoveryRunner(pageDefinition.routeView, stack.key, runnerIndex);
    const regenerateRunner = isRegeneratedIdentitiesRunner(pageDefinition.routeView, stack.key, runnerIndex);
    const promptDrivenIteration = removalLoopRunner || regenerateRunner;
    const autoLoop = runMode !== "primary";
    const untilExit = runMode === "until_exit";
    const effectiveModelId = resolveRunnerModelId(stack, runner);
    const effectiveValidatorModelId = resolveValidatorModelId(stack, runner);
    const validatorPromptText = String(runner.validatorPromptText || "").trim();
    const validatorEnabled = Boolean(effectiveValidatorModelId && validatorPromptText && runner.validatorPromptName !== VALIDATOR_PROMPT_DISABLED);
    const imageSourceBeforeLabel = imageFieldLabel("before");
    const imageSourceAfterLabel = imageFieldLabel("after");
    const bColumn = stackColumns.find((candidate) => candidate.key === "B");
    const b1RunnerIndex = bColumn?.runners.findIndex((candidate, index) =>
      isRemovalDiscoveryRunner(pageDefinition.routeView, "B", index)
    ) ?? -1;
    const b1Runner = bColumn && b1RunnerIndex >= 0 ? bColumn.runners[b1RunnerIndex] : null;
    const bucketManyObjects = (activeSetup?.analysis?.subimages || [])
      .filter((item) => /^many_objects/.test(item.key))
      .map((item) => ({ key: item.key, label: item.label, value: item.value }));
    const b1ManyObjects = bucketManyObjects.length
      ? bucketManyObjects
      : (b1Runner ? manyObjectImagesFromRunner(b1Runner) : []);
    const useManyObjectsForB2 = regenerateRunner && b1ManyObjects.length > 0;
    const imageSourceBefore = useManyObjectsForB2
      ? { name: b1ManyObjects[0].label, dataUrl: b1ManyObjects[0].value }
      : (activeSetup?.beforeImage || stack.beforeImage);
    const imageSourceAfter = useManyObjectsForB2
      ? {
        name: b1ManyObjects[1]?.label || b1ManyObjects[0].label,
        dataUrl: b1ManyObjects[1]?.value || b1ManyObjects[0].value,
      }
      : (activeSetup?.afterImage || stack.afterImage);
    const effectiveImageSourceBefore = role === "removal" && isB1B2PipelineRoute(pageDefinition.routeView)
      ? (imageSourceAfter || imageSourceBefore)
      : imageSourceBefore;
    if (!effectiveModelId) {
      setRunnerState(stackIndex, runnerIndex, (previous) => ({ ...previous, error: "Select an enabled model first. exit_value=unran." }));
      return;
    }
    if (!effectiveImageSourceBefore || !imageSourceAfter) {
      setRunnerState(stackIndex, runnerIndex, (previous) => ({
        ...previous,
        error: `Load ${imageSourceBeforeLabel}/${imageSourceAfterLabel} first. exit_value=unran.`,
      }));
      return;
    }
    const runnerId = runnerDisplayId(pageDefinition.routeView, stack.key, runnerIndex);
    controllersRef.current[runnerId]?.abort();
    const controller = new AbortController();
    controllersRef.current[runnerId] = controller;
    const outputId = runnerDisplayId(pageDefinition.routeView, stack.key, runnerIndex);
    setSelectedOutputId(outputId);
    setRunnerState(stackIndex, runnerIndex, (previous) => ({
      ...previous,
      running: true,
      currentRunMode: runMode,
      message: runMode === "primary"
        ? "Running primary prompt..."
        : runMode === "until_exit"
          ? `Running loop until exit (${validatorPromptDisplayName(pageDefinition.routeView, stack.key, runnerIndex, runner.validatorPromptName)})...`
          : `Running loop (${validatorPromptDisplayName(pageDefinition.routeView, stack.key, runnerIndex, runner.validatorPromptName)})...`,
      error: "",
      rawResponse: "",
      parsed: null,
      debugLogPath: "",
      debugLog: "",
      removedIdentityId: "",
      removedObjectImage: "",
      removedBackgroundImage: "",
      loopImageWithCircles: "",
      removalValidationSummary: "",
    }));
    try {
      const filesAddress = stackColumns.flatMap((column) => (
        column.runners.map((candidate, index) => ({
          id: runnerDisplayId(pageDefinition.routeView, column.key, index),
          stackKey: column.key,
          parsed: candidate.parsed,
          rawResponse: candidate.rawResponse,
          generationSeq: candidate.generationSeq,
        }))
      ));
      const filesSources = resolveFilesSources(runner.filesSourceIds, filesAddress, stack.key, outputHistory, stackColumns, runner);
      const validationFrame = await buildImageValidationFrame(imageSourceAfter.dataUrl);
      let latestParsed = runner.parsed;
      let acceptedAnyPass = false;
      const totalPasses = autoLoop ? Math.max(1, Math.floor(runner.autoLoopMaxIterations || AUTO_GAP_MAX_PASSES)) : 1;
      const maxLoopMs = autoLoop ? Math.max(10000, Math.floor((runner.autoLoopMaxSeconds || defaultTimeoutSeconds) * 1000)) : 0;
      const invocationTimeoutSeconds = Math.max(10, Math.floor(runner.maxPrimarySeconds || defaultTimeoutSeconds));
      const loopStartMs = Date.now();
      for (let passNumber = 1; passNumber <= totalPasses; passNumber += 1) {
        if (autoLoop && Date.now() - loopStartMs >= maxLoopMs) {
          setRunnerState(stackIndex, runnerIndex, (previous) => ({
            ...previous,
            message: `Loop stopped at time limit (${Math.floor(maxLoopMs / 1000)}s) after ${passNumber - 1} pass(es). exit_value=loop_overbudgeted.`,
          }));
          break;
        }
        const priorPassParsed = latestParsed;
        const isGapPass = autoLoop && passNumber > 1;
        const baseImageLabels = {
          before: `${imageSourceBeforeLabel} (${effectiveImageSourceBefore.name})`,
          after: `${imageSourceAfterLabel} (${imageSourceAfter.name})`,
        };
        let overlaySource = "";
        const image = isGapPass
          ? await (async () => {
            overlaySource = await createIdentityOverlay(
              imageSourceAfter.dataUrl,
              asIdentityCandidates(priorPassParsed),
            );
            return triSheet(
              { label: baseImageLabels.before, source: effectiveImageSourceBefore.dataUrl },
              { label: baseImageLabels.after, source: imageSourceAfter.dataUrl },
              { label: "debug_overlay_image (claimed boxes)", source: overlaySource },
            );
          })()
          : await pairSheet(
            { label: baseImageLabels.before, source: effectiveImageSourceBefore.dataUrl },
            { label: baseImageLabels.after, source: imageSourceAfter.dataUrl },
          );
        if (overlaySource) {
          setRunnerState(stackIndex, runnerIndex, (previous) => ({ ...previous, loopImageWithCircles: overlaySource }));
        }
        let acceptedParsed: ParsedPrologPayload | null = null;
        let acceptedInvocation: ModelInvocation | null = null;
        let acceptedRaw = "";
        let lastValidationIssues: ValidationIssue[] = [];
        let acceptedNewCount = 0;
        let acceptedExitValue: PromptExitValue = "next_iteration";
        for (let attempt = 0; attempt <= AUTO_VALIDATION_REPAIR_ATTEMPTS; attempt += 1) {
          const isRepairAttempt = attempt > 0;
          const passPrompt = isGapPass
            ? (removalLoopRunner
              ? runner.promptText
              : [runner.promptText, GAP_DISCOVERY_PASS_PROMPT].join("\n\n"))
            : runner.promptText;
          const prompt = [
            `Use stack ${stack.key} fields ${imageSourceBeforeLabel}/${imageSourceAfterLabel}. Treat image #1 as parent and image #2 as current state.`,
            isGapPass ? "Image #3 is debug_overlay_image for pass-N coverage gap discovery." : "",
            "Also generate current_identities, current_hypotheses, action_history, objects_english, differences_english, and rules_english in the JSON response.",
            filesSources.length
              ? `Files input sources: ${filesSources.map((source) => source.label).join(" | ")}.`
              : "Files input source: none.",
            filesSources.length
              ? filesSources.map((source) => `Files source content (${source.label}):\n${source.content}`).join("\n\n")
              : "",
            isGapPass && Array.isArray(priorPassParsed?.current_identities)
              ? `Prior pass current_identities:\n${JSON.stringify({ current_identities: priorPassParsed.current_identities }, null, 2)}`
              : "",
            isRepairAttempt && lastValidationIssues.length
              ? `VALIDATION_ERRORS:\n${JSON.stringify(lastValidationIssues, null, 2)}`
              : "",
            isRepairAttempt ? VALIDATION_REPAIR_PROMPT : "",
            passPrompt,
          ].filter(Boolean).join("\n\n");
          const payload = await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/models/${encodeURIComponent(effectiveModelId)}/invoke`, {
            method: "POST",
            signal: controller.signal,
            body: JSON.stringify({ prompt, image, timeoutSeconds: invocationTimeoutSeconds }),
          });
          const invocation = payload as ModelInvocation;
          const raw = typeof invocation.text === "string"
            ? invocation.text
            : JSON.stringify(payload, null, 2);
          const parsedPayloadRaw = tryParseResponse(raw);
          const parsedPayload = parsedPayloadRaw ? normalizeParsedPayload(parsedPayloadRaw, priorPassParsed) : null;
          if (parsedPayload && regenerateRunner) {
            const regenerated = Array.isArray(parsedPayload.regenerated_identities)
              ? parsedPayload.regenerated_identities
              : [];
            const current = Array.isArray(parsedPayload.current_identities)
              ? parsedPayload.current_identities
              : [];
            parsedPayload.regenerated_identities = regenerated.length ? regenerated : current;
          }
          generationSeqRef.current += 1;
          const currentSeq = generationSeqRef.current;
          setOutputHistory((previous) => [
            {
              id: `G${currentSeq}`,
              generationSeq: currentSeq,
              runnerId,
              createdAt: new Date().toISOString(),
              parsed: parsedPayload,
              rawResponse: raw,
            },
            ...previous,
          ].slice(0, 200));
          let loopMessage = parsedPayload
            ? `Pass ${passNumber}${isRepairAttempt ? ` repair ${attempt}` : ""} parsed.`
            : `Pass ${passNumber}${isRepairAttempt ? ` repair ${attempt}` : ""} was not strict JSON. exit_value=llm_error.`;
          if (!parsedPayload) {
            setRunnerState(stackIndex, runnerIndex, (previous) => ({
              ...previous,
              result: invocation,
              rawResponse: raw,
              parsed: parsedPayload,
              generationSeq: currentSeq,
              message: loopMessage,
            }));
            if (invocation.debugLogPath) await loadDebugLog(stackIndex, runnerIndex, invocation.debugLogPath);
            break;
          }
          const validation = validatePassOutput(
            priorPassParsed,
            parsedPayload,
            validationFrame,
            isGapPass ? "gap" : "baseline",
          );
          let passAccepted = validation.accepted;
          let passIssues = validation.issues;
          let passExitValue = normalizeExitValue((parsedPayload as Record<string, unknown>).exit_value, "next_iteration");
          let removalArtifacts: RemovalArtifacts | null = null;
          if (passAccepted && removalLoopRunner) {
            const selectedRemovable = pickRemovableIdentity(priorPassParsed, parsedPayload);
            if (selectedRemovable) {
              removalArtifacts = await generateRemovalArtifacts(imageSourceAfter.dataUrl, selectedRemovable);
              if (!removalArtifacts.accepted) {
                passAccepted = false;
                passIssues = [
                  ...passIssues,
                  ...removalArtifacts.issues.map((detail) => ({
                    id: selectedRemovable.id,
                    code: "removal_validation_failed",
                    detail,
                  })),
                ];
              } else {
                if (parsedPayload) {
                  const parsedRecord = parsedPayload as unknown as Record<string, unknown>;
                  parsedRecord.image_of_object_removed = removalArtifacts.objectImage;
                  parsedRecord.image_without_object = removalArtifacts.backgroundImage;
                  parsedRecord.removed_object_image = removalArtifacts.objectImage;
                  parsedRecord.many_objects_1 = removalArtifacts.objectImage;
                  parsedRecord.many_objects_2 = removalArtifacts.backgroundImage;
                  parsedRecord.many_objects = [removalArtifacts.objectImage, removalArtifacts.backgroundImage];
                }
                setRunnerState(stackIndex, runnerIndex, (previous) => ({
                  ...previous,
                  removedIdentityId: selectedRemovable.id,
                  removedObjectImage: removalArtifacts?.objectImage || "",
                  removedBackgroundImage: removalArtifacts?.backgroundImage || "",
                  removalValidationSummary: `Removal validated for ${selectedRemovable.id}.`,
                }));
              }
            }
          }
          loopMessage = passAccepted
            ? `Pass ${passNumber} validated: ${validation.newCount} new identities.`
            : `Pass ${passNumber} validation failed (${passIssues.length} issue(s)).`;
          if (passAccepted && validatorEnabled) {
            const validatorPrompt = [
              "You are validating a candidate ARC extraction result for correctness.",
              "Use strict checks for duplicate IDs, missing/invalid bboxes, out-of-bounds boxes, and implausible new identities.",
              "Return strict JSON only: {\"approved\": boolean, \"exit_value\": \"llm_error|next_iteration|loop_complete|loop_overbudgeted|unran\", \"issues\": [\"...\"]}.",
              `Validation image context: image #1 parent, image #2 current${isGapPass ? ", image #3 debug overlay" : ""}.`,
              `Validation mode: ${isGapPass ? "gap-pass" : "baseline-pass"}.`,
              `Prior current_identities:\n${JSON.stringify({ current_identities: priorPassParsed?.current_identities || [] }, null, 2)}`,
              `Candidate output:\n${JSON.stringify(parsedPayload, null, 2)}`,
              validatorPromptText,
            ].join("\n\n");
            const validatorPayload = await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/models/${encodeURIComponent(effectiveValidatorModelId)}/invoke`, {
              method: "POST",
              signal: controller.signal,
              body: JSON.stringify({ prompt: validatorPrompt, image, timeoutSeconds: invocationTimeoutSeconds }),
            });
            const validatorInvocation = validatorPayload as ModelInvocation;
            const validatorRaw = typeof validatorInvocation.text === "string"
              ? validatorInvocation.text
              : JSON.stringify(validatorPayload, null, 2);
            const assessment = tryParseValidatorAssessment(validatorRaw);
            if (!assessment) {
              passAccepted = false;
              passIssues = [
                ...passIssues,
                {
                  id: "*",
                  code: "validator_non_json",
                  detail: "Validator response was not strict assessment JSON.",
                },
              ];
            } else if (!assessment.approved || assessment.exitValue === "llm_error" || assessment.exitValue === "unran") {
              passAccepted = false;
              passIssues = [
                ...passIssues,
                ...(assessment.issues.length
                  ? assessment.issues.map((detail: string) => ({
                    id: "*",
                    code: "validator_reject",
                    detail,
                  }))
                  : [{
                    id: "*",
                    code: "validator_reject",
                    detail: "Validator rejected without details.",
                  }]),
              ];
            } else {
              passExitValue = assessment.exitValue;
            }
          }
          if (passAccepted && (passExitValue === "llm_error" || passExitValue === "unran")) {
            passAccepted = false;
            passIssues = [
              ...passIssues,
              {
                id: "*",
                code: "exit_value_invalid_for_accept",
                detail: `Candidate requested non-accepting exit_value=${passExitValue}.`,
              },
            ];
          }
          setRunnerState(stackIndex, runnerIndex, (previous) => ({
            ...previous,
            result: invocation,
            rawResponse: raw,
            parsed: parsedPayload,
            generationSeq: currentSeq,
            message: passAccepted
              ? (validatorEnabled ? `${loopMessage} External validator approved. exit_value=${passExitValue}.` : `${loopMessage} exit_value=${passExitValue}.`)
              : `Pass ${passNumber} validation failed (${passIssues.length} issue(s)).`,
          }));
          if (invocation.debugLogPath) await loadDebugLog(stackIndex, runnerIndex, invocation.debugLogPath);
          if (passAccepted) {
            acceptedParsed = parsedPayload;
            acceptedInvocation = invocation;
            acceptedRaw = raw;
            acceptedNewCount = validation.newCount;
            acceptedExitValue = passExitValue;
            break;
          }
          lastValidationIssues = passIssues;
          if (attempt === AUTO_VALIDATION_REPAIR_ATTEMPTS) {
            setRunnerState(stackIndex, runnerIndex, (previous) => ({
              ...previous,
              error: `Validation failed after ${AUTO_VALIDATION_REPAIR_ATTEMPTS + 1} attempts: ${passIssues.map((issue) => `${issue.id}:${issue.code}`).join(", ")}`,
            }));
          }
        }
        if (!acceptedParsed || !acceptedInvocation) break;
        latestParsed = acceptedParsed;
        acceptedAnyPass = true;
        if (!autoLoop) {
          setRunnerState(stackIndex, runnerIndex, (previous) => ({
            ...previous,
            result: acceptedInvocation,
            rawResponse: acceptedRaw,
            parsed: acceptedParsed,
            message: "Validated single pass complete.",
          }));
          break;
        }
        if (!isGapPass) {
          setRunnerState(stackIndex, runnerIndex, (previous) => ({
            ...previous,
            message: "Baseline pass validated. Running coverage-gap passes.",
          }));
          continue;
        }
        if (acceptedExitValue === "loop_complete") {
          setRunnerState(stackIndex, runnerIndex, (previous) => ({
            ...previous,
            message: `Loop converged at pass ${passNumber}: exit_value=loop_complete.`,
          }));
          break;
        }
        if (untilExit) {
          continue;
        }
        if (promptDrivenIteration) {
          if (acceptedExitValue === "next_iteration") {
            continue;
          }
          setRunnerState(stackIndex, runnerIndex, (previous) => ({
            ...previous,
            message: `Loop stopped at pass ${passNumber}: exit_value=${acceptedExitValue}.`,
          }));
          break;
        }
        if (acceptedNewCount === 0) {
          setRunnerState(stackIndex, runnerIndex, (previous) => ({
            ...previous,
            message: `Loop converged at pass ${passNumber}: validation passed and no new identities remained.`,
          }));
          break;
        }
      }
      if (replaceGuesserOnFinish && regenerateRunner && acceptedAnyPass && isB1B2PipelineRoute(pageDefinition.routeView) && latestParsed) {
        const finalIdentities = Array.isArray(latestParsed.regenerated_identities) && latestParsed.regenerated_identities.length
          ? latestParsed.regenerated_identities
          : (Array.isArray(latestParsed.current_identities) ? latestParsed.current_identities : []);
        const guesserIndex = bColumn
          ? bColumn.runners.findIndex((_, index) => runnerRole(pageDefinition.routeView, "B", index) === "extraction")
          : -1;
        const guesserStackIndex = stackColumns.findIndex((column) => column.key === "B");
        if (finalIdentities.length && guesserIndex >= 0 && guesserStackIndex >= 0) {
          setRunnerState(guesserStackIndex, guesserIndex, (previous) => {
            const base = previous.parsed ?? ({} as ParsedPrologPayload);
            return {
              ...previous,
              parsed: { ...base, current_identities: finalIdentities, regenerated_identities: finalIdentities },
              message: `GUESSER list replaced with REGENERATOR result (${finalIdentities.length} identities).`,
            };
          });
        }
      }
    } catch (reason) {
      if (reason instanceof DOMException && reason.name === "AbortError") {
        setRunnerState(stackIndex, runnerIndex, (previous) => ({
          ...previous,
          message: "Run canceled. exit_value=unran.",
          error: "",
        }));
      } else {
        setRunnerState(stackIndex, runnerIndex, (previous) => ({
          ...previous,
          error: reason instanceof Error ? reason.message : String(reason),
        }));
        if (reason instanceof RequestFailure && reason.debugLogPath) {
          await loadDebugLog(stackIndex, runnerIndex, reason.debugLogPath);
        }
      }
    } finally {
      controllersRef.current[runnerId] = null;
      setRunnerState(stackIndex, runnerIndex, (previous) => ({ ...previous, running: false, currentRunMode: "" }));
      captureImageAnalysis(stackIndex, runnerIndex, activeSetupIndex);
    }
  };

  const runnerOutputOptions = stackColumns.flatMap((stack, stackIndex) => (
    stack.runners.map((runner, runnerIndex) => ({
      id: runnerDisplayId(pageDefinition.routeView, stack.key, runnerIndex),
      label: `Files ${runnerDisplayId(pageDefinition.routeView, stack.key, runnerIndex)}`,
      stackIndex,
      runnerIndex,
      runner,
    }))
  ));
  const selectedOutput = runnerOutputOptions.find((option) => option.id === selectedOutputId) || runnerOutputOptions[0];
  const selectedRunner = selectedOutput?.runner || null;
  const modeFor = (key: string, fallback: AccordionDisplayMode = "scroll") => accordionModes[key] || fallback;
  const setModeFor = (key: string, mode: AccordionDisplayMode) => setAccordionModes((current) => ({ ...current, [key]: mode }));
  const applyScannedDataFiles = async (candidateFiles: WorkspaceFileRecord[], overwriteExisting = true) => {
    if (!workspaceId) return;
    const updates = await Promise.all(activeStackColumns.map(async (column) => ({
      key: column.key,
      generated: await readWorkspaceTextDataField(workspaceId, candidateFiles, column.key, "Generated"),
      command: await readWorkspaceTextDataField(workspaceId, candidateFiles, column.key, "Command"),
      prompts: await Promise.all(
        Array.from({ length: 12 }, (_, index) =>
          readWorkspaceTextDataField(workspaceId, candidateFiles, column.key, "Prompt", index + 1),
        ),
      ),
    })));
    setStackColumns((previous) => previous.map((stack) => {
      const update = updates.find((candidate) => candidate.key === stack.key);
      if (!update) return stack;
      const stackASetups = shouldUseDescendSetups(pageDefinition.routeView, stack.key)
        ? stackADescendSetupsFromFiles(workspaceId, candidateFiles)
        : [];
      const normalizedSetups = stackASetups.length
        ? stackASetups
        : (stack.setups?.length ? stack.setups : defaultSetups(stack.key));
      const autoBefore = autoImageFromWorkspaceData(workspaceId, candidateFiles, stack.key, "before");
      const autoAfter = autoImageFromWorkspaceData(workspaceId, candidateFiles, stack.key, "after");
      return {
        ...stack,
        beforeImage: overwriteExisting
          ? (autoBefore || normalizedSetups[0]?.beforeImage || stack.beforeImage)
          : (stack.beforeImage || autoBefore || normalizedSetups[0]?.beforeImage),
        afterImage: overwriteExisting
          ? (autoAfter || normalizedSetups[0]?.afterImage || stack.afterImage)
          : (stack.afterImage || autoAfter || normalizedSetups[0]?.afterImage),
        setups: normalizedSetups,
        desc1: overwriteExisting ? (update.generated ?? stack.desc1) : (stack.desc1 || update.generated || ""),
        desc2: overwriteExisting ? (update.command ?? stack.desc2) : (stack.desc2 || update.command || ""),
        runners: stack.runners.map((runner, index) => ({
          ...runner,
          promptText: overwriteExisting ? (update.prompts[index] ?? runner.promptText) : (runner.promptText || update.prompts[index] || ""),
          setupIndex: Math.max(0, Math.min(runner.setupIndex || 0, Math.max(0, normalizedSetups.length - 1))),
        })),
      };
    }));
  };
  useEffect(() => {
    if (!workspaceId) return;
    let canceled = false;
    const autoScanDataFiles = async () => {
      try {
        const payload = await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/data/files`);
        if (canceled) return;
        const records = Array.isArray(payload.files) ? payload.files : [];
        const dataFiles = records
          .filter((item): item is WorkspaceFileRecord => Boolean(item)
            && typeof (item as Record<string, unknown>).path === "string"
            && typeof (item as Record<string, unknown>).name === "string"
            && typeof (item as Record<string, unknown>).suffix === "string"
            && typeof (item as Record<string, unknown>).modified === "number")
          .filter((item) => isDataFilePath(item.path));
        await applyScannedDataFiles(dataFiles.length ? dataFiles : files, true);
      } catch {
        // Keep page usable even if initial data scan endpoint is temporarily unavailable.
      }
    };
    void autoScanDataFiles();
    return () => {
      canceled = true;
    };
  }, [workspaceId]);
  useEffect(() => {
    setSelectedOutputId(initialSelectedOutputId(pageDefinition));
  }, [pageDefinition.id, pageDefinition.routeView]);
  const scanDataByName = async () => {
    setScanDataBusy(true);
    try {
      await Promise.resolve(onPageDefinitionSaved());
      const payload = await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/data/files`);
      const records = Array.isArray(payload.files) ? payload.files : [];
      const dataFiles = records
        .filter((item): item is WorkspaceFileRecord => Boolean(item)
          && typeof (item as Record<string, unknown>).path === "string"
          && typeof (item as Record<string, unknown>).name === "string"
          && typeof (item as Record<string, unknown>).suffix === "string"
          && typeof (item as Record<string, unknown>).modified === "number")
        .filter((item) => isDataFilePath(item.path));
      await applyScannedDataFiles(dataFiles.length ? dataFiles : files, true);
    } finally {
      setScanDataBusy(false);
    }
  };

  const registry: WorkflowPageComponentRegistry = {
    Arc3ImagePairInputs: () => {
      const stackIndex = 0;
      const stack = stackColumns[stackIndex];
      if (!stack) {
        return {
          value: "No stack",
          detail: "No image stack configured",
          baseClass: "english-workflow-panel arc3-prolog-page-panel",
          content: <small>No image stack configured.</small>,
        };
      }
      const setups = stack.setups?.length ? stack.setups : defaultSetups(stack.key);
      const selectedIndex = Math.max(0, Math.min(stack.selectedImageIndex ?? 0, Math.max(0, setups.length - 1)));
      const imagesStackId = "arc3-b1b2-images-A";
      return {
        value: `${setups.length} image${setups.length === 1 ? "" : "s"}`,
        detail: `Active: ${setups[selectedIndex]?.label || `image_${selectedIndex + 1}`}`,
        baseClass: "english-workflow-panel arc3-prolog-page-panel",
        scrollSize: "calc(100vh - 250px)",
        content: <ThreeStateAccordionStack id={imagesStackId} className="arc3-prolog-accordion-stack" controlsLabel="IMAGES">
          {setups.map((setup, imageIndex) => {
            const analysis = setup.analysis;
            const subimages = analysis?.subimages || [];
            const textFiles = analysis?.textFiles || [];
            const isActive = imageIndex === selectedIndex;
            const stateDirDefault = (() => {
              const normalized = normalizeAssetPath(setup.afterImage?.name || "");
              const slash = normalized.lastIndexOf("/");
              return slash > 0 ? normalized.slice(0, slash) : "";
            })();
            const pathPrefix = normalizeAssetPath(setup.stateDir ?? stateDirDefault).replace(/\/+$/, "") || "$PATH";
            const cleanStateDir = normalizeAssetPath(setup.stateDir ?? stateDirDefault).replace(/\/+$/, "");
            const relativeToSetupDir = (fileName: string) => {
              const base = normalizeAssetPath(fileName).split("/").pop() || normalizeAssetPath(fileName);
              return cleanStateDir ? `${cleanStateDir}/${base}` : base;
            };
            const imageSuffixesLower = [...IMAGE_SUFFIXES].map((suffix) => suffix.toLowerCase());
            const imageMatches = files
              .filter((file) => imageSuffixesLower.includes((file.suffix || "").toLowerCase()))
              .map((file) => file.path.replace(/\\/g, "/"))
              .filter((path, index, all) => all.indexOf(path) === index)
              .sort((left, right) => left.localeCompare(right));
            const renderSingleImageControls = (browseKey: string, setter: (path: string) => void) => <>
              <label className="secondary arc3-prolog-browse-btn arc3-prolog-browse-b" title="Load a file from your computer">
                Load
                <input
                  type="file"
                  accept={imageSuffixesLower.join(",")}
                  style={{ display: "none" }}
                  onChange={(event) => {
                    const picked = event.target.files && event.target.files[0];
                    if (picked) {
                      setter(relativeToSetupDir(picked.name));
                    }
                    event.target.value = "";
                  }}
                />
              </label>
              <button
                type="button"
                className="secondary arc3-prolog-browse-btn"
                title="Pick from workspace files"
                onClick={() => setOpenBrowseKey(openBrowseKey === browseKey ? null : browseKey)}
              >Select</button>
            </>;
            const renderSingleImageList = (browseKey: string, setter: (path: string) => void) => openBrowseKey === browseKey && <div className="arc3-prolog-browse-list">
              {imageMatches.length
                ? imageMatches.map((path) => <button
                  key={path}
                  type="button"
                  className="arc3-prolog-browse-option"
                  onClick={() => {
                    setter(path);
                    setOpenBrowseKey(null);
                  }}
                >{path}</button>)
                : <div className="arc3-prolog-browse-empty">No matching workspace files</div>}
            </div>;
            const resolveEditorPath = (name: string) => {
              const normalized = normalizeAssetPath(name).replace(/^\/+/, "");
              if (!normalized) return "";
              return normalized.includes("/") ? normalized : (cleanStateDir ? `${cleanStateDir}/${normalized}` : normalized);
            };
            const openEntryEditor = async (field: SetupCollectionField, entryIndex: number, path: string) => {
              setOpenBrowseKey(null);
              setOpenEditorKey(`edit:${field}:${setup.id}:${entryIndex}`);
              setEditorName(path);
              setEditorText("");
              setEditorError("");
              const rel = normalizeAssetPath(path).replace(/^\/+/, "");
              if (!rel || !workspaceId) return;
              setEditorBusy(true);
              try {
                const response = await fetch(workspaceAssetUrl(workspaceId, rel), { cache: "no-store" });
                if (response.ok) setEditorText(await response.text());
                else setEditorError(`Could not load ${rel} (${response.status})`);
              } catch (reason) {
                setEditorError(reason instanceof Error ? reason.message : String(reason));
              } finally {
                setEditorBusy(false);
              }
            };
            const openNewEditor = (field: SetupCollectionField, suggestedName: string) => {
              setOpenBrowseKey(null);
              setOpenEditorKey(`new:${field}:${setup.id}`);
              setEditorName(suggestedName);
              setEditorText("");
              setEditorError("");
            };
            const expandNonEmptyGroups = () => {
              const groupCounts: Array<[SetupCollectionField, number]> = [
                ["objectImages", setup.objectImages?.length ?? 0],
                ["groupImages", setup.groupImages?.length ?? 0],
                ["subImages", (setup.subImages?.length ?? 0) + subimages.length],
                ["plFiles", setup.plFiles?.length ?? 0],
                ["engFiles", setup.engFiles?.length ?? 0],
                ["jsonFiles", setup.jsonFiles?.length ?? 0],
                ["mettaFiles", setup.mettaFiles?.length ?? 0],
                ["promptFiles", setup.promptFiles?.length ?? 0],
                ["unknownFiles", (setup.unknownFiles?.length ?? 0) + textFiles.length],
              ];
              setGroupOpen((previous) => {
                const next = { ...previous };
                for (const [groupField, count] of groupCounts) {
                  if (count > 0) next[`${groupField}:${setup.id}`] = true;
                }
                return next;
              });
            };
            const renderFileEditor = (editorKey: string, onSaved: (path: string) => void) => openEditorKey === editorKey && <div className="arc3-prolog-setup-file-editor">
              <div className="arc3-prolog-setup-file-editor-head">
                <span>FILE</span>
                <input
                  className="arc3-prolog-setup-inline-input"
                  type="text"
                  value={editorName}
                  placeholder={`${pathPrefix}/name.ext`}
                  onChange={(event) => setEditorName(event.target.value)}
                />
                <button
                  type="button"
                  className="secondary arc3-prolog-browse-btn arc3-prolog-setup-editor-save"
                  disabled={editorBusy}
                  onClick={async () => {
                    const path = resolveEditorPath(editorName);
                    if (!path) {
                      setEditorError("A file path is required.");
                      return;
                    }
                    setEditorBusy(true);
                    const ok = await saveDataFile(path, editorText);
                    setEditorBusy(false);
                    if (ok) {
                      onSaved(path);
                      setOpenEditorKey(null);
                    }
                  }}
                >Save</button>
                <button
                  type="button"
                  className="secondary arc3-prolog-browse-btn arc3-prolog-setup-editor-saveas"
                  onClick={() => void saveTextFileAs(editorName, editorText)}
                >Save as..</button>
                <button
                  type="button"
                  className="secondary arc3-prolog-browse-btn arc3-prolog-setup-editor-close"
                  onClick={() => {
                    setOpenEditorKey(null);
                    setEditorError("");
                  }}
                >Close</button>
              </div>
              <textarea
                className="arc3-prolog-setup-state-json arc3-prolog-setup-editor-text"
                value={editorText}
                placeholder={editorBusy ? "Loading…" : ""}
                spellCheck={false}
                rows={8}
                onChange={(event) => setEditorText(event.target.value)}
              />
              {editorError ? <div className="arc3-prolog-error">{editorError}</div> : null}
            </div>;
            const renderSetupCollectionGroup = (
              field: SetupCollectionField,
              title: string,
              itemLabel: string,
              kind: "image" | "file",
              accept: string[],
              options?: { defaultOpen?: boolean; derivedCount?: number; derived?: ReactNode; placeholder?: string; editable?: boolean },
            ) => {
              const entries = setup[field] || [];
              const acceptLower = accept.map((suffix) => suffix.toLowerCase());
              const acceptAttr = acceptLower.join(",");
              const workspaceMatches = files
                .filter((file) => acceptLower.length === 0 || acceptLower.includes((file.suffix || "").toLowerCase()))
                .map((file) => file.path.replace(/\\/g, "/"))
                .filter((path, index, all) => all.indexOf(path) === index)
                .sort((left, right) => left.localeCompare(right));
              const addKey = `${field}:${setup.id}:__add`;
              const groupKey = `${field}:${setup.id}`;
              const totalCount = (options?.derivedCount ?? 0) + entries.length;
              const groupIsOpen = groupOpen[groupKey] ?? (options?.defaultOpen ?? true);
              return <details
                open={groupIsOpen}
                className="arc3-prolog-setup-object-images"
                onToggle={(event) => {
                  const nextOpen = event.currentTarget.open;
                  setGroupOpen((previous) => (previous[groupKey] === nextOpen ? previous : { ...previous, [groupKey]: nextOpen }));
                }}
              >
                <summary>{`${title} (${totalCount})`}</summary>
                {options?.derived}
                {entries.map((entry, entryIndex) => {
                  const rowKey = `${field}:${setup.id}:${entryIndex}`;
                  const entryBase = normalizeAssetPath(entry.name).split("/").pop() || "";
                  const entryLabel = entryBase ? entryBase.replace(/\./g, "_") : `${itemLabel} ${entryIndex + 1}`;
                  return <div
                    key={`${field}-${setup.id}-${entryIndex}`}
                    className="arc3-prolog-object-image-row"
                  >
                    <label className="arc3-prolog-inline-select-label">
                      <span>{entryLabel}</span>
                      <div className="arc3-prolog-browse-inputwrap">
                        <input
                          className="arc3-prolog-setup-inline-input"
                          type="text"
                          value={entry.name}
                          placeholder={options?.placeholder ?? (kind === "image" ? "data/... image path" : "data/... file path")}
                          onChange={(event) => setSetupEntryPath(stackIndex, imageIndex, field, entryIndex, event.target.value)}
                        />
                        {options?.editable && <button
                          type="button"
                          className="secondary arc3-prolog-browse-btn arc3-prolog-setup-edit"
                          title="Load and edit this file"
                          onClick={() => void openEntryEditor(field, entryIndex, entry.name)}
                        >Load/Edit</button>}
                        <button
                          type="button"
                          className="secondary arc3-prolog-browse-btn"
                          title="Pick from workspace files"
                          onClick={() => setOpenBrowseKey(openBrowseKey === rowKey ? null : rowKey)}
                        >Select</button>
                        <label className="secondary arc3-prolog-browse-btn arc3-prolog-browse-b" title="Browse for a file on your computer">
                          Browse
                          <input
                            type="file"
                            accept={acceptAttr}
                            style={{ display: "none" }}
                            onChange={(event) => {
                              const picked = event.target.files && event.target.files[0];
                              if (picked) {
                                setSetupEntryPath(stackIndex, imageIndex, field, entryIndex, relativeToSetupDir(picked.name));
                              }
                              event.target.value = "";
                            }}
                          />
                        </label>
                        <button
                          type="button"
                          className="secondary arc3-prolog-browse-btn arc3-prolog-object-image-remove"
                          onClick={() => removeSetupEntry(stackIndex, imageIndex, field, entryIndex)}
                        >Remove</button>
                        {options?.editable && <button
                          type="button"
                          className="secondary arc3-prolog-browse-btn arc3-prolog-setup-entry-saveas"
                          title="Save this file to your computer"
                          onClick={() => void saveEntryFileAs(entry.name)}
                        >Save as..</button>}
                      </div>
                    </label>
                    {kind === "image"
                      ? (entry.dataUrl
                        ? <img className="arc3-prolog-preview" src={entry.dataUrl} alt={`${itemLabel.toLowerCase()} ${entryIndex + 1}`} />
                        : <div className="arc3-prolog-setup-preview-placeholder">No image</div>)
                      : null}
                    {openBrowseKey === rowKey && <div className="arc3-prolog-browse-list">
                      {workspaceMatches.length
                        ? workspaceMatches.map((path) => <button
                          key={path}
                          type="button"
                          className="arc3-prolog-browse-option"
                          onClick={() => {
                            setSetupEntryPath(stackIndex, imageIndex, field, entryIndex, path);
                            setOpenBrowseKey(null);
                          }}
                        >{path}</button>)
                        : <div className="arc3-prolog-browse-empty">No matching workspace files</div>}
                    </div>}
                    {renderFileEditor(`edit:${field}:${setup.id}:${entryIndex}`, (path) => {
                      if (path !== entry.name) setSetupEntryPath(stackIndex, imageIndex, field, entryIndex, path);
                    })}
                  </div>;
                })}
                <div className="arc3-prolog-object-image-actions">
                  <label className="secondary arc3-prolog-browse-btn arc3-prolog-browse-b" title="Load a file from your computer">
                    Load
                    <input
                      type="file"
                      accept={acceptAttr}
                      style={{ display: "none" }}
                      onChange={(event) => {
                        const picked = event.target.files && event.target.files[0];
                        if (picked) {
                          appendSetupEntryPath(stackIndex, imageIndex, field, relativeToSetupDir(picked.name));
                        }
                        event.target.value = "";
                      }}
                    />
                  </label>
                  <button
                    type="button"
                    className="secondary arc3-prolog-browse-btn"
                    title="Pick from workspace files"
                    onClick={() => setOpenBrowseKey(openBrowseKey === addKey ? null : addKey)}
                  >Select</button>
                  {options?.editable && <button
                    type="button"
                    className="secondary arc3-prolog-browse-btn arc3-prolog-setup-new"
                    title="Create a new file"
                    onClick={() => openNewEditor(field, `${pathPrefix}/untitled${accept[0] ?? ".txt"}`)}
                  >New</button>}
                </div>
                {openBrowseKey === addKey && <div className="arc3-prolog-browse-list">
                  {workspaceMatches.length
                    ? workspaceMatches.map((path) => <button
                      key={path}
                      type="button"
                      className="arc3-prolog-browse-option"
                      onClick={() => {
                        appendSetupEntryPath(stackIndex, imageIndex, field, path);
                        setOpenBrowseKey(null);
                      }}
                    >{path}</button>)
                    : <div className="arc3-prolog-browse-empty">No matching workspace files</div>}
                </div>}
                {renderFileEditor(`new:${field}:${setup.id}`, (path) => appendSetupEntryPath(stackIndex, imageIndex, field, path))}
              </details>;
            };
            return <ThreeStateAccordionMember
              key={setup.id}
              stackId={imagesStackId}
              memberKey={`image-${setup.id}`}
              label={`Setup_${imageIndex + 1}`}
              value={isActive ? "ACTIVE" : `Setup_${imageIndex + 1}`}
              detail={`${subimages.length} image(s) / ${textFiles.length} textual file(s)`}
              mode={modeFor(`image-${setup.id}`)}
              onChange={(mode) => setModeFor(`image-${setup.id}`, mode)}
              baseClass="english-workflow-panel arc3-prolog-page-panel"
              scrollSize="480px"
              accessories={<button type="button" className={isActive ? "arc3-prolog-active-toggle" : "secondary"} onClick={() => selectImage(stackIndex, imageIndex)}>{isActive ? "Selected" : "Select"}</button>}
            >
              <details
                className="arc3-prolog-setup-extra arc3-prolog-setup-dir-props"
                onToggle={(event) => {
                  if (event.currentTarget.open && !(setup.stateJson ?? "").trim()) {
                    void loadSetupStateJson(stackIndex, imageIndex, setup.stateDir ?? stateDirDefault, setup.stateFile ?? "state.json");
                  }
                }}
              >
                <summary>
                  DIR &amp; PROPERTIES
                  <button
                    type="button"
                    className="secondary arc3-prolog-browse-btn arc3-prolog-setup-scan arc3-prolog-setup-scan-summary"
                    title="Scan this directory into the file groups (no need to expand)"
                    onClick={(event) => {
                      event.preventDefault();
                      event.stopPropagation();
                      void scanSetupStatePath(stackIndex, imageIndex, setup.stateDir ?? stateDirDefault);
                    }}
                  >scan</button>
                  <button
                    type="button"
                    className="secondary arc3-prolog-browse-btn arc3-prolog-setup-scan-summary arc3-prolog-setup-expand-summary"
                    title="Expand all non-empty file groups"
                    onClick={(event) => {
                      event.preventDefault();
                      event.stopPropagation();
                      expandNonEmptyGroups();
                    }}
                  >expand</button>
                </summary>
                <label className="arc3-prolog-inline-select-label">
                  <span>PATH</span>
                  <div className="arc3-prolog-browse-inputwrap">
                    <input
                      className="arc3-prolog-setup-inline-input"
                      type="text"
                      value={setup.stateDir ?? stateDirDefault}
                      placeholder="data/level_1/LEFT"
                      onChange={(event) => setSetupStateField(stackIndex, imageIndex, "stateDir", event.target.value)}
                    />
                    <button
                      type="button"
                      className="secondary arc3-prolog-browse-btn arc3-prolog-setup-scan"
                      title="Scan the files in this directory into the state.json editor"
                      onClick={() => void scanSetupStatePath(stackIndex, imageIndex, setup.stateDir ?? stateDirDefault)}
                    >scan</button>
                  </div>
                </label>
                <label className="arc3-prolog-inline-select-label">
                  <span>PROP_FILE</span>
                  <input
                    className="arc3-prolog-setup-inline-input"
                    type="text"
                    value={setup.stateFile ?? "state.json"}
                    placeholder="state.json"
                    onChange={(event) => setSetupStateField(stackIndex, imageIndex, "stateFile", event.target.value)}
                  />
                </label>
                <div className="arc3-prolog-setup-state-actions">
                  <button
                    type="button"
                    className="secondary arc3-prolog-setup-state-load"
                    onClick={() => void loadSetupStateJson(stackIndex, imageIndex, setup.stateDir ?? stateDirDefault, setup.stateFile ?? "state.json")}
                  >Load</button>
                  <button
                    type="button"
                    className="secondary arc3-prolog-setup-state-saveas"
                    onClick={() => void saveSetupStateJson(setup.stateFile ?? "state.json", setup.stateJson ?? "")}
                  >Save as..</button>
                </div>
                <textarea
                  className="arc3-prolog-setup-state-json"
                  value={setup.stateJson ?? ""}
                  placeholder="{ }"
                  spellCheck={false}
                  rows={8}
                  onChange={(event) => setSetupStateField(stackIndex, imageIndex, "stateJson", event.target.value)}
                />
              </details>
              <details className="arc3-prolog-setup-extra">
                <summary>BEFORE &amp; COMMAND</summary>
                <label className="arc3-prolog-inline-select-label">
                  <span>BEFORE</span>
                  <div className="arc3-prolog-browse-inputwrap">
                    <input
                      className="arc3-prolog-setup-inline-input"
                      type="text"
                      value={setup.beforeImage?.name || "../image.png"}
                      onChange={(event) => setBeforeImagePath(stackIndex, imageIndex, event.target.value)}
                    />
                    {renderSingleImageControls(`before:${setup.id}`, (path) => setBeforeImagePath(stackIndex, imageIndex, path))}
                  </div>
                </label>
                {renderSingleImageList(`before:${setup.id}`, (path) => setBeforeImagePath(stackIndex, imageIndex, path))}
                {setup.beforeImage?.dataUrl
                  ? <img className="arc3-prolog-preview" src={setup.beforeImage.dataUrl} alt={`${setup.label || `image_${imageIndex + 1}`} before image`} />
                  : null}
                <label className="arc3-prolog-inline-select-label">
                  <span>COMMAND</span>
                  <input
                    className="arc3-prolog-setup-inline-input"
                    type="text"
                    value={setup.command}
                    onChange={(event) => setSetupCommand(stackIndex, imageIndex, event.target.value)}
                  />
                </label>
              </details>
              <label className="arc3-prolog-inline-select-label">
                <span>AFTER</span>
                <div className="arc3-prolog-browse-inputwrap">
                  <input
                    className="arc3-prolog-setup-inline-input"
                    type="text"
                    value={setup.afterImage.name}
                    onChange={(event) => setImagePath(stackIndex, imageIndex, event.target.value)}
                  />
                  {renderSingleImageControls(`after:${setup.id}`, (path) => setImagePath(stackIndex, imageIndex, path))}
                </div>
              </label>
              {renderSingleImageList(`after:${setup.id}`, (path) => setImagePath(stackIndex, imageIndex, path))}
              {setup.afterImage.dataUrl
                ? <img className="arc3-prolog-preview" src={setup.afterImage.dataUrl} alt={`${setup.label || `image_${imageIndex + 1}`} image`} />
                : <div className="arc3-prolog-setup-preview-placeholder">No image</div>}
              {renderSetupCollectionGroup("objectImages", "OBJ_IMAGES", "OBJECT", "image", [...IMAGE_SUFFIXES], {
                defaultOpen: true,
                placeholder: `${pathPrefix}/obj*_*.png`,
              })}
              {renderSetupCollectionGroup("groupImages", "GRP_IMAGES", "GROUP", "image", [...IMAGE_SUFFIXES], {
                defaultOpen: false,
                placeholder: `${pathPrefix}/grp*_*.png`,
              })}
              {renderSetupCollectionGroup("subImages", "SUB_IMAGES", "SUB", "image", [...IMAGE_SUFFIXES], {
                defaultOpen: false,
                placeholder: `${pathPrefix}/*.png`,
                derivedCount: subimages.length,
                derived: subimages.length
                  ? <div className="arc3-prolog-setup-preview-grid">
                    {subimages.map((item) => <figure key={item.key}>
                      <figcaption>{item.label}</figcaption>
                      <img className="arc3-prolog-preview" src={item.value} alt={item.label} />
                    </figure>)}
                  </div>
                  : null,
              })}
              {renderSetupCollectionGroup("plFiles", "PL_FILES", "PL", "file", [".pl"], {
                defaultOpen: false,
                editable: true,
                placeholder: `${pathPrefix}/*.pl`,
              })}
              {renderSetupCollectionGroup("engFiles", "ENG_FILES", "ENG", "file", [".eng"], {
                defaultOpen: false,
                editable: true,
                placeholder: `${pathPrefix}/*eng*`,
              })}
              {renderSetupCollectionGroup("jsonFiles", "JSON_FILES", "JSON", "file", [".json"], {
                defaultOpen: false,
                editable: true,
                placeholder: `${pathPrefix}/*.json`,
              })}
              {renderSetupCollectionGroup("mettaFiles", "METTA_FILES", "METTA", "file", [".metta"], {
                defaultOpen: false,
                editable: true,
                placeholder: `${pathPrefix}/*.metta`,
              })}
              {renderSetupCollectionGroup("promptFiles", "PROMPT_FILES", "PROMPT", "file", [".prompt"], {
                defaultOpen: false,
                editable: true,
                placeholder: `${pathPrefix}/*.prompt`,
              })}
              {renderSetupCollectionGroup("unknownFiles", "UNKNOWN_FILES", "UNKNOWN", "file", [], {
                defaultOpen: false,
                editable: true,
                placeholder: `${pathPrefix}/*.*`,
                derivedCount: textFiles.length,
                derived: textFiles.length
                  ? <>{textFiles.map((item) => <details key={item.key}>
                    <summary>{item.label}</summary>
                    <pre className="arc3-prolog-prompt-text">{item.value}</pre>
                  </details>)}</>
                  : null,
              })}
            </ThreeStateAccordionMember>;
          })}
        </ThreeStateAccordionStack>,
      };
    },
    Arc3CombinedPrompt: () => ({
      value: `${COMBINED_PROMPT_PARTS.length} contract lines`,
      detail: "Exact combined prompt used for invocation",
      baseClass: "english-workflow-panel arc3-prolog-page-panel",
      scrollSize: "520px",
      content: <pre className="arc3-prolog-prompt-text">{JSON.stringify({ combined: COMBINED_PROMPT_PARTS }, null, 2)}</pre>,
    }),
    Arc3PromptRunner: () => ({
      value: anyRunning ? "Running…" : "Ready",
      detail: `${workspaceLabel} · ${visionModels.length} vision enabled`,
      baseClass: "english-workflow-panel arc3-prolog-page-panel",
      content: <section className="arc3-prolog-runner">
        <ThreeStateAccordionStack id="arc3-prolog-main-stack" controlsLabel="PROLOG">
          <ThreeStateAccordionMember
            stackId="arc3-prolog-main-stack"
            memberKey="shared-g"
            label="G · SHARED THING"
            value="Shared"
            detail="Global shared context"
            mode={modeFor("shared-g")}
            onChange={(mode) => setModeFor("shared-g", mode)}
            baseClass="english-workflow-panel arc3-prolog-page-panel"
            scrollSize="220px"
          >
            <small>{visionModels.length
              ? `Vision-capable models: ${visionModels.map((model) => model.label || model.id).join(", ")}`
              : "Vision-capable models: none currently enabled."}</small>
            <label className="arc3-prolog-inline-select-label">
              <span>PAGE MODEL</span>
              <select
                aria-label="Page model"
                value={pageModelId}
                onChange={(event) => setPageModelId(event.target.value)}
                title={`Effective: ${effectiveModelSummary(resolvePageModelId(), enabledModels)}`}
              >
                <option value={RUNNER_WORKSPACE_MODEL_SENTINEL}>&lt;Workspace Model&gt;</option>
                <option value={RUNNER_WORKBENCH_MODEL_SENTINEL}>&lt;Workbench Model&gt;</option>
                {enabledModels.map((model) => <option key={`page-model-${model.id}`} value={model.id}>
                  {modelOptionLabel(model)}
                </option>)}
              </select>
            </label>
            <small>Each stack is an independent race lane for comparing different vision models.</small>
            {modelSelectionMessage ? <small>{modelSelectionMessage}</small> : null}
          </ThreeStateAccordionMember>
          <ThreeStateAccordionMember
            stackId="arc3-prolog-main-stack"
            memberKey="all-stack"
            label="ALL-STACK"
            value={activeStackColumns.map((column) => column.key).join(" | ")}
            detail={`${activeStackColumns.length} stack column${activeStackColumns.length === 1 ? "" : "s"}`}
            mode={modeFor("all-stack")}
            onChange={(mode) => setModeFor("all-stack", mode)}
            baseClass="english-workflow-panel arc3-prolog-page-panel"
            scrollSize="calc(100vh - 320px)"
            accessories={<button type="button" className="secondary" onClick={() => void scanDataByName()} disabled={scanDataBusy}>
              {scanDataBusy ? "Scanning…" : "Scan Data"}
            </button>}
          >
            <div className="arc3-prolog-accordion-columns">
              {stackColumns.map((stack, stackIndex) => {
                const stackContainerId = `arc3-prolog-stack-${stack.key}`;
                const effectiveColumnModelId = resolveColumnModelId(stack);
                const stackSetups = stack.setups?.length ? stack.setups : defaultSetups(stack.key);
                const activeImageIndex = Math.max(0, Math.min(stack.selectedImageIndex ?? 0, Math.max(0, stackSetups.length - 1)));
                return <ThreeStateAccordionStack
                  key={`stack-${stack.key}`}
                  id={stackContainerId}
                  className="arc3-prolog-accordion-stack"
                  controlsLabel={`${stack.key}`}
                >
                  <div className="arc3-prolog-runner-toolbar">
                    <label className="arc3-prolog-inline-select-label">
                      <span>ACTIVE IMAGE</span>
                      <select
                        aria-label={`Active image for stack ${stack.key}`}
                        value={activeImageIndex}
                        onChange={(event) => selectImage(stackIndex, Number(event.target.value))}
                      >
                        {stackSetups.map((setup, imageIndex) => <option key={setup.id} value={imageIndex}>
                          {`${imageIndex + 1}. ${setup.label || `image_${imageIndex + 1}`}`}
                        </option>)}
                      </select>
                    </label>
                    <label className="arc3-prolog-inline-select-label">
                      <span>{`COLUMN MODEL (${stack.key})`}</span>
                      <select
                        aria-label={`Column model for stack ${stack.key}`}
                        value={stack.columnModelSelection}
                        title={`Effective: ${effectiveModelSummary(effectiveColumnModelId, enabledModels)}`}
                        onChange={(event) => setStackState(
                          stackIndex,
                          (previous) => ({ ...previous, columnModelSelection: event.target.value }),
                        )}
                      >
                        <option value={PAGE_MODEL_SENTINEL}>&lt;Page Model&gt;</option>
                        {enabledModels.map((model) => <option key={`column-model-${stack.key}-${model.id}`} value={model.id}>
                          {modelOptionLabel(model)}
                        </option>)}
                      </select>
                    </label>
                  </div>
                  {stack.runners.map((runner, runnerIndex) => {
                    const effectiveRunnerModelId = resolveRunnerModelId(stack, runner);
                    const effectiveValidatorModelId = resolveValidatorModelId(stack, runner);
                    const setups = stack.setups?.length ? stack.setups : defaultSetups(stack.key);
                    const setupIndex = Math.max(0, Math.min(runner.setupIndex || 0, Math.max(0, setups.length - 1)));
                    const activeSetup = setups[setupIndex];
                    const runnerDisplay = runnerDisplayId(pageDefinition.routeView, stack.key, runnerIndex);
                    const runnerRoleMode = runnerRole(pageDefinition.routeView, stack.key, runnerIndex);
                    const statusLabel = runner.running
                      ? (runner.currentRunMode === "primary"
                        ? "Running Primary"
                        : runner.currentRunMode === "until_exit"
                          ? `Running Until Exit ${validatorPromptDisplayName(pageDefinition.routeView, stack.key, runnerIndex, runner.validatorPromptName)}`
                          : `Running Loop ${validatorPromptDisplayName(pageDefinition.routeView, stack.key, runnerIndex, runner.validatorPromptName)}`)
                      : (runner.result || runner.rawResponse || runner.parsed ? "Ready" : "Not Run");
                    const currentIdentitiesContent = Array.isArray(runner.parsed?.current_identities)
                      ? JSON.stringify({ current_identities: runner.parsed?.current_identities || [] }, null, 2)
                      : "";
                    const loopFileItems: Array<{ key: string; label: string; kind: "image" | "text"; value: string }> = [];
                    const manyObjectImages = manyObjectImagesFromRunner(runner);
                    if (runnerRoleMode === "removal" && manyObjectImages.length) {
                      manyObjectImages.forEach((item) => {
                        loopFileItems.push({ key: item.key, label: item.label, kind: "image", value: item.value });
                      });
                    } else {
                      if (runner.removedObjectImage) {
                        loopFileItems.push({ key: "image_of_object_removed", label: "image_of_object_removed", kind: "image", value: runner.removedObjectImage });
                      }
                      if (runner.removedBackgroundImage) {
                        loopFileItems.push({ key: "image_without_object", label: "image_without_object", kind: "image", value: runner.removedBackgroundImage });
                      }
                    }
                    if (!manyObjectImages.length && !runner.removedObjectImage && !runner.removedBackgroundImage && runner.loopImageWithCircles) {
                      loopFileItems.push({ key: "image_with_circles", label: "image_with_circles", kind: "image", value: runner.loopImageWithCircles });
                    }
                    if (currentIdentitiesContent) {
                      loopFileItems.push({ key: "current_identities", label: "current_identities", kind: "text", value: currentIdentitiesContent });
                    }
                    const syntheticOutputItems: Array<{ key: string; label: string; kind: "image" | "text"; value: string }> = [];
                    if (runner.removedBackgroundImage) {
                      syntheticOutputItems.push({ key: "without_uncircled_objects", label: "without uncircled objects", kind: "image", value: runner.removedBackgroundImage });
                    } else if (runner.message.toLowerCase().includes("loop converged") || runner.message.includes("loop_complete")) {
                      syntheticOutputItems.push({ key: "without_uncircled_objects", label: "without uncircled objects", kind: "text", value: runner.message });
                    }
                    if (activeSetup?.afterImage?.dataUrl) {
                      const primaryName = (runner.primaryPromptName || "").toLowerCase();
                      if (primaryName.includes("remove") || runner.removedBackgroundImage || runner.removedObjectImage) {
                        syntheticOutputItems.push({ key: "image_with_objects", label: "image_with_objects", kind: "image", value: activeSetup.afterImage.dataUrl });
                      }
                    }
                    if (currentIdentitiesContent) {
                      syntheticOutputItems.push({ key: "current_identities", label: "current_identities", kind: "text", value: currentIdentitiesContent });
                    }
                    const primaryPromptNameOptions = dedupeStringList([
                      runner.primaryPromptName || "",
                      primaryPromptName(pageDefinition.routeView, stack.key, runnerIndex),
                      "circle_one_identity_at_a_time",
                      "remove_smallest_object",
                      "regenerated_identities_from_many_objects",
                      "remove_one_found_identity_per_pass",
                      `stack_${stack.key.toLowerCase()}${runnerDisplayOrdinal(pageDefinition.routeView, stack.key, runnerIndex)}_identity_pass`,
                    ]).filter(Boolean);
                    const validatorPromptNameOptions = dedupeStringList([
                      runner.validatorPromptName || "",
                      "no_uncircled_objects",
                      "no_objects",
                      "LOOP CONDITIONS PROMPT",
                      "validate_identity_pass_output",
                    ]).filter((option) => Boolean(option) && option !== VALIDATOR_PROMPT_DISABLED);
                    const setupBundleOptions = setups.map((setup, ordinal) => ({
                      value: `${ALL_SETUP_SOURCE_PREFIX}${ordinal + 1}`,
                      label: `${ALL_SETUP_SOURCE_PREFIX}${ordinal + 1} (${setup.label || `Setup${ordinal + 1}`})`,
                    }));
                    const tokenSourceOptions = dedupeSourceOptions([
                      { value: "X.Image1", label: "PARENT_IMAGE (this column)" },
                      { value: "X_COMMAND", label: "COMMAND (this column)" },
                      { value: "X.Image2", label: "CURRENT_IMAGE (this column)" },
                      { value: "X_SETUP_LABEL", label: "SETUP LABEL (this column, active setup)" },
                      { value: "X_SETUP_COMMAND", label: "SETUP COMMAND (this column, active setup)" },
                      { value: "X_SETUP_NOTE", label: "SETUP NOTE (this column, active setup)" },
                      { value: "X_SETUP_BEFORE_PATH", label: "SETUP BEFORE PATH (this column, active setup)" },
                      { value: "X_SETUP_AFTER_PATH", label: "SETUP AFTER PATH (this column, active setup)" },
                      { value: "X_SETUP_BEFORE_IMAGE", label: "SETUP BEFORE IMAGE (this column, active setup)" },
                      { value: "X_SETUP_AFTER_IMAGE", label: "SETUP AFTER IMAGE (this column, active setup)" },
                      ...activeStackColumns.flatMap((column) => ([
                        {
                          value: `${column.key}.Image1`,
                          label: `PARENT_IMAGE (${column.key})`,
                        },
                        {
                          value: `${column.key}_COMMAND`,
                          label: `COMMAND (${column.key})`,
                        },
                        {
                          value: `${column.key}.Image2`,
                          label: `CURRENT_IMAGE (${column.key})`,
                        },
                        {
                          value: `${column.key}_SETUP_LABEL`,
                          label: `SETUP LABEL (${column.key}, active setup)`,
                        },
                        {
                          value: `${column.key}_SETUP_COMMAND`,
                          label: `SETUP COMMAND (${column.key}, active setup)`,
                        },
                        {
                          value: `${column.key}_SETUP_NOTE`,
                          label: `SETUP NOTE (${column.key}, active setup)`,
                        },
                        {
                          value: `${column.key}_SETUP_BEFORE_PATH`,
                          label: `SETUP BEFORE PATH (${column.key}, active setup)`,
                        },
                        {
                          value: `${column.key}_SETUP_AFTER_PATH`,
                          label: `SETUP AFTER PATH (${column.key}, active setup)`,
                        },
                        {
                          value: `${column.key}_SETUP_BEFORE_IMAGE`,
                          label: `SETUP BEFORE IMAGE (${column.key}, active setup)`,
                        },
                        {
                          value: `${column.key}_SETUP_AFTER_IMAGE`,
                          label: `SETUP AFTER IMAGE (${column.key}, active setup)`,
                        },
                      ])),
                      ...stackColumns.flatMap((columnState) => (
                        columnState.runners.map((_, index) => ({
                          value: `${columnState.key}_${index + 1}_PROMPT`,
                          label: `PROMPT (${runnerDisplayId(pageDefinition.routeView, columnState.key, index)})`,
                        }))
                      )),
                      ...stackColumns.flatMap((columnState) => (
                        (columnState.setups?.length ? columnState.setups : defaultSetups(columnState.key)).flatMap((_, setupOrdinal) => ([
                          {
                            value: `${columnState.key}_SETUP${setupOrdinal + 1}_LABEL`,
                            label: `SETUP ${setupOrdinal + 1} LABEL (${columnState.key})`,
                          },
                          {
                            value: `${columnState.key}_SETUP${setupOrdinal + 1}_COMMAND`,
                            label: `SETUP ${setupOrdinal + 1} COMMAND (${columnState.key})`,
                          },
                          {
                            value: `${columnState.key}_SETUP${setupOrdinal + 1}_NOTE`,
                            label: `SETUP ${setupOrdinal + 1} NOTE (${columnState.key})`,
                          },
                          {
                            value: `${columnState.key}_SETUP${setupOrdinal + 1}_BEFORE_PATH`,
                            label: `SETUP ${setupOrdinal + 1} BEFORE PATH (${columnState.key})`,
                          },
                          {
                            value: `${columnState.key}_SETUP${setupOrdinal + 1}_AFTER_PATH`,
                            label: `SETUP ${setupOrdinal + 1} AFTER PATH (${columnState.key})`,
                          },
                          {
                            value: `${columnState.key}_SETUP${setupOrdinal + 1}_BEFORE_IMAGE`,
                            label: `SETUP ${setupOrdinal + 1} BEFORE IMAGE (${columnState.key})`,
                          },
                          {
                            value: `${columnState.key}_SETUP${setupOrdinal + 1}_AFTER_IMAGE`,
                            label: `SETUP ${setupOrdinal + 1} AFTER IMAGE (${columnState.key})`,
                          },
                        ]))
                      )),
                      ...stackColumns.flatMap((columnState) => (
                        (columnState.setups || []).flatMap((setup, setupOrdinal) => (
                          [
                            ...(setup.analysis?.subimages || []),
                            ...(setup.analysis?.textFiles || []),
                          ].map((item) => ({
                            value: `setup-file:${setup.id}:${item.key}`,
                            label: `SETUP ${setupOrdinal + 1} FILE ${item.label} (${columnState.key})`,
                          }))
                        ))
                      )),
                    ]);
                    const otherColumnsAC = activeStackColumns
                      .map((column) => column.key)
                      .filter((columnKey) => columnKey !== stack.key);
                    const otherColumnsCA = [...otherColumnsAC].reverse();
                    const onePassOtherColumnSources = (columnOrder: StackKey[]) => dedupeStringList(columnOrder.flatMap((columnKey) => {
                      const columnState = stackColumns.find((candidate) => candidate.key === columnKey);
                      const promptTokens = (columnState?.runners || []).map((_, index) => `${columnKey}_${index + 1}_PROMPT`);
                      return [
                        `${columnKey}.Image1`,
                        `${columnKey}.Image2`,
                        `${columnKey}_COMMAND`,
                        `${columnKey}_SETUP_LABEL`,
                        `${columnKey}_SETUP_COMMAND`,
                        `${columnKey}_SETUP_NOTE`,
                        `${columnKey}_SETUP_BEFORE_PATH`,
                        `${columnKey}_SETUP_AFTER_PATH`,
                        `${columnKey}_SETUP_BEFORE_IMAGE`,
                        `${columnKey}_SETUP_AFTER_IMAGE`,
                        ...promptTokens,
                      ];
                    }));
                    const filesSourceOptions = dedupeSourceOptions([
                      ...setupBundleOptions,
                      { value: ALL_FIELDS_ABOVE_SOURCE, label: ALL_FIELDS_ABOVE_SOURCE },
                      { value: ALL_FIELDS_OTHER_AC_SOURCE, label: ALL_FIELDS_OTHER_AC_SOURCE },
                      { value: ALL_FIELDS_OTHER_CA_SOURCE, label: ALL_FIELDS_OTHER_CA_SOURCE },
                      { value: "none", label: "None" },
                      { value: "latest:this", label: `Latest generated files (this stack ${stack.key})` },
                      { value: "latest:any", label: "Latest generated files (any stack)" },
                      ...activeStackColumns.map((column) => ({
                        value: `latest:stack:${column.key}`,
                        label: `Latest generated files (stack ${column.key})`,
                      })),
                      ...outputHistory.map((entry) => ({
                        value: `history:${entry.id}`,
                        label: `Generated set ${entry.id} (${entry.runnerId})`,
                      })),
                      ...outputHistory.flatMap((entry) => (
                        outputFileRows(entry.parsed).map((row) => ({
                          value: `history-file:${entry.id}:${row.key}`,
                          label: `Generated file ${entry.id}.${row.label} (${entry.runnerId})`,
                        }))
                      )),
                      ...runnerOutputOptions.map((option) => ({
                        value: `runner:${option.id}`,
                        label: option.label,
                      })),
                      ...runnerOutputOptions.flatMap((option) => (
                        outputFileRows(option.runner.parsed).map((row) => ({
                          value: `file:${option.id}:${row.key}`,
                          label: `Latest file ${option.id}.${row.label}`,
                        }))
                      )),
                      ...tokenSourceOptions,
                    ]);
                    const normalizedSelection = filesSourceOptions.some((option) => option.value === runner.filesSourceSelection)
                      ? runner.filesSourceSelection
                      : (filesSourceOptions[0]?.value || "none");
                    const filesSourceLabelByValue = new Map(filesSourceOptions.map((option) => [option.value, option.label]));
                    const expandableFilesSourceIds = filesSourceOptions
                      .map((option) => option.value)
                      .filter((value) => value !== "none"
                        && value !== ALL_FIELDS_ABOVE_SOURCE
                        && value !== ALL_FIELDS_OTHER_AC_SOURCE
                        && value !== ALL_FIELDS_OTHER_CA_SOURCE);
                    const otherColumnsACOnceIds = onePassOtherColumnSources(otherColumnsAC);
                    const otherColumnsCAOnceIds = onePassOtherColumnSources(otherColumnsCA);
                    return <ThreeStateAccordionMember
                      key={`runner-${stack.key}-${runnerIndex}`}
                      stackId={stackContainerId}
                      memberKey={`runner-${runnerDisplay}`}
                      label={`RUNNER ${runnerDisplay}`}
                      value={statusLabel}
                      detail={runner.result ? `${runner.result.inputTokens ?? 0}/${runner.result.outputTokens ?? 0} tokens` : "Awaiting run"}
                      mode={modeFor(`runner-${runnerDisplay}`)}
                      onChange={(mode) => setModeFor(`runner-${runnerDisplay}`, mode)}
                      baseClass="english-workflow-panel arc3-prolog-page-panel"
                      scrollSize="520px"
                    >
                      {(() => {
                        return <label className="arc3-prolog-inline-select-label arc3-prolog-inline-composite-label">
                          <span>INPUT_FILES</span>
                          <div className="arc3-prolog-files-source-picker">
                            <select
                              aria-label={`Files input source selector for ${runnerDisplay}`}
                              value={normalizedSelection}
                              onChange={(event) => setRunnerState(
                                stackIndex,
                                runnerIndex,
                                (previous) => ({ ...previous, filesSourceSelection: event.target.value }),
                              )}
                            >
                              {filesSourceOptions.map((option) => <option key={`files-source-${option.value}`} value={option.value}>
                                {option.label}
                              </option>)}
                            </select>
                            <button
                              type="button"
                              className="secondary"
                              aria-label={`Add files source for ${runnerDisplay}`}
                              onClick={() => setRunnerState(
                                stackIndex,
                                runnerIndex,
                                (previous) => {
                                  const candidate = (filesSourceOptions.some((option) => option.value === previous.filesSourceSelection)
                                    ? previous.filesSourceSelection
                                    : (filesSourceOptions[0]?.value || "none")).trim();
                                  if (!candidate) return previous;
                                  if (candidate === ALL_FIELDS_ABOVE_SOURCE) {
                                    const expanded = Array.from(new Set([...previous.filesSourceIds, ...expandableFilesSourceIds]));
                                    return { ...previous, filesSourceIds: expanded };
                                  }
                                  if (candidate === ALL_FIELDS_OTHER_AC_SOURCE) {
                                    const expanded = Array.from(new Set([...previous.filesSourceIds, ...otherColumnsACOnceIds]));
                                    return { ...previous, filesSourceIds: expanded };
                                  }
                                  if (candidate === ALL_FIELDS_OTHER_CA_SOURCE) {
                                    const expanded = Array.from(new Set([...previous.filesSourceIds, ...otherColumnsCAOnceIds]));
                                    return { ...previous, filesSourceIds: expanded };
                                  }
                                  if (candidate.toLowerCase() === "none" || previous.filesSourceIds.includes(candidate)) return previous;
                                  return { ...previous, filesSourceIds: [...previous.filesSourceIds, candidate] };
                                },
                              )}
                            >
                              +
                            </button>
                            <button
                              type="button"
                              className="secondary"
                              aria-label={`Remove files source for ${runnerDisplay}`}
                              onClick={() => setRunnerState(
                                stackIndex,
                                runnerIndex,
                                (previous) => {
                                  const candidate = (filesSourceOptions.some((option) => option.value === previous.filesSourceSelection)
                                    ? previous.filesSourceSelection
                                    : (filesSourceOptions[0]?.value || "none")).trim();
                                  if (!candidate) return previous;
                                  const next = previous.filesSourceIds.filter((source) => source !== candidate);
                                  return { ...previous, filesSourceIds: next };
                                },
                              )}
                            >
                              -
                            </button>
                            <button
                              type="button"
                              className="secondary"
                              aria-label={`Clear files sources for ${runnerDisplay}`}
                              onClick={() => setRunnerState(
                                stackIndex,
                                runnerIndex,
                                (previous) => ({ ...previous, filesSourceIds: [] }),
                              )}
                            >
                              Clear
                            </button>
                          </div>
                          {runner.filesSourceIds.length
                            ? <div className="arc3-prolog-selected-source-chips">
                              {runner.filesSourceIds.map((sourceId) => <button
                                key={`selected-source-${runnerDisplay}-${sourceId}`}
                                type="button"
                                className="secondary arc3-prolog-source-chip"
                                title={filesSourceLabelByValue.get(sourceId) || sourceId}
                                onClick={() => setRunnerState(
                                  stackIndex,
                                  runnerIndex,
                                  (previous) => ({
                                    ...previous,
                                    filesSourceIds: previous.filesSourceIds.filter((item) => item !== sourceId),
                                  }),
                                )}
                              >
                                {displayFieldToken(sourceId)} [x]
                              </button>)}
                            </div>
                            : <small>Selected: none</small>}
                        </label>;
                      })()}
                      <label className="arc3-prolog-inline-select-label">
                        <span>PRIMARY_MODEL</span>
                        <select
                          aria-label={`Model for stack ${runnerDisplay}`}
                          value={runner.selectedModelId}
                          title={`Effective: ${effectiveModelSummary(effectiveRunnerModelId, enabledModels)} | Source: ${runnerModelSelectionLabel(runner.selectedModelId)}`}
                          onChange={(event) => setRunnerState(stackIndex, runnerIndex, (previous) => ({ ...previous, selectedModelId: event.target.value }))}
                        >
                          <option value={COLUMN_MODEL_SENTINEL}>&lt;Column Model&gt;</option>
                          <option value={RUNNER_WORKSPACE_MODEL_SENTINEL}>&lt;Workspace Model&gt;</option>
                          <option value={RUNNER_WORKBENCH_MODEL_SENTINEL}>&lt;Workbench Model&gt;</option>
                          {enabledModels.map((model) => <option key={model.id} value={model.id}>{modelOptionLabel(model)}</option>)}
                        </select>
                      </label>
                      <label className="arc3-prolog-inline-select-label">
                        <span>LOOP_MODEL</span>
                        <select
                          aria-label={`Validator model for stack ${runnerDisplay}`}
                          value={runner.validatorModelId}
                          title={`Effective: ${effectiveModelSummary(effectiveValidatorModelId, enabledModels)} | Source: ${runnerModelSelectionLabel(runner.validatorModelId)}`}
                          onChange={(event) => setRunnerState(stackIndex, runnerIndex, (previous) => ({ ...previous, validatorModelId: event.target.value }))}
                        >
                          <option value={RUNNER_VALIDATOR_PRIMARY_MODEL}>&lt;Runner Model&gt;</option>
                          <option value={RUNNER_VALIDATOR_DISABLED}>Disabled</option>
                          <option value={COLUMN_MODEL_SENTINEL}>&lt;Column Model&gt;</option>
                          <option value={RUNNER_WORKSPACE_MODEL_SENTINEL}>&lt;Workspace Model&gt;</option>
                          <option value={RUNNER_WORKBENCH_MODEL_SENTINEL}>&lt;Workbench Model&gt;</option>
                          {enabledModels.map((model) => <option key={`validator-${runnerDisplay}-${model.id}`} value={model.id}>
                            {modelOptionLabel(model)}
                          </option>)}
                        </select>
                      </label>
                      <div className="arc3-prolog-stack-actions">
                        <small>{`Setup pointer: ${activeSetup?.label || "Setup1"} (${setupIndex + 1}/${setups.length})`}</small>
                        <button
                          type="button"
                          className="secondary"
                          disabled={runner.running || setupIndex >= setups.length - 1}
                          onClick={() => incrementRunnerSetup(stackIndex, runnerIndex)}
                        >
                          Next Setup
                        </button>
                      </div>
                      <details className="arc3-prolog-prompt-collapsible">
                        <summary className="arc3-prolog-prompt-summary">
                          <span>|&gt; Primary Prompt -</span>
                          <select
                            aria-label={`Primary prompt name for ${runnerDisplay}`}
                            value={runner.primaryPromptName || primaryPromptName(pageDefinition.routeView, stack.key, runnerIndex)}
                            onPointerDown={(event) => event.stopPropagation()}
                            onClick={(event) => event.stopPropagation()}
                            onChange={(event) => setRunnerState(
                              stackIndex,
                              runnerIndex,
                              (previous) => ({ ...previous, primaryPromptName: event.target.value }),
                            )}
                          >
                            {primaryPromptNameOptions.map((option) => <option key={`primary-prompt-name-${runnerDisplay}-${option}`} value={option}>
                              {option}
                            </option>)}
                          </select>
                        </summary>
                        <textarea
                          className="arc3-prolog-prompt-editor"
                          value={runner.promptText}
                          onChange={(event) => setRunnerState(stackIndex, runnerIndex, (previous) => ({ ...previous, promptText: event.target.value }))}
                          rows={7}
                        />
                      </details>
                      <details className="arc3-prolog-prompt-collapsible">
                        <summary className="arc3-prolog-prompt-summary">
                          <span>|&gt; Loop/Validate Prompt -</span>
                          <select
                            aria-label={`Validator prompt name for ${runnerDisplay}`}
                            value={runner.validatorPromptName || validatorPromptName(pageDefinition.routeView, stack.key, runnerIndex)}
                            onPointerDown={(event) => event.stopPropagation()}
                            onClick={(event) => event.stopPropagation()}
                            onChange={(event) => setRunnerState(
                              stackIndex,
                              runnerIndex,
                              (previous) => ({ ...previous, validatorPromptName: event.target.value }),
                            )}
                          >
                            <option value={VALIDATOR_PROMPT_DISABLED}>&lt;disabled&gt;</option>
                            {validatorPromptNameOptions.map((option) => <option key={`validator-prompt-name-${runnerDisplay}-${option}`} value={option}>
                              {option}
                            </option>)}
                          </select>
                        </summary>
                        <textarea
                          className="arc3-prolog-prompt-editor"
                          value={runner.validatorPromptText}
                          onChange={(event) => setRunnerState(
                            stackIndex,
                            runnerIndex,
                            (previous) => ({ ...previous, validatorPromptText: event.target.value }),
                          )}
                          rows={5}
                        />
                      </details>
                      <div className="arc3-prolog-loop-limits arc3-prolog-runner-limits-line" title="Loop limits">
                        <span>LIMITS:</span>
                        <span className="arc3-prolog-loop-limit-item">
                          <span>max_primary_secs</span>
                          <span>[</span>
                          <input
                            type="number"
                            min={10}
                            max={3600}
                            value={runner.maxPrimarySeconds}
                            onChange={(event) => setRunnerState(
                              stackIndex,
                              runnerIndex,
                              (previous) => ({
                                ...previous,
                                maxPrimarySeconds: Math.max(10, Number.parseInt(event.target.value || "10", 10) || 10),
                              }),
                            )}
                          />
                          <span>]</span>
                        </span>
                        <span className="arc3-prolog-loop-limit-item">
                          <span>max_loop_secs</span>
                          <span>[</span>
                          <input
                            type="number"
                            min={10}
                            max={3600}
                            value={runner.autoLoopMaxSeconds}
                            onChange={(event) => setRunnerState(
                              stackIndex,
                              runnerIndex,
                              (previous) => ({
                                ...previous,
                                autoLoopMaxSeconds: Math.max(10, Number.parseInt(event.target.value || "10", 10) || 10),
                              }),
                            )}
                          />
                          <span>]</span>
                        </span>
                        <span className="arc3-prolog-loop-limit-item">
                          <span>max_iterations</span>
                          <span>[</span>
                          <input
                            type="number"
                            min={1}
                            max={200}
                            value={runner.autoLoopMaxIterations}
                            onChange={(event) => setRunnerState(
                              stackIndex,
                              runnerIndex,
                              (previous) => ({
                                ...previous,
                                autoLoopMaxIterations: Math.max(1, Number.parseInt(event.target.value || "1", 10) || 1),
                              }),
                            )}
                          />
                          <span>]</span>
                        </span>
                      </div>
                      <div className="arc3-prolog-stack-actions">
                        <button
                          type="button"
                          className="primary"
                          disabled={runner.running || !stack.beforeImage || !stack.afterImage || !effectiveRunnerModelId}
                          onClick={() => void runPrompt(stackIndex, runnerIndex, "primary")}
                        >
                          {runner.running ? "Running…" : `Run ${runnerDisplay} Primary`}
                        </button>
                        <button
                          type="button"
                          className="secondary"
                          disabled={!runner.running}
                          onClick={() => cancelPrompt(stackIndex, runnerIndex)}
                        >
                          Cancel
                        </button>
                        <button
                          type="button"
                          className="secondary"
                          disabled={runner.running || !stack.beforeImage || !stack.afterImage || !effectiveRunnerModelId}
                          onClick={() => void runPrompt(stackIndex, runnerIndex, "loop")}
                        >
                          Run Loop
                        </button>
                        <button
                          type="button"
                          className="secondary"
                          disabled={runner.running || !stack.beforeImage || !stack.afterImage || !effectiveRunnerModelId}
                          onClick={() => void runPrompt(stackIndex, runnerIndex, "until_exit")}
                        >
                          Run Until Exit
                        </button>
                      </div>
                      {isRegeneratedIdentitiesRunner(pageDefinition.routeView, stack.key, runnerIndex) && (
                        <label
                          className="arc3-b1b2-writeback-toggle"
                          style={{ display: "flex", alignItems: "center", gap: "6px", margin: "6px 0" }}
                          title="Experimental: when this REGENERATOR run finishes, overwrite the GUESSER runner's identity list with this result so the next run starts warm."
                        >
                          <input
                            type="checkbox"
                            checked={replaceGuesserOnFinish}
                            onChange={(event) => setReplaceGuesserOnFinish(event.target.checked)}
                          />
                          <span>Replace GUESSER list with this result on finish</span>
                        </label>
                      )}
                      <details className="arc3-prolog-stack-output">
                        <summary>LOOP_FILES</summary>
                        {loopFileItems.length
                          ? loopFileItems.map((item) => <details key={`loop-files-${runnerDisplay}-${item.key}`} open>
                            <summary>{item.label}</summary>
                            {item.kind === "image"
                              ? <img className="arc3-prolog-preview" src={item.value} alt={item.label} />
                              : <pre>{item.value}</pre>}
                          </details>)
                          : <small>No loop files yet.</small>}
                      </details>
                      <small>{runner.message}</small>
                      {runner.removalValidationSummary ? <small>{runner.removalValidationSummary}</small> : null}
                      {runner.error && <p className="arc3-prolog-error">{runner.error}</p>}
                      {runner.result && <div className="arc3-prolog-meta">
                        <span>{runner.result.backendId || "resolved backend"} · {runner.result.modelId || effectiveRunnerModelId}</span>
                        <span>{runner.result.inputTokens ?? 0}/{runner.result.outputTokens ?? 0} tokens · {runner.result.latencyMs ?? 0} ms</span>
                      </div>}
                      <details className="arc3-prolog-stack-output">
                        <summary>RAW_PARSED</summary>
                        <details open>
                          <summary>raw</summary>
                          <pre>{runner.rawResponse || "No raw response yet."}</pre>
                        </details>
                        <details open>
                          <summary>parsed</summary>
                          <pre>{runner.parsed ? JSON.stringify(runner.parsed, null, 2) : "No parsed output yet."}</pre>
                        </details>
                      </details>
                      {(runner.removedObjectImage || runner.removedBackgroundImage) && <details open className="arc3-prolog-stack-output">
                        <summary>REMOVAL_IMAGES</summary>
                        {runner.removedIdentityId ? <small>Removed identity: {runner.removedIdentityId}</small> : null}
                        <div className="arc3-prolog-removal-images">
                          {isRemovalDiscoveryRunner(pageDefinition.routeView, stack.key, runnerIndex)
                            ? manyObjectImagesFromRunner(runner).map((item) => <figure key={`stack-many-${stack.key}-${runnerIndex}-${item.key}`}>
                              <figcaption>{item.label}</figcaption>
                              <img className="arc3-prolog-preview" src={item.value} alt={item.label} />
                            </figure>)
                            : <>
                              {runner.removedObjectImage && <figure>
                                <figcaption>Removed object image</figcaption>
                                <img className="arc3-prolog-preview" src={runner.removedObjectImage} alt="Removed object" />
                              </figure>}
                              {runner.removedBackgroundImage && <figure>
                                <figcaption>Background without object</figcaption>
                                <img className="arc3-prolog-preview" src={runner.removedBackgroundImage} alt="Background without removed object" />
                              </figure>}
                            </>}
                        </div>
                      </details>}
                      <details className="arc3-prolog-stack-output">
                        <summary>OUTPUT_FILES</summary>
                        {syntheticOutputItems.map((item) => <details key={`stack-output-synth-${stack.key}-${runnerIndex}-${item.key}`} open>
                          <summary>{item.label}</summary>
                          {item.kind === "image"
                            ? <img className="arc3-prolog-preview" src={item.value} alt={item.label} />
                            : <pre>{item.value}</pre>}
                        </details>)}
                        {outputFileRows(runner.parsed).length
                          ? outputFileRows(runner.parsed).map((row) => <details key={`stack-inline-${stack.key}-${runnerIndex}-${row.key}`} open>
                            <summary>{row.label}</summary>
                            <pre>{row.content}</pre>
                          </details>)
                          : <small>No parsed output files yet.</small>}
                      </details>
                    </ThreeStateAccordionMember>;
                  })}
                </ThreeStateAccordionStack>;
              })}
            </div>
          </ThreeStateAccordionMember>
          <ThreeStateAccordionMember
            stackId="arc3-prolog-main-stack"
            memberKey="history-h"
            label={`H · ADDRESSABLE HISTORY (${outputHistory.length})`}
            value={`${outputHistory.length} entries`}
            detail="Addressable generated output snapshots"
            mode={modeFor("history-h")}
            onChange={(mode) => setModeFor("history-h", mode)}
            baseClass="english-workflow-panel arc3-prolog-page-panel"
            scrollSize="420px"
          >
            <pre>{JSON.stringify(outputHistory.map((entry) => ({
              id: entry.id,
              runnerId: entry.runnerId,
              createdAt: entry.createdAt,
              address_runner: `history:${entry.id}`,
              address_keys: Object.keys((entry.parsed || {}) as Record<string, unknown>).map((key) => `history-file:${entry.id}:${key}`),
            })), null, 2)}</pre>
          </ThreeStateAccordionMember>
        </ThreeStateAccordionStack>
      </section>,
    }),
    Arc3PrologOutputs: () => ({
      value: selectedRunner?.parsed ? "Parsed JSON contract" : "Awaiting parsed response",
      detail: selectedRunner?.parsed ? `${outputFileRows(selectedRunner.parsed).length} output file(s)` : "No parsed output yet",
      baseClass: "english-workflow-panel arc3-prolog-page-panel",
      scrollSize: "680px",
      content: <section className="arc3-prolog-outputs">
        <label className="arc3-prolog-inline-select-label">
          <span>OUTPUT RUNNER</span>
          <select
            value={selectedOutput?.id || "A1"}
            title={`Selected runner: ${selectedOutput?.id || "A1"}`}
            onChange={(event) => setSelectedOutputId(event.target.value)}
          >
            {runnerOutputOptions.map((option) => <option key={option.id} value={option.id}>{option.label}</option>)}
          </select>
        </label>
        <details>
          <summary>H · Addressable History ({outputHistory.length})</summary>
          <pre>{JSON.stringify(outputHistory.map((entry) => ({
            id: entry.id,
            runnerId: entry.runnerId,
            createdAt: entry.createdAt,
            address_runner: `history:${entry.id}`,
            address_keys: Object.keys((entry.parsed || {}) as Record<string, unknown>).map((key) => `history-file:${entry.id}:${key}`),
            keys: Object.keys((entry.parsed || {}) as Record<string, unknown>),
          })), null, 2)}</pre>
        </details>
        {outputFileRows(selectedRunner?.parsed).length
          ? outputFileRows(selectedRunner?.parsed).map((row) => <details key={row.key} open>
            <summary>{row.label}</summary>
            <pre>{row.content}</pre>
          </details>)
          : <small>No parsed output files yet.</small>}
        {(selectedRunner?.removedObjectImage || selectedRunner?.removedBackgroundImage) && <details open>
          <summary>Removal Images</summary>
          {selectedRunner?.removedIdentityId ? <small>Removed identity: {selectedRunner.removedIdentityId}</small> : null}
          <div className="arc3-prolog-removal-images">
            {(selectedOutput?.id === "REMOVER"
              ? manyObjectImagesFromRunner(selectedRunner).map((item) => <figure key={`selected-many-${item.key}`}>
                <figcaption>{item.label}</figcaption>
                <img className="arc3-prolog-preview" src={item.value} alt={item.label} />
              </figure>)
              : <>
                {selectedRunner?.removedObjectImage && <figure>
                  <figcaption>Removed object image</figcaption>
                  <img className="arc3-prolog-preview" src={selectedRunner.removedObjectImage} alt="Removed object" />
                </figure>}
                {selectedRunner?.removedBackgroundImage && <figure>
                  <figcaption>Background without object</figcaption>
                  <img className="arc3-prolog-preview" src={selectedRunner.removedBackgroundImage} alt="Background without removed object" />
                </figure>}
              </>)}
          </div>
        </details>}
      </section>,
    }),
    Arc3RawResponse: () => ({
      value: selectedRunner?.rawResponse ? "Raw model response captured" : "No response yet",
      detail: selectedRunner?.debugLogPath ? "Shows raw model text and invocation trace log" : "Shows exact model text if parse fails",
      baseClass: "english-workflow-panel arc3-prolog-page-panel",
      scrollSize: "520px",
      content: <section className="arc3-prolog-right-column">
        <label className="arc3-prolog-inline-select-label">
          <span>RAW RUNNER</span>
          <select
            value={selectedOutput?.id || "A1"}
            title={`Selected runner: ${selectedOutput?.id || "A1"}`}
            onChange={(event) => setSelectedOutputId(event.target.value)}
          >
            {runnerOutputOptions.map((option) => <option key={option.id} value={option.id}>{option.label}</option>)}
          </select>
        </label>
        <pre className="arc3-prolog-raw">{selectedRunner?.rawResponse || "Run a runner to view raw response text."}</pre>
        {selectedRunner?.debugLogPath && <details open className="arc3-prolog-debug-log">
          <summary>Invocation log: {selectedRunner.debugLogPath}</summary>
          <pre className="arc3-prolog-raw">{selectedRunner.debugLog || "No debug log content yet."}</pre>
        </details>}
      </section>,
    }),
    ResourceSourceEditor: () => ({
      value: `${pageDefinition.id}.workflow_page.json`,
      detail: "Filesystem page specification",
      baseClass: "english-workflow-panel arc3-prolog-page-panel",
      scrollSize: "520px",
      content: <WorkflowPageSourceEditor workspaceId={workspaceId} pageId={pageDefinition.id} disabled={anyRunning} onSaved={onPageDefinitionSaved} />,
    }),
  };

  return <WorkflowPageHost
    definition={pageDefinition}
    componentRegistry={registry}
    pageClassName="english-workflow-page arc3-b1b2-page"
    columnsRef={columnsElRef}
    columnsStyle={{ position: "relative", ...(columnTemplate ? { gridTemplateColumns: columnTemplate } : {}) }}
    columnsOverlay={resizerLefts.length ? <div
      className="arc3-b1b2-col-resizers"
      style={{ position: "absolute", top: 0, left: 0, height: resizerHeight || "100%", width: 0, pointerEvents: "none" }}
      aria-hidden="true"
    >
      {resizerLefts.map((left, index) => <div
        key={index}
        className="arc3-b1b2-col-resizer"
        style={{ position: "absolute", top: 0, height: "100%", left: left - 4, width: 8, cursor: "col-resize", pointerEvents: "auto" }}
        title="Drag to resize columns"
        onPointerDown={(event) => startColumnResize(index, event)}
      />)}
    </div> : null}
  />;
}
