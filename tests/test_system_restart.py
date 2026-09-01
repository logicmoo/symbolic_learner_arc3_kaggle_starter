from __future__ import annotations

from pathlib import Path

import system_control_api


def test_restart_trigger_touches_only_api_marker(
    tmp_path: Path, monkeypatch,
) -> None:
    api_marker = tmp_path / "api.py"
    web_marker = tmp_path / "vite.config.ts"
    api_marker.write_text("api", encoding="utf-8")
    web_marker.write_text("vite", encoding="utf-8")
    before_api = api_marker.stat().st_mtime_ns
    before_web = web_marker.stat().st_mtime_ns
    monkeypatch.setattr(system_control_api.time, "sleep", lambda _seconds: None)

    system_control_api.trigger_api_restart(api_marker)

    assert api_marker.stat().st_mtime_ns >= before_api
    assert web_marker.stat().st_mtime_ns == before_web


def test_supervised_restart_exits_worker_with_restart_code(
    tmp_path: Path, monkeypatch,
) -> None:
    marker = tmp_path / "restart.request"
    exits: list[int] = []
    monkeypatch.setenv("WORKBENCH_API_SUPERVISED_WORKER", "1")
    monkeypatch.setattr(system_control_api.time, "sleep", lambda _seconds: None)
    monkeypatch.setattr(system_control_api.os, "_exit", exits.append)

    system_control_api.trigger_api_restart(marker)

    assert marker.is_file()
    assert exits == [75]


def test_restart_claim_debounces_multiple_tabs(
    tmp_path: Path, monkeypatch,
) -> None:
    marker = tmp_path / "api_restart.request"
    monkeypatch.setattr(system_control_api.time, "time", lambda: 100.0)
    assert system_control_api._claim_api_restart(marker) is True
    system_control_api.os.utime(marker, (100.0, 100.0))
    assert system_control_api._claim_api_restart(marker) is False


def test_restart_endpoint_is_registered_in_active_app() -> None:
    routes = {
        (route.path, method)
        for route in system_control_api.router.routes
        for method in (getattr(route, "methods", None) or [])
    }
    assert ("/system/restart", "POST") in routes
    assert ("/system/presence", "POST") in routes
    assert ("/system/presence", "GET") in routes
    assert ("/system/restart-pending", "POST") in routes
    assert ("/system/resource-provider", "GET") in routes
    assert system_control_api.INSTANCE_ID


def test_workbench_presence_registry_tracks_and_removes_tabs() -> None:
    assert system_control_api._PRESENCE_TTL_SECONDS == 60.0
    with system_control_api._workbench_presence_lock:
        system_control_api._workbench_presence.clear()

    first = system_control_api.report_workbench_presence({
        "tabId": "tab-a",
        "workspaceId": "workspace-a",
        "pageId": "videoImport",
        "href": "http://localhost/?view=videoImport",
        "active": True,
        "seenAt": 123,
    })
    system_control_api.report_workbench_presence({
        "tabId": "tab-b",
        "workspaceId": "workspace-b",
        "pageId": "models",
        "active": True,
        "seenAt": 456,
    })

    assert first["accepted"] is True
    assert len(system_control_api.list_workbench_presence()["workbenches"]) == 2
    removed = system_control_api.report_workbench_presence({"tabId": "tab-a", "active": False})
    assert [entry["tabId"] for entry in removed["workbenches"]] == ["tab-b"]


def test_restart_pending_registry_is_shared_with_presence() -> None:
    pending = system_control_api.report_restart_pending({
        "active": True,
        "reason": "workers active",
        "changes": ["scheduler update"],
    })
    assert pending["restartPending"]["reason"] == "workers active"
    assert system_control_api.list_workbench_presence()["restartPending"]["changes"] == ["scheduler update"]
    cleared = system_control_api.report_restart_pending({"active": False})
    assert cleared["restartPending"] is None


def test_resource_provider_status_exposes_migration_metrics() -> None:
    payload = system_control_api.resource_provider_status()
    assert payload["provider"] == "FilesystemProvider"
    assert isinstance(payload["metrics"], dict)
