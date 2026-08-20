from pathlib import Path

from resource_store import get_filesystem_provider


ROOT = Path(__file__).resolve().parents[1]
WORKSPACES = ROOT / "workbench" / "workspaces"


def test_every_operation_has_at_least_one_topic() -> None:
    resources = get_filesystem_provider()
    operations = list(WORKSPACES.glob("*/design/operations/*.operation.metta"))
    assert operations
    for path in operations:
        payload = resources.read_json(path.with_suffix(".json"))
        documents = payload if isinstance(payload, list) else [payload]
        for document in documents:
            topics = document.get("topics")
            assert isinstance(topics, list) and topics, (path, document.get("id"))
            assert all(isinstance(topic, str) and topic.strip(" /") for topic in topics), (path, document.get("id"))
            # Topics are flat, top-level matters (converted from the old category paths).
            assert all("/" not in topic for topic in topics), (path, document.get("id"))


def test_titlecase_llm_implementation_is_a_sample_topic() -> None:
    path = WORKSPACES / "shared_library_system" / "design" / "operations" / "echo_into_titlecased_llm.operation.metta"
    document = get_filesystem_provider().read_json(path)
    assert document["kind"] == "operation"
    assert document["parents"] == ["echo_into_titlecased"]
    assert "sample-demos" in document["topics"]


def test_topic_sets_resolve_participating_operations() -> None:
    from artifact_category_library import apply_artifact_categories, load_workspace_artifact_categories
    from operation_library import DEFAULT_WORKSPACES_ROOT, load_workspace_operation_records

    root = DEFAULT_WORKSPACES_ROOT / "shared_library_system"
    category_ids = {str((r.get("document") or {}).get("id")) for r in load_workspace_artifact_categories(root)}
    assert {"topics.segmentation", "topics.vision", "topics.object_identity", "topics.world_modeling"} <= category_ids

    applied = apply_artifact_categories(
        load_workspace_operation_records(root),
        load_workspace_artifact_categories(root),
        "operations",
    )
    declared = {
        str(r["document"]["id"]): set(r["document"].get("topics") or [])
        for r in applied if r.get("document")
    }
    resolved = {
        str(r["document"]["id"]): {c["path"] for c in (r.get("resolvedArtifactCategories") or [])}
        for r in applied if r.get("document")
    }

    # A topic is declared independently of how the operation executes.
    assert {"segmentation", "world-modeling"} <= declared["shared.extract_entities"]
    # Segmentation is not inherently visual: extract_entities is not in the vision topic.
    assert "vision" not in declared["shared.extract_entities"]
    assert "object-identity" in declared["shared.assign_identities"]

    # The topic set resources attach their bare, top-level path to each member operation.
    assert {"segmentation", "world-modeling"} <= resolved["shared.extract_entities"]
    assert "vision" not in resolved["shared.extract_entities"]
    assert "object-identity" in resolved["shared.assign_identities"]
    assert "vision" in resolved["vision.object_analysis"]
    # A single operation can belong to multiple topics.
    assert {"segmentation", "vision"} <= resolved["vision.extract_scene_objects"]
