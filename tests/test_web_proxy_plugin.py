from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "workbench" / "server"
if str(SERVER) not in sys.path:
    sys.path.insert(0, str(SERVER))


def test_web_proxy_plugin_is_discovered_and_loaded() -> None:
    app_module = importlib.import_module("app")
    with TestClient(app_module.app) as client:
        response = client.get("/api/plugins")
    assert response.status_code == 200
    plugin = next(item for item in response.json()["plugins"] if item["id"] == "web_proxy")
    assert plugin["scan"] == "startup"
    assert plugin["loaded"] is True
    assert plugin["routePrefix"] == "/web_proxy"
    assert plugin["allowedTargets"] == ["http://127.0.0.1:8801"]


def test_web_proxy_rejects_targets_outside_manifest_allowlist() -> None:
    app_module = importlib.import_module("app")
    with TestClient(app_module.app) as client:
        response = client.get("/web_proxy/http/127.0.0.1:9999/health")
    assert response.status_code == 403
    assert "not allowed" in response.json()["error"]


def test_plugin_scan_policy_validation() -> None:
    app_module = importlib.import_module("app")
    with TestClient(app_module.app) as client:
        response = client.put("/api/plugins/web_proxy", json={"scan": "sometimes"})
    assert response.status_code == 400


def test_plugins_navigation_and_page_are_wired() -> None:
    source = (ROOT / "workbench" / "frontend" / "src" / "pages" / "FilesystemWorkbenchPage.tsx").read_text(encoding="utf-8")
    page = (ROOT / "workbench" / "frontend" / "src" / "components" / "PluginManagerPage.tsx").read_text(encoding="utf-8")
    assert 'group: "PLUGINS"' in source
    assert '{ label: "Plugins", view: "plugins"' in source
    assert 'view === "plugins" && <PluginManagerPage />' in source
    assert 'fetch(`/api/plugins${refresh ? "/refresh" : ""}`' in page
    assert '<option value="startup">Scan at startup</option>' in page
    assert '<option value="disabled">Disabled</option>' in page


def test_every_plugin_publishes_an_admin_link_the_scanner_reads_from_disk() -> None:
    app_module = importlib.import_module("app")
    with TestClient(app_module.app) as client:
        response = client.get("/api/plugins")
    assert response.status_code == 200
    payload = response.json()
    assert payload["manifestName"] == "plugin.json"
    for plugin in payload["plugins"]:
        assert plugin["adminPath"].startswith("/")
        assert plugin["adminApiPath"] == f"/api{plugin['adminPath']}"
        configure = [page for page in plugin["uiPages"] if page["kind"] in {"configure", "admin"}]
        assert configure, f"{plugin['id']} contributes no configure page"
        assert configure[0]["address"], f"{plugin['id']} configure page has no address"


def test_plugin_directory_never_overwrites_the_declared_admin_path() -> None:
    """The loader stores the plugin directory under 'path'; that must not win."""

    app_module = importlib.import_module("app")
    with TestClient(app_module.app) as client:
        plugins = {item["id"]: item for item in client.get("/api/plugins").json()["plugins"]}
    web_proxy = plugins["web_proxy"]
    assert web_proxy["adminPath"] == "/web_proxy/admin"
    assert Path(web_proxy["path"]).name == "web_proxy"


def test_ws_collab_resolves_its_own_pages_to_the_page_it_serves() -> None:
    app_module = importlib.import_module("app")
    with TestClient(app_module.app) as client:
        plugins = {item["id"]: item for item in client.get("/api/plugins").json()["plugins"]}
    ws_collab = plugins["ws_collab"]
    assert ws_collab["configPage"] == "http://127.0.0.1:5173/ws_collab/admin"
    for page in ws_collab["uiPages"]:
        assert page["external"] is True
        assert page["address"].startswith("http://127.0.0.1:5173/ws_collab/admin")


def test_plugin_init_mounts_the_requested_path_through_web_proxy() -> None:
    """ws_collab asks web_proxy to serve /ws_collab; the loader runs that command."""

    app_module = importlib.import_module("app")
    with TestClient(app_module.app) as client:
        plugins = {item["id"]: item for item in client.get("/api/plugins").json()["plugins"]}
        mounted = client.get("/ws_collab/admin")
    results = plugins["ws_collab"]["initCommandResults"]
    assert results, "ws_collab declared plugin-init but nothing ran"
    assert all(result["applied"] for result in results), results
    assert results[0]["command"] == "web_proxy"
    manifest = json.loads(
        (ROOT / "workbench" / "plugins" / "web_proxy" / "plugin.json").read_text(encoding="utf-8")
    )
    assert any(mount["path"] == "/ws_collab" for mount in manifest["mounts"])
    assert mounted.status_code == 200


