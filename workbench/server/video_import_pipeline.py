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
    turtle_render,
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


DEFAULT_TURTLE_PROMPT = "\n".join([
    "TURTLE LEAF RENDERER.",
    "The attached image is the terminal object {{subjectName}}. Its recursive Describer found no further sub-objects.",
    "Object description: {{description}}",
    "Write a constrained turtle drawing program that reconstructs this one object.",
    "Use normalized coordinates from 0 to 1000 with origin at the top-left.",
    "Allowed commands: pen, move, line, polyline, polygon, rectangle, ellipse, dot.",
    "Use transparent background unless the object itself requires a background. Use at most 100 commands.",
    'Answer ONLY with JSON: {"version":1,"background":"transparent","penColor":"#RRGGBB","penWidth":4,"commands":[{"op":"move","x":0,"y":0},...]}',
])

DEFAULT_TURTLE_PNG_PROMPT = "\n".join([
    "TURTLE PNG DRAW STEP.",
    "The attached image is terminal object {{subjectName}}.",
    "Object description: {{description}}",
    "Review the draft Turtle program below and return the final drawing program that should be rendered to PNG.",
    "Preserve accurate silhouette, colors, holes, and visible internal details. Coordinates are normalized from 0 to 1000 with top-left origin.",
    "Allowed commands: pen, move, line, polyline, polygon, rectangle, ellipse, dot. Use at most 200 commands.",
    "DRAFT TURTLE PROGRAM:",
    "{{draftProgram}}",
    "Answer ONLY with the final JSON object. Do not include Markdown or Python.",
])


def render_turtle_prompt(template: str, subject_name: str, description: str) -> str:
    return (
        template.replace("{{subjectName}}", subject_name)
        .replace("{{description}}", description or "No additional description.")
    )


def render_turtle_png_prompt(template: str, subject_name: str, description: str, draft_program: str) -> str:
    return (
        template.replace("{{subjectName}}", subject_name)
        .replace("{{description}}", description or "No additional description.")
        .replace("{{draftProgram}}", draft_program)
    )


def _derive_box(command: dict[str, Any]) -> list[float] | None:
    def num(key: str) -> float | None:
        try:
            return float(command[key])
        except (KeyError, TypeError, ValueError):
            return None

    if all(k in command for k in ("x0", "y0", "x1", "y1")):
        vals = [num("x0"), num("y0"), num("x1"), num("y1")]
        return vals if None not in vals else None  # type: ignore[return-value]
    x, y = num("x"), num("y")
    width = num("width") if "width" in command else num("w")
    height = num("height") if "height" in command else num("h")
    if None not in (x, y, width, height):
        return [x, y, x + width, y + height]  # type: ignore[operator]
    return None


def _normalize_points(value: Any) -> list[list[float]] | None:
    if not isinstance(value, list):
        return None
    points: list[list[float]] = []
    for pt in value:
        if isinstance(pt, (list, tuple)) and len(pt) >= 2:
            try:
                points.append([float(pt[0]), float(pt[1])])
            except (TypeError, ValueError):
                return None
        elif isinstance(pt, dict) and "x" in pt and "y" in pt:
            try:
                points.append([float(pt["x"]), float(pt["y"])])
            except (TypeError, ValueError):
                return None
        else:
            return None
    return points


def normalize_turtle_program(program: Any) -> dict[str, Any] | None:
    """Reconcile common model variations to the shape turtle_render expects:
    rectangle/ellipse need box=[x0,y0,x1,y1] (models often emit x/y/width/height),
    and polygon/polyline points may arrive as {x,y} objects."""
    prog: Any
    if isinstance(program, dict):
        prog = program
    elif isinstance(program, str):
        match = re.search(r"\{[\s\S]*\}", program)
        if not match:
            return None
        try:
            prog = json.loads(match.group(0))
        except (json.JSONDecodeError, ValueError):
            return None
    else:
        return None
    if not isinstance(prog, dict):
        return None
    commands = prog.get("commands")
    if not isinstance(commands, list):
        return prog
    aliases = {"rect": "rectangle", "circle": "ellipse", "oval": "ellipse"}
    for command in commands:
        if not isinstance(command, dict):
            continue
        op = str(command.get("op") or "").lower()
        if op in aliases:
            op = aliases[op]
            command["op"] = op
        if op in ("rectangle", "ellipse"):
            box = command.get("box")
            if not (isinstance(box, list) and len(box) == 4):
                derived = _derive_box(command)
                if derived:
                    command["box"] = derived
        elif op in ("polygon", "polyline"):
            pts = _normalize_points(command.get("points") or command.get("vertices"))
            if pts is not None:
                command["points"] = pts
    return prog




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
            if thing.get("outputImages") or thing.get("outlineSkipped"):
                continue  # extracted, or given up on after repeated failures
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


