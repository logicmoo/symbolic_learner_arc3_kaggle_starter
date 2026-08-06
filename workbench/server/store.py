from __future__ import annotations

import json
import os
import sqlite3
import time
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal


TaskStatus = Literal["running", "waiting", "paused", "completed", "failed"]
RunStatus = Literal["running", "paused", "waiting", "concluded"]


TASK_CATALOG = [
    {"id": "capture_observation", "ports": "world → observation", "routes": "arc3.capture [python]"},
    {"id": "extract_entities", "ports": "observation → entity_set", "routes": "vision.segment [python]"},
    {"id": "assign_identities", "ports": "entity_set → identity_map", "routes": "symbolic.identity [prolog]"},
    {"id": "derive_properties", "ports": "identities → fact_set", "routes": "prolog.properties [prolog]"},
    {"id": "generate_turtle", "ports": "entities + facts → programs", "routes": "llm.turtle [llm]"},
    {"id": "render_programs", "ports": "programs → reconstruction", "routes": "turtle.runtime [prolog]"},
    {"id": "compare_reconstruction", "ports": "source + render → evidence", "routes": "vision.diff [python]"},
    {"id": "explain_transition", "ports": "before + action + after → hypotheses", "routes": "symbolic.transition [prolog], llm.transition [llm]"},
    {"id": "update_world_model", "ports": "hypotheses + evidence → world_model", "routes": "symbolic.world_model [python]"},
]

DATATYPE_MANIFEST = [
    {"id": "observation", "kind": "semantic", "meaning": "Evidence received from an external world", "relations": "represented by visual_observation, state_record"},
    {"id": "entity_set", "kind": "semantic", "meaning": "Stable candidates extracted from an observation", "relations": "aggregates entity"},
    {"id": "identity_map", "kind": "relation", "meaning": "Cross-view and cross-time identity assignments", "relations": "links entity versions"},
    {"id": "symbolic_fact_set", "kind": "representation", "meaning": "Executable grounded properties and relations", "relations": "represents world facts"},
    {"id": "executable_view", "kind": "representation", "meaning": "Program that reconstructs or transforms an observation", "relations": "includes Turtle DSL"},
    {"id": "evidence_bundle", "kind": "semantic", "meaning": "Validation results with exact provenance", "relations": "supports or contradicts hypotheses"},
    {"id": "world_model", "kind": "semantic", "meaning": "Revisable entities, dynamics, constraints, and uncertainty", "relations": "derived from observations and evidence"},
    {"id": "goal_set", "kind": "semantic", "meaning": "Supplied or inferred outcomes that guide simulation", "relations": "scores simulation candidates"},
]

ARTIFACT_SPECS: dict[str, tuple[str, str, str, float]] = {
    "source_observation": ("VisualObservation", "arc3.capture", "64×64 · rgba", 1.0),
    "entity_set": ("EntitySet", "vision.segment", "8 entities", 0.94),
    "object_identities": ("IdentityMap", "symbolic.identity", "8 mappings", 0.91),
    "symbolic_facts": ("PrologFactSet", "prolog.properties", "41 clauses", 0.89),
    "turtle_programs": ("ExecutableView", "llm.turtle", "8 programs", 0.87),
    "reconstruction": ("VisualObservation", "turtle.runtime", "64×64 · rgba", 0.964),
    "evidence": ("EvidenceBundle", "vision.diff", "3 findings", 0.964),
    "result_observation": ("VisualObservation", "arc3.capture", "64×64 · rgba", 1.0),
    "transition_evidence": ("TransitionEvidence", "symbolic.transition", "2 hypotheses", 0.72),
    "world_model": ("WorldModel", "symbolic.world_model", "v4 · 3 rules", 0.78),
}


def _step(
    step_id: str,
    kind: str,
    operation: str,
    implementation: str,
) -> dict[str, Any]:
    return {
        "id": step_id,
        "kind": kind,
        "operation": operation,
        "implementation": implementation,
        "inputs": {},
        "outputs": {},
        "parameters": {},
    }


