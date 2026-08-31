from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from operation_library import DEFAULT_WORKSPACES_ROOT, SHARED_WORKSPACE_ID
from workspace_inheritance import effective_workspace_layers, layer_source
from resource_relationships import points_to, relationship_ids, resolve_inherited_document
from resource_store import get_filesystem_provider

PROMPT_DIRECTORY = "prompts"
PROMPT_KIND = "prompt"
PROMPT_IMPLEMENTATION_KIND = "prompt_implementation"
PROMPT_PROFILE_KIND = "prompt_profile"
PROMPT_KINDS = {PROMPT_KIND, PROMPT_IMPLEMENTATION_KIND, PROMPT_PROFILE_KIND}
PROMPT_DIRECTORIES = ("design/prompts", "design/prompt_implementations", "prompts", "prompt_implementations")


def _validate_prompt(value: Any, path: Path) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"Prompt definition must be a JSON object: {path}")

    raw_kind = str(value.get("kind") or PROMPT_KIND).replace("-", "_")
    if raw_kind not in PROMPT_KINDS:
        raise ValueError(
            f"Prompt resource must declare kind='prompt', 'prompt_implementation', or 'prompt_profile': {path}"
        )
    value["kind"] = PROMPT_PROFILE_KIND if raw_kind == PROMPT_PROFILE_KIND else PROMPT_KIND

    if not str(value.get("id") or "").strip():
        raise ValueError(f"Prompt definition requires id: {path}")

    if raw_kind == PROMPT_PROFILE_KIND:
        prompts = value.get("prompts")
        if not isinstance(prompts, list) or not prompts or not all(isinstance(item, str) and item.strip() for item in prompts):
            raise ValueError(f"Prompt profile requires a non-empty prompts list: {path}")
        separator = value.get("separator", "\n\n")
        if not isinstance(separator, str):
            raise ValueError(f"Prompt profile separator must be a string: {path}")
        value["separator"] = separator
        return value

    if raw_kind == PROMPT_IMPLEMENTATION_KIND and not relationship_ids(value.get("implements")):
        raise ValueError(f"Legacy prompt implementation requires implements: {path}")
    text = value.get("text")
    if text is not None and not isinstance(text, (str, list)):
        raise ValueError(f"Prompt text must be a string or list of strings: {path}")
    if isinstance(text, list) and not all(isinstance(item, str) for item in text):
        raise ValueError(f"Prompt text list must contain only strings: {path}")

    return value


def read_prompt_file(path: Path) -> dict[str, Any]:
    try:
        return _validate_prompt(get_filesystem_provider().read_json_documents(path)[0], path)
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"Invalid prompt definition {path}: {error}") from error