# After this many failed outline attempts an object is given up on ("skipped") so
# a single stubborn object can't block its whole parallel group (and thus every
# later group / the extraction of the scene) forever.
MAX_OUTLINE_ATTEMPTS = 3


def _clamp_point(point: Any, width: int, height: int) -> list[float] | None:
    if not isinstance(point, (list, tuple)) or len(point) < 2:
        return None
    try:
        x = min(max(0.0, float(point[0])), float(max(0, width - 1)))
        y = min(max(0.0, float(point[1])), float(max(0, height - 1)))
    except (TypeError, ValueError):
        return None
    return [x, y]


def clamp_geometry(geometry: dict[str, Any], width: int, height: int) -> dict[str, Any]:
    """Clamp outliner coordinates into [0,width-1]x[0,height-1]. Models often emit
    edge points at exactly width/height, which the verifier rejects as out of
    bounds — clamping keeps those otherwise-valid outlines."""
    def _clamp_polys(polys: Any) -> list[list[list[float]]]:
        out: list[list[list[float]]] = []
        for poly in polys or []:
            pts = [p for p in (_clamp_point(pt, width, height) for pt in poly) if p is not None]
            if len(pts) >= 3:
                out.append(pts)
        return out

    box = geometry.get("box")
    clamped_box = None
    if isinstance(box, (list, tuple)) and len(box) == 4:
        tl = _clamp_point([box[0], box[1]], width, height)
        br = _clamp_point([box[2], box[3]], width, height)
        if tl and br:
            clamped_box = [tl[0], tl[1], br[0], br[1]]
    return {
        **geometry,
        "polygons": _clamp_polys(geometry.get("polygons")),
        "holes": _clamp_polys(geometry.get("holes")),
        "box": clamped_box,
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
    member: dict[str, Any] | None = None,
) -> None:
    """Patch a single thing (matched by name) within an inventory, full-state safe.

    Optionally appends a gallery `member` (a produced cutout) so the objects
    gallery populates, and merges `member_scenes` (progressively reduced scenes).
    """
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
        if member:
            members = state.get("members") or []
            # Replace any prior member for the same object in this inventory.
            members = [
                m for m in members
                if not (isinstance(m, dict) and m.get("inventoryId") == inventory_id and m.get("name") == thing_name)
            ]
            members.append(member)
            state["members"] = members
        _save_page_state_payload({"workspaceId": workspace_id, "state": state})


def persist_turtle_artifact(workspace_id: str, source_image: str, artifact: dict[str, Any]) -> None:
    """Merge one turtle artifact (keyed by its source cutout) into page-state,
    full-state safe."""
    with _page_state_lock(workspace_id):
        state = load_state(workspace_id)
        artifacts = state.get("turtleArtifacts")
        if not isinstance(artifacts, dict):
            artifacts = {}
        artifacts[source_image] = artifact
        state["turtleArtifacts"] = artifacts
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


