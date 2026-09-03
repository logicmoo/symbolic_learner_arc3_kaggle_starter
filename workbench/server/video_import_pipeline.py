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
import os
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
    # Center + radius variants (models often emit ellipse/circle as cx/cy/r,
    # rx/ry, or center:[x,y] + radius:r|[rx,ry] instead of a box).
    cx, cy = num("cx"), num("cy")
    center = command.get("center")
    if (cx is None or cy is None) and isinstance(center, (list, tuple)) and len(center) >= 2:
        try:
            cx, cy = float(center[0]), float(center[1])
        except (TypeError, ValueError):
            pass
    rx, ry = num("rx"), num("ry")
    radius_scalar = num("r") if "r" in command else num("radius")
    radius_value = command.get("radius")
    if (rx is None or ry is None) and isinstance(radius_value, (list, tuple)) and len(radius_value) >= 2:
        try:
            rx, ry = float(radius_value[0]), float(radius_value[1])
        except (TypeError, ValueError):
            pass
    if rx is None and radius_scalar is not None:
        rx = radius_scalar
    if ry is None and radius_scalar is not None:
        ry = radius_scalar
    # When x/y are present with a radius (and no width/height), treat them as the
    # center rather than a top-left corner.
    if cx is None and x is not None and rx is not None:
        cx = x
    if cy is None and y is not None and ry is not None:
        cy = y
    if None not in (cx, cy, rx, ry):
        return [cx - rx, cy - ry, cx + rx, cy + ry]  # type: ignore[operator]
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
    allowed_ops = {"pen", "move", "line", "polyline", "polygon", "rectangle", "ellipse", "dot"}

    def canon_op(name: Any) -> str:
        n = str(name or "").lower()
        return aliases.get(n, n)

    def num(value: Any) -> float | None:
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    def coerce(command: Any) -> dict[str, Any] | None:
        """Return a render-ready command, or None to drop it. Tolerates map-form,
        aliases, alternate coordinate shapes (points arrays, center+radius,
        x/y/w/h, size), and 'none' colors. Dropping malformed commands means one
        bad command no longer blanks the whole PNG (best-effort render)."""
        if not isinstance(command, dict):
            return None
        # MAP FORM: {"rectangle":{...}} -> {"op":"rectangle",...}
        if not command.get("op"):
            for key, value in list(command.items()):
                if isinstance(value, dict) and canon_op(key) in allowed_ops:
                    command = {"op": canon_op(key), **value}
                    break
        op = canon_op(command.get("op"))
        if op not in allowed_ops:
            return None
        command = {**command, "op": op}
        # "none" colors -> transparent (Pillow rejects the literal "none")
        for field in ("fill", "outline", "color"):
            if isinstance(command.get(field), str) and command[field].strip().lower() == "none":
                command[field] = "transparent"
        pts = _normalize_points(command.get("points") or command.get("vertices"))
        if pts is not None:
            command["points"] = pts
        if op == "pen":
            return command
        if op in ("move", "line", "dot"):
            x, y = num(command.get("x")), num(command.get("y"))
            if (x is None or y is None) and isinstance(command.get("points"), list) and command["points"]:
                # A "line" carrying >=2 points is really a polyline.
                if op == "line" and len(command["points"]) >= 2:
                    return {**command, "op": "polyline"}
                first = command["points"][0]
                command["x"], command["y"] = first[0], first[1]
            if op == "dot" and command.get("radius") is None and command.get("size") is not None:
                command["radius"] = command.get("size")
            if num(command.get("x")) is None or num(command.get("y")) is None:
                return None
            return command
        if op in ("rectangle", "ellipse"):
            box = command.get("box")
            if not (isinstance(box, list) and len(box) == 4 and all(num(b) is not None for b in box)):
                derived = _derive_box(command)
                if not derived:
                    return None
                command["box"] = derived
            return command
        if op in ("polygon", "polyline"):
            need = 3 if op == "polygon" else 2
            good = [p for p in (command.get("points") or []) if isinstance(p, (list, tuple)) and len(p) == 2 and num(p[0]) is not None and num(p[1]) is not None]
            if len(good) < need:
                return None
            command["points"] = [[float(p[0]), float(p[1])] for p in good]
            return command
        return None

    prog["commands"] = [c for c in (coerce(cmd) for cmd in commands) if c is not None]
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


def _turtle_gen(
    workspace_id: str,
    leaves: list[dict[str, Any]],
    *,
    model_override: str | None = None,
    model_state_key: str = "turtleModel",
    template_override: str | None = None,
    extra_artifact_fields: dict[str, Any] | None = None,
    concurrency_override: int | None = None,
    stop_event: threading.Event | None = None,
    log: Callable[[str], None] | None = None,
    counts: dict[str, int] | None = None,
) -> str:
    """Generate a Turtle drawing program for each supplied leaf cutout.

    Shared core for the Objects-page turtle stage (leaves from
    memberInventories) and the Recognition-page turtle stage (leaves from
    recognitionInventories). model_state_key / template_override let the
    Recognition rows use their own model + prompt."""
    emit = log or (lambda _msg: None)
    counts = counts if counts is not None else {}
    root = _workspace_root(workspace_id)
    state = load_state(workspace_id)
    model_id = _effective_stage_model(state, model_state_key, model_override)
    if not model_id:
        raise RuntimeError(f"no turtle model configured (set {model_state_key}/allCallsModel or pass --model)")
    if template_override is not None:
        template = template_override
    else:
        template = str(state.get("turtlePrompt") or "").strip()
        if not template or state.get("turtlePromptSelection") == "default":
            template = DEFAULT_TURTLE_PROMPT
    artifacts = state.get("turtleArtifacts") if isinstance(state.get("turtleArtifacts"), dict) else {}
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
            **(extra_artifact_fields or {}),
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
    """Generate a Turtle drawing program for every extracted Objects-page leaf."""
    state = load_state(workspace_id)
    return _turtle_gen(
        workspace_id,
        _collect_turtle_leaves(state),
        model_override=model_override,
        concurrency_override=concurrency_override,
        stop_event=stop_event,
        log=log,
        counts=counts,
    )


