from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "workbench" / "server"
sys.path.insert(0, str(SERVER))

import policy_api  # noqa: E402
from model_discovery import discover_backend_models, import_discovered_models, reconcile_discovered_models, remove_missing_models  # noqa: E402
from model_policy_ping import run_ping_job  # noqa: E402
from model_benchmark import run_benchmark  # noqa: E402
from policy_library import effective_model_registry, load_workspace_policy_records  # noqa: E402
from resource_store import get_filesystem_provider  # noqa: E402


def _records(*documents: dict) -> list[dict]:
    return [{"document": document, "path": f"policies/{document['id']}.json"} for document in documents]


def test_effective_eligibility_keeps_policy_separate_from_health() -> None:
    records = _records(
        {"kind": "model_policy", "id": "default", "enabled": True, "rules": {"slowLatencyMs": 1000, "excludeSlowFromRuntime": True}},
        {"kind": "vendor_policy", "id": "vendor", "vendorId": "v", "enabled": True, "policy": {"wanted": "on", "runtime": "on", "benchmark": "on"}},
        {"kind": "model_policy_entry", "id": "v:m", "vendorId": "v", "enabled": True, "policy": {"wanted": "auto", "runtime": "on", "benchmark": "on"}},
        {"kind": "model_health_observation", "id": "health", "modelPolicyEntryId": "v:m", "observedAt": "2026-01-01T00:00:00Z", "status": "slow", "latencyMs": 1500},
    )
    model = effective_model_registry(records)["models"][0]
    assert model["policy"]["wanted"] == "auto"
    assert model["effective"]["runtime"] is False
    assert model["effective"]["runtimeState"] == "temporarily_disabled"
    assert "latency threshold exceeded" in model["effective"]["reasons"]


def test_off_policy_is_disabled_even_when_healthy() -> None:
    records = _records(
        {"kind": "model_policy", "id": "default", "enabled": True},
        {"kind": "model_policy_entry", "id": "v:m", "vendorId": "v", "policy": {"wanted": "off", "runtime": "on", "benchmark": "on"}},
        {"kind": "model_health_observation", "id": "health", "modelPolicyEntryId": "v:m", "observedAt": "2026-01-01T00:00:00Z", "status": "online"},
    )
    effective = effective_model_registry(records)["models"][0]["effective"]
    assert effective["runtimeState"] == "disabled"
    assert effective["benchmarkState"] == "disabled"


def test_catalog_backends_models_and_profiles_load_until_policy_disables_them() -> None:
    backends = [{"kind": "backend", "id": "vendor", "label": "Vendor", "enabled": True}]
    catalog = [
        {"document": {"kind": "model", "id": "model", "label": "Model", "capabilities": ["text"], "pricing": {"prompt": "0.1"}, "properties": {"multimodal": True}},
         "resolved": {"backendId": "vendor", "model": "remote-model", "enabled": True, "defaults": {}, "inheritance": ["vendor", "model"]}},
        {"document": {"kind": "profile", "id": "model-fast", "label": "Fast", "inherits": "model"},
         "resolved": {"backendId": "vendor", "model": "remote-model", "enabled": True, "defaults": {}, "inheritance": ["vendor", "model", "model-fast"]}},
    ]
    registry = effective_model_registry([], backends, catalog)
    assert [vendor["vendorId"] for vendor in registry["vendors"]] == ["vendor"]
    assert {model["modelResourceId"] for model in registry["models"]} == {"model", "model-fast"}
    assert all(model["policy"]["wanted"] == "on" for model in registry["models"])
    assert registry["models"][1]["capabilities"]["text"] is True
    model_row = next(item for item in registry["models"] if item["modelResourceId"] == "model")
    assert model_row["pricing"]["prompt"] == "0.1"
    assert model_row["properties"]["multimodal"] is True

    override = _records({"kind": "model_policy_entry", "id": "vendor:model", "vendorId": "vendor", "modelResourceId": "model", "policy": {"wanted": "off"}})
    overridden = effective_model_registry(override, backends, catalog)
    model = next(item for item in overridden["models"] if item["modelResourceId"] == "model")
    assert model["policy"]["wanted"] == "off"
    assert model["effective"]["runtimeState"] == "disabled"


def test_explicit_model_override_can_reenable_vendor_child() -> None:
    records = _records(
        {"kind": "vendor_policy", "id": "vendor_policy", "vendorId": "vendor", "policy": {"wanted": "off"}},
        {"kind": "model_policy_entry", "id": "vendor:model", "vendorId": "vendor", "policy": {"wanted": "on", "runtime": "on"}},
        {"kind": "model_health_observation", "id": "health", "modelPolicyEntryId": "vendor:model", "observedAt": "2026-01-01T00:00:00Z", "status": "online"},
    )
    model = effective_model_registry(records)["models"][0]
    assert model["effective"]["runtimeState"] == "enabled"


def test_vendor_change_cascades_to_children_in_policy_editor() -> None:
    source = (ROOT / "workbench" / "frontend" / "src" / "components" / "ModelPolicyPage.tsx").read_text(encoding="utf-8")
    assert "filter(model=>model.vendorId===vendor.vendorId)" in source
    assert "next[model.id]" in source


