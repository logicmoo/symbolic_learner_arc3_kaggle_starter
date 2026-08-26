from pathlib import Path
import json

from resource_relationships import implements_resource, specializes_resource, synchronize_implementation_backlinks
from resource_store import FilesystemProvider


def test_synchronizes_added_and_removed_parent_backlinks(tmp_path: Path) -> None:
    resources = FilesystemProvider()
    first = tmp_path / "design" / "models" / "first.backend.json"
    second = tmp_path / "design" / "models" / "second.backend.json"
    resources.write_json(first, {"kind": "backend", "id": "first", "specializations": specializes_resource("child")})
    resources.write_json(second, {"kind": "backend", "id": "second"})

    result = synchronize_implementation_backlinks(
        tmp_path,
        {"kind": "model", "id": "child", "implements": implements_resource("second")},
        {"kind": "model", "id": "child", "implements": implements_resource("first")},
        resources,
    )

    assert result == {"updated": ["first", "second"], "unresolved": []}
    assert resources.read_json(first)["specializations"] == {}
    assert resources.read_json(second)["specializations"] == specializes_resource("child")


def test_does_not_mutate_parent_outside_edited_workspace(tmp_path: Path) -> None:
    resources = FilesystemProvider()
    workspace = tmp_path / "project"
    shared_parent = tmp_path / "shared" / "design" / "models" / "shared.backend.json"
    resources.write_json(shared_parent, {"kind": "backend", "id": "shared-parent", "specializations": {}})

    result = synchronize_implementation_backlinks(
        workspace,
        {"kind": "model", "id": "child", "implements": implements_resource("shared-parent")},
        None,
        resources,
    )

    assert result == {"updated": [], "unresolved": ["shared-parent"]}
    assert resources.read_json(shared_parent)["specializations"] == {}


def test_replaces_only_parent_entity_in_multi_resource_metta(tmp_path: Path) -> None:
    resources = FilesystemProvider()
    catalog = tmp_path / "design" / "models" / "catalog.backend.json"
    resources.write_text(
        catalog,
        json.dumps(
            [
                {"kind": "backend", "id": "parent"},
                {"kind": "backend", "id": "neighbor", "label": "Keep me"},
            ]
        ),
    )

    synchronize_implementation_backlinks(
        tmp_path,
        {"kind": "model", "id": "child", "implements": implements_resource("parent")},
        None,
        resources,
    )

    documents = resources.read_json_documents(catalog)
    assert documents[0]["specializations"] == specializes_resource("child")
    assert documents[1] == {"kind": "backend", "id": "neighbor", "label": "Keep me"}
