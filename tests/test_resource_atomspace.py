from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "workbench" / "server"
sys.path.insert(0, str(SERVER))

import workspace_api  # noqa: E402
from resource_relationships import (  # noqa: E402
    depended_on_by_resource,
    depends_on_resource,
    implemented_by_resource,
    implements_resource,
    inherited_by_resource,
    inherits_from_resource,
)
from resource_store import get_filesystem_provider  # noqa: E402


def test_resource_atomspace_contains_all_canonical_relationships(
    tmp_path: Path,
    monkeypatch,
) -> None:
    resources = get_filesystem_provider()
    parent_path = tmp_path / "design" / "operations" / "parent.operation.json"
    child_path = tmp_path / "design" / "operations" / "child.operation.json"
    resources.write_json(
        parent_path,
        {
            "kind": "operation",
            "id": "parent",
            "implementedBy": implemented_by_resource("child"),
            "inheritedBy": inherited_by_resource("child"),
            "dependedOnBy": depended_on_by_resource("child"),
            "preferredImplementation": "child",
        },
    )
    resources.write_json(
        child_path,
        {
            "kind": "operation",
            "id": "child",
            "implements": implements_resource("parent"),
            "inheritsFrom": inherits_from_resource("parent"),
            "dependsOn": depends_on_resource("parent"),
        },
    )
    monkeypatch.setattr(
        workspace_api,
        "_resolve_workspace_without_counts",
        lambda _workspace_id: {"id": "test", "root": str(tmp_path)},
    )
    monkeypatch.setattr(
        workspace_api,
        "effective_workspace_layers",
        lambda _root, _workspaces_root: [tmp_path],
    )
    monkeypatch.setattr(workspace_api, "layer_source", lambda _layer, _root: "workspace")

    payload = workspace_api.workspace_resource_atomspace("test")
    relationships = {link["relationship"] for link in payload["links"]}
    assert {atom["id"] for atom in payload["atoms"]} == {"parent", "child"}
    assert {
        "implements",
        "implementedBy",
        "inheritsFrom",
        "inheritedBy",
        "dependsOn",
        "dependedOnBy",
        "preferredImplementation",
    } <= relationships


def test_resource_atomspace_page_is_real_and_navigable() -> None:
    component = (
        ROOT
        / "workbench"
        / "frontend"
        / "src"
        / "components"
        / "ResourceAtomspacePage.tsx"
    ).read_text(encoding="utf-8")
    shell = (
        ROOT
        / "workbench"
        / "frontend"
        / "src"
        / "pages"
        / "FilesystemWorkbenchPage.tsx"
    ).read_text(encoding="utf-8")
    assert "/resource-atomspace" in component
    assert "Every effective filesystem/runtime resource is an atom" in component
    assert "Resource AtomSpace" in shell
    assert 'view === "resourceAtomspace"' in shell
