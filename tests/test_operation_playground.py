from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest
from fastapi import HTTPException
from urllib.error import HTTPError

from operation_api import invoke_operation
from operation_library import DEFAULT_WORKSPACES_ROOT, resolve_operation_implementation
from operation_resolution import materialize_workflow_step
from workflow_providers import _llm_complete


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
    assert executable["modelSelection"] == {"models": ["openrouter/free"], "strategy": "single"}
    assert executable["parameters"]["model"] == "openrouter/free"
    assert executable["parameters"]["backendId"] == "openrouter"
    assert executable["parameters"]["apiKeyEnv"] == "OPENROUTER_API_KEY"
    assert executable["parameters"]["baseUrl"] == "https://openrouter.ai/api/v1"


def test_operation_playground_routes_selected_model_through_openrouter(monkeypatch: pytest.MonkeyPatch) -> None:
    sent: dict[str, object] = {}

    class Response:
        def __enter__(self): return self
        def __exit__(self, *_args: object) -> None: return None
        def read(self) -> bytes:
            return json.dumps({"choices": [{"message": {"content": "Hello World"}}]}).encode()

    def urlopen(request: object, **_kwargs: object) -> Response:
        sent["url"] = getattr(request, "full_url")
        sent["authorization"] = getattr(request, "headers")["Authorization"]
        sent["body"] = json.loads(getattr(request, "data").decode())
        return Response()

    monkeypatch.setenv("OPENROUTER_API_KEY", "openrouter-test-key")
    monkeypatch.setattr("workflow_providers.urllib.request.urlopen", urlopen)

    result = invoke_operation("shared", "echo_into_titlecased", {
        "implementationVariant": "echo_into_titlecased_llm",
        "inputs": {"text": "hello world"},
    })

    assert sent["url"] == "https://openrouter.ai/api/v1/chat/completions"
    assert sent["authorization"] == "Bearer openrouter-test-key"
    assert sent["body"]["model"] == "openrouter/free"  # type: ignore[index]
    assert result["outputs"]["text"] == "Hello World"


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


def test_implementation_parent_link_is_sufficient_for_resolution(tmp_path: Path) -> None:
    directory = tmp_path / "shared" / "design" / "operations"
    directory.mkdir(parents=True)
    (directory / "echo.operation.json").write_text(json.dumps({
        "kind": "operation", "id": "shared.echo", "inputs": {"value": "Any"}, "outputs": {"value": "Any"},
    }), encoding="utf-8")
    implementations = tmp_path / "shared" / "design" / "operation_implementations"
    implementations.mkdir(parents=True)
    (implementations / "echo_prolog.operation_implementation.json").write_text(json.dumps({
        "kind": "operation_implementation",
        "id": "shared.echo.prolog",
        "parents": ["shared.echo"],
        "implementation": "prolog.source",
    }), encoding="utf-8")

    resolved = resolve_operation_implementation(
        tmp_path / "shared", "shared.echo", "shared.echo.prolog", workspaces_root=tmp_path,
    )

    assert resolved["implementation"]["id"] == "shared.echo.prolog"


def test_operation_playground_preserves_provider_rate_limit(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")

    def rate_limited(*_args: object, **_kwargs: object) -> object:
        raise HTTPError("https://provider.invalid", 429, "Too Many Requests", {}, None)

    monkeypatch.setattr("workflow_providers.urllib.request.urlopen", rate_limited)
    with pytest.raises(HTTPException) as caught:
        invoke_operation("shared", "echo_into_titlecased", {
            "implementationVariant": "echo_into_titlecased_llm",
            "inputs": {"text": "hello"},
        })

    assert caught.value.status_code == 429
    assert "provider request failed with HTTP 429" in str(caught.value.detail)


def test_automatic_vision_variant_sends_bitmap_inputs_and_parses_json(monkeypatch: pytest.MonkeyPatch) -> None:
    resolved = resolve_operation_implementation(DEFAULT_WORKSPACES_ROOT / "shared", "vision.extract_scene_objects")
    assert resolved["implementation"]["id"] == "vision.extract_scene_objects.automatic_llm"
    sent: dict[str, object] = {}

    class Response:
        def __enter__(self): return self
        def __exit__(self, *_args: object) -> None: return None
        def read(self) -> bytes:
            return json.dumps({"choices": [{"message": {"content": '{"objects":[],"reconstruction":""}'}}]}).encode()

    def urlopen(request: object, **_kwargs: object) -> Response:
        sent.update(json.loads(getattr(request, "data").decode()))
        return Response()

    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr("workflow_providers.urllib.request.urlopen", urlopen)
    output = _llm_complete(
        {"current_image": "data:image/png;base64,AAAA", "previous_image": ""},
        {"promptPrefix": "Extract objects", "parseJson": True, "responseFormat": "json_object"},
    )
    content = sent["messages"][0]["content"]  # type: ignore[index]
    assert any(item.get("type") == "image_url" for item in content)
    assert sent["response_format"] == {"type": "json_object"}
    assert output == {"objects": [], "reconstruction": ""}