def _turtle_png(
    workspace_id: str,
    *,
    source_filter: set[str] | None = None,
    model_override: str | None = None,
    concurrency_override: int | None = None,
    stop_event: threading.Event | None = None,
    log: Callable[[str], None] | None = None,
    counts: dict[str, int] | None = None,
) -> str:
    """Turn generated Turtle programs into rendered PNGs. When source_filter is
    given, only artifacts whose sourceImage is in that set are rendered (so the
    Recognition stage renders only its own cutouts, not Objects-page leaves)."""
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
        and (source_filter is None or src in source_filter)
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
    """Turn every generated Turtle program into a rendered PNG (the final output)."""
    return _turtle_png(
        workspace_id,
        source_filter=None,
        model_override=model_override,
        concurrency_override=concurrency_override,
        stop_event=stop_event,
        log=log,
        counts=counts,
    )


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


# --------------------------------------------------------------------------- #
# Recognition experiment: one-pass describe+outline+extract, then match        #
# --------------------------------------------------------------------------- #

DEFAULT_ONEPASS_PROMPT = "\n".join([
    "ONE-PASS OBJECT DESCRIBE + OUTLINE.",
    "In a SINGLE pass, identify each distinct extractable object in this image AND give its exact pixel outline.",
    "{{goal}}",
    "PIXEL COORDINATE SPACE: width={{imageWidth}}, height={{imageHeight}}. Use x=0..{{maxX}} and y=0..{{maxY}} only.",
    "For each object return: name, a short description, polygons (one or more rings of >=3 pixel-coordinate [x,y] points tracing the visible silhouette), optional holes, an optional box [x0,y0,x1,y1] fallback, and a normalized 0..1000 traceTurtle (move/line commands) of the main contour.",
    "Trace only the pixels of each object; exclude neighbors, shadows, and background.",
    'Answer ONLY with JSON: {"description":"scene description","objects":[{"name":"short unique name","description":"visual identity","polygons":[[[x,y],...]],"holes":[],"box":[x0,y0,x1,y1],"traceTurtle":[{"op":"move","x":0,"y":0},{"op":"line","x":0,"y":0}]}]}',
])

# Recognition-page prompts — each stage row has its OWN editable prompt, decoupled
# from the Objects-page prompts. Prompts 1/2/3 are pure (no image instructions);
# only prompt 4 (Turtle → Image) is a real image-gen prompt.
DEFAULT_RECOGNIZE_ONEPASS_PROMPT = DEFAULT_ONEPASS_PROMPT

DEFAULT_RECOGNIZE_TURTLE_PROMPT = "\n".join([
    "TURTLE PROGRAM FROM A CUTOUT.",
    "The attached image is a single extracted object: {{subjectName}}.",
    "Description: {{description}}",
    "Write a turtle drawing program that reconstructs this one object as faithfully as possible.",
    "Coordinates are normalized 0..1000 with the origin at the top-left.",
    "Allowed ops: pen, move, line, polyline, polygon, rectangle, ellipse, dot. rectangle/ellipse require box:[x0,y0,x1,y1]; polyline/polygon require points:[[x,y],...]. Use at most 120 commands.",
    "EXAMPLE (a red circle on a transparent background):",
    '{"version":1,"background":"transparent","penColor":"#c0392b","penWidth":6,"commands":[{"op":"ellipse","box":[250,250,750,750],"fill":"#e74c3c"}]}',
    "Answer ONLY with the JSON object.",
])

DEFAULT_RECOGNIZE_OBJECTS_TURTLE_PROMPT = "\n".join([
    "ONE-PASS OBJECTS + TURTLE PROGRAMS.",
    "In a SINGLE pass, identify each distinct extractable object in this image, give its exact pixel outline, AND a turtle drawing program that reconstructs it.",
    "{{goal}}",
    "PIXEL COORDINATE SPACE for outlines: width={{imageWidth}}, height={{imageHeight}}. Use x=0..{{maxX}} and y=0..{{maxY}} only.",
    "For each object return: name, a short description, polygons (rings of >=3 pixel [x,y] points), optional holes, an optional box [x0,y0,x1,y1], a normalized 0..1000 traceTurtle (move/line) of the main contour, AND turtleProgram (a full turtle drawing program with coords normalized 0..1000; ops pen/move/line/polyline/polygon/rectangle/ellipse/dot; rectangle/ellipse need box, polyline/polygon need points).",
    'EXAMPLE turtleProgram (a red circle): {"version":1,"background":"transparent","penColor":"#c0392b","penWidth":6,"commands":[{"op":"ellipse","box":[250,250,750,750],"fill":"#e74c3c"}]}',
    'Answer ONLY with JSON: {"description":"scene description","objects":[{"name":"short unique name","description":"visual identity","polygons":[[[x,y],...]],"holes":[],"box":[x0,y0,x1,y1],"traceTurtle":[{"op":"move","x":0,"y":0}],"turtleProgram":{"version":1,"background":"transparent","penColor":"#RRGGBB","penWidth":4,"commands":[]}}]}',
])

DEFAULT_RECOGNIZE_TURTLE_PNG_PROMPT = "\n".join([
    "TURTLE → IMAGE.",
    "Render the object {{subjectName}} described by the turtle program below as a clean, faithful image.",
    "Description: {{description}}",
    "TURTLE PROGRAM:",
    "{{draftProgram}}",
    "Match the silhouette, colors, holes, and visible details. Transparent background unless the object needs one.",
])


def _recognition_prompt(state: dict[str, Any], key: str, selection_key: str, default: str) -> str:
    """Resolve a recognition stage prompt: workspace-edited text unless the row's
    selection is 'default'. Decoupled from the Objects-page prompts."""
    template = str(state.get(key) or "").strip()
    if not template or state.get(selection_key) == "default":
        return default
    return template


def _recognition_inputs(state: dict[str, Any]) -> list[dict[str, Any]]:
    """Images loaded on the Recognition page; fall back to the selected frames."""
    inputs = [f for f in (state.get("recognitionInputs") or []) if isinstance(f, dict) and f.get("path")]
    if inputs:
        return inputs
    return _selected_frame_paths(state, only_selected=True)


def persist_recognition_result(
    workspace_id: str, inventory: dict[str, Any], new_members: list[dict[str, Any]]
) -> None:
    with _page_state_lock(workspace_id):
        state = load_state(workspace_id)
        invs = [i for i in (state.get("recognitionInventories") or []) if isinstance(i, dict) and i.get("id") != inventory.get("id")]
        invs.append(inventory)
        state["recognitionInventories"] = invs
        members = [m for m in (state.get("recognitionMembers") or []) if isinstance(m, dict) and m.get("inventoryId") != inventory.get("id")]
        members.extend(new_members)
        state["recognitionMembers"] = members
        _save_page_state_payload({"workspaceId": workspace_id, "state": state})


