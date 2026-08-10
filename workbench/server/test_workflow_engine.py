from pathlib import Path

from workflow_engine import OperationRegistry, OperationSpec, WorkflowEngine, default_registry


def engine(tmp_path: Path) -> WorkflowEngine:
    return WorkflowEngine(tmp_path / 'engine.db', default_registry())


def test_versioned_workflow_and_artifacts(tmp_path: Path) -> None:
    e = engine(tmp_path)
    wf = e.save_workflow({
        'id': 'echo_flow',
        'inputs': {'message': 'String'},
        'outputs': {'result': '$slots.echoed'},
        'steps': [{
            'id': 'echo', 'kind': 'operation', 'implementation': 'core.echo',
            'inputs': {'value': '$workflow.message'},
            'outputs': {'value': 'echoed'},
        }],
    })
    assert wf['version'] == 1
    run = e.start('echo_flow', {'message': 'hello'})
    assert run['status'] == 'completed'
    assert run['outputs']['result'] == 'hello'
    assert any(a['name'] == 'echoed' and a['contentHash'] for a in run['artifacts'])
    assert any(event['kind'] == 'workflow.completed' for event in run['events'])


def test_artifacts_preserve_datatype_representation_contract(tmp_path: Path) -> None:
    registry = OperationRegistry()
    registry.register(OperationSpec(
        'test.scene', {},
        {'image': {'datatype': 'Image', 'representation': 'scene_graph'}},
        lambda _inputs, _params: {'image': {'objects': []}},
    ))
    e = WorkflowEngine(tmp_path / 'engine.db', registry)
    e.save_workflow({
        'id': 'represented_artifact', 'inputs': {}, 'outputs': {},
        'steps': [{'id': 'scene', 'kind': 'operation', 'implementation': 'test.scene',
                   'inputs': {}, 'outputs': {'image': 'scene_image'}}],
    })

    run = e.start('represented_artifact', {})
    artifact = next(item for item in run['artifacts'] if item['name'] == 'scene_image')
    assert artifact['datatype'] == 'Image'
    assert artifact['representation'] == 'scene_graph'
    assert artifact['createdAt']
    event = next(item for item in run['events'] if item['kind'] == 'artifact.created')
    assert event['payload']['representation'] == 'scene_graph'


def test_direct_dollar_binding_resolves_workflow_input(tmp_path: Path) -> None:
    e = engine(tmp_path)
    e.save_workflow({
        'id': 'direct_binding', 'inputs': {'payload': 'Object'}, 'outputs': {},
        'steps': [{'id': 'echo', 'kind': 'operation', 'implementation': 'core.echo',
                   'inputs': {'value': '$payload'}, 'outputs': {'value': 'copied'}}],
    })
    run = e.start('direct_binding', {'payload': {'value': 3}})
    assert run['status'] == 'completed'
    assert next(item for item in run['artifacts'] if item['name'] == 'copied')['payload'] == {'value': 3}


def test_human_step_waits_and_resumes(tmp_path: Path) -> None:
    e = engine(tmp_path)
    e.save_workflow({
        'id': 'approval', 'inputs': {}, 'outputs': {'choice': '$slots.choice'},
        'steps': [{
            'id': 'ask', 'kind': 'human',
            'form': {'choice': {'type': 'String'}},
            'outputs': {'choice': 'choice'},
        }],
    })
    run = e.start('approval', {})
    assert run['status'] == 'waiting'
    run = e.submit_human_input(run['id'], 'ask', {'choice': 'approved'})
    assert run['status'] == 'completed'
    assert run['outputs']['choice'] == 'approved'


def test_human_input_draft_survives_restart_and_omits_secrets(tmp_path: Path) -> None:
    path = tmp_path / 'engine.db'
    e = WorkflowEngine(path, default_registry())
    e.save_workflow({
        'id': 'drafted', 'inputs': {}, 'outputs': {},
        'steps': [{'id': 'ask', 'kind': 'human', 'form': {
            'choice': {'type': 'String'}, 'token': {'type': 'String', 'secret': True},
        }, 'outputs': {'choice': 'choice', 'token': 'token'}}],
    })
    run = e.start('drafted', {})
    draft = e.save_human_input_draft(run['id'], 'ask', {'choice': 'yes', 'token': 'do-not-store', 'extra': 4})
    assert draft['values'] == {'choice': 'yes'}
    assert set(draft['omittedFields']) == {'token', 'extra'}
    reopened = WorkflowEngine(path, default_registry())
    assert reopened.get_human_input_draft(run['id'], 'ask')['values'] == {'choice': 'yes'}
    reopened.submit_human_input(run['id'], 'ask', {'choice': 'yes', 'token': 'used-once'})
    assert reopened.get_human_input_draft(run['id'], 'ask')['values'] == {}


