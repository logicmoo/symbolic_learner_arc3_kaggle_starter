from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _batch(name: str) -> str:
    return (ROOT / "scripts" / name).read_text(encoding="utf-8")


def test_interactive_launcher_preserves_workspace_and_repairs_dependencies() -> None:
    source = _batch("interactive_runner.bat")

    assert 'set "ARC3_CALLER_CWD=%CD%"' in source
    assert 'set "ARC3_LAUNCH_CWD=%CD%"' in source
    assert 'for %%I in ("%~dp0..") do set "REPO_ROOT=%%~fI"' in source
    assert 'cd /d "%~dp0.."' not in source
    assert 'set "PYTHONHOME="' in source
    assert 'set "PYTHONPATH="' in source
    assert 'set "VENV_PYTHON=%REPO_ROOT%\\.venv\\Scripts\\python.exe"' in source
    assert '"%VENV_PYTHON%" -c "import json_repair"' in source
    assert 'pushd "%REPO_ROOT%"' in source
    assert '"%VENV_PYTHON%" -m pip install -e "."' in source
    assert '"%VENV_PYTHON%" -m pip install -e ".[all]"' in source
    assert "pip install -e '.[all]'" not in source
    assert '"%VENV_PYTHON%" "%REPO_ROOT%\\scripts\\interactive_runner.py" %*' in source


def test_windows_setup_sanitizes_python_paths_and_verifies_json_repair() -> None:
    source = _batch("setup_windows.bat")

    assert 'set "PYTHONHOME="' in source
    assert 'set "PYTHONPATH="' in source
    assert '"%VENV_PYTHON%" -m pip install -e ".[all]"' in source
    assert "pip install -e '.[all]'" not in source
    assert "import arc_agi, json_repair, numpy, PIL" in source


def test_missing_json_repair_message_is_copy_pasteable_on_windows() -> None:
    source = (ROOT / "python" / "llm_json.py").read_text(encoding="utf-8")

    assert '.venv\\Scripts\\python.exe -m pip install -e ".[all]"' in source
    assert "if os.name == \"nt\"" in source


def test_workbench_launchers_share_the_root_environment() -> None:
    launcher = (ROOT / "workbench" / "run_demo.bat").read_text(encoding="utf-8")
    api = (ROOT / "workbench" / "scripts" / "run_api_server.bat").read_text(encoding="utf-8")

    assert 'set "WORKBENCH_PYTHON=%REPO_ROOT%\\.venv\\Scripts\\python.exe"' in launcher
    assert 'set "PYTHON_EXE=%REPO_ROOT%\\.venv\\Scripts\\python.exe"' in api
    assert '"%REPO_ROOT%[all]"' in launcher
    assert ".venv-workbench" not in launcher + api
    assert "workbench\\.venv" not in launcher + api


def test_api_server_uses_explicit_batched_restarts() -> None:
    api = (ROOT / "workbench" / "scripts" / "run_api_server.bat").read_text(encoding="utf-8")
    runner = (ROOT / "workbench" / "scripts" / "run_api_server.py").read_text(encoding="utf-8")

    assert '"%ROOT%\\scripts\\run_api_server.py"' in api
    assert "reload=False" in runner
    assert "reload=True" not in runner
    assert "reload_dirs" not in runner
    assert "timeout_graceful_shutdown=5" in runner
    assert "_run_explicit_restart_supervisor" in runner
    assert "RESTART_EXIT_CODE = 75" in runner
    assert "WORKBENCH_API_SUPERVISED_WORKER" in runner
    assert "timeout_graceful_shutdown=5" in runner
