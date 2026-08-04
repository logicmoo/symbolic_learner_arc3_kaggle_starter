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
)


@pytest.fixture(autouse=True)
def _clean_runtime_environment(monkeypatch: pytest.MonkeyPatch):
    for name in _RUNTIME_ENV_NAMES:
        monkeypatch.delenv(name, raising=False)
    yield
    for name in _RUNTIME_ENV_NAMES:
        os.environ.pop(name, None)


def _load_runtime_module():
    spec = importlib.util.spec_from_file_location("arc3_dotenv_runtime", RUNTIME_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _make_project(path: Path) -> tuple[Path, Path]:
    path.mkdir(parents=True)
    (path / "README.md").write_text("# test project\n", encoding="utf-8")
    (path / "pyproject.toml").write_text(
        "[project]\nname='test'\nversion='0'\n",
        encoding="utf-8",
    )
    config = path / "config"
    config.mkdir()
    (config / "llm_providers.json").write_text("{}\n", encoding="utf-8")
    (path / "action_trees").mkdir()
    script = path / "scripts" / "demo.py"
    script.parent.mkdir()
    script.write_text("", encoding="utf-8")
    return path.resolve(), script


def test_runtime_loads_project_dotenv_without_overriding_shell(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    runtime = _load_runtime_module()
    project, script = _make_project(tmp_path / "project")
    (project / ".env").write_text(
        "ARC3_LLM_PROVIDER=unsloth\n"
        "ARC3_UNSLOTH_API_KEY=sk-unsloth-from-dotenv\n"
        "OPENAI_API_KEY=from-dotenv\n",
        encoding="utf-8",
    )

    monkeypatch.chdir(project)
    monkeypatch.delenv("ARC3_LLM_PROVIDER", raising=False)
    monkeypatch.delenv("ARC3_UNSLOTH_API_KEY", raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "from-shell")
    monkeypatch.setenv("ARC3_PYCHARM_DEBUG", "0")

    assert runtime.configure_runtime_home(script) == project
    assert os.environ["ARC3_LLM_PROVIDER"] == "unsloth"
    assert os.environ["ARC3_UNSLOTH_API_KEY"] == "sk-unsloth-from-dotenv"
    assert os.environ["OPENAI_API_KEY"] == "from-shell"
    assert Path(os.environ["ARC3_LLM_CONFIG"]) == project / "config" / "llm_providers.json"
    assert Path(os.environ["ARC3_TREE_ROOT"]) == project / "action_trees"
    assert str(project / ".env") in os.environ["ARC3_ENV_FILES"]
