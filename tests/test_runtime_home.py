from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
RUNTIME_PATH = ROOT / "scripts" / "_runtime.py"


def _load_runtime_module():
    spec = importlib.util.spec_from_file_location("arc3_script_runtime", RUNTIME_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _make_project_root(path: Path) -> Path:
    path.mkdir(parents=True)
    (path / "README.md").write_text("# test project\n", encoding="utf-8")
    (path / "pyproject.toml").write_text(
        "[project]\nname='test'\nversion='0'\n", encoding="utf-8"
    )
    return path.resolve()


def test_explicit_runtime_home_has_priority(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    runtime = _load_runtime_module()
    configured = _make_project_root(tmp_path / "configured")
    working = _make_project_root(tmp_path / "working")
    script_root = _make_project_root(tmp_path / "script-root")
    script = script_root / "scripts" / "demo.py"
    script.parent.mkdir()
    script.write_text("", encoding="utf-8")

    monkeypatch.setenv("ARC3_RUNTIME_HOME", str(configured))
    monkeypatch.chdir(working)

    selected = runtime.configure_runtime_home(script)

    assert selected == configured
    assert Path.cwd() == configured
    assert os.environ["ARC3_RUNTIME_HOME"] == str(configured)


def test_working_directory_is_checked_before_script_location(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    runtime = _load_runtime_module()
    working = _make_project_root(tmp_path / "working")
    nested_working = working / "nested" / "directory"
    nested_working.mkdir(parents=True)
    script_root = _make_project_root(tmp_path / "script-root")
    script = script_root / "scripts" / "demo.py"
    script.parent.mkdir()
    script.write_text("", encoding="utf-8")

    monkeypatch.delenv("ARC3_RUNTIME_HOME", raising=False)
    monkeypatch.chdir(nested_working)

    selected = runtime.configure_runtime_home(script)

    assert selected == working
    assert Path.cwd() == working


def test_script_location_is_final_fallback(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    runtime = _load_runtime_module()
    unrelated = tmp_path / "unrelated"
    unrelated.mkdir()
    script_root = _make_project_root(tmp_path / "script-root")
    script = script_root / "scripts" / "demo.py"
    script.parent.mkdir()
    script.write_text("", encoding="utf-8")

    monkeypatch.delenv("ARC3_RUNTIME_HOME", raising=False)
    monkeypatch.chdir(unrelated)

    selected = runtime.configure_runtime_home(script)

    assert selected == script_root
    assert Path.cwd() == script_root


def test_invalid_explicit_runtime_home_is_not_silently_ignored(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    runtime = _load_runtime_module()
    invalid = tmp_path / "invalid"
    invalid.mkdir()
    script_root = _make_project_root(tmp_path / "script-root")
    script = script_root / "scripts" / "demo.py"
    script.parent.mkdir()
    script.write_text("", encoding="utf-8")

    monkeypatch.setenv("ARC3_RUNTIME_HOME", str(invalid))

    with pytest.raises(RuntimeError, match="ARC3_RUNTIME_HOME"):
        runtime.configure_runtime_home(script)


def test_shared_pycharm_hook_uses_established_defaults(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime = _load_runtime_module()
    calls: list[dict[str, object]] = []
    fake_pydevd = SimpleNamespace(settrace=lambda **kwargs: calls.append(kwargs))
    monkeypatch.setitem(sys.modules, "pydevd_pycharm", fake_pydevd)

    assert runtime.hook_debugger(timeout=0.01, retry_interval=0.001)
    assert calls == [
        {
            "host": "localhost",
            "port": 5678,
            "suspend": True,
            "stdout_to_server": False,
            "stderr_to_server": False,
        }
    ]


def test_runtime_home_invokes_shared_debugger(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    runtime = _load_runtime_module()
    project_root = _make_project_root(tmp_path / "project")
    script = project_root / "scripts" / "demo.py"
    script.parent.mkdir()
    script.write_text("", encoding="utf-8")
    calls: list[bool] = []

    monkeypatch.setenv("ARC3_RUNTIME_HOME", str(project_root))
    monkeypatch.setattr(
        runtime, "configure_pycharm_debugger", lambda: calls.append(True) or False
    )

    assert runtime.configure_runtime_home(script) == project_root
    assert calls == [True]


def test_pytest_disables_debugger_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    runtime = _load_runtime_module()
    monkeypatch.delenv("ARC3_PYCHARM_DEBUG", raising=False)

    assert runtime.configure_pycharm_debugger() is False


def test_explicit_debug_setting_enables_shared_hook(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime = _load_runtime_module()
    received: list[dict[str, object]] = []
    monkeypatch.setenv("ARC3_PYCHARM_DEBUG", "1")
    monkeypatch.setattr(
        runtime,
        "hook_debugger",
        lambda **kwargs: received.append(kwargs) or True,
    )

    assert runtime.configure_pycharm_debugger() is True
    assert received == [
        {
            "host": "localhost",
            "port": 5678,
            "suspend": True,
            "timeout": 7.0,
            "retry_interval": 1.0,
            "wait_for_user_if_not_started": False,
        }
    ]


def test_every_runnable_script_uses_shared_runtime_resolver() -> None:
    scripts = sorted(
        path for path in (ROOT / "scripts").glob("*.py") if path.name != "_runtime.py"
    )
    assert scripts

    for script in scripts:
        source = script.read_text(encoding="utf-8")
        assert "from _runtime import configure_runtime_home" in source, script.name
        assert "configure_runtime_home(__file__)" in source, script.name