def _persist_recognition_step(workspace_id: str, step: int) -> None:
    """Persist the recognition cutout step counter so subsequent runs keep
    advancing it — one-shot and two-shot cutouts then never share a filename."""
    with _page_state_lock(workspace_id):
        state = load_state(workspace_id)
        if int(state.get("recognitionStep") or 0) < step:
            state["recognitionStep"] = step
            _save_page_state_payload({"workspaceId": workspace_id, "state": state})


def parse_onepass_output(raw: str, *, capture_turtle: bool = False) -> dict[str, Any]:
    parsed = detect_json(raw)
    if not isinstance(parsed, dict):
        return {"description": "", "objects": []}
    objects: list[dict[str, Any]] = []
    seen: set[str] = set()
    for obj in parsed.get("objects") or []:
        if not isinstance(obj, dict):
            continue
        name = str(obj.get("name") or "").strip()[:60]
        key = name.lower()
        if not name or key in seen:
            continue
        seen.add(key)
        geom = parse_outline_geometry(json.dumps(obj))
        entry = {
            "name": name,
            "description": str(obj.get("description") or name).strip()[:320],
            "polygons": geom.get("polygons") or [],
            "holes": geom.get("holes") or [],
            "box": geom.get("box"),
            "traceTurtle": geom.get("traceTurtle") or [],
        }
        if capture_turtle:
            prog = obj.get("turtleProgram")
            if isinstance(prog, dict) and isinstance(prog.get("commands"), list):
                entry["turtleProgram"] = prog
        objects.append(entry)
    return {"description": str(parsed.get("description") or "").strip(), "objects": objects}


