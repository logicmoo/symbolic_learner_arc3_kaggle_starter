from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "workbench" / "server"
sys.path.insert(0, str(SERVER))

import policy_api  # noqa: E402
from model_policy_ping import run_ping_job  # noqa: E402
from model_benchmark import run_benchmark  # noqa: E402
from policy_library import effective_model_registry, load_workspace_policy_records  # noqa: E402


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


def test_observation_api_persists_a_real_resource(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(policy_api, "_resolve_workspace", lambda workspace_id: {"id": workspace_id, "root": str(tmp_path)})
    document = {"kind": "model_ping_event", "id": "ping:one", "jobId": "job", "status": "succeeded"}
    result = policy_api.record_model_policy_observation("demo", document)
    assert result["path"] == "policies/ping_one.model_ping_event.json"
    assert json.loads((tmp_path / result["path"]).read_text(encoding="utf-8")) == document
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
    persisted = list((tmp_path / "policies").glob("*.json"))
    assert len(persisted) == 5  # one job, two events, and two health observations


def test_model_policy_ui_calls_real_ping_executor() -> None:
    source = (ROOT / "workbench" / "frontend" / "src" / "components" / "ModelPolicyPage.tsx").read_text(encoding="utf-8")
    assert "/model-policy/ping" in source
    for label in ("Ping All", "Ping Wanted", "Ping Auto", "Ping Unwanted"):
        assert label in source


def test_model_policy_ui_edits_and_filters_dynamic_registry() -> None:
    source = (ROOT / "workbench" / "frontend" / "src" / "components" / "ModelPolicyPage.tsx").read_text(encoding="utf-8")
    styles = (ROOT / "workbench" / "frontend" / "src" / "styles" / "model_policy_todo.css").read_text(encoding="utf-8")
    for token in ("Filesystem Load", "Filesystem Save", "Ping Selected", "All capabilities", "All runtime", "All benchmark", "dynamicColumns", "toggleSort"):
        assert token in source
    assert 'scope==="selected"?[...selected]' in source
    assert ".policy-table-scroll th:nth-child(-n+7)" in styles


def test_benchmark_job_executes_declared_cases_and_persists_measurements(tmp_path: Path) -> None:
    policy = {"id":"quality","cases":[{"id":"token","prompt":"say OK","expected":"OK","evaluator":"exact_match"}],"repetitions":2,"concurrency":2}
    models = [{"id":"vendor:model","vendorId":"vendor"}]
    profiles = [{"document":{"id":"profile"},"resolved":{"enabled":True}}]
    def invoke(_model:dict,_profile:dict,_prompt:str,_timeout:int)->dict:
        return {"text":"OK","latencyMs":10,"inputTokens":2,"outputTokens":1}
    result = run_benchmark(tmp_path,policy,models,profiles,invoke=invoke)
    assert result["job"]["status"] == "completed"
    assert result["results"][0]["metrics"] == {"accuracy":1.0,"latency_ms":10.0,"input_tokens":4,"output_tokens":2,"success_rate":1.0}
    assert list((tmp_path/"policies").glob("*.benchmark_job.json"))
    assert list((tmp_path/"policies").glob("*.benchmark_result.json"))


def test_model_policy_ui_exposes_explicit_benchmark_run() -> None:
    source = (ROOT / "workbench" / "frontend" / "src" / "components" / "ModelPolicyPage.tsx").read_text(encoding="utf-8")
    assert "/model-policy/benchmarks/" in source
    assert "Run Benchmark" in source