def test_model_discovery_has_bulk_selection_controls() -> None:
    source = (ROOT / "workbench" / "frontend" / "src" / "components" / "LlmModelsEditor.tsx").read_text(encoding="utf-8")
    assert "Select new/changed" in source
    assert "Select missing" in source
    assert "Clear selection" in source
    assert "discoverySelection.size} selected" in source
    assert 'body:JSON.stringify({models,overwrite:true})' in source
    assert "setSnapshot(null);setOpenDocs([]);setActiveKey(null);setCompareKey(null)" in source
    assert 'cache:"no-store"' in source
    assert "Remove missing" in source


def test_backend_model_discovery_supports_openai_and_ollama_shapes(tmp_path: Path) -> None:
    class Response:
        def __enter__(self): return self
        def __exit__(self, *_args): return None
        def read(self): return json.dumps({"models": [{"name": "local/a"}, {"model": "local/b"}]}).encode()
    backend = {"id": "local", "configuration": {"baseUrl": "http://localhost:11434/v1"}}
    discovered = discover_backend_models(backend, opener=lambda *_args, **_kwargs: Response())
    assert [row["id"] for row in discovered] == ["local/a", "local/b"]
    imported = import_discovered_models(tmp_path, backend, discovered[:1])
    assert imported[0]["inherits"] == "local"
    assert imported[0]["model"] == "local/a"
    assert set(imported[0]["capabilities"]) >= {"multimodal", "vision", "audio", "tools", "reasoning"}
    assert imported[0]["providerMetadata"]["name"] == "local/a"
    assert imported[0]["properties"]["name"] == "local/a"
    assert (tmp_path / "design" / "models" / "local-local_a.model.metta").is_file()


def test_model_import_route_always_targets_shared_workspace(tmp_path: Path, monkeypatch) -> None:
    project = tmp_path / "project"; shared = tmp_path / "shared"
    (shared / "models").mkdir(parents=True); project.mkdir()
    (shared / "models" / "vendor.backend.json").write_text(json.dumps({"kind": "backend", "id": "vendor", "provider": "openai", "configuration": {"baseUrl": "https://example.invalid/v1"}}))
    monkeypatch.setattr(policy_api, "_resolve_workspace", lambda workspace_id: {"id": workspace_id, "root": str(shared if workspace_id == "shared" else project)})
    monkeypatch.setattr(policy_api, "load_workspace_backend_records", lambda _root: [{"document": {"kind": "backend", "id": "vendor", "provider": "openai"}}])
    result = policy_api.import_models("project", "vendor", {"models": [{"id": "remote/model", "label": "Remote"}]})
    assert result["targetWorkspace"]["id"] == "shared"
    assert not (project / "models").exists()
    assert (shared / "design" / "models" / "vendor-remote_model.model.metta").is_file()


