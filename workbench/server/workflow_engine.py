from __future__ import annotations

import hashlib
import json
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable
from resource_store import get_filesystem_provider


def now() -> str:
    return datetime.now(UTC).isoformat().replace('+00:00', 'Z')


def digest(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(',', ':'), default=str).encode()
    return hashlib.sha256(raw).hexdigest()


@dataclass(frozen=True)
class OperationSpec:
    name: str
    inputs: dict[str, Any]
    outputs: dict[str, Any]
    handler: Callable[[dict[str, Any], dict[str, Any]], dict[str, Any]]


class OperationRegistry:
    def __init__(self) -> None:
        self._operations: dict[str, OperationSpec] = {}

    def register(self, spec: OperationSpec) -> None:
        if spec.name in self._operations:
            raise ValueError(f'operation already registered: {spec.name}')
        self._operations[spec.name] = spec

    def get(self, name: str) -> OperationSpec:
        if name not in self._operations:
            raise KeyError(f'unknown operation implementation: {name}')
        return self._operations[name]

    def describe(self) -> list[dict[str, Any]]:
        return [{'name': s.name, 'inputs': s.inputs, 'outputs': s.outputs} for s in self._operations.values()]


class WorkflowEngine:
    """Durable typed workflow engine with nested workflows and human waits."""

    TERMINAL = {'completed', 'failed', 'cancelled'}

    @staticmethod
    def _normalize_output_bindings(value: Any) -> dict[str, Any]:
        """Accept concise same-name output lists as well as explicit mappings."""
        if isinstance(value, list):
            return {str(name): str(name) for name in value}
        return dict(value or {})

    @classmethod
    def _normalize_workflow(cls, document: dict[str, Any]) -> dict[str, Any]:
        normalized = {**document}
        normalized['steps'] = [
            {**step, 'outputs': cls._normalize_output_bindings(step.get('outputs'))}
            for step in document.get('steps') or []
        ]
        return normalized

    @staticmethod
    def _infer_capture_group_plan(document: dict[str, Any]) -> list[dict[str, Any]]:
        steps = document.get('steps') or []
        writes: dict[str, list[int]] = {}
        for step_index, step in enumerate(steps):
            for binding in (step.get('outputs') or {}).values():
                name = str(binding or '')
                if name:
                    writes.setdefault(name, []).append(step_index)
        plans: list[dict[str, Any]] = []
        for marker_name, positions in writes.items():
            if len(positions) < 2:
                continue
            iterations = []
            for iteration, start in enumerate(positions, 1):
                end = positions[iteration] if iteration < len(positions) else len(steps)
                members = steps[start:end]
                iterations.append({
                    'iteration': iteration,
                    'startStepId': steps[start]['id'],
                    'endStepId': members[-1]['id'] if members else steps[start]['id'],
                    'memberStepIds': [step['id'] for step in members],
                })
            plans.append({
                'id': f'repeated-output:{marker_name}',
                'inference': 'repeated_output_binding',
                'markerName': marker_name,
                'iterationCount': len(positions),
                'iterations': iterations,
            })
        return plans

    def __init__(self, db_path: str | Path, registry: OperationRegistry | None = None) -> None:
        self.db_path = Path(db_path)
        get_filesystem_provider().make_directory(self.db_path.parent)
        self.registry = registry or default_registry()
        self._init_db()

    def _db(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.db_path, timeout=15)
        db.row_factory = sqlite3.Row
        db.execute('PRAGMA foreign_keys=ON')
        db.execute('PRAGMA journal_mode=WAL')
        return db

    def _init_db(self) -> None:
        with self._db() as db:
            db.executescript('''
            CREATE TABLE IF NOT EXISTS wf_definitions(
              id TEXT NOT NULL, version INTEGER NOT NULL, document TEXT NOT NULL,
              created_at TEXT NOT NULL, PRIMARY KEY(id,version));
            CREATE TABLE IF NOT EXISTS wf_runs(
              id TEXT PRIMARY KEY, workflow_id TEXT NOT NULL, workflow_version INTEGER NOT NULL,
              parent_run_id TEXT, parent_step_id TEXT, status TEXT NOT NULL,
              inputs TEXT NOT NULL, outputs TEXT NOT NULL DEFAULT '{}', error TEXT,
              created_at TEXT NOT NULL, updated_at TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS wf_steps(
              run_id TEXT NOT NULL, step_id TEXT NOT NULL, status TEXT NOT NULL,
              attempt INTEGER NOT NULL DEFAULT 0, child_run_id TEXT, error TEXT,
              started_at TEXT, finished_at TEXT, PRIMARY KEY(run_id,step_id));
            CREATE TABLE IF NOT EXISTS wf_artifacts(
              id TEXT PRIMARY KEY, run_id TEXT NOT NULL, step_id TEXT,
              name TEXT NOT NULL, datatype TEXT NOT NULL, representation TEXT, payload TEXT NOT NULL,
              content_hash TEXT NOT NULL, provenance TEXT NOT NULL, created_at TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS wf_events(
              id INTEGER PRIMARY KEY AUTOINCREMENT, run_id TEXT NOT NULL,
              step_id TEXT, kind TEXT NOT NULL, payload TEXT NOT NULL, created_at TEXT NOT NULL);
            CREATE INDEX IF NOT EXISTS wf_events_run_idx ON wf_events(run_id,id);
            CREATE TABLE IF NOT EXISTS wf_logs(
              id INTEGER PRIMARY KEY AUTOINCREMENT, run_id TEXT NOT NULL,
              step_id TEXT, stream TEXT NOT NULL, message TEXT NOT NULL, created_at TEXT NOT NULL);
            CREATE INDEX IF NOT EXISTS wf_logs_run_idx ON wf_logs(run_id,id);
            CREATE TABLE IF NOT EXISTS wf_human_drafts(
              run_id TEXT NOT NULL, step_id TEXT NOT NULL, values_json TEXT NOT NULL,
              updated_at TEXT NOT NULL, PRIMARY KEY(run_id,step_id));
            CREATE TABLE IF NOT EXISTS goal_runs(
              id TEXT PRIMARY KEY, workspace_id TEXT NOT NULL,
              goal_id TEXT NOT NULL, goal_variant_id TEXT,
              plan_id TEXT NOT NULL, plan_variant_id TEXT NOT NULL,
              context_id TEXT, workflow_run_id TEXT NOT NULL,
              created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
              context_variant_id TEXT,
              FOREIGN KEY(workflow_run_id) REFERENCES wf_runs(id));
            CREATE INDEX IF NOT EXISTS goal_runs_created_idx ON goal_runs(created_at DESC);
            ''')
            columns = {row['name'] for row in db.execute('PRAGMA table_info(goal_runs)').fetchall()}
            if 'context_variant_id' not in columns:
                db.execute('ALTER TABLE goal_runs ADD COLUMN context_variant_id TEXT')
            run_columns = {row['name'] for row in db.execute('PRAGMA table_info(wf_runs)').fetchall()}
            if 'workspace_id' not in run_columns:
                db.execute('ALTER TABLE wf_runs ADD COLUMN workspace_id TEXT')
            artifact_columns = {row['name'] for row in db.execute('PRAGMA table_info(wf_artifacts)').fetchall()}
            if 'representation' not in artifact_columns:
                db.execute('ALTER TABLE wf_artifacts ADD COLUMN representation TEXT')
            db.execute('CREATE INDEX IF NOT EXISTS wf_runs_workspace_created_idx ON wf_runs(workspace_id,created_at DESC)')

    def save_workflow(self, document: dict[str, Any]) -> dict[str, Any]:
        document = self._normalize_workflow(document)
        errors = self.validate(document)
        if errors:
            raise ValueError('; '.join(errors))
        workflow_id = str(document['id'])
        with self._db() as db:
            row = db.execute('SELECT COALESCE(MAX(version),0)+1 v FROM wf_definitions WHERE id=?', (workflow_id,)).fetchone()
            version = int(row['v'])
            frozen = {
                **document,
                'version': version,
                'captureGroupPlan': self._infer_capture_group_plan(document),
            }
            db.execute('INSERT INTO wf_definitions VALUES(?,?,?,?)', (workflow_id, version, json.dumps(frozen), now()))
        return frozen

    def get_workflow(self, workflow_id: str, version: int | None = None) -> dict[str, Any]:
        with self._db() as db:
            if version is None:
                row = db.execute('SELECT document FROM wf_definitions WHERE id=? ORDER BY version DESC LIMIT 1', (workflow_id,)).fetchone()
            else:
                row = db.execute('SELECT document FROM wf_definitions WHERE id=? AND version=?', (workflow_id, version)).fetchone()
        if not row:
            raise KeyError('workflow not found')
        return json.loads(row['document'])

    def list_workflows(self) -> list[dict[str, Any]]:
        with self._db() as db:
            rows = db.execute('''SELECT d.document FROM wf_definitions d JOIN
              (SELECT id,MAX(version) version FROM wf_definitions GROUP BY id) x
              ON d.id=x.id AND d.version=x.version ORDER BY d.id''').fetchall()
        return [json.loads(r['document']) for r in rows]

    def list_runs(self, limit: int = 100, workspace_id: str | None = None) -> list[dict[str, Any]]:
        with self._db() as db:
            if workspace_id:
                rows = db.execute(
                    'SELECT id FROM wf_runs WHERE workspace_id=? ORDER BY created_at DESC LIMIT ?',
                    (workspace_id, limit),
                ).fetchall()
            else:
                rows = db.execute('SELECT id FROM wf_runs ORDER BY created_at DESC LIMIT ?', (limit,)).fetchall()
        return [self.get_run(str(row['id'])) for row in rows]

    def create_goal_run(self, workspace_id: str, goal_id: str, goal_variant_id: str | None,
                        plan_id: str, plan_variant_id: str, context_id: str | None,
                        context_variant_id: str | None, workflow_run_id: str) -> dict[str, Any]:
        self.get_run(workflow_run_id)
        goal_run_id = str(uuid.uuid4())
        stamp = now()
        with self._db() as db:
            db.execute(
                '''INSERT INTO goal_runs(
                   id,workspace_id,goal_id,goal_variant_id,plan_id,plan_variant_id,
                   context_id,workflow_run_id,created_at,updated_at,context_variant_id)
                   VALUES(?,?,?,?,?,?,?,?,?,?,?)''',
                (goal_run_id, workspace_id, goal_id, goal_variant_id, plan_id,
                 plan_variant_id, context_id, workflow_run_id, stamp, stamp, context_variant_id),
            )
        return self.get_goal_run(goal_run_id)

    def get_goal_run(self, goal_run_id: str) -> dict[str, Any]:
        with self._db() as db:
            row = db.execute('SELECT * FROM goal_runs WHERE id=?', (goal_run_id,)).fetchone()
        if not row:
            raise KeyError('goal run not found')
        workflow_run = self.get_run(str(row['workflow_run_id']))
        return {
            'id': row['id'], 'workspaceId': row['workspace_id'], 'goalId': row['goal_id'],
            'goalVariantId': row['goal_variant_id'], 'planId': row['plan_id'],
            'planVariantId': row['plan_variant_id'], 'contextId': row['context_id'],
            'contextVariantId': row['context_variant_id'],
            'workflowRunId': row['workflow_run_id'], 'status': workflow_run['status'],
            'createdAt': row['created_at'], 'updatedAt': workflow_run.get('updatedAt') or row['updated_at'],
            'workflowRun': workflow_run,
        }

    def list_goal_runs(self, workspace_id: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
        with self._db() as db:
            if workspace_id:
                rows = db.execute(
                    'SELECT id FROM goal_runs WHERE workspace_id=? ORDER BY created_at DESC LIMIT ?',
                    (workspace_id, limit),
                ).fetchall()
            else:
                rows = db.execute('SELECT id FROM goal_runs ORDER BY created_at DESC LIMIT ?', (limit,)).fetchall()
        return [self.get_goal_run(str(row['id'])) for row in rows]

    @staticmethod
    def _contract_compatible(actual: Any, expected: Any) -> bool:
        actual_type, actual_representation = WorkflowEngine._artifact_contract(actual)
        expected_type, expected_representation = WorkflowEngine._artifact_contract(expected)
        aliases = {
            'str': 'text', 'string': 'text',
            'bool': 'boolean',
            'int': 'number', 'integer': 'number', 'float': 'number', 'double': 'number',
            'list': 'array',
        }
        normalized_actual = aliases.get(actual_type.lower(), actual_type.lower())
        normalized_expected = aliases.get(expected_type.lower(), expected_type.lower())
        type_matches = normalized_actual == normalized_expected or normalized_actual in {'any', 'object'} or normalized_expected in {'any', 'object'}
        representation_matches = not expected_representation or not actual_representation or expected_representation == actual_representation
        return type_matches and representation_matches

    @staticmethod
    def _binding_name(binding: Any) -> str | None:
        if not isinstance(binding, str) or not binding.startswith('$'):
            return None
        parts = binding.lstrip('$').split('.')
        if parts[0] == 'steps' and len(parts) >= 3:
            return parts[2]
        if parts[0] in {'workflow', 'inputs', 'slots', 'artifacts', 'outputs'} and len(parts) >= 2:
            return parts[1]
        return parts[0]

    def validate(self, document: dict[str, Any]) -> list[str]:
        document = self._normalize_workflow(document)
        errors: list[str] = []
        if not document.get('id'): errors.append('workflow id is required')
        steps = document.get('steps')
        if not isinstance(steps, list): return errors + ['steps must be an array']
        ids: set[str] = set()
        produced: dict[str, Any] = dict(document.get('inputs') or {})
        for i, step in enumerate(steps):
            sid = str(step.get('id') or '')
            if not sid: errors.append(f'step {i} requires id')
            if sid in ids: errors.append(f'duplicate step id: {sid}')
            ids.add(sid)
            kind = step.get('kind', 'operation')
            if kind == 'operation':
                try: spec = self.registry.get(str(step.get('implementation') or step.get('operation') or ''))
                except KeyError as e: errors.append(str(e)); continue
                foreach = step.get('foreach') if isinstance(step.get('foreach'), dict) else None
                item_port = str(foreach.get('itemPort', 'item')) if foreach else None
                if foreach:
                    items_binding = foreach.get('items')
                    items_name = self._binding_name(items_binding)
                    if items_name and items_name not in produced:
                        errors.append(f'{sid}.foreach.items references unavailable artifact ${items_name}')
                    elif items_name and not self._contract_compatible(produced[items_name], 'Array'):
                        actual, _ = self._artifact_contract(produced[items_name])
                        errors.append(f'{sid}.foreach.items expects Array but ${items_name} is {actual}')
                for port, dtype in spec.inputs.items():
                    binding = (step.get('inputs') or {}).get(port)
                    if foreach and port == item_port:
                        continue
                    if binding is None: errors.append(f'{sid}.{port} is required ({dtype})')
                    binding_name = self._binding_name(binding)
                    if binding_name and binding_name not in produced:
                        errors.append(f'{sid}.{port} references unavailable artifact ${binding_name}')
                    elif binding_name and not self._contract_compatible(produced[binding_name], dtype):
                        actual, _ = self._artifact_contract(produced[binding_name])
                        expected, _ = self._artifact_contract(dtype)
                        errors.append(f'{sid}.{port} expects {expected} but ${binding_name} is {actual}')
                for port, name in (step.get('outputs') or {}).items():
                    produced[str(name)] = spec.outputs.get(port, 'Any')
            elif kind == 'workflow':
                if not step.get('workflowId'): errors.append(f'{sid} requires workflowId')
                for _port, name in (step.get('outputs') or {}).items(): produced[str(name)] = 'Any'
            elif kind == 'human':
                form = step.get('form') or {}
                for port, name in (step.get('outputs') or {}).items():
                    field = form.get(port) if isinstance(form, dict) else None
                    produced[str(name)] = field.get('datatype') or field.get('type') or 'Any' if isinstance(field, dict) else 'Any'
            else: errors.append(f'{sid} has unsupported kind {kind}')
        for port, binding in (document.get('outputs') or {}).items():
            binding_name = self._binding_name(binding)
            if binding_name and binding_name not in produced:
                errors.append(f'workflow output {port} references unavailable artifact ${binding_name}')
        return errors

    def start(self, workflow_id: str, inputs: dict[str, Any], version: int | None = None,
              parent_run_id: str | None = None, parent_step_id: str | None = None,
              workspace_id: str | None = None,
              state_values: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        wf = self.get_workflow(workflow_id, version)
        inputs = {**(wf.get('inputDefaults') or {}), **inputs}
        missing = [k for k in (wf.get('inputs') or {}) if k not in inputs]
        if missing: raise ValueError(f'missing workflow inputs: {missing}')
        run_id = str(uuid.uuid4())
        stamp = now()
        if not workspace_id and parent_run_id:
            workspace_id = self.get_run(parent_run_id).get('workspaceId')
        with self._db() as db:
            db.execute('''INSERT INTO wf_runs(
                       id,workflow_id,workflow_version,parent_run_id,parent_step_id,status,
                       inputs,outputs,error,created_at,updated_at,workspace_id)
                       VALUES(?,?,?,?,?,?,?,?,?,?,?,?)''',
                       (run_id, workflow_id, wf['version'], parent_run_id, parent_step_id, 'running',
                        json.dumps(inputs), '{}', None, stamp, stamp, workspace_id))
            for step in wf.get('steps', []):
                db.execute('INSERT INTO wf_steps(run_id,step_id,status) VALUES(?,?,?)', (run_id, step['id'], 'pending'))
        self._event(run_id, None, 'workflow.started', {
            'workflowId': workflow_id,
            'version': wf['version'],
            'stateValues': state_values or [],
            'captureGroupPlan': wf.get('captureGroupPlan') or self._infer_capture_group_plan(wf),
        })
        for name, value in inputs.items():
            dtype = (wf.get('inputs') or {}).get(name, 'Any')
            self._artifact(run_id, None, name, dtype, value, {'source': 'workflow.input'})
        self.advance(run_id)
        return self.get_run(run_id)

    def _event(self, run_id: str, step_id: str | None, kind: str, payload: dict[str, Any]) -> None:
        with self._db() as db:
            db.execute('INSERT INTO wf_events(run_id,step_id,kind,payload,created_at) VALUES(?,?,?,?,?)',
                       (run_id, step_id, kind, json.dumps(payload), now()))

    def _log(self, run_id: str, step_id: str | None, stream: str, message: Any) -> None:
        text = str(message or '')
        if not text:
            return
        with self._db() as db:
            db.execute('INSERT INTO wf_logs(run_id,step_id,stream,message,created_at) VALUES(?,?,?,?,?)',
                       (run_id, step_id, stream, text, now()))

    def _capture_result_logs(self, run_id: str, step_id: str, result: dict[str, Any]) -> None:
        candidates = [result, *(value for value in result.values() if isinstance(value, dict))]
        for candidate in candidates:
            for stream in ('stdout', 'stderr'):
                if candidate.get(stream):
                    self._log(run_id, step_id, stream, candidate[stream])

    @staticmethod
    def _artifact_contract(contract: Any) -> tuple[str, str | None]:
        if isinstance(contract, dict):
            datatype = str(contract.get('datatype') or contract.get('type') or 'Any')
            representation = contract.get('representation')
            return datatype, str(representation) if representation else None
        return str(contract or 'Any'), None

    def _artifact(self, run_id: str, step_id: str | None, name: str, contract: Any,
                  payload: Any, provenance: dict[str, Any]) -> str:
        artifact_id = str(uuid.uuid4())
        datatype, representation = self._artifact_contract(contract)
        with self._db() as db:
            db.execute('''INSERT INTO wf_artifacts(
                          id,run_id,step_id,name,datatype,payload,content_hash,provenance,created_at,representation)
                          VALUES(?,?,?,?,?,?,?,?,?,?)''',
                       (artifact_id, run_id, step_id, name, datatype, json.dumps(payload), digest(payload), json.dumps(provenance), now(), representation))
        event = {'artifactId': artifact_id, 'name': name, 'datatype': datatype}
        if representation:
            event['representation'] = representation
        self._event(run_id, step_id, 'artifact.created', event)
        return artifact_id

    def _resolve(self, run_id: str, binding: Any) -> Any:
        if not isinstance(binding, str) or not binding.startswith('$'):
            return binding
        parts = binding.lstrip('$').split('.')
        if parts[0] == 'steps' and len(parts) >= 3:
            parts = parts[2:]
        elif parts[0] in {'workflow', 'inputs', 'slots', 'artifacts', 'outputs'} and len(parts) >= 2:
            parts = parts[1:]
        name = parts[0]
        with self._db() as db:
            row = db.execute('SELECT payload FROM wf_artifacts WHERE run_id=? AND name=? ORDER BY created_at DESC LIMIT 1', (run_id, name)).fetchone()
            if not row and len(parts) > 1:
                # Compatibility with the original last-segment lookup used by
                # early workflow documents.
                row = db.execute('SELECT payload FROM wf_artifacts WHERE run_id=? AND name=? ORDER BY created_at DESC LIMIT 1', (run_id, parts[-1])).fetchone()
                if row:
                    parts = parts[-1:]
        if not row:
            raise ValueError(f'unresolved binding: {binding}')
        value = json.loads(row['payload'])
        for part in parts[1:]:
            if isinstance(value, dict) and part in value:
                value = value[part]
            elif isinstance(value, list) and part.isdigit() and int(part) < len(value):
                value = value[int(part)]
            else:
                raise ValueError(f'unresolved binding path: {binding}')
        return value

    def _resolve_public(self, run_id: str, binding: Any) -> Any:
        if not isinstance(binding, str) or not binding.startswith('$'):
            return binding
        parts = binding.lstrip('$').split('.')
        if parts[0] == 'steps' and len(parts) >= 3:
            parts = parts[2:]
        elif parts[0] in {'workflow', 'inputs', 'slots', 'artifacts', 'outputs'} and len(parts) >= 2:
            parts = parts[1:]
        name = parts[0]
        with self._db() as db:
            row = db.execute('SELECT payload,provenance FROM wf_artifacts WHERE run_id=? AND name=? ORDER BY created_at DESC LIMIT 1', (run_id, name)).fetchone()
            if not row and len(parts) > 1:
                row = db.execute('SELECT payload,provenance FROM wf_artifacts WHERE run_id=? AND name=? ORDER BY created_at DESC LIMIT 1', (run_id, parts[-1])).fetchone()
                if row:
                    parts = parts[-1:]
        if not row:
            raise ValueError(f'unresolved binding: {binding}')
        provenance = json.loads(row['provenance'])
        if provenance.get('sensitive'):
            return '[REDACTED]'
        value = json.loads(row['payload'])
        for part in parts[1:]:
            if isinstance(value, dict) and part in value:
                value = value[part]
            elif isinstance(value, list) and part.isdigit() and int(part) < len(value):
                value = value[int(part)]
            else:
                raise ValueError(f'unresolved binding path: {binding}')
        return value

    def advance(self, run_id: str) -> None:
        run = self.get_run(run_id)
        if run['status'] in self.TERMINAL or run['status'] in {'waiting', 'paused'}: return
        wf = self.get_workflow(run['workflowId'], run['workflowVersion'])
        for step in wf.get('steps', []):
            state = next(s for s in run['steps'] if s['stepId'] == step['id'])
            if state['status'] in {'completed', 'skipped'}: continue
            if state['status'] in {'running', 'waiting'}: return
            probe = step.get('probe') if isinstance(step.get('probe'), dict) else None
            if probe is not None:
                required = bool(probe.get('required', False))
                enabled = bool(probe.get('enabled', required))
                if not required and not enabled:
                    with self._db() as db:
                        db.execute(
                            'UPDATE wf_steps SET status=?,finished_at=? WHERE run_id=? AND step_id=?',
                            ('skipped', now(), run_id, step['id']),
                        )
                    self._event(run_id, step['id'], 'step.skipped', {
                        'reason': 'optional_probe_disabled',
                        'blocking': bool(probe.get('blocking', False)),
                    })
                    run = self.get_run(run_id)
                    continue
            self._execute_step(run_id, step)
            refreshed = self.get_run(run_id)
            current = next(s for s in refreshed['steps'] if s['stepId'] == step['id'])
            if current['status'] != 'completed': return
            run = refreshed
        outputs: dict[str, Any] = {}
        for name, binding in (wf.get('outputs') or {}).items(): outputs[name] = self._resolve_public(run_id, binding)
        with self._db() as db:
            db.execute('UPDATE wf_runs SET status=?,outputs=?,updated_at=? WHERE id=?', ('completed', json.dumps(outputs), now(), run_id))
        self._event(run_id, None, 'workflow.completed', {'outputs': list(outputs)})

    def _execute_step(self, run_id: str, step: dict[str, Any]) -> None:
        sid = step['id']; kind = step.get('kind', 'operation')
        with self._db() as db:
            db.execute('UPDATE wf_steps SET status=?,attempt=attempt+1,started_at=? WHERE run_id=? AND step_id=?', ('running', now(), run_id, sid))
        self._event(run_id, sid, 'step.started', {'kind': kind})
        try:
            if kind == 'human':
                with self._db() as db:
                    db.execute('UPDATE wf_steps SET status=? WHERE run_id=? AND step_id=?', ('waiting', run_id, sid))
                    db.execute('UPDATE wf_runs SET status=?,updated_at=? WHERE id=?', ('waiting', now(), run_id))
                self._event(run_id, sid, 'step.waiting', {'schema': step.get('form', {})})
                return
            if kind == 'workflow':
                child_inputs = {k: self._resolve(run_id, v) for k, v in (step.get('inputs') or {}).items()}
                child = self.start(step['workflowId'], child_inputs, parent_run_id=run_id, parent_step_id=sid)
                with self._db() as db:
                    db.execute('UPDATE wf_steps SET child_run_id=? WHERE run_id=? AND step_id=?', (child['id'], run_id, sid))
                if child['status'] != 'completed':
                    with self._db() as db:
                        db.execute('UPDATE wf_steps SET status=? WHERE run_id=? AND step_id=?', ('waiting', run_id, sid))
                        db.execute('UPDATE wf_runs SET status=? WHERE id=?', ('waiting', run_id))
                    return
                result = child['outputs']
            else:
                spec = self.registry.get(str(step.get('implementation') or step.get('operation')))
                values = {k: self._resolve(run_id, v) for k, v in (step.get('inputs') or {}).items()}
                result = spec.handler(values, step.get('parameters') or {})
                if not isinstance(result, dict): raise TypeError('operation handler must return an object')
                self._capture_result_logs(run_id, sid, result)
            output_bindings = step.get('outputs') or {}
            if kind == 'operation': output_types = self.registry.get(str(step.get('implementation') or step.get('operation'))).outputs
            else: output_types = {k: 'Any' for k in output_bindings}
            for port, artifact_name in output_bindings.items():
                if port not in result: raise ValueError(f'missing operation output: {port}')
                provenance: dict[str, Any] = {'stepId': sid}
                operation_id = step.get('operation') or step.get('implementation')
                implementation_id = step.get('implementation')
                if operation_id:
                    provenance['operationId'] = str(operation_id)
                if implementation_id and implementation_id != operation_id:
                    provenance['implementationId'] = str(implementation_id)
                model_id = (step.get('parameters') or {}).get('modelId')
                if model_id:
                    provenance['modelId'] = str(model_id)
                self._artifact(run_id, sid, artifact_name, output_types.get(port, 'Any'), result[port], provenance)
            with self._db() as db:
                db.execute('UPDATE wf_steps SET status=?,finished_at=? WHERE run_id=? AND step_id=?', ('completed', now(), run_id, sid))
            self._event(run_id, sid, 'step.completed', {'outputs': list(output_bindings.values())})
        except Exception as exc:
            self._log(run_id, sid, 'stderr', exc)
            retries = int((step.get('retry') or {}).get('maxAttempts', 1))
            retry_attempt: int | None = None
            with self._db() as db:
                row = db.execute('SELECT attempt FROM wf_steps WHERE run_id=? AND step_id=?', (run_id, sid)).fetchone()
                if int(row['attempt']) < retries:
                    db.execute('UPDATE wf_steps SET status=?,error=? WHERE run_id=? AND step_id=?', ('pending', str(exc), run_id, sid))
                    retry_attempt = int(row['attempt'])
                else:
                    db.execute('UPDATE wf_steps SET status=?,error=?,finished_at=? WHERE run_id=? AND step_id=?', ('failed', str(exc), now(), run_id, sid))
                    db.execute('UPDATE wf_runs SET status=?,error=?,updated_at=? WHERE id=?', ('failed', str(exc), now(), run_id))
            if retry_attempt is not None:
                self._event(run_id, sid, 'step.retrying', {'error': str(exc), 'attempt': retry_attempt})
                return self.advance(run_id)
            self._event(run_id, sid, 'step.failed', {'error': str(exc)})

    def submit_human_input(self, run_id: str, step_id: str, values: dict[str, Any]) -> dict[str, Any]:
        run = self.get_run(run_id)
        wf = self.get_workflow(run['workflowId'], run['workflowVersion'])
        step = next((s for s in wf['steps'] if s['id'] == step_id), None)
        if not step or step.get('kind') != 'human': raise ValueError('not a human step')
        state = next(s for s in run['steps'] if s['stepId'] == step_id)
        if state['status'] != 'waiting': raise ValueError('step is not waiting')
        form = step.get('form') or {}
        artifact_ids: list[str] = []
        artifact_names: list[str] = []
        redacted_fields: list[str] = []
        for port, artifact_name in (step.get('outputs') or {}).items():
            if port not in values: raise ValueError(f'missing human value: {port}')
            field = form.get(port, {})
            contract = field if isinstance(field, dict) else {'type': field}
            artifact_ids.append(self._artifact(
                run_id, step_id, artifact_name, contract, values[port],
                {'source': 'human', 'field': port, 'sensitive': bool(contract.get('secret') or contract.get('sensitive'))},
            ))
            artifact_names.append(str(artifact_name))
            if contract.get('secret') or contract.get('sensitive'):
                redacted_fields.append(port)
        with self._db() as db:
            db.execute('UPDATE wf_steps SET status=?,finished_at=? WHERE run_id=? AND step_id=?', ('completed', now(), run_id, step_id))
            db.execute('UPDATE wf_runs SET status=?,updated_at=? WHERE id=?', ('running', now(), run_id))
            db.execute('DELETE FROM wf_human_drafts WHERE run_id=? AND step_id=?', (run_id, step_id))
        self._event(run_id, step_id, 'human_input.received', {
            'artifactIds': artifact_ids,
            'artifacts': artifact_names,
            'fields': [port for port in (step.get('outputs') or {}) if port not in redacted_fields],
            'redactedFields': redacted_fields,
        })
        self._event(run_id, step_id, 'step.completed', {'source': 'human'})
        self.advance(run_id)
        return self.get_run(run_id)

    def save_human_input_draft(self, run_id: str, step_id: str, values: dict[str, Any]) -> dict[str, Any]:
        run = self.get_run(run_id)
        state = next((item for item in run['steps'] if item['stepId'] == step_id), None)
        if not state or state['status'] != 'waiting':
            raise ValueError('human-input drafts require a waiting step')
        workflow = self.get_workflow(run['workflowId'], run['workflowVersion'])
        step = next((item for item in workflow.get('steps', []) if item.get('id') == step_id), None)
        if not step or step.get('kind') != 'human':
            raise ValueError('not a human step')
        form = step.get('form') or {}
        safe_values = {name: values[name] for name, spec in form.items()
                       if name in values and not (spec or {}).get('secret') and not (spec or {}).get('sensitive')}
        omitted = [name for name in values if name not in safe_values]
        updated_at = now()
        with self._db() as db:
            db.execute('''INSERT INTO wf_human_drafts(run_id,step_id,values_json,updated_at) VALUES(?,?,?,?)
                          ON CONFLICT(run_id,step_id) DO UPDATE SET values_json=excluded.values_json,updated_at=excluded.updated_at''',
                       (run_id, step_id, json.dumps(safe_values), updated_at))
        return {'values': safe_values, 'omittedFields': omitted, 'updatedAt': updated_at}

    def get_human_input_draft(self, run_id: str, step_id: str) -> dict[str, Any]:
        self.get_run(run_id)
        with self._db() as db:
            row = db.execute('SELECT values_json,updated_at FROM wf_human_drafts WHERE run_id=? AND step_id=?', (run_id, step_id)).fetchone()
        if not row:
            return {'values': {}, 'omittedFields': [], 'updatedAt': None}
        return {'values': json.loads(row['values_json']), 'omittedFields': [], 'updatedAt': row['updated_at']}

    def command(self, run_id: str, command: str) -> dict[str, Any]:
        if command not in {'pause','resume','cancel'}: raise ValueError('invalid command')
        run = self.get_run(run_id)
        if command == 'pause' and run['status'] == 'running': status = 'paused'
        elif command == 'resume' and run['status'] == 'paused': status = 'running'
        elif command == 'cancel' and run['status'] not in self.TERMINAL: status = 'cancelled'
        else: return run
        with self._db() as db: db.execute('UPDATE wf_runs SET status=?,updated_at=? WHERE id=?', (status, now(), run_id))
        self._event(run_id, None, f'workflow.{status}', {})
        if status == 'running': self.advance(run_id)
        return self.get_run(run_id)

    @staticmethod
    def _artifact_view(row: sqlite3.Row) -> dict[str, Any]:
        provenance = json.loads(row['provenance'])
        sensitive = bool(provenance.get('sensitive'))
        return {
            'id': row['id'], 'stepId': row['step_id'], 'name': row['name'],
            'datatype': row['datatype'], 'representation': row['representation'],
            'payload': '[REDACTED]' if sensitive else json.loads(row['payload']),
            'contentHash': row['content_hash'], 'provenance': provenance,
            'createdAt': row['created_at'], 'redacted': sensitive,
        }

    @staticmethod
    def _infer_capture_groups(artifacts: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Infer loop iterations from repeated writes to the same output binding.

        A marker write begins an iteration. Every artifact from that write up to,
        but not including, the next write to the marker belongs to that group.
        Multiple repeated bindings are retained because inferred loops may overlap.
        """
        marker_positions: dict[str, list[int]] = {}
        for index, artifact in enumerate(artifacts):
            provenance = artifact.get('provenance') or {}
            if provenance.get('source') == 'workflow.input':
                continue
            marker_positions.setdefault(str(artifact.get('name') or ''), []).append(index)
        groups: list[dict[str, Any]] = []
        for marker_name, positions in marker_positions.items():
            if not marker_name or len(positions) < 2:
                continue
            for iteration, start in enumerate(positions, 1):
                end = positions[iteration] if iteration < len(positions) else len(artifacts)
                members = artifacts[start:end]
                groups.append({
                    'id': f'{marker_name}:{iteration}',
                    'markerName': marker_name,
                    'iteration': iteration,
                    'iterationCount': len(positions),
                    'startArtifactId': artifacts[start]['id'],
                    'endArtifactId': members[-1]['id'] if members else artifacts[start]['id'],
                    'memberArtifactIds': [artifact['id'] for artifact in members],
                    'memberNames': [artifact['name'] for artifact in members],
                    'startedAt': artifacts[start].get('createdAt'),
                    'endedAt': members[-1].get('createdAt') if members else artifacts[start].get('createdAt'),
                })
        return groups

    def get_run(self, run_id: str) -> dict[str, Any]:
        with self._db() as db:
            run = db.execute('SELECT * FROM wf_runs WHERE id=?', (run_id,)).fetchone()
            if not run: raise KeyError('run not found')
            steps = db.execute('SELECT * FROM wf_steps WHERE run_id=? ORDER BY rowid', (run_id,)).fetchall()
            artifacts = db.execute('SELECT * FROM wf_artifacts WHERE run_id=? ORDER BY created_at', (run_id,)).fetchall()
            events = db.execute('SELECT * FROM wf_events WHERE run_id=? ORDER BY id', (run_id,)).fetchall()
            logs = db.execute('SELECT * FROM wf_logs WHERE run_id=? ORDER BY id', (run_id,)).fetchall()
        artifact_views = [self._artifact_view(a) for a in artifacts]
        return {'id': run['id'], 'workspaceId': run['workspace_id'],
                'workflowId': run['workflow_id'], 'workflowVersion': run['workflow_version'],
                'parentRunId': run['parent_run_id'], 'parentStepId': run['parent_step_id'], 'status': run['status'],
                'inputs': json.loads(run['inputs']), 'outputs': json.loads(run['outputs']), 'error': run['error'],
                'createdAt': run['created_at'], 'updatedAt': run['updated_at'],
                'steps': [{'stepId': s['step_id'], 'status': s['status'], 'attempt': s['attempt'], 'childRunId': s['child_run_id'], 'error': s['error']} for s in steps],
                'artifacts': artifact_views,
                'captureGroups': self._infer_capture_groups(artifact_views),
                'events': [{'id': e['id'], 'stepId': e['step_id'], 'kind': e['kind'], 'payload': json.loads(e['payload']), 'createdAt': e['created_at']} for e in events],
                'logs': [{'id': entry['id'], 'stepId': entry['step_id'], 'stream': entry['stream'], 'message': entry['message'], 'createdAt': entry['created_at']} for entry in logs]}

    def get_state(self, state_id: str) -> dict[str, Any]:
        """Resolve a durable state artifact and the run that owns it."""
        with self._db() as db:
            artifact = db.execute(
                'SELECT * FROM wf_artifacts WHERE id=?',
                (state_id,),
            ).fetchone()
        if not artifact:
            raise KeyError('state not found')
        return {
            'state': self._artifact_view(artifact),
            'run': self.get_run(str(artifact['run_id'])),
        }


def default_registry() -> OperationRegistry:
    registry = OperationRegistry()
    registry.register(OperationSpec('core.echo', {'value': 'Any'}, {'value': 'Any'}, lambda i, p: {'value': i['value']}))
    registry.register(OperationSpec('echo.value', {'played_games': 'Array'}, {'played_games': 'Array'}, lambda i, p: {'played_games': i['played_games']}))
    registry.register(OperationSpec('core.merge', {'left': 'Object', 'right': 'Object'}, {'value': 'Object'}, lambda i, p: {'value': {**i['left'], **i['right']}}))
    registry.register(OperationSpec('core.select', {'value': 'Object'}, {'value': 'Any'}, lambda i, p: {'value': i['value'][p['key']]}))
    registry.register(OperationSpec('core.constant', {}, {'value': 'Any'}, lambda i, p: {'value': p.get('value')}))
    return registry
