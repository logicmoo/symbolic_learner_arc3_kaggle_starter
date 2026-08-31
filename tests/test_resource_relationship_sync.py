from pathlib import Path
import json

from resource_relationships import (
    depended_on_by_resource,
    depends_on_resource,
    implemented_by_resource,
    implements_resource,
    inherited_by_resource,
    inherits_from_resource,
    synchronize_dependency_backlinks,
    synchronize_inheritance_backlinks,
    synchronize_implementation_backlinks,
)
from resource_store import FilesystemProvider


def test_synchronizes_added_and_removed_parent_backlinks(tmp_path: Path) -> None:
    resources = FilesystemProvider()
    first = tmp_path / "design" / "models" / "first.backend.json"
    second = tmp_path / "design" / "models" / "second.backend.json"
    resources.write_json(first, {"kind": "backend", "id": "first", "implementedBy": implemented_by_resource("child")})
    resources.write_json(second, {"kind": "backend", "id": "second"})

    result = synchronize_implementation_backlinks(
        tmp_path,
        {"kind": "model", "id": "child", "implements": implements_resource("second")},
        {"kind": "model", "id": "child", "implements": implements_resource("first")},
        resources,
    )

    assert result == {"updated": ["first", "second"], "unresolved": []}
    assert resources.read_json(first)["implementedBy"] == {}
    assert resources.read_json(second)["implementedBy"] == implemented_by_resource("child")


def test_does_not_mutate_parent_outside_edited_workspace(tmp_path: Path) -> None:
    resources = FilesystemProvider()
    workspace = tmp_path / "project"
    shared_parent = tmp_path / "shared" / "design" / "models" / "shared.backend.json"
    resources.write_json(shared_parent, {"kind": "backend", "id": "shared-parent", "implementedBy": {}})

    result = synchronize_implementation_backlinks(
        workspace,
        {"kind": "model", "id": "child", "implements": implements_resource("shared-parent")},
        None,
        resources,
    )

    assert result == {"updated": [], "unresolved": ["shared-parent"]}
    assert resources.read_json(shared_parent)["implementedBy"] == {}


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
    assert documents[0]["implementedBy"] == implemented_by_resource("child")
    assert documents[1] == {"kind": "backend", "id": "neighbor", "label": "Keep me"}


def test_synchronizes_added_and_removed_dependency_backlinks(tmp_path: Path) -> None:
    resources = FilesystemProvider()
    first = tmp_path / "design" / "systems" / "first.system.json"
    second = tmp_path / "design" / "systems" / "second.system.json"
    resources.write_json(
        first,
        {
            "kind": "system",
            "id": "first",
            "dependedOnBy": depended_on_by_resource("consumer"),
        },
    )
    resources.write_json(second, {"kind": "system", "id": "second"})

    result = synchronize_dependency_backlinks(
        tmp_path,
        {
            "kind": "operation",
            "id": "consumer",
            "dependsOn": depends_on_resource("second"),
        },
        {
            "kind": "operation",
            "id": "consumer",
            "dependsOn": depends_on_resource("first"),
        },
        resources,
    )

    assert result == {"updated": ["first", "second"], "unresolved": []}
    assert resources.read_json(first)["dependedOnBy"] == {}
    assert resources.read_json(second)["dependedOnBy"] == depended_on_by_resource("consumer")


def test_synchronizes_property_inheritance_backlinks(tmp_path: Path) -> None:
    resources = FilesystemProvider()
    parent = tmp_path / "design" / "models" / "parent.backend.json"
    resources.write_json(parent, {"kind": "backend", "id": "parent"})

    result = synchronize_inheritance_backlinks(
        tmp_path,
        {
            "kind": "model",
            "id": "child",
            "inheritsFrom": inherits_from_resource("parent"),
        },
        None,
        resources,
    )

    assert result == {"updated": ["parent"], "unresolved": []}
    assert resources.read_json(parent)["inheritedBy"] == inherited_by_resource("child")


def test_legacy_resource_write_serializes_only_canonical_names(tmp_path: Path) -> None:
    resources = FilesystemProvider()
    path = tmp_path / "design" / "operations" / "parent.operation.json"
    resources.write_json(
        path,
        {
            "kind": "operation",
            "id": "parent",
            "specializations": {
                "child": {
                    "lend": ["*"],
                    "withhold": ["id", "specializations", "preferredSpecialization"],
                }
            },
            "preferredSpecialization": "child",
        },
    )

    physical = path.with_suffix(".metta").read_text(encoding="utf-8")
    assert "specializations" not in physical
    assert "preferredSpecialization" not in physical
    loaded = resources.read_json(path)
    assert loaded["implementedBy"] == {"child": {}}
    assert loaded["preferredImplementation"] == "child"
