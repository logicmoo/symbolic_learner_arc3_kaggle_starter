from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "workbench" / "server"
sys.path.insert(0, str(SERVER))

from backend_library import load_workspace_backend_records  # noqa: E402
from model_library import resolve_model_records  # noqa: E402
from model_discovery import discover_backend_models  # noqa: E402


def test_shared_asi_backends_load_with_expected_credentials_and_endpoints() -> None:
    shared = ROOT / "workbench" / "workspaces" / "shared_library_system"
    backends = {
        str((record.get("document") or {}).get("id")): record.get("document") or {}
        for record in load_workspace_backend_records(shared)
    }

    asicloud = backends["https.inference.asicloud.cudos.org.v1"]
    assert {"asicloud", "asi-cloud", "cudos", "https://inference.asicloud.cudos.org/v1"} <= set(asicloud["aliases"])
    assert asicloud["enabled"] is True
    assert asicloud["configuration"]["adapter"] == "openai_chat_completions"
    assert asicloud["configuration"]["baseUrl"] == "https://inference.asicloud.cudos.org/v1"
    assert asicloud["configuration"]["apiKeyEnvironmentVariable"] == "ASI_API_KEY"
    assert asicloud["configuration"]["defaultModel"] == "asi1-mini"
    assert "asicloud-asi1-mini" in asicloud["specializations"]

    models = {
        str((record.get("document") or {}).get("id")): record
        for record in resolve_model_records(shared)
    }
    asi1_mini = models["asicloud-asi1-mini"]
    assert asi1_mini["document"]["model"] == "asi1-mini"
    assert asi1_mini["resolved"]["model"] == "asi1-mini"
    assert asi1_mini["resolved"]["configuration"]["baseUrl"] == "https://inference.asicloud.cudos.org/v1"
    assert asi1_mini["resolved"]["configuration"]["apiKeyEnvironmentVariable"] == "ASI_API_KEY"

    asione = backends["https.api.asi1.ai.v1"]
    assert {"asione", "asi-one", "asi1", "https://api.asi1.ai/v1"} <= set(asione["aliases"])
    assert asione["enabled"] is True
    assert asione["configuration"]["adapter"] == "openai_chat_completions"
    assert asione["configuration"]["baseUrl"] == "https://api.asi1.ai/v1"
    assert asione["configuration"]["apiKeyEnvironmentVariable"] == "ASIONE_API_KEY"
    assert asione["configuration"]["defaultModel"] == "asi1-ultra"


def test_asi_and_singularitynet_model_list_requests_use_their_declared_keys(monkeypatch) -> None:
    shared = ROOT / "workbench" / "workspaces" / "shared_library_system"
    backends = {
        str((record.get("document") or {}).get("id")): record.get("document") or {}
        for record in load_workspace_backend_records(shared)
    }
    expected = {
        "https.api.asi1.ai.v1": ("ASIONE_API_KEY", "asione-secret"),
        "https.inference.asicloud.cudos.org.v1": ("ASI_API_KEY", "asicloud-secret"),
        "https.llm.c.singularitynet.io.v1": ("SNET_API_KEY", "snet-secret"),
    }

    class Response:
        def __enter__(self): return self
        def __exit__(self, *_args): return None
        def read(self): return b'{"data": []}'

    for backend_id, (environment_name, secret) in expected.items():
        monkeypatch.setenv(environment_name, secret)
        captured: list[object] = []

        def opener(request, **_kwargs):
            captured.append(request)
            return Response()

        discover_backend_models(backends[backend_id], opener=opener)
        assert len(captured) == 1
        request = captured[0]
        assert request.full_url == f"{backends[backend_id]['configuration']['baseUrl']}/models"
        assert request.get_header("Authorization") == f"Bearer {secret}"
