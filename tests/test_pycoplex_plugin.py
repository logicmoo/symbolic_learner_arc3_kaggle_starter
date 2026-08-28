from __future__ import annotations

import importlib
import importlib.util
import json
import shutil
import sys
import time
import uuid
from pathlib import Path
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
PLUGIN_PACKAGES = ROOT / "workbench" / "plugins"
SERVER = ROOT / "workbench" / "server"
if str(PLUGIN_PACKAGES) not in sys.path:
    sys.path.insert(0, str(PLUGIN_PACKAGES))
if str(SERVER) not in sys.path:
    sys.path.insert(0, str(SERVER))

from pycoplex import HarnessTaskManager


@pytest.fixture
def isolated_plugin(tmp_path: Path) -> tuple[Any, FastAPI, dict[str, Any], Path, Path]:
    """Mount a fresh plugin module against a temporary repository and manifest."""

    repository = tmp_path / "repository"
    plugin_directory = repository / "workbench" / "plugins" / "pycoplex"
    plugin_directory.mkdir(parents=True)
    source_directory = ROOT / "workbench" / "plugins" / "pycoplex"
    manifest_path = plugin_directory / "plugin.json"
    shutil.copyfile(source_directory / "plugin.json", manifest_path)
    shutil.copyfile(source_directory / "README.md", plugin_directory / "README.md")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["path"] = str(plugin_directory)

    plugin_path = source_directory / "plugin.py"
    spec = importlib.util.spec_from_file_location(
        f"pycoplex_isolated_{uuid.uuid4().hex}",
        plugin_path,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.initialize(manifest)

    app = FastAPI()
    app.include_router(module.create_router(manifest))
    admin_router = module.create_admin_router(manifest)
    app.include_router(admin_router)
    app.include_router(admin_router, prefix="/api")
    try:
        yield module, app, manifest, manifest_path, repository
    finally:
        manager = module._manager
        if manager is not None:
            manager.close()
            module._manager = None


def test_pycoplex_manifest_and_packaging_contract() -> None:
    directory = ROOT / "workbench" / "plugins" / "pycoplex"
    manifest = json.loads((directory / "plugin.json").read_text(encoding="utf-8"))
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    ignore = (ROOT / "workbench" / "plugins" / ".gitignore").read_text(encoding="utf-8")
    assert manifest["id"] == "pycoplex"
    assert manifest["routePrefix"] == "/pycoplex"
    assert manifest["adminPage"] == "/pycoplex/admin"
    assert manifest["entrypoint"] == "plugin.py"
    assert manifest["executionEnabled"] is False
    assert manifest["maximumPermissionProfile"] == "workspace-write"
    assert manifest["allowApprovalNever"] is False
    assert any(page["kind"] == "configure" for page in manifest["ui"]["pages"])
    assert any(page["id"] == "task-console" for page in manifest["ui"]["pages"])
    assert all(isinstance(item, dict) and item.get("path") for item in manifest["plugin-install"]["files"])
    assert 'pycoplex = "workbench/plugins/pycoplex"' in pyproject
    assert "!/pycoplex/" in ignore
    assert (directory / "__init__.py").is_file()
    assert (directory / "runtime.py").is_file()
    assert not (ROOT / "python" / "pycoplex.py").exists()


def test_pycoplex_is_discovered_loaded_and_serves_capabilities() -> None:
    app_module = importlib.import_module("app")
    with TestClient(app_module.app) as client:
        catalog = client.get("/api/plugins")
        health = client.get("/pycoplex/health")
        capabilities = client.get("/pycoplex/capabilities")
    assert catalog.status_code == 200
    plugin = next(item for item in catalog.json()["plugins"] if item["id"] == "pycoplex")
    assert plugin["loaded"] is True, plugin.get("error")
    assert plugin["scan"] == "startup"
    assert plugin["adminPath"] == "/pycoplex/admin"
    assert plugin["initialization"]["ready"] is True
    console = next(page for page in plugin["uiPages"] if page["id"] == "task-console")
    assert console["external"] is True
    assert console["address"] == "/pycoplex/ui"
    assert health.status_code == 200
    assert health.json()["ok"] is True
    assert capabilities.status_code == 200
    payload = capabilities.json()
    assert payload["executionEnabled"] is False
    assert {tool["name"] for tool in payload["tools"]} >= {
        "read_file", "write_file", "apply_patch", "run_tests", "subagents", "request_user_input"
    }


def test_pycoplex_serves_real_task_console(
    isolated_plugin: tuple[Any, FastAPI, dict[str, Any], Path, Path],
) -> None:
    _, app, _, _, _ = isolated_plugin
    with TestClient(app) as client:
        response = client.get("/pycoplex/ui")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "frame-ancestors 'self'" in response.headers["content-security-policy"]
    assert "LLM Task Harness" in response.text
    assert 'const API = "/pycoplex"' in response.text
    assert "approval.requested" not in response.text  # events are loaded from the real task API


def test_pycoplex_admin_descriptor_is_native_and_documented(
    isolated_plugin: tuple[Any, FastAPI, dict[str, Any], Path, Path],
) -> None:
    _, app, _, _, _ = isolated_plugin
    with TestClient(app) as client:
        direct = client.get("/pycoplex/admin")
        mirrored = client.get("/api/pycoplex/admin")
    assert direct.status_code == 200
    assert mirrored.status_code == 200
    payload = direct.json()
    assert payload["pluginId"] == "pycoplex"
    assert payload["adminPath"] == "/pycoplex/admin"
    assert {section["id"] for section in payload["sections"]} == {"execution", "provider", "limits"}
    assert {action["id"] for action in payload["actions"]} == {"probe-models"}
    execution = next(section for section in payload["sections"] if section["id"] == "execution")
    assert {item["id"] for item in execution["fields"]} >= {
        "maximumPermissionProfile", "allowApprovalNever"
    }
    assert payload["documentation"].startswith("# LLM Task Harness")
    assert mirrored.json()["pluginId"] == "pycoplex"


def test_pycoplex_task_api_is_gated_by_default(
    isolated_plugin: tuple[Any, FastAPI, dict[str, Any], Path, Path],
) -> None:
    _, app, _, _, _ = isolated_plugin
    with TestClient(app) as client:
        response = client.post("/pycoplex/tasks", json={"task": "do not execute"})
    assert response.status_code == 403
    assert "disabled" in str(response.json().get("detail") or response.json().get("error"))


def test_pycoplex_rejects_invalid_admin_settings_without_editing_manifest(
    isolated_plugin: tuple[Any, FastAPI, dict[str, Any], Path, Path],
) -> None:
    _, app, _, manifest, _ = isolated_plugin
    before = manifest.read_text(encoding="utf-8")
    with TestClient(app) as client:
        response = client.put(
            "/api/pycoplex/admin/settings",
            json={"values": {"modelBaseUrl": "not-a-url", "maxSteps": 0}},
        )
    assert response.status_code == 400
    assert manifest.read_text(encoding="utf-8") == before


def test_pycoplex_admin_rejects_ambiguous_booleans_numbers_and_open_network(
    isolated_plugin: tuple[Any, FastAPI, dict[str, Any], Path, Path],
) -> None:
    _, app, _, manifest, _ = isolated_plugin
    before = manifest.read_text(encoding="utf-8")
    with TestClient(app) as client:
        ambiguous = client.put(
            "/api/pycoplex/admin/settings",
            json={"values": {"executionEnabled": "definitely"}},
        )
        number = client.put(
            "/api/pycoplex/admin/settings",
            json={"values": {"maxSteps": "many"}},
        )
        network = client.put(
            "/api/pycoplex/admin/settings",
            json={"values": {"allowToolNetwork": True, "allowedHosts": []}},
        )
        insecure_model = client.put(
            "/api/pycoplex/admin/settings",
            json={"values": {"modelBaseUrl": "http://models.example/v1"}},
        )
    assert ambiguous.status_code == 400
    assert number.status_code == 400
    assert network.status_code == 400
    assert insecure_model.status_code == 400
    assert manifest.read_text(encoding="utf-8") == before


def test_pycoplex_manager_reopens_across_app_lifespans(
    isolated_plugin: tuple[Any, FastAPI, dict[str, Any], Path, Path],
) -> None:
    module, app, _, _, _ = isolated_plugin
    with TestClient(app) as first:
        assert first.get("/pycoplex/health").status_code == 200
    assert module._manager is None
    with TestClient(app) as second:
        response = second.get("/pycoplex/health")
        assert module._manager is not None
        assert module._manager._executor.submit(lambda: "open").result(timeout=1) == "open"
    assert response.status_code == 200
    assert response.json()["ok"] is True


def test_pycoplex_enabled_http_task_lifecycle_is_real_and_isolated(
    isolated_plugin: tuple[Any, FastAPI, dict[str, Any], Path, Path],
) -> None:
    module, app, manifest, _, repository = isolated_plugin
    enabled = {
        **manifest,
        "executionEnabled": True,
        "defaultPermissionProfile": "read-only",
        "maximumPermissionProfile": "read-only",
        "defaultApprovalMode": "on-request",
        "maxWorkers": 1,
        "maxSteps": 2,
        "modelTimeoutSeconds": 5,
        "taskTimeoutSeconds": 30,
    }
    assert module._manager is not None
    module._manager.close()
    module._manifest = enabled
    module._manager = HarnessTaskManager(
        repository,
        enabled,
        adapter_factory=lambda _: lambda __: {"content": "isolated complete", "tool_calls": []},
        state_directory="runtime/pycoplex",
    )
    with TestClient(app) as client:
        submitted = client.post("/pycoplex/tasks", json={"task": "inspect safely"})
        assert submitted.status_code == 202, submitted.text
        task_id = submitted.json()["id"]
        deadline = time.monotonic() + 5
        current: dict[str, Any] = {}
        while time.monotonic() < deadline:
            response = client.get(f"/pycoplex/tasks/{task_id}")
            assert response.status_code == 200
            current = response.json()
            if current["status"] in {"completed", "failed", "cancelled"}:
                break
            time.sleep(0.01)
        assert current["status"] == "completed", current
        assert current["answer"] == "isolated complete"
        events = client.get(f"/pycoplex/tasks/{task_id}/events").json()["events"]
        assert {event["event"] for event in events} >= {
            "task.queued", "task.started", "task.completed",
        }
    assert (repository / "runtime" / "pycoplex" / "tasks" / f"{task_id}.json").is_file()
    assert not (ROOT / "runtime" / "pycoplex" / "tasks" / f"{task_id}.json").exists()


def test_pycoplex_valid_admin_settings_persist_and_hot_update(
    isolated_plugin: tuple[Any, FastAPI, dict[str, Any], Path, Path],
) -> None:
    module, app, _, manifest_path, _ = isolated_plugin
    with TestClient(app) as client:
        response = client.put(
            "/api/pycoplex/admin/settings",
            json={"values": {"defaultModel": "fixture/model", "maxSteps": 17}},
        )
        assert response.status_code == 200, response.text
        assert module._manager.settings["defaultModel"] == "fixture/model"
        assert module._manager.settings["maxSteps"] == 17
    stored = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert stored["defaultModel"] == "fixture/model"
    assert stored["maxSteps"] == 17


def test_plugin_page_route_persists_and_restores_plugin_identity() -> None:
    source = (
        ROOT / "workbench" / "frontend" / "src" / "pages" / "FilesystemWorkbenchPage.tsx"
    ).read_text(encoding="utf-8")
    assert 'url.searchParams.set("pluginId", options.pluginPage.pluginId)' in source
    assert 'url.searchParams.set("pluginPage", options.pluginPage.id)' in source
    assert 'const pluginId = params.get("pluginId")' in source
    assert 'const pageId = params.get("pluginPage")' in source
    assert 'setView("pluginPage", { pluginPage: entry })' in source


def test_pycoplex_initialize_rejects_malformed_policy() -> None:
    path = ROOT / "workbench" / "plugins" / "pycoplex" / "plugin.py"
    spec = importlib.util.spec_from_file_location("pycoplex_validation_test", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    manifest = json.loads(path.with_name("plugin.json").read_text(encoding="utf-8"))
    manifest["path"] = str(path.parent)
    with pytest.raises(ValueError, match="executionEnabled"):
        module.initialize({**manifest, "executionEnabled": "false"})
    with pytest.raises(ValueError, match="maximumPermissionProfile"):
        module.initialize({
            **manifest,
            "defaultPermissionProfile": "full-access",
            "maximumPermissionProfile": "workspace-write",
        })
    with pytest.raises(ValueError, match="allowApprovalNever"):
        module.initialize({
            **manifest,
            "defaultApprovalMode": "never",
            "allowApprovalNever": False,
        })
