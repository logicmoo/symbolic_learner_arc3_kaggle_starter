from pathlib import Path

from advanced_workflow_engine import AdvancedWorkflowEngine
from workflow_engine import OperationRegistry, OperationSpec, WorkflowEngine


def _engine(tmp_path: Path) -> WorkflowEngine:
    registry = OperationRegistry()
    registry.register(OperationSpec("text.consume", {"text": "Text"}, {"value": "Text"}, lambda inputs, _parameters: {"value": inputs["text"]}))
    return WorkflowEngine(tmp_path / "workflow.db", registry)


def test_validation_rejects_unavailable_artifact_binding(tmp_path: Path) -> None:
    errors = _engine(tmp_path).validate({
        "id": "missing-binding",
        "steps": [{
            "id": "consume",
            "kind": "operation",
            "implementation": "text.consume",
            "inputs": {"text": "$not_produced"},
            "outputs": {"value": "result"},
        }],
    })

    assert "consume.text references unavailable artifact $not_produced" in errors


def test_validation_rejects_incompatible_artifact_contract(tmp_path: Path) -> None:
    errors = _engine(tmp_path).validate({
        "id": "wrong-contract",
        "inputs": {"count": "Number"},
        "steps": [{
            "id": "consume",
            "kind": "operation",
            "implementation": "text.consume",
            "inputs": {"text": "$count"},
            "outputs": {"value": "result"},
        }],
    })

    assert "consume.text expects Text but $count is Number" in errors


def test_validation_tracks_operation_and_human_output_contracts(tmp_path: Path) -> None:
    engine = _engine(tmp_path)
    valid = {
        "id": "typed-chain",
        "inputs": {"source": "String"},
        "outputs": {"result": "$final"},
        "steps": [
            {
                "id": "first",
                "kind": "operation",
                "implementation": "text.consume",
                "inputs": {"text": "$source"},
                "outputs": {"value": "normalized"},
            },
            {
                "id": "second",
                "kind": "operation",
                "implementation": "text.consume",
                "inputs": {"text": "$normalized"},
                "outputs": {"value": "final"},
            },
        ],
    }

    assert engine.validate(valid) == []


def test_validation_rejects_missing_workflow_output_artifact(tmp_path: Path) -> None:
    errors = _engine(tmp_path).validate({"id": "bad-output", "outputs": {"result": "$missing"}, "steps": []})

    assert "workflow output result references unavailable artifact $missing" in errors


def test_foreach_item_port_is_injected_without_resolving_a_fake_artifact(tmp_path: Path) -> None:
    registry = OperationRegistry()
    registry.register(OperationSpec("value.echo", {"value": "Any"}, {"value": "Any"}, lambda inputs, _parameters: {"value": inputs["value"]}))
    engine = AdvancedWorkflowEngine(tmp_path / "foreach.db", registry)
    workflow = {
        "id": "foreach-values",
        "inputs": {"items": "Array"},
        "outputs": {"values": "$values"},
        "steps": [{
            "id": "map",
            "kind": "operation",
            "implementation": "value.echo",
            "inputs": {"value": "$item"},
            "foreach": {"items": "$items", "itemPort": "value", "maxItems": 10},
            "outputs": {"value": "values"},
        }],
    }

    assert engine.validate(workflow) == []
    engine.save_workflow(workflow)
    run = engine.start("foreach-values", {"items": ["a", "b"]})

    assert run["status"] == "completed"
    assert run["outputs"] == {"values": ["a", "b"]}
