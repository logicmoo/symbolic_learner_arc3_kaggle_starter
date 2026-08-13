from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "workbench" / "server"
sys.path.insert(0, str(SERVER))

from backend_library import load_workspace_backend_records  # noqa: E402


SHARED_WORKSPACE = ROOT / "workbench" / "workspaces" / "shared_library_system"


def test_shared_snet_backend_uses_environment_backed_credentials() -> None:
    backends = {
        str((record.get("document") or {}).get("id")): record.get("document") or {}
        for record in load_workspace_backend_records(SHARED_WORKSPACE)
    }

    snet = backends["snet"]
    assert snet["provider"] == "singularitynet"
    assert snet["enabled"] is True
    assert snet["configuration"]["adapter"] == "openai_chat_completions"
    assert snet["configuration"]["baseUrl"] == "https://llm.c.singularitynet.io/v1"
    assert snet["configuration"]["apiKeyEnvironmentVariable"] == "SNET_API_KEY"
    assert "apiKey" not in snet["configuration"]
