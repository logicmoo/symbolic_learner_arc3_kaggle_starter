from __future__ import annotations

from pathlib import Path
from typing import Any

from resource_store import FilesystemProvider


DEFAULT_IMPLEMENTATION_INHERITANCE = {"borrow": ["*"], "exclude": []}
DEFAULT_SPECIALIZATION_INHERITANCE = {
    "lend": ["*"],
    "withhold": ["id", "label", "description", "implements", "specializations", "preferredSpecialization"],
}


def relationship_ids(value: Any) -> list[str]:
    """Normalize IDs from policy maps and ordinary ID-list fields."""
    if isinstance(value, dict):
        values = value
    elif isinstance(value, list):
        values = value
    elif isinstance(value, str):
        values = [value]
    else:
        values = []
    return list(dict.fromkeys(str(item) for item in values if str(item).strip()))


def relationship_map(value: Any) -> dict[str, dict[str, Any]]:
    if not isinstance(value, dict):
        return {}
    return {
        str(resource_id): dict(policy) if isinstance(policy, dict) else {}
        for resource_id, policy in value.items()
        if str(resource_id).strip()
    }


def implements_resource(resource_id: str) -> dict[str, dict[str, list[str]]]:
    return {
        resource_id: {
            key: list(value)
            for key, value in DEFAULT_IMPLEMENTATION_INHERITANCE.items()
        }
    }


def specializes_resource(resource_id: str) -> dict[str, dict[str, list[str]]]:
    return {
        resource_id: {
            key: list(value)
            for key, value in DEFAULT_SPECIALIZATION_INHERITANCE.items()
        }
    }


def _selector_matches(path: str, selector: str) -> bool:
    if selector == "*":
        return True
    if selector.endswith(".*"):
        prefix = selector[:-2]
        return path == prefix or path.startswith(f"{prefix}.")
    return path == selector or path.startswith(f"{selector}.")


def _selected(path: str, selectors: list[str]) -> bool:
    return any(_selector_matches(path, selector) for selector in selectors)


def _policy_selectors(policy: dict[str, Any], key: str, fallback: list[str]) -> list[str]:
    value = policy.get(key)
    if not isinstance(value, list):
        return list(fallback)
    return list(dict.fromkeys(str(item) for item in value if str(item).strip()))


def _flatten(value: Any, prefix: str = "", result: dict[str, Any] | None = None) -> dict[str, Any]:
    flattened = {} if result is None else result
    if not isinstance(value, dict):
        if prefix:
            flattened[prefix] = value
        return flattened
    for key, child in value.items():
        path = f"{prefix}.{key}" if prefix else str(key)
        if isinstance(child, dict) and child:
            _flatten(child, path, flattened)
        else:
            flattened[path] = child
    return flattened


