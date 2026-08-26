from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

from prompt_library import (
    load_workspace_prompt_implementation_records,
    load_workspace_prompt_records,
)
from operation_library import (
    DEFAULT_WORKSPACES_ROOT,
    SHARED_WORKSPACE_ID,
    load_workspace_operation_implementation_records,
    load_workspace_operation_records,
)
from resource_relationships import points_to, relationship_ids, resolve_inherited_document
from workspace_inheritance import effective_workspace_layers, layer_source
from resource_store import get_filesystem_provider

DATATYPE_DIRECTORY = "design/semantic_datatypes"
REPRESENTATION_DIRECTORY = "design/representation_datatypes"
CONCRETE_DIRECTORY = "design/concrete_datatypes"
DATATYPE_KIND = "semantic_datatype"
REPRESENTATION_KIND = "representation_datatype"
CONCRETE_KIND = "concrete_datatype"
BUILTIN_INTERFACE_DATATYPES = {"Any"}


def _type_key(value: Any) -> str:
    return "".join(character for character in str(value).casefold() if character.isalnum())


def _implemented_datatypes(document: dict[str, Any]) -> list[str]:
    return relationship_ids(document.get("implements"))


def _read_resource(path: Path, expected_kind: str) -> dict[str, Any]:
    try:
        value = get_filesystem_provider().read_json_documents(path)[0]
    except (OSError, json.JSONDecodeError, ValueError) as error:
        raise ValueError(f"Invalid {expected_kind} definition {path}: {error}") from error
    return _validate_resource(value, path, expected_kind)