def run_recognize_onepass(
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
    """Describe + outline every object in ONE model call per image, then extract
    each outlined object into a cutout. A different 'cutting' than the Objects
    page (which describes, then outlines, then extracts in separate passes)."""
    emit = log or (lambda _msg: None)
    counts = counts if counts is not None else {}
    root = _workspace_root(workspace_id)
    state = load_state(workspace_id)
    model_id = _effective_stage_model(state, "recognizeOnepassModel", model_override)
    if not model_id:
        raise RuntimeError("no model configured (set recognizeOnepassModel/allCallsModel or pass --model)")
    goal = goal_override or str(state.get("memberGoal") or "any")
    goal_text = MEMBER_INVENTORY_GOALS.get(goal, MEMBER_INVENTORY_GOALS["any"])
    template = _recognition_prompt(state, "recognizeOnepassPrompt", "recognizeOnepassPromptSelection", DEFAULT_RECOGNIZE_ONEPASS_PROMPT)
    fill_mode = str(state.get("memberFill") or "transparent")
    inputs = _recognition_inputs(state)
    if not inputs:
        emit(f"{_ts()} no recognition images loaded (upload images or select frames)")
        return "no recognition images"
    concurrency = _stage_concurrency(state, "recognizer", concurrency_override, 2)
    counts["stage"] = "recognizeOnepass"
    counts["total"] = len(inputs)
    counts["done"] = 0
    counts["failed"] = 0
    counts["active"] = 0
    active = _Active(counts)
    step_lock = threading.Lock()
    step_counter = {"n": int(state.get("recognitionStep") or 0)}

    def next_step() -> int:
        with step_lock:
            step_counter["n"] += 1
            return step_counter["n"]

    emit(f"{_ts()} one-pass start · {len(inputs)} image(s) · model {model_id} · concurrency {concurrency}")

    def onepass_one(frame: dict[str, Any]) -> None:
        if stop_event is not None and stop_event.is_set():
            return
        path = str(frame.get("path"))
        index = int(frame.get("index") or 0)
        inventory_id = f"recog:two_shot:{path}"
        dims = image_dimensions(root, path)
        if not dims:
            counts["failed"] += 1
            emit(f"{_ts()} ✗ one-pass #{index}: could not load {path}")
            return
        width, height = dims
        prompt = (
            template.replace("{{goal}}", goal_text)
            .replace("{{imageWidth}}", str(width)).replace("{{imageHeight}}", str(height))
            .replace("{{maxX}}", str(max(0, width - 1))).replace("{{maxY}}", str(max(0, height - 1)))
        )
        image = image_to_data_url(root, path)
        try:
            with active:
                raw = invoke_model(root, model_id, prompt, image, 180).strip()
        except Exception as error:  # noqa: BLE001
            counts["failed"] += 1
            emit(f"{_ts()} ✗ one-pass #{index}: {error}")
            return
        parsed = parse_onepass_output(raw)
        objects = parsed["objects"]
        things: list[dict[str, Any]] = []
        new_members: list[dict[str, Any]] = []
        for obj in objects:
            if stop_event is not None and stop_event.is_set():
                break
            name = obj["name"]
            geom = clamp_geometry(obj, width, height)
            polygons = geom.get("polygons") or []
            box = geom.get("box")
            trace = obj.get("traceTurtle") or []
            thing: dict[str, Any] = {"name": name, "description": obj["description"], "status": "listed"}
            if (polygons or box) and trace:
                try:
                    verification = outline_verification({
                        "workspaceId": workspace_id, "image": path, "name": name,
                        "polygons": polygons, "holes": geom.get("holes") or [], "box": box,
                        "traceTurtle": trace, "plannerNumber": len(things) + 1,
                    })
                    cut = member_cut({
                        "workspaceId": workspace_id, "image": path,
                        "outlineSourceImage": path, "outlineSourceDimensions": {"width": width, "height": height},
                        "polygons": polygons, "holes": geom.get("holes") or [], "box": box,
                        "outlineVerificationImage": verification.get("verificationImage"),
                        "outlineGeometryHash": verification.get("geometryHash"),
                        "name": name, "step": next_step(), "fill": fill_mode, "fillInstructions": {},
                    })
                    cutout = str(cut.get("cutout") or "")
                    thing.update({
                        "status": "extracted", "outputImages": [cutout],
                        "outlinePolygons": polygons, "outlineBox": box, "outlineImage": path,
                        "outlineDimensions": {"width": width, "height": height},
                        "outlineVerificationImage": verification.get("verificationImage"),
                        "outlineGeometryHash": verification.get("geometryHash"),
                    })
                    new_members.append({
                        "framePath": path, "frameIndex": index, "name": name, "cutout": cutout,
                        "box": cut.get("box") or box or [0, 0, 0, 0], "step": step_counter["n"],
                        "status": "pending", "probeIndex": -1, "probeLabel": "recognition",
                        "inventoryId": inventory_id, "depth": 0, "method": "two_shot",
                        "provenance": str(cut.get("cutoutProvenance") or ""),
                    })
                except Exception as error:  # noqa: BLE001
                    thing.update({"status": "failed", "error": f"one-pass cut failed: {getattr(error, 'detail', None) or error}"})
            things.append(thing)
        inventory = {
            "id": inventory_id, "framePath": path, "frameIndex": index, "probeIndex": 0,
            "probeLabel": "recognition", "goal": goal, "sourceImage": path, "method": "two_shot",
            "descriptionOutput": raw, "sceneDescription": parsed["description"],
            "modelId": model_id, "depth": 0, "subjectName": f"recog_{index}",
            "status": "done", "things": things,
            "extractionOrder": [t["name"] for t in things],
            "parallelGroups": [[t["name"] for t in things]] if things else [],
        }
        persist_recognition_result(workspace_id, inventory, new_members)
        counts["done"] += 1
        emit(f"{_ts()} ✦ #{index}: {len(objects)} object(s), {len(new_members)} cut in one pass")

    if concurrency <= 1:
        for frame in inputs:
            if stop_event is not None and stop_event.is_set():
                break
            onepass_one(frame)
    else:
        with ThreadPoolExecutor(max_workers=concurrency) as pool:
            list(pool.map(onepass_one, inputs))
    _persist_recognition_step(workspace_id, step_counter["n"])
    summary = f"one-pass complete: {counts.get('done', 0)} image(s), {counts.get('failed', 0)} failed of {counts.get('total', 0)}"
    emit(f"{_ts()} {summary}")
    return summary


def run_recognize_objects_turtle(
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
    """Combined 1+2 in a SINGLE model call per image: find objects (+ outlines →
    cutouts) AND emit a turtle program per object. A one-shot alternative to
    running onepass then turtle. The PNG render stays a separate pass."""
    emit = log or (lambda _msg: None)
    counts = counts if counts is not None else {}
    root = _workspace_root(workspace_id)
    state = load_state(workspace_id)
    model_id = _effective_stage_model(state, "recognizeObjectsTurtleModel", model_override)
    if not model_id:
        raise RuntimeError("no model configured (set recognizeObjectsTurtleModel/allCallsModel or pass --model)")
    goal = goal_override or str(state.get("memberGoal") or "any")
    goal_text = MEMBER_INVENTORY_GOALS.get(goal, MEMBER_INVENTORY_GOALS["any"])
    template = _recognition_prompt(state, "recognizeObjectsTurtlePrompt", "recognizeObjectsTurtlePromptSelection", DEFAULT_RECOGNIZE_OBJECTS_TURTLE_PROMPT)
    fill_mode = str(state.get("memberFill") or "transparent")
    inputs = _recognition_inputs(state)
    if not inputs:
        emit(f"{_ts()} no recognition images loaded (upload images or select frames)")
        return "no recognition images"
    concurrency = _stage_concurrency(state, "recognizer", concurrency_override, 2)
    counts["stage"] = "recognizeObjectsTurtle"
    counts["total"] = len(inputs)
    counts["done"] = 0
    counts["failed"] = 0
    counts["active"] = 0
    active = _Active(counts)
    step_lock = threading.Lock()
    step_counter = {"n": int(state.get("recognitionStep") or 0)}

    def next_step() -> int:
        with step_lock:
            step_counter["n"] += 1
            return step_counter["n"]

    emit(f"{_ts()} objects+turtle start · {len(inputs)} image(s) · model {model_id} · concurrency {concurrency}")

    def pass_one(frame: dict[str, Any]) -> None:
        if stop_event is not None and stop_event.is_set():
            return
        path = str(frame.get("path"))
        index = int(frame.get("index") or 0)
        inventory_id = f"recog:one_shot:{path}"
        dims = image_dimensions(root, path)
        if not dims:
            counts["failed"] += 1
            emit(f"{_ts()} ✗ objects+turtle #{index}: could not load {path}")
            return
        width, height = dims
        prompt = (
            template.replace("{{goal}}", goal_text)
            .replace("{{imageWidth}}", str(width)).replace("{{imageHeight}}", str(height))
            .replace("{{maxX}}", str(max(0, width - 1))).replace("{{maxY}}", str(max(0, height - 1)))
        )
        image = image_to_data_url(root, path)
        try:
            with active:
                raw = invoke_model(root, model_id, prompt, image, 180).strip()
        except Exception as error:  # noqa: BLE001
            counts["failed"] += 1
            emit(f"{_ts()} ✗ objects+turtle #{index}: {error}")
            return
        parsed = parse_onepass_output(raw, capture_turtle=True)
        objects = parsed["objects"]
        things: list[dict[str, Any]] = []
        new_members: list[dict[str, Any]] = []
        turtle_arts: list[tuple[str, str, str, dict[str, Any]]] = []
        for obj in objects:
            if stop_event is not None and stop_event.is_set():
                break
            name = obj["name"]
            geom = clamp_geometry(obj, width, height)
            polygons = geom.get("polygons") or []
            box = geom.get("box")
            trace = obj.get("traceTurtle") or []
            thing: dict[str, Any] = {"name": name, "description": obj["description"], "status": "listed"}
            if (polygons or box) and trace:
                try:
                    verification = outline_verification({
                        "workspaceId": workspace_id, "image": path, "name": name,
                        "polygons": polygons, "holes": geom.get("holes") or [], "box": box,
                        "traceTurtle": trace, "plannerNumber": len(things) + 1,
                    })
                    cut = member_cut({
                        "workspaceId": workspace_id, "image": path,
                        "outlineSourceImage": path, "outlineSourceDimensions": {"width": width, "height": height},
                        "polygons": polygons, "holes": geom.get("holes") or [], "box": box,
                        "outlineVerificationImage": verification.get("verificationImage"),
                        "outlineGeometryHash": verification.get("geometryHash"),
                        "name": name, "step": next_step(), "fill": fill_mode, "fillInstructions": {},
                    })
                    cutout = str(cut.get("cutout") or "")
                    thing.update({
                        "status": "extracted", "outputImages": [cutout],
                        "outlinePolygons": polygons, "outlineBox": box, "outlineImage": path,
                        "outlineDimensions": {"width": width, "height": height},
                        "outlineVerificationImage": verification.get("verificationImage"),
                        "outlineGeometryHash": verification.get("geometryHash"),
                    })
                    new_members.append({
                        "framePath": path, "frameIndex": index, "name": name, "cutout": cutout,
                        "box": cut.get("box") or box or [0, 0, 0, 0], "step": step_counter["n"],
                        "status": "pending", "probeIndex": -1, "probeLabel": "recognition",
                        "inventoryId": inventory_id, "depth": 0, "method": "one_shot",
                        "provenance": str(cut.get("cutoutProvenance") or ""),
                    })
                    prog = obj.get("turtleProgram")
                    if cutout and isinstance(prog, dict) and isinstance(prog.get("commands"), list):
                        turtle_arts.append((cutout, name, obj["description"], prog))
                except Exception as error:  # noqa: BLE001
                    thing.update({"status": "failed", "error": f"objects+turtle cut failed: {getattr(error, 'detail', None) or error}"})
            things.append(thing)
        inventory = {
            "id": inventory_id, "framePath": path, "frameIndex": index, "probeIndex": 0,
            "probeLabel": "recognition", "goal": goal, "sourceImage": path, "method": "one_shot",
            "descriptionOutput": raw, "sceneDescription": parsed["description"],
            "modelId": model_id, "depth": 0, "subjectName": f"recog_{index}",
            "status": "done", "things": things,
            "extractionOrder": [t["name"] for t in things],
            "parallelGroups": [[t["name"] for t in things]] if things else [],
        }
        persist_recognition_result(workspace_id, inventory, new_members)
        # Persist the turtle PROGRAM per cutout (no image — the PNG is a separate
        # local-render pass). rawProgram lets the render/render-on-demand fill in.
        for cutout, name, description, prog in turtle_arts:
            persist_turtle_artifact(workspace_id, cutout, {
                "sourceImage": cutout, "subjectName": name, "description": description,
                "prompt": "", "rawProgram": json.dumps(prog, ensure_ascii=False),
                "status": "generated", "error": None, "failedStage": None, "method": "one_shot",
            })
        counts["done"] += 1
        emit(f"{_ts()} ✦ #{index}: {len(objects)} object(s), {len(new_members)} cut, {len(turtle_arts)} turtle program(s)")

    if concurrency <= 1:
        for frame in inputs:
            if stop_event is not None and stop_event.is_set():
                break
            pass_one(frame)
    else:
        with ThreadPoolExecutor(max_workers=concurrency) as pool:
            list(pool.map(pass_one, inputs))
    _persist_recognition_step(workspace_id, step_counter["n"])
    summary = f"objects+turtle complete: {counts.get('done', 0)} image(s), {counts.get('failed', 0)} failed of {counts.get('total', 0)}"
    emit(f"{_ts()} {summary}")
    return summary


# --- Matching: recognition cutouts vs Objects-page cutouts, with probability ---

def _load_thumb(root: Path, rel: str, size: int) -> Any:
    from PIL import Image  # noqa: PLC0415
    if not rel:
        return None
    p = (root / rel).resolve()
    try:
        p.relative_to(root.resolve())
    except ValueError:
        return None
    if not p.is_file():
        return None
    try:
        im = Image.open(p).convert("RGBA")
    except Exception:  # noqa: BLE001
        return None
    im.thumbnail((size, size))
    return im


def _contact_sheet(root: Path, members: list[dict[str, Any]], cols: int = 5, cell: int = 150) -> Any:
    from PIL import Image, ImageDraw, ImageFont  # noqa: PLC0415
    rows = max(1, (len(members) + cols - 1) // cols)
    sheet = Image.new("RGBA", (cols * cell, rows * cell), (18, 22, 28, 255))
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 18)
    except OSError:
        font = ImageFont.load_default()
    for idx, m in enumerate(members):
        r, c = divmod(idx, cols)
        x, y = c * cell, r * cell
        thumb = _load_thumb(root, m.get("cutout") or "", cell - 26)
        if thumb is not None:
            sheet.alpha_composite(thumb, (x + 13, y + 24))
        draw.text((x + 6, y + 4), str(idx + 1), fill=(255, 230, 0, 255), font=font)
    return sheet


def _img_to_dataurl(im: Any) -> str:
    import io  # noqa: PLC0415
    buf = io.BytesIO()
    im.convert("RGBA").save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")


def run_recognize_match(
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
    """Match each recognition cutout against the Objects-page cutouts and record
    the best match with a probability. Uses one model call per recognition cutout:
    the query image over a numbered contact sheet of all object cutouts."""
    from PIL import Image  # noqa: PLC0415
    emit = log or (lambda _msg: None)
    counts = counts if counts is not None else {}
    root = _workspace_root(workspace_id)
    state = load_state(workspace_id)
    model_id = _effective_stage_model(state, "describerModel", model_override)
    if not model_id:
        raise RuntimeError("no model configured (set describerModel/allCallsModel or pass --model)")
    object_members = [m for m in (state.get("members") or []) if isinstance(m, dict) and m.get("cutout")]
    recog_members = [m for m in (state.get("recognitionMembers") or []) if isinstance(m, dict) and m.get("cutout")]
    if not object_members:
        emit(f"{_ts()} no Objects-page cutouts to match against (extract on the Objects page first)")
        return "no object cutouts"
    if not recog_members:
        emit(f"{_ts()} no recognition cutouts (run one-pass first)")
        return "no recognition cutouts"
    sheet = _contact_sheet(root, object_members)
    concurrency = _stage_concurrency(state, "recognizer", concurrency_override, 2)
    counts["stage"] = "recognizeMatch"
    counts["total"] = len(recog_members)
    counts["done"] = 0
    counts["failed"] = 0
    counts["active"] = 0
    active = _Active(counts)
    emit(f"{_ts()} match start · {len(recog_members)} query cutout(s) vs {len(object_members)} object cutout(s) · model {model_id}")
    prompt = (
        "The TOP image is a QUERY object. Below it is a numbered grid of CANDIDATE objects (1.."
        f"{len(object_members)}). Which candidate is the SAME object/character as the query? "
        'Answer ONLY with JSON: {"bestIndex": <1-based index, or 0 if none match>, "probability": 0.0, "reason": "..."}.'
    )
    results: dict[str, Any] = {}
    results_lock = threading.Lock()

    def match_one(query: dict[str, Any]) -> None:
        if stop_event is not None and stop_event.is_set():
            return
        thumb = _load_thumb(root, query.get("cutout") or "", 220)
        if thumb is None:
            counts["failed"] += 1
            return
        canvas = Image.new("RGBA", (max(thumb.width, sheet.width), thumb.height + sheet.height + 12), (10, 12, 16, 255))
        canvas.alpha_composite(thumb, (0, 0))
        canvas.alpha_composite(sheet, (0, thumb.height + 12))
        try:
            with active:
                raw = invoke_model(root, model_id, prompt, _img_to_dataurl(canvas), 120).strip()
        except Exception as error:  # noqa: BLE001
            counts["failed"] += 1
            emit(f"{_ts()} ✗ match {query.get('name')}: {error}")
            return
        parsed = detect_json(raw)
        best_index = 0
        probability = 0.0
        reason = ""
        if isinstance(parsed, dict):
            try:
                best_index = int(parsed.get("bestIndex") or 0)
            except (TypeError, ValueError):
                best_index = 0
            try:
                probability = round(float(parsed.get("probability") or 0.0), 2)
            except (TypeError, ValueError):
                probability = 0.0
            reason = str(parsed.get("reason") or "")
        matched = object_members[best_index - 1] if 1 <= best_index <= len(object_members) else None
        entry = {
            "queryCutout": query.get("cutout"),
            "queryName": query.get("name"),
            "matchedCutout": matched.get("cutout") if matched else None,
            "matchedName": matched.get("name") if matched else None,
            "probability": probability,
            "reason": reason,
        }
        with results_lock:
            results[query.get("cutout")] = entry
        counts["done"] += 1
        label = f"{matched.get('name')} ({probability:.0%})" if matched else "no match"
        emit(f"{_ts()} 🔗 {query.get('name')} → {label}")

    if concurrency <= 1:
        for query in recog_members:
            if stop_event is not None and stop_event.is_set():
                break
            match_one(query)
    else:
        with ThreadPoolExecutor(max_workers=concurrency) as pool:
            list(pool.map(match_one, recog_members))
    with _page_state_lock(workspace_id):
        state = load_state(workspace_id)
        existing = state.get("recognitionMatches") if isinstance(state.get("recognitionMatches"), dict) else {}
        existing.update(results)
        state["recognitionMatches"] = existing
        _save_page_state_payload({"workspaceId": workspace_id, "state": state})
    summary = f"match complete: {counts.get('done', 0)} matched, {counts.get('failed', 0)} failed of {counts.get('total', 0)}"
    emit(f"{_ts()} {summary}")
    return summary


# --- Recognition turtle: turtleize the content inside recognition outlines --- #

def _collect_recognition_turtle_leaves(state: dict[str, Any], method: str | None = None) -> list[dict[str, Any]]:
    """Every recognition cutout (content inside a found outline) is a leaf for
    turtle rendering — same shape as _collect_turtle_leaves but sourced from the
    Recognition page's recognitionInventories. When `method` is given, only
    inventories tagged with that method (e.g. 'two_shot') are considered."""
    leaves: list[dict[str, Any]] = []
    seen: set[str] = set()
    for inv in state.get("recognitionInventories") or []:
        if not isinstance(inv, dict):
            continue
        if method is not None and str(inv.get("method") or "") != method:
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


def run_recognize_turtle(
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
    """Make a Turtle program from the content inside each recognition outline
    (generation only — the PNG render is a separate pass, run_recognize_turtle_png).
    Step 2 of the TWO-SHOT path: scoped to two_shot cutouts, tagged two_shot."""
    emit = log or (lambda _msg: None)
    counts = counts if counts is not None else {}
    state = load_state(workspace_id)
    leaves = _collect_recognition_turtle_leaves(state, method="two_shot")
    if not leaves:
        emit(f"{_ts()} no recognition cutouts to turtle (run 'Make Outline from Image' first)")
        return "no recognition cutouts"
    template = _recognition_prompt(state, "recognizeTurtlePrompt", "recognizeTurtlePromptSelection", DEFAULT_RECOGNIZE_TURTLE_PROMPT)
    return _turtle_gen(
        workspace_id, leaves,
        model_state_key="recognizeTurtleModel", template_override=template,
        extra_artifact_fields={"method": "two_shot"},
        model_override=model_override, concurrency_override=concurrency_override,
        stop_event=stop_event, log=emit, counts=counts,
    )


def _turtle_render_local(
    workspace_id: str,
    leaves: list[dict[str, Any]],
    *,
    concurrency_override: int | None = None,
    stop_event: threading.Event | None = None,
    log: Callable[[str], None] | None = None,
    counts: dict[str, int] | None = None,
) -> str:
    """Render each turtle program to a PNG with the LOCAL deterministic renderer
    (no model / no prompt). Best-effort: per-item failures are recorded, never
    raised, so a slow or bad render never fails a stage."""
    emit = log or (lambda _msg: None)
    counts = counts if counts is not None else {}
    state = load_state(workspace_id)
    artifacts = state.get("turtleArtifacts") if isinstance(state.get("turtleArtifacts"), dict) else {}
    candidates: list[tuple[dict[str, Any], dict[str, Any]]] = []
    seen: set[str] = set()
    for leaf in leaves:
        src = leaf["sourceImage"]
        if src in seen:
            continue
        seen.add(src)
        art = artifacts.get(src) or {}
        if art.get("rawProgram") and not art.get("renderedImage"):
            candidates.append((leaf, art))
    if not candidates:
        emit(f"{_ts()} nothing to render (no un-rendered turtle programs)")
        return "nothing to render"
    concurrency = _stage_concurrency(state, "recognizeTurtlePng", concurrency_override, 1)
    counts["stage"] = "turtlePng"
    counts["total"] = len(candidates)
    counts["done"] = 0
    counts["failed"] = 0
    counts["active"] = 0
    active = _Active(counts)
    emit(f"{_ts()} local turtle render start · {len(candidates)} program(s) · concurrency {concurrency}")

    def render_one(pair: tuple[dict[str, Any], dict[str, Any]]) -> None:
        if stop_event is not None and stop_event.is_set():
            return
        leaf, art = pair
        src = leaf["sourceImage"]
        subject = str(art.get("subjectName") or leaf.get("subjectName") or "object")
        raw = str(art.get("rawProgram") or "")
        program = normalize_turtle_program(raw) or raw
        try:
            with active:
                result = turtle_render({
                    "workspaceId": workspace_id, "sourceImage": src,
                    "subjectName": subject, "modelId": "local", "prompt": "",
                    "program": program,
                })
        except Exception as error:  # noqa: BLE001
            counts["failed"] += 1
            message = str(getattr(error, "detail", None) or error)
            emit(f"{_ts()} ✗ local render {subject}: {message}")
            persist_turtle_artifact(workspace_id, src, {**art, "status": "failed", "failedStage": "png", "error": message})
            return
        persist_turtle_artifact(workspace_id, src, {
            **art,
            "programPath": str(result.get("programPath") or ""),
            "renderedImage": str(result.get("renderedImage") or ""),
            "provenance": str(result.get("provenance") or ""),
            "status": "rendered", "error": None, "failedStage": None,
        })
        counts["done"] += 1
        emit(f"{_ts()} 🐢 rendered {subject} ({counts['done']}/{counts['total']}): {result.get('renderedImage')}")

    if concurrency <= 1:
        for pair in candidates:
            if stop_event is not None and stop_event.is_set():
                break
            render_one(pair)
    else:
        with ThreadPoolExecutor(max_workers=concurrency) as pool:
            list(pool.map(render_one, candidates))
    summary = f"local turtle render complete: {counts.get('done', 0)} rendered, {counts.get('failed', 0)} failed of {counts.get('total', 0)}"
    emit(f"{_ts()} {summary}")
    return summary


def run_recognize_turtle_png(
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
    """Denote each recognition Turtle program with its locally-rendered image —
    a pure local code render (turtle_render → PNG), no model/prompt. UI-only and
    best-effort. Scoped to recognition cutouts only."""
    emit = log or (lambda _msg: None)
    counts = counts if counts is not None else {}
    state = load_state(workspace_id)
    leaves = _collect_recognition_turtle_leaves(state)
    if not leaves:
        emit(f"{_ts()} no recognition turtle programs to render (run 'Make Turtle' first)")
        return "no recognition cutouts"
    return _turtle_render_local(
        workspace_id, leaves,
        concurrency_override=concurrency_override,
        stop_event=stop_event, log=emit, counts=counts,
    )


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


_REDUCE_SLUG_ORDER = [
    "bart_simpson", "lisa_simpson", "homer_simpson", "marge_simpson",
    "maggie_simpson", "grandpa_simpson", "spongebob", "patrick_star",
    "squidward", "scooby_doo", "shaggy", "mickey_mouse", "minnie_mouse",
    "donald_duck", "goofy", "bugs_bunny", "pikachu", "mario", "sonic", "moana",
]
_REDUCE_COND_ORDER = [
    "c1_bw", "c2_flip", "c3_rot45", "c4_busy", "c5_new",
    "c6_verybusy", "c7_withchars", "c8_typical", "c9_colorful", "c10_modality",
]
_REDUCE_TRANSFORMS = {"c1_bw", "c2_flip", "c3_rot45"}
# Independent per-tier stage panels (NO composite blob). Each of these is saved
# as its OWN PNG so every image/stage is fully independent in the UI.
_REDUCE_STAGE_KEYS = ["parts", "turtle", "partmap"]
_reduce_manifest_lock = threading.Lock()


def _reduce_lab_dir() -> Path:
    """The parent turtle_prompt_lab that owns the proven reduction code."""
    override = os.environ.get("REDUCE_LAB_DIR")
    if override and Path(override).is_dir():
        return Path(override)
    default = Path.home() / ".copilot" / "session-state" / \
        "d8ae6703-980e-4204-b654-bd655b9bf145" / "files" / "turtle_prompt_lab"
    return default


def run_reduce(
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
    """Reduction PREPASS as a pooled server stage that uses the PARENT'S proven
    turtle code (turtle_prompt_lab): for every condition image it runs the parent
    1-shot + 2-shot extraction, renders each stage panel (parts / turtle-to-PNG
    with colors / part-map) as its OWN independent PNG (never a composite blob),
    writes per-tier .metta, and streams counts. All images fan out through one
    ThreadPoolExecutor at the configured max-processes."""
    emit = log or (lambda _msg: None)
    counts = counts if counts is not None else {}
    root = _workspace_root(workspace_id)
    state = load_state(workspace_id)

    lab = _reduce_lab_dir()
    if not lab.is_dir():
        raise RuntimeError(f"parent turtle_prompt_lab not found: {lab} (set REDUCE_LAB_DIR)")
    if str(lab) not in sys.path:
        sys.path.insert(0, str(lab))
    import reduce_pool as rp  # noqa: PLC0415  (parent's proven reduction module)
    from PIL import Image  # noqa: PLC0415

    bases = ["data/recognition_reduce", "data/arc3_games/curated/recognition_reduce"]
    base_rel = next((b for b in bases if (root / b / "pool").is_dir()), bases[0])
    ws_dir = root / base_rel
    stages_dir = ws_dir / "stages"
    sym_dir = ws_dir / "sym"
    stages_dir.mkdir(parents=True, exist_ok=True)
    sym_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = ws_dir / "manifest.json"

    prov: dict[str, Any] = {}
    for b in bases:
        pp = root / b / "provenance.json"
        if pp.is_file():
            try:
                loaded = json.loads(pp.read_text(encoding="utf-8"))
                if isinstance(loaded, dict):
                    prov = loaded
                break
            except (OSError, json.JSONDecodeError):
                pass

    def order_key(idv: str) -> tuple[int, int]:
        slug, _, cond = idv.partition("__")
        s = _REDUCE_SLUG_ORDER.index(slug) if slug in _REDUCE_SLUG_ORDER else 99
        c = _REDUCE_COND_ORDER.index(cond) if cond in _REDUCE_COND_ORDER else 99
        return (s, c)

    pool_dir = ws_dir / "pool"
    canon = {f"{s}__{c}" for s in _REDUCE_SLUG_ORDER for c in _REDUCE_COND_ORDER}
    entries = [e for e in rp.build_pool() if (pool_dir / f"{e['id']}.jpg").is_file() and e["id"] in canon]
    entries.sort(key=lambda e: order_key(e["id"]))

    # Tiers to run. The parent's 2-shot (nshot) extraction is currently broken
    # (returns empty), so we run the reliable 1-shot tier only unless
    # REDUCE_TIERS is explicitly set in the environment. Each tier spec is
    # re-created per item inside reduce_one via _tier_specs() so parallel workers
    # don't share mutable tier dicts.
    def _tier_specs() -> list[dict[str, Any]]:
        specs = rp._tiers()
        return specs if os.environ.get("REDUCE_TIERS") else specs[:1]

    tiers_meta = [{"shots": t["shots"], "kind": t["kind"], "model": rp._short(t["model"])} for t in _tier_specs()]
    manifest_rows: dict[str, dict[str, Any]] = {}
    if manifest_path.is_file():
        try:
            existing = json.loads(manifest_path.read_text(encoding="utf-8"))
            for it in (existing.get("items") or []):
                if isinstance(it, dict) and it.get("id"):
                    manifest_rows[str(it["id"])] = it
        except (OSError, json.JSONDecodeError):
            pass

    nocache = os.environ.get("REDUCE_NOCACHE") == "1"
    counts["stage"] = "reduce"
    counts["total"] = len(entries)
    counts["done"] = 0
    counts["failed"] = 0
    counts["active"] = 0
    active = _Active(counts)
    # Reduction is I/O-bound on the model relay, so allow a wide fan-out. Default
    # to 19 workers (cap 19) to get all 200 done fast; overridable per call.
    concurrency = min(19, concurrency_override or _stage_concurrency(state, "recognizer", None, 19))
    emit(f"{_ts()} reduce start · {len(entries)} image(s) · tiers "
         f"{', '.join(f'{t['shots']}-shot/{t['model']}' for t in tiers_meta)} · concurrency {concurrency}")

    def _write_manifest() -> None:
        ordered = [manifest_rows[i] for i in sorted(manifest_rows, key=order_key)]
        payload = {"tiers": tiers_meta, "count": len(ordered), "items": ordered}
        with _reduce_manifest_lock:
            manifest_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _save_png(img: "Image.Image", name: str) -> str:
        (stages_dir / name).parent.mkdir(parents=True, exist_ok=True)
        img.convert("RGB").save(stages_dir / name, quality=92)
        return f"{base_rel}/stages/{name}"

    def reduce_one(entry: dict[str, Any]) -> None:
        if stop_event is not None and stop_event.is_set():
            return
        idv, slug, cond = entry["id"], entry["slug"], entry["cond"]
        src_path = pool_dir / f"{idv}.jpg"
        expected_sym = [sym_dir / f"{idv}__{t['shots']}shot.metta" for t in tiers_meta]
        expected_png = [stages_dir / f"{idv}__t{t['shots']}__{k}.png" for t in tiers_meta for k in _REDUCE_STAGE_KEYS]
        if (not nocache and idv in manifest_rows
                and all(p.is_file() for p in expected_sym)
                and all(p.is_file() for p in expected_png)):
            counts["done"] += 1
            return
        try:
            with active:
                src = Image.open(src_path).convert("RGB")
                scene = cond in rp.SCENE_CONDS
                tiers = _tier_specs()
                for tier in tiers:
                    tier["data"] = rp._extract_tier(src_path, tier, idv, scene)
                    tier["facts"] = rp._tier_facts(slug, tier)
                ref = tiers[0]["facts"]
                for tier in tiers[1:]:
                    tier["agree"] = rp.agreement(ref, tier["facts"])
                rows: list[dict[str, Any]] = []
                for tier in tiers:
                    # parent panels: [input, parts-found, turtle-render, part-map, graph]
                    panels, _boxes = rp._tier_panels(tier, src)
                    shots = tier["shots"]
                    stage_imgs = {"parts": panels[1], "turtle": panels[2], "partmap": panels[3]}
                    stage_paths = {k: _save_png(stage_imgs[k], f"{idv}__t{shots}__{k}.png") for k in _REDUCE_STAGE_KEYS}
                    sym_path = sym_dir / f"{idv}__{shots}shot.metta"
                    sym_path.write_text(rp.to_metta(tier["facts"]), encoding="utf-8")
                    rows.append({
                        "shots": shots, "kind": tier["kind"], "model": rp._short(tier["model"]),
                        "nparts": tier["facts"]["nparts"], "nrels": len(tier["facts"]["relations"]),
                        "metta": sym_path.name, "stages": stage_paths,
                        "agree": tier.get("agree", {"score": 1.0, "verdict": "ref"}),
                    })
        except Exception as error:  # noqa: BLE001
            counts["failed"] += 1
            emit(f"{_ts()} ✗ reduce {idv}: {error}")
            return
        pv = prov.get(idv) or {}
        source = pv.get("source") or ("web" if cond in rp.WEB_CONDS else "transform")
        manifest_rows[idv] = {
            "id": idv, "slug": slug, "cond": cond, "label": entry.get("label") or slug.replace("_", " "),
            "input": f"{idv}.jpg", "source": source, "source_url": pv.get("source_url", ""),
            "scene": cond in rp.SCENE_CONDS, "rows": rows,
        }
        _write_manifest()
        counts["done"] += 1
        ag = rows[1]["agree"].get("verdict") if len(rows) > 1 else "ref"
        emit(f"{_ts()} ✦ {idv}: {rows[0]['nparts']}p / {rows[-1]['nparts']}p · agree {ag}")

    if not entries:
        emit(f"{_ts()} no pool images in {base_rel}/pool (nothing to reduce)")
        return "no pool images"
    if concurrency <= 1:
        for entry in entries:
            if stop_event is not None and stop_event.is_set():
                break
            reduce_one(entry)
    else:
        with ThreadPoolExecutor(max_workers=concurrency) as pool:
            list(pool.map(reduce_one, entries))
    _write_manifest()
    summary = f"reduce complete: {counts.get('done', 0)} image(s), {counts.get('failed', 0)} failed of {counts.get('total', 0)}"
    emit(f"{_ts()} {summary}")
    return summary


_STAGE_RUNNERS: dict[str, Callable[..., str]] = {
    "describe": run_describe,
    "outline": run_outline,
    "extract": run_extract,
    "turtle": run_turtle,
    "turtlePng": run_turtle_png,
    "recognize": run_recognize,
    "recognizeOnepass": run_recognize_onepass,
    "recognizeObjectsTurtle": run_recognize_objects_turtle,
    "recognizeMatch": run_recognize_match,
    "recognizeTurtle": run_recognize_turtle,
    "recognizeTurtlePng": run_recognize_turtle_png,
    "reduce": run_reduce,
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
