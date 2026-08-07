from __future__ import annotations

from operation_api import invoke_operation
from operation_resolution import materialize_workflow_step


def test_operation_playground_invokes_python_variant() -> None:
    result = invoke_operation(
        "shared",
        "echo_into_titlecased",
        {
            "implementationVariant": "echo_into_titlecased_python",
            "inputs": {"text": "hello symbolic world"},
        },
    )
    assert result["implementation"]["id"] == "echo_into_titlecased_python"
    assert result["implementation"]["route"] == "python.callable"
    assert result["outputs"]["text"] == "Hello Symbolic World"
    assert result["elapsedMs"] >= 0


def test_operation_materialization_resolves_requested_prompt_variant() -> None:
    executable = materialize_workflow_step(
        {"id": "playground", "workspaceId": "shared"},
        {
            "id": "invoke",
            "operation": "echo_into_titlecased",
            "implementationVariant": "echo_into_titlecased_llm",
            "inputs": {"text": "hello world"},
            "promptVariants": {
                "titlecase_received_text": "titlecase_received_text.text_only.claude"
            },
        },
    )
    assert executable["implementation"] == "llm.complete"
    assert executable["inputs"] == {"prompt": "hello world"}
    assert executable["resolvedPrompts"] == [
        {
            "promptId": "titlecase_received_text",
            "implementationId": "titlecase_received_text.text_only.claude",
            "inline": False,
            "targets": ["anthropic", "claude"],
            "version": 1,
        }
    ]
    assert "Convert" in executable["parameters"]["promptPrefix"]
