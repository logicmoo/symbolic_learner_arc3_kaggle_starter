from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "workbench" / "server"
sys.path.insert(0, str(SERVER))

from backend_library import load_workspace_backend_records  # noqa: E402
from model_library import resolve_model_records  # noqa: E402


def test_shared_asi_backends_load_with_expected_credentials_and_endpoints() -> None:
    shared = ROOT / "workbench" / "workspaces" / "shared_library_system"
    backends = {
        str((record.get("document") or {}).get("id")): record.get("document") or {}
        for record in load_workspace_backend_records(shared)
    }

    asicloud = backends["asicloud"]
    assert asicloud["enabled"] is True
    assert asicloud["configuration"]["adapter"] == "openai_chat_completions"
    assert asicloud["configuration"]["baseUrl"] == "https://inference.asicloud.cudos.org/v1"
    assert asicloud["configuration"]["apiKeyEnvironmentVariable"] == "ASI_API_KEY"
    assert asicloud["configuration"]["defaultModel"] == "asi1-mini"
    assert "asicloud-asi1-mini" in asicloud["children"]

    models = {
        str((record.get("document") or {}).get("id")): record
        for record in resolve_model_records(shared)
    }
    asi1_mini = models["asicloud-asi1-mini"]
    assert asi1_mini["document"]["model"] == "asi1-mini"
    assert asi1_mini["resolved"]["model"] == "asi1-mini"
    assert asi1_mini["resolved"]["configuration"]["baseUrl"] == "https://inference.asicloud.cudos.org/v1"
    assert asi1_mini["resolved"]["configuration"]["apiKeyEnvironmentVariable"] == "ASI_API_KEY"

    asione = backends["asione"]
    assert asione["enabled"] is True
    assert asione["configuration"]["adapter"] == "openai_chat_completions"
    assert asione["configuration"]["baseUrl"] == "https://api.asi1.ai/v1"
    assert asione["configuration"]["apiKeyEnvironmentVariable"] == "ASIONE_API_KEY"
    assert asione["configuration"]["defaultModel"] == "asi1-ultra"
