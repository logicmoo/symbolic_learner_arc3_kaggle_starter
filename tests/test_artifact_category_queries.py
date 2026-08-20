from pathlib import Path

import pytest

from artifact_category_library import (
    apply_artifact_categories,
    load_workspace_artifact_categories,
    validate_artifact_category,
)
from model_library import resolve_model_records
from operation_library import load_workspace_operation_implementation_records


ROOT = Path(__file__).resolve().parents[1]
SHARED = ROOT / "workbench" / "workspaces" / "shared_library_system"


def test_shared_query_categories_are_valid_and_tree_scoped() -> None:
    records = load_workspace_artifact_categories(SHARED)
    by_id = {record["document"]["id"]: record["document"] for record in records}
    assert set(by_id) >= {
        "filtered.prolog",
        "models.free",
        "models.vision",
        "models.large_context",
        "models.local",
    }
    assert all(record["document"]["trees"] for record in records)
    assert set(by_id["filtered.prolog"]["trees"]) == {"operations", "prompts"}
    assert by_id["models.free"]["path"] == "filtered/free"
    for category_id in ("models.free", "models.vision", "models.large_context", "models.local"):
        assert by_id[category_id]["parentMode"] == "hide"
        assert by_id[category_id]["path"].startswith("filtered/")
        assert "/models/" not in by_id[category_id]["path"]


def test_incompatible_query_kind_and_tree_is_rejected() -> None:
    with pytest.raises(ValueError, match="incompatible"):
        validate_artifact_category({
            "kind": "artifact_category",
            "id": "bad",
            "path": "filtered/bad",
            "trees": ["goals"],
            "query": {"kinds": ["model"], "where": {}},
        })


def test_prolog_query_adds_resolved_membership_without_mutating_source() -> None:
    categories = load_workspace_artifact_categories(SHARED)
    source = load_workspace_operation_implementation_records(SHARED)
    resolved = apply_artifact_categories(source, categories, "operations")
    prolog = next(record for record in resolved if record["document"]["id"] == "echo_into_titlecased_prolog")
    original = next(record for record in source if record["document"]["id"] == "echo_into_titlecased_prolog")
    assert "filtered/prolog" in prolog["document"]["categories"]
    assert "filtered/prolog" not in original["document"].get("categories", [])
    assert prolog["resolvedArtifactCategories"][0]["parentMode"] == "show"


def test_prolog_query_is_available_to_prompt_resources() -> None:
    categories = load_workspace_artifact_categories(SHARED)
    resolved = apply_artifact_categories([{
        "document": {"kind": "prompt", "id": "prolog_prompt", "implementation": "prolog.source"},
    }], categories, "prompts")
    assert {"id": "filtered.prolog", "path": "filtered/prolog", "parentMode": "show"} in resolved[0]["resolvedArtifactCategories"]


def test_model_examples_resolve_real_matches() -> None:
    categories = load_workspace_artifact_categories(SHARED)
    records = [{
        "document": {
            "kind": "model",
            "id": "example-vision-model",
            "capabilities": ["vision"],
            "properties": {"context_length": 131072},
        },
        "resolved": {"backendId": "unsloth"},
    }]
    resolved = apply_artifact_categories(records, categories, "models")
    memberships = {entry["id"] for record in resolved for entry in record.get("resolvedArtifactCategories", [])}
    assert {"models.vision", "models.large_context", "models.local"} <= memberships


def test_free_model_category_matches_the_router_resource() -> None:
    categories = load_workspace_artifact_categories(SHARED)
    resolved = apply_artifact_categories([{
        "document": {"kind": "model", "id": "openrouter-free", "model": "openrouter/free"},
    }], categories, "models")
    memberships = resolved[0]["resolvedArtifactCategories"]
    assert {"id": "models.free", "path": "filtered/free", "parentMode": "hide"} in memberships


def test_resource_topic_buckets_tag_by_kind_and_flag_todo() -> None:
    categories = load_workspace_artifact_categories(SHARED)

    def tags(kind: str, tree: str, **extra: object) -> set[str]:
        record = {"document": {"kind": kind, "id": "x", **extra}}
        resolved = apply_artifact_categories([record], categories, tree)
        return {entry["path"] for entry in (resolved[0].get("resolvedArtifactCategories") or [])}

    assert {"datatypes", "todo-needs-categorization"} <= tags("semantic_datatype", "datatypes")
    assert {"prompts", "todo-needs-categorization"} <= tags("prompt", "prompts")
    assert {"models", "todo-needs-categorization"} <= tags("model", "models")
    # Systems are bucketed and additionally split by runtime provider.
    assert {"systems", "systems/systems-python", "todo-needs-categorization"} <= tags("system", "models", provider="python")
    assert {"systems", "systems/systems-prolog", "todo-needs-categorization"} <= tags("system", "models", provider="prolog")
    # A provider without a dedicated bucket still lands in systems + todo.
    python_only = tags("system", "models", provider="codex")
    assert "systems" in python_only and "todo-needs-categorization" in python_only
    assert not any(path.startswith("systems/") for path in python_only)
