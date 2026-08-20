from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from urllib.error import HTTPError

from operation_api import invoke_operation, read_operation_debug_log
from operation_library import DEFAULT_WORKSPACES_ROOT, load_shared_operation_documents, resolve_operation_implementation
from operation_resolution import _prompt_composition_prefix, materialize_workflow_step
from prompt_library import prompt_hierarchy, resolve_prompt_profile
from workflow_providers import _llm_complete, _llm_response_text, _load_python_module, _python_callable


def test_resource_tool_operations_use_declared_semantic_datatypes() -> None:
    operations = {item["id"]: item for item in load_shared_operation_documents()}
    expected = {
        "resource_validate": ("Resource", "ResourceValidation"),
        "datatype_sample": ("DatatypeContract", "DatatypeSample"),
        "datatype_conversion_inspect": ("DatatypeContract", "ConversionInventory"),
        "prompt_render": ("PromptResource", "Text"),
        "prompt_compose": ("PromptResource", "PromptComposition"),
        "goal_evaluate": ("Goal", "Evaluation"),
        "goal_interpret": ("Goal", "GoalInterpretation"),
        "goal_check_satisfaction": ("Goal", "GoalSatisfaction"),
        "planning_strategy_generate": ("PlanningStrategy", "PlannedWorkflow"),
        "atomspace_query": ("AtomSpace", "AtomSpaceQueryResult"),
        "atomspace_assert": ("AtomSpace", "AtomSpaceChange"),
        "atomspace_retract": ("AtomSpace", "AtomSpaceChange"),
        "system_inspect": ("SystemContract", "SystemInspection"),
        "system_check_readiness": ("SystemContract", "SystemReadiness"),
        "data_inspect": ("DataValue", "DataInspection"),
        "artifact_inspect": ("Artifact", "ArtifactInspection"),
        "policy_evaluate": ("Policy", "PolicyDecision"),
        "category_resolve_matches": ("ArtifactCategory", "CategoryMatchSet"),
    }
    for operation_id, (input_type, output_type) in expected.items():
        operation = operations[operation_id]
        assert operation["inputs"] == {"resource": input_type}
        assert operation["outputs"] == {"result": output_type}
        assert "Any" not in {*operation["inputs"].values(), *operation["outputs"].values()}


