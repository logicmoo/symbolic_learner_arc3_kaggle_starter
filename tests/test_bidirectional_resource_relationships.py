from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKSPACES = ROOT / "workbench" / "workspaces"

FAMILIES = {
    "goal_variant": "goal",
    "plan_variant": "plan",
    "operation_implementation": "operation",
    "prompt_implementation": "prompt",
    "datatype_representation": "datatype",
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
        family = FAMILIES.get(child.get("kind"))
        if not family:
            continue
        parent_kind = family
        parent_ids = child.get("parents")
        assert isinstance(parent_ids, list) and parent_ids, f"{child['id']}.parents must be a non-empty array"
        for parent_id in parent_ids:
            parent = by_id[parent_id]
            assert parent["kind"] == parent_kind
            backlinks = parent.get("children")
            assert isinstance(backlinks, list), f"{parent_id}.children must be an array"
            assert child["id"] in backlinks, f"{parent_id}.children is missing {child['id']}"
            checked += 1

    for child_kind, parent_kind in FAMILIES.items():
        for parent in (document for document in documents if document.get("kind") == parent_kind):
            child_ids = parent.get("children", [])
            assert isinstance(child_ids, list), f"{parent['id']}.children must be an array"
            for child_id in child_ids:
                child = by_id[child_id]
                assert child["kind"] == child_kind
                assert parent["id"] in child["parents"], f"{child_id}.parents is missing {parent['id']}"

    assert checked >= 29
