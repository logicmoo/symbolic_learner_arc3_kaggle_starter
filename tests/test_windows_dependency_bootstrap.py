from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _batch(name: str) -> str:
    return (ROOT / "scripts" / name).read_text(encoding="utf-8")


def test_interactive_launcher_uses_isolated_venv_and_repairs_core_dependencies() -> None:
    source = _batch("interactive_runner.bat")

    assert 'set "PYTHONHOME="' in source
    assert 'set "PYTHONPATH="' in source
    assert 'set "VENV_PYTHON=%CD%\\.venv\\Scripts\\python.exe"' in source
    assert '"%VENV_PYTHON%" -c "import json_repair"' in source
    assert '"%VENV_PYTHON%" -m pip install -e "."' in source
    assert '.venv\\Scripts\\python.exe -m pip install -e ".[all]"' in source
    assert "pip install -e '.[all]'" not in source
    assert '"%VENV_PYTHON%" ".\\scripts\\interactive_runner.py" %*' in source


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
