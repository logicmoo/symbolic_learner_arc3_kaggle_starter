from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "workbench" / "server"
sys.path.insert(0, str(SERVER))

from backend_library import load_workspace_backend_records  # noqa: E402
from model_library import resolve_model_records  # noqa: E402
from policy_library import load_workspace_policy_records  # noqa: E402
from workflow_providers import _llm_complete  # noqa: E402
from workspace_credentials import (  # noqa: E402
    bootstrap_backend_credential,
    credential_statuses,
    read_workspace_credentials,
    resolve_workspace_credential,
    write_workspace_credential,
)


def test_shared_router_backends_and_free_first_defaults_load_from_metta() -> None:
    shared = ROOT / "workbench" / "workspaces" / "shared"
    backends = {
        str((record.get("document") or {}).get("id")): record.get("document") or {}
        for record in load_workspace_backend_records(shared)
    }
    assert (backends["clawrouter"].get("configuration") or {})["baseUrl"] == "http://127.0.0.1:3456/v1"
    assert (backends["freerouter"].get("configuration") or {})["baseUrl"] == "http://127.0.0.1:18800/v1"
    omniroute = backends["omniroute"]
    assert (omniroute.get("configuration") or {})["baseUrl"] == "http://localhost:20128/v1"
    assert (omniroute.get("configuration") or {})["credentialBootstrap"]["url"] == "http://localhost:20128/api/keys"
    assert all(backends[name]["enabled"] is False for name in ("anthropic", "clawrouter", "groq", "omniroute", "openai", "unsloth"))

    vendor_policies = {
        str((record.get("document") or {}).get("vendorId")): record.get("document") or {}
        for record in load_workspace_policy_records(shared)
        if (record.get("document") or {}).get("kind") == "vendor_policy"
    }
    for vendor_id in ("anthropic", "groq", "openai", "xai"):
        assert (vendor_policies[vendor_id].get("policy") or {}) == {
            "wanted": "off", "runtime": "off", "benchmark": "off",
        }

    routers = {
        str((record.get("document") or {}).get("id")): record.get("resolved") or {}
        for record in resolve_model_records(shared)
        if str((record.get("document") or {}).get("id", "")).startswith("openrouter-")
    }
    assert routers["openrouter-free-router"]["enabled"] is True
    assert all(
        resolved["enabled"] is False
        for router_id, resolved in routers.items()
        if router_id != "openrouter-free-router"
    )


def test_workspace_credentials_override_environment_without_leaking_values(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EXAMPLE_API_KEY", "process-secret")
    backend = {
        "id": "example",
        "label": "Example",
        "configuration": {"apiKeyEnvironmentVariable": "EXAMPLE_API_KEY"},
    }
    assert resolve_workspace_credential(tmp_path, "EXAMPLE_API_KEY") == "process-secret"
    write_workspace_credential(tmp_path, "EXAMPLE_API_KEY", "workspace-secret")
    assert read_workspace_credentials(tmp_path) == {"EXAMPLE_API_KEY": "workspace-secret"}
    assert resolve_workspace_credential(tmp_path, "EXAMPLE_API_KEY") == "workspace-secret"
    statuses = credential_statuses(tmp_path, [backend])
    assert statuses[0]["source"] == "workspace"
    assert "workspace-secret" not in json.dumps(statuses)
    write_workspace_credential(tmp_path, "EXAMPLE_API_KEY", None)
    assert resolve_workspace_credential(tmp_path, "EXAMPLE_API_KEY") == "process-secret"


def test_omniroute_bootstrap_fetches_one_time_key_from_loopback(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

        def read(self) -> bytes:
            return b'{"id":"key-1","key":"omni-secret"}'

    captured: dict[str, object] = {}

    def open_request(request, timeout):
        captured["url"] = request.full_url
        captured["body"] = json.loads(request.data.decode("utf-8"))
        captured["timeout"] = timeout
        return Response()

    monkeypatch.setattr("workspace_credentials.urllib.request.urlopen", open_request)
    backend = {
        "id": "omniroute",
        "label": "OmniRoute",
        "configuration": {
            "apiKeyEnvironmentVariable": "OMNIROUTE_API_KEY",
            "credentialBootstrap": {
                "url": "http://localhost:20128/api/keys",
                "method": "POST",
                "request": {"name": "MeTTaSymbolicLearnerWorkbench"},
                "responseField": "key",
            },
        },
    }
    assert bootstrap_backend_credential(tmp_path, backend) == "OMNIROUTE_API_KEY"
    assert captured["url"] == "http://localhost:20128/api/keys"
    assert captured["body"] == {"name": "MeTTaSymbolicLearnerWorkbench"}
    assert resolve_workspace_credential(tmp_path, "OMNIROUTE_API_KEY") == "omni-secret"


def test_credential_bootstrap_rejects_non_loopback_services(tmp_path: Path) -> None:
    backend = {
        "id": "unsafe",
        "configuration": {
            "apiKeyEnvironmentVariable": "UNSAFE_API_KEY",
            "credentialBootstrap": {"url": "https://example.com/api/keys"},
        },
    }
    with pytest.raises(ValueError, match="restricted to a local HTTP service"):
        bootstrap_backend_credential(tmp_path, backend)


def test_llm_invocation_uses_workspace_key_and_allows_keyless_local_router(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

        def getcode(self) -> int:
            return 200

        def read(self) -> bytes:
            return b'{"choices":[{"message":{"content":"ok"}}]}'

    requests = []

    def open_request(request, **_kwargs):
        requests.append(request)
        return Response()

    monkeypatch.setattr("workflow_providers.urllib.request.urlopen", open_request)
    write_workspace_credential(tmp_path, "ROUTER_API_KEY", "workspace-secret")
    keyed = _llm_complete(
        {"prompt": "test"},
        {"baseUrl": "https://router.example/v1", "apiKeyEnv": "ROUTER_API_KEY", "workspaceRoot": str(tmp_path)},
    )
    assert keyed["text"] == "ok"
    assert requests[-1].headers["Authorization"] == "Bearer workspace-secret"

    keyless = _llm_complete(
        {"prompt": "test"},
        {"baseUrl": "http://127.0.0.1:18800/v1", "model": "auto"},
    )
    assert keyless["text"] == "ok"
    assert "Authorization" not in requests[-1].headers
