from __future__ import annotations

import json
from pathlib import Path

from task_library import legacy_catalog_view, load_shared_task_documents, load_workspace_task_records


def write_task(root: Path, workspace: str, filename: str, document: dict) -> None:
    directory = root / workspace / "tasks"
    directory.mkdir(parents=True, exist_ok=True)
    (directory / filename).write_text(json.dumps(document), encoding="utf-8")


def test_workspace_tasks_extend_and_override_defaults(tmp_path: Path) -> None:
    write_task(
        tmp_path,
        "default",
        "echo.json",
        {"id": "shared.echo", "implementation": "core.echo", "inputs": {"value": "Any"}, "outputs": {"value": "Any"}},
    )
    write_task(
        tmp_path,
        "default",
        "constant.json",
        {"id": "shared.constant", "implementation": "core.constant", "inputs": {}, "outputs": {"value": "Any"}},
    )
    write_task(
        tmp_path,
        "tic_tac_toe_learner",
        "echo.json",
        {"id": "shared.echo", "implementation": "python.callable", "inputs": {"value": "Any"}, "outputs": {"value": "Any"}},
    )
    write_task(
        tmp_path,
        "tic_tac_toe_learner",
        "legal_move.json",
        {"id": "tic_tac_toe.legal_move", "implementation": "python.callable", "inputs": {"board": "Array"}, "outputs": {"move": "Object"}},
    )

    records = load_workspace_task_records(
        tmp_path / "tic_tac_toe_learner",
        workspaces_root=tmp_path,
    )
    by_id = {record["document"]["id"]: record for record in records}

    assert set(by_id) == {"shared.echo", "shared.constant", "tic_tac_toe.legal_move"}
    assert by_id["shared.constant"]["source"] == "shared"
    assert by_id["shared.echo"]["source"] == "workspace"
    assert by_id["shared.echo"]["document"]["implementation"] == "python.callable"


def test_legacy_catalog_is_derived_from_filesystem_documents(tmp_path: Path) -> None:
    write_task(
        tmp_path,
        "default",
        "compare.json",
        {
            "id": "shared.compare",
            "label": "Compare Artifacts",
            "implementation": "artifact.compare",
            "inputs": {"left": "Any", "right": "Any"},
            "outputs": {"evidence": "Evidence"},
        },
    )

    documents = load_shared_task_documents(tmp_path)
    catalog = legacy_catalog_view(documents)

    assert catalog == [
        {
            "id": "shared.compare",
            "label": "Compare Artifacts",
            "ports": "left + right → evidence",
            "routes": "artifact.compare",
            "definition": documents[0],
        }
    ]
