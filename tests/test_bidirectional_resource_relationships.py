from __future__ import annotations

from pathlib import Path

from resource_store import get_filesystem_provider


ROOT = Path(__file__).resolve().parents[1]
WORKSPACES = ROOT / "workbench" / "workspaces"

IMPLEMENTED_KIND_BY_CHILD = {
    "representation_datatype": "semantic_datatype",
    "concrete_datatype": "representation_datatype",
    "model_policy_variant": "model_policy",
}


def test_all_resource_relationships_are_bidirectional_and_canonical() -> None:
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
        legacy_fields = {
            "children",
            "parents",
            "inherits",
            "specializations",
            "preferredSpecialization",
        } & document.keys()
        assert not legacy_fields, f"{document['id']} still declares legacy relationship fields: {sorted(legacy_fields)}"
        by_id.setdefault(document["id"], []).append(document)
    implementation_checked = 0
    inheritance_checked = 0
    dependency_checked = 0
    for child in documents:
        implemented_ids = child.get("implements")
        if implemented_ids is None:
            continue
        assert isinstance(implemented_ids, dict) and implemented_ids, f"{child['id']}.implements must be a non-empty map"
        for implemented_id in implemented_ids:
            assert child["implements"][implemented_id] == {}
            expected_kind = IMPLEMENTED_KIND_BY_CHILD.get(child.get("kind"), child.get("kind"))
            allowed_kinds = {expected_kind}
            if child.get("kind") == "semantic_datatype":
                allowed_kinds.add("semantic_datatype")
            if child.get("kind") == "model":
                allowed_kinds.add("backend")
            implemented = next(
                (
                    candidate
                    for candidate in by_id.get(implemented_id, [])
                    if candidate.get("kind") in allowed_kinds
                    and child["id"] in (candidate.get("implementedBy") or {})
                ),
                None,
            )
            assert implemented is not None, f"{implemented_id} has no implemented resource of kind {sorted(allowed_kinds)}"
            backlinks = implemented.get("implementedBy")
            assert isinstance(backlinks, dict), f"{implemented_id}.implementedBy must be a map"
            assert child["id"] in backlinks, f"{implemented_id}.implementedBy is missing {child['id']}"
            assert backlinks[child["id"]] == {}
            implementation_checked += 1

    for parent in documents:
        implementation_map = parent.get("implementedBy", {})
        assert isinstance(implementation_map, dict), f"{parent['id']}.implementedBy must be a map"
        preferred = parent.get("preferredImplementation")
        if preferred:
            assert preferred in implementation_map, f"{parent['id']}.preferredImplementation is not declared"

    for child in documents:
        for inherited_id, request in (child.get("inheritsFrom") or {}).items():
            assert isinstance(request.get("borrow"), list)
            assert isinstance(request.get("exclude"), list)
            inherited = next(
                (
                    candidate
                    for candidate in by_id.get(inherited_id, [])
                    if child["id"] in (candidate.get("inheritedBy") or {})
                ),
                None,
            )
            assert inherited is not None, f"{inherited_id} has no inherited resource"
            grant = (inherited.get("inheritedBy") or {}).get(child["id"])
            assert isinstance(grant, dict), f"{inherited_id}.inheritedBy is missing {child['id']}"
            assert isinstance(grant.get("lend"), list)
            assert isinstance(grant.get("withhold"), list)
            inheritance_checked += 1

    for dependency in documents:
        for dependent_id, policy in (dependency.get("dependedOnBy") or {}).items():
            assert policy == {}
            matching_dependents = [
                dependent for dependent in by_id.get(dependent_id, [])
                if dependency["id"] in (dependent.get("dependsOn") or {})
            ]
            assert matching_dependents, f"{dependent_id}.dependsOn is missing {dependency['id']}"
            dependency_checked += 1

    for inherited in documents:
        for child_id, policy in (inherited.get("inheritedBy") or {}).items():
            assert isinstance(policy.get("lend"), list)
            assert isinstance(policy.get("withhold"), list)
            assert "id" in policy["withhold"]
            assert {"label", "description"} <= set(policy["withhold"])
            matching_children = [
                child for child in by_id.get(child_id, [])
                if inherited["id"] in (child.get("inheritsFrom") or {})
            ]
            assert matching_children, f"{child_id}.inheritsFrom is missing {inherited['id']}"

    assert implementation_checked >= 45
    assert inheritance_checked >= 45
    assert dependency_checked >= 45
