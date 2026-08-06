from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from task_library import DEFAULT_WORKSPACES_ROOT, SHARED_WORKSPACE_ID

DATATYPE_DIRECTORY = "datatypes"
REPRESENTATION_DIRECTORY = "representations"
DATATYPE_KIND = "datatype"
REPRESENTATION_KIND = "datatype_representation"


def _read_resource(path: Path, expected_kind: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"Invalid {expected_kind} definition {path}: {error}") from error
    if not isinstance(value, dict):
        raise ValueError(f"{expected_kind} definition must be a JSON object: {path}")
    kind = str(value.get("kind") or expected_kind).replace("-", "_")
    if kind != expected_kind:
        raise ValueError(f"Expected kind={expected_kind!r}, found {kind!r}: {path}")
    value["kind"] = expected_kind
    if not str(value.get("id") or "").strip():
        raise ValueError(f"{expected_kind} definition requires id: {path}")
    if expected_kind == REPRESENTATION_KIND and not str(value.get("implements") or "").strip():
        raise ValueError(f"Datatype representation requires implements: {path}")
    return value


def _records(workspace_root: Path, directory: str, kind: str, source: str, workspace_id: str) -> list[dict[str, Any]]:
    resource_dir = workspace_root / directory
    if not resource_dir.is_dir():
        return []
    records: list[dict[str, Any]] = []
    for path in sorted(resource_dir.glob("*.json"), key=lambda item: item.name.lower()):
        record: dict[str, Any] = {
            "path": path.relative_to(workspace_root).as_posix(),
            "source": source,
            "workspaceId": workspace_id,
        }
        try:
            document = _read_resource(path, kind)
            record["document"] = document
            record["convention"] = "canonical" if path.name.endswith(f".{kind}.json") else "legacy-filename"
        except ValueError as error:
            record["error"] = str(error)
        records.append(record)
    return records


def _effective(workspace_root: Path, directory: str, kind: str, *, workspaces_root: Path = DEFAULT_WORKSPACES_ROOT) -> list[dict[str, Any]]:
    combined: dict[str, dict[str, Any]] = {}
    shared_root = workspaces_root / SHARED_WORKSPACE_ID
    for record in _records(shared_root, directory, kind, "shared", SHARED_WORKSPACE_ID):
        document = record.get("document") or {}
        combined[str(document.get("id") or record["path"])] = record
    if workspace_root.name != SHARED_WORKSPACE_ID:
        for record in _records(workspace_root, directory, kind, "workspace", workspace_root.name):
            document = record.get("document") or {}
            combined[str(document.get("id") or record["path"])] = record
    return sorted(combined.values(), key=lambda item: str((item.get("document") or {}).get("label") or item["path"]).lower())


def load_workspace_datatype_records(workspace_root: Path, *, workspaces_root: Path = DEFAULT_WORKSPACES_ROOT) -> list[dict[str, Any]]:
    return _effective(workspace_root, DATATYPE_DIRECTORY, DATATYPE_KIND, workspaces_root=workspaces_root)


def load_workspace_representation_records(workspace_root: Path, *, workspaces_root: Path = DEFAULT_WORKSPACES_ROOT) -> list[dict[str, Any]]:
    return _effective(workspace_root, REPRESENTATION_DIRECTORY, REPRESENTATION_KIND, workspaces_root=workspaces_root)


def resolve_datatype_representation(workspace_root: Path, datatype_id: str, requested: str | None = None, *, workspaces_root: Path = DEFAULT_WORKSPACES_ROOT) -> dict[str, Any]:
    datatypes = {str((record.get("document") or {}).get("id")): record for record in load_workspace_datatype_records(workspace_root, workspaces_root=workspaces_root)}
    representations = {str((record.get("document") or {}).get("id")): record for record in load_workspace_representation_records(workspace_root, workspaces_root=workspaces_root)}
    datatype_record = datatypes.get(datatype_id)
    if not datatype_record:
        raise KeyError(f"datatype not found: {datatype_id}")
    datatype = datatype_record["document"]
    selection = datatype.get("representationSelection") or {}
    variants = [str(value) for value in selection.get("variants") or []]
    chosen = requested or selection.get("default") or (variants[0] if variants else None)
    if not chosen:
        raise ValueError(f"datatype has no representation variant: {datatype_id}")
    if variants and chosen not in variants:
        raise ValueError(f"representation {chosen} is not allowed by datatype {datatype_id}")
    representation_record = representations.get(str(chosen))
    if not representation_record:
        raise KeyError(f"datatype representation not found: {chosen}")
    representation = representation_record["document"]
    if representation.get("implements") != datatype_id:
        raise ValueError(f"representation {chosen} does not implement {datatype_id}")
    return {
        "datatype": datatype,
        "datatypeRecord": datatype_record,
        "representation": representation,
        "representationRecord": representation_record,
    }


def representation_graph(workspace_root: Path, *, workspaces_root: Path = DEFAULT_WORKSPACES_ROOT) -> dict[str, Any]:
    datatypes = load_workspace_datatype_records(workspace_root, workspaces_root=workspaces_root)
    representations = load_workspace_representation_records(workspace_root, workspaces_root=workspaces_root)
    by_datatype: dict[str, list[str]] = {}
    for record in representations:
        document = record.get("document") or {}
        datatype_id = str(document.get("implements") or "")
        if datatype_id:
            by_datatype.setdefault(datatype_id, []).append(str(document.get("id")))
    return {
        "datatypes": datatypes,
        "representations": representations,
        "representationIdsByDatatype": {key: sorted(values) for key, values in sorted(by_datatype.items())},
    }
