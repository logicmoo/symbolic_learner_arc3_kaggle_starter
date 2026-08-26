# Filesystem Resource Model

[Back to repository README](../../../README.md)

Detailed negotiated inheritance semantics are defined in
[Specialization Inheritance Model](SPECIALIZATION_INHERITANCE_MODEL.md).

## Principle

The filesystem provider is the source of truth for semantic artifacts. Abstract specifications and concrete alternatives may be separate documents or top-level forms in one MeTTa file.

## Resource Families

Current conventions include:

- `operation` (roots and implementation specializations)
- `semantic_datatype` / `representation_datatype` / `concrete_datatype`
- `prompt` (roots and wording specializations)
- `backend` / `model` (model and preset specializations)
- `workflow`
- `goal`
- `planning_strategy`
- `atomspace`
- `model_policy` / `model_policy_variant`
- `benchmark_policy` / `benchmark_result`

Runtime workflow and Goal Run records are durable SQLite data because they are append-oriented execution evidence. Their selected Goal, Plan, Context, workflow, policy, and benchmark definitions remain filesystem resources.

## Bidirectional many-to-many relationships

Specialization status is structural, not a separate kind. A resource is an implicit specialization when its `implements` policy map names another resource. Same-kind links represent interchangeable implementations or variants; cross-kind links let a representation implement a semantic datatype and a concrete datatype implement a representation.

Every specification/alternative family uses the same three flat fields: `implements`, `specializations`, and `preferredSpecialization`. Both directions store policy maps. The specialization's `implements[parent]` entry declares what it will borrow or exclude; the parent's `specializations[child]` entry declares what it will lend or withhold. `children` remains available for future resource-specific structures and must not represent interchangeable alternatives.

This is an inheritance hierarchy. Each ID in `implements` is conceptually a
parent contract from which the specialization may receive fields, defaults,
constraints, and behavior. `specializations` is the reverse index maintained on
that parent. The persisted relationship is always named `implements`; “parent”
describes its inheritance role rather than a second pointer field.

How much flows from a parent is family-specific resolution behavior, not encoded
by changing the relationship name. Resolvers must define which fields inherit,
which child values override them, and expose resolved provenance so the editor
can show what was declared locally versus inherited.

Abstractness is the amount of implementation still missing for the resource to
get its job done. It is not determined solely by being a root or by inheritance
depth. A specialization may satisfy only part of a parent's contract, remain
abstract, and expose further specializations. A resource becomes concrete when
its required behavior, bindings, constraints, and execution route are resolved
enough to perform the job. Runtime resolution may therefore traverse several
`implements` edges before reaching a runnable specialization.

Abstractness is derived UI state and must not be persisted as an authoritative
flag. The editor recomputes it from the current draft, its resolved inheritance
chain, and family-specific job requirements. It should display a useful status
such as **abstract**, **partial**, **concrete**, or **runnable**, together with the unresolved
behavior, bindings, constraints, or execution route that produced that status.
The runtime still performs authoritative validation before execution.

Concreteness is contextual and reversible. Multiple `implements` parents may
contribute different required pieces. Removing an edge, losing or disabling a
parent, changing a workspace override, or making an inherited binding
unresolvable can turn a previously runnable resource back into partial or
abstract. The UI must therefore invalidate and recompute derived status for the
changed resource and all affected specializations, and explain which parent or
obligation was lost.

Policy maps are required even when there is only one relationship. This permits one specialization to implement multiple specifications with a different borrow/lend agreement on every edge. `preferredSpecialization` stays on each implemented resource because the same specialization can have a different priority for each contract. Run `node scripts/sync_resource_relationships.mjs` after bulk resource edits to normalize pointers and add missing backlinks.

`preferredSpecialization` is the implemented resource's single default/fallback specialization. Future
policy-driven selection must use a separate ordered priority-list field rather
than changing the pointer's type. The intended shape is a named map such as:

```json
{
  "preferredSpecialization": "accurate_specialization",
  "specializationPriorities": {
    "bySpeed": ["fast_specialization", "balanced_specialization", "accurate_specialization"],
    "byAccuracy": ["accurate_specialization", "balanced_specialization", "fast_specialization"]
  }
}
```

The priority profile selected by a workflow or policy may reorder candidates;
the single preferred specialization remains the deterministic fallback.

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

## API and Safety

Workspace snapshots enumerate effective resources and editable files. File reads/writes must remain inside the resolved workspace root, accept supported text formats only, infer and canonicalize JSON resource kinds, and preserve UTF-8. New resource families require loaders, snapshot/API exposure, override tests, and canonical path tests before UI data is displayed.