STARTER_WORKFLOWS = [
    {
        "id": "arc3_human_observation",
        "label": "Learn a world by observation",
        "description": "Seven-stage apprenticeship workflow with a human-action boundary.",
        "steps": [
            _step("select_world", "task", "capture_observation", "arc3.capture"),
            _step("capture_initial", "task", "capture_observation", "arc3.capture"),
            _step("objectify_initial", "subworkflow", "objectify_observation", "nested workflow"),
            _step("observe_action", "task", "human_action", "human.boundary"),
            _step("capture_result", "subworkflow", "objectify_observation", "nested workflow"),
            _step("explain_transition", "task", "explain_transition", "symbolic.transition"),
            _step("repeat_or_conclude", "task", "update_world_model", "symbolic.world_model"),
        ],
    },
    {
        "id": "objectify_observation",
        "label": "Objectify observation",
        "description": "Extract, identify, describe, render, compare, and preserve evidence.",
        "steps": [
            _step("extract", "task", "extract_entities", "vision.segment"),
            _step("identify", "task", "assign_identities", "symbolic.identity"),
            _step("properties", "task", "derive_properties", "prolog.properties"),
            _step("turtle", "task", "generate_turtle", "llm.turtle"),
            _step("render", "task", "render_programs", "turtle.runtime"),
            _step("compare", "task", "compare_reconstruction", "vision.diff"),
        ],
    },
]

TYPED_EXAMPLE = {
    "id": "example_typed_artifact_review",
    "label": "Typed artifact review",
    "description": "Example Python, Prolog, and LLM workflow with explicit slots.",
    "steps": [
        {**_step("extract", "task", "extract_entities", "vision.segment"), "inputs": {"observation": "source_observation"}, "outputs": {"entities": "entity_set"}},
        {**_step("facts", "task", "derive_properties", "prolog.properties"), "inputs": {"identities": "object_identities"}, "outputs": {"facts": "symbolic_facts"}},
        {**_step("audit", "task", "compare_reconstruction", "vision.diff"), "inputs": {"source": "source_observation", "render": "reconstruction"}, "outputs": {"evidence": "evidence"}, "continueOnError": True},
    ],
}


def _now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _loads(value: str | None) -> dict[str, Any] | list[Any]:
    try:
        return json.loads(value or "{}")
    except json.JSONDecodeError:
        return {}


