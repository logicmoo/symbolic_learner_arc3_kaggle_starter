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


def test_restart_endpoint_is_registered_in_active_app() -> None:
    routes = {
        (route.path, method)
        for route in system_control_api.router.routes
        for method in (getattr(route, "methods", None) or [])
    }
    assert ("/system/restart", "POST") in routes
    assert ("/system/resource-provider", "GET") in routes
    assert system_control_api.INSTANCE_ID


def test_resource_provider_status_exposes_migration_metrics() -> None:
    payload = system_control_api.resource_provider_status()
    assert payload["provider"] == "FilesystemProvider"
    assert isinstance(payload["metrics"], dict)
