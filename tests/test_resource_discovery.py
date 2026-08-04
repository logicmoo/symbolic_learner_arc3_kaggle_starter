from __future__ import annotations

import importlib.util
import os
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
RUNTIME_PATH = ROOT / "scripts" / "_runtime.py"
_RUNTIME_ENV_NAMES = (
    "ARC3_RUNTIME_HOME",
    "ARC3_CODE_ROOT",
    "ARC3_LAUNCH_CWD",
    "ARC3_CONFIG_ROOT",
    "ARC3_LLM_CONFIG",
    "ARC3_TREE_ROOT",
    "ARC3_CONFIG_SOURCE",
    "ARC3_TREE_SOURCE",
    "ARC3_ENV_FILES",
    "ARC3_SHOW_PATHS",
    "ARC3_PYCHARM_DEBUG",
)


@pytest.fixture(autouse=True)
def _clean_environment(monkeypatch: pytest.MonkeyPatch):
    for name in _RUNTIME_ENV_NAMES:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("ARC3_PYCHARM_DEBUG", "0")


def _runtime_module():
    spec = importlib.util.spec_from_file_location(
        f"arc3_runtime_{id(object())}",
        RUNTIME_PATH,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _project(path: Path, *, resources: bool = True) -> Path:
    path.mkdir(parents=True)
    (path / "README.md").write_text("# project\n", encoding="utf-8")
    (path / "pyproject.toml").write_text(
        "[project]\nname='test'\nversion='0'\n",
        encoding="utf-8",
    )
    if resources:
        _workspace_resources(path)
    return path.resolve()


def _workspace_resources(path: Path) -> tuple[Path, Path]:
    config = path / "config"
    config.mkdir(parents=True, exist_ok=True)
    config_file = config / "llm_providers.json"
    config_file.write_text(
        '{"prompt_text":{"base":["x"]},"llm_providers":[]}',
        encoding="utf-8",
    )
    trees = path / "action_trees"
    trees.mkdir(parents=True, exist_ok=True)
    return config_file.resolve(), trees.resolve()


def _script(root: Path) -> Path:
    script = root / "scripts" / "demo.py"
    script.parent.mkdir(exist_ok=True)
    script.write_text("", encoding="utf-8")
    return script


def test_launch_workspace_resources_override_script_checkout(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime = _runtime_module()
    script_root = _project(tmp_path / "code")
    script = _script(script_root)
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    config_file, trees = _workspace_resources(workspace)
    launch = workspace / "jobs" / "experiment-a"
    launch.mkdir(parents=True)
    monkeypatch.chdir(launch)

    code_root = runtime.configure_runtime_home(script)

    assert code_root == script_root
    assert Path(os.environ["ARC3_LAUNCH_CWD"]) == launch
    assert Path(os.environ["ARC3_LLM_CONFIG"]) == config_file
    assert Path(os.environ["ARC3_TREE_ROOT"]) == trees
    assert os.environ["ARC3_CONFIG_SOURCE"] == "launch directory config search"
    assert os.environ["ARC3_TREE_SOURCE"] == "launch directory action_trees search"


def test_runtime_home_without_resources_uses_launch_workspace_first(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime = _runtime_module()
    runtime_root = _project(tmp_path / "runtime", resources=False)
    script_root = _project(tmp_path / "code")
    script = _script(script_root)
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    config_file, trees = _workspace_resources(workspace)
    monkeypatch.setenv("ARC3_RUNTIME_HOME", str(runtime_root))
    monkeypatch.chdir(workspace)

    code_root = runtime.configure_runtime_home(script)

    assert code_root == runtime_root
    assert Path(os.environ["ARC3_LLM_CONFIG"]) == config_file
    assert Path(os.environ["ARC3_TREE_ROOT"]) == trees


def test_missing_launch_and_runtime_resources_fall_back_to_script_checkout(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime = _runtime_module()
    runtime_root = _project(tmp_path / "runtime", resources=False)
    script_root = _project(tmp_path / "code")
    script = _script(script_root)
    unrelated = tmp_path / "unrelated" / "deep"
    unrelated.mkdir(parents=True)
    monkeypatch.setenv("ARC3_RUNTIME_HOME", str(runtime_root))
    monkeypatch.chdir(unrelated)

    code_root = runtime.configure_runtime_home(script)

    assert code_root == runtime_root
    assert Path(os.environ["ARC3_LLM_CONFIG"]) == (
        script_root / "config" / "llm_providers.json"
    )
    assert Path(os.environ["ARC3_TREE_ROOT"]) == script_root / "action_trees"
    assert os.environ["ARC3_CONFIG_SOURCE"] == "script/code config"
    assert os.environ["ARC3_TREE_SOURCE"] == "script/code action_trees"


def test_startup_reports_config_and_action_tree_locations(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    runtime = _runtime_module()
    script_root = _project(tmp_path / "code")
    script = _script(script_root)
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    config_file, trees = _workspace_resources(workspace)
    monkeypatch.chdir(workspace)
    monkeypatch.setenv("ARC3_SHOW_PATHS", "1")

    runtime.configure_runtime_home(script)
    output = capsys.readouterr().out

    assert "ARC3 resolved paths" in output
    assert f"Launch directory: {workspace}" in output
    assert f"Code/runtime root: {script_root}" in output
    assert f"LLM config source: {config_file}" in output
    assert f"Action-tree output: {trees}" in output