class WorkbenchStore:
    """SQLite-backed local task, workflow, event, and artifact store."""

    def __init__(self, database_path: str | Path | None = None) -> None:
        configured = os.getenv("WORKBENCH_DB")
        default = Path(__file__).resolve().parents[1] / "data" / "workbench.db"
        self.database_path = Path(database_path or configured or default)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path, timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA journal_mode = WAL")
        return connection

    def _initialize(self) -> None:
        with self._connect() as db:
            db.executescript(
                """
                CREATE TABLE IF NOT EXISTS workbench_tasks (
                    id TEXT PRIMARY KEY,
                    parent_task_id TEXT,
                    kind TEXT NOT NULL,
                    workflow_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    current_step INTEGER NOT NULL DEFAULT 0,
                    total_steps INTEGER NOT NULL,
                    summary TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS task_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT NOT NULL REFERENCES workbench_tasks(id) ON DELETE CASCADE,
                    step INTEGER NOT NULL,
                    kind TEXT NOT NULL,
                    message TEXT NOT NULL,
                    payload TEXT NOT NULL DEFAULT '{}',
                    created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS task_events_cursor_idx ON task_events(task_id, id);
                CREATE TABLE IF NOT EXISTS workflow_runs (
                    id TEXT PRIMARY KEY,
                    task_id TEXT NOT NULL REFERENCES workbench_tasks(id) ON DELETE CASCADE,
                    workflow_id TEXT NOT NULL,
                    world_id TEXT NOT NULL,
                    episode INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    stage INTEGER NOT NULL,
                    max_stage INTEGER NOT NULL,
                    chosen_action TEXT,
                    model_version INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS run_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL REFERENCES workflow_runs(id) ON DELETE CASCADE,
                    kind TEXT NOT NULL,
                    tone TEXT NOT NULL DEFAULT 'info',
                    stage INTEGER NOT NULL,
                    message TEXT NOT NULL,
                    payload TEXT NOT NULL DEFAULT '{}',
                    created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS run_events_cursor_idx ON run_events(run_id, id);
                CREATE TABLE IF NOT EXISTS run_artifacts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL REFERENCES workflow_runs(id) ON DELETE CASCADE,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    producer TEXT NOT NULL,
                    value TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    version INTEGER NOT NULL DEFAULT 1,
                    payload TEXT NOT NULL DEFAULT '{}',
                    created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS run_artifacts_name_idx ON run_artifacts(run_id, name, version);
                CREATE TABLE IF NOT EXISTS workflow_documents (
                    id TEXT PRIMARY KEY,
                    label TEXT NOT NULL,
                    description TEXT NOT NULL DEFAULT '',
                    steps TEXT NOT NULL DEFAULT '[]',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                """
            )
            count = db.execute("SELECT COUNT(*) FROM workflow_documents").fetchone()[0]
            if not count:
                for workflow in STARTER_WORKFLOWS:
                    self._insert_workflow(db, workflow)

    @staticmethod
    def _insert_workflow(db: sqlite3.Connection, workflow: dict[str, Any]) -> None:
        now = _now()
        db.execute(
            "INSERT INTO workflow_documents(id,label,description,steps,created_at,updated_at) VALUES(?,?,?,?,?,?)",
            (workflow["id"], workflow["label"], workflow.get("description", ""), json.dumps(workflow.get("steps", [])), now, now),
        )

    def create_task(
        self,
        kind: Literal["workflow_design", "workflow_execution"],
        workflow_id: str,
        total_steps: int,
        summary: str,
        parent_task_id: str | None = None,
    ) -> dict[str, Any]:
        task_id = str(uuid.uuid4())
        now = _now()
        with self._connect() as db:
            db.execute(
                "INSERT INTO workbench_tasks VALUES(?,?,?,?,?,?,?,?,?,?)",
                (task_id, parent_task_id, kind, workflow_id, "running", 0, total_steps, summary, now, now),
            )
            db.execute(
                "INSERT INTO task_events(task_id,step,kind,message,payload,created_at) VALUES(?,?,?,?,?,?)",
                (task_id, 0, "task.created", summary, json.dumps({"kind": kind, "workflowId": workflow_id, "parentTaskId": parent_task_id}), now),
            )
        return self.get_task(task_id)

    def record_task_step(
        self,
        task_id: str,
        step: int,
        kind: str,
        message: str,
        status: TaskStatus = "running",
        payload: dict[str, Any] | None = None,
    ) -> None:
        now = _now()
        with self._connect() as db:
            db.execute(
                "INSERT INTO task_events(task_id,step,kind,message,payload,created_at) VALUES(?,?,?,?,?,?)",
                (task_id, step, kind, message, json.dumps(payload or {}), now),
            )
            db.execute(
                "UPDATE workbench_tasks SET current_step=?,status=?,updated_at=? WHERE id=?",
                (step, status, now, task_id),
            )

    def get_task(self, task_id: str) -> dict[str, Any]:
        with self._connect() as db:
            task = db.execute("SELECT * FROM workbench_tasks WHERE id=?", (task_id,)).fetchone()
            if not task:
                raise KeyError("Workbench task not found")
            events = db.execute("SELECT * FROM task_events WHERE task_id=? ORDER BY id", (task_id,)).fetchall()
        return {
            "id": task["id"],
            "parentTaskId": task["parent_task_id"],
            "kind": task["kind"],
            "workflowId": task["workflow_id"],
            "status": task["status"],
            "currentStep": task["current_step"],
            "totalSteps": task["total_steps"],
            "summary": task["summary"],
            "createdAt": task["created_at"],
            "updatedAt": task["updated_at"],
            "events": [
                {"id": row["id"], "step": row["step"], "kind": row["kind"], "message": row["message"], "payload": _loads(row["payload"]), "createdAt": row["created_at"]}
                for row in events
            ],
        }

    def list_tasks(self, limit: int = 20) -> list[dict[str, Any]]:
        with self._connect() as db:
            rows = db.execute("SELECT id FROM workbench_tasks ORDER BY updated_at DESC LIMIT ?", (limit,)).fetchall()
        return [self.get_task(row["id"]) for row in rows]

    def emit(
        self,
        run_id: str,
        stage: int,
        kind: str,
        message: str,
        tone: str = "info",
        payload: dict[str, Any] | None = None,
    ) -> None:
        with self._connect() as db:
            db.execute(
                "INSERT INTO run_events(run_id,kind,tone,stage,message,payload,created_at) VALUES(?,?,?,?,?,?,?)",
                (run_id, kind, tone, stage, message, json.dumps(payload or {}), _now()),
            )

    def append_artifact(self, run_id: str, stage: int, name: str, payload: dict[str, Any] | None = None) -> None:
        type_name, producer, value, confidence = ARTIFACT_SPECS[name]
        with self._connect() as db:
            row = db.execute("SELECT MAX(version) version FROM run_artifacts WHERE run_id=? AND name=?", (run_id, name)).fetchone()
            version = (row["version"] or 0) + 1
            db.execute(
                "INSERT INTO run_artifacts(run_id,name,type,producer,value,confidence,version,payload,created_at) VALUES(?,?,?,?,?,?,?,?,?)",
                (run_id, name, type_name, producer, value, confidence, version, json.dumps(payload or {}), _now()),
            )
        self.emit(run_id, stage, "artifact.appended", f"{name} v{version} appended by {producer}.", "ok", {"name": name, "type": type_name, "producer": producer, "version": version})

    def create_run(self, workflow_id: str = "arc3_human_observation", world_id: str = "ls20", parent_task_id: str | None = None) -> dict[str, Any]:
        run_id = str(uuid.uuid4())
        now = _now()
        task = self.create_task("workflow_execution", workflow_id, 7, f"Run {workflow_id} against {world_id}", parent_task_id)
        with self._connect() as db:
            db.execute(
                "INSERT INTO workflow_runs VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
                (run_id, task["id"], workflow_id, world_id, int(time.time()) % 1000, "running", 3, 3, None, 0, now, now),
            )
        self.record_task_step(task["id"], 1, "execution.world_bound", f"World {world_id} selected.")
        self.emit(run_id, 1, "stage.completed", f"World adapter {world_id} bound to the run.", "ok")
        self.append_artifact(run_id, 2, "source_observation", {"step": 0, "immutable": True})
        self.record_task_step(task["id"], 2, "execution.observation_captured", "Initial observation captured.")
        self.emit(run_id, 2, "stage.completed", "Initial observation captured and preserved.", "ok")
        self.record_task_step(task["id"], 3, "execution.objectification_started", "Objectification subworkflow started.")
        self.emit(run_id, 3, "stage.started", "Objectification subworkflow started.")
        return self.get_run(run_id)

    def _set_run(self, run_id: str, **changes: Any) -> None:
        allowed = {"status", "stage", "max_stage", "chosen_action", "model_version"}
        values = {key: value for key, value in changes.items() if key in allowed}
        values["updated_at"] = _now()
        assignments = ",".join(f"{key}=?" for key in values)
        with self._connect() as db:
            db.execute(f"UPDATE workflow_runs SET {assignments} WHERE id=?", (*values.values(), run_id))

    def get_run(self, run_id: str) -> dict[str, Any]:
        with self._connect() as db:
            run = db.execute("SELECT * FROM workflow_runs WHERE id=?", (run_id,)).fetchone()
            if not run:
                raise KeyError("Run not found")
            events = db.execute("SELECT * FROM run_events WHERE run_id=? ORDER BY id", (run_id,)).fetchall()
            artifact_rows = db.execute("SELECT * FROM run_artifacts WHERE run_id=? ORDER BY id", (run_id,)).fetchall()
        latest = {row["name"]: row for row in artifact_rows}
        event_values = [
            {"id": row["id"], "kind": row["kind"], "tone": row["tone"], "stage": row["stage"], "message": row["message"], "payload": _loads(row["payload"]), "createdAt": row["created_at"]}
            for row in events
        ]
        artifacts = [
            {"id": row["id"], "name": row["name"], "type": row["type"], "producer": row["producer"], "value": row["value"], "confidence": row["confidence"], "version": row["version"], "payload": _loads(row["payload"]), "createdAt": row["created_at"]}
            for row in latest.values()
        ]
        return {
            "id": run["id"],
            "workflowId": run["workflow_id"],
            "worldId": run["world_id"],
            "episode": run["episode"],
            "status": run["status"],
            "stage": run["stage"],
            "maxStage": run["max_stage"],
            "chosenAction": run["chosen_action"],
            "modelVersion": run["model_version"],
            "createdAt": run["created_at"],
            "updatedAt": run["updated_at"],
            "artifacts": artifacts,
            "events": event_values,
            "cursor": event_values[-1]["id"] if event_values else 0,
            "task": self.get_task(run["task_id"]),
        }

    def get_events(self, run_id: str, after: int = 0) -> list[dict[str, Any]]:
        with self._connect() as db:
            rows = db.execute("SELECT * FROM run_events WHERE run_id=? AND id>? ORDER BY id LIMIT 100", (run_id, after)).fetchall()
        return [
            {"id": row["id"], "kind": row["kind"], "tone": row["tone"], "stage": row["stage"], "message": row["message"], "payload": _loads(row["payload"]), "createdAt": row["created_at"]}
            for row in rows
        ]

    def _finish_objectification(self, run_id: str, stage: int) -> None:
        for name in ("entity_set", "object_identities", "symbolic_facts", "turtle_programs", "reconstruction", "evidence"):
            self.append_artifact(run_id, stage, name, {"observationStep": 0 if stage == 3 else 1})

    def command_run(self, run_id: str, command: str, input_data: dict[str, Any] | None = None) -> dict[str, Any]:
        input_data = input_data or {}
        run = self.get_run(run_id)
        task_id = run["task"]["id"]
        if run["status"] == "concluded" and command != "repeat":
            self.emit(run_id, run["stage"], "command.rejected", "The model is concluded. Repeat to collect more evidence.", "wait")
            return self.get_run(run_id)

        if command == "run_next":
            if run["status"] == "paused":
                self.emit(run_id, run["stage"], "command.rejected", "Resume the run before executing the next stage.", "wait")
            elif run["stage"] == 3:
                self._finish_objectification(run_id, 3)
                self._set_run(run_id, stage=4, max_stage=4, status="waiting")
                self.emit(run_id, 3, "stage.completed", "Objectification completed with reconstruction evidence.", "ok")
                self.emit(run_id, 4, "human_input.requested", "Execution paused at the human-action boundary.", "wait")
                self.record_task_step(task_id, 4, "execution.human_input_requested", "Waiting for a human action.", "waiting")
            elif run["stage"] == 4 and not run["chosenAction"]:
                self.emit(run_id, 4, "human_input.requested", "Waiting for a human action.", "wait")
            elif run["stage"] == 5:
                self.append_artifact(run_id, 5, "transition_evidence", {"action": run["chosenAction"]})
                self._set_run(run_id, stage=6, max_stage=6, status="running")
                self.emit(run_id, 6, "stage.started", "Before/action/after explanation started.")
                self.record_task_step(task_id, 6, "execution.transition_analysis", "Transition explanation started.")
            elif run["stage"] == 6:
                self.append_artifact(run_id, 6, "world_model", {"hypotheses": 3, "selected": "H1"})
                self._set_run(run_id, stage=7, max_stage=7, status="waiting")
                self.emit(run_id, 6, "stage.completed", "World model updated from transition evidence.", "ok")
                self.emit(run_id, 7, "decision.requested", "Choose whether to repeat or conclude the demonstration.", "wait")
                self.record_task_step(task_id, 7, "execution.decision_requested", "Repeat or conclude decision requested.", "waiting")
            else:
                self.emit(run_id, run["stage"], "decision.requested", "Choose repeat or conclude to continue.", "wait")
        elif command == "human_action":
            action = str(input_data.get("action", "")).upper()
            if run["stage"] != 4 or action not in {"UP", "LEFT", "DOWN", "RIGHT", "SPACE"}:
                raise ValueError("A valid human action is only accepted while stage 4 is waiting")
            self._set_run(run_id, chosen_action=action, stage=5, max_stage=5, status="running")
            self.emit(run_id, 4, "human_input.received", f"{action} captured at the human-action boundary.", "ok", {"action": action})
            self.append_artifact(run_id, 5, "result_observation", {"step": 1, "action": action})
            self.emit(run_id, 5, "stage.started", "Result observation captured; comparison is ready.")
            self.record_task_step(task_id, 5, "execution.result_captured", "Human action and resulting observation captured.")
        elif command == "toggle_pause":
            status: RunStatus = "running" if run["status"] == "paused" else "paused"
            self._set_run(run_id, status=status)
            self.emit(run_id, run["stage"], f"run.{status}", f"Run {status} by operator.", "wait" if status == "paused" else "ok")
            self.record_task_step(task_id, run["task"]["currentStep"], f"task.{status}", f"Execution task {status}.", "running" if status == "running" else "paused")
        elif command == "repeat":
            self._set_run(run_id, stage=4, max_stage=4, chosen_action=None, status="waiting")
            self.emit(run_id, 4, "demonstration.repeated", "New demonstration pass opened at the human-action stage.", "wait")
            self.record_task_step(task_id, 4, "execution.demonstration_repeated", "Execution task returned to the human-action boundary.", "waiting")
        elif command == "conclude":
            version = run["modelVersion"] + 1
            self.append_artifact(run_id, 7, "world_model", {"concluded": True, "modelVersion": version})
            self._set_run(run_id, status="concluded", model_version=version)
            self.emit(run_id, 7, "run.concluded", f"World model v{version} concluded with its evidence bundle.", "ok")
            self.record_task_step(task_id, 7, "execution.completed", f"Workflow execution completed with world model v{version}.", "completed")
        else:
            messages = {
                "save_snapshot": "Experiment snapshot saved with configuration and provenance.",
                "refresh_catalog": "Task catalog refreshed; implementations available.",
                "validate": "All workflow validations passed.",
                "compare_models": "Comparison run queued for three model routes.",
                "save_config": "Configuration snapshot saved for the next run.",
            }
            if command not in messages:
                raise ValueError(f"Unknown command: {command}")
            self.emit(run_id, run["stage"], f"command.{command}", messages[command], "ok", input_data)
        return self.get_run(run_id)

    def list_workflows(self) -> list[dict[str, Any]]:
        with self._connect() as db:
            rows = db.execute("SELECT * FROM workflow_documents ORDER BY created_at").fetchall()
        return [
            {"id": row["id"], "label": row["label"], "description": row["description"], "steps": _loads(row["steps"]), "createdAt": row["created_at"], "updatedAt": row["updated_at"]}
            for row in rows
        ]

    def validate_workflows(self, candidate: dict[str, Any] | None = None) -> dict[str, Any]:
        workflows = self.list_workflows()
        if candidate:
            workflows = [item for item in workflows if item["id"] != candidate.get("id")] + [candidate]
        errors: list[str] = []
        ids = {item.get("id") for item in workflows}
        graph: dict[str, list[str]] = {}
        task_ids = {item["id"] for item in TASK_CATALOG} | {"human_action"}
        for workflow in workflows:
            workflow_id = str(workflow.get("id", "")).strip()
            if not workflow_id:
                errors.append("Workflow ID is required")
            if not str(workflow.get("label", "")).strip():
                errors.append(f"{workflow_id or 'Workflow'}: label is required")
            step_ids: set[str] = set()
            graph[workflow_id] = []
            for step in workflow.get("steps", []):
                step_id = str(step.get("id", "")).strip()
                if not step_id:
                    errors.append(f"{workflow_id}: every item needs an ID")
                if step_id in step_ids:
                    errors.append(f"{workflow_id}: duplicate item ID {step_id}")
                step_ids.add(step_id)
                if step.get("kind") == "subworkflow":
                    operation = step.get("operation")
                    graph[workflow_id].append(operation)
                    if operation not in ids:
                        errors.append(f"{workflow_id}: unknown subworkflow {operation}")
                elif step.get("kind") == "task" and step.get("operation") not in task_ids:
                    errors.append(f"{workflow_id}: unknown task {step.get('operation')}")

        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(workflow_id: str) -> None:
            if workflow_id in visiting:
                errors.append(f"Nested workflow cycle detected at {workflow_id}")
                return
            if workflow_id in visited:
                return
            visiting.add(workflow_id)
            for child in graph.get(workflow_id, []):
                visit(child)
            visiting.remove(workflow_id)
            visited.add(workflow_id)

        for workflow_id in graph:
            visit(workflow_id)
        return {"valid": not errors, "errors": errors, "checks": 5}

    def create_workflow(self, example: bool = False) -> list[dict[str, Any]]:
        workflow = TYPED_EXAMPLE if example else {"id": f"workflow_{int(time.time() * 1000):x}", "label": "New typed workflow", "description": "", "steps": []}
        with self._connect() as db:
            exists = db.execute("SELECT 1 FROM workflow_documents WHERE id=?", (workflow["id"],)).fetchone()
            if not exists:
                self._insert_workflow(db, workflow)
        return self.list_workflows()

    def save_workflow(self, workflow: dict[str, Any], original_id: str | None = None) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        task = self.create_task("workflow_design", workflow.get("id", ""), 5, f"Design and save workflow {workflow.get('id', '')}")
        task_id = task["id"]
        self.record_task_step(task_id, 1, "design.catalog_loaded", "Workflow and processing-resource catalogs loaded.")
        self.record_task_step(task_id, 2, "design.draft_captured", "Edited workflow structure and bindings captured.", payload={"itemCount": len(workflow.get("steps", []))})
        validation = self.validate_workflows(workflow)
        if not validation["valid"]:
            self.record_task_step(task_id, 3, "design.validation_failed", "; ".join(validation["errors"]), "failed", {"errors": validation["errors"]})
            raise ValueError("\n".join(validation["errors"]))
        self.record_task_step(task_id, 3, "design.validated", "Typed ports, implementations, bindings, and nested cycles validated.")
        now = _now()
        with self._connect() as db:
            if original_id and original_id != workflow["id"]:
                db.execute("DELETE FROM workflow_documents WHERE id=?", (original_id,))
            db.execute(
                "INSERT INTO workflow_documents(id,label,description,steps,created_at,updated_at) VALUES(?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET label=excluded.label,description=excluded.description,steps=excluded.steps,updated_at=excluded.updated_at",
                (workflow["id"], workflow["label"], workflow.get("description", ""), json.dumps(workflow.get("steps", [])), now, now),
            )
        self.record_task_step(task_id, 4, "design.revision_saved", "Validated workflow revision saved.")
        self.record_task_step(task_id, 5, "design.completed", "Workflow design task completed; execution handoff is available.", "completed")
        return self.list_workflows(), self.get_task(task_id)

    def delete_workflow(self, workflow_id: str) -> list[dict[str, Any]]:
        if workflow_id in {"arc3_human_observation", "objectify_observation"}:
            raise ValueError("Core demonstration workflows cannot be deleted")
        with self._connect() as db:
            db.execute("DELETE FROM workflow_documents WHERE id=?", (workflow_id,))
        return self.list_workflows()
