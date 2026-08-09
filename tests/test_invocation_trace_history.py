from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "workbench" / "server"
sys.path.insert(0, str(SERVER))

from invocation_trace import list_invocation_traces, write_invocation_trace  # noqa: E402
from resource_store import get_filesystem_provider  # noqa: E402


def test_lists_newest_invocation_traces_and_skips_malformed_files(tmp_path: Path) -> None:
    first = write_invocation_trace(tmp_path, "model", "alpha", "model_invocation_trace", {"status": "completed", "modelId": "alpha"})
    second = write_invocation_trace(tmp_path, "model", "beta", "model_invocation_trace", {"status": "failed", "modelId": "beta"})
    get_filesystem_provider().write_text(tmp_path / "runtime" / "logs" / "model_invocations" / "broken.log", "not json")

    rows = list_invocation_traces(tmp_path, "model")

    assert [row["modelId"] for row in rows] == ["beta", "alpha"]
    assert [row["logPath"] for row in rows] == [second, first]
    assert all(row["kind"] == "model_invocation_trace" for row in rows)


def test_invocation_history_honors_limit(tmp_path: Path) -> None:
    for name in ("one", "two", "three"):
        write_invocation_trace(tmp_path, "operation", name, "operation_invocation_trace", {"status": "completed", "operationId": name})

    rows = list_invocation_traces(tmp_path, "operation", limit=2)

    assert len(rows) == 2
    assert rows[0]["operationId"] == "three"
    assert json.loads(get_filesystem_provider().read_text(tmp_path / rows[0]["logPath"]))["id"] == rows[0]["id"]
