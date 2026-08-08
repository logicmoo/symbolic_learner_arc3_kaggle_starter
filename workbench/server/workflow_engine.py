from __future__ import annotations

import hashlib
import json
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable


def now() -> str:
    return datetime.now(UTC).isoformat().replace('+00:00', 'Z')


def digest(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(',', ':'), default=str).encode()
    return hashlib.sha256(raw).hexdigest()


@dataclass(frozen=True)
class OperationSpec:
    name: str
    inputs: dict[str, str]
    outputs: dict[str, str]
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

    def __init__(self, db_path: str | Path, registry: OperationRegistry | None = None) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
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
              name TEXT NOT NULL, datatype TEXT NOT NULL, payload TEXT NOT NULL,
              content_hash TEXT NOT NULL, provenance TEXT NOT NULL, created_at TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS wf_events(
              id INTEGER PRIMARY KEY AUTOINCREMENT, run_id TEXT NOT NULL,
              step_id TEXT, kind TEXT NOT NULL, payload TEXT NOT NULL, created_at TEXT NOT NULL);
            CREATE INDEX IF NOT EXISTS wf_events_run_idx ON wf_events(run_id,id);
            CREATE TABLE IF NOT EXISTS goal_runs(
              id TEXT PRIMARY KEY, workspace_id TEXT NOT NULL,
              goal_id TEXT NOT NULL, goal_variant_id TEXT,
              plan_id TEXT NOT NULL, plan_variant_id TEXT NOT NULL,
              context_id TEXT, workflow_run_id TEXT NOT NULL,
              created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
              FOREIGN KEY(workflow_run_id) REFERENCES wf_runs(id));
            CREATE INDEX IF NOT EXISTS goal_runs_created_idx ON goal_runs(created_at DESC);
            ''')

    def save_workflow(self, document: dict[str, Any]) -> dict[str, Any]:
        errors = self.validate(document)
        if errors:
            raise ValueError('; '.join(errors))
        workflow_id = str(document['id'])
        with self._db() as db:
            row = db.execute('SELECT COALESCE(MAX(version),0)+1 v FROM wf_definitions WHERE id=?', (workflow_id,)).fetchone()
            version = int(row['v'])
            frozen = {**document, 'version': version}
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

    def list_runs(self, limit: int = 100) -> list[dict[str, Any]]:
        with self._db() as db:
            rows = db.execute('SELECT id FROM wf_runs ORDER BY created_at DESC LIMIT ?', (limit,)).fetchall()
        return [self.get_run(str(row['id'])) for row in rows]

    def create_goal_run(self, workspace_id: str, goal_id: str, goal_variant_id: str | None,
                        plan_id: str, plan_variant_id: str, context_id: str | None,
                        workflow_run_id: str) -> dict[str, Any]:
        self.get_run(workflow_run_id)
        goal_run_id = str(uuid.uuid4())
        stamp = now()
        with self._db() as db:
            db.execute(
                'INSERT INTO goal_runs VALUES(?,?,?,?,?,?,?,?,?,?)',
                (goal_run_id, workspace_id, goal_id, goal_variant_id, plan_id,
                 plan_variant_id, context_id, workflow_run_id, stamp, stamp),
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

    def validate(self, document: dict[str, Any]) -> list[str]:
        errors: list[str] = []
        if not document.get('id'): errors.append('workflow id is required')
        steps = document.get('steps')
        if not isinstance(steps, list): return errors + ['steps must be an array']
        ids: set[str] = set()
        produced = set((document.get('inputs') or {}).keys())
        for i, step in enumerate(steps):
            sid = str(step.get('id') or '')
            if not sid: errors.append(f'step {i} requires id')
            if sid in ids: errors.append(f'duplicate step id: {sid}')
            ids.add(sid)
            kind = step.get('kind', 'operation')
            if kind == 'operation':
                try: spec = self.registry.get(str(step.get('implementation') or step.get('operation') or ''))
                except KeyError as e: errors.append(str(e)); continue
                for port, dtype in spec.inputs.items():
                    binding = (step.get('inputs') or {}).get(port)
                    if binding is None: errors.append(f'{sid}.{port} is required ({dtype})')
                for name in (step.get('outputs') or {}): produced.add(name)
            elif kind == 'workflow':
                if not step.get('workflowId'): errors.append(f'{sid} requires workflowId')
            elif kind == 'human':
                pass
            else: errors.append(f'{sid} has unsupported kind {kind}')
        return errors

    def start(self, workflow_id: str, inputs: dict[str, Any], version: int | None = None,
              parent_run_id: str | None = None, parent_step_id: str | None = None) -> dict[str, Any]:
        wf = self.get_workflow(workflow_id, version)
        missing = [k for k in (wf.get('inputs') or {}) if k not in inputs]
        if missing: raise ValueError(f'missing workflow inputs: {missing}')
        run_id = str(uuid.uuid4())
        stamp = now()
        with self._db() as db:
            db.execute('INSERT INTO wf_runs VALUES(?,?,?,?,?,?,?,?,?,?,?)',
                       (run_id, workflow_id, wf['version'], parent_run_id, parent_step_id, 'running', json.dumps(inputs), '{}', None, stamp, stamp))
            for step in wf.get('steps', []):
                db.execute('INSERT INTO wf_steps(run_id,step_id,status) VALUES(?,?,?)', (run_id, step['id'], 'pending'))
        self._event(run_id, None, 'workflow.started', {'workflowId': workflow_id, 'version': wf['version']})
        for name, value in inputs.items():
            dtype = (wf.get('inputs') or {}).get(name, 'Any')
            self._artifact(run_id, None, name, dtype, value, {'source': 'workflow.input'})
        self.advance(run_id)
        return self.get_run(run_id)

    def _event(self, run_id: str, step_id: str | None, kind: str, payload: dict[str, Any]) -> None:
        with self._db() as db:
            db.execute('INSERT INTO wf_events(run_id,step_id,kind,payload,created_at) VALUES(?,?,?,?,?)',
                       (run_id, step_id, kind, json.dumps(payload), now()))

    def _artifact(self, run_id: str, step_id: str | None, name: str, datatype: str,
                  payload: Any, provenance: dict[str, Any]) -> str:
        artifact_id = str(uuid.uuid4())
        with self._db() as db:
            db.execute('INSERT INTO wf_artifacts VALUES(?,?,?,?,?,?,?,?,?)',
                       (artifact_id, run_id, step_id, name, datatype, json.dumps(payload), digest(payload), json.dumps(provenance), now()))
        self._event(run_id, step_id, 'artifact.created', {'artifactId': artifact_id, 'name': name, 'datatype': datatype})
        return artifact_id

    def _resolve(self, run_id: str, binding: Any) -> Any:
        if not isinstance(binding, str) or not binding.startswith('$'):
            return binding
        name = binding.lstrip('$').split('.')[-1]
        with self._db() as db:
            row = db.execute('SELECT payload FROM wf_artifacts WHERE run_id=? AND name=? ORDER BY created_at DESC LIMIT 1', (run_id, name)).fetchone()
        if not row: raise ValueError(f'unresolved binding: {binding}')
        return json.loads(row['payload'])

    def advance(self, run_id: str) -> None:
        run = self.get_run(run_id)
        if run['status'] in self.TERMINAL or run['status'] in {'waiting', 'paused'}: return
        wf = self.get_workflow(run['workflowId'], run['workflowVersion'])
        for step in wf.get('steps', []):
            state = next(s for s in run['steps'] if s['stepId'] == step['id'])
            if state['status'] == 'completed': continue
            if state['status'] in {'running', 'waiting'}: return
            self._execute_step(run_id, step)
            refreshed = self.get_run(run_id)
            current = next(s for s in refreshed['steps'] if s['stepId'] == step['id'])
            if current['status'] != 'completed': return
            run = refreshed
        outputs: dict[str, Any] = {}
        for name, binding in (wf.get('outputs') or {}).items(): outputs[name] = self._resolve(run_id, binding)
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
            output_bindings = step.get('outputs') or {}
            if kind == 'operation': output_types = self.registry.get(str(step.get('implementation') or step.get('operation'))).outputs
            else: output_types = {k: 'Any' for k in output_bindings}
            for port, artifact_name in output_bindings.items():
                if port not in result: raise ValueError(f'missing operation output: {port}')
                self._artifact(run_id, sid, artifact_name, output_types.get(port, 'Any'), result[port], {'stepId': sid})
            with self._db() as db:
                db.execute('UPDATE wf_steps SET status=?,finished_at=? WHERE run_id=? AND step_id=?', ('completed', now(), run_id, sid))
            self._event(run_id, sid, 'step.completed', {'outputs': list(output_bindings.values())})
        except Exception as exc:
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
        for port, artifact_name in (step.get('outputs') or {}).items():
            if port not in values: raise ValueError(f'missing human value: {port}')
            self._artifact(run_id, step_id, artifact_name, (step.get('form') or {}).get(port, {}).get('type', 'Any'), values[port], {'source': 'human'})
        with self._db() as db:
            db.execute('UPDATE wf_steps SET status=?,finished_at=? WHERE run_id=? AND step_id=?', ('completed', now(), run_id, step_id))
            db.execute('UPDATE wf_runs SET status=?,updated_at=? WHERE id=?', ('running', now(), run_id))
        self._event(run_id, step_id, 'step.completed', {'source': 'human'})
        self.advance(run_id)
        return self.get_run(run_id)

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

    def get_run(self, run_id: str) -> dict[str, Any]:
        with self._db() as db:
            run = db.execute('SELECT * FROM wf_runs WHERE id=?', (run_id,)).fetchone()
            if not run: raise KeyError('run not found')
            steps = db.execute('SELECT * FROM wf_steps WHERE run_id=? ORDER BY rowid', (run_id,)).fetchall()
            artifacts = db.execute('SELECT * FROM wf_artifacts WHERE run_id=? ORDER BY created_at', (run_id,)).fetchall()
            events = db.execute('SELECT * FROM wf_events WHERE run_id=? ORDER BY id', (run_id,)).fetchall()
        return {'id': run['id'], 'workflowId': run['workflow_id'], 'workflowVersion': run['workflow_version'],
                'parentRunId': run['parent_run_id'], 'parentStepId': run['parent_step_id'], 'status': run['status'],
                'inputs': json.loads(run['inputs']), 'outputs': json.loads(run['outputs']), 'error': run['error'],
                'createdAt': run['created_at'], 'updatedAt': run['updated_at'],
                'steps': [{'stepId': s['step_id'], 'status': s['status'], 'attempt': s['attempt'], 'childRunId': s['child_run_id'], 'error': s['error']} for s in steps],
                'artifacts': [{'id': a['id'], 'stepId': a['step_id'], 'name': a['name'], 'datatype': a['datatype'], 'payload': json.loads(a['payload']), 'contentHash': a['content_hash'], 'provenance': json.loads(a['provenance'])} for a in artifacts],
                'events': [{'id': e['id'], 'stepId': e['step_id'], 'kind': e['kind'], 'payload': json.loads(e['payload']), 'createdAt': e['created_at']} for e in events]}


def default_registry() -> OperationRegistry:
    registry = OperationRegistry()
    registry.register(OperationSpec('core.echo', {'value': 'Any'}, {'value': 'Any'}, lambda i, p: {'value': i['value']}))
    registry.register(OperationSpec('core.merge', {'left': 'Object', 'right': 'Object'}, {'value': 'Object'}, lambda i, p: {'value': {**i['left'], **i['right']}}))
    registry.register(OperationSpec('core.select', {'value': 'Object'}, {'value': 'Any'}, lambda i, p: {'value': i['value'][p['key']]}))
    registry.register(OperationSpec('core.constant', {}, {'value': 'Any'}, lambda i, p: {'value': p.get('value')}))
    return registry
