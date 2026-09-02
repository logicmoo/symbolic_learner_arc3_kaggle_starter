"""Headless Video Import pipeline runner.

The scene-object extraction pipeline (describe -> group -> outline -> extract)
historically lived entirely in the browser page (VideoImportPage.tsx). That made
it fragile: the tab froze under scheduler churn, multiple tabs clobbered each
other's saves, and results were lost on refresh because they only existed in
React state.

This module moves the *orchestration* to the server so it can run without any
GUI. It reads the same ``page_state`` the page renders, calls the shared model
invoke primitive (exactly what ``POST .../models/{id}/invoke`` uses), and
persists results back into the ``memberInventories`` shard. The browser becomes
an optional viewer that polls status.

It is importable (used by control endpoints in ``video_import_api``) and also
runnable head-less from the command line::

    python -m video_import_pipeline --workspace arc3_random_player --stage describe

Only the describe stage is implemented here so far; outline and extract are
added incrementally.
"""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import re
import sys
import threading
import time
import traceback
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from arc3_play_api import _workspace_root
from operation_resolution import _model_execution_parameters
from policy_api import _resolved_model_records
from workflow_providers import _llm_complete

# Page-state helpers live in video_import_api. Importing them here is safe
# because video_import_api never imports this module at top level (its control
# endpoints import it lazily at call time), so there is no import cycle.
from video_import_api import (
    _atomic_json_write,
    _imports_root,
    _page_state_lock,
    _save_page_state_payload,
    get_page_state,
    member_cut,
    outline_verification,
)

# --------------------------------------------------------------------------- #
# Prompts (ported verbatim from VideoImportPage.tsx defaults)                  #
# --------------------------------------------------------------------------- #

MEMBER_INVENTORY_GOALS: dict[str, str] = {
    "any": "List distinct extractable people, characters, creatures, objects, and text/sign elements.",
    "faces": "List each distinct extractable face.",
    "characters": "List each distinct extractable person, character, or creature.",
    "objects": "List each distinct extractable inanimate object.",
    "text": "List each distinct extractable piece of text or signage.",
}

DEFAULT_MEMBER_DESCRIPTION_PROMPT = "\n".join([
    "SCENE OBJECTS TEXTUAL DESCRIPTION.",
    "{{subjectContext}}",
    "Describe this image, list only its direct visually separable child objects, then group those objects into ordered parallel-extraction waves.",
    "{{goal}}",
    "List every distinct extractable thing you can identify. Do not return polygons or coordinates in this stage.",
    "Grouping: objects in the same group can be lifted in parallel (none covers, contains, or is part/parent of another in that group). Group 1 is the fully-visible foreground; each later group becomes liftable only after earlier groups are removed. Every listed thing appears in exactly one group by its exact name.",
    "{{alreadyExtracted}}",
    'Answer ONLY with JSON: {"description":"scene description","things":[{"name":"short unique name","description":"visual identity and location"}],"groups":[["exact thing name",...],...]}',
])

_DEFAULT_SUBJECT_CONTEXT = "This is a root input image. List its top-level objects."


DEFAULT_MEMBER_OUTLINER_PROMPT = "\n".join([
    "OBJECT OUTLINER.",
    "Outline exactly ONE object in the attached current scene. Planner has already selected its order position.",
    "Do not outline, include, or remove any other listed object.",
    "TEXTUAL DESCRIPTION:",
    "{{textualDescription}}",
    "PLANNER-SELECTED OBJECT: {{nextObjectName}}",
    "Object description: {{nextObjectDescription}}",
    "Planner position: {{plannerPosition}} of {{plannerTotal}}",
    "PLANNER-DECLARED CONTACT AND OCCLUSION RELATIONSHIPS FOR THIS OBJECT:",
    "{{plannerRelationships}}",
    "OUTLINE SOURCE IMAGE: {{outlineImage}}",
    "PIXEL COORDINATE SPACE: width={{imageWidth}}, height={{imageHeight}}. Use x=0..{{maxX}} and y=0..{{maxY}} only.",
    "Trace the named object's visible silhouette at pixel-edge precision in THIS current image.",
    "Explicitly include only pixels belonging to the named object and exclude adjacent body parts, neighboring objects, shadows, and background.",
    "Preserve disconnected visible parts as separate polygons and enclosed transparent gaps as holes. Respect occluders: trace only the visible contour and never invent hidden pixels.",
    "For parts such as a character's chest, exclude the head, arms, hands, lower body, clothing outside the chest, and background unless truly part of the named object.",
    "Also describe the contour clockwise and as normalized 0..1000 move/line commands in Turtle form for inspection.",
    'Answer ONLY with JSON: {"name":"{{nextObjectName}}","polygons":[[[x,y],...]],"holes":[[[x,y],...]],"traceClockwise":["start at ...","follow edge ...","return to start"],"traceTurtle":[{"op":"move","x":0,"y":0},{"op":"line","x":0,"y":0}],"occlusion":"..."} using pixel coordinates in THIS current image.',
    "Use polygon only as a compatibility fallback for one connected part. Use box only for a genuinely rectangular object with exact rectangular boundaries.",
    "If this exact object is no longer visible, answer exactly: NONE",
])

DEFAULT_RECURSIVE_EXTRACTOR_PROMPT = "\n".join([
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
    'Answer ONLY with JSON: {"name":"{{nextObjectName}}","backgroundFill":{"description":"...","colors":["#RRGGBB"],"continueEdges":["..."],"texture":"..."}}.',
])


def render_outliner_prompt(
    template: str,
    textual_description: str,
    thing: dict[str, Any],
    position: int,
    total: int,
    width: int,
    height: int,
    planner_relationships: Any = None,
) -> str:
    relationships = json.dumps(planner_relationships or {}, indent=2)
    return (
        template.replace("{{textualDescription}}", textual_description)
        .replace("{{nextObjectName}}", str(thing.get("name", "")))
        .replace("{{nextObjectDescription}}", str(thing.get("description", "")))
        .replace("{{plannerPosition}}", str(position))
        .replace("{{plannerTotal}}", str(total))
        .replace("{{plannerRelationships}}", relationships)
        .replace("{{outlineImage}}", str(thing.get("outlineImage") or ""))
        .replace("{{imageWidth}}", str(width))
        .replace("{{imageHeight}}", str(height))
        .replace("{{maxX}}", str(max(0, width - 1)))
        .replace("{{maxY}}", str(max(0, height - 1)))
    )