def test_retry_policy(tmp_path: Path) -> None:
    attempts = {'count': 0}
    registry = OperationRegistry()

    def flaky(inputs, params):
        attempts['count'] += 1
        if attempts['count'] == 1:
            raise RuntimeError('temporary')
        return {'value': 7}

    registry.register(OperationSpec('test.flaky', {}, {'value': 'Integer'}, flaky))
    e = WorkflowEngine(tmp_path / 'engine.db', registry)
    e.save_workflow({
        'id': 'retry', 'inputs': {}, 'outputs': {'value': '$slots.value'},
        'steps': [{
            'id': 'flaky', 'kind': 'operation', 'implementation': 'test.flaky',
            'inputs': {}, 'outputs': {'value': 'value'},
            'retry': {'maxAttempts': 2},
        }],
    })
    run = e.start('retry', {})
    assert run['status'] == 'completed'
    assert attempts['count'] == 2
    assert any(event['kind'] == 'step.retrying' for event in run['events'])
    assert any(log['stream'] == 'stderr' and log['message'] == 'temporary' for log in run['logs'])


def test_subprocess_style_output_is_persisted_as_run_logs(tmp_path: Path) -> None:
    registry = OperationRegistry()
    registry.register(OperationSpec('test.process', {}, {'result': 'Object'}, lambda _inputs, _params: {
        'result': {'stdout': 'answer\n', 'stderr': 'warning\n', 'returncode': 0},
    }))
    e = WorkflowEngine(tmp_path / 'engine.db', registry)
    e.save_workflow({'id': 'logged', 'inputs': {}, 'outputs': {}, 'steps': [{
        'id': 'process', 'kind': 'operation', 'implementation': 'test.process',
        'inputs': {}, 'outputs': {'result': 'process_result'},
    }]})
    run = e.start('logged', {})
    assert [(entry['stream'], entry['message']) for entry in run['logs']] == [
        ('stdout', 'answer\n'), ('stderr', 'warning\n'),
    ]


def test_pause_resume_cancel(tmp_path: Path) -> None:
    e = engine(tmp_path)
    e.save_workflow({
        'id': 'pause_flow', 'inputs': {}, 'outputs': {'choice': '$slots.choice'},
        'steps': [{'id': 'wait', 'kind': 'human', 'form': {'choice': {'type': 'String'}}, 'outputs': {'choice': 'choice'}}],
    })
    run = e.start('pause_flow', {})
    run = e.command(run['id'], 'cancel')
    assert run['status'] == 'cancelled'


def test_durable_run_history_and_goal_run_linkage(tmp_path: Path) -> None:
    e = engine(tmp_path)
    e.save_workflow({
        'id': 'goal_flow', 'inputs': {}, 'outputs': {},
        'steps': [{'id': 'constant', 'kind': 'operation', 'implementation': 'core.constant',
                   'parameters': {'value': 1}, 'outputs': {'value': 'value'}}],
    })
    workflow_run = e.start('goal_flow', {})
    goal_run = e.create_goal_run(
        'default', 'solve', 'solve.safe', 'observe', 'observe.default',
        'vision_analysis', 'vision_analysis.default', workflow_run['id'],
    )
    assert goal_run['status'] == 'completed'
    assert goal_run['workflowRunId'] == workflow_run['id']
    assert e.list_runs()[0]['id'] == workflow_run['id']
    assert e.list_goal_runs('default')[0]['goalVariantId'] == 'solve.safe'
    assert e.get_goal_run(goal_run['id'])['contextId'] == 'vision_analysis'
    assert e.get_goal_run(goal_run['id'])['contextVariantId'] == 'vision_analysis.default'

    reopened = WorkflowEngine(tmp_path / 'engine.db', default_registry())
    assert reopened.list_goal_runs('default')[0]['contextVariantId'] == 'vision_analysis.default'


def test_run_history_is_scoped_to_workspace_and_survives_restart(tmp_path: Path) -> None:
    path = tmp_path / 'engine.db'
    e = WorkflowEngine(path, default_registry())
    e.save_workflow({'id': 'scoped', 'inputs': {}, 'outputs': {}, 'steps': []})

    alpha = e.start('scoped', {}, workspace_id='alpha')
    beta = e.start('scoped', {}, workspace_id='beta')

    assert alpha['workspaceId'] == 'alpha'
    assert [run['id'] for run in e.list_runs(workspace_id='alpha')] == [alpha['id']]
    assert [run['id'] for run in e.list_runs(workspace_id='beta')] == [beta['id']]
    assert {run['id'] for run in e.list_runs()} == {alpha['id'], beta['id']}

    reopened = WorkflowEngine(path, default_registry())
    assert reopened.get_run(alpha['id'])['workspaceId'] == 'alpha'