def test_operation_playground_invokes_python_variant() -> None:
    result = invoke_operation(
        "shared_library_system",
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
    trace = json.loads(read_operation_debug_log("shared_library_system", result["debugLogPath"])["content"])
    assert trace["status"] == "completed"
    assert trace["providerExecution"]["provider"] == "python.callable"
    assert trace["providerExecution"]["stdout"] == ""
    assert trace["providerExecution"]["stderr"] == ""


def test_operation_playground_materializes_human_input_variant() -> None:
    executable = materialize_workflow_step(
        {"id": "playground", "workspaceId": "arc3_random_player"},
        {
            "id": "select_game",
            "operation": "arc3_random.select_game",
            "implementationVariant": "arc3_random.select_game.manual",
            "inputs": {"games": [], "previous_game_id": "", "seed": 0},
        },
    )

    assert executable["kind"] == "human"
    assert executable["implementation"] == "human.await_input"
    assert executable["form"]["game"]["prompt"] == "Enter the ARC game name or ID"
    assert executable["outputs"] == {"game": "Object"}

    response = invoke_operation(
        "arc3_random_player",
        "arc3_random.select_game",
        {
            "implementationVariant": "arc3_random.select_game.manual",
            "inputs": {"games": [], "previous_game_id": "", "seed": 0},
        },
    )
    assert response["implementation"]["route"] == "human.await_input"
    assert response["outputs"]["status"] == "waiting_for_input"
    assert response["outputs"]["form"]["game"]["prompt"] == "Enter the ARC game name or ID"


def test_resource_tool_operations_execute_real_filesystem_resources() -> None:
    atomspace = {
        "kind": "atomspace",
        "id": "test_space",
        "label": "Test Space",
        "bindings": ["facts", "rules"],
    }
    query = invoke_operation("shared_library_system", "atomspace_query", {"inputs": {"resource": atomspace}})
    assert query["implementation"]["route"] == "resource.tool"
    assert query["outputs"]["result"]["query"] == ["facts", "rules"]
    asserted = invoke_operation("shared_library_system", "atomspace_assert", {"inputs": {"resource": atomspace}})
    assert asserted["outputs"]["result"]["event"] == "atomspace.changed"
    retracted = invoke_operation("shared_library_system", "atomspace_retract", {"inputs": {"resource": atomspace}})
    assert retracted["outputs"]["result"]["event"] == "atomspace.changed"


def test_system_resource_tools_inspect_and_check_readiness_without_execution() -> None:
    system = {
        "kind": "system",
        "id": "test_runtime",
        "label": "Test Runtime",
        "provider": "python",
        "systemType": "runtime",
        "enabled": True,
        "capabilities": ["python.callable"],
        "configuration": {"executable": "python", "timeoutSeconds": 30},
    }
    inspected = invoke_operation("shared_library_system", "system_inspect", {"inputs": {"resource": system}})
    assert inspected["outputs"]["result"]["capabilities"] == ["python.callable"]
    assert inspected["outputs"]["result"]["configurationKeys"] == ["executable", "timeoutSeconds"]
    readiness = invoke_operation("shared_library_system", "system_check_readiness", {"inputs": {"resource": system}})
    assert readiness["outputs"]["result"]["ready"] is True
    assert readiness["outputs"]["result"]["connectionDeclared"] is True


def test_knowledge_file_resource_tools_inspect_loaded_values() -> None:
    data = {
        "kind": "data",
        "id": "knowledge/data/examples/example.json",
        "label": "example.json",
        "workspacePath": "knowledge/data/examples/example.json",
        "format": ".json",
        "mediaType": "application/json",
        "size": 21,
        "value": {"example": True},
        "valueEncoding": "text",
    }
    inspected_data = invoke_operation(
        "shared_library_system", "data_inspect", {"inputs": {"resource": data}}
    )["outputs"]["result"]
    assert inspected_data["workspacePath"] == data["workspacePath"]
    assert inspected_data["valueType"] == "dict"
    assert inspected_data["hasValue"] is True

    artifact = {
        **data,
        "kind": "artifact",
        "id": "runtime/artifacts/result.png",
        "workspacePath": "runtime/artifacts/result.png",
        "format": ".png",
        "mediaType": "image/png",
        "value": "data:image/png;base64,AA==",
        "valueEncoding": "data-url",
    }
    inspected_artifact = invoke_operation(
        "shared_library_system", "artifact_inspect", {"inputs": {"resource": artifact}}
    )["outputs"]["result"]
    assert inspected_artifact["storage"] == "runtime"
    assert inspected_artifact["valueType"] == "str"
    assert inspected_artifact["valueEncoding"] == "data-url"


def test_python_provider_captures_stdout_and_stderr(monkeypatch: pytest.MonkeyPatch) -> None:
    def noisy(value: str) -> str:
        print(f"stdout: {value}")
        print(f"stderr: {value}", file=sys.stderr)
        return value.upper()

    monkeypatch.setattr("workflow_providers._load_python_module", lambda _source: SimpleNamespace(noisy=noisy))
    parameters: dict[str, object] = {
        "source": {"importMode": "module", "module": "fake", "callable": "noisy"},
        "outputBinding": "value",
    }
    assert _python_callable({"value": "hello"}, parameters) == {"value": "HELLO"}
    debug = parameters["_debugExecution"]
    assert isinstance(debug, dict)
    assert debug["stdout"] == "stdout: hello\n"
    assert debug["stderr"] == "stderr: hello\n"


def test_python_provider_preserves_declared_multiple_outputs(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "workflow_providers._load_python_module",
        lambda _source: SimpleNamespace(run=lambda: {"session": {"handle": "abc"}, "controls": ["RESET"]}),
    )
    parameters = {
        "source": {"importMode": "module", "module": "fake", "callable": "run"},
        "_outputBindings": ["session", "controls"],
    }

    assert _python_callable({}, parameters) == {
        "session": {"handle": "abc"},
        "controls": ["RESET"],
    }


def test_file_python_provider_can_import_sibling_modules(tmp_path: Path) -> None:
    (tmp_path / "sibling_helper.py").write_text(
        "def answer():\n    return 42\n",
        encoding="utf-8",
    )
    entrypoint = tmp_path / "entrypoint.py"
    entrypoint.write_text(
        "from sibling_helper import answer\n\ndef run():\n    return answer()\n",
        encoding="utf-8",
    )

    module = _load_python_module({"importMode": "file", "file": str(entrypoint)})

    assert module.run() == 42


def test_file_python_provider_reuses_module_state(tmp_path: Path) -> None:
    entrypoint = tmp_path / "stateful.py"
    entrypoint.write_text(
        "counter = 0\n\ndef increment():\n    global counter\n    counter += 1\n    return counter\n",
        encoding="utf-8",
    )
    source = {"importMode": "file", "file": str(entrypoint)}

    first = _load_python_module(source)
    second = _load_python_module(source)

    assert first is second
    assert first.increment() == 1
    assert second.increment() == 2


@pytest.mark.skipif(shutil.which("swipl") is None, reason="SWI-Prolog is not installed")
def test_operation_playground_invokes_swi_prolog_variant() -> None:
    result = invoke_operation("shared_library_system", "echo_into_titlecased", {
        "implementationVariant": "echo_into_titlecased_prolog",
        "inputs": {"text": "the quick brown fox"},
    })
    assert result["outputs"]["text"] == "The Quick Brown Fox"
    assert result["outputs"]["execution"]["predicate"] == "titlecase_text"
    assert result["implementation"]["route"] == "prolog.source"
    assert result["elapsedMs"] >= 0
    trace = json.loads(read_operation_debug_log("shared_library_system", result["debugLogPath"])["content"])
    assert trace["providerExecution"]["completeSource"].startswith("titlecase_text")
    assert trace["providerExecution"]["returnCode"] == 0
    assert trace["providerExecution"]["stdout"] == "The Quick Brown Fox\n"
    assert trace["providerExecution"]["stderr"] == ""


def test_operation_materialization_resolves_requested_prompt_variant() -> None:
    executable = materialize_workflow_step(
        {"id": "playground", "workspaceId": "shared_library_system"},
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


def test_populate_workflow_from_english_resolves_its_bound_prompt_variant() -> None:
    executable = materialize_workflow_step(
        {"id": "generate", "workspaceId": "generate_count_to_ten"},
        {
            "id": "author",
            "operation": "workflow.populate_from_english",
            "implementationVariant": "workflow.populate_from_english.json",
            "inputs": {
                "english_specification": "Count to ten.",
                "effective_operation_catalog": [],
                "workflow_schema": {},
                "memory_values_plan": {},
                "existing_workflow": {},
                "validation_errors": [],
            },
        },
    )
    assert executable["resolvedPrompts"][0]["promptId"] == "workflow.generate_from_english"
    assert executable["resolvedPrompts"][0]["implementationId"] == "workflow.generate_from_english.json"
    assert "Workflow revision author" in executable["parameters"]["promptPrefix"]
    assert "Do not compile or emit MeTTa source" in executable["parameters"]["promptPrefix"]
    assert "new_memory_values_plan is required" in executable["parameters"]["promptPrefix"]
    assert "existing_workflow is always the previous Workflow" in executable["parameters"]["promptPrefix"]
    assert executable["parameters"]["parseJson"] is True
    assert executable["parameters"].get("wrapJsonOutput") is not True
    assert executable["modelSelection"] == {
        "models": ["https.llm.c.singularitynet.io.v1-asi1"],
        "strategy": "workspace_override",
    }


def test_playground_model_selection_overrides_implementation_for_one_run() -> None:
    executable = materialize_workflow_step(
        {"id": "playground", "workspaceId": "shared_library_system"},
        {
            "id": "operation_playground",
            "operation": "echo_into_titlecased",
            "implementationVariant": "echo_into_titlecased_llm",
            "inputs": {"text": "hello"},
            "modelSelection": {"models": ["asicloud-asi1-mini"], "strategy": "single"},
        },
    )
    assert executable["modelSelection"] == {"models": ["asicloud-asi1-mini"], "strategy": "single"}
    assert executable["parameters"]["model"] == "asi1-mini"


def test_prompt_profiles_are_first_class_composition_resources() -> None:
    root = DEFAULT_WORKSPACES_ROOT / "shared_library_system"
    hierarchy = prompt_hierarchy(root)
    profiles = {record["document"]["id"]: record["document"] for record in hierarchy["promptProfiles"]}
    assert set(profiles) >= {"object_first", "scene_graph"}
    assert profiles["object_first"]["kind"] == "prompt_profile"
    assert profiles["object_first"]["prompts"][0] == "object_extraction"

    resolved = resolve_prompt_profile(root, "scene_graph")
    assert resolved["prompts"] == [
        "symbolic_scene_fact_schema",
        "logical_image_coordinates",
        "structured_json_response",
        "output_quality_control",
    ]
    prefix, resolved_prompts, resolved_profiles = _prompt_composition_prefix(
        root, ["scene_graph"], [], "\n\n"
    )
    assert "JSON" in prefix
    assert [item["promptId"] for item in resolved_prompts] == resolved["prompts"]
    assert resolved_profiles == [{
        "profileId": "scene_graph",
        "promptIds": resolved["prompts"],
        "separator": "\n\n",
    }]


def test_direct_llm_operation_materializes_bound_prompt_profile() -> None:
    executable = materialize_workflow_step(
        {"id": "vision", "workspaceId": "shared_library_system"},
        {
            "id": "analyze",
            "operation": "vision.object_analysis",
            "inputs": {"image": "data:image/png;base64,AAAA"},
        },
    )
    assert executable["implementation"] == "llm.complete"
    assert executable["parameters"]["promptProfileIds"] == ["vision_object_analysis"]
    assert executable["resolvedPromptProfiles"][0]["profileId"] == "vision_object_analysis"
    assert [item["promptId"] for item in executable["resolvedPrompts"]] == [
        "structured_json_response",
        "logical_image_coordinates",
        "object_extraction",
        "symbolic_scene_fact_schema",
        "turtle_reconstruction",
        "turtle_motion_dsl",
        "output_quality_control",
    ]
    assert "coordinates of the source image" in executable["parameters"]["promptPrefix"].lower()


def test_abstract_only_operation_uses_contract_derived_openrouter_fallback() -> None:
    resolved = resolve_operation_implementation(
        DEFAULT_WORKSPACES_ROOT / "shared_library_system", "text_to_scene_graph"
    )
    implementation = resolved["implementation"]
    assert resolved["fallback"] is True
    assert implementation["id"] == "text_to_scene_graph.automatic_llm_fallback"
    assert implementation["virtual"] is True
    assert implementation["modelSelection"] == {
        "models": ["openrouter/free"],
        "strategy": "single",
    }

    executable = materialize_workflow_step(
        {"id": "playground", "workspaceId": "shared_library_system"},
        {
            "id": "invoke",
            "operation": "text_to_scene_graph",
            "inputs": {"image": "A blue ball above a red box."},
        },
    )

    assert executable["implementation"] == "llm.complete"
    assert executable["inputs"] == {"image": "A blue ball above a red box."}
    assert executable["parameters"]["backendId"] == "openrouter"
    assert executable["parameters"]["model"] == "openrouter/free"
    prompt = executable["parameters"]["promptPrefix"]
    assert "automatic LLM fallback" in prompt
    assert "Do the best you can" in prompt
    assert 'Execute the operation "Text to Scene Graph"' in prompt
    assert "natural-language description" in prompt
    assert '"representation": "scene_graph"' in prompt
    assert "complete operation resource follows in MeTTa" in prompt
    assert "example/default value" in prompt
    assert "(id text_to_scene_graph)" in prompt
    assert "(representation scene_graph)" in prompt


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

    result = invoke_operation("shared_library_system", "echo_into_titlecased", {
        "implementationVariant": "echo_into_titlecased_llm",
        "inputs": {"text": "hello world"},
    })

    assert sent["url"] == "https://openrouter.ai/api/v1/chat/completions"
    assert sent["authorization"] == "Bearer openrouter-test-key"
    assert sent["body"]["model"] == "openrouter/free"  # type: ignore[index]
    assert result["outputs"]["text"] == "Hello World"
    trace_text = read_operation_debug_log("shared_library_system", result["debugLogPath"])["content"]
    trace = json.loads(trace_text)
    assert "openrouter-test-key" not in trace_text
    assert trace["providerExecution"]["request"]["headers"]["Authorization"] == "[REDACTED]"
    assert trace["providerExecution"]["request"]["body"] == sent["body"]
    assert trace["providerExecution"]["response"]["bodyJson"]["choices"][0]["message"]["content"] == "Hello World"


def test_automatic_fallback_marks_live_inputs_authoritative(monkeypatch: pytest.MonkeyPatch) -> None:
    sent: dict[str, object] = {}

    class Response:
        def __enter__(self): return self
        def __exit__(self, *_args: object) -> None: return None
        def read(self) -> bytes:
            return json.dumps({"choices": [{"message": {"content": '{"text":"Codex Zebra Marker 92841"}'}}]}).encode()

    def urlopen(request: object, **_kwargs: object) -> Response:
        sent["body"] = json.loads(getattr(request, "data").decode())
        return Response()

    monkeypatch.setenv("OPENROUTER_API_KEY", "openrouter-test-key")
    monkeypatch.setattr("workflow_providers.urllib.request.urlopen", urlopen)
    result = invoke_operation("shared_library_system", "echo_into_titlecased", {
        "implementationVariant": "echo_into_titlecased.automatic_llm_fallback",
        "inputs": {"text": "codex zebra marker 92841"},
    })

    content = sent["body"]["messages"][0]["content"]  # type: ignore[index]
    assert "AUTHORITATIVE RUNTIME INPUTS" in content
    assert content.endswith('{"text": "codex zebra marker 92841"}')
    assert content.rfind("codex zebra marker 92841") > content.rfind("the quick brown fox")
    assert result["outputs"] == {"text": "Codex Zebra Marker 92841"}


def test_llm_complete_sends_multi_input_authoring_envelope_and_wraps_workflow(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sent: dict[str, object] = {}

    class Response:
        def __enter__(self): return self
        def __exit__(self, *_args: object) -> None: return None
        def read(self) -> bytes:
            return json.dumps({
                "choices": [{"message": {"content": '{"kind":"workflow","id":"count","steps":[]}'}}],
            }).encode()

    def urlopen(request: object, **_kwargs: object) -> Response:
        sent["body"] = json.loads(getattr(request, "data").decode())
        return Response()

    monkeypatch.setenv("OPENAI_API_KEY", "openai-test-key")
    monkeypatch.setattr("workflow_providers.urllib.request.urlopen", urlopen)
    result = _llm_complete(
        {
            "english_specification": "Count from one through ten.",
            "workflow_schema": {"kind": "workflow", "required": ["id", "steps"]},
        },
        {
            "promptPrefix": "Return one Workflow JSON object.",
            "parseJson": True,
            "responseFormat": "json_object",
            "wrapJsonOutput": True,
            "outputBinding": "workflow",
        },
    )

    content = sent["body"]["messages"][0]["content"]  # type: ignore[index]
    assert "AUTHORITATIVE RUNTIME INPUTS" in content
    assert '"english_specification": "Count from one through ten."' in content
    assert '"workflow_schema": {"kind": "workflow"' in content
    assert result == {"workflow": {"kind": "workflow", "id": "count", "steps": []}}


def test_constant_value_uses_workbench_provider() -> None:
    result = invoke_operation("shared_library_system", "shared.constant", {
        "implementationVariant": "shared.constant.workbench",
        "inputs": {},
        "parameters": {"value": 42},
    })
    assert result["implementation"]["route"] == "system.workbench"
    assert result["outputs"] == {"value": 42}


def test_direct_root_implementation_runs_without_an_llm_fallback() -> None:
    resolved = resolve_operation_implementation(DEFAULT_WORKSPACES_ROOT / "shared_library_system", "shared.echo")
    assert resolved["direct"] is True
    assert resolved["implementation"]["id"] == "shared.echo"
    assert resolved["implementation"]["implementation"] == "core.echo"

    executable = materialize_workflow_step(
        {"id": "playground", "workspaceId": "shared_library_system"},
        {"id": "invoke", "operation": "shared.echo", "inputs": {"value": "Suff"}},
    )
    assert executable["implementation"] == "core.echo"
    assert executable["implementationVariant"] == "shared.echo"

    result = invoke_operation("shared_library_system", "shared.echo", {
        "implementationVariant": "shared.echo",
        "inputs": {"value": "Suff"},
    })
    assert result["implementation"]["route"] == "core.echo"
    assert result["outputs"] == {"value": "Suff"}


def test_automatic_llm_fallback_can_override_an_available_implementation() -> None:
    direct = resolve_operation_implementation(
        DEFAULT_WORKSPACES_ROOT / "shared_library_system",
        "shared.echo",
        "shared.echo.automatic_llm_fallback",
    )
    assert direct["fallback"] is True
    assert direct["implementation"]["implementation"] == "llm.complete"

    with_children = resolve_operation_implementation(
        DEFAULT_WORKSPACES_ROOT / "shared_library_system",
        "echo_into_titlecased",
        "echo_into_titlecased.automatic_llm_fallback",
    )
    assert with_children["fallback"] is True
    assert with_children["implementation"]["modelSelection"] == {
        "models": ["openrouter/free"],
        "strategy": "single",
    }


def test_user_request_materializes_as_human_input() -> None:
    executable = materialize_workflow_step(
        {"id": "sample", "workspaceId": "shared_library_system"},
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

    preview = invoke_operation("shared_library_system", "sample.request_number", {"inputs": {}})
    assert preview["outputs"]["status"] == "waiting_for_input"
    assert preview["outputs"]["form"]["value"]["type"] == "Number"
    assert preview["outputs"]["form"]["value"]["prompt"] == "How many objects are visible?"


def test_implementation_parent_link_is_sufficient_for_resolution(tmp_path: Path) -> None:
    directory = tmp_path / "shared_library_system" / "design" / "operations"
    directory.mkdir(parents=True)
    (directory / "echo.operation.json").write_text(json.dumps({
        "kind": "operation", "id": "shared.echo", "inputs": {"value": "Any"}, "outputs": {"value": "Any"},
    }), encoding="utf-8")
    implementations = tmp_path / "shared_library_system" / "design" / "operation_implementations"
    implementations.mkdir(parents=True)
    (implementations / "echo_prolog.operation_implementation.json").write_text(json.dumps({
        "kind": "operation_implementation",
        "id": "shared.echo.prolog",
        "parents": ["shared.echo"],
        "implementation": "prolog.source",
    }), encoding="utf-8")

    resolved = resolve_operation_implementation(
        tmp_path / "shared_library_system", "shared.echo", "shared.echo.prolog", workspaces_root=tmp_path,
    )

    assert resolved["implementation"]["id"] == "shared.echo.prolog"


def test_operation_playground_preserves_provider_rate_limit(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")

    def rate_limited(*_args: object, **_kwargs: object) -> object:
        raise HTTPError("https://provider.invalid", 429, "Too Many Requests", {}, None)

    monkeypatch.setattr("workflow_providers.urllib.request.urlopen", rate_limited)
    with pytest.raises(HTTPException) as caught:
        invoke_operation("shared_library_system", "echo_into_titlecased", {
            "implementationVariant": "echo_into_titlecased_llm",
            "inputs": {"text": "hello"},
        })

    assert caught.value.status_code == 429
    assert "provider request failed with HTTP 429" in str(caught.value.detail)
    assert isinstance(caught.value.detail, dict)
    trace = json.loads(read_operation_debug_log("shared_library_system", caught.value.detail["debugLogPath"])["content"])
    assert trace["status"] == "failed"
    assert trace["providerExecution"]["response"]["status"] == 429
    assert trace["error"]["type"] == "HTTPError"


def test_automatic_vision_variant_sends_bitmap_inputs_and_parses_json(monkeypatch: pytest.MonkeyPatch) -> None:
    resolved = resolve_operation_implementation(DEFAULT_WORKSPACES_ROOT / "shared_library_system", "vision.extract_scene_objects")
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


def test_llm_response_parser_supports_responses_api_output() -> None:
    assert _llm_response_text({
        "output": [{"content": [{"type": "output_text", "text": "done"}]}]
    }) == "done"


def test_llm_response_parser_surfaces_embedded_provider_error() -> None:
    with pytest.raises(RuntimeError, match="free vision capacity is temporarily unavailable"):
        _llm_response_text({
            "error": {
                "code": 429,
                "message": "free vision capacity is temporarily unavailable",
            }
        })


def test_llm_response_parser_reports_unexpected_keys() -> None:
    with pytest.raises(RuntimeError, match=r"unsupported response shape \(keys: id, model\)"):
        _llm_response_text({"id": "response-id", "model": "unexpected"})


def test_declared_subject_matter_route_falls_back_when_no_handler_registered() -> None:
    root = DEFAULT_WORKSPACES_ROOT / "shared_library_system"
    # Without a route predicate the declared abstract label is returned verbatim
    # (preserves legacy resolution for callers that do not know the registry).
    direct = resolve_operation_implementation(root, "shared.extract_entities")
    assert direct.get("direct") is True
    assert direct["implementation"]["implementation"] == "vision.segment"
    # With the engine's route predicate, a declared-but-unregistered subject-matter
    # label degrades to the automatic LLM fallback instead of an unknown-operation error.
    resolved = resolve_operation_implementation(
        root,
        "shared.extract_entities",
        is_known_route={"core.echo", "llm.complete"}.__contains__,
    )
    assert resolved["fallback"] is True
    assert resolved["implementation"]["implementation"] == "llm.complete"
    assert resolved["implementation"]["id"] == "shared.extract_entities.automatic_llm_fallback"


def test_known_direct_route_is_preserved_when_predicate_supplied() -> None:
    resolved = resolve_operation_implementation(
        DEFAULT_WORKSPACES_ROOT / "shared_library_system",
        "shared.echo",
        is_known_route={"core.echo"}.__contains__,
    )
    assert resolved["direct"] is True
    assert resolved["implementation"]["implementation"] == "core.echo"


def test_materialize_step_uses_llm_fallback_for_unregistered_route() -> None:
    executable = materialize_workflow_step(
        {"id": "seg", "workspaceId": "shared_library_system"},
        {"id": "s1", "operation": "shared.extract_entities", "inputs": {"observation": "obs"}},
        is_known_route={"llm.complete"}.__contains__,
    )
    assert executable["implementation"] == "llm.complete"
    assert executable["implementationVariant"] == "shared.extract_entities.automatic_llm_fallback"
    assert executable["parameters"].get("automaticFallback") is True


def test_engine_registry_reports_known_and_unknown_routes() -> None:
    from workflow_engine_api import engine

    assert engine.registry.has("llm.complete") is True
    assert engine.registry.has("core.echo") is True
    assert engine.registry.has("vision.segment") is False


def test_invoke_operation_runs_declared_only_operation_via_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    sent: dict[str, object] = {}

    class Response:
        def __enter__(self): return self
        def __exit__(self, *_args: object) -> None: return None
        def read(self) -> bytes:
            return json.dumps({"choices": [{"message": {"content": '{"entities": []}'}}]}).encode()

    def urlopen(request: object, **_kwargs: object) -> Response:
        sent.update(json.loads(getattr(request, "data").decode()))
        return Response()

    monkeypatch.setenv("OPENROUTER_API_KEY", "openrouter-test-key")
    monkeypatch.setattr("workflow_providers.urllib.request.urlopen", urlopen)
    result = invoke_operation("shared_library_system", "shared.extract_entities", {
        "inputs": {"observation": "a grid of colored cells"},
    })
    assert result["implementation"]["route"] == "llm.complete"
    assert result["implementation"]["id"] == "shared.extract_entities.automatic_llm_fallback"
    assert result["outputs"] == {"entities": []}