def _prompt_records(workspace_root: Path, source: str, workspace_id: str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    paths = get_filesystem_provider().glob(workspace_root, PROMPT_DIRECTORIES)
    for path in sorted(paths, key=lambda item: item.name.lower()):
        try:
            documents = get_filesystem_provider().read_json_documents(path)
        except (OSError, json.JSONDecodeError, ValueError) as error:
            records.append({"path": path.relative_to(workspace_root).as_posix(), "source": source, "workspaceId": workspace_id, "error": str(error)})
            continue
        for resource_index, value in enumerate(documents):
            record: dict[str, Any] = {"path": path.relative_to(workspace_root).as_posix(), "source": source, "workspaceId": workspace_id, "resourceIndex": resource_index}
            try:
                document = _validate_prompt(value, path)
                record["document"] = document
                record["convention"] = "canonical" if path.name.endswith(".prompt.json") else "multi-resource" if len(documents) > 1 else "legacy-filename"
            except ValueError as error:
                record["error"] = str(error)
            records.append(record)
    return records


def load_shared_prompt_resource_records(
    workspaces_root: Path = DEFAULT_WORKSPACES_ROOT,
) -> list[dict[str, Any]]:
    return _prompt_records(workspaces_root / SHARED_WORKSPACE_ID, "shared", SHARED_WORKSPACE_ID)


def load_workspace_local_prompt_resource_records(workspace_root: Path) -> list[dict[str, Any]]:
    if workspace_root.name == SHARED_WORKSPACE_ID:
        return []
    return _prompt_records(workspace_root, "workspace", workspace_root.name)


def _effective_prompt_resources(
    workspace_root: Path,
    *,
    workspaces_root: Path = DEFAULT_WORKSPACES_ROOT,
) -> list[dict[str, Any]]:
    # Kind participates in the key so a prompt and one of its implementations
    # can never shadow each other accidentally.
    combined: dict[str, dict[str, Any]] = {}
    for layer in effective_workspace_layers(workspace_root, workspaces_root):
        for record in _prompt_records(layer, layer_source(layer, workspace_root), layer.name):
            document = record.get("document") or {}
            key = str(document.get('id') or record['path'])
            combined[key] = record
    return sorted(
        combined.values(),
        key=lambda item: str((item.get("document") or {}).get("label") or item["path"]).lower(),
    )


def load_shared_prompt_records(workspaces_root: Path = DEFAULT_WORKSPACES_ROOT) -> list[dict[str, Any]]:
    return [
        record
        for record in load_shared_prompt_resource_records(workspaces_root)
        if (record.get("document") or {}).get("kind") == PROMPT_KIND
        and not relationship_ids((record.get("document") or {}).get("implements"))
    ]


def load_shared_prompt_implementation_records(
    workspaces_root: Path = DEFAULT_WORKSPACES_ROOT,
) -> list[dict[str, Any]]:
    return [
        record
        for record in load_shared_prompt_resource_records(workspaces_root)
        if (record.get("document") or {}).get("kind") == PROMPT_KIND
        and relationship_ids((record.get("document") or {}).get("implements"))
    ]


def load_workspace_local_prompt_records(workspace_root: Path) -> list[dict[str, Any]]:
    return [
        record
        for record in load_workspace_local_prompt_resource_records(workspace_root)
        if (record.get("document") or {}).get("kind") == PROMPT_KIND
        and not relationship_ids((record.get("document") or {}).get("implements"))
    ]


def load_workspace_prompt_records(
    workspace_root: Path,
    *,
    workspaces_root: Path = DEFAULT_WORKSPACES_ROOT,
) -> list[dict[str, Any]]:
    return [
        record
        for record in _effective_prompt_resources(workspace_root, workspaces_root=workspaces_root)
        if (record.get("document") or {}).get("kind") == PROMPT_KIND
        and not relationship_ids((record.get("document") or {}).get("implements"))
    ]


def load_workspace_prompt_implementation_records(
    workspace_root: Path,
    *,
    workspaces_root: Path = DEFAULT_WORKSPACES_ROOT,
) -> list[dict[str, Any]]:
    return [
        record
        for record in _effective_prompt_resources(workspace_root, workspaces_root=workspaces_root)
        if (record.get("document") or {}).get("kind") == PROMPT_KIND
        and relationship_ids((record.get("document") or {}).get("implements"))
    ]


def load_workspace_prompt_profile_records(
    workspace_root: Path,
    *,
    workspaces_root: Path = DEFAULT_WORKSPACES_ROOT,
) -> list[dict[str, Any]]:
    return [
        record
        for record in _effective_prompt_resources(workspace_root, workspaces_root=workspaces_root)
        if (record.get("document") or {}).get("kind") == PROMPT_PROFILE_KIND
    ]


def resolve_prompt_profile(
    workspace_root: Path,
    profile_id: str,
    *,
    workspaces_root: Path = DEFAULT_WORKSPACES_ROOT,
) -> dict[str, Any]:
    record = next(
        (
            item for item in load_workspace_prompt_profile_records(workspace_root, workspaces_root=workspaces_root)
            if str((item.get("document") or {}).get("id")) == profile_id
        ),
        None,
    )
    if not record:
        raise KeyError(f"prompt profile not found: {profile_id}")
    profile = record["document"]
    return {
        "profile": profile,
        "profileRecord": record,
        "prompts": [str(item) for item in profile.get("prompts") or []],
        "separator": str(profile.get("separator") or "\n\n"),
    }


def resolve_prompt_implementation(
    workspace_root: Path,
    prompt_id: str,
    requested: str | None = None,
    *,
    workspaces_root: Path = DEFAULT_WORKSPACES_ROOT,
) -> dict[str, Any]:
    prompts = {
        str((record.get("document") or {}).get("id")): record
        for record in load_workspace_prompt_records(workspace_root, workspaces_root=workspaces_root)
    }
    implementations = {
        str((record.get("document") or {}).get("id")): record
        for record in load_workspace_prompt_implementation_records(
            workspace_root, workspaces_root=workspaces_root
        )
    }
    prompt_record = prompts.get(prompt_id)
    if not prompt_record:
        raise KeyError(f"prompt not found: {prompt_id}")

    prompt = prompt_record["document"]
    all_records = {**prompts, **implementations}
    documents_by_id = {
        resource_id: record["document"]
        for resource_id, record in all_records.items()
        if record.get("document")
    }

    def inheritance_resolution(document: dict[str, Any]) -> dict[str, Any]:
        resolution = resolve_inherited_document(document, documents_by_id)
        blockers = [
            *resolution["conflicts"],
            *resolution["missingResources"],
            *resolution["missingBacklinks"],
        ]
        if blockers:
            raise ValueError(f"prompt inheritance is unresolved for {document.get('id')}: {'; '.join(blockers)}")
        return resolution

    def has_text(document: dict[str, Any]) -> bool:
        text = inheritance_resolution(document)["document"].get("text")
        return isinstance(text, str) and bool(text.strip()) or isinstance(text, list) and bool(text)

    def implementation_ids(resource_id: str) -> list[str]:
        record = all_records.get(resource_id)
        if not record:
            return []
        document = record.get("document") or {}
        declared = relationship_ids(document.get("implementedBy"))
        reverse = [
            candidate_id
            for candidate_id, candidate in implementations.items()
            if points_to(candidate.get("document") or {}, "implements", resource_id)
        ]
        ordered = list(dict.fromkeys([*declared, *reverse]))
        preferred = str(document.get("preferredImplementation") or "")
        return ([preferred] if preferred in ordered else []) + [candidate for candidate in ordered if candidate != preferred]

    def resolve_candidate(candidate_id: str, trail: tuple[str, ...]) -> tuple[dict[str, Any], list[str]] | None:
        if candidate_id in trail:
            raise ValueError(f"prompt implementation cycle: {' -> '.join((*trail, candidate_id))}")
        record = all_records.get(candidate_id)
        if not record:
            return None
        document = record.get("document") or {}
        path = [*trail, candidate_id]
        if has_text(document):
            return record, path
        for implementation_id in implementation_ids(candidate_id):
            resolved = resolve_candidate(implementation_id, tuple(path))
            if resolved:
                return resolved
        return None

    reachable: set[str] = set()

    def collect(resource_id: str, trail: tuple[str, ...] = ()) -> None:
        if resource_id in trail:
            raise ValueError(f"prompt implementation cycle: {' -> '.join((*trail, resource_id))}")
        for implementation_id in implementation_ids(resource_id):
            if implementation_id in reachable:
                continue
            reachable.add(implementation_id)
            collect(implementation_id, (*trail, resource_id))

    collect(prompt_id)
    if requested == prompt_id:
        if not has_text(prompt):
            raise ValueError(f"prompt {prompt_id} has no inline text")
        inheritance = inheritance_resolution(prompt)
        return {
            "prompt": prompt,
            "promptRecord": prompt_record,
            "implementation": inheritance["document"],
            "declaredImplementation": prompt,
            "implementationRecord": prompt_record,
            "propertyInheritanceResolution": inheritance,
            "implementationPath": [prompt_id],
            "inline": True,
        }
    if requested and requested not in reachable:
        raise ValueError(f"prompt implementation {requested} is not allowed by prompt {prompt_id}")

    starts = [requested] if requested else implementation_ids(prompt_id)
    for candidate_id in starts:
        if not candidate_id:
            continue
        resolved = resolve_candidate(candidate_id, (prompt_id,))
        if not resolved:
            continue
        implementation_record, resolution_path = resolved
        implementation = implementation_record["document"]
        inheritance = inheritance_resolution(implementation)
        return {
            "prompt": prompt,
            "promptRecord": prompt_record,
            "implementation": inheritance["document"],
            "declaredImplementation": implementation,
            "implementationRecord": implementation_record,
            "propertyInheritanceResolution": inheritance,
            "selectedImplementation": candidate_id,
            "implementationPath": resolution_path,
            "inline": False,
        }

    if has_text(prompt):
        inheritance = inheritance_resolution(prompt)
        return {
            "prompt": prompt,
            "promptRecord": prompt_record,
            "implementation": inheritance["document"],
            "declaredImplementation": prompt,
            "implementationRecord": prompt_record,
            "propertyInheritanceResolution": inheritance,
            "implementationPath": [prompt_id],
            "inline": True,
        }
    if requested:
        raise ValueError(f"prompt implementation {requested} has no concrete descendant")
    raise ValueError(f"prompt has no concrete implementation: {prompt_id}")


def prompt_hierarchy(
    workspace_root: Path,
    *,
    workspaces_root: Path = DEFAULT_WORKSPACES_ROOT,
) -> dict[str, Any]:
    prompts = load_workspace_prompt_records(workspace_root, workspaces_root=workspaces_root)
    implementations = load_workspace_prompt_implementation_records(
        workspace_root, workspaces_root=workspaces_root
    )
    profiles = load_workspace_prompt_profile_records(workspace_root, workspaces_root=workspaces_root)
    by_prompt: dict[str, list[dict[str, Any]]] = {}
    for record in implementations:
        document = record.get("document") or {}
        for parent in relationship_ids(document.get("implements")):
            by_prompt.setdefault(parent, []).append(record)
    for values in by_prompt.values():
        values.sort(key=lambda item: str((item.get("document") or {}).get("label") or item["path"]).lower())
    return {
        "prompts": prompts,
        "promptImplementations": implementations,
        "promptProfiles": profiles,
        "implementedByResource": by_prompt,
    }


def load_prompt_library_records(
    workspace_root: Path,
    *,
    workspaces_root: Path = DEFAULT_WORKSPACES_ROOT,
) -> dict[str, Any]:
    return {
        "shared": load_shared_prompt_resource_records(workspaces_root),
        "workspace": load_workspace_local_prompt_resource_records(workspace_root),
        "effective": _effective_prompt_resources(workspace_root, workspaces_root=workspaces_root),
        "hierarchy": prompt_hierarchy(workspace_root, workspaces_root=workspaces_root),
    }
