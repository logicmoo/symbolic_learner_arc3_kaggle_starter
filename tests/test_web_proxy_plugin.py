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
        response = client.get("/workbench/plugins")
    assert response.status_code == 200
    plugin = next(item for item in response.json()["plugins"] if item["id"] == "web_proxy")
    assert plugin["scan"] == "startup"
    assert plugin["loaded"] is True
    assert plugin["routePrefix"] == "/web_proxy"
    assert plugin["allowedTargets"] == ["*://127.0.0.1:*/*"]


def test_plugin_scanner_skips_hidden_and_manifestless_entries(
    tmp_path: Path,
    monkeypatch,
) -> None:
    plugin_api = importlib.import_module("plugin_api")
    visible = tmp_path / "visible"
    visible.mkdir()
    (visible / "plugin.json").write_text(
        json.dumps({"id": "visible", "scan": "disabled"}),
        encoding="utf-8",
    )
    for name in ("HIDE_broken", "HiDe_also_broken"):
        hidden = tmp_path / name
        hidden.mkdir()
        (hidden / "plugin.json").write_text("{not valid json", encoding="utf-8")
    (tmp_path / "missing_manifest").mkdir()
    (tmp_path / "loose_object").write_text("not a plugin", encoding="utf-8")

    monkeypatch.setattr(plugin_api, "PLUGINS_ROOT", tmp_path)
    monkeypatch.setattr(plugin_api, "POLICY_PATH", tmp_path / "plugins.json")

    catalog = plugin_api._scan(register=False)

    assert [plugin["id"] for plugin in catalog] == ["visible"]


def test_plugin_scanner_declared_masks_found_list_and_enabled_toggle(
    tmp_path: Path,
    monkeypatch,
) -> None:
    """plugins.json declares discovery: startupScan masks reach two levels,
    skipScan masks hide entries case-insensitively, every discovery is
    recorded in foundList, and "enabled": false there keeps a plugin off."""

    plugin_api = importlib.import_module("plugin_api")
    top = tmp_path / "top"
    top.mkdir()
    (top / "plugin.json").write_text(json.dumps({"id": "top", "scan": "disabled"}), encoding="utf-8")
    nested = tmp_path / "vendor" / "nested"
    nested.mkdir(parents=True)
    (nested / "plugin.json").write_text(json.dumps({"id": "nested", "scan": "disabled"}), encoding="utf-8")
    secret = tmp_path / "vendor" / "SeCrEt_lab"
    secret.mkdir()
    (secret / "plugin.json").write_text(json.dumps({"id": "secret", "scan": "disabled"}), encoding="utf-8")
    policy_path = tmp_path / "plugins.json"
    policy_path.write_text(json.dumps({
        "startupScan": ["*/plugin.json", "*/*/plugin.json"],
        "skipScan": ["hide_*", "secret_*"],
        "pluginsFound": {"nested": {"path": "vendor/nested/plugin.json", "scan": "disabled", "enabled": False}},
        "plugins": {},
    }), encoding="utf-8")
    monkeypatch.setattr(plugin_api, "PLUGINS_ROOT", tmp_path)
    monkeypatch.setattr(plugin_api, "POLICY_PATH", policy_path)

    catalog = {plugin["id"]: plugin for plugin in plugin_api._scan(register=False)}

    assert set(catalog) == {"top", "nested"}, "two-level discovery minus skipScan matches"
    assert catalog["nested"]["scan"] == "disabled", "enabled: false in pluginsFound disables the plugin"
    stored = json.loads(policy_path.read_text(encoding="utf-8"))
    assert stored["pluginsFound"]["top"] == {"path": "top/plugin.json", "scan": "disabled", "enabled": True}, "new discovery recorded"
    assert stored["pluginsFound"]["nested"]["enabled"] is False, "existing toggle preserved"
    assert "secret" not in stored["pluginsFound"]


