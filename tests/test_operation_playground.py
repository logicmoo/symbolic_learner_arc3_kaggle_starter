from __future__ import annotations

import shutil

import pytest

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


@pytest.mark.skipif(shutil.which("swipl") is None, reason="SWI-Prolog is not installed")
def test_operation_playground_invokes_swi_prolog_variant() -> None:
    result = invoke_operation("shared", "echo_into_titlecased", {
        "implementationVariant": "echo_into_titlecased_prolog",
        "inputs": {"text": "the quick brown fox"},
    })
    assert result["outputs"]["text"] == "The Quick Brown Fox"
    assert result["outputs"]["execution"]["predicate"] == "titlecase_text"
    assert result["implementation"]["route"] == "prolog.source"
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


def test_constant_value_uses_workbench_provider() -> None:
    result = invoke_operation("shared", "shared.constant", {
        "implementationVariant": "shared.constant.workbench",
        "inputs": {},
        "parameters": {"value": 42},
    })
    assert result["implementation"]["route"] == "system.workbench"
    assert result["outputs"] == {"value": 42}


def test_user_request_materializes_as_human_input() -> None:
    executable = materialize_workflow_step(
        {"id": "sample", "workspaceId": "shared"},
        {
            "id": "ask",
            "operation": "sample.request_number",
            "parameters": {"prompt": "Enter the count", "datatype": "Number"},
        },
    )
    assert executable["kind"] == "human"
    assert executable["implementation"] == "system.workbench"
    assert executable["form"]["value"]["prompt"] == "Enter the count"
    assert executable["form"]["value"]["type"] == "Number"

    preview = invoke_operation("shared", "sample.request_number", {"inputs": {}})
    assert preview["outputs"]["status"] == "waiting_for_input"
    assert preview["outputs"]["form"]["value"]["type"] == "Number"
    assert preview["outputs"]["form"]["value"]["prompt"] == "How many objects are visible?"
