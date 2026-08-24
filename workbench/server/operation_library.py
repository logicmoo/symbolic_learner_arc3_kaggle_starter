from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable, Iterable

from metta_resource_codec import json_document_to_metta
from resource_relationships import points_to, relationship_ids
from workspace_inheritance import effective_workspace_layers, layer_source
from resource_store import get_filesystem_provider


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_WORKSPACES_ROOT = REPOSITORY_ROOT / "workbench" / "workspaces"
SHARED_WORKSPACE_ID = "shared_library_system"
# Concrete implementations are operations whose same-kind parent is another
# operation.  Keep the legacy spelling readable during migration, but never
# expose it beyond validation.
OPERATION_KINDS = {"operation", "operation_implementation"}
OPERATION_DIRECTORIES = ("design/operations", "design/operation_implementations", "operations", "operation_implementations")
AUTOMATIC_LLM_FALLBACK_SUFFIX = ".automatic_llm_fallback"


def automatic_llm_fallback_id(operation_id: str) -> str:
    return f"{operation_id}{AUTOMATIC_LLM_FALLBACK_SUFFIX}"


def automatic_llm_fallback(operation: dict[str, Any]) -> dict[str, Any]:
    """Build an ephemeral LLM implementation from an abstract contract.

    This is deliberately not a filesystem resource. Normal resolution prefers
    a declared implementation, but callers may explicitly select the fallback
    for a one-off playground or runtime invocation.
    """
    operation_id = str(operation["id"])
    label = str(operation.get("label") or operation_id)
    description = str(operation.get("description") or "Perform the declared operation.")
    inputs = dict(operation.get("inputs") or {})
    outputs = dict(operation.get("outputs") or {})
    operation_metta = json_document_to_metta(operation).strip()
    prompt = "\n".join(
        (
            "No concrete implementation exists for this operation. You are its automatic LLM fallback.",
            "Do the best you can to perform the operation while respecting its declared contracts.",
            f'Execute the operation "{label}".',
            f"Operation description: {description}",
            f"Declared input contract: {json.dumps(inputs, ensure_ascii=False, sort_keys=True)}",
            f"Declared output contract: {json.dumps(outputs, ensure_ascii=False, sort_keys=True)}",
            "Return exactly one valid JSON object using the declared output field names.",
            "Do not add Markdown fences or commentary outside the JSON object.",
            "Values under example_execute, including default values, are examples only.",
            "Never use an example/default value when an authoritative runtime input is supplied after the resource.",
            "The complete operation resource follows in MeTTa; use every relevant field when making your best attempt:",
            operation_metta,
        )
    )
    parameters: dict[str, Any] = {
        "promptPrefix": prompt,
        "parseJson": True,
        "responseFormat": "json_object",
        "automaticFallback": True,
    }
    if len(inputs) == 1:
        parameters["inputBinding"] = next(iter(inputs))
    return {
        "kind": "operation",
        "id": automatic_llm_fallback_id(operation_id),
        "label": f"{label} / Automatic LLM fallback",
        "description": "Runtime-generated fallback derived from the operation name, description, and contracts.",
        "implementation": "llm.complete",
        "inputs": inputs,
        "outputs": outputs,
        "modelSelection": {"models": ["asicloud-asi1-mini"], "strategy": "single"},
        "parameters": parameters,
        "parents": [operation_id],
        "virtual": True,
    }


def _validate_operation(value: Any, path: Path) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"Operation definition must be a JSON object: {path}")
    raw_kind = str(value.get("kind") or "operation")
    kind = raw_kind.replace("-", "_")
    if kind not in OPERATION_KINDS:
        raise ValueError(f"Operation definition must declare kind='operation' or kind='operation_implementation': {path}")
    value["kind"] = "operation"
    if not str(value.get("id") or "").strip():
        raise ValueError(f"Operation definition requires id: {path}")
    if kind == "operation_implementation" and not relationship_ids(value.get("parents")):
        raise ValueError(f"Legacy operation implementation requires parents: {path}")
    if relationship_ids(value.get("parents")):
        if not str(value.get("implementation") or "").strip():
            raise ValueError(f"Operation implementation requires implementation: {path}")
    return value