def test_web_proxy_admin_page_is_served_on_the_api_port_and_under_api() -> None:
    app_module = importlib.import_module("app")
    with TestClient(app_module.app) as client:
        direct = client.get("/web_proxy/admin")
        mirrored = client.get("/api/web_proxy/admin")
    assert direct.status_code == 200
    assert mirrored.status_code == 200
    descriptor = direct.json()
    assert descriptor["pluginId"] == "web_proxy"
    assert descriptor["declaredOnDisk"] is True
    assert descriptor["adminPath"] == "/web_proxy/admin"
    assert any(section["id"] == "targets" for section in descriptor["sections"])
    assert descriptor["documentation"].startswith("# Web Proxy administration and setup")
    assert mirrored.json()["pluginId"] == "web_proxy"


def test_web_proxy_admin_reports_initialization_requirements() -> None:
    app_module = importlib.import_module("app")
    with TestClient(app_module.app) as client:
        descriptor = client.get("/api/web_proxy/admin").json()
        initialized = client.post("/api/web_proxy/admin/initialize", json={})
    initialization = descriptor["initialization"]
    assert initialization["ready"] is True
    assert {check["name"] for check in initialization["checks"]} >= {"httpx", "websockets"}
    assert initialized.status_code == 200
    assert initialized.json()["actionResult"]["ready"] is True


def test_web_proxy_admin_rejects_an_invalid_timeout_and_keeps_the_manifest() -> None:
    app_module = importlib.import_module("app")
    manifest = ROOT / "workbench" / "plugins" / "web_proxy" / "plugin.json"
    before = manifest.read_text(encoding="utf-8")
    with TestClient(app_module.app) as client:
        response = client.put(
            "/api/web_proxy/admin/settings", json={"values": {"requestTimeoutSeconds": -3}}
        )
    assert response.status_code == 400
    assert manifest.read_text(encoding="utf-8") == before


def test_web_proxy_admin_saves_settings_to_plain_json_not_a_metta_sibling() -> None:
    app_module = importlib.import_module("app")
    directory = ROOT / "workbench" / "plugins" / "web_proxy"
    manifest = directory / "plugin.json"
    before = manifest.read_text(encoding="utf-8")
    try:
        with TestClient(app_module.app) as client:
            response = client.put(
                "/api/web_proxy/admin/settings",
                json={"values": {"requestTimeoutSeconds": 12, "followRedirects": True}},
            )
        assert response.status_code == 200
        stored = json.loads(manifest.read_text(encoding="utf-8"))
        assert stored["requestTimeoutSeconds"] == 12
        assert stored["followRedirects"] is True
        # Plugin manifests are plain configuration, never workspace resources.
        assert not (directory / "plugin.metta").exists()
    finally:
        manifest.write_text(before, encoding="utf-8")


def test_plugin_admin_panel_renders_the_descriptor_natively() -> None:
    panel = (ROOT / "workbench" / "frontend" / "src" / "components" / "PluginAdminPanel.tsx").read_text(encoding="utf-8")
    page = (ROOT / "workbench" / "frontend" / "src" / "components" / "PluginManagerPage.tsx").read_text(encoding="utf-8")
    assert "Initialize plugin" in panel
    assert "`${adminPath}/settings`" in panel
    assert "`${adminPath}/initialize`" in panel
    assert "`${adminPath}/actions/${encodeURIComponent(action.id)}`" in panel
    assert "PluginAdminPanel" in page
    assert "plugin-page-links" in page
    assert "address" in page


def test_vite_forwards_proxy_http_and_websockets_to_the_backend() -> None:
    """The dev/preview proxy is generated from the plugin manifests, and anything
    the web server does not own falls back to the API."""

    source = (ROOT / "workbench" / "frontend" / "vite.config.ts").read_text(encoding="utf-8")
    assert "pluginProxyPrefixes" in source
    assert "manifest.routePrefix" in source
    assert "manifest.mounts" in source
    assert "API_FALLBACK" in source
    assert source.count("proxy: apiProxy(apiTarget)") == 2
    assert "ws: true" in source


def test_every_plugin_route_prefix_uses_the_plugin_identifier() -> None:
    """A plugin's route prefix matches its id, so links stay predictable."""

    for manifest_path in sorted((ROOT / "workbench" / "plugins").glob("*/plugin.json")):
        manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
        assert manifest["routePrefix"] == f"/{manifest['id']}", manifest_path
