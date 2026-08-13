from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "workbench" / "server"
sys.path.insert(0, str(SERVER))

import service_monitor_api  # noqa: E402


def test_monitor_registers_real_service_routes() -> None:
    routes = {
        (route.path, method)
        for route in service_monitor_api.router.routes
        for method in (getattr(route, "methods", None) or [])
    }
    assert ("/system/services", "GET") in routes
    assert ("/system/services/{service_id}/{action}", "POST") in routes
    assert {item.id for item in service_monitor_api.MANAGED_SERVICES} == {
        "clawrouter", "omniroute", "freerouter",
        "channel-relay",
    }
    assert {item.port for item in service_monitor_api.MANAGED_SERVICES} == {3456, 20128, 18800, 46667}
    assert all(item.launcher and item.launcher.is_file() for item in service_monitor_api.MANAGED_SERVICES)


def test_service_payload_reports_listener_process_and_redacted_logs(monkeypatch) -> None:
    definition = next(item for item in service_monitor_api.MANAGED_SERVICES if item.id == "clawrouter")
    monkeypatch.setattr(service_monitor_api, "_health", lambda _port, _path: "healthy")
    monkeypatch.setattr(service_monitor_api, "_process_name", lambda _pid: "node.exe")
    monkeypatch.setattr(service_monitor_api, "_tail", lambda _path: "Authorization: Bearer secret-token")

    payload = service_monitor_api._service_payload(definition, {definition.port: 1234})

    assert payload["running"] is True
    assert payload["pid"] == 1234
    assert payload["processName"] == "node.exe"
    assert payload["launcher"].endswith("run_clawrouter.bat")
    assert "secret-token" not in service_monitor_api._redact(payload["stdout"])
    assert service_monitor_api._redact("\x1b[32mhealthy\x1b[0m") == "healthy"


def test_settings_ui_exposes_process_controls_and_log_streams() -> None:
    source = (ROOT / "workbench" / "frontend" / "src" / "components" / "WorkspaceSettingsPanel.tsx").read_text(encoding="utf-8")
    assert 'fetch("/api/system/services")' in source
    assert "Hidden-process monitor" in source
    assert "Recent stdout / stderr" in source
    assert ">Start<" in source
    assert ">Restart<" in source
    assert ">Stop<" in source