class _Active:
    """Thread-safe in-flight counter written into a stage's counts dict so the run
    snapshot (and the websocket) reflects real-time PROCESSING/ACTIVE WORKERS."""

    def __init__(self, counts: dict[str, int]) -> None:
        self._counts = counts
        self._lock = threading.Lock()

    def __enter__(self) -> "_Active":
        with self._lock:
            self._counts["active"] = self._counts.get("active", 0) + 1
        return self

    def __exit__(self, *_exc: Any) -> None:
        with self._lock:
            self._counts["active"] = max(0, self._counts.get("active", 0) - 1)


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
    counts["stage"] = "describe"
    counts["total"] = len(frames)
    counts["done"] = 0
    counts["failed"] = 0
    counts["active"] = 0
    active = _Active(counts)

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
            with active:
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
            if not isinstance(thing, dict) or thing.get("outputImages") or thing.get("outlineSkipped"):
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
    counts["stage"] = "outline"
    counts["total"] = len(candidates)
    counts["done"] = 0
    counts["failed"] = 0
    counts["active"] = 0
    active = _Active(counts)
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
        attempts = int(thing.get("outlineAttempts") or 0) + 1
        skip = attempts >= MAX_OUTLINE_ATTEMPTS

        def fail(error: str, status: str = "listed", extra: dict[str, Any] | None = None) -> None:
            counts["failed"] += 1
            update_thing(workspace_id, inventory_id, name, {
                "status": "skipped" if skip else status,
                "outlineError": error,
                "outlineAttempts": attempts,
                "outlineSkipped": skip,
                **(extra or {}),
            })
            if skip:
                emit(f"{_ts()} ⨯ giving up on outline {name} after {attempts} attempt(s): {error}")
            else:
                emit(f"{_ts()} ✗ outline {name}: {error}")

        dims = image_dimensions(root, scene_path)
        if not dims:
            fail(f"could not load Outliner input image: {scene_path}")
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
            with active:
                raw = invoke_model(root, model_id, prompt, image, 120).strip()
        except Exception as error:  # noqa: BLE001
            fail(str(error))
            return
        if re.fullmatch(r"\s*none[.!]?\s*", raw, re.IGNORECASE):
            fail("Outliner could not locate this object.", status="not_found", extra={"outlineOutput": raw})
            return
        geometry = clamp_geometry(parse_outline_geometry(raw), width, height)
        polygons = geometry.get("polygons") or []
        box = geometry.get("box")
        trace_turtle = geometry.get("traceTurtle") or []
        if not polygons and not box:
            fail("Outliner returned no usable precise polygons or box.", extra={"outlineOutput": raw})
            return
        if not trace_turtle:
            fail("Outliner returned no Turtle trace to verify.", extra={"outlineOutput": raw})
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
            message = str(error)
            # HTTPException stringifies as "409: <detail>"; keep the detail.
            detail = getattr(error, "detail", None)
            if detail:
                message = str(detail)
            fail(f"verification failed: {message}", extra={"outlineOutput": raw})
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
    # not yet fully resolved) contains at least one outlined, un-extracted object.
    # A "resolved" object is one already extracted OR given up on (outlineSkipped).
    def _resolved(thing: dict[str, Any]) -> bool:
        return bool(thing.get("outputImages") or thing.get("outlineSkipped"))

    def _group_extract_ready(inventory: dict[str, Any]) -> bool:
        by_name = {str(t.get("name")): t for t in inventory.get("things") or []}
        groups = inventory.get("parallelGroups") or [inventory.get("extractionOrder") or list(by_name)]
        for group in groups:
            pending = [n for n in group if not _resolved(by_name.get(n) or {})]
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
    counts["stage"] = "extract"
    counts["total"] = total_objects
    counts["done"] = 0
    counts["failed"] = 0
    counts["active"] = 0
    active = _Active(counts)
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
            pending = [n for n in group if not _resolved(by_name.get(n) or {})]
            if not pending:
                continue  # group already fully resolved — advance to the next
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
                    with active:
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
                next_pass = str(cut.get("nextPassImage") or cutout)
                cut_box = cut.get("box") or thing.get("outlineBox") or [0, 0, 0, 0]
                scenes[inventory_id] = new_scene
                if thing is not None:
                    thing["outputImages"] = [cutout]
                member = {
                    "framePath": inventory.get("framePath"),
                    "frameIndex": inventory.get("frameIndex"),
                    "name": name,
                    "cutout": cutout,
                    "box": cut_box,
                    "step": step_counter["n"],
                    "status": "pending",
                    "probeIndex": -1,
                    "probeLabel": inventory.get("probeLabel") or "input image",
                    "route": "direct_from_scene",
                    "promptSource": "outliner",
                    "inputImage": thing.get("inputImage") or scene_path,
                    "sceneAfter": new_scene,
                    "inventoryId": inventory_id,
                    "depth": inventory.get("depth") or 0,
                    "nextPassImage": next_pass,
                    "provenance": str(cut.get("cutoutProvenance") or ""),
                    "nextPassProvenance": str(cut.get("nextPassProvenance") or ""),
                    "sceneProvenance": str(cut.get("sceneProvenance") or ""),
                }
                update_thing(
                    workspace_id,
                    inventory_id,
                    name,
                    {"status": "extracted", "outputImages": [cutout], "fillInstructions": fill_instructions, "error": None},
                    inventory_patch={"status": "extracting"},
                    member_scenes={inventory_id: new_scene},
                    member=member,
                )
                scene_path = new_scene
                extracted_names.add(name)
                counts["done"] += 1
                emit(f"{_ts()} ✓ extracted {name} ({counts['done']}/{total_objects})")
            # If the current group still has unresolved objects, later groups stay
            # blocked (they may be occluded until this group is fully removed).
            still_pending = [n for n in group if not _resolved(by_name.get(n) or {})]
            if still_pending:
                break
        all_done = all(_resolved(by_name.get(n) or {}) for g in groups for n in g)
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