def render_extractor_prompt(
    template: str,
    textual_description: str,
    thing: dict[str, Any],
    position: int,
    total: int,
) -> str:
    outline = str(thing.get("outlineOutput") or thing.get("cutoutInstructions") or "Outliner result is unavailable.")
    return (
        template.replace("{{textualDescription}}", textual_description)
        .replace("{{nextObjectName}}", str(thing.get("name", "")))
        .replace("{{nextObjectDescription}}", str(thing.get("description", "")))
        .replace("{{outline}}", outline)
        .replace("{{cutoutInstructions}}", outline)
        .replace("{{plannerPosition}}", str(position))
        .replace("{{plannerTotal}}", str(total))
    )


def parse_outline_geometry(text: str) -> dict[str, Any]:
    """Parse the Outliner JSON: polygons / holes / box / traceTurtle / name."""
    match = re.search(r"\{[\s\S]*\}", text or "")
    if not match:
        return {}
    try:
        parsed = json.loads(match.group(0))
    except (json.JSONDecodeError, ValueError):
        return {}
    if not isinstance(parsed, dict):
        return {}

    def _polys(value: Any) -> list[list[list[float]]]:
        if not isinstance(value, list):
            return []
        return [poly for poly in value if isinstance(poly, list) and len(poly) >= 3]

    polygons = _polys(parsed.get("polygons"))
    holes = _polys(parsed.get("holes"))
    if not polygons and isinstance(parsed.get("polygon"), list) and len(parsed["polygon"]) >= 3:
        polygons = [parsed["polygon"]]
    box = None
    if isinstance(parsed.get("box"), list) and len(parsed["box"]) == 4:
        try:
            box = [float(v) for v in parsed["box"]]
        except (TypeError, ValueError):
            box = None
    trace_turtle: list[dict[str, Any]] = []
    if isinstance(parsed.get("traceTurtle"), list):
        for command in parsed["traceTurtle"]:
            if not isinstance(command, dict):
                continue
            try:
                trace_turtle.append(
                    {"op": str(command.get("op") or ""), "x": float(command.get("x")), "y": float(command.get("y"))}
                )
            except (TypeError, ValueError):
                continue
    return {
        "name": str(parsed.get("name") or ""),
        "polygons": polygons,
        "holes": holes,
        "box": box,
        "traceTurtle": trace_turtle,
    }


def parse_background_fill(text: str) -> dict[str, Any]:
    match = re.search(r"\{[\s\S]*\}", text or "")
    if not match:
        return {}
    try:
        parsed = json.loads(match.group(0))
    except (json.JSONDecodeError, ValueError):
        return {}
    fill = parsed.get("backgroundFill") if isinstance(parsed, dict) else None
    return fill if isinstance(fill, dict) else {}


def has_aligned_outline(thing: dict[str, Any]) -> bool:
    box = thing.get("outlineBox")
    has_geometry = bool(thing.get("outlinePolygons")) or (isinstance(box, list) and len(box) == 4)
    dims = thing.get("outlineDimensions") or {}
    return bool(
        has_geometry
        and thing.get("outlineImage")
        and isinstance(dims, dict)
        and dims.get("width")
        and dims.get("height")
        and thing.get("outlineVerificationImage")
        and thing.get("outlineGeometryHash")
        and thing.get("outlineTraceAgreement") is not None
        and thing.get("outlineBoundaryCoverage") is not None
    )


def has_visualized_plan(inventory: dict[str, Any]) -> bool:
    return bool(inventory.get("extractionOrder")) and bool(inventory.get("parallelGroups"))


def active_outline_group_names(inventory: dict[str, Any]) -> set[str] | None:
    """The earliest parallel group that still has a thing needing an outline.

    Returns None when there is no group gating to apply (0/1 groups).
    """
    groups = inventory.get("parallelGroups") or []
    if len(groups) <= 1:
        return None
    by_name = {str(t.get("name")): t for t in inventory.get("things") or []}
    for group in groups:
        needs = False
        for name in group:
            thing = by_name.get(name)
            if not thing:
                continue
            if thing.get("outputImages"):
                continue
            if not has_aligned_outline(thing):
                needs = True
                break
        if needs:
            return set(group)
    return None


def image_dimensions(root: Path, rel_path: str) -> tuple[int, int] | None:
    candidate = (root / rel_path).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError:
        return None
    if not candidate.is_file():
        return None
    try:
        from PIL import Image  # noqa: PLC0415

        with Image.open(candidate) as img:
            return int(img.width), int(img.height)
    except Exception:  # noqa: BLE001
        return None


def render_description_prompt(
    template: str,
    goal: str,
    known: list[str],
    subject_context: str = _DEFAULT_SUBJECT_CONTEXT,
) -> str:
    goal_text = MEMBER_INVENTORY_GOALS.get(goal, MEMBER_INVENTORY_GOALS["any"])
    already = (
        f"Do not list things already extracted: {', '.join(known)}."
        if known
        else "No things have been extracted yet."
    )
    return (
        template.replace("{{subjectContext}}", subject_context)
        .replace("{{goal}}", goal_text)
        .replace("{{alreadyExtracted}}", already)
    )


# --------------------------------------------------------------------------- #
# Output parsing (ported from formatDetectedJson / parseMemberDescriptionOutput)#
# --------------------------------------------------------------------------- #

_JSON_BLOB = re.compile(r"\{[\s\S]*\}|\[[\s\S]*\]")
_FENCE_OPEN = re.compile(r"^```(?:json)?\s*", re.IGNORECASE)
_FENCE_CLOSE = re.compile(r"\s*```$", re.IGNORECASE)


