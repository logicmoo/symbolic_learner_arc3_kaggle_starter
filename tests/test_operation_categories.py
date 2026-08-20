from pathlib import Path

from resource_store import get_filesystem_provider


ROOT = Path(__file__).resolve().parents[1]
WORKSPACES = ROOT / "workbench" / "workspaces"


def test_every_operation_has_at_least_one_valid_category_path() -> None:
    resources = get_filesystem_provider()
    operations = list(WORKSPACES.glob("*/design/operations/*.operation.metta"))
    assert operations
    for path in operations:
        payload = resources.read_json(path.with_suffix(".json"))
        documents = payload if isinstance(payload, list) else [payload]
        for document in documents:
            categories = document.get("categories")
            assert isinstance(categories, list) and categories, (path, document.get("id"))
            assert all(isinstance(category, str) and category.strip(" /") for category in categories), (path, document.get("id"))


def test_titlecase_llm_implementation_is_a_sample_llm() -> None:
    path = WORKSPACES / "shared_library_system" / "design" / "operations" / "echo_into_titlecased_llm.operation.metta"
    document = get_filesystem_provider().read_json(path)
    assert document["kind"] == "operation"
    assert document["parents"] == ["echo_into_titlecased"]
    assert "sample/llm" in document["categories"]


def test_subject_matter_sets_resolve_participating_operations() -> None:
    from artifact_category_library import apply_artifact_categories, load_workspace_artifact_categories
    from operation_library import DEFAULT_WORKSPACES_ROOT, load_workspace_operation_records

    root = DEFAULT_WORKSPACES_ROOT / "shared_library_system"
    categories = {str((r.get("document") or {}).get("id")) for r in load_workspace_artifact_categories(root)}
    assert {"subjects.segmentation", "subjects.vision", "subjects.object_identity", "subjects.world_modeling"} <= categories

    applied = apply_artifact_categories(
        load_workspace_operation_records(root),
        load_workspace_artifact_categories(root),
        "operations",
    )
    declared = {
        str(r["document"]["id"]): set(r["document"].get("subjects") or [])
        for r in applied if r.get("document")
    }
    resolved = {
        str(r["document"]["id"]): {c["path"] for c in (r.get("resolvedArtifactCategories") or [])}
        for r in applied if r.get("document")
    }

    # An operation participates in subject-matter sets independently of how it executes.
    assert {"segmentation", "world-modeling"} <= declared["shared.extract_entities"]
    # Segmentation is not inherently visual: extract_entities is not in the vision set.
    assert "vision" not in declared["shared.extract_entities"]
    assert declared["shared.assign_identities"] == {"object-identity"}

    # The set resources attach their path to every participating operation.
    assert "subjects/segmentation" in resolved["shared.extract_entities"]
    assert "subjects/world-modeling" in resolved["shared.extract_entities"]
    assert "subjects/vision" not in resolved["shared.extract_entities"]
    assert "subjects/object-identity" in resolved["shared.assign_identities"]
    assert "subjects/vision" in resolved["vision.object_analysis"]
    # A single operation can belong to multiple subject-matter sets.
    assert {"subjects/segmentation", "subjects/vision"} <= resolved["vision.extract_scene_objects"]
