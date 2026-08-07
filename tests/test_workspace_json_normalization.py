from __future__ import annotations

import importlib.util
import json
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "workbench" / "scripts" / "normalize_workspace_json.py"
spec = importlib.util.spec_from_file_location("normalize_workspace_json", SCRIPT)
assert spec and spec.loader
normalize_workspace_json = importlib.util.module_from_spec(spec)
spec.loader.exec_module(normalize_workspace_json)


def test_merge_json_values_keeps_canonical_scalars_and_unions_lists():
    legacy = {
        "label": "Legacy",
        "capabilities": ["llm.complete", "vision"],
        "configuration": {"timeoutSeconds": 900, "legacyOnly": True},
    }
    canonical = {
        "label": "Canonical",
        "capabilities": ["vision", "reasoning"],
        "configuration": {"timeoutSeconds": 300, "currentOnly": True},
    }

    merged = normalize_workspace_json.merge_json_values(legacy, canonical)

    assert merged["label"] == "Canonical"
    assert merged["capabilities"] == ["llm.complete", "vision", "reasoning"]
    assert merged["configuration"] == {
        "timeoutSeconds": 300,
        "legacyOnly": True,
        "currentOnly": True,
    }


def test_normalize_file_merges_existing_canonical_target_and_removes_legacy(tmp_path: Path):
    workspace = tmp_path / "shared"
    models = workspace / "models"
    models.mkdir(parents=True)

    legacy = models / "backend_openai.json"
    canonical = models / "openai.backend.json"
    legacy.write_text(
        json.dumps(
            {
                "kind": "backend",
                "id": "openai",
                "label": "OpenAI API",
                "provider": "openai",
                "official": True,
                "capabilities": ["llm.complete"],
                "configuration": {"adapter": "openai_responses", "timeoutSeconds": 900},
            }
        ),
        encoding="utf-8",
    )
    canonical.write_text(
        json.dumps(
            {
                "kind": "backend",
                "id": "openai",
                "label": "OpenAI",
                "provider": "openai",
                "capabilities": ["llm", "reasoning"],
                "configuration": {"defaultModel": "gpt-5.6", "timeoutSeconds": 300},
            }
        ),
        encoding="utf-8",
    )

    original_root = normalize_workspace_json.WORKSPACES
    normalize_workspace_json.WORKSPACES = tmp_path
    try:
        changed, messages = normalize_workspace_json.normalize_file(legacy, write=True)
    finally:
        normalize_workspace_json.WORKSPACES = original_root

    assert changed is True
    assert not legacy.exists()
    assert canonical.exists()
    merged = json.loads(canonical.read_text(encoding="utf-8"))
    assert merged["label"] == "OpenAI"
    assert merged["official"] is True
    assert merged["capabilities"] == ["llm.complete", "llm", "reasoning"]
    assert merged["configuration"] == {
        "adapter": "openai_responses",
        "timeoutSeconds": 300,
        "defaultModel": "gpt-5.6",
    }
    assert any("merge duplicate" in message for message in messages)


def test_normalize_file_refuses_to_merge_different_ids(tmp_path: Path):
    workspace = tmp_path / "shared"
    tasks = workspace / "tasks"
    tasks.mkdir(parents=True)

    legacy = tasks / "wrong_name.json"
    canonical = tasks / "task_a.task.json"
    legacy.write_text(json.dumps({"kind": "task", "id": "task_a"}), encoding="utf-8")
    canonical.write_text(json.dumps({"kind": "task", "id": "task_b"}), encoding="utf-8")

    original_root = normalize_workspace_json.WORKSPACES
    normalize_workspace_json.WORKSPACES = tmp_path
    try:
        changed, messages = normalize_workspace_json.normalize_file(legacy, write=True)
    finally:
        normalize_workspace_json.WORKSPACES = original_root

    assert changed is False
    assert legacy.exists()
    assert canonical.exists()
    assert any("refusing to merge different resource ids" in message for message in messages)
