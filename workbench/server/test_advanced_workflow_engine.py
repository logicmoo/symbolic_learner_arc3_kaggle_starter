from pathlib import Path

from advanced_workflow_engine import AdvancedWorkflowEngine


def engine(tmp_path: Path) -> AdvancedWorkflowEngine:
    return AdvancedWorkflowEngine(tmp_path / 'engine.db')


def test_dependency_graph_condition_and_fan_in(tmp_path: Path) -> None:
    runtime = engine(tmp_path)
    runtime.save_workflow({
        'id': 'dag',
        'inputs': {'seed': 'Any'},
        'outputs': {'merged': '$merged'},
        'steps': [
            {'id': 'left', 'kind': 'task', 'implementation': 'core.constant', 'parameters': {'value': {'a': 1}}, 'outputs': {'value': 'left'}},
            {'id': 'right', 'kind': 'task', 'implementation': 'core.constant', 'parameters': {'value': {'b': 2}}, 'outputs': {'value': 'right'}},
            {'id': 'merge', 'kind': 'task', 'implementation': 'core.merge', 'dependsOn': ['left', 'right'],
             'inputs': {'left': '$left', 'right': '$right'}, 'outputs': {'value': 'merged'}},
            {'id': 'skip', 'kind': 'task', 'implementation': 'core.constant', 'when': False,
             'parameters': {'value': 99}, 'outputs': {'value': 'never'}},
        ],
    })
    run = runtime.start('dag', {'seed': 0})
    assert run['status'] == 'completed'
    assert run['outputs']['merged'] == {'a': 1, 'b': 2}
    assert next(step for step in run['steps'] if step['stepId'] == 'skip')['status'] == 'skipped'


def test_foreach_aggregates_outputs(tmp_path: Path) -> None:
    runtime = engine(tmp_path)
    runtime.save_workflow({
        'id': 'foreach',
        'inputs': {'items': 'Array'},
        'outputs': {'values': '$values'},
        'steps': [{
            'id': 'map', 'kind': 'task', 'implementation': 'core.echo',
            'inputs': {'value': None},
            'foreach': {'items': '$items', 'itemPort': 'value', 'maxItems': 10},
            'outputs': {'value': 'values'},
        }],
    })
    run = runtime.start('foreach', {'items': [1, 2, 3]})
    assert run['status'] == 'completed'
    assert run['outputs']['values'] == [1, 2, 3]


def test_human_wait_resume_and_logs(tmp_path: Path) -> None:
    runtime = engine(tmp_path)
    runtime.save_workflow({
        'id': 'human',
        'inputs': {},
        'outputs': {'answer': '$answer'},
        'steps': [{
            'id': 'approval', 'kind': 'human',
            'form': {'answer': {'type': 'Boolean'}},
            'outputs': {'answer': 'answer'},
        }],
    })
    waiting = runtime.start('human', {})
    assert waiting['status'] == 'waiting'
    finished = runtime.submit_human_input(waiting['id'], 'approval', {'answer': True})
    assert finished['status'] == 'completed'
    assert finished['outputs']['answer'] is True


def test_retry_events_and_failure(tmp_path: Path) -> None:
    runtime = engine(tmp_path)
    runtime.save_workflow({
        'id': 'failure', 'inputs': {}, 'outputs': {},
        'steps': [{
            'id': 'fail', 'kind': 'task', 'implementation': 'core.fail',
            'parameters': {'message': 'boom'},
            'retry': {'maxAttempts': 2, 'delaySeconds': 0},
        }],
    })
    run = runtime.start('failure', {})
    assert run['status'] == 'failed'
    kinds = [event['kind'] for event in run['events']]
    assert 'step.retry_scheduled' in kinds
    assert 'step.failed' in kinds


def test_replay_creates_new_run(tmp_path: Path) -> None:
    runtime = engine(tmp_path)
    runtime.save_workflow({
        'id': 'replayable', 'inputs': {'x': 'Any'}, 'outputs': {'x': '$x'}, 'steps': []
    })
    first = runtime.start('replayable', {'x': 7})
    second = runtime.replay(first['id'])
    assert second['id'] != first['id']
    assert second['outputs']['x'] == 7
    assert any(event['kind'] == 'workflow.replayed' for event in second['events'])


def test_cycle_validation(tmp_path: Path) -> None:
    runtime = engine(tmp_path)
    errors = runtime.validate({
        'id': 'cycle', 'inputs': {}, 'outputs': {},
        'steps': [
            {'id': 'a', 'kind': 'task', 'implementation': 'core.constant', 'dependsOn': ['b'], 'outputs': {'value': 'a'}},
            {'id': 'b', 'kind': 'task', 'implementation': 'core.constant', 'dependsOn': ['a'], 'outputs': {'value': 'b'}},
        ],
    })
    assert any('cycle' in error for error in errors)