def _collect_turtle_leaves(state: dict[str, Any]) -> list[dict[str, Any]]:
    """Every extracted object cutout is a terminal leaf for turtle rendering."""
    leaves: list[dict[str, Any]] = []
    seen: set[str] = set()
    for inv in state.get("memberInventories") or []:
        if not isinstance(inv, dict):
            continue
        for thing in inv.get("things") or []:
            outs = thing.get("outputImages") or []
            if outs and outs[0] not in seen:
                seen.add(outs[0])
                leaves.append({
                    "sourceImage": outs[0],
                    "subjectName": str(thing.get("name") or "object"),
                    "description": str(thing.get("description") or ""),
                })
    return leaves


def run_turtle(
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
    """Generate a Turtle drawing program for every extracted leaf cutout."""
    emit = log or (lambda _msg: None)
    counts = counts if counts is not None else {}
    root = _workspace_root(workspace_id)
    state = load_state(workspace_id)
    model_id = _effective_stage_model(state, "turtleModel", model_override)
    if not model_id:
        raise RuntimeError("no turtle model configured (set turtleModel/allCallsModel or pass --model)")
    template = str(state.get("turtlePrompt") or "").strip()
    if not template or state.get("turtlePromptSelection") == "default":
        template = DEFAULT_TURTLE_PROMPT
    artifacts = state.get("turtleArtifacts") if isinstance(state.get("turtleArtifacts"), dict) else {}
    leaves = _collect_turtle_leaves(state)
    candidates = [
        leaf for leaf in leaves
        if not (artifacts.get(leaf["sourceImage"]) or {}).get("rawProgram")
    ]
    if not candidates:
        emit(f"{_ts()} nothing to turtle (extract objects first, or all leaves already have programs)")
        return "nothing to turtle"
    concurrency = _stage_concurrency(state, "turtle", concurrency_override, 2)
    counts["stage"] = "turtle"
    counts["total"] = len(candidates)
    counts["done"] = 0
    counts["failed"] = 0
    counts["active"] = 0
    active = _Active(counts)
    emit(f"{_ts()} turtle-gen start · {len(candidates)} leaf/leaves · model {model_id} · concurrency {concurrency}")

    def turtle_one(leaf: dict[str, Any]) -> None:
        if stop_event is not None and stop_event.is_set():
            return
        src = leaf["sourceImage"]
        prompt = render_turtle_prompt(template, leaf["subjectName"], leaf["description"])
        image = image_to_data_url(root, src)
        if not image:
            counts["failed"] += 1
            emit(f"{_ts()} ✗ turtle {leaf['subjectName']}: could not load {src}")
            persist_turtle_artifact(workspace_id, src, {
                "sourceImage": src, "subjectName": leaf["subjectName"], "prompt": prompt,
                "rawProgram": "", "status": "failed", "failedStage": "gen",
                "error": f"could not load Turtle input: {src}",
            })
            return
        try:
            with active:
                raw = invoke_model(root, model_id, prompt, image, 180).strip()
        except Exception as error:  # noqa: BLE001
            counts["failed"] += 1
            emit(f"{_ts()} ✗ turtle {leaf['subjectName']}: {error}")
            persist_turtle_artifact(workspace_id, src, {
                "sourceImage": src, "subjectName": leaf["subjectName"], "prompt": prompt,
                "rawProgram": "", "status": "failed", "failedStage": "gen", "error": str(error),
            })
            return
        persist_turtle_artifact(workspace_id, src, {
            "sourceImage": src, "subjectName": leaf["subjectName"], "prompt": prompt,
            "rawProgram": raw, "status": "generated", "error": None, "failedStage": None,
        })
        counts["done"] += 1
        emit(f"{_ts()} 🐢 generated turtle program for {leaf['subjectName']} ({counts['done']}/{counts['total']})")

    if concurrency <= 1:
        for leaf in candidates:
            if stop_event is not None and stop_event.is_set():
                break
            turtle_one(leaf)
    else:
        with ThreadPoolExecutor(max_workers=concurrency) as pool:
            list(pool.map(turtle_one, candidates))
    summary = f"turtle-gen complete: {counts.get('done', 0)} program(s), {counts.get('failed', 0)} failed of {counts.get('total', 0)}"
    emit(f"{_ts()} {summary}")
    return summary


def run_turtle_png(
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
    """Turn each generated Turtle program into a rendered PNG (the final output)."""
    emit = log or (lambda _msg: None)
    counts = counts if counts is not None else {}
    root = _workspace_root(workspace_id)
    state = load_state(workspace_id)
    model_id = _effective_stage_model(state, "turtlePngModel", model_override)
    if not model_id:
        raise RuntimeError("no turtle-png model configured (set turtlePngModel/allCallsModel or pass --model)")
    template = str(state.get("turtlePngPrompt") or "").strip()
    if not template or state.get("turtlePngPromptSelection") == "default":
        template = DEFAULT_TURTLE_PNG_PROMPT
    artifacts = state.get("turtleArtifacts") if isinstance(state.get("turtleArtifacts"), dict) else {}
    candidates = [
        (src, art) for src, art in artifacts.items()
        if isinstance(art, dict) and art.get("rawProgram") and not art.get("renderedImage")
    ]
    if not candidates:
        emit(f"{_ts()} nothing to render (generate turtle programs first)")
        return "nothing to render"
    concurrency = _stage_concurrency(state, "turtlePng", concurrency_override, 2)
    counts["stage"] = "turtlePng"
    counts["total"] = len(candidates)
    counts["done"] = 0
    counts["failed"] = 0
    counts["active"] = 0
    active = _Active(counts)
    emit(f"{_ts()} turtle-png start · {len(candidates)} program(s) · model {model_id} · concurrency {concurrency}")

    def png_one(pair: tuple[str, dict[str, Any]]) -> None:
        if stop_event is not None and stop_event.is_set():
            return
        src, art = pair
        subject = str(art.get("subjectName") or "object")
        png_prompt = render_turtle_png_prompt(template, subject, str(art.get("description") or ""), str(art.get("rawProgram") or ""))
        image = image_to_data_url(root, src)
        try:
            with active:
                png_program = invoke_model(root, model_id, png_prompt, image, 180).strip() if image else str(art.get("rawProgram") or "")
        except Exception as error:  # noqa: BLE001
            counts["failed"] += 1
            emit(f"{_ts()} ✗ turtle-png {subject}: {error}")
            persist_turtle_artifact(workspace_id, src, {**art, "pngPrompt": png_prompt, "status": "failed", "failedStage": "png", "error": str(error)})
            return
        try:
            result = turtle_render({
                "workspaceId": workspace_id,
                "sourceImage": src,
                "subjectName": subject,
                "modelId": model_id,
                "prompt": png_prompt,
                "program": normalize_turtle_program(png_program) or png_program,
            })
        except Exception as error:  # noqa: BLE001
            message = str(getattr(error, "detail", None) or error)
            counts["failed"] += 1
            emit(f"{_ts()} ✗ turtle-png {subject}: render failed: {message}")
            persist_turtle_artifact(workspace_id, src, {**art, "pngPrompt": png_prompt, "pngProgram": png_program, "status": "failed", "failedStage": "png", "error": message})
            return
        persist_turtle_artifact(workspace_id, src, {
            **art,
            "pngPrompt": png_prompt,
            "pngProgram": png_program,
            "programPath": str(result.get("programPath") or ""),
            "renderedImage": str(result.get("renderedImage") or ""),
            "provenance": str(result.get("provenance") or ""),
            "status": "rendered",
            "error": None,
            "failedStage": None,
        })
        counts["done"] += 1
        emit(f"{_ts()} 🖼 rendered turtle PNG for {subject} ({counts['done']}/{counts['total']}): {result.get('renderedImage')}")

    if concurrency <= 1:
        for pair in candidates:
            if stop_event is not None and stop_event.is_set():
                break
            png_one(pair)
    else:
        with ThreadPoolExecutor(max_workers=concurrency) as pool:
            list(pool.map(png_one, candidates))
    summary = f"turtle-png complete: {counts.get('done', 0)} PNG(s), {counts.get('failed', 0)} failed of {counts.get('total', 0)}"
    emit(f"{_ts()} {summary}")
    return summary


# --------------------------------------------------------------------------- #
# Recognition stage                                                           #
# --------------------------------------------------------------------------- #

import urllib.parse as _urlparse  # noqa: E402


DEFAULT_RECOGNIZE_PROMPT = "\n".join([
    "CHARACTER / OBJECT RECOGNITION.",
    "Identify each well-known character, person, mascot, logo, or recognizable object visible in this image.",
    "For each, give the canonical name, the franchise/source it comes from, a confidence 0..1, where it is in the image, and a short web search query that would find reference images of it.",
    'Answer ONLY with JSON: {"characters":[{"name":"<canonical name>","franchise":"<movie/show/brand>","confidence":0.0,"where":"<position>","searchQuery":"<web search query>"}]}.',
    "If nothing recognizable is present, return an empty characters array.",
])


def persist_recognition(workspace_id: str, key: str, entry: dict[str, Any]) -> None:
    """Merge one recognition result (keyed by frame/cutout path) into page-state."""
    with _page_state_lock(workspace_id):
        state = load_state(workspace_id)
        recognitions = state.get("recognitions")
        if not isinstance(recognitions, dict):
            recognitions = {}
        recognitions[key] = entry
        state["recognitions"] = recognitions
        _save_page_state_payload({"workspaceId": workspace_id, "state": state})


def _web_search_url(query: str) -> str:
    return "https://www.bing.com/images/search?q=" + _urlparse.quote(query)


def _recognition_targets(state: dict[str, Any], only_selected: bool) -> list[dict[str, Any]]:
    """Prefer per-object extracted cutouts; fall back to whole input frames.

    Recognizing cutouts identifies each isolated character; recognizing frames
    identifies every character present in the scene ("identify them in images").
    """
    members = state.get("members") or []
    targets: list[dict[str, Any]] = []
    seen: set[str] = set()
    for m in members:
        if isinstance(m, dict) and m.get("cutout") and m["cutout"] not in seen:
            seen.add(m["cutout"])
            targets.append({"image": m["cutout"], "kind": "object", "label": m.get("name") or "object", "frameIndex": m.get("frameIndex")})
    if targets:
        return targets
    for frame in _selected_frame_paths(state, only_selected):
        path = frame.get("path")
        if path and path not in seen:
            seen.add(path)
            targets.append({"image": path, "kind": "frame", "label": f"frame #{frame.get('index', 0)}", "frameIndex": frame.get("index")})
    return targets


def run_recognize(
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
    """Identify well-known characters/objects in each frame (or extracted cutout)
    and attach web-search references for each."""
    emit = log or (lambda _msg: None)
    counts = counts if counts is not None else {}
    root = _workspace_root(workspace_id)
    state = load_state(workspace_id)
    model_id = _effective_stage_model(state, "recognizerModel", model_override)
    if not model_id:
        raise RuntimeError("no recognizer model configured (set recognizerModel/allCallsModel or pass --model)")
    template = str(state.get("recognizePrompt") or "").strip() or DEFAULT_RECOGNIZE_PROMPT
    targets = _recognition_targets(state, only_selected)
    existing = state.get("recognitions") if isinstance(state.get("recognitions"), dict) else {}
    candidates = [t for t in targets if t["image"] not in existing]
    if not candidates:
        emit(f"{_ts()} nothing to recognize (extract objects or select frames first)")
        return "nothing to recognize"
    concurrency = _stage_concurrency(state, "recognizer", concurrency_override, 3)
    counts["stage"] = "recognize"
    counts["total"] = len(candidates)
    counts["done"] = 0
    counts["failed"] = 0
    counts["active"] = 0
    active = _Active(counts)
    emit(f"{_ts()} recognize start · {len(candidates)} {candidates[0]['kind']}(s) · model {model_id} · concurrency {concurrency}")

    def recognize_one(target: dict[str, Any]) -> None:
        if stop_event is not None and stop_event.is_set():
            return
        img_rel = target["image"]
        image = image_to_data_url(root, img_rel)
        if not image:
            counts["failed"] += 1
            emit(f"{_ts()} ✗ recognize {target['label']}: could not load {img_rel}")
            return
        try:
            with active:
                raw = invoke_model(root, model_id, template, image, 120).strip()
        except Exception as error:  # noqa: BLE001
            counts["failed"] += 1
            emit(f"{_ts()} ✗ recognize {target['label']}: {error}")
            persist_recognition(workspace_id, img_rel, {"image": img_rel, "kind": target["kind"], "label": target["label"], "frameIndex": target.get("frameIndex"), "characters": [], "error": str(error)})
            return
        parsed = detect_json(raw)
        characters: list[dict[str, Any]] = []
        raw_chars = parsed.get("characters") if isinstance(parsed, dict) else None
        for c in raw_chars or []:
            if not isinstance(c, dict):
                continue
            name = str(c.get("name") or "").strip()
            if not name:
                continue
            franchise = str(c.get("franchise") or "").strip()
            try:
                confidence = float(c.get("confidence"))
            except (TypeError, ValueError):
                confidence = 0.0
            query = str(c.get("searchQuery") or f"{name} {franchise}".strip())
            characters.append({
                "name": name,
                "franchise": franchise,
                "confidence": round(confidence, 2),
                "where": str(c.get("where") or ""),
                "searchQuery": query,
                "webSearchUrl": _web_search_url(query),
            })
        persist_recognition(workspace_id, img_rel, {
            "image": img_rel,
            "kind": target["kind"],
            "label": target["label"],
            "frameIndex": target.get("frameIndex"),
            "characters": characters,
            "rawOutput": raw,
        })
        counts["done"] += 1
        names = ", ".join(f"{c['name']} ({c['confidence']:.0%})" for c in characters[:6]) or "none recognized"
        emit(f"{_ts()} 🔎 {target['label']}: {names}")

    if concurrency <= 1:
        for target in candidates:
            if stop_event is not None and stop_event.is_set():
                break
            recognize_one(target)
    else:
        with ThreadPoolExecutor(max_workers=concurrency) as pool:
            list(pool.map(recognize_one, candidates))
    summary = f"recognize complete: {counts.get('done', 0)} image(s), {counts.get('failed', 0)} failed of {counts.get('total', 0)}"
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
    total_outlined = 0
    total_extracted = 0
    # Outline + extract advance group-by-group; loop until a whole round makes no
    # progress (no new outlines AND no new extractions), which also breaks out of
    # a persistently-failing outline instead of looping forever. The shared counts
    # dict is passed to each sub-stage so the websocket shows live current-stage
    # stats (stage/active/done/failed/total).
    for round_index in range(1, 41):
        if stop_event is not None and stop_event.is_set():
            return f"stopped during round {round_index}"
        emit(f"{_ts()} === full pipeline: outline (round {round_index}) ===")
        run_outline(workspace_id, counts=counts, **common)
        outlined_this = counts.get("done", 0)
        total_outlined += outlined_this
        if stop_event is not None and stop_event.is_set():
            return f"stopped during outline round {round_index}"
        emit(f"{_ts()} === full pipeline: extract (round {round_index}) ===")
        run_extract(workspace_id, counts=counts, **common)
        extracted_this = counts.get("done", 0)
        total_extracted += extracted_this
        if outlined_this == 0 and extracted_this == 0:
            emit(f"{_ts()} no further progress after round {round_index} — stopping")
            break
    # Finally turn every extracted leaf cutout into a Turtle program and render it
    # to a PNG (the terminal output of the pipeline).
    total_turtle = 0
    total_png = 0
    if stop_event is None or not stop_event.is_set():
        emit(f"{_ts()} === full pipeline: turtle-gen ===")
        run_turtle(workspace_id, counts=counts, **common)
        total_turtle = counts.get("done", 0)
    if stop_event is None or not stop_event.is_set():
        emit(f"{_ts()} === full pipeline: turtle-png ===")
        run_turtle_png(workspace_id, counts=counts, **common)
        total_png = counts.get("done", 0)
    summary = (
        f"full pipeline complete: {total_outlined} outlined, {total_extracted} extracted, "
        f"{total_turtle} turtle program(s), {total_png} PNG(s)"
    )
    emit(f"{_ts()} {summary}")
    return summary


_STAGE_RUNNERS: dict[str, Callable[..., str]] = {
    "describe": run_describe,
    "outline": run_outline,
    "extract": run_extract,
    "turtle": run_turtle,
    "turtlePng": run_turtle_png,
    "recognize": run_recognize,
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
