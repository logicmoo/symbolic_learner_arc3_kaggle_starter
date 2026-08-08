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
SHARED = ROOT / "workbench" / "workspaces" / "shared"


def test_shared_query_categories_are_valid_and_tree_scoped() -> None:
    records = load_workspace_artifact_categories(SHARED)
    assert {record["document"]["id"] for record in records} >= {
        "filtered.prolog",
        "models.vision",
        "models.large_context",
        "models.local",
        "models.openai",
    }
    assert all(record["document"]["trees"] for record in records)


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
