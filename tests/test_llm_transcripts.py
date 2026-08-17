from __future__ import annotations

import json
import os
import time
from pathlib import Path

from action_tree import ActionTreeStore
from llm_readme_patch import install_llm_readme_patch
from llm_transcripts import (
    LlmTranscriptRun,
    RESTORABLE_ARTIFACTS,
    restore_transcript,
    save_transcript,
    transcript_metadata,
)


def _store_and_node(tmp_path: Path):
    store = ActionTreeStore(tmp_path / "trees", "ls20", 1)
    node = store.create_initial(
        b"not-a-real-png-but-stable-for-the-store",
        {
            "state": "NOT_FINISHED",
            "step_count": 0,
            "observation": {},
        },
    )
    return store, node


def _run(path: Path, *, provider: str, model: str, level: int, tokens: int):
    return LlmTranscriptRun(
        path=path,
        metadata={
            "transcript_version": 1,
            "provider_id": provider,
            "provider_label": provider.title(),
            "adapter": "openai_responses",
            "model": model,
            "base_url": "http://127.0.0.1:8888/v1",
            "analysis_level": level,
            "analysis_profile": {"name": "extreme", "tokens": tokens},
            "max_output_tokens": tokens,
            "reasoning": {"effort": "high"},
            "started_at": "2026-08-04T00:00:00+00:00",
            "completed_at": "2026-08-04T00:03:00+00:00",
            "game_id": "ls20",
            "level": "1",
            "state": "NOT_FINISHED",
            "step_count": 0,
            "incoming_action": "initial",
            "action_data": {},
            "action_path": [],
            "image_hash": "abc123",
            "node_path": str(path.parent),
            "prompt_sections": ["system_contract", "object_analysis"],
        },
        request_input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": "# Prompt heading\n\nExplain the state exactly.",
                    }
                ],
            }
        ],
        required_keys=("new_identities", "objects_pl", "rules_pl"),
        raw_response='{"new_identities":[],"objects_pl":"object(a).","rules_pl":"rule(a)."}',
        normalized_response=(
            '{\n  "new_identities": [],\n  "objects_pl": "object(a).",\n'
            '  "rules_pl": "rule(a)."\n}\n'
        ),
        elapsed_seconds=173.0,
        repair_method="strict_json",
        status="complete",
    )


def test_transcript_is_artifact_first_and_response_last(tmp_path: Path) -> None:
    store, node = _store_and_node(tmp_path)
    path = node.path / (
        "llm_adapter_openai_responses_unsloth_gemma-4-E2B-it-GGUF_"
        "L4_extreme_tokens_32000_20260804T000000Z.md"
    )
    run = _run(
        path,
        provider="unsloth",
        model="unsloth/gemma-4-E2B-it-GGUF",
        level=4,
        tokens=32000,
    )
    artifacts = {
        "object_registry.pl": "object_identity(a, cell, 'a').\n",
        "objects.pl": "object(a).\n",
        "rules.pl": "rule(a).\n",
    }

    save_transcript(run, artifacts=artifacts)
    text = path.read_text(encoding="utf-8")

    assert text.index("### `objects.pl`") < text.index("# Debug transcript")
    assert "<!-- ARC3_LLM_PROMPT_BEGIN -->\n# Prompt heading" in text
    assert "```text\n# Prompt heading" not in text
    assert text.rfind("### Initial raw response") > text.index("## Initial request sent")
    assert text.rstrip().endswith("````")
    assert run.raw_response in text
    metadata = transcript_metadata(path)
    assert metadata["provider_id"] == "unsloth"
    assert metadata["analysis_level"] == 4


def test_restore_transcript_rewrites_latest_artifacts_and_provenance(
    tmp_path: Path,
) -> None:
    store, node = _store_and_node(tmp_path)
    path = node.path / "llm_adapter_openai_responses_unsloth_old_L2_demo_tokens_12000.md"
    run = _run(path, provider="unsloth", model="old-model", level=2, tokens=12000)
    artifacts = {
        "object_registry.pl": "object_identity(old_cell, cell, 'old cell').\n",
        "objects.pl": "old_object(old_cell).\n",
        "rules.pl": "old_rule(old_cell).\n",
    }
    save_transcript(run, artifacts=artifacts)

    store.object_registry_path.write_text("new registry\n", encoding="utf-8")
    (node.path / "objects.pl").write_text("new objects\n", encoding="utf-8")
    (node.path / "rules.pl").write_text("new rules\n", encoding="utf-8")

    restored = restore_transcript(store, node, path)

    assert store.object_registry_path.read_text(encoding="utf-8") == artifacts["object_registry.pl"]
    assert (node.path / "objects.pl").read_text(encoding="utf-8") == artifacts["objects.pl"]
    assert (node.path / "rules.pl").read_text(encoding="utf-8") == artifacts["rules.pl"]
    provenance = json.loads((node.path / "llm_provider.json").read_text(encoding="utf-8"))
    assert provenance["model"] == "old-model"
    assert provenance["analysis_level"] == 2
    assert provenance["prompt_sections"] == ["system_contract", "object_analysis"]
    assert provenance["source_node"] == str(node.path)
    assert provenance["restored_from_transcript"] == path.name
    assert node.path / "objects.pl" in restored
    readme = node.readme_path.read_text(encoding="utf-8")
    assert "## LLM provider output" in readme
    assert "`Unsloth` (`unsloth`)" in readme
    assert "`old-model`" in readme
    assert "`system_contract, object_analysis`" in readme
    assert str(node.path) in readme
    assert "**Restored transcript:**" in readme


def test_readme_links_all_transcripts_but_embeds_only_latest_artifacts(
    tmp_path: Path,
) -> None:
    install_llm_readme_patch()
    store, node = _store_and_node(tmp_path)

    older = node.path / "llm_adapter_openai_responses_openai_model_L2_demo_tokens_12000.md"
    newer = node.path / "llm_adapter_openai_responses_unsloth_model_L4_extreme_tokens_32000.md"
    failed = node.path / "llm_adapter_openai_responses_unsloth_failed_L4_extreme_tokens_32000.md"

    save_transcript(
        _run(older, provider="openai", model="model-a", level=2, tokens=12000),
        artifacts={"objects.pl": "from_openai.\n"},
    )
    save_transcript(
        _run(newer, provider="unsloth", model="model-b", level=4, tokens=32000),
        artifacts={"objects.pl": "from_unsloth.\n"},
    )
    failed_run = _run(failed, provider="unsloth", model="failed", level=4, tokens=32000)
    failed_run.status = "failed"
    failed_run.error = "bad output"
    save_transcript(failed_run)

    now = time.time()
    os.utime(older, (now - 20, now - 20))
    os.utime(newer, (now - 10, now - 10))
    os.utime(failed, (now, now))

    store.refresh_readme(node)
    readme = node.readme_path.read_text(encoding="utf-8")

    assert "## LLM comparison transcripts" in readme
    assert older.name in readme
    assert newer.name in readme
    assert failed.name in readme
    assert f"[`{newer.name}`]({newer.name})" in readme
    assert f"[`{failed.name}`]({failed.name}) **(active)**" not in readme
    assert f"<summary><code>{older.name}</code></summary>" not in readme
    assert f"<summary><code>{newer.name}</code></summary>" not in readme
    assert "`debug-only`" in readme


def test_declared_artifact_order_is_stable() -> None:
    assert RESTORABLE_ARTIFACTS[0] == "object_registry.pl"
    assert RESTORABLE_ARTIFACTS[-1] == "rules.pl"
