from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "workbench" / "server"
if str(SERVER) not in sys.path:
    sys.path.insert(0, str(SERVER))

from metta_resource_codec import metta_documents_to_json  # noqa: E402
from resource_relationships import (  # noqa: E402
    DEFAULT_INHERITANCE_GRANT,
    normalize_resource_relationships,
)
from resource_store import get_filesystem_provider  # noqa: E402


def raw_documents(path: Path) -> list[Any]:
    if path.suffix.lower() == ".metta":
        return metta_documents_to_json(path.read_text(encoding="utf-8"))
    return get_filesystem_provider().read_config_json(path)


def relationship_resources(workspace: Path) -> list[tuple[Path, dict[str, Any]]]:
    resources: list[tuple[Path, dict[str, Any]]] = []
    paths = [*workspace.rglob("*.metta"), *workspace.rglob("*.json")]
    for physical_path in paths:
        if any(part in {"runtime", "node_modules", ".git"} for part in physical_path.relative_to(workspace).parts):
            continue
        try:
            documents = raw_documents(physical_path)
        except (OSError, ValueError):
            continue
        rows = documents if isinstance(documents, list) else [documents]
        logical_path = physical_path.with_suffix(".json") if physical_path.suffix.lower() == ".metta" else physical_path
        for document in rows:
            if isinstance(document, dict) and document.get("kind") and document.get("id"):
                resources.append((logical_path, document))
    return resources


def migrate_workspace(workspace: Path, *, write: bool) -> dict[str, Any]:
    filesystem = get_filesystem_provider()
    records = relationship_resources(workspace)
    ambiguous: list[str] = []
    canonical: list[tuple[Path, dict[str, Any], dict[str, Any]]] = []
    for path, document in records:
        raw_implements = document.get("implements")
        if (
            raw_implements is not None
            and not isinstance(raw_implements, dict)
            and "inheritsFrom" not in document
        ):
            ambiguous.append(
                f"{path.relative_to(workspace).as_posix()}:{document['id']} "
                "has policy-free legacy implements; property inheritance was not inferred"
            )
        normalized = normalize_resource_relationships(document)
        canonical.append((path, document, normalized))

    by_id = {
        str(document["id"]): document
        for _, _, document in canonical
    }
    unresolved: set[str] = set()
    for _, _, child in canonical:
        child_id = str(child["id"])
        for parent_id in child.get("implements") or {}:
            parent = by_id.get(str(parent_id))
            if parent is None:
                unresolved.add(str(parent_id))
                continue
            parent.setdefault("implementedBy", {}).setdefault(child_id, {})
        for parent_id in child.get("inheritsFrom") or {}:
            parent = by_id.get(str(parent_id))
            if parent is None:
                unresolved.add(str(parent_id))
                continue
            parent.setdefault("inheritedBy", {}).setdefault(
                child_id,
                {
                    key: list(value)
                    for key, value in DEFAULT_INHERITANCE_GRANT.items()
                },
            )
        for dependency_id in child.get("dependsOn") or {}:
            dependency = by_id.get(str(dependency_id))
            if dependency is None:
                unresolved.add(str(dependency_id))
                continue
            dependency.setdefault("dependedOnBy", {}).setdefault(child_id, {})

    migrated = 0
    for path, original, normalized in canonical:
        if normalized == original:
            continue
        migrated += 1
        if write:
            filesystem.write_json_resource(path, normalized)
    return {
        "workspace": workspace.name,
        "resources": len(records),
        "migrated": migrated,
        "unresolved": sorted(unresolved),
        "ambiguous": ambiguous,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Migrate resource relationship fields to canonical graphs."
    )
    parser.add_argument("--check", action="store_true", help="Report without writing")
    parser.add_argument(
        "--workspace",
        action="append",
        default=[],
        help="Workspace directory name; repeat to limit the migration",
    )
    args = parser.parse_args()
    workspaces_root = ROOT / "workbench" / "workspaces"
    selected = set(args.workspace)
    reports = []
    for workspace in sorted(
        path
        for path in workspaces_root.iterdir()
        if path.is_dir() and not path.name.startswith(".")
    ):
        if selected and workspace.name not in selected:
            continue
        report = migrate_workspace(workspace, write=not args.check)
        reports.append(report)
        print(report)
    return 2 if any(report["ambiguous"] for report in reports) else 0


if __name__ == "__main__":
    raise SystemExit(main())
