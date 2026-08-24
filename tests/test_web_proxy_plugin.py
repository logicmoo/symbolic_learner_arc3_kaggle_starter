from __future__ import annotations

import importlib
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
    assert plugin["routePrefix"] == "/web-proxy"
    assert plugin["allowedTargets"] == ["http://127.0.0.1:8801"]


def test_web_proxy_rejects_targets_outside_manifest_allowlist() -> None:
    app_module = importlib.import_module("app")
    with TestClient(app_module.app) as client:
        response = client.get("/web-proxy/http/127.0.0.1:9999/health")
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
    assert 'fetch(`/api/plugins${refresh?"/refresh":""}`' in page
    assert '<option value="startup">Scan at startup</option>' in page
    assert '<option value="disabled">Disabled</option>' in page


def test_vite_forwards_proxy_http_and_websockets_to_the_backend() -> None:
    source = (ROOT / "workbench" / "frontend" / "vite.config.ts").read_text(encoding="utf-8")
    assert source.count('"/web-proxy"') == 2
    assert source.count("ws: true") == 2