def test_plugin_mailbox_endpoints_resolve_for_every_declaring_server(
    tmp_path: Path,
    monkeypatch,
) -> None:
    """Each plugin server's mailbox list is discoverable from the catalog: a
    top-level `mailboxEndpoint` (string or object) resolves to an address the
    Chat page can query; plugins without one report null."""

    plugin_api = importlib.import_module("plugin_api")
    manifests = {
        "relay": {
            "id": "relay",
            "scan": "disabled",
            "mailboxEndpoint": {
                "path": "/relay/v1/mailbox/mailboxes",
                "protocol": "ws_collab",
                "description": "directory",
            },
        },
        "registryish": {
            "id": "registryish",
            "scan": "disabled",
            "mailboxEndpoint": {"path": "/registryish/v1/registry", "protocol": "registry"},
        },
        "terse": {"id": "terse", "scan": "disabled", "mailboxEndpoint": "/terse/mailbox/mailboxes"},
        "plain": {"id": "plain", "scan": "disabled"},
    }
    for name, manifest in manifests.items():
        directory = tmp_path / name
        directory.mkdir()
        (directory / "plugin.json").write_text(json.dumps(manifest), encoding="utf-8")
    monkeypatch.setattr(plugin_api, "PLUGINS_ROOT", tmp_path)
    monkeypatch.setattr(plugin_api, "POLICY_PATH", tmp_path / "plugins.json")

    catalog = {plugin["id"]: plugin for plugin in plugin_api._scan(register=False)}

    relay = catalog["relay"]["mailboxEndpoint"]
    assert relay["address"] == "/relay/v1/mailbox/mailboxes"
    assert relay["protocol"] == "ws_collab"
    registryish = catalog["registryish"]["mailboxEndpoint"]
    assert registryish["address"] == "/registryish/v1/registry"
    assert registryish["protocol"] == "registry"
    terse = catalog["terse"]["mailboxEndpoint"]
    assert terse["address"] == "/terse/mailbox/mailboxes"
    assert terse["protocol"] == "ws_collab"
    assert catalog["plain"]["mailboxEndpoint"] is None


def test_chat_page_queries_every_declared_mailbox_server() -> None:
    """The Chat page discovers mailbox servers from the plugin catalog and
    queries each declared endpoint instead of only ws_collab."""

    source = (
        ROOT / "workbench" / "frontend" / "src" / "components" / "ChatConversation.tsx"
    ).read_text(encoding="utf-8")
    assert "discoverMailboxEndpoints" in source
    assert "plugin.mailboxEndpoint" in source
    assert "...queried.map((endpoint) =>" in source
    assert "serverProtocol: endpoint.protocol" in source
    assert "mailboxApiBase(option)" in source
    for manifest_name in ("ws_collab", "mailbox_chat", "emullm"):
        manifest = json.loads(
            (ROOT / "workbench" / "plugins" / manifest_name / "plugin.json").read_text(encoding="utf-8"),
        )
        endpoint = manifest["mailboxEndpoint"]
        assert endpoint["path"].startswith("/"), manifest_name
        assert endpoint["protocol"] in ("ws_collab", "registry"), manifest_name


def test_web_proxy_rejects_targets_outside_manifest_allowlist() -> None:
    app_module = importlib.import_module("app")
    with TestClient(app_module.app) as client:
        # The manifest allowlist covers only 127.0.0.1; any other host is refused
        # before a connection is even attempted.
        response = client.get("/web_proxy/http/203.0.113.5:9999/health")
    assert response.status_code == 403
    assert "not allowed" in response.json()["error"]


def test_plugin_scan_policy_validation() -> None:
    app_module = importlib.import_module("app")
    with TestClient(app_module.app) as client:
        response = client.put("/workbench/plugins/web_proxy", json={"scan": "sometimes"})
    assert response.status_code == 400


def test_plugins_navigation_and_page_are_wired() -> None:
    source = (ROOT / "workbench" / "frontend" / "src" / "pages" / "FilesystemWorkbenchPage.tsx").read_text(encoding="utf-8")
    page = (ROOT / "workbench" / "frontend" / "src" / "components" / "PluginManagerPage.tsx").read_text(encoding="utf-8")
    assert 'group: "PLUGINS"' in source
    assert '{ label: "Plugins", view: "plugins"' in source
    assert 'view === "plugins" && <PluginManagerPage />' in source
    assert 'fetch(`/workbench/plugins${refresh ? "/refresh" : ""}`' in page
    assert '<option value="startup">Scan at startup</option>' in page
    assert '<option value="disabled">Disabled</option>' in page


def test_every_plugin_publishes_an_admin_link_the_scanner_reads_from_disk() -> None:
    app_module = importlib.import_module("app")
    with TestClient(app_module.app) as client:
        response = client.get("/workbench/plugins")
    assert response.status_code == 200
    payload = response.json()
    assert payload["manifestName"] == "plugin.json"
    for plugin in payload["plugins"]:
        assert plugin["adminPath"].startswith("/")
        assert plugin["adminApiPath"] == f"/workbench{plugin['adminPath']}"
        configure = [page for page in plugin["uiPages"] if page["kind"] in {"configure", "admin"}]
        assert configure, f"{plugin['id']} contributes no configure page"
        assert configure[0]["address"], f"{plugin['id']} configure page has no address"


