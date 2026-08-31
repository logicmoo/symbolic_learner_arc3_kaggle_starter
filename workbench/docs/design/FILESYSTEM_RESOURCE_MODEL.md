# Filesystem Resource Model

[Back to repository README](../../../README.md)

Detailed relationship semantics are defined in
[Resource Relationship Model](RESOURCE_RELATIONSHIP_MODEL.md).

## Principle

The filesystem provider is the source of truth for semantic artifacts. Abstract specifications and concrete alternatives may be separate documents or top-level forms in one MeTTa file.

## Resource Families

Current conventions include:

- `operation` (roots and implementations)
- `semantic_datatype` / `representation_datatype` / `concrete_datatype`
- `prompt` (roots and wording implementations)
- `backend` / `model` (models and presets)
- `workflow`
- `goal`
- `planning_strategy`
- `atomspace`
- `model_policy` / `model_policy_variant`
- `benchmark_policy` / `benchmark_result`

Runtime workflow and Goal Run records are durable SQLite data because they are append-oriented execution evidence. Their selected Goal, Plan, Context, workflow, policy, and benchmark definitions remain filesystem resources.

## Bidirectional many-to-many relationships

Resources use three independent map pairs:

- `implements` / `implementedBy` for implementation, classification, and
  interface conformance;
- `inheritsFrom` / `inheritedBy` for negotiated property inheritance;
- `dependsOn` / `dependedOnBy` for availability.

`implements` values are empty maps. `inheritsFrom` values declare
`borrow`/`exclude`, while `inheritedBy` values declare `lend`/`withhold`.
`preferredImplementation` optionally selects one key from `implementedBy`.
Generic `parents`, `children`, and `inherits` are not resource relationship
fields.

Abstractness is the amount of implementation still missing for the resource to
get its job done. It is not determined solely by being a root or by inheritance
depth. A specialization may satisfy only part of a parent's contract, remain
abstract, and expose further implementations. A resource becomes concrete when
its required behavior, bindings, constraints, and execution route are resolved
enough to perform the job. Runtime resolution may therefore traverse several
`implements` edges before reaching a runnable implementation.

Abstractness is derived UI state and must not be persisted as an authoritative
flag. The editor recomputes it from the current draft, its resolved inheritance
chain, and family-specific job requirements. It should display a useful status
such as **abstract**, **partial**, **concrete**, or **runnable**, together with the unresolved
behavior, bindings, constraints, or execution route that produced that status.
The runtime still performs authoritative validation before execution.

Concreteness is contextual and reversible. Multiple `inheritsFrom` parents may
contribute different required pieces. Removing an edge, changing a workspace
override, or making an inherited binding
unresolvable can turn a previously runnable resource back into partial or
abstract. The UI must therefore invalidate and recompute derived status for the
changed resource and all affected implementations, and explain which parent or
obligation was lost.

Property-inheritance policy maps are required even when there is only one
inheritance edge. Run `python scripts/migrate_resource_relationships.py` after
bulk legacy edits to normalize canonical names and reverse links.

`preferredImplementation` is the implemented resource's single deterministic
default/fallback implementation. It is a string selector, not a Boolean or a
child-side property. Speed- and quality-specific preferred fields are not
defined.

Canonical filenames carry the kind, for example `shared.echo.operation.metta`, `image.semantic_datatype.metta`, `bitmap.representation_datatype.metta`, and `png.concrete_datatype.metta`. A file may contain multiple top-level resources; the provider identifies and updates each resource independently by `id`.

Workspace paths are lifecycle-first and then kind-specific:

- `design/operations/`
- `design/semantic_datatypes/`, `design/representation_datatypes/`, and `design/concrete_datatypes/`
- `design/goals/`, `design/planning_strategies/`, and `design/atomspaces/`
- `design/prompts/`
- `design/backends/` and `design/models/`
- `knowledge/data/` and `knowledge/artifacts/`
- `runtime/goal_runs/`, `runtime/workflow_runs/`, `runtime/execs/`, `runtime/events/`, `runtime/states/`, `runtime/contexts/`, and `runtime/logs/`

The reader accepts legacy root-level family directories for existing workspaces. New specification resources are saved under `design/<plural-kind>/`. Shared normally has no runtime records. `knowledge/data/` holds imported or authored workspace values, while `knowledge/artifacts/` holds persisted outputs that can be inspected and reused. `policies/` remains a deliberately mixed family, while `docs/` is outside the JSON resource hierarchy.

## Inheritance and Overrides

The `shared` workspace provides inherited defaults. A project workspace may add resources or override an inherited resource by semantic identity. API records must identify whether their effective document came from `shared` or the selected workspace. Editors saving an inherited resource into a project must create a workspace-local override rather than modify the shared file.

Inheritance, preference, and availability are distinct graphs:

- `implements` / `implementedBy` declares implementation or classification.
- `inheritsFrom` / `inheritedBy` negotiates inherited fields.
- `preferredImplementation` selects the default child from `implementedBy`.
- `dependsOn` / `dependedOnBy` controls effective enabled state and optional
  enable/disable propagation.

A disabled inheritance or implementation parent does not disable a resource
unless that resource also declares the parent in `dependsOn`. Conversely, a
dependency contributes no fields unless it is independently declared in
`inheritsFrom`.

## API and Safety

Workspace snapshots enumerate effective resources and editable files. File reads/writes must remain inside the resolved workspace root, accept supported text formats only, infer and canonicalize JSON resource kinds, and preserve UTF-8. New resource families require loaders, snapshot/API exposure, override tests, and canonical path tests before UI data is displayed.
