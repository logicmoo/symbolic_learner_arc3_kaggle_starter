from pathlib import Path
import sys
import json


ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "workbench" / "server"
sys.path.insert(0, str(SERVER))

from model_policy_todo_api import get_model_policy_mockup, get_model_policy_todo  # noqa: E402
from resource_store import get_filesystem_provider  # noqa: E402


def test_model_policy_todo_is_read_from_checked_in_files() -> None:
    payload = get_model_policy_todo()
    assert payload["status"] == "pending"
    assert payload["mockupAvailable"] is True
    assert "Model Runtime Usage" in str(payload["markdown"])
    assert str(payload["specificationPath"]).endswith("MODEL_RUNTIME_USAGE_AND_BENCHMARKING_POLICIES.md")


def test_model_policy_mockup_endpoint_returns_checked_in_png() -> None:
    response = get_model_policy_mockup()
    assert response.media_type == "image/png"
    assert Path(response.path).is_file()


def test_active_model_policy_page_uses_live_filesystem_policy_api() -> None:
    page = (ROOT / "workbench" / "frontend" / "src" / "components" / "ModelPolicyPage.tsx").read_text(encoding="utf-8")
    shell = (ROOT / "workbench" / "frontend" / "src" / "pages" / "FilesystemWorkbenchPage.tsx").read_text(encoding="utf-8")
    assert "/model-policy`" in page
    assert "/model-policy/ping`" in page
    for token in ("All Models", "Benchmark Matrix", "Performance History", "Filter any resource property"):
        assert token in page
    assert 'view==="modelPolicy"&&<ModelPolicyPage workspaceId={workspace.id}' in shell


def test_shared_policy_examples_form_a_resolvable_reference_graph() -> None:
    shared = ROOT / "workbench" / "workspaces" / "shared"
    paths = [
        shared / "policies" / "default_model_runtime.model_policy.json",
        shared / "policies" / "balanced_model_runtime.model_policy_variant.json",
        shared / "policies" / "economy_model_runtime.model_policy_variant.json",
        shared / "policies" / "openai.vendor_policy.json",
        shared / "policies" / "openai_gpt_5_6.model_policy_entry.json",
        shared / "policies" / "openai_gpt_5_6.model_health_observation.json",
        shared / "policies" / "example_vendor_ping.model_ping_job.json",
        shared / "policies" / "example_openai_gpt_5_6.model_ping_event.json",
        shared / "policies" / "reasoning_quality.benchmark_policy.json",
        shared / "policies" / "example_reasoning_quality.benchmark_result.json",
    ]
    documents = [get_filesystem_provider().read_json(path) for path in paths]
    by_id = {document["id"]: document for document in documents}
    assert all(document.get("example") is True for document in documents)
    assert {document["kind"] for document in documents} == {
        "model_policy", "model_policy_variant", "vendor_policy", "model_policy_entry",
        "model_health_observation", "model_ping_job", "model_ping_event",
        "benchmark_policy", "benchmark_result",
    }
    assert by_id["default_model_runtime"]["preferredChild"] in by_id
    assert by_id["balanced_model_runtime"]["parents"] == ["default_model_runtime"]
    assert by_id["economy_model_runtime"]["enabled"] is False
    assert by_id["openai:gpt-5.6"]["vendorId"] == "openai"
    assert by_id["example_openai_gpt_5_6_ping"]["jobId"] == "example_vendor_ping"
    assert by_id["example_reasoning_quality_gpt_5_6"]["benchmarkPolicyId"] == "reasoning_quality"
