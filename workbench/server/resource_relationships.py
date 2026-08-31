from __future__ import annotations

from pathlib import Path
from typing import Any

from resource_store import FilesystemProvider


DEFAULT_INHERITANCE_REQUEST = {"borrow": ["*"], "exclude": []}
DEFAULT_INHERITANCE_GRANT = {
    "lend": ["*"],
    "withhold": [
        "id",
        "label",
        "description",
        "enabled",
        "implements",
        "implementedBy",
        "preferredImplementation",
        "inheritsFrom",
        "inheritedBy",
        "dependsOn",
        "dependedOnBy",
    ],
}
NON_INHERITED_FIELDS = {
    "id",
    "enabled",
    "implements",
    "implementedBy",
    "preferredImplementation",
    "inheritsFrom",
    "inheritedBy",
    "specializations",
    "preferredSpecialization",
    "dependsOn",
    "dependedOnBy",
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


def implements_resource(resource_id: str) -> dict[str, dict[str, Any]]:
    return {resource_id: {}}


def implemented_by_resource(resource_id: str) -> dict[str, dict[str, Any]]:
    return {resource_id: {}}


def inherits_from_resource(resource_id: str) -> dict[str, dict[str, list[str]]]:
    return {
        resource_id: {
            key: list(value)
            for key, value in DEFAULT_INHERITANCE_REQUEST.items()
        }
    }


def inherited_by_resource(resource_id: str) -> dict[str, dict[str, list[str]]]:
    return {
        resource_id: {
            key: list(value)
            for key, value in DEFAULT_INHERITANCE_GRANT.items()
        }
    }


def depends_on_resource(resource_id: str) -> dict[str, dict[str, Any]]:
    return {resource_id: {}}


def depended_on_by_resource(resource_id: str) -> dict[str, dict[str, Any]]:
    return {resource_id: {}}


def _canonical_selector(selector: str) -> str:
    if selector == "specializations" or selector.startswith("specializations."):
        return selector.replace("specializations", "implementedBy", 1)
    if selector == "preferredSpecialization" or selector.startswith("preferredSpecialization."):
        return selector.replace("preferredSpecialization", "preferredImplementation", 1)
    return selector


def _canonical_policy_selectors(
    policy: dict[str, Any], key: str, fallback: list[str]
) -> list[str]:
    return list(
        dict.fromkeys(
            _canonical_selector(selector)
            for selector in _policy_selectors(policy, key, fallback)
        )
    )


def normalize_resource_relationships(
    document: dict[str, Any],
    *,
    validate_preferred: bool = True,
) -> dict[str, Any]:
    """Normalize legacy relationship names and split implementation from inheritance."""
    normalized = dict(document)
    legacy_implemented_by = document.get("specializations")
    legacy_preferred = document.get("preferredSpecialization")
    raw_implements = document.get("implements")

    if "implementedBy" not in normalized and legacy_implemented_by is not None:
        normalized["implementedBy"] = {
            resource_id: {} for resource_id in relationship_ids(legacy_implemented_by)
        }
    if "inheritedBy" not in normalized and legacy_implemented_by is not None:
        legacy_policies = relationship_map(legacy_implemented_by)
        normalized["inheritedBy"] = {
            resource_id: {
                "lend": _canonical_policy_selectors(
                    policy, "lend", DEFAULT_INHERITANCE_GRANT["lend"]
                ),
                "withhold": _canonical_policy_selectors(
                    policy, "withhold", DEFAULT_INHERITANCE_GRANT["withhold"]
                ),
            }
            for resource_id, policy in legacy_policies.items()
        }
    if "preferredImplementation" not in normalized and legacy_preferred is not None:
        normalized["preferredImplementation"] = legacy_preferred
    if "inheritsFrom" not in normalized and isinstance(raw_implements, dict):
        implementation_policies = relationship_map(raw_implements)
        if any(
            "borrow" in policy or "exclude" in policy
            for policy in implementation_policies.values()
        ):
            normalized["inheritsFrom"] = {
                resource_id: {
                    "borrow": _canonical_policy_selectors(
                        policy, "borrow", DEFAULT_INHERITANCE_REQUEST["borrow"]
                    ),
                    "exclude": _canonical_policy_selectors(
                        policy, "exclude", DEFAULT_INHERITANCE_REQUEST["exclude"]
                    ),
                }
                for resource_id, policy in implementation_policies.items()
            }
    if raw_implements is not None:
        normalized["implements"] = {
            resource_id: {} for resource_id in relationship_ids(raw_implements)
        }
    if normalized.get("implementedBy") is not None:
        normalized["implementedBy"] = {
            resource_id: {}
            for resource_id in relationship_ids(normalized.get("implementedBy"))
        }
    if normalized.get("inheritsFrom") is not None:
        normalized["inheritsFrom"] = {
            resource_id: {
                "borrow": _canonical_policy_selectors(
                    policy, "borrow", DEFAULT_INHERITANCE_REQUEST["borrow"]
                ),
                "exclude": _canonical_policy_selectors(
                    policy, "exclude", DEFAULT_INHERITANCE_REQUEST["exclude"]
                ),
            }
            for resource_id, policy in relationship_map(
                normalized.get("inheritsFrom")
            ).items()
        }
    if normalized.get("inheritedBy") is not None:
        normalized["inheritedBy"] = {
            resource_id: {
                "lend": _canonical_policy_selectors(
                    policy, "lend", DEFAULT_INHERITANCE_GRANT["lend"]
                ),
                "withhold": _canonical_policy_selectors(
                    policy, "withhold", DEFAULT_INHERITANCE_GRANT["withhold"]
                ),
            }
            for resource_id, policy in relationship_map(
                normalized.get("inheritedBy")
            ).items()
        }
    for field in ("dependsOn", "dependedOnBy"):
        if normalized.get(field) is not None:
            normalized[field] = {
                resource_id: {}
                for resource_id in relationship_ids(normalized.get(field))
            }

    normalized.pop("specializations", None)
    normalized.pop("preferredSpecialization", None)
    preferred = str(normalized.get("preferredImplementation") or "").strip()
    if (
        validate_preferred
        and preferred
        and preferred not in relationship_ids(normalized.get("implementedBy"))
    ):
        raise ValueError(
            f"preferredImplementation {preferred!r} must belong to implementedBy"
        )
    return normalized



def resolve_dependency_enablement(
    document: dict[str, Any],
    documents_by_id: dict[str, dict[str, Any]],
    trail: tuple[str, ...] = (),
) -> dict[str, Any]:
    """Resolve availability through dependsOn, independently of inheritance."""
    resource_id = str(document.get("id") or "")
    if resource_id and resource_id in trail:
        raise ValueError(f"dependency cycle: {' -> '.join((*trail, resource_id))}")
    dependency_ids = relationship_ids(document.get("dependsOn"))
    missing_dependencies: list[str] = []
    missing_backlinks: list[str] = []
    blocking_dependencies: list[str] = []
    for dependency_id in dependency_ids:
        dependency = documents_by_id.get(dependency_id)
        if not dependency:
            missing_dependencies.append(dependency_id)
            continue
        if resource_id not in relationship_ids(dependency.get("dependedOnBy")):
            missing_backlinks.append(f"{dependency_id}.dependedOnBy[{resource_id}]")
        resolved = resolve_dependency_enablement(
            dependency,
            documents_by_id,
            (*trail, resource_id) if resource_id else trail,
        )
        if not resolved["enabled"]:
            blocking_dependencies.append(dependency_id)
        blocking_dependencies.extend(resolved["blockingDependencies"])
        missing_dependencies.extend(resolved["missingDependencies"])
        missing_backlinks.extend(resolved["missingBacklinks"])
    declared_enabled = document.get("enabled", True) is not False
    enabled = (
        declared_enabled
        and not missing_dependencies
        and not missing_backlinks
        and not blocking_dependencies
    )
    return {
        "enabled": enabled,
        "declaredEnabled": declared_enabled,
        "dependencies": dependency_ids,
        "blockingDependencies": sorted(set(blocking_dependencies)),
        "missingDependencies": sorted(set(missing_dependencies)),
        "missingBacklinks": sorted(set(missing_backlinks)),
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
    document = normalize_resource_relationships(document)
    documents_by_id = {
        resource_id: normalize_resource_relationships(candidate)
        for resource_id, candidate in documents_by_id.items()
    }
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
    inheritance_policies = relationship_map(document.get("inheritsFrom"))

    for inherited_id in relationship_ids(document.get("inheritsFrom")):
        inherited_resource = documents_by_id.get(inherited_id)
        if not inherited_resource:
            missing_resources.append(inherited_id)
            continue
        inherited_resolution = resolve_inherited_document(
            inherited_resource,
            documents_by_id,
            (*trail, resource_id) if resource_id else trail,
        )
        missing_resources.extend(inherited_resolution["missingResources"])
        missing_backlinks.extend(inherited_resolution["missingBacklinks"])
        conflicts.extend(inherited_resolution["conflicts"])
        request = inheritance_policies.get(inherited_id, {})
        inheritance_grants = relationship_map(inherited_resource.get("inheritedBy"))
        if resource_id not in inheritance_grants:
            missing_backlinks.append(f"{inherited_id}.inheritedBy[{resource_id}]")
        grant = inheritance_grants.get(resource_id, {})
        borrow_selectors = _policy_selectors(request, "borrow", DEFAULT_INHERITANCE_REQUEST["borrow"])
        exclude_selectors = _policy_selectors(request, "exclude", DEFAULT_INHERITANCE_REQUEST["exclude"])
        lend_selectors = _policy_selectors(grant, "lend", DEFAULT_INHERITANCE_GRANT["lend"])
        withhold_selectors = _policy_selectors(grant, "withhold", DEFAULT_INHERITANCE_GRANT["withhold"])

        for path, value in _flatten(inherited_resolution["document"]).items():
            if path.split(".", 1)[0] in NON_INHERITED_FIELDS:
                withheld.append(f"{inherited_id}:{path}")
                continue
            if not _selected(path, borrow_selectors) or not _selected(path, lend_selectors):
                continue
            if _selected(path, exclude_selectors):
                excluded.append(f"{inherited_id}:{path}")
                continue
            if _selected(path, withhold_selectors):
                withheld.append(f"{inherited_id}:{path}")
                continue
            if path in local:
                continue
            if path in inherited and inherited[path] != value:
                conflicts.append(f"{path}: {inherited_sources[path]} <> {inherited_id}")
                inherited.pop(path, None)
                inherited_sources.pop(path, None)
                continue
            inherited[path] = value
            inherited_sources[path] = inherited_id
            borrowed.append(f"{inherited_id}:{path}")

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
        implemented_by = relationship_map(implemented.get("implementedBy"))
        previous_implemented_by = relationship_map(implemented.get("implementedBy"))
        if implemented_id in new_implemented_ids:
            implemented_by.setdefault(resource_id, {})
        if implemented_id not in new_implemented_ids:
            implemented_by.pop(resource_id, None)
        if implemented_by != previous_implemented_by or not isinstance(implemented.get("implementedBy"), dict):
            implemented["implementedBy"] = implemented_by
            resources.write_json_resource(path, implemented)
            updated.append(implemented_id)
    return {"updated": updated, "unresolved": unresolved}


def synchronize_inheritance_backlinks(
    workspace_root: Path,
    document: dict[str, Any],
    previous_document: dict[str, Any] | None,
    resources: FilesystemProvider,
) -> dict[str, list[str]]:
    """Synchronize inheritsFrom with inheritedBy inside the edited workspace."""
    resource_id = str(document.get("id") or "").strip()
    if not resource_id:
        return {"updated": [], "unresolved": []}
    old_parent_ids = set(relationship_ids((previous_document or {}).get("inheritsFrom")))
    new_parent_ids = set(relationship_ids(document.get("inheritsFrom")))
    affected = old_parent_ids | new_parent_ids
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
        inherited_by = relationship_map(parent.get("inheritedBy"))
        previous_inherited_by = relationship_map(parent.get("inheritedBy"))
        if parent_id in new_parent_ids:
            inherited_by.setdefault(
                resource_id,
                {
                    key: list(value)
                    for key, value in DEFAULT_INHERITANCE_GRANT.items()
                },
            )
        else:
            inherited_by.pop(resource_id, None)
        if inherited_by != previous_inherited_by or not isinstance(parent.get("inheritedBy"), dict):
            parent["inheritedBy"] = inherited_by
            resources.write_json_resource(path, parent)
            updated.append(parent_id)
    return {"updated": updated, "unresolved": unresolved}


def synchronize_dependency_backlinks(
    workspace_root: Path,
    document: dict[str, Any],
    previous_document: dict[str, Any] | None,
    resources: FilesystemProvider,
) -> dict[str, list[str]]:
    """Synchronize dependsOn with dependedOnBy inside the edited workspace."""
    resource_id = str(document.get("id") or "").strip()
    if not resource_id:
        return {"updated": [], "unresolved": []}
    old_dependency_ids = set(relationship_ids((previous_document or {}).get("dependsOn")))
    new_dependency_ids = set(relationship_ids(document.get("dependsOn")))
    affected = old_dependency_ids | new_dependency_ids
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
    for dependency_id in sorted(affected):
        located = locations.get(dependency_id)
        if not located:
            unresolved.append(dependency_id)
            continue
        path, dependency = located
        dependents = relationship_map(dependency.get("dependedOnBy"))
        previous_dependents = relationship_map(dependency.get("dependedOnBy"))
        if dependency_id in new_dependency_ids:
            dependents.setdefault(resource_id, {})
        else:
            dependents.pop(resource_id, None)
        if dependents != previous_dependents or not isinstance(dependency.get("dependedOnBy"), dict):
            dependency["dependedOnBy"] = dependents
            resources.write_json_resource(path, dependency)
            updated.append(dependency_id)
    return {"updated": updated, "unresolved": unresolved}


def synchronize_resource_backlinks(
    workspace_root: Path,
    document: dict[str, Any],
    previous_document: dict[str, Any] | None,
    resources: FilesystemProvider,
) -> dict[str, Any]:
    implementation = synchronize_implementation_backlinks(
        workspace_root, document, previous_document, resources
    )
    properties = synchronize_inheritance_backlinks(
        workspace_root, document, previous_document, resources
    )
    dependencies = synchronize_dependency_backlinks(
        workspace_root, document, previous_document, resources
    )
    return {
        "updated": sorted(
            set(implementation["updated"])
            | set(properties["updated"])
            | set(dependencies["updated"])
        ),
        "unresolved": sorted(
            set(implementation["unresolved"])
            | set(properties["unresolved"])
            | set(dependencies["unresolved"])
        ),
        "implementation": implementation,
        "inheritance": properties,
        "dependencies": dependencies,
    }
