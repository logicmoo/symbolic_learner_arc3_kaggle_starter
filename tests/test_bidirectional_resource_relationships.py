from __future__ import annotations

from pathlib import Path

from resource_store import get_filesystem_provider


ROOT = Path(__file__).resolve().parents[1]
WORKSPACES = ROOT / "workbench" / "workspaces"

FAMILIES = {
    "representation_datatype": "semantic_datatype",
    "concrete_datatype": "representation_datatype",
    "model_policy_variant": "model_policy",
}


def test_all_variant_relationships_are_plural_and_bidirectional() -> None:
    documents: list[dict] = []
    resources = get_filesystem_provider()
    for path in resources.rglob(WORKSPACES, "*.metta"):
        try:
            loaded = resources.read_json_documents(path.with_suffix(".json"))
        except (OSError, ValueError):
            continue
        documents.extend(
            document for document in loaded
            if isinstance(document, dict) and document.get("kind") and document.get("id")
        )

    by_id: dict[str, list[dict]] = {}
    for document in documents:
        by_id.setdefault(document["id"], []).append(document)
    checked = 0
    for child in documents:
        parent_ids = child.get("parents")
        if parent_ids is None:
            continue
        assert isinstance(parent_ids, list) and parent_ids, f"{child['id']}.parents must be a non-empty array"
        for parent_id in parent_ids:
            expected_parent_kind = FAMILIES.get(child.get("kind"), child.get("kind"))
            allowed_parent_kinds = {expected_parent_kind}
            if child.get("kind") == "semantic_datatype":
                allowed_parent_kinds.add("semantic_datatype")
            if child.get("kind") == "model":
                # Concrete models inherit transport/configuration from a backend;
                # model presets inherit another model. Both links remain explicit
                # and bidirectional in the unified model catalog.
                allowed_parent_kinds.add("backend")
            parent = next(
                (candidate for candidate in by_id[parent_id] if candidate.get("kind") in allowed_parent_kinds),
                None,
            )
            assert parent is not None, f"{parent_id} has no parent resource of kind {sorted(allowed_parent_kinds)}"
            backlinks = parent.get("children")
            assert isinstance(backlinks, list), f"{parent_id}.children must be an array"
            assert child["id"] in backlinks, f"{parent_id}.children is missing {child['id']}"
            checked += 1

    for parent in documents:
        child_ids = parent.get("children", [])
        assert isinstance(child_ids, list), f"{parent['id']}.children must be an array"
        for child_id in child_ids:
            matching_children = [
                child for child in by_id[child_id]
                if parent["id"] in (child.get("parents") or [])
            ]
            assert matching_children, f"{child_id}.parents is missing {parent['id']}"

    assert checked >= 45