def detect_json(value: str) -> Any | None:
    """Best-effort JSON extraction matching the frontend's formatDetectedJson."""
    raw = (value or "").strip()
    if not raw:
        return None
    unfenced = _FENCE_CLOSE.sub("", _FENCE_OPEN.sub("", raw)).strip()
    match = _JSON_BLOB.search(unfenced)
    candidate = match.group(0) if match else unfenced
    try:
        return json.loads(candidate)
    except (json.JSONDecodeError, ValueError):
        return None


def parse_description_output(raw: str) -> dict[str, Any]:
    parsed = detect_json(raw)
    if not isinstance(parsed, dict):
        return {"sceneDescription": raw, "things": [], "groups": None}
    scene = str(parsed.get("description") or parsed.get("scene") or "").strip()
    seen: set[str] = set()
    things: list[dict[str, Any]] = []
    raw_things = parsed.get("things") if isinstance(parsed.get("things"), list) else []
    for thing in raw_things:
        if isinstance(thing, str):
            value: dict[str, Any] = {"name": thing, "description": thing}
        elif isinstance(thing, dict):
            value = thing
        else:
            continue
        name = str(value.get("name") or "").strip()[:60]
        description = str(
            value.get("description") or value.get("details") or value.get("name") or ""
        ).strip()[:320]
        key = name.lower()
        if not key or key in seen:
            continue
        seen.add(key)
        things.append({"name": name, "description": description, "status": "listed"})
    groups = parsed.get("groups")
    if groups is None:
        groups = parsed.get("parallelGroups")
    if groups is None:
        groups = parsed.get("waves")
    return {"sceneDescription": scene, "things": things, "groups": groups}


def build_parallel_groups(
    raw_groups: Any, things: list[dict[str, Any]]
) -> dict[str, Any]:
    """Ordered parallel-extraction waves, matching the frontend buildParallelGroups.

    Names are matched to described things; any omitted thing is appended as a
    final group so every thing is covered exactly once.
    """
    by_name = {str(t.get("name", "")).lower(): str(t.get("name", "")) for t in things}
    seen: set[str] = set()
    parallel_groups: list[list[str]] = []
    if isinstance(raw_groups, list):
        for wave in raw_groups:
            names = wave if isinstance(wave, list) else [wave]
            group: list[str] = []
            for value in names:
                if isinstance(value, dict):
                    key = str(value.get("name") or "").strip().lower()
                else:
                    key = str(value or "").strip().lower()
                name = by_name.get(key)
                if not name or name in seen:
                    continue
                seen.add(name)
                group.append(name)
            if group:
                parallel_groups.append(group)
    omitted = [str(t.get("name", "")) for t in things if str(t.get("name", "")) not in seen]
    if omitted:
        parallel_groups.append(omitted)
    extraction_order = [name for group in parallel_groups for name in group]
    return {
        "parallelGroups": parallel_groups,
        "extractionOrder": extraction_order,
        "omitted": omitted,
    }


# --------------------------------------------------------------------------- #
# Model invocation (mirrors policy_api.invoke_model_example)                    #
# --------------------------------------------------------------------------- #


