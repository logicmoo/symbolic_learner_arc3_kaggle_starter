from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKSPACES = ROOT / "workbench" / "workspaces"

FAMILIES = {
    "goal_variant": "goal",
    "plan_variant": "plan",
    "context_variant": "context",
    "operation_implementation": "operation",
    "prompt_implementation": "prompt",
    "representation_datatype": "semantic_datatype",
    "concrete_datatype": "representation_datatype",
    "model_policy_variant": "model_policy",
}


def test_all_variant_relationships_are_plural_and_bidirectional() -> None:
    documents: list[dict] = []
    for path in WORKSPACES.rglob("*.json"):
        try:
            document = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(document, dict) and document.get("kind") and document.get("id"):
            documents.append(document)

    by_id = {document["id"]: document for document in documents}
    checked = 0
    for child in documents:
        parent_ids = child.get("parents")
        if parent_ids is None:
            continue
        assert isinstance(parent_ids, list) and parent_ids, f"{child['id']}.parents must be a non-empty array"
        for parent_id in parent_ids:
            parent = by_id[parent_id]
            expected_parent_kind = FAMILIES.get(child.get("kind"), child.get("kind"))
            allowed_parent_kinds = {expected_parent_kind}
            if child.get("kind") == "semantic_datatype":
                allowed_parent_kinds.add("semantic_datatype")
            assert parent["kind"] in allowed_parent_kinds
            backlinks = parent.get("children")
            assert isinstance(backlinks, list), f"{parent_id}.children must be an array"
            assert child["id"] in backlinks, f"{parent_id}.children is missing {child['id']}"
            checked += 1

    for parent in documents:
        child_ids = parent.get("children", [])
        assert isinstance(child_ids, list), f"{parent['id']}.children must be an array"
        for child_id in child_ids:
            child = by_id[child_id]
            assert parent["id"] in child["parents"], f"{child_id}.parents is missing {parent['id']}"

    assert checked >= 45
