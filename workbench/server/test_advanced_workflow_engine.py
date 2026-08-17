from pathlib import Path

from advanced_workflow_engine import AdvancedWorkflowEngine
from workflow_engine import OperationSpec


def engine(tmp_path: Path) -> AdvancedWorkflowEngine:
    return AdvancedWorkflowEngine(tmp_path / 'engine.db')


def test_dependency_graph_condition_and_fan_in(tmp_path: Path) -> None:
    runtime = engine(tmp_path)
    runtime.save_workflow({
        'id': 'dag',
        'inputs': {'seed': 'Any'},
        'outputs': {'merged': '$merged'},
        'steps': [
            {'id': 'left', 'kind': 'operation', 'implementation': 'core.constant', 'parameters': {'value': {'a': 1}}, 'outputs': {'value': 'left'}},
            {'id': 'right', 'kind': 'operation', 'implementation': 'core.constant', 'parameters': {'value': {'b': 2}}, 'outputs': {'value': 'right'}},
            {'id': 'merge', 'kind': 'operation', 'implementation': 'core.merge', 'dependsOn': ['left', 'right'],
             'inputs': {'left': '$left', 'right': '$right'}, 'outputs': {'value': 'merged'}},
            {'id': 'skip', 'kind': 'operation', 'implementation': 'core.constant', 'when': False,
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
            'id': 'map', 'kind': 'operation', 'implementation': 'core.echo',
            'inputs': {'value': None},
            'foreach': {'items': '$items', 'itemPort': 'value', 'maxItems': 10},
            'outputs': {'value': 'values'},
        }],
    })
    run = runtime.start('foreach', {'items': [1, 2, 3]})
    assert run['status'] == 'completed'
    assert run['outputs']['values'] == [1, 2, 3]


def test_bounded_while_reexecutes_region_until_nested_condition_changes(tmp_path: Path) -> None:
    runtime = engine(tmp_path)
    runtime.registry.register(OperationSpec(
        'test.increment',
        {'value': 'Number'},
        {'result': 'Object'},
        lambda inputs, _parameters: {'result': {'count': inputs['value'] + 1}},
    ))
    runtime.save_workflow({
        'id': 'bounded-while',
        'inputs': {'state': 'Object'},
        'outputs': {'count': '$state.count'},
        'steps': [{
            'id': 'increment',
            'kind': 'operation',
            'implementation': 'test.increment',
            'inputs': {'value': '$state.count'},
            'outputs': {'result': 'state'},
            'while': {
                'condition': '$state.count',
                'operator': 'less_than',
                'conditionPort': 3,
                'maxIterations': 5,
                'targetStepId': 'increment',
            },
        }],
    })
    # Seed the same structured value shape consumed by subsequent iterations.
    run = runtime.start('bounded-while', {'state': {'count': 0}})

    assert run['status'] == 'completed'
    assert run['outputs'] == {'count': 3}
    iterations = [event for event in run['events'] if event['kind'] == 'loop.iteration']
    assert [event['payload']['iteration'] for event in iterations] == [1, 2]
    assert next(step for step in run['steps'] if step['stepId'] == 'increment')['attempt'] == 3


def test_bounded_while_fails_when_condition_outlives_iteration_limit(tmp_path: Path) -> None:
    runtime = engine(tmp_path)
    runtime.save_workflow({
        'id': 'bounded-while-limit',
        'outputs': {},
        'steps': [{
            'id': 'again',
            'kind': 'operation',
            'implementation': 'core.constant',
            'parameters': {'value': True},
            'outputs': {'value': 'again'},
            'while': {
                'condition': '$again',
                'operator': 'truthy',
                'maxIterations': 2,
            },
        }],
    })

    run = runtime.start('bounded-while-limit', {})

    assert run['status'] == 'failed'
    assert 'exceeded maxIterations=2' in run['error']
    assert next(step for step in run['steps'] if step['stepId'] == 'again')['attempt'] == 2


def test_while_validation_requires_positive_bound_and_backward_target(tmp_path: Path) -> None:
    runtime = engine(tmp_path)
    errors = runtime.validate({
        'id': 'invalid-while',
        'steps': [
            {
                'id': 'controller',
                'kind': 'operation',
                'implementation': 'core.constant',
                'parameters': {'value': True},
                'outputs': {'value': 'value'},
                'while': {'condition': '$value', 'maxIterations': 0, 'targetStepId': 'later'},
            },
            {
                'id': 'later',
                'kind': 'operation',
                'implementation': 'core.constant',
                'parameters': {'value': False},
                'outputs': {'value': 'later'},
            },
        ],
    })

    assert 'controller.while[0].maxIterations must be positive' in errors
    assert 'controller.while[0] targetStepId must not follow its controller' in errors


def test_while_validation_reports_bad_operator_binding_and_bound_without_crashing(tmp_path: Path) -> None:
    runtime = engine(tmp_path)
    errors = runtime.validate({
        'id': 'malformed-while',
        'steps': [{
            'id': 'controller',
            'kind': 'operation',
            'implementation': 'core.constant',
            'parameters': {'value': True},
            'outputs': {'value': 'available'},
            'while': {
                'condition': '$missing.value',
                'operator': 'approximately',
                'maxIterations': 'many',
            },
        }],
    })

    assert 'controller.while[0].maxIterations must be an integer' in errors
    assert 'controller.while[0] has unsupported operator: approximately' in errors
    assert 'controller.while[0].condition references unavailable artifact $missing' in errors


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
            'id': 'fail', 'kind': 'operation', 'implementation': 'core.fail',
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
            {'id': 'a', 'kind': 'operation', 'implementation': 'core.constant', 'dependsOn': ['b'], 'outputs': {'value': 'a'}},
            {'id': 'b', 'kind': 'operation', 'implementation': 'core.constant', 'dependsOn': ['a'], 'outputs': {'value': 'b'}},
        ],
    })
    assert any('cycle' in error for error in errors)