def image_to_data_url(root: Path, rel_path: str) -> str | None:
    candidate = (root / rel_path).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError:
        return None
    if not candidate.is_file():
        return None
    mime, _ = mimetypes.guess_type(str(candidate))
    mime = mime or "image/png"
    data = base64.b64encode(candidate.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{data}"


def invoke_model(
    root: Path,
    model_id: str,
    prompt: str,
    image: str | None,
    timeout_seconds: int = 120,
) -> str:
    """Call a model and return its text. Raises on provider failure."""
    resolved_records = _resolved_model_records(root)
    record = next(
        (
            item
            for item in resolved_records
            if (item.get("document") or {}).get("id") == model_id
        ),
        None,
    )
    if not record or not (record.get("resolved") or {}).get("enabled"):
        raise RuntimeError(f"enabled model/profile not found: {model_id}")
    parameters = _model_execution_parameters(
        root, {"models": [model_id], "strategy": "single"}, resolved_records
    )
    parameters["timeoutSeconds"] = int(timeout_seconds)
    inputs: dict[str, Any] = {"prompt": prompt}
    if image:
        inputs["image"] = image
    result = _llm_complete(inputs, parameters)
    return str(result.get("text") or "") if isinstance(result, dict) else ""


# --------------------------------------------------------------------------- #
# Page-state access                                                            #
# --------------------------------------------------------------------------- #


def load_state(workspace_id: str) -> dict[str, Any]:
    payload = get_page_state(workspace_id)
    state = payload.get("state") if isinstance(payload, dict) else None
    return state if isinstance(state, dict) else {}


def clear_llm_work(workspace_id: str) -> None:
    """Full-state-safe clear of all LLM-produced work (inventories, cache,
    scenes, members, outputs) while preserving frames/selection/prompts/models."""
    with _page_state_lock(workspace_id):
        state = load_state(workspace_id)
        state["memberInventories"] = []
        state["modelResponseCache"] = {}
        state["memberScenes"] = {}
        state["members"] = []
        state["output"] = []
        _save_page_state_payload({
            "workspaceId": workspace_id,
            "clearShards": ["memberInventories", "modelResponseCache"],
            "state": state,
        })


def _effective_describer_model(state: dict[str, Any], override: str | None) -> str:
    if override:
        return override
    return str(state.get("describerModel") or state.get("allCallsModel") or "").strip()


def _selected_frame_paths(state: dict[str, Any], only_selected: bool) -> list[dict[str, Any]]:
    frames = [f for f in (state.get("frames") or []) if isinstance(f, dict) and f.get("path")]
    if not only_selected:
        return frames
    selected = set(state.get("memberInputPaths") or [])
    if not selected:
        return frames
    return [f for f in frames if f.get("path") in selected]


def _describer_concurrency(state: dict[str, Any], override: int | None) -> int:
    if override:
        return max(1, int(override))
    concurrency = state.get("llmCallConcurrency")
    if isinstance(concurrency, dict) and concurrency.get("describer"):
        try:
            return max(1, int(concurrency["describer"]))
        except (TypeError, ValueError):
            pass
    return 3


def persist_inventory(workspace_id: str, inventory: dict[str, Any]) -> None:
    """Read-modify-write ONE inventory into the full page-state.

    The whole state is loaded and re-saved (with only memberInventories changed)
    so the manifest keeps frames/models/prompts/selection intact — passing a
    partial state to _save_page_state_payload would rewrite page_state.json down
    to just that key. Serialized by the page-state lock so concurrent workers
    cannot lose each other's updates.
    """
    with _page_state_lock(workspace_id):
        state = load_state(workspace_id)
        inventories = [
            item
            for item in (state.get("memberInventories") or [])
            if isinstance(item, dict) and item.get("id") != inventory.get("id")
        ]
        inventories.append(inventory)
        state["memberInventories"] = inventories
        _save_page_state_payload({"workspaceId": workspace_id, "state": state})


def update_thing(
    workspace_id: str,
    inventory_id: str,
    thing_name: str,
    patch: dict[str, Any],
    *,
    inventory_patch: dict[str, Any] | None = None,
    member_scenes: dict[str, Any] | None = None,
) -> None:
    """Patch a single thing (matched by name) within an inventory, full-state safe."""
    with _page_state_lock(workspace_id):
        state = load_state(workspace_id)
        inventories = state.get("memberInventories") or []
        for inventory in inventories:
            if not isinstance(inventory, dict) or inventory.get("id") != inventory_id:
                continue
            if inventory_patch:
                inventory.update(inventory_patch)
            things = inventory.get("things") or []
            for thing in things:
                if isinstance(thing, dict) and thing.get("name") == thing_name:
                    thing.update(patch)
                    break
            break
        state["memberInventories"] = inventories
        if member_scenes:
            scenes = state.get("memberScenes") or {}
            scenes.update(member_scenes)
            state["memberScenes"] = scenes
        _save_page_state_payload({"workspaceId": workspace_id, "state": state})


# --------------------------------------------------------------------------- #
# Run registry (start/stop/status for headless + endpoint use)                 #
# --------------------------------------------------------------------------- #


@dataclass
class PipelineRun:
    workspace_id: str
    stage: str
    status: str = "running"  # running | done | failed | stopped
    started_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    finished_at: str | None = None
    summary: str = ""
    error: str | None = None
    log: list[str] = field(default_factory=list)
    counts: dict[str, int] = field(default_factory=dict)
    stop_event: threading.Event = field(default_factory=threading.Event)
    thread: threading.Thread | None = None

    def snapshot(self) -> dict[str, Any]:
        return {
            "workspaceId": self.workspace_id,
            "stage": self.stage,
            "status": self.status,
            "startedAt": self.started_at,
            "finishedAt": self.finished_at,
            "summary": self.summary,
            "error": self.error,
            "counts": dict(self.counts),
            "log": list(self.log[-200:]),
        }


_runs: dict[str, PipelineRun] = {}
_runs_guard = threading.Lock()


def get_run(workspace_id: str) -> PipelineRun | None:
    with _runs_guard:
        return _runs.get(workspace_id)


def stop_run(workspace_id: str) -> bool:
    with _runs_guard:
        run = _runs.get(workspace_id)
    if not run or run.status != "running":
        return False
    run.stop_event.set()
    run.log.append(f"{_ts()} stop requested")
    return True


def _ts() -> str:
    return datetime.now(timezone.utc).strftime("%H:%M:%S")


# --------------------------------------------------------------------------- #
# Describe stage                                                               #
# --------------------------------------------------------------------------- #


def run_describe(
    workspace_id: str,
    *,
    model_override: str | None = None,
    goal_override: str | None = None,
    only_selected: bool = True,
    concurrency_override: int | None = None,
    stop_event: threading.Event | None = None,
    log: Callable[[str], None] | None = None,
    counts: dict[str, int] | None = None,
) -> str:
    """Describe every selected input image and persist things + parallel groups."""
    emit = log or (lambda _msg: None)
    counts = counts if counts is not None else {}
    root = _workspace_root(workspace_id)
    state = load_state(workspace_id)

    model_id = _effective_describer_model(state, model_override)
    if not model_id:
        raise RuntimeError(
            "no describer model configured (set describerModel/allCallsModel in "
            "page-state or pass --model)"
        )
    goal = goal_override or str(state.get("memberGoal") or "any")
    template = str(state.get("memberDescriptionPrompt") or "").strip()
    if not template or (state.get("describerPromptSelection") == "default"):
        template = DEFAULT_MEMBER_DESCRIPTION_PROMPT

    frames = _selected_frame_paths(state, only_selected)
    if not frames:
        emit(f"{_ts()} no input images selected — nothing to describe")
        return "no input images selected"

    existing = {
        item.get("id"): item
        for item in (state.get("memberInventories") or [])
        if isinstance(item, dict)
    }
    concurrency = _describer_concurrency(state, concurrency_override)
    emit(
        f"{_ts()} describe start · {len(frames)} image(s) · model {model_id} · "
        f"goal {goal} · concurrency {concurrency}"
    )
    counts["total"] = len(frames)
    counts["done"] = 0
    counts["failed"] = 0

    subject_context = (
        "This is a root input image. Describe the scene and list its top-level "
        "visually separable objects."
    )
    prompt = render_description_prompt(template, goal, [], subject_context)

    def describe_one(frame: dict[str, Any]) -> None:
        if stop_event is not None and stop_event.is_set():
            return
        path = str(frame.get("path"))
        index = int(frame.get("index") or 0)
        inventory_id = f"input:{path}"
        previous = existing.get(inventory_id) or {}
        emit(f"{_ts()} ① describe input image #{index}")
        image = image_to_data_url(root, path)
        if not image:
            counts["failed"] = counts.get("failed", 0) + 1
            emit(f"{_ts()} ✗ could not load input image: {path}")
            persist_inventory(
                workspace_id,
                {
                    **previous,
                    "id": inventory_id,
                    "framePath": path,
                    "frameIndex": index,
                    "probeIndex": 0,
                    "probeLabel": "input image",
                    "goal": goal,
                    "sourceImage": path,
                    "modelId": model_id,
                    "depth": 0,
                    "subjectName": f"input_{index}",
                    "status": "failed",
                    "descriptionOutput": f"ERROR: could not load input image: {path}",
                    "things": previous.get("things") or [],
                },
            )
            return
        try:
            raw = invoke_model(root, model_id, prompt, image, 120)
        except Exception as error:  # noqa: BLE001 - report provider failures
            counts["failed"] = counts.get("failed", 0) + 1
            emit(f"{_ts()} ✗ describe #{index} failed: {error}")
            persist_inventory(
                workspace_id,
                {
                    **previous,
                    "id": inventory_id,
                    "framePath": path,
                    "frameIndex": index,
                    "probeIndex": 0,
                    "probeLabel": "input image",
                    "goal": goal,
                    "sourceImage": path,
                    "descriptionPrompt": prompt,
                    "modelId": model_id,
                    "depth": 0,
                    "subjectName": f"input_{index}",
                    "status": "failed",
                    "descriptionOutput": f"ERROR: {error}",
                    "things": previous.get("things") or [],
                },
            )
            return
        parsed = parse_description_output(raw)
        things = parsed["things"]
        grouped = build_parallel_groups(parsed["groups"], things)
        inventory = {
            **previous,
            "id": inventory_id,
            "framePath": path,
            "frameIndex": index,
            "probeIndex": 0,
            "probeLabel": "input image",
            "goal": goal,
            "sourceImage": path,
            "descriptionPrompt": prompt,
            "descriptionOutput": raw,
            "sceneDescription": parsed["sceneDescription"],
            "modelId": model_id,
            "depth": 0,
            "subjectName": f"input_{index}",
            "status": "done" if things else "failed",
            "describedThings": things,
            "things": things,
            "extractionOrder": grouped["extractionOrder"],
            "parallelGroups": grouped["parallelGroups"],
            "plannerTouching": [],
            "plannerOcclusions": [],
            "plannerContainments": [],
            "plannerLabels": [],
            "plannerVisualizationImage": "",
        }
        persist_inventory(workspace_id, inventory)
        counts["done"] = counts.get("done", 0) + 1
        emit(
            f"{_ts()} ① [input image] #{index}: {len(things)} thing(s) in "
            f"{len(grouped['parallelGroups'])} parallel group(s)"
        )

    if concurrency <= 1:
        for frame in frames:
            if stop_event is not None and stop_event.is_set():
                break
            describe_one(frame)
    else:
        with ThreadPoolExecutor(max_workers=concurrency) as pool:
            list(pool.map(describe_one, frames))

    summary = (
        f"describe complete: {counts.get('done', 0)} described, "
        f"{counts.get('failed', 0)} failed of {counts.get('total', 0)}"
    )
    emit(f"{_ts()} {summary}")
    return summary


def _effective_stage_model(state: dict[str, Any], key: str, override: str | None) -> str:
    if override:
        return override
    return str(state.get(key) or state.get("allCallsModel") or "").strip()


def _stage_concurrency(state: dict[str, Any], key: str, override: int | None, default: int = 2) -> int:
    if override:
        return max(1, int(override))
    concurrency = state.get("llmCallConcurrency")
    if isinstance(concurrency, dict) and concurrency.get(key):
        try:
            return max(1, int(concurrency[key]))
        except (TypeError, ValueError):
            pass
    return default


def run_outline(
    workspace_id: str,
    *,
    model_override: str | None = None,
    goal_override: str | None = None,
    only_selected: bool = True,
    concurrency_override: int | None = None,
    stop_event: threading.Event | None = None,
    log: Callable[[str], None] | None = None,
    counts: dict[str, int] | None = None,
) -> str:
    """Outline every not-yet-outlined object, honoring parallel-group order."""
    emit = log or (lambda _msg: None)
    counts = counts if counts is not None else {}
    root = _workspace_root(workspace_id)
    state = load_state(workspace_id)
    model_id = _effective_stage_model(state, "outlinerModel", model_override)
    if not model_id:
        raise RuntimeError("no outliner model configured (set outlinerModel/allCallsModel or pass --model)")
    template = str(state.get("memberOutlinerPrompt") or "").strip()
    if not template or state.get("outlinerPromptSelection") == "default":
        template = DEFAULT_MEMBER_OUTLINER_PROMPT

    # Build the current candidate set (group-gated) from a fresh state read.
    candidates: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for inventory in state.get("memberInventories") or []:
        if not isinstance(inventory, dict) or not has_visualized_plan(inventory):
            continue
        active_group = active_outline_group_names(inventory)
        for thing in inventory.get("things") or []:
            if not isinstance(thing, dict) or thing.get("outputImages"):
                continue
            if active_group is not None and thing.get("name") not in active_group:
                continue
            if has_aligned_outline(thing):
                continue
            candidates.append((inventory, thing))
    if not candidates:
        emit(f"{_ts()} nothing to outline (describe first, or all objects already outlined)")
        return "nothing to outline"

    concurrency = _stage_concurrency(state, "outliner", concurrency_override, 2)
    scenes = dict(state.get("memberScenes") or {})
    counts["total"] = len(candidates)
    counts["done"] = 0
    counts["failed"] = 0
    emit(f"{_ts()} outline start · {len(candidates)} object(s) · model {model_id} · concurrency {concurrency}")

    def outline_one(pair: tuple[dict[str, Any], dict[str, Any]]) -> None:
        if stop_event is not None and stop_event.is_set():
            return
        inventory, thing = pair
        inventory_id = str(inventory.get("id"))
        name = str(thing.get("name"))
        # Outline on the CURRENT (progressively reduced) scene so a later parallel
        # group is traced after earlier groups have been removed and no longer
        # occlude it.
        scene_path = scenes.get(inventory_id) or str(inventory.get("sourceImage") or inventory.get("framePath") or "")
        order = inventory.get("extractionOrder") or []
        position = order.index(name) if name in order else 0
        total = len(order) or len(inventory.get("things") or [])
        dims = image_dimensions(root, scene_path)
        if not dims:
            counts["failed"] += 1
            emit(f"{_ts()} ✗ outline {name}: could not load {scene_path}")
            update_thing(workspace_id, inventory_id, name, {
                "status": "listed",
                "outlineError": f"Could not load Outliner input image: {scene_path}",
            })
            return
        width, height = dims
        prompt = render_outliner_prompt(
            template,
            str(inventory.get("descriptionOutput") or inventory.get("sceneDescription") or ""),
            {**thing, "outlineImage": scene_path},
            position + 1,
            total,
            width,
            height,
        )
        update_thing(workspace_id, inventory_id, name, {
            "status": "outlining",
            "inputImage": scene_path,
            "outlineImage": scene_path,
            "outlinePrompt": prompt,
            "outlineDimensions": {"width": width, "height": height},
        })
        image = image_to_data_url(root, scene_path)
        try:
            raw = invoke_model(root, model_id, prompt, image, 120).strip()
        except Exception as error:  # noqa: BLE001
            counts["failed"] += 1
            emit(f"{_ts()} ✗ outline {name}: {error}")
            update_thing(workspace_id, inventory_id, name, {"status": "listed", "outlineError": str(error)})
            return
        if re.fullmatch(r"\s*none[.!]?\s*", raw, re.IGNORECASE):
            counts["failed"] += 1
            emit(f"{_ts()} ✗ outline {name}: Outliner could not locate this object")
            update_thing(workspace_id, inventory_id, name, {
                "status": "not_found",
                "outlineOutput": raw,
                "outlineError": "Outliner could not locate this object.",
            })
            return
        geometry = parse_outline_geometry(raw)
        polygons = geometry.get("polygons") or []
        box = geometry.get("box")
        trace_turtle = geometry.get("traceTurtle") or []
        if not polygons and not box:
            counts["failed"] += 1
            emit(f"{_ts()} ✗ outline {name}: no usable polygons or box")
            update_thing(workspace_id, inventory_id, name, {
                "status": "listed", "outlineOutput": raw,
                "outlineError": "Outliner returned no usable precise polygons or box.",
            })
            return
        if not trace_turtle:
            counts["failed"] += 1
            emit(f"{_ts()} ✗ outline {name}: no Turtle trace to verify")
            update_thing(workspace_id, inventory_id, name, {
                "status": "listed", "outlineOutput": raw,
                "outlineError": "Outliner returned no Turtle trace to verify.",
            })
            return
        try:
            verification = outline_verification({
                "workspaceId": workspace_id,
                "image": scene_path,
                "name": name,
                "polygons": polygons,
                "holes": geometry.get("holes") or [],
                "box": box,
                "traceTurtle": trace_turtle,
                "plannerNumber": position + 1,
            })
        except Exception as error:  # noqa: BLE001
            counts["failed"] += 1
            emit(f"{_ts()} ✗ outline {name}: verification failed: {error}")
            update_thing(workspace_id, inventory_id, name, {
                "status": "listed", "outlineOutput": raw, "outlineError": f"verification failed: {error}",
            })
            return
        update_thing(workspace_id, inventory_id, name, {
            "status": "outlined",
            "outlineOutput": raw,
            "outlineImage": scene_path,
            "outlineDimensions": verification.get("dimensions") or {"width": width, "height": height},
            "outlinePolygons": polygons,
            "outlineHoles": geometry.get("holes") or [],
            "outlineBox": box,
            "outlineTraceTurtle": trace_turtle,
            "outlineVerificationImage": str(verification.get("verificationImage") or ""),
            "outlineGeometryHash": str(verification.get("geometryHash") or ""),
            "outlineTraceAgreement": verification.get("traceAgreement"),
            "outlineBoundaryCoverage": verification.get("boundaryCoverage"),
            "cutoutInstructions": raw,
            "outlineError": None,
        })
        counts["done"] += 1
        emit(f"{_ts()} ✓ outlined {name} (position {position + 1}/{total})")

    if concurrency <= 1:
        for pair in candidates:
            if stop_event is not None and stop_event.is_set():
                break
            outline_one(pair)
    else:
        with ThreadPoolExecutor(max_workers=concurrency) as pool:
            list(pool.map(outline_one, candidates))

    summary = f"outline complete: {counts.get('done', 0)} outlined, {counts.get('failed', 0)} failed of {counts.get('total', 0)}"
    emit(f"{_ts()} {summary}")
    return summary


def run_extract(
    workspace_id: str,
    *,
    model_override: str | None = None,
    goal_override: str | None = None,
    only_selected: bool = True,
    concurrency_override: int | None = None,
    stop_event: threading.Event | None = None,
    log: Callable[[str], None] | None = None,
    counts: dict[str, int] | None = None,
) -> str:
    """Extract outlined objects in group/order, removing each from the scene."""
    emit = log or (lambda _msg: None)
    counts = counts if counts is not None else {}
    root = _workspace_root(workspace_id)
    state = load_state(workspace_id)
    model_id = _effective_stage_model(state, "extractorModel", model_override)
    if not model_id:
        raise RuntimeError("no extractor model configured (set extractorModel/allCallsModel or pass --model)")
    template = str(state.get("memberExtractorPrompt") or "").strip()
    if not template or state.get("extractorPromptSelection") == "default":
        template = DEFAULT_RECURSIVE_EXTRACTOR_PROMPT
    fill_mode = str(state.get("memberFill") or "transparent")

    inventories = [
        inventory
        for inventory in (state.get("memberInventories") or [])
        if isinstance(inventory, dict) and has_visualized_plan(inventory)
    ]
    # An inventory is extractable when its current parallel group (the first group
    # not yet fully extracted) contains at least one outlined, un-extracted object.
    def _group_extract_ready(inventory: dict[str, Any]) -> bool:
        by_name = {str(t.get("name")): t for t in inventory.get("things") or []}
        groups = inventory.get("parallelGroups") or [inventory.get("extractionOrder") or list(by_name)]
        for group in groups:
            pending = [n for n in group if not (by_name.get(n) or {}).get("outputImages")]
            if not pending:
                continue
            return any(has_aligned_outline(by_name.get(n) or {}) for n in pending)
        return False

    ready = [inventory for inventory in inventories if _group_extract_ready(inventory)]
    if not ready:
        emit(f"{_ts()} nothing to extract (outline the current group first)")
        return "nothing to extract"

    scenes = dict(state.get("memberScenes") or {})
    concurrency = _stage_concurrency(state, "extractor", concurrency_override, 2)
    total_objects = sum(len([t for t in inv.get("things") or [] if not t.get("outputImages")]) for inv in ready)
    counts["total"] = total_objects
    counts["done"] = 0
    counts["failed"] = 0
    emit(f"{_ts()} extract start · {len(ready)} scene(s), {total_objects} object(s) · model {model_id} · concurrency {concurrency}")
    step_lock = threading.Lock()
    step_counter = {"n": int(state.get("memberStep") or 0)}

    def next_step() -> int:
        with step_lock:
            step_counter["n"] += 1
            return step_counter["n"]

    def extract_inventory(inventory: dict[str, Any]) -> None:
        inventory_id = str(inventory.get("id"))
        by_name = {str(t.get("name")): t for t in inventory.get("things") or []}
        groups = inventory.get("parallelGroups") or [inventory.get("extractionOrder") or list(by_name)]
        scene_path = scenes.get(inventory_id) or str(inventory.get("sourceImage") or inventory.get("framePath") or "")
        description = str(inventory.get("descriptionOutput") or inventory.get("sceneDescription") or "")
        extracted_names: set[str] = set()
        for group in groups:
            if stop_event is not None and stop_event.is_set():
                return
            pending = [n for n in group if not (by_name.get(n) or {}).get("outputImages")]
            if not pending:
                continue  # group already fully extracted — advance to the next
            # Objects within a parallel group are independent: extract every one
            # that is outlined; skip (do not block on) any not-yet-outlined ones.
            for name in pending:
                if stop_event is not None and stop_event.is_set():
                    return
                thing = by_name.get(name)
                if not thing or not has_aligned_outline(thing):
                    continue
                position = (inventory.get("extractionOrder") or []).index(name) + 1 if name in (inventory.get("extractionOrder") or []) else 0
                prompt = render_extractor_prompt(template, description, thing, position, len(by_name))
                image = image_to_data_url(root, scene_path)
                try:
                    raw = invoke_model(root, model_id, prompt, image, 120).strip()
                except Exception as error:  # noqa: BLE001
                    counts["failed"] += 1
                    emit(f"{_ts()} ✗ extract {name}: {error}")
                    update_thing(workspace_id, inventory_id, name, {"status": "failed", "error": str(error)})
                    continue
                fill_instructions = parse_background_fill(raw)
                if not fill_instructions:
                    counts["failed"] += 1
                    emit(f"{_ts()} ✗ extract {name}: no usable backgroundFill plan")
                    update_thing(workspace_id, inventory_id, name, {
                        "status": "failed", "error": "Extractor returned no usable backgroundFill reconstruction plan.",
                    })
                    continue
                try:
                    cut = member_cut({
                        "workspaceId": workspace_id,
                        "image": scene_path,
                        "outlineSourceImage": thing.get("outlineImage"),
                        "outlineSourceDimensions": thing.get("outlineDimensions"),
                        "polygons": thing.get("outlinePolygons") or [],
                        "holes": thing.get("outlineHoles") or [],
                        "box": thing.get("outlineBox"),
                        "outlineVerificationImage": thing.get("outlineVerificationImage"),
                        "outlineGeometryHash": thing.get("outlineGeometryHash"),
                        "name": name,
                        "step": next_step(),
                        "fill": fill_mode,
                        "fillInstructions": fill_instructions,
                    })
                except Exception as error:  # noqa: BLE001
                    counts["failed"] += 1
                    emit(f"{_ts()} ✗ extract {name}: member-cut failed: {error}")
                    update_thing(workspace_id, inventory_id, name, {"status": "failed", "error": f"member-cut failed: {error}"})
                    continue
                cutout = str(cut.get("cutout") or "")
                new_scene = str(cut.get("scene") or scene_path)
                scenes[inventory_id] = new_scene
                if thing is not None:
                    thing["outputImages"] = [cutout]
                update_thing(
                    workspace_id,
                    inventory_id,
                    name,
                    {"status": "extracted", "outputImages": [cutout], "fillInstructions": fill_instructions, "error": None},
                    inventory_patch={"status": "extracting"},
                    member_scenes={inventory_id: new_scene},
                )
                scene_path = new_scene
                extracted_names.add(name)
                counts["done"] += 1
                emit(f"{_ts()} ✓ extracted {name} ({counts['done']}/{total_objects})")
            # If the current group still has un-outlined objects, later groups stay
            # blocked (they may be occluded until this group is fully removed).
            still_pending = [n for n in group if not (by_name.get(n) or {}).get("outputImages")]
            if still_pending:
                break
        all_done = all((by_name.get(n) or {}).get("outputImages") for g in groups for n in g)
        if all_done:
            update_thing(workspace_id, inventory_id, next(iter(by_name), ""), {}, inventory_patch={"status": "done"})

    if concurrency <= 1:
        for inventory in ready:
            if stop_event is not None and stop_event.is_set():
                break
            extract_inventory(inventory)
    else:
        with ThreadPoolExecutor(max_workers=concurrency) as pool:
            list(pool.map(extract_inventory, ready))

    summary = f"extract complete: {counts.get('done', 0)} extracted, {counts.get('failed', 0)} failed of {counts.get('total', 0)}"
    emit(f"{_ts()} {summary}")
    return summary


def run_full(
    workspace_id: str,
    *,
    model_override: str | None = None,
    goal_override: str | None = None,
    only_selected: bool = True,
    concurrency_override: int | None = None,
    stop_event: threading.Event | None = None,
    log: Callable[[str], None] | None = None,
    counts: dict[str, int] | None = None,
) -> str:
    """Run describe -> outline -> extract, repeating outline+extract until the
    current parallel groups are drained (later groups unblock as earlier ones
    are removed)."""
    emit = log or (lambda _msg: None)
    counts = counts if counts is not None else {}
    common = dict(
        model_override=model_override,
        goal_override=goal_override,
        only_selected=only_selected,
        concurrency_override=concurrency_override,
        stop_event=stop_event,
        log=emit,
    )
    emit(f"{_ts()} === full pipeline: describe ===")
    run_describe(workspace_id, counts=counts, **common)
    if stop_event is not None and stop_event.is_set():
        return "stopped after describe"
    # Outline + extract advance group-by-group; loop until a whole round makes no
    # progress (no new outlines AND no new extractions), which also breaks out of
    # a persistently-failing outline instead of looping forever.
    for round_index in range(1, 41):
        if stop_event is not None and stop_event.is_set():
            return f"stopped during round {round_index}"
        emit(f"{_ts()} === full pipeline: outline (round {round_index}) ===")
        outline_counts: dict[str, int] = {}
        run_outline(workspace_id, counts=outline_counts, **common)
        if stop_event is not None and stop_event.is_set():
            return f"stopped during outline round {round_index}"
        emit(f"{_ts()} === full pipeline: extract (round {round_index}) ===")
        extract_counts: dict[str, int] = {}
        run_extract(workspace_id, counts=extract_counts, **common)
        counts["outlined"] = counts.get("outlined", 0) + outline_counts.get("done", 0)
        counts["extracted"] = counts.get("extracted", 0) + extract_counts.get("done", 0)
        if outline_counts.get("done", 0) == 0 and extract_counts.get("done", 0) == 0:
            emit(f"{_ts()} no further progress after round {round_index} — stopping")
            break
    summary = (
        f"full pipeline complete: {counts.get('outlined', 0)} outlined, "
        f"{counts.get('extracted', 0)} extracted"
    )
    emit(f"{_ts()} {summary}")
    return summary


_STAGE_RUNNERS: dict[str, Callable[..., str]] = {
    "describe": run_describe,
    "outline": run_outline,
    "extract": run_extract,
    "full": run_full,
}


def start_run(
    workspace_id: str,
    stage: str = "describe",
    *,
    model_override: str | None = None,
    goal_override: str | None = None,
    only_selected: bool = True,
    concurrency_override: int | None = None,
) -> dict[str, Any]:
    """Start a background pipeline run for a workspace (one at a time)."""
    stage = stage or "describe"
    if stage not in _STAGE_RUNNERS:
        raise ValueError(f"unknown stage: {stage} (available: {', '.join(_STAGE_RUNNERS)})")
    with _runs_guard:
        current = _runs.get(workspace_id)
        if current and current.status == "running":
            return current.snapshot()
        run = PipelineRun(workspace_id=workspace_id, stage=stage)
        _runs[workspace_id] = run

    runner = _STAGE_RUNNERS[stage]

    def worker() -> None:
        try:
            summary = runner(
                workspace_id,
                model_override=model_override,
                goal_override=goal_override,
                only_selected=only_selected,
                concurrency_override=concurrency_override,
                stop_event=run.stop_event,
                log=run.log.append,
                counts=run.counts,
            )
            run.summary = summary
            run.status = "stopped" if run.stop_event.is_set() else "done"
        except Exception as error:  # noqa: BLE001 - surface to status endpoint
            run.status = "failed"
            run.error = str(error)
            run.log.append(f"{_ts()} ✗ pipeline failed: {error}")
            run.log.append(traceback.format_exc())
        finally:
            run.finished_at = datetime.now(timezone.utc).isoformat()

    thread = threading.Thread(target=worker, name=f"vi-pipeline-{workspace_id}", daemon=True)
    run.thread = thread
    thread.start()
    return run.snapshot()


def run_stage_blocking(
    workspace_id: str,
    stage: str = "describe",
    **kwargs: Any,
) -> str:
    """Run a stage synchronously (used by the CLI). Returns the summary."""
    if stage not in _STAGE_RUNNERS:
        raise ValueError(f"unknown stage: {stage}")
    return _STAGE_RUNNERS[stage](workspace_id, log=lambda msg: print(msg, flush=True), **kwargs)


# --------------------------------------------------------------------------- #
# CLI                                                                          #
# --------------------------------------------------------------------------- #


def _main(argv: list[str] | None = None) -> int:
    # The status log uses non-ASCII glyphs (①, ✗). A Windows console defaults to
    # cp1252 and would crash on them, so force UTF-8 with a safe fallback.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[union-attr]
        except (AttributeError, ValueError):
            pass
    parser = argparse.ArgumentParser(description="Headless Video Import pipeline runner")
    parser.add_argument("--workspace", required=True, help="workspace id, e.g. arc3_random_player")
    parser.add_argument("--stage", default="describe", choices=sorted(_STAGE_RUNNERS))
    parser.add_argument("--model", default=None, help="override describer model id")
    parser.add_argument("--goal", default=None, help="override inventory goal")
    parser.add_argument("--concurrency", type=int, default=None, help="override describer concurrency")
    parser.add_argument(
        "--all",
        action="store_true",
        help="describe every extracted frame, not just the selected input images",
    )
    args = parser.parse_args(argv)
    summary = run_stage_blocking(
        args.workspace,
        args.stage,
        model_override=args.model,
        goal_override=args.goal,
        only_selected=not args.all,
        concurrency_override=args.concurrency,
    )
    print(summary, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