def test_plugin_directory_never_overwrites_the_declared_admin_path() -> None:
    """The loader stores the plugin directory under 'path'; that must not win."""

    app_module = importlib.import_module("app")
    with TestClient(app_module.app) as client:
        plugins = {item["id"]: item for item in client.get("/workbench/plugins").json()["plugins"]}
    web_proxy = plugins["web_proxy"]
    assert web_proxy["adminPath"] == "/web_proxy/admin"
    assert Path(web_proxy["path"]).name == "web_proxy"


def test_ws_collab_resolves_its_own_pages_to_the_page_it_serves() -> None:
    app_module = importlib.import_module("app")
    with TestClient(app_module.app) as client:
        plugins = {item["id"]: item for item in client.get("/workbench/plugins").json()["plugins"]}
    ws_collab = plugins["ws_collab"]
    assert ws_collab["configPage"] == "http://127.0.0.1:5173/ws_collab/admin"
    for page in ws_collab["uiPages"]:
        assert page["external"] is True
        assert page["address"].startswith("http://127.0.0.1:5173/ws_collab/admin")


def test_plugin_init_mounts_the_requested_path_through_web_proxy() -> None:
    """ws_collab asks web_proxy to serve /ws_collab; the loader runs that command."""

    app_module = importlib.import_module("app")
    with TestClient(app_module.app) as client:
        plugins = {item["id"]: item for item in client.get("/workbench/plugins").json()["plugins"]}
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


def test_web_proxy_admin_page_is_served_on_the_api_port_and_under_workbench() -> None:
    app_module = importlib.import_module("app")
    with TestClient(app_module.app) as client:
        direct = client.get("/web_proxy/admin")
        mirrored = client.get("/workbench/web_proxy/admin")
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
        descriptor = client.get("/workbench/web_proxy/admin").json()
        initialized = client.post("/workbench/web_proxy/admin/initialize", json={})
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
            "/workbench/web_proxy/admin/settings", json={"values": {"requestTimeoutSeconds": -3}}
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
                "/workbench/web_proxy/admin/settings",
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


def test_lifecycle_phase_peeks_plugin_status_and_reports_liveness(monkeypatch) -> None:
    """Running a lifecycle phase verifies each participating plugin is alive by
    peeking at its status endpoint: the hook receives the verdict as
    ``statusPeek`` and the phase outcome carries it as ``status``."""

    plugin_api = importlib.import_module("plugin_api")

    seen: dict[str, object] = {}

    class FakeModule:
        @staticmethod
        def on_shutdown(notice: dict) -> str:
            seen.update(notice)
            return "done"

    item = {
        "id": "probed",
        "apiSections": {"status": {"address": "/probed/status"}},
        "plugin-lifecycle": {"standalone": True, "hooks": {"workbenchShutdown": "on_shutdown"}},
    }
    monkeypatch.setattr(
        plugin_api, "_peek_plugin_status",
        lambda entry: {"alive": True, "address": "/probed/status", "detail": "HTTP 200"},
    )

    outcome = plugin_api._call_lifecycle_hook(item, FakeModule, "workbenchShutdown", reason="test")

    assert outcome is not None and outcome["ok"] is True
    assert outcome["status"] == {"alive": True, "address": "/probed/status", "detail": "HTTP 200"}
    assert seen["statusPeek"] == {"alive": True, "address": "/probed/status", "detail": "HTTP 200"}


def test_peek_plugin_status_reports_dead_and_undeclared_plugins(monkeypatch) -> None:
    """The status peek answers alive=False when the endpoint cannot be reached
    (a standalone server that is down) and alive=None when the plugin declares
    no status surface at all — and never raises either way."""

    plugin_api = importlib.import_module("plugin_api")

    def refuse(url: str, timeout: float = 0):  # noqa: ARG001 - signature match
        raise OSError("connection refused")

    monkeypatch.setattr(plugin_api.urllib.request, "urlopen", refuse)
    dead = plugin_api._peek_plugin_status({
        "id": "downer",
        "apiSections": {"status": {"address": "/downer/status"}},
    })
    assert dead["alive"] is False
    assert "refused" in dead["detail"]

    monkeypatch.setattr(plugin_api, "_route_is_registered", lambda path: False)
    undeclared = plugin_api._peek_plugin_status({"id": "silent", "apiSections": {}})
    assert undeclared == {"alive": None, "address": None, "detail": "no status endpoint declared"}