def _validate_resource(value: Any, path: Path, expected_kind: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{expected_kind} definition must be a JSON object: {path}")
    kind = str(value.get("kind") or expected_kind).replace("-", "_")
    if kind != expected_kind:
        raise ValueError(f"Expected kind={expected_kind!r}, found {kind!r}: {path}")
    value["kind"] = expected_kind
    if not str(value.get("id") or "").strip():
        raise ValueError(f"{expected_kind} definition requires id: {path}")
    if expected_kind == REPRESENTATION_KIND and not _implemented_datatypes(value):
        raise ValueError(f"Datatype representation requires implements: {path}")
    return value


def _records(workspace_root: Path, directories: tuple[str, ...], kind: str, source: str, workspace_id: str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    paths = get_filesystem_provider().glob(workspace_root, directories)
    for path in sorted(paths, key=lambda item: item.name.lower()):
        try:
            documents = get_filesystem_provider().read_json_documents(path)
        except ValueError as error:
            records.append({"path": path.relative_to(workspace_root).as_posix(), "source": source, "workspaceId": workspace_id, "error": str(error)})
            continue
        for resource_index, raw in enumerate(documents):
            if not isinstance(raw, dict) or str(raw.get("kind") or kind).replace("-", "_") != kind:
                continue
            record: dict[str, Any] = {"path": path.relative_to(workspace_root).as_posix(), "source": source, "workspaceId": workspace_id, "resourceIndex": resource_index}
            try:
                record["document"] = _validate_resource(raw, path, kind)
                record["convention"] = "canonical" if path.name.endswith(f".{kind}.json") else "legacy-filename"
            except ValueError as error:
                record["error"] = str(error)
            records.append(record)
    return records


def _effective(workspace_root: Path, directories: tuple[str, ...], kind: str, *, workspaces_root: Path = DEFAULT_WORKSPACES_ROOT) -> list[dict[str, Any]]:
    combined: dict[str, dict[str, Any]] = {}
    for layer in effective_workspace_layers(workspace_root, workspaces_root):
        for record in _records(layer, directories, kind, layer_source(layer, workspace_root), layer.name):
            document = record.get("document") or {}
            combined[str(document.get("id") or record["path"])] = record
    return sorted(combined.values(), key=lambda item: str((item.get("document") or {}).get("label") or item["path"]).lower())


def load_workspace_datatype_records(workspace_root: Path, *, workspaces_root: Path = DEFAULT_WORKSPACES_ROOT) -> list[dict[str, Any]]:
    return _effective(workspace_root, (DATATYPE_DIRECTORY, "semantic_datatypes", "datatypes"), DATATYPE_KIND, workspaces_root=workspaces_root)


def load_workspace_representation_records(workspace_root: Path, *, workspaces_root: Path = DEFAULT_WORKSPACES_ROOT) -> list[dict[str, Any]]:
    return _effective(workspace_root, (REPRESENTATION_DIRECTORY, "representation_datatypes", "representations"), REPRESENTATION_KIND, workspaces_root=workspaces_root)


def load_workspace_concrete_datatype_records(workspace_root: Path, *, workspaces_root: Path = DEFAULT_WORKSPACES_ROOT) -> list[dict[str, Any]]:
    return _effective(workspace_root, (CONCRETE_DIRECTORY, "concrete_datatypes"), CONCRETE_KIND, workspaces_root=workspaces_root)


def resolve_datatype_representation(workspace_root: Path, datatype_id: str, requested: str | None = None, *, workspaces_root: Path = DEFAULT_WORKSPACES_ROOT) -> dict[str, Any]:
    datatypes = {_type_key((record.get("document") or {}).get("id")): record for record in load_workspace_datatype_records(workspace_root, workspaces_root=workspaces_root)}
    representations = {_type_key((record.get("document") or {}).get("id")): record for record in load_workspace_representation_records(workspace_root, workspaces_root=workspaces_root)}
    datatype_record = datatypes.get(_type_key(datatype_id))
    if not datatype_record:
        raise KeyError(f"datatype not found: {datatype_id}")
    datatype = datatype_record["document"]
    variants = relationship_ids(datatype.get("specializations"))
    chosen = requested or datatype.get("preferredSpecialization") or (variants[0] if variants else None)
    if not chosen:
        raise ValueError(f"datatype has no representation variant: {datatype_id}")
    canonical_variants = {_type_key(variant): variant for variant in variants}
    if variants and _type_key(chosen) not in canonical_variants:
        raise ValueError(f"representation {chosen} is not allowed by datatype {datatype_id}")
    chosen = canonical_variants.get(_type_key(chosen), str(chosen))
    representation_record = representations.get(_type_key(chosen))
    if not representation_record:
        raise KeyError(f"datatype representation not found: {chosen}")
    representation = representation_record["document"]
    if not points_to(representation, "implements", str(datatype.get("id"))):
        raise ValueError(f"representation {chosen} does not implement {datatype_id}")
    records = [
        *datatypes.values(),
        *representations.values(),
        *load_workspace_concrete_datatype_records(workspace_root, workspaces_root=workspaces_root),
    ]
    documents_by_id = {
        str((record.get("document") or {}).get("id")): record["document"]
        for record in records
        if (record.get("document") or {}).get("id")
    }
    datatype_resolution = resolve_inherited_document(datatype, documents_by_id)
    representation_resolution = resolve_inherited_document(representation, documents_by_id)
    blockers = [
        *datatype_resolution["conflicts"],
        *datatype_resolution["missingResources"],
        *datatype_resolution["missingBacklinks"],
        *representation_resolution["conflicts"],
        *representation_resolution["missingResources"],
        *representation_resolution["missingBacklinks"],
    ]
    if blockers:
        raise ValueError(f"datatype inheritance is unresolved for {datatype_id}: {'; '.join(blockers)}")
    return {
        "datatype": datatype_resolution["document"],
        "declaredDatatype": datatype,
        "datatypeRecord": datatype_record,
        "datatypeInheritance": datatype_resolution,
        "representation": representation_resolution["document"],
        "declaredRepresentation": representation,
        "representationInheritance": representation_resolution,
        "representationRecord": representation_record,
    }


def representation_graph(workspace_root: Path, *, workspaces_root: Path = DEFAULT_WORKSPACES_ROOT) -> dict[str, Any]:
    datatypes = load_workspace_datatype_records(workspace_root, workspaces_root=workspaces_root)
    representations = load_workspace_representation_records(workspace_root, workspaces_root=workspaces_root)
    concrete_datatypes = load_workspace_concrete_datatype_records(workspace_root, workspaces_root=workspaces_root)
    by_datatype: dict[str, list[str]] = {}
    for record in representations:
        document = record.get("document") or {}
        for datatype_id in _implemented_datatypes(document):
            by_datatype.setdefault(datatype_id, []).append(str(document.get("id")))
    return {
        "datatypes": datatypes,
        "representations": representations,
        "concreteDatatypes": concrete_datatypes,
        "representationIdsByDatatype": {key: sorted(values) for key, values in sorted(by_datatype.items())},
        "concreteIdsByRepresentation": {
            str((record.get("document") or {}).get("id")): relationship_ids((record.get("document") or {}).get("specializations"))
            for record in representations
            if (record.get("document") or {}).get("id")
        },
    }


def _port_contract_types(value: Any) -> Iterable[tuple[str, str | None]]:
    """Yield (datatype, representation) pairs from old and new port syntax."""
    if isinstance(value, str):
        datatype = value.strip()
        if datatype and not datatype.startswith("$"):
            yield datatype, None
        return
    if isinstance(value, dict):
        datatype = value.get("datatype") or value.get("type")
        representation = value.get("representation")
        if isinstance(datatype, str) and datatype.strip():
            yield datatype, str(representation) if representation else None


def _collect_contract(owner_kind: str, owner_id: str, ports: Any, direction: str, refs: list[dict[str, Any]]) -> None:
    if not isinstance(ports, dict):
        return
    for port, contract in ports.items():
        for datatype, representation in _port_contract_types(contract):
            refs.append({
                "ownerKind": owner_kind,
                "ownerId": owner_id,
                "direction": direction,
                "port": str(port),
                "datatype": datatype,
                "representation": representation,
            })


def interface_type_inventory(
    workspace_root: Path,
    *,
    workspaces_root: Path = DEFAULT_WORKSPACES_ROOT,
) -> dict[str, Any]:
    """Inventory every datatype/representation referenced by executable interfaces.

    This deliberately scans both abstract resources and implementations. The Data
    editor can therefore show types mentioned inside operations, prompt contracts, and
    workflows even when someone forgot to add a first-class definition yet.
    """
    refs: list[dict[str, Any]] = []

    operation_records = [
        *load_workspace_operation_records(workspace_root, workspaces_root=workspaces_root),
        *load_workspace_operation_implementation_records(workspace_root, workspaces_root=workspaces_root),
    ]
    for record in operation_records:
        document = record.get("document") or {}
        owner_id = str(document.get("id") or record.get("path"))
        owner_kind = str(document.get("kind") or "operation")
        _collect_contract(owner_kind, owner_id, document.get("inputs"), "input", refs)
        _collect_contract(owner_kind, owner_id, document.get("outputs"), "output", refs)

    prompt_records = [
        *load_workspace_prompt_records(workspace_root, workspaces_root=workspaces_root),
        *load_workspace_prompt_implementation_records(workspace_root, workspaces_root=workspaces_root),
    ]
    for record in prompt_records:
        document = record.get("document") or {}
        owner_id = str(document.get("id") or record.get("path"))
        owner_kind = str(document.get("kind") or "prompt")
        _collect_contract(owner_kind, owner_id, document.get("inputs"), "input", refs)
        _collect_contract(owner_kind, owner_id, document.get("outputs"), "output", refs)

    resources = get_filesystem_provider()
    workflow_documents: dict[str, dict[str, Any]] = {}
    for layer in effective_workspace_layers(workspace_root, workspaces_root):
        for path in resources.glob(layer, ("design/workflows", "workflows")):
            try:
                documents = resources.read_json_documents(path)
            except (OSError, json.JSONDecodeError, ValueError):
                continue
            for document in documents:
                if not isinstance(document, dict):
                    continue
                if str(document.get("kind") or "workflow") != "workflow":
                    continue
                workflow_documents[str(document.get("id") or path.stem)] = document
    for document in workflow_documents.values():
        owner_id = str(document.get("id") or "workflow")
        _collect_contract("workflow", owner_id, document.get("inputs"), "input", refs)
        _collect_contract("workflow", owner_id, document.get("outputs"), "output", refs)
        steps = document.get("steps") or []
        if isinstance(steps, list):
            for step in steps:
                if not isinstance(step, dict):
                    continue
                step_id = f"{owner_id}/{step.get('id') or 'step'}"
                for direction in ("inputs", "outputs"):
                    contracts = step.get(f"{direction}Contract") or step.get(f"{direction}Types")
                    _collect_contract("workflow_step", step_id, contracts, direction[:-1], refs)

    declared_datatypes = {
        str((record.get("document") or {}).get("id"))
        for record in load_workspace_datatype_records(workspace_root, workspaces_root=workspaces_root)
        if (record.get("document") or {}).get("id")
    }
    declared_representations = {
        str((record.get("document") or {}).get("id"))
        for record in load_workspace_representation_records(workspace_root, workspaces_root=workspaces_root)
        if (record.get("document") or {}).get("id")
    }
    referenced_datatypes = sorted({ref["datatype"] for ref in refs})
    referenced_representations = sorted({ref["representation"] for ref in refs if ref.get("representation")})

    declared_datatype_keys = {_type_key(item) for item in declared_datatypes}
    builtin_datatype_keys = {_type_key(item) for item in BUILTIN_INTERFACE_DATATYPES}
    declared_representation_keys = {_type_key(item) for item in declared_representations}
    return {
        "references": refs,
        "referencedDatatypes": referenced_datatypes,
        "referencedRepresentations": referenced_representations,
        "builtinDatatypes": sorted(BUILTIN_INTERFACE_DATATYPES),
        "undeclaredDatatypes": sorted(item for item in set(referenced_datatypes) if _type_key(item) not in declared_datatype_keys | builtin_datatype_keys),
        "undeclaredRepresentations": sorted(item for item in set(referenced_representations) if _type_key(item) not in declared_representation_keys),
    }