def read_operation_file(path: Path) -> dict[str, Any]:
    try:
        return _validate_operation(get_filesystem_provider().read_json_documents(path)[0], path)
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"Invalid operation definition {path}: {error}") from error


def _operation_records(workspace_root: Path, source: str, workspace_id: str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    paths = get_filesystem_provider().glob(workspace_root, OPERATION_DIRECTORIES)
    for path in sorted(paths, key=lambda item: item.name.lower()):
        try:
            documents = get_filesystem_provider().read_json_documents(path)
        except (OSError, json.JSONDecodeError, ValueError) as error:
            records.append({"path": path.relative_to(workspace_root).as_posix(), "source": source, "workspaceId": workspace_id, "error": str(error)})
            continue
        for resource_index, value in enumerate(documents):
            record: dict[str, Any] = {"path": path.relative_to(workspace_root).as_posix(), "source": source, "workspaceId": workspace_id, "resourceIndex": resource_index}
            try:
                document = _validate_operation(value, path)
                record["document"] = document
                expected = ".operation.json"
                record["convention"] = "canonical" if path.name.endswith(expected) else "multi-resource" if len(documents) > 1 else "legacy-filename"
            except ValueError as error:
                record["error"] = str(error)
            records.append(record)
    return records


def load_shared_operation_resource_records(workspaces_root: Path = DEFAULT_WORKSPACES_ROOT) -> list[dict[str, Any]]:
    return _operation_records(workspaces_root / SHARED_WORKSPACE_ID, "shared", SHARED_WORKSPACE_ID)


def load_workspace_local_operation_resource_records(workspace_root: Path) -> list[dict[str, Any]]:
    if workspace_root.name == SHARED_WORKSPACE_ID:
        return []
    return _operation_records(workspace_root, "workspace", workspace_root.name)


def _effective_resources(workspace_root: Path, *, workspaces_root: Path = DEFAULT_WORKSPACES_ROOT) -> list[dict[str, Any]]:
    combined: dict[str, dict[str, Any]] = {}
    for layer in effective_workspace_layers(workspace_root, workspaces_root):
        for record in _operation_records(layer, layer_source(layer, workspace_root), layer.name):
            document = record.get("document") or {}
            combined[str(document.get("id") or record["path"])] = record
    return sorted(combined.values(), key=lambda item: str((item.get("document") or {}).get("label") or item["path"]).lower())


def load_shared_operation_records(workspaces_root: Path = DEFAULT_WORKSPACES_ROOT) -> list[dict[str, Any]]:
    return [r for r in load_shared_operation_resource_records(workspaces_root) if not relationship_ids((r.get("document") or {}).get("parents"))]


def load_shared_operation_implementation_records(workspaces_root: Path = DEFAULT_WORKSPACES_ROOT) -> list[dict[str, Any]]:
    return [r for r in load_shared_operation_resource_records(workspaces_root) if relationship_ids((r.get("document") or {}).get("parents"))]


def load_workspace_operation_records(workspace_root: Path, *, workspaces_root: Path = DEFAULT_WORKSPACES_ROOT) -> list[dict[str, Any]]:
    return [r for r in _effective_resources(workspace_root, workspaces_root=workspaces_root) if not relationship_ids((r.get("document") or {}).get("parents"))]


def load_workspace_operation_implementation_records(workspace_root: Path, *, workspaces_root: Path = DEFAULT_WORKSPACES_ROOT) -> list[dict[str, Any]]:
    return [r for r in _effective_resources(workspace_root, workspaces_root=workspaces_root) if relationship_ids((r.get("document") or {}).get("parents"))]


def resolve_operation_implementation(workspace_root: Path, operation_id: str, requested: str | None = None, *, workspaces_root: Path = DEFAULT_WORKSPACES_ROOT, is_known_route: Callable[[str], bool] | None = None) -> dict[str, Any]:
    operations = {str((r.get("document") or {}).get("id")): r for r in load_workspace_operation_records(workspace_root, workspaces_root=workspaces_root)}
    implementations = {str((r.get("document") or {}).get("id")): r for r in load_workspace_operation_implementation_records(workspace_root, workspaces_root=workspaces_root)}
    operation_record = operations.get(operation_id)
    if not operation_record:
        raise KeyError(f"operation not found: {operation_id}")
    operation = operation_record["document"]
    fallback = automatic_llm_fallback(operation)
    fallback_id = str(fallback["id"])
    if requested == fallback_id:
        return {
            "operation": operation,
            "operationRecord": operation_record,
            "implementation": fallback,
            "implementationRecord": {
                "path": "runtime://automatic-llm-fallback",
                "source": "runtime",
                "workspaceId": workspace_root.name,
                "document": fallback,
                "virtual": True,
            },
            "fallback": True,
        }
    declared_variants = relationship_ids(operation.get("children"))
    reverse_variants = [
        implementation_id
        for implementation_id, record in implementations.items()
        if points_to(record.get("document") or {}, "parents", operation_id)
    ]
    variants = list(dict.fromkeys([*declared_variants, *reverse_variants]))
    if not variants:
        direct_route = str(operation.get("implementation") or "").strip()
        # A declared route is only executable when the engine registers a handler
        # for it. Abstract subject-matter labels (e.g. vision.segment, symbolic.identity)
        # have no handler, so they must degrade to the automatic LLM fallback rather
        # than being handed to the engine as an unknown implementation.
        direct_executable = bool(direct_route) and (is_known_route is None or is_known_route(direct_route))
        if direct_executable:
            if requested and requested != operation_id:
                raise ValueError(f"implementation {requested} is not allowed by operation {operation_id}")
            return {
                "operation": operation,
                "operationRecord": operation_record,
                "implementation": operation,
                "implementationRecord": operation_record,
                "direct": True,
            }
        allowed_requests = {fallback_id}
        if direct_route:
            allowed_requests.add(operation_id)
        if requested and requested not in allowed_requests:
            raise ValueError(f"implementation {requested} is not allowed by operation {operation_id}")
        return {
            "operation": operation,
            "operationRecord": operation_record,
            "implementation": fallback,
            "implementationRecord": {
                "path": "runtime://automatic-llm-fallback",
                "source": "runtime",
                "workspaceId": workspace_root.name,
                "document": fallback,
                "virtual": True,
            },
            "fallback": True,
        }
    chosen = requested or operation.get("preferredChild") or (variants[0] if variants else None)
    if not chosen:
        raise ValueError(f"operation has no implementation variant: {operation_id}")
    if chosen not in variants:
        raise ValueError(f"implementation {chosen} is not allowed by operation {operation_id}")
    record = implementations.get(str(chosen))
    if not record:
        raise KeyError(f"operation implementation not found: {chosen}")
    implementation = record["document"]
    if not points_to(implementation, "parents", operation_id):
        raise ValueError(f"implementation {chosen} does not implement {operation_id}")
    return {"operation": operation, "operationRecord": operation_record, "implementation": implementation, "implementationRecord": record}


def load_shared_operation_documents(workspaces_root: Path = DEFAULT_WORKSPACES_ROOT) -> list[dict[str, Any]]:
    return [record["document"] for record in load_shared_operation_records(workspaces_root) if "document" in record]


def load_effective_operation_documents(workspace_root: Path, *, workspaces_root: Path = DEFAULT_WORKSPACES_ROOT) -> list[dict[str, Any]]:
    return [record["document"] for record in load_workspace_operation_records(workspace_root, workspaces_root=workspaces_root) if "document" in record]


def operation_ids(documents: Iterable[dict[str, Any]]) -> set[str]:
    return {str(document["id"]) for document in documents if document.get("id")}


def legacy_catalog_view(documents: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for document in documents:
        inputs = document.get("inputs") or {}
        outputs = document.get("outputs") or {}
        left = " + ".join(inputs) or "∅"
        right = " + ".join(outputs) or "∅"
        routes = str(document.get("preferredChild") or document.get("implementation") or "")
        result.append({"id": document["id"], "label": document.get("label") or document["id"], "ports": f"{left} → {right}", "routes": routes, "definition": document, "source": "workbench/workspaces/shared_library_system/design/operations"})
    return sorted(result, key=lambda item: str(item["label"]).lower())
