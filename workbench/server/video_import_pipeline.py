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
    """Read-modify-write the memberInventories shard for one inventory.

    Serialized by the page-state lock so concurrent describe workers cannot lose
    each other's updates.
    """
    with _page_state_lock(workspace_id):
        state = load_state(workspace_id)
        inventories = [
            item
            for item in (state.get("memberInventories") or [])
            if isinstance(item, dict) and item.get("id") != inventory.get("id")
        ]
        inventories.append(inventory)
        # Persist only the memberInventories shard; omit modelResponseCache so the
        # empty-overwrite guard keeps the existing cache intact.
        _save_page_state_payload(
            {
                "workspaceId": workspace_id,
                "state": {"memberInventories": inventories},
            }
        )


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


_STAGE_RUNNERS: dict[str, Callable[..., str]] = {
    "describe": run_describe,
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
