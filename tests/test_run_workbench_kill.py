from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "workbench" / "scripts"))

import stop_workbench  # noqa: E402


def test_run_workbench_kill_switch_routes_to_scoped_shutdown_helper() -> None:
    launcher = (ROOT / "run_workbench.bat").read_text(encoding="utf-8")
    assert 'if /I "%~1"=="/kill"' in launcher
    assert "stop_workbench.py" in launcher
    assert '--web-port "!KILL_WEB_PORT!" --api-port "!KILL_API_PORT!"' in launcher


def test_shutdown_targets_only_declared_workbench_listener_ports(monkeypatch) -> None:
    monkeypatch.setattr(stop_workbench, "PROCESS_LEDGER", ROOT / "does-not-exist.json")
    assert stop_workbench.stop_targets(17777, 16666) == 0

    source = (ROOT / "workbench" / "scripts" / "stop_workbench.py").read_text(encoding="utf-8")
    for port in (3456, 20128, 46667):
        assert f", {port}," in source
    assert ", 18800," not in source
    assert '["taskkill", "/PID", str(pid), "/T", "/F"]' in source
    assert '"python.exe"' not in source
    assert '"node.exe"' not in source


def test_launcher_routes_mailbox_relay_through_startup_policy_and_pid_ledger() -> None:
    demo = (ROOT / "workbench" / "run_demo.bat").read_text(encoding="utf-8")
    starter = (ROOT / "workbench" / "scripts" / "start_with_policy.py").read_text(encoding="utf-8")
    assert "--service mailbox_server" in demo
    assert "mailbox-server.cmd" in demo
    assert "PROCESS_LEDGER" in starter
    assert "_record_started_process(args.service, process, list(args.command), args.cwd)" in starter
    assert '"rawCommand": command' in starter
    assert '"terminationScope": "process-tree"' in starter
    service = (ROOT / "workbench" / "workspaces" / "shared_library_system" / "design" / "services" / "channel_relay.managed_service.metta").read_text(encoding="utf-8")
    policy = (ROOT / "workbench" / "workspaces" / "shared_library_system" / "policies" / "workbench_startup.workbench_startup_policy.metta").read_text(encoding="utf-8")
    assert "(defaultStartup ((start true)" in service
    assert "(mailbox_server ((start true)" in policy


def test_every_long_running_demo_service_uses_the_python_process_launcher() -> None:
    demo = (ROOT / "workbench" / "run_demo.bat").read_text(encoding="utf-8")
    for service in (
        "mailbox_server", "clawrouter", "omniroute",
        "workbench-api", "workbench-web",
    ):
        assert f'"%ROOT%scripts\\start_with_policy.py" --service {service}' in demo
    assert "--service freerouter" not in demo
    assert demo.count('-- "%ComSpec%" /d /c') == 5
    assert demo.count('--cwd "%ROOT%."') == 5
    assert '--cwd "%ROOT%"' not in demo


def test_managed_batch_files_submit_expanded_final_commands_to_api() -> None:
    expected = {
        "run_clawrouter.bat": ("--service clawrouter", "npx.cmd --yes @blockrun/clawrouter --port %CLAWROUTER_PORT%"),
        "run_omniroute.bat": ("--service omniroute", "serve --port %OMNIROUTE_PORT%"),
        "run_vite_server.bat": ("--service workbench-web", "npm.cmd run dev"),
        "run_channel_relay.bat": ("--service mailbox_server", "-m mailbox_channels.server"),
    }
    scripts = ROOT / "workbench" / "scripts"
    for filename, fragments in expected.items():
        source = (scripts / filename).read_text(encoding="utf-8")
        assert "submit_managed_command.py" in source
        for fragment in fragments:
            assert fragment in source

    api = (scripts / "run_api_server.bat").read_text(encoding="utf-8")
    assert "Bootstrap legacy mode" in api


def test_api_startup_reconciles_enabled_missing_daemons(monkeypatch) -> None:
    sys.path.insert(0, str(ROOT / "workbench" / "server"))
    import service_monitor_api

    enabled = service_monitor_api.ServiceDefinition("enabled", "Enabled", "", 31001, "/", Path("launcher.bat"), True)
    running = service_monitor_api.ServiceDefinition("running", "Running", "", 31002, "/", Path("launcher.bat"), True)
    disabled = service_monitor_api.ServiceDefinition("disabled", "Disabled", "", 31003, "/", Path("launcher.bat"), True)
    api = service_monitor_api.ServiceDefinition("workbench-api", "API", "", 8000, "/")
    web = service_monitor_api.ServiceDefinition("workbench-web", "Web", "", 5173, "/")
    monkeypatch.setattr(service_monitor_api, "_definitions", lambda _port: (enabled, running, disabled, api, web))
    monkeypatch.setattr(service_monitor_api, "_startup_policy", lambda: {
        "enabled": {"start": True}, "running": {"start": True}, "disabled": {"start": False},
        "workbench-api": {"start": True}, "workbench-web": {"start": True},
    })
    monkeypatch.setattr(service_monitor_api, "_port_open", lambda port: port == 31002)
    started = []
    monkeypatch.setattr(service_monitor_api, "_start", lambda definition: started.append(definition.id))
    results = service_monitor_api.reconcile_startup_services()
    assert started == ["enabled"]
    assert {item["serviceId"]: item["status"] for item in results} == {
        "enabled": "launch-requested", "running": "already-running", "disabled": "disabled",
    }


def test_api_launch_ledger_uses_unique_temp_files_and_deduplicates_pending_requests() -> None:
    monitor = (ROOT / "workbench" / "server" / "service_monitor_api.py").read_text(encoding="utf-8")
    starter = (ROOT / "workbench" / "scripts" / "start_with_policy.py").read_text(encoding="utf-8")
    assert "_PENDING_LAUNCHES" in monitor
    assert '"status": "launch-pending"' in monitor
    assert "with _LAUNCH_LOCK:" in monitor
    assert "get_ident()" in monitor
    assert "get_ident()" in starter
    assert 'with_suffix(".tmp")' not in monitor
    assert 'with_suffix(".tmp")' not in starter


def test_api_submitted_commands_forward_only_service_allowlisted_environment() -> None:
    monitor = (ROOT / "workbench" / "server" / "service_monitor_api.py").read_text(encoding="utf-8")
    assert "_validated_environment" in monitor
    assert '"omniroute": {"PORT", "DASHBOARD_PORT"}' in monitor
    assert '"workbench-web": {"WORKBENCH_WEB_HOST", "WORKBENCH_WEB_PORT", "WORKBENCH_API_TARGET"}' in monitor
    assert '"mailbox_server": {"PYTHONPATH"}' in monitor
    assert "env={**os.environ, **environment}" in monitor
    demo = (ROOT / "workbench" / "run_demo.bat").read_text(encoding="utf-8")
    assert demo.count("wait_for_managed_service.py") == 3
    waiter = (ROOT / "workbench" / "scripts" / "wait_for_managed_service.py").read_text(encoding="utf-8")
    assert "exited before becoming healthy" in waiter
