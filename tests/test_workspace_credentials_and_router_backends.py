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
    shared = ROOT / "workbench" / "workspaces" / "shared_library_system"
    backends = {
        str((record.get("document") or {}).get("id")): record.get("document") or {}
        for record in load_workspace_backend_records(shared)
    }
    assert (backends["clawrouter"].get("configuration") or {})["baseUrl"] == "http://127.0.0.1:3456/v1"
    assert (backends["freerouter"].get("configuration") or {})["baseUrl"] == "http://127.0.0.1:18800/v1"
    omniroute = backends["omniroute"]
    assert (omniroute.get("configuration") or {})["baseUrl"] == "http://localhost:20128/v1"
    assert (omniroute.get("configuration") or {})["credentialBootstrap"]["url"] == "http://localhost:20128/api/keys"
    assert backends["clawrouter"]["enabled"] is True
    assert (backends["clawrouter"].get("configuration") or {})["defaultModel"] == "blockrun/free"
    assert backends["omniroute"]["enabled"] is True
    assert (backends["omniroute"].get("configuration") or {})["defaultModel"] == "auto/best-free"
    assert backends["freerouter"]["enabled"] is True
    assert all(isinstance(backends[name]["enabled"], bool) for name in ("anthropic", "groq", "openai", "unsloth"))
    assert all(backends[name]["enabled"] is False for name in ("groq", "openai", "unsloth"))

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
    assert routers["openrouter-body-builder"]["enabled"] is True
    assert routers["openrouter-body-builder"]["model"] == "openrouter/bodybuilder"

    clawrouter = next(
        record.get("resolved") or {}
        for record in resolve_model_records(shared)
        if str((record.get("document") or {}).get("id")) == "clawrouter-free-router"
    )
    assert clawrouter["enabled"] is True
    assert clawrouter["model"] == "blockrun/free"
    assert (clawrouter.get("configuration") or {})["baseUrl"] == "http://127.0.0.1:3456/v1"

    omniroute_model = next(
        record.get("resolved") or {}
        for record in resolve_model_records(shared)
        if str((record.get("document") or {}).get("id")) == "omniroute-free-router"
    )
    assert omniroute_model["enabled"] is True
    assert omniroute_model["model"] == "auto/best-free"

    freerouter_model = next(
        record.get("resolved") or {}
        for record in resolve_model_records(shared)
        if str((record.get("document") or {}).get("id")) == "freerouter-auto-free"
    )
    assert freerouter_model["enabled"] is True
    assert freerouter_model["model"] == "auto"


def test_windows_clawrouter_launcher_uses_the_workbench_port_and_free_route() -> None:
    launcher = (ROOT / "workbench" / "scripts" / "run_clawrouter.bat").read_text(encoding="utf-8")
    demo = (ROOT / "workbench" / "run_demo.bat").read_text(encoding="utf-8")
    assert 'if exist "C:\\snet\\setkeys.bat" call "C:\\snet\\setkeys.bat"' in launcher
    assert "@blockrun/clawrouter --port %CLAWROUTER_PORT%" in launcher
    assert "Default workbench model: blockrun/free" in launcher
    assert 'set "CLAWROUTER_PORT=3456"' in demo
    assert "scripts\\run_clawrouter.bat %CLAWROUTER_PORT%" in demo


def test_windows_omniroute_launcher_uses_the_official_gateway_and_bootstrap() -> None:
    launcher = (ROOT / "workbench" / "scripts" / "run_omniroute.bat").read_text(encoding="utf-8")
    bootstrap = (ROOT / "workbench" / "scripts" / "bootstrap_omniroute.py").read_text(encoding="utf-8")
    demo = (ROOT / "workbench" / "run_demo.bat").read_text(encoding="utf-8")
    assert "npm.cmd install -g omniroute" in launcher
    assert 'set "PORT=%OMNIROUTE_PORT%"' in launcher
    assert 'set "DASHBOARD_PORT=%OMNIROUTE_PORT%"' in launcher
    assert "serve --port %OMNIROUTE_PORT% --no-open --no-tray --log" in launcher
    assert "bootstrap_backend_credential" in bootstrap
    assert 'set "OMNIROUTE_PORT=20128"' in demo
    assert "scripts\\bootstrap_omniroute.py" in demo