def test_model_example_invokes_resolved_model(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(policy_api, "_resolve_workspace", lambda workspace_id: {"id": workspace_id, "root": str(tmp_path)})
    monkeypatch.setattr(policy_api, "resolve_model_records", lambda _root: [{"document": {"id": "model"}, "resolved": {"enabled": True, "model": "remote", "configuration": {}, "defaults": {}}}])
    monkeypatch.setattr(policy_api, "call_model", lambda model, profile, prompt, timeout: {"text": prompt.upper(), "latencyMs": 1})
    result = policy_api.invoke_model_example("shared", "model", {"arguments": {"prompt": "hello"}})
    assert result["text"] == "HELLO"


def test_example_executor_is_shared_by_models_and_prompts() -> None:
    panel = (ROOT / "workbench" / "frontend" / "src" / "components" / "ExampleExecutePanel.tsx").read_text(encoding="utf-8")
    models = (ROOT / "workbench" / "frontend" / "src" / "components" / "LlmModelsEditor.tsx").read_text(encoding="utf-8")
    prompts = (ROOT / "workbench" / "frontend" / "src" / "components" / "PromptLibraryEditor.tsx").read_text(encoding="utf-8")
    assert "EXAMPLE EXECUTE" in panel and "Run example" in panel
    assert "exampleFor(document)" in models and "executeModelExample" in models
    assert "contractParent?.example_execute" in prompts and "renderPromptExample" in prompts


def test_discovery_reconciles_and_only_removes_managed_missing_models(tmp_path: Path) -> None:
    backend = {"id": "vendor", "label": "Vendor"}
    imported = import_discovered_models(tmp_path, backend, [{"id": "old", "label": "Old"}, {"id": "keep", "label": "Keep"}])
    manual = tmp_path / "design" / "models" / "manual.model.json"
    manual.write_text(json.dumps({"kind": "model", "id": "manual", "inherits": "vendor", "model": "manual"}))
    rows = reconcile_discovered_models(tmp_path, backend, [{"id": "keep", "label": "Keep"}, {"id": "new", "label": "New"}])
    assert {row["id"]: row["status"] for row in rows} == {"keep": "unchanged", "new": "new", "old": "missing"}
    assert remove_missing_models(tmp_path, backend, [imported[0]["id"], "manual"]) == [imported[0]["id"]]
    assert manual.is_file()


def test_observation_api_persists_a_real_resource(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(policy_api, "_resolve_workspace", lambda workspace_id: {"id": workspace_id, "root": str(tmp_path)})
    document = {"kind": "model_ping_event", "id": "ping:one", "jobId": "job", "status": "succeeded"}
    result = policy_api.record_model_policy_observation("demo", document)
    assert result["path"] == "policies/ping_one.model_ping_event.json"
    assert get_filesystem_provider().read_json(tmp_path / result["path"]) == document
    loaded = load_workspace_policy_records(tmp_path, workspaces_root=tmp_path.parent)
    assert loaded[0]["document"]["id"] == "ping:one"


def test_active_app_registers_model_policy_backend_router() -> None:
    source = (SERVER / "app.py").read_text(encoding="utf-8")
    assert "from policy_api import router as policy_router" in source
    assert "app.include_router(policy_router, prefix=\"/api\")" in source


def test_ping_job_persists_independent_health_and_events(tmp_path: Path) -> None:
    models = [
        {"id": "vendor:fast", "vendorId": "vendor"},
        {"id": "vendor:broken", "vendorId": "vendor"},
    ]
    def probe(model: dict, _backend: dict | None, _timeout: int) -> dict:
        if model["id"].endswith("broken"):
            raise RuntimeError("probe failed")
        return {"status": "online", "latencyMs": 12}
    result = run_ping_job(
        tmp_path,
        {"id": "job", "targets": [item["id"] for item in models], "concurrency": 2, "timeoutMs": 1000},
        models,
        [{"id": "vendor", "configuration": {"baseUrl": "http://example.test"}}],
        probe=probe,
    )
    assert result["job"]["status"] == "completed_with_errors"
    assert result["job"]["failureCount"] == 1
    assert {item["health"]["status"] for item in result["results"]} == {"online", "error"}
    persisted = list((tmp_path / "policies").glob("*.metta"))
    assert len(persisted) == 5  # one job, two events, and two health observations


def test_model_policy_ui_calls_real_ping_executor() -> None:
    source = (ROOT / "workbench" / "frontend" / "src" / "components" / "ModelPolicyPage.tsx").read_text(encoding="utf-8")
    assert "/model-policy/ping" in source
    for label in ("Ping All", "Ping Wanted", "Ping Auto", "Ping Unwanted"):
        assert label in source


def test_model_policy_ui_edits_and_filters_dynamic_registry() -> None:
    source = (ROOT / "workbench" / "frontend" / "src" / "components" / "ModelPolicyPage.tsx").read_text(encoding="utf-8")
    styles = (ROOT / "workbench" / "frontend" / "src" / "styles" / "model_policy_todo.css").read_text(encoding="utf-8")
    for token in ("Filesystem Load", "Filesystem Save", "Ping Selected", "Select Visible", "Clear Selection", "All capabilities", "All runtime", "All benchmark", "dynamicColumns", "toggleSort"):
        assert token in source
    assert 'scope==="selected"?[...selected]' in source
    assert "registryDocument" in source
    assert ".policy-table-scroll th:nth-child(-n+7)" in styles
    assert ".matrix-row{display:grid;grid-auto-flow:column;grid-auto-columns:145px" in styles
    assert ".matrix-row>b{position:sticky;left:0" in styles
    assert "const flattenFields=" in source
    assert "dynamicEntries(model).map(([key])=>key)" in source
    assert "displayValue(dynamicValue(model,key))" in source
    assert 'heading("Effective Runtime","effective.runtime")' in source
    assert 'heading("Effective Benchmark","effective.benchmark")' in source
    assert 'aria-label={`Sort by ${label}`}' in source
    assert ".policy-sort{display:flex;width:100%" in styles


def test_benchmark_job_executes_declared_cases_and_persists_measurements(tmp_path: Path) -> None:
    policy = {"id":"quality","cases":[{"id":"token","prompt":"say OK","expected":"OK","evaluator":"exact_match"}],"repetitions":2,"concurrency":2}
    models = [{"id":"vendor:model","vendorId":"vendor"}]
    profiles = [{"document":{"id":"profile"},"resolved":{"enabled":True}}]
    def invoke(_model:dict,_profile:dict,_prompt:str,_timeout:int)->dict:
        return {"text":"OK","latencyMs":10,"inputTokens":2,"outputTokens":1}
    result = run_benchmark(tmp_path,policy,models,profiles,invoke=invoke)
    assert result["job"]["status"] == "completed"
    assert result["results"][0]["metrics"] == {"accuracy":1.0,"latency_ms":10.0,"input_tokens":4,"output_tokens":2,"success_rate":1.0}
    assert list((tmp_path/"policies").glob("*.benchmark_job.metta"))
    assert list((tmp_path/"policies").glob("*.benchmark_result.metta"))


def test_model_policy_ui_exposes_explicit_benchmark_run() -> None:
    source = (ROOT / "workbench" / "frontend" / "src" / "components" / "ModelPolicyPage.tsx").read_text(encoding="utf-8")
    assert "/model-policy/benchmarks/" in source
    assert "Run Benchmark" in source
