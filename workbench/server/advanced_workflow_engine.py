from __future__ import annotations

import json
import subprocess
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout
from pathlib import Path
from typing import Any

from workflow_engine import TaskRegistry, TaskSpec, WorkflowEngine, now


class AdvancedWorkflowEngine(WorkflowEngine):
    """Feature-complete local workflow engine layered on the durable core.

    Adds dependency-graph scheduling, conditions, bounded foreach loops,
    timeouts, delayed retries, compensation, task logs, child-run propagation,
    recovery, replay, subprocess and HTTP task implementations.
    """

    def __init__(self, db_path: str | Path, registry: TaskRegistry | None = None) -> None:
        super().__init__(db_path, registry)
        self._init_advanced_db()
        self._register_runtime_tasks()
        self.recover_interrupted_runs()

    def _init_advanced_db(self) -> None:
        with self._db() as db:
            db.executescript('''
            CREATE TABLE IF NOT EXISTS wf_step_logs(
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              run_id TEXT NOT NULL,
              step_id TEXT NOT NULL,
              stream TEXT NOT NULL,
              message TEXT NOT NULL,
              created_at TEXT NOT NULL);
            CREATE INDEX IF NOT EXISTS wf_step_logs_idx ON wf_step_logs(run_id,step_id,id);
            CREATE TABLE IF NOT EXISTS wf_run_relations(
              parent_run_id TEXT NOT NULL,
              parent_step_id TEXT NOT NULL,
              child_run_id TEXT NOT NULL,
              created_at TEXT NOT NULL,
              PRIMARY KEY(parent_run_id,parent_step_id,child_run_id));
            ''')

    def _register_runtime_tasks(self) -> None:
        existing = {item['name'] for item in self.registry.describe()}

        def register(spec: TaskSpec) -> None:
            if spec.name not in existing:
                self.registry.register(spec)
                existing.add(spec.name)

        register(TaskSpec('process.run', {}, {'result': 'ProcessResult'}, self._task_process))
        register(TaskSpec('http.request', {}, {'result': 'HttpResult'}, self._task_http))
        register(TaskSpec('python.expression', {'context': 'Object'}, {'value': 'Any'}, self._task_expression))
        register(TaskSpec('core.collect', {'items': 'Array'}, {'value': 'Array'}, lambda i, p: {'value': i['items']}))
        register(TaskSpec('core.fail', {}, {}, lambda i, p: (_ for _ in ()).throw(RuntimeError(str(p.get('message', 'forced failure'))))))

    @staticmethod
    def _task_process(_inputs: dict[str, Any], parameters: dict[str, Any]) -> dict[str, Any]:
        command = parameters.get('command')
        if not command:
            raise ValueError('process.run requires parameters.command')
        shell = bool(parameters.get('shell', isinstance(command, str)))
        completed = subprocess.run(
            command,
            shell=shell,
            cwd=parameters.get('cwd'),
            env=parameters.get('env'),
            text=True,
            capture_output=True,
            check=False,
        )
        result = {'returnCode': completed.returncode, 'stdout': completed.stdout, 'stderr': completed.stderr}
        if completed.returncode and not parameters.get('allowFailure', False):
            raise RuntimeError(f"process exited {completed.returncode}: {completed.stderr.strip()}")
        return {'result': result}

    @staticmethod
    def _task_http(inputs: dict[str, Any], parameters: dict[str, Any]) -> dict[str, Any]:
        url = str(parameters.get('url') or inputs.get('url') or '')
        if not url:
            raise ValueError('http.request requires url')
        method = str(parameters.get('method', 'GET')).upper()
        body = parameters.get('body')
        data = None if body is None else json.dumps(body).encode('utf-8')
        headers = {'Accept': 'application/json', **(parameters.get('headers') or {})}
        if data is not None:
            headers.setdefault('Content-Type', 'application/json')
        request = urllib.request.Request(url, data=data, method=method, headers=headers)
        with urllib.request.urlopen(request, timeout=float(parameters.get('timeoutSeconds', 30))) as response:
            raw = response.read().decode('utf-8')
            try:
                parsed: Any = json.loads(raw)
            except json.JSONDecodeError:
                parsed = raw
            return {'result': {'status': response.status, 'headers': dict(response.headers), 'body': parsed}}

    @staticmethod
    def _task_expression(inputs: dict[str, Any], parameters: dict[str, Any]) -> dict[str, Any]:
        expression = str(parameters.get('expression') or '')
        if not expression:
            raise ValueError('python.expression requires parameters.expression')
        safe_globals = {'__builtins__': {'len': len, 'min': min, 'max': max, 'sum': sum, 'sorted': sorted, 'str': str, 'int': int, 'float': float, 'bool': bool}}
        return {'value': eval(expression, safe_globals, {'context': inputs.get('context', {})})}

    def _log(self, run_id: str, step_id: str, stream: str, message: str) -> None:
        with self._db() as db:
            db.execute('INSERT INTO wf_step_logs(run_id,step_id,stream,message,created_at) VALUES(?,?,?,?,?)',
                       (run_id, step_id, stream, message, now()))
        self._event(run_id, step_id, 'step.log', {'stream': stream, 'message': message})

    def validate(self, document: dict[str, Any]) -> list[str]:
        errors = super().validate(document)
        steps = document.get('steps') or []
        ids = {str(step.get('id')) for step in steps if step.get('id')}
        graph: dict[str, set[str]] = {}
        for step in steps:
            sid = str(step.get('id') or '')
            deps = set(map(str, step.get('dependsOn') or []))
            missing = sorted(dep for dep in deps if dep not in ids)
            if missing:
                errors.append(f'{sid} depends on unknown steps: {missing}')
            graph[sid] = deps
            loop = step.get('foreach')
            if loop and int(loop.get('maxItems', 1000)) <= 0:
                errors.append(f'{sid}.foreach.maxItems must be positive')
            if step.get('timeoutSeconds') is not None and float(step['timeoutSeconds']) <= 0:
                errors.append(f'{sid}.timeoutSeconds must be positive')
        visiting: set[str] = set(); visited: set[str] = set()
        def visit(node: str) -> None:
            if node in visiting:
                errors.append(f'dependency cycle detected at {node}')
                return
            if node in visited:
                return
            visiting.add(node)
            for dep in graph.get(node, set()):
                visit(dep)
            visiting.remove(node); visited.add(node)
        for node in graph:
            visit(node)
        return list(dict.fromkeys(errors))

    def _condition_true(self, run_id: str, condition: Any) -> bool:
        if condition is None:
            return True
        if isinstance(condition, bool):
            return condition
        if isinstance(condition, str):
            value = self._resolve(run_id, condition) if condition.startswith('$') else condition
            return bool(value)
        if isinstance(condition, dict):
            left = self._resolve(run_id, condition.get('left'))
            right = self._resolve(run_id, condition.get('right'))
            op = condition.get('op', 'eq')
            return {'eq': left == right, 'ne': left != right, 'gt': left > right, 'gte': left >= right,
                    'lt': left < right, 'lte': left <= right, 'in': left in right, 'contains': right in left}.get(op, False)
        return bool(condition)

    def _dependencies(self, workflow: dict[str, Any], step: dict[str, Any]) -> set[str]:
        explicit = set(map(str, step.get('dependsOn') or []))
        inferred: set[str] = set()
        for binding in (step.get('inputs') or {}).values():
            if isinstance(binding, str) and binding.startswith('$steps.'):
                parts = binding.split('.')
                if len(parts) > 1:
                    inferred.add(parts[1])
        return explicit | inferred

    def _ready_steps(self, run: dict[str, Any], workflow: dict[str, Any]) -> list[dict[str, Any]]:
        states = {item['stepId']: item['status'] for item in run['steps']}
        ready: list[dict[str, Any]] = []
        for step in workflow.get('steps', []):
            if states.get(step['id']) != 'pending':
                continue
            dependencies = self._dependencies(workflow, step)
            if all(states.get(dep) in {'completed', 'skipped', 'compensated'} for dep in dependencies):
                ready.append(step)
        return ready

    def advance(self, run_id: str) -> None:
        self.refresh_children(run_id)
        while True:
            run = self.get_run(run_id)
            if run['status'] in self.TERMINAL or run['status'] in {'waiting', 'paused', 'compensating'}:
                return
            workflow = self.get_workflow(run['workflowId'], run['workflowVersion'])
            ready = self._ready_steps(run, workflow)
            if not ready:
                states = {s['status'] for s in run['steps']}
                if states <= {'completed', 'skipped', 'compensated'}:
                    outputs = {name: self._resolve(run_id, binding) for name, binding in (workflow.get('outputs') or {}).items()}
                    with self._db() as db:
                        db.execute('UPDATE wf_runs SET status=?,outputs=?,updated_at=? WHERE id=?', ('completed', json.dumps(outputs), now(), run_id))
                    self._event(run_id, None, 'workflow.completed', {'outputs': list(outputs)})
                    self._resume_parent(run_id)
                elif 'failed' in states:
                    self._compensate(run_id, workflow)
                return
            for step in ready:
                if not self._condition_true(run_id, step.get('when')):
                    with self._db() as db:
                        db.execute('UPDATE wf_steps SET status=?,finished_at=? WHERE run_id=? AND step_id=?', ('skipped', now(), run_id, step['id']))
                    self._event(run_id, step['id'], 'step.skipped', {'reason': 'condition_false'})
                    continue
                self._execute_advanced_step(run_id, step)
                current = self.get_run(run_id)
                if current['status'] in {'waiting', 'paused', 'failed', 'cancelled', 'compensating'}:
                    return

    def _execute_advanced_step(self, run_id: str, step: dict[str, Any]) -> None:
        sid = step['id']
        kind = step.get('kind', 'task')
        with self._db() as db:
            db.execute('UPDATE wf_steps SET status=?,attempt=attempt+1,started_at=?,error=NULL WHERE run_id=? AND step_id=?', ('running', now(), run_id, sid))
        self._event(run_id, sid, 'step.started', {'kind': kind})
        self._log(run_id, sid, 'system', 'step execution started')
        try:
            if kind in {'human', 'workflow'}:
                super()._execute_step(run_id, step)
                state = next(s for s in self.get_run(run_id)['steps'] if s['stepId'] == sid)
                if state.get('childRunId'):
                    with self._db() as db:
                        db.execute('INSERT OR IGNORE INTO wf_run_relations VALUES(?,?,?,?)', (run_id, sid, state['childRunId'], now()))
                return
            spec = self.registry.get(str(step.get('implementation') or step.get('operation')))
            values = {k: self._resolve(run_id, v) for k, v in (step.get('inputs') or {}).items()}
            foreach = step.get('foreach')
            timeout = float(step.get('timeoutSeconds', 0) or 0)
            def invoke() -> dict[str, Any]:
                if foreach:
                    items = self._resolve(run_id, foreach.get('items'))
                    if not isinstance(items, list):
                        raise ValueError('foreach.items must resolve to an array')
                    max_items = int(foreach.get('maxItems', 1000))
                    if len(items) > max_items:
                        raise ValueError(f'foreach exceeds maxItems={max_items}')
                    item_port = str(foreach.get('itemPort', 'item'))
                    results = []
                    for index, item in enumerate(items):
                        self._log(run_id, sid, 'system', f'foreach item {index + 1}/{len(items)}')
                        results.append(spec.handler({**values, item_port: item}, step.get('parameters') or {}))
                    aggregate: dict[str, Any] = {}
                    for port in spec.outputs:
                        aggregate[port] = [result.get(port) for result in results]
                    return aggregate
                return spec.handler(values, step.get('parameters') or {})
            if timeout:
                with ThreadPoolExecutor(max_workers=1) as pool:
                    future = pool.submit(invoke)
                    try:
                        result = future.result(timeout=timeout)
                    except FutureTimeout as exc:
                        future.cancel()
                        raise TimeoutError(f'step exceeded timeoutSeconds={timeout}') from exc
            else:
                result = invoke()
            if not isinstance(result, dict):
                raise TypeError('task handler must return an object')
            if 'result' in result and isinstance(result['result'], dict):
                proc = result['result']
                if proc.get('stdout'):
                    self._log(run_id, sid, 'stdout', str(proc['stdout']))
                if proc.get('stderr'):
                    self._log(run_id, sid, 'stderr', str(proc['stderr']))
            for port, artifact_name in (step.get('outputs') or {}).items():
                if port not in result:
                    raise ValueError(f'missing task output: {port}')
                self._artifact(run_id, sid, artifact_name, spec.outputs.get(port, 'Any'), result[port], {'stepId': sid, 'attempt': self._attempt(run_id, sid)})
            with self._db() as db:
                db.execute('UPDATE wf_steps SET status=?,finished_at=? WHERE run_id=? AND step_id=?', ('completed', now(), run_id, sid))
            self._event(run_id, sid, 'step.completed', {'outputs': list((step.get('outputs') or {}).values())})
            self._log(run_id, sid, 'system', 'step execution completed')
        except Exception as exc:
            self._handle_failure(run_id, step, exc)

    def _attempt(self, run_id: str, step_id: str) -> int:
        with self._db() as db:
            row = db.execute('SELECT attempt FROM wf_steps WHERE run_id=? AND step_id=?', (run_id, step_id)).fetchone()
        return int(row['attempt'])

    def _handle_failure(self, run_id: str, step: dict[str, Any], exc: Exception) -> None:
        sid = step['id']; attempt = self._attempt(run_id, sid)
        retry = step.get('retry') or {}
        max_attempts = int(retry.get('maxAttempts', 1))
        if attempt < max_attempts:
            delay = float(retry.get('delaySeconds', 0) or 0)
            backoff = float(retry.get('backoffMultiplier', 1) or 1)
            actual_delay = delay * (backoff ** max(0, attempt - 1))
            self._event(run_id, sid, 'step.retry_scheduled', {'attempt': attempt, 'delaySeconds': actual_delay, 'error': str(exc)})
            self._log(run_id, sid, 'stderr', str(exc))
            if actual_delay:
                time.sleep(actual_delay)
            with self._db() as db:
                db.execute('UPDATE wf_steps SET status=?,error=? WHERE run_id=? AND step_id=?', ('pending', str(exc), run_id, sid))
            return
        with self._db() as db:
            db.execute('UPDATE wf_steps SET status=?,error=?,finished_at=? WHERE run_id=? AND step_id=?', ('failed', str(exc), now(), run_id, sid))
            db.execute('UPDATE wf_runs SET status=?,error=?,updated_at=? WHERE id=?', ('failed', str(exc), now(), run_id))
        self._event(run_id, sid, 'step.failed', {'error': str(exc), 'attempt': attempt})
        self._log(run_id, sid, 'stderr', str(exc))

    def _compensate(self, run_id: str, workflow: dict[str, Any]) -> None:
        completed = {s['stepId']: s for s in self.get_run(run_id)['steps'] if s['status'] == 'completed'}
        compensable = [s for s in workflow.get('steps', []) if s['id'] in completed and s.get('compensate')]
        if not compensable:
            return
        with self._db() as db:
            db.execute('UPDATE wf_runs SET status=?,updated_at=? WHERE id=?', ('compensating', now(), run_id))
        self._event(run_id, None, 'workflow.compensating', {'steps': [s['id'] for s in compensable]})
        for step in reversed(compensable):
            comp = dict(step['compensate'])
            comp.setdefault('id', f"{step['id']}__compensate")
            try:
                spec = self.registry.get(str(comp.get('implementation') or comp.get('operation')))
                values = {k: self._resolve(run_id, v) for k, v in (comp.get('inputs') or {}).items()}
                spec.handler(values, comp.get('parameters') or {})
                with self._db() as db:
                    db.execute('UPDATE wf_steps SET status=? WHERE run_id=? AND step_id=?', ('compensated', run_id, step['id']))
                self._event(run_id, step['id'], 'step.compensated', {})
            except Exception as exc:
                self._event(run_id, step['id'], 'step.compensation_failed', {'error': str(exc)})
        with self._db() as db:
            db.execute('UPDATE wf_runs SET status=?,updated_at=? WHERE id=?', ('failed', now(), run_id))
        self._event(run_id, None, 'workflow.compensated', {})

    def refresh_children(self, run_id: str | None = None) -> None:
        with self._db() as db:
            if run_id:
                rows = db.execute('SELECT * FROM wf_run_relations WHERE parent_run_id=?', (run_id,)).fetchall()
            else:
                rows = db.execute('SELECT * FROM wf_run_relations').fetchall()
        for relation in rows:
            child = self.get_run(relation['child_run_id'])
            if child['status'] == 'completed':
                parent = self.get_run(relation['parent_run_id'])
                step_id = relation['parent_step_id']
                workflow = self.get_workflow(parent['workflowId'], parent['workflowVersion'])
                step = next(s for s in workflow['steps'] if s['id'] == step_id)
                for port, artifact_name in (step.get('outputs') or {}).items():
                    if port in child['outputs']:
                        self._artifact(parent['id'], step_id, artifact_name, 'Any', child['outputs'][port], {'childRunId': child['id']})
                with self._db() as db:
                    db.execute('UPDATE wf_steps SET status=?,finished_at=? WHERE run_id=? AND step_id=?', ('completed', now(), parent['id'], step_id))
                    db.execute('UPDATE wf_runs SET status=?,updated_at=? WHERE id=? AND status=?', ('running', now(), parent['id'], 'waiting'))
                self._event(parent['id'], step_id, 'step.completed', {'childRunId': child['id']})
            elif child['status'] in {'failed', 'cancelled'}:
                with self._db() as db:
                    db.execute('UPDATE wf_steps SET status=?,error=?,finished_at=? WHERE run_id=? AND step_id=?', ('failed', f"child run {child['status']}", now(), relation['parent_run_id'], relation['parent_step_id']))
                    db.execute('UPDATE wf_runs SET status=?,error=?,updated_at=? WHERE id=?', ('failed', f"child run {child['status']}", now(), relation['parent_run_id']))

    def _resume_parent(self, child_run_id: str) -> None:
        child = self.get_run(child_run_id)
        if child.get('parentRunId'):
            self.refresh_children(child['parentRunId'])
            self.advance(child['parentRunId'])

    def recover_interrupted_runs(self) -> None:
        with self._db() as db:
            db.execute("UPDATE wf_steps SET status='pending',error=COALESCE(error,'recovered after restart') WHERE status='running'")
            db.execute("UPDATE wf_runs SET status='running',updated_at=? WHERE status='running'", (now(),))
            rows = db.execute("SELECT id FROM wf_runs WHERE status IN ('running','waiting')").fetchall()
        self.refresh_children()
        for row in rows:
            try:
                self.advance(row['id'])
            except Exception as exc:
                self._event(row['id'], None, 'workflow.recovery_failed', {'error': str(exc)})

    def replay(self, run_id: str) -> dict[str, Any]:
        original = self.get_run(run_id)
        replayed = self.start(original['workflowId'], original['inputs'], original['workflowVersion'])
        self._event(replayed['id'], None, 'workflow.replayed', {'sourceRunId': run_id})
        return self.get_run(replayed['id'])

    def get_run(self, run_id: str) -> dict[str, Any]:
        result = super().get_run(run_id)
        with self._db() as db:
            logs = db.execute('SELECT * FROM wf_step_logs WHERE run_id=? ORDER BY id', (run_id,)).fetchall()
            children = db.execute('SELECT * FROM wf_run_relations WHERE parent_run_id=? ORDER BY created_at', (run_id,)).fetchall()
        result['logs'] = [{'id': r['id'], 'stepId': r['step_id'], 'stream': r['stream'], 'message': r['message'], 'createdAt': r['created_at']} for r in logs]
        result['children'] = [{'stepId': r['parent_step_id'], 'runId': r['child_run_id']} for r in children]
        return result
