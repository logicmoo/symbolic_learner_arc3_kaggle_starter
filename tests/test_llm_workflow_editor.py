from __future__ import annotations

import json
from pathlib import Path

from llm_workflow_editor import (
    EXAMPLE_PATH,
    ensure_example_workflow,
    load_example_workflow,
)

ROOT = Path(__file__).resolve().parents[1]


def test_example_workflow_matches_staged_artifact_process() -> None:
    example = load_example_workflow()

    assert example["id"] == "example_multistep_artifact_review"
    assert [step["transaction"] for step in example["steps"]] == [
        "extract_scene_objects",
        "explain_object_changes",
        "prolog_render_symbolic_evidence",
        "induce_rules_from_prolog",
        "audit_artifact_bundle",
    ]
    assert example["steps"][0]["profile"] == "openai-gpt-5.6-light"
    assert example["steps"][1]["profile"] == "groq-qwen-3.6-27b-deep"
    assert example["steps"][3]["profile"] == "openrouter-north-mini-code-rules"
    assert example["steps"][-1]["continue_on_error"] is True


def test_ensure_example_is_idempotent() -> None:
    raw = {"llm_workflows": []}

    assert ensure_example_workflow(raw) is True
    assert ensure_example_workflow(raw) is False
    assert len(raw["llm_workflows"]) == 1


def test_example_file_is_valid_json() -> None:
    parsed = json.loads(EXAMPLE_PATH.read_text(encoding="utf-8"))
    assert parsed == load_example_workflow()


def test_interactive_launcher_installs_workflow_gui() -> None:
    text = (ROOT / "scripts" / "interactive_runner.py").read_text(encoding="utf-8")

    assert "install_workflow_editor_ui" in text
    assert "install_workflow_ui" not in text