def _unflatten(value: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for path, child in value.items():
        target = result
        parts = path.split(".")
        for part in parts[:-1]:
            nested = target.get(part)
            if not isinstance(nested, dict):
                nested = {}
                target[part] = nested
            target = nested
        target[parts[-1]] = child
    return result


def resolve_inherited_document(
    document: dict[str, Any],
    documents_by_id: dict[str, dict[str, Any]],
    trail: tuple[str, ...] = (),
) -> dict[str, Any]:
    """Resolve negotiated multi-parent inheritance with field provenance."""
    resource_id = str(document.get("id") or "")
    if resource_id and resource_id in trail:
        raise ValueError(f"inheritance cycle: {' -> '.join((*trail, resource_id))}")

    local = _flatten(document)
    inherited: dict[str, Any] = {}
    inherited_sources: dict[str, str] = {}
    borrowed: list[str] = []
    excluded: list[str] = []
    withheld: list[str] = []
    conflicts: list[str] = []
    missing_resources: list[str] = []
    missing_backlinks: list[str] = []
    implementation_policies = relationship_map(document.get("implements"))

    for implemented_id in relationship_ids(document.get("implements")):
        implemented = documents_by_id.get(implemented_id)
        if not implemented:
            missing_resources.append(implemented_id)
            continue
        implemented_resolution = resolve_inherited_document(
            implemented,
            documents_by_id,
            (*trail, resource_id) if resource_id else trail,
        )
        missing_resources.extend(implemented_resolution["missingResources"])
        missing_backlinks.extend(implemented_resolution["missingBacklinks"])
        conflicts.extend(implemented_resolution["conflicts"])
        request = implementation_policies.get(implemented_id, {})
        specialization_policies = relationship_map(implemented.get("specializations"))
        if resource_id not in specialization_policies:
            missing_backlinks.append(f"{implemented_id}.specializations[{resource_id}]")
        grant = specialization_policies.get(resource_id, {})
        borrow_selectors = _policy_selectors(request, "borrow", DEFAULT_IMPLEMENTATION_INHERITANCE["borrow"])
        exclude_selectors = _policy_selectors(request, "exclude", DEFAULT_IMPLEMENTATION_INHERITANCE["exclude"])
        lend_selectors = _policy_selectors(grant, "lend", DEFAULT_SPECIALIZATION_INHERITANCE["lend"])
        withhold_selectors = _policy_selectors(grant, "withhold", DEFAULT_SPECIALIZATION_INHERITANCE["withhold"])

        for path, value in _flatten(implemented_resolution["document"]).items():
            if not _selected(path, borrow_selectors) or not _selected(path, lend_selectors):
                continue
            if _selected(path, exclude_selectors):
                excluded.append(f"{implemented_id}:{path}")
                continue
            if _selected(path, withhold_selectors):
                withheld.append(f"{implemented_id}:{path}")
                continue
            if path in local:
                continue
            if path in inherited and inherited[path] != value:
                conflicts.append(f"{path}: {inherited_sources[path]} <> {implemented_id}")
                inherited.pop(path, None)
                inherited_sources.pop(path, None)
                continue
            inherited[path] = value
            inherited_sources[path] = implemented_id
            borrowed.append(f"{implemented_id}:{path}")

    return {
        "document": _unflatten({**inherited, **local}),
        "provenance": {**inherited_sources, **{path: resource_id or "local" for path in local}},
        "borrowed": sorted(set(borrowed)),
        "excluded": sorted(set(excluded)),
        "withheld": sorted(set(withheld)),
        "conflicts": sorted(set(conflicts)),
        "missingResources": sorted(set(missing_resources)),
        "missingBacklinks": sorted(set(missing_backlinks)),
    }


def points_to(document: dict[str, Any], field: str, resource_id: str) -> bool:
    return resource_id in relationship_ids(document.get(field))


def synchronize_implementation_backlinks(
    workspace_root: Path,
    document: dict[str, Any],
    previous_document: dict[str, Any] | None,
    resources: FilesystemProvider,
) -> dict[str, list[str]]:
    """Synchronize a saved resource's implemented resources' backlinks.

    Only resources physically owned by ``workspace_root`` are changed. This is
    deliberate: editing a project workspace must never mutate an inherited
    resource in Shared behind the user's back.
    """
    resource_id = str(document.get("id") or "").strip()
    if not resource_id:
        return {"updated": [], "unresolved": []}
    old_implemented_ids = set(relationship_ids((previous_document or {}).get("implements")))
    new_implemented_ids = set(relationship_ids(document.get("implements")))
    affected = old_implemented_ids | new_implemented_ids
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
    for implemented_id in sorted(affected):
        located = locations.get(implemented_id)
        if not located:
            unresolved.append(implemented_id)
            continue
        path, implemented = located
        specializations = relationship_map(implemented.get("specializations"))
        previous_specializations = relationship_map(implemented.get("specializations"))
        if implemented_id in new_implemented_ids and resource_id not in specializations:
            specializations[resource_id] = {
                key: list(value)
                for key, value in DEFAULT_SPECIALIZATION_INHERITANCE.items()
            }
        if implemented_id not in new_implemented_ids:
            specializations.pop(resource_id, None)
        if specializations != previous_specializations or not isinstance(implemented.get("specializations"), dict):
            implemented["specializations"] = specializations
            resources.write_json_resource(path, implemented)
            updated.append(implemented_id)
    return {"updated": updated, "unresolved": unresolved}
