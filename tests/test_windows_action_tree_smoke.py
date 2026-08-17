from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.skipif(sys.platform != "win32", reason="native Windows smoke")
def test_native_windows_smoke_resolves_paths_and_records_one_node(tmp_path: Path) -> None:
    output_root = tmp_path / "recorded tree"
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "windows_action_tree_smoke.py"),
            "--output-root",
            str(output_root),
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout.strip().splitlines()[-1])
    assert Path(payload["repositoryRoot"]).resolve() == ROOT.resolve()
    assert Path(payload["pythonRoot"]).resolve() == (ROOT / "python").resolve()
    for field in ("state", "image", "readme"):
        assert Path(payload[field]).is_file()
    state = json.loads(Path(payload["state"]).read_text(encoding="utf-8"))
    assert state["state"] == "SMOKE_READY"
    assert state["observation"]["source"] == "native_windows_smoke"
    readme = Path(payload["readme"]).read_text(encoding="utf-8")
    assert "windows_smoke" in readme
    assert "Identity registry provenance" in readme
