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
    assert ("/system/services/{service_id}/processes/{pid}/{action}", "POST") in routes
    assert {item.id for item in service_monitor_api.MANAGED_SERVICES} == {
        "clawrouter", "omniroute",
        "mailbox_server",
    }
    assert {item.port for item in service_monitor_api.MANAGED_SERVICES} == {3456, 20128, 46667}
    router_services = [item for item in service_monitor_api.MANAGED_SERVICES if item.id in {"clawrouter", "omniroute"}]
    assert all(item.launcher and item.launcher.is_file() for item in router_services)


def test_service_payload_reports_listener_process_and_redacted_logs(monkeypatch) -> None:
    definition = next(item for item in service_monitor_api.MANAGED_SERVICES if item.id == "clawrouter")
    monkeypatch.setattr(service_monitor_api, "_health", lambda _port, _path: "healthy")
    monkeypatch.setattr(service_monitor_api, "_process_name", lambda _pid: "node.exe")
    monkeypatch.setattr(service_monitor_api, "_tail", lambda _path: "Authorization: Bearer secret-token")

    payload = service_monitor_api._service_payload(definition, {definition.port: 1234})

    assert payload["running"] is True
    assert payload["pid"] == 1234
    assert payload["processName"] == "node.exe"
    assert payload["processes"][0]["listener"] is True
    assert payload["launcher"].endswith("run_clawrouter.bat")
    assert "secret-token" not in service_monitor_api._redact(payload["stdout"])
    assert service_monitor_api._redact("\x1b[32mhealthy\x1b[0m") == "healthy"


def test_matching_processes_include_external_equivalent_and_redact_command(monkeypatch) -> None:
    definition = next(item for item in service_monitor_api.MANAGED_SERVICES if item.id == "omniroute")
    processes = [
        {"ProcessId": 7, "ParentProcessId": 1, "Name": "cmd.exe", "CommandLine": "launcher"},
        {"ProcessId": 41, "ParentProcessId": 7, "Name": "node.exe", "CommandLine": "node omniroute --port 20128 --token=secret-value"},
        {"ProcessId": 42, "Name": "python.exe", "CommandLine": "python unrelated.py"},
    ]

    monkeypatch.setattr(service_monitor_api, "_working_directory", lambda pid: f"C:/processes/{pid}")
    matches = service_monitor_api._matching_processes(definition, processes, None)

    assert [item["pid"] for item in matches] == [41]
    assert matches[0]["listener"] is False
    assert matches[0]["workingDirectory"] == "C:/processes/41"
    assert matches[0]["parentPid"] == 7
    assert matches[0]["parentProcessName"] == "cmd.exe"
    assert matches[0]["parentWorkingDirectory"] == "C:/processes/7"
    assert matches[0]["parentCommandLine"] == "launcher"
    assert "secret-value" not in matches[0]["commandLine"]


def test_workbench_api_matches_flask_processes_started_elsewhere() -> None:
    definition = service_monitor_api._definitions(8000)[0]
    matches = service_monitor_api._matching_processes(
        definition,
        [{"ProcessId": 73, "Name": "python.exe", "CommandLine": "python -m flask run --port 8000"}],
        None,
    )
    assert matches[0]["pid"] == 73


def test_external_matching_process_counts_as_running_without_listener(monkeypatch) -> None:
    definition = service_monitor_api._definitions(8000)[0]
    monkeypatch.setattr(service_monitor_api, "_port_open", lambda _port: False)
    payload = service_monitor_api._service_payload(
        definition, {},
        [{"ProcessId": 73, "Name": "python.exe", "CommandLine": "python -m flask run --port 9000"}],
    )
    assert payload["running"] is True
    assert payload["listening"] is False
    assert payload["status"] == "process detected"


def test_singleton_service_does_not_launch_when_matching_process_exists(monkeypatch) -> None:
    definition = service_monitor_api.ServiceDefinition(
        "demo", "Demo", "Demo service", 9123, "/health", ROOT / "demo.cmd", True,
        ("demo-server",), ROOT, True, True, True, False, True,
    )
    monkeypatch.setattr(service_monitor_api, "_port_open", lambda _port: False)
    monkeypatch.setattr(service_monitor_api, "_system_processes", lambda: [
        {"ProcessId": 41, "Name": "demo.exe", "CommandLine": "demo-server --other-port"},
    ])
    monkeypatch.setattr(service_monitor_api.subprocess, "Popen", lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("must not launch")))
    service_monitor_api._start(definition)


def test_settings_ui_exposes_process_controls_and_log_streams() -> None:
    source = (ROOT / "workbench" / "frontend" / "src" / "components" / "WorkspaceSettingsPanel.tsx").read_text(encoding="utf-8")
    assert '"/workbench/system/services?include_hidden=true":"/workbench/system/services"' in source
    assert "Hidden-process monitor" in source
    assert "Recent stdout / stderr" in source
    assert "MATCHING OS PROCESS" in source
    assert "<small>CWD</small>" in source
    assert "process-tree-parent-evidence" in source
    assert "parentProcessName" in source
    assert "ALWAYS-EXPANDED PARENT/CHILD TREE" in source
    assert "process-external-parent" in source
    assert "children.get(process.pid)" in source
    assert "ENOUGH INFORMATION TO RESTART" in source
    assert "parentCommandLine" in source
    assert "parentWorkingDirectory" in source
    assert "process-tree-parent-evidence" in source
    assert "process-parent-readiness" not in source
    styles = (ROOT / "workbench" / "frontend" / "src" / "styles" / "workbench.css").read_text(encoding="utf-8")
    assert ".process-tree-parent-evidence b,.process-tree-parent-evidence code,.process-tree-parent-evidence small,.process-tree-details code{overflow:visible;text-overflow:clip;white-space:normal" in styles
    assert "grid-template-columns:auto minmax(100px,.45fr) auto auto minmax(160px,.7fr) auto minmax(260px,1.3fr) auto" in styles
    assert ">Relaunch PID<" in source
    assert ">Stop PID only<" in source
    assert "Its parent and child processes will not be terminated" in source
    assert ">Start<" in source
    assert ">Restart<" in source
    assert ">Stop<" in source


def test_pid_kill_does_not_request_tree_termination(monkeypatch) -> None:
    recorded: list[str] = []
    monkeypatch.setattr(service_monitor_api.os, "name", "nt")
    monkeypatch.setattr(service_monitor_api.subprocess, "run", lambda command, **_kwargs: recorded.extend(command) or type("Completed", (), {"returncode": 0, "stderr": ""})())
    service_monitor_api._kill_pid(123)
    assert recorded == ["taskkill", "/PID", "123", "/F"]
    assert "/T" not in recorded
