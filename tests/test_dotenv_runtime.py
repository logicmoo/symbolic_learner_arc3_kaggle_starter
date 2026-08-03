from __future__ import annotations

import importlib.util
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_PATH = ROOT / "scripts" / "_runtime.py"


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
    script = path / "scripts" / "demo.py"
    script.parent.mkdir()
    script.write_text("", encoding="utf-8")
    return path.resolve(), script


def test_runtime_loads_project_dotenv_without_overriding_shell(
    tmp_path: Path, monkeypatch
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
    monkeypatch.delenv("ARC3_RUNTIME_HOME", raising=False)
    monkeypatch.delenv("ARC3_LLM_PROVIDER", raising=False)
    monkeypatch.delenv("ARC3_UNSLOTH_API_KEY", raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "from-shell")
    monkeypatch.setenv("ARC3_PYCHARM_DEBUG", "0")

    assert runtime.configure_runtime_home(script) == project
    assert os.environ["ARC3_LLM_PROVIDER"] == "unsloth"
    assert os.environ["ARC3_UNSLOTH_API_KEY"] == "sk-unsloth-from-dotenv"
    assert os.environ["OPENAI_API_KEY"] == "from-shell"