def test_windows_freerouter_launcher_uses_only_the_free_openrouter_route() -> None:
    launcher = (ROOT / "workbench" / "scripts" / "run_freerouter.bat").read_text(encoding="utf-8")
    configuration = json.loads((ROOT / "workbench" / "config" / "freerouter.config.json").read_text(encoding="utf-8"))
    demo = (ROOT / "workbench" / "run_demo.bat").read_text(encoding="utf-8")
    assert "https://github.com/openfreerouter/freerouter.git" in launcher
    assert 'set "CLAWROUTER_PORT=18800"' in launcher
    assert "node dist\\server.js" in launcher
    assert configuration["providers"]["openrouter"]["auth"]["key"] == "OPENROUTER_API_KEY"
    for tier_map in (configuration["tiers"], configuration["agenticTiers"]):
        assert {tier["primary"] for tier in tier_map.values()} == {"openrouter/openrouter/free"}
        assert all(tier["fallback"] == [] for tier in tier_map.values())
    assert 'set "FREEROUTER_PORT=18800"' in demo
    assert "scripts\\run_freerouter.bat" in demo


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
    assert statuses[0]["required"] is True
    assert "workspace-secret" not in json.dumps(statuses)
    write_workspace_credential(tmp_path, "EXAMPLE_API_KEY", None)
    assert resolve_workspace_credential(tmp_path, "EXAMPLE_API_KEY") == "process-secret"


def test_credential_status_reports_optional_backend_keys(tmp_path: Path) -> None:
    backend = {"id": "local", "label": "Local backend", "configuration": {"apiKeyEnvironmentVariable": "LOCAL_OPTIONAL_KEY", "apiKeyOptional": True}}
    status = credential_statuses(tmp_path, [backend])[0]
    assert status["required"] is False
    assert status["configured"] is False
    assert status["source"] == "missing"


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


def test_omniroute_bootstrap_can_authenticate_a_local_management_session(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    requests: list[dict[str, object]] = []

    class Response:
        def __init__(self, payload: bytes):
            self.payload = payload

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

        def read(self) -> bytes:
            return self.payload

    class Opener:
        def open(self, request, timeout):
            requests.append({"url": request.full_url, "body": json.loads(request.data.decode("utf-8")), "timeout": timeout})
            return Response(b'{"success":true}' if request.full_url.endswith("/login") else b'{"key":"session-key"}')

    monkeypatch.setattr("workspace_credentials.urllib.request.build_opener", lambda *_args: Opener())
    backend = {
        "id": "omniroute",
        "label": "OmniRoute",
        "configuration": {
            "apiKeyEnvironmentVariable": "OMNIROUTE_API_KEY",
            "credentialBootstrap": {
                "url": "http://localhost:20128/api/keys",
                "request": {"name": "MeTTaSymbolicLearnerWorkbench"},
                "responseField": "key",
                "sessionLogin": {
                    "url": "http://localhost:20128/api/auth/login",
                    "passwordEnvironmentVariable": "OMNIROUTE_ADMIN_PASSWORD",
                    "defaultPassword": "CHANGEME",
                    "requestField": "password",
                },
            },
        },
    }
    bootstrap_backend_credential(tmp_path, backend)
    assert [request["url"] for request in requests] == [
        "http://localhost:20128/api/auth/login",
        "http://localhost:20128/api/keys",
    ]
    assert requests[0]["body"] == {"password": "CHANGEME"}
    assert resolve_workspace_credential(tmp_path, "OMNIROUTE_API_KEY") == "session-key"


def test_workspace_credentials_inherit_from_shared_and_allow_local_override(tmp_path: Path) -> None:
    shared = tmp_path / "shared_library_system"
    project = tmp_path / "project"
    shared.mkdir()
    project.mkdir()
    write_workspace_credential(shared, "ROUTER_API_KEY", "shared-secret")
    assert resolve_workspace_credential(project, "ROUTER_API_KEY") == "shared-secret"
    write_workspace_credential(project, "ROUTER_API_KEY", "project-secret")
    assert resolve_workspace_credential(project, "ROUTER_API_KEY") == "project-secret"


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
