from __future__ import annotations

from pathlib import Path

from resource_store import get_filesystem_provider


ROOT = Path(__file__).resolve().parents[1]
WORKSPACES = ROOT / "workbench" / "workspaces"

IMPLEMENTED_KIND_BY_SPECIALIZATION = {
    "representation_datatype": "semantic_datatype",
    "concrete_datatype": "representation_datatype",
    "model_policy_variant": "model_policy",
}


def test_all_specialization_relationships_are_plural_bidirectional_and_canonical() -> None:
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
        legacy_fields = {"children", "parents", "inherits"} & document.keys()
        assert not legacy_fields, f"{document['id']} still declares legacy relationship fields: {sorted(legacy_fields)}"
        by_id.setdefault(document["id"], []).append(document)
    checked = 0
    for specialization in documents:
        implemented_ids = specialization.get("implements")
        if implemented_ids is None:
            continue
        assert isinstance(specialization.get("implements"), dict) and implemented_ids, f"{specialization['id']}.implements must be a non-empty policy map"
        for implemented_id in implemented_ids:
            request = specialization["implements"][implemented_id]
            assert isinstance(request.get("borrow"), list)
            assert isinstance(request.get("exclude"), list)
            expected_kind = IMPLEMENTED_KIND_BY_SPECIALIZATION.get(specialization.get("kind"), specialization.get("kind"))
            allowed_kinds = {expected_kind}
            if specialization.get("kind") == "semantic_datatype":
                allowed_kinds.add("semantic_datatype")
            if specialization.get("kind") == "model":
                # Concrete models implement a backend's transport/configuration;
                # model presets implement another model. Both links remain explicit
                # and bidirectional in the unified model catalog.
                allowed_kinds.add("backend")
            implemented = next(
                (candidate for candidate in by_id.get(implemented_id, []) if candidate.get("kind") in allowed_kinds),
                None,
            )
            assert implemented is not None, f"{implemented_id} has no implemented resource of kind {sorted(allowed_kinds)}"
            backlinks = implemented.get("specializations")
            assert isinstance(backlinks, dict), f"{implemented_id}.specializations must be a policy map"
            assert specialization["id"] in backlinks, f"{implemented_id}.specializations is missing {specialization['id']}"
            checked += 1

    for implemented in documents:
        specialization_map = implemented.get("specializations", {})
        assert isinstance(specialization_map, dict), f"{implemented['id']}.specializations must be a policy map"
        preferred = implemented.get("preferredSpecialization")
        if preferred:
            assert preferred in specialization_map, f"{implemented['id']}.preferredSpecialization is not declared"
        for specialization_id, policy in specialization_map.items():
            assert isinstance(policy.get("lend"), list)
            assert isinstance(policy.get("withhold"), list)
            assert "id" in policy["withhold"]
            assert {"label", "description"} <= set(policy["withhold"])
            matching_specializations = [
                specialization for specialization in by_id.get(specialization_id, [])
                if implemented["id"] in (specialization.get("implements") or [])
            ]
            assert matching_specializations, f"{specialization_id}.implements is missing {implemented['id']}"

    assert checked >= 45
