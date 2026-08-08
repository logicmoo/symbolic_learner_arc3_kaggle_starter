# Filesystem Resource Model

[Back to repository README](../../../README.md)

## Principle

The filesystem is the source of truth for semantic artifacts. Abstract specifications and concrete alternatives are independent JSON documents rather than entries folded into one catalog.

## Resource Families

Current conventions include:

- `operation` / `operation_implementation`
- `semantic_datatype` / `representation_datatype` / `concrete_datatype`
- `prompt` / `prompt_implementation`
- `backend` / `model` / `profile`
- `workflow`
- `goal` / `goal_variant`
- `plan` / `plan_variant`
- `context` / `context_variant`
- `model_policy` / `model_policy_variant`
- `benchmark_policy` / `benchmark_result`

Runtime workflow and Goal Run records are durable SQLite data because they are append-oriented execution evidence. Their selected Goal, Plan, Context, workflow, policy, and benchmark definitions remain filesystem resources.

## Bidirectional many-to-many relationships

Every specification/alternative family uses the same three flat fields: `parents`, `children`, and `preferredChild`. Both sides store explicit arrays, so an operation may contain `"children": ["python_echo"]` while that implementation contains `"parents": ["echo"]`. The resource kinds give these generic links their domain meaning—implementation, representation, variant, or another relationship shown by the editor.

Arrays are required even when there is only one relationship. This permits one alternative to satisfy multiple specifications. `preferredChild` stays on each parent because the same child can have a different priority under different specifications. Run `node scripts/sync_resource_relationships.mjs` after bulk resource edits to normalize pointers and add missing backlinks.

Canonical filenames carry the kind, for example `shared.echo.operation.metta`, `image.semantic_datatype.metta`, `bitmap.representation_datatype.metta`, and `png.concrete_datatype.metta`. A file may contain multiple top-level resources; the provider identifies and updates each resource independently by `id`.

Workspace paths are lifecycle-first and then kind-specific:

- `design/operations/` and `design/operation_implementations/`
- `design/semantic_datatypes/`, `design/representation_datatypes/`, and `design/concrete_datatypes/`
- `design/goals/` and `design/goal_variants/`
- `design/atomspaces/` and `design/atomspace_variants/`
- `design/backends/`, `design/models/`, and `design/profiles/`
- `runtime/goal_runs/`, `runtime/workflow_runs/`, `runtime/execs/`, `runtime/events/`, `runtime/states/`, `runtime/contexts/`, and `runtime/logs/`

The reader accepts legacy root-level family directories for existing workspaces. New resources are saved under `design/<plural-kind>/`. Shared normally has no runtime records. `policies/` remains a deliberately mixed family, while `docs/` is outside the JSON resource hierarchy.

## Inheritance and Overrides

The `shared` workspace provides inherited defaults. A project workspace may add resources or override an inherited resource by semantic identity. API records must identify whether their effective document came from `shared` or the selected workspace. Editors saving an inherited resource into a project must create a workspace-local override rather than modify the shared file.

## API and Safety

Workspace snapshots enumerate effective resources and editable files. File reads/writes must remain inside the resolved workspace root, accept supported text formats only, infer and canonicalize JSON resource kinds, and preserve UTF-8. New resource families require loaders, snapshot/API exposure, override tests, and canonical path tests before UI data is displayed.
