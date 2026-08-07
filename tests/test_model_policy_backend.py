from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "workbench" / "server"
sys.path.insert(0, str(SERVER))

import policy_api  # noqa: E402
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
