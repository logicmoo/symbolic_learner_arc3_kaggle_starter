from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from operation_library import DEFAULT_WORKSPACES_ROOT, SHARED_WORKSPACE_ID
from workspace_inheritance import effective_workspace_layers, layer_source
from resource_relationships import points_to, relationship_ids
from resource_store import get_filesystem_provider

PROMPT_DIRECTORY = "prompts"
PROMPT_KIND = "prompt"
PROMPT_IMPLEMENTATION_KIND = "prompt_implementation"
PROMPT_KINDS = {PROMPT_KIND, PROMPT_IMPLEMENTATION_KIND}
PROMPT_DIRECTORIES = ("design/prompts", "design/prompt_implementations", "prompts", "prompt_implementations")


def _validate_prompt(value: Any, path: Path) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"Prompt definition must be a JSON object: {path}")

    raw_kind = str(value.get("kind") or PROMPT_KIND).replace("-", "_")
    if raw_kind not in PROMPT_KINDS:
        raise ValueError(
            f"Prompt resource must declare kind='prompt' or kind='prompt_implementation': {path}"
        )
    value["kind"] = raw_kind

    if not str(value.get("id") or "").strip():
        raise ValueError(f"Prompt definition requires id: {path}")

    if raw_kind == PROMPT_IMPLEMENTATION_KIND:
        if not relationship_ids(value.get("parents")):
            raise ValueError(f"Prompt implementation requires parents: {path}")
        text = value.get("text")
        if not isinstance(text, (str, list)):
            raise ValueError(f"Prompt implementation requires text as a string or list of strings: {path}")
        if isinstance(text, list) and not all(isinstance(item, str) for item in text):
            raise ValueError(f"Prompt text list must contain only strings: {path}")
    else:
        # Backwards compatible: an abstract prompt may still carry inline text.
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
                record["convention"] = "canonical" if path.name.endswith(f".{document['kind']}.json") else "multi-resource" if len(documents) > 1 else "legacy-filename"
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
            key = f"{document.get('kind')}:{document.get('id') or record['path']}"
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
    ]


def load_shared_prompt_implementation_records(
    workspaces_root: Path = DEFAULT_WORKSPACES_ROOT,
) -> list[dict[str, Any]]:
    return [
        record
        for record in load_shared_prompt_resource_records(workspaces_root)
        if (record.get("document") or {}).get("kind") == PROMPT_IMPLEMENTATION_KIND
    ]


def load_workspace_local_prompt_records(workspace_root: Path) -> list[dict[str, Any]]:
    return [
        record
        for record in load_workspace_local_prompt_resource_records(workspace_root)
        if (record.get("document") or {}).get("kind") == PROMPT_KIND
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
    ]


def load_workspace_prompt_implementation_records(
    workspace_root: Path,
    *,
    workspaces_root: Path = DEFAULT_WORKSPACES_ROOT,
) -> list[dict[str, Any]]:
    return [
        record
        for record in _effective_prompt_resources(workspace_root, workspaces_root=workspaces_root)
        if (record.get("document") or {}).get("kind") == PROMPT_IMPLEMENTATION_KIND
    ]


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
    variants = relationship_ids(prompt.get("children"))
    chosen = requested or prompt.get("preferredChild") or (variants[0] if variants else None)

    if not chosen:
        if prompt.get("text") is not None:
            return {
                "prompt": prompt,
                "promptRecord": prompt_record,
                "implementation": prompt,
                "implementationRecord": prompt_record,
                "inline": True,
            }
        raise ValueError(f"prompt has no implementation variant: {prompt_id}")

    if variants and chosen not in variants:
        raise ValueError(f"prompt implementation {chosen} is not allowed by prompt {prompt_id}")

    implementation_record = implementations.get(str(chosen))
    if not implementation_record:
        raise KeyError(f"prompt implementation not found: {chosen}")
    implementation = implementation_record["document"]
    if not points_to(implementation, "parents", prompt_id):
        raise ValueError(f"prompt implementation {chosen} does not implement {prompt_id}")

    return {
        "prompt": prompt,
        "promptRecord": prompt_record,
        "implementation": implementation,
        "implementationRecord": implementation_record,
        "inline": False,
    }


def prompt_hierarchy(
    workspace_root: Path,
    *,
    workspaces_root: Path = DEFAULT_WORKSPACES_ROOT,
) -> dict[str, Any]:
    prompts = load_workspace_prompt_records(workspace_root, workspaces_root=workspaces_root)
    implementations = load_workspace_prompt_implementation_records(
        workspace_root, workspaces_root=workspaces_root
    )
    by_prompt: dict[str, list[dict[str, Any]]] = {}
    for record in implementations:
        document = record.get("document") or {}
        for parent in relationship_ids(document.get("parents")):
            by_prompt.setdefault(parent, []).append(record)
    for values in by_prompt.values():
        values.sort(key=lambda item: str((item.get("document") or {}).get("label") or item["path"]).lower())
    return {
        "prompts": prompts,
        "promptImplementations": implementations,
        "implementationsByPrompt": by_prompt,
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
