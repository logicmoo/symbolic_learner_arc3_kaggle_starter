from __future__ import annotations

from pathlib import Path
from typing import Any

from resource_store import FilesystemProvider


def relationship_ids(value: Any) -> list[str]:
    """Normalize a persisted relationship pointer to a list of resource IDs.

    Scalars remain readable for compatibility, but new and edited resources use
    arrays so every relationship can be many-to-many.
    """
    if isinstance(value, str):
        return [value] if value.strip() else []
    if isinstance(value, list):
        return list(dict.fromkeys(str(item) for item in value if str(item).strip()))
    return []


def points_to(document: dict[str, Any], field: str, resource_id: str) -> bool:
    return resource_id in relationship_ids(document.get(field))


def synchronize_parent_backlinks(
    workspace_root: Path,
    document: dict[str, Any],
    previous_document: dict[str, Any] | None,
    resources: FilesystemProvider,
) -> dict[str, list[str]]:
    """Synchronize a saved resource's local parent ``children`` pointers.

    Only resources physically owned by ``workspace_root`` are changed. This is
    deliberate: editing a project workspace must never mutate an inherited
    resource in Shared behind the user's back.
    """
    resource_id = str(document.get("id") or "").strip()
    if not resource_id:
        return {"updated": [], "unresolved": []}
    old_parents = set(relationship_ids((previous_document or {}).get("parents")))
    new_parents = set(relationship_ids(document.get("parents")))
    affected = old_parents | new_parents
    if not affected:
        return {"updated": [], "unresolved": []}

    locations: dict[str, tuple[Path, dict[str, Any]]] = {}
    design_root = workspace_root / "design"
    scan_root = design_root if resources.is_dir(design_root) else workspace_root
    paths = resources.rglob(scan_root, "*.metta") + resources.rglob(scan_root, "*.json")
    for physical_path in paths:
        logical_path = physical_path.with_suffix(".json") if physical_path.suffix.lower() == ".metta" else physical_path
        try:
            documents = resources.read_json_documents(logical_path)
        except (OSError, ValueError):
            continue
        for candidate in documents:
            if isinstance(candidate, dict) and str(candidate.get("id") or "") in affected:
                locations[str(candidate["id"])] = (logical_path, candidate)

    updated: list[str] = []
    unresolved: list[str] = []
    for parent_id in sorted(affected):
        located = locations.get(parent_id)
        if not located:
            unresolved.append(parent_id)
            continue
        path, parent = located
        children = relationship_ids(parent.get("children"))
        if parent_id in new_parents and resource_id not in children:
            children.append(resource_id)
        if parent_id not in new_parents and resource_id in children:
            children = [child for child in children if child != resource_id]
        if children != relationship_ids(parent.get("children")) or not isinstance(parent.get("children"), list):
            parent["children"] = children
            resources.write_json_resource(path, parent)
            updated.append(parent_id)
    return {"updated": updated, "unresolved": unresolved}
