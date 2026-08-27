# Specialization Inheritance Model

[Back to repository README](../../../README.md) ·
[Filesystem resource model](FILESYSTEM_RESOURCE_MODEL.md)

## Purpose

Workbench resources form negotiated inheritance hierarchies. A general resource
describes a job or contract. A specialization can implement some or all of that
contract, borrow selected content from one or more implemented resources, add
local details, and remain abstract until enough of the job is implemented.

This model replaces generic specialization relationship fields such as
`parents` and `children`.

## Canonical Relationship Fields

The upward relationship is `implements`. It is a map on the specialization,
keyed by the IDs of the contracts it implements:

```json
{
  "id": "echo.python",
  "implements": {
    "echo": {
      "borrow": ["*"],
      "exclude": ["description"]
    }
  }
}
```

The downward relationship is `specializations`. It is a map on the implemented
resource, keyed by specialization ID:

```json
{
  "id": "echo",
  "specializations": {
    "echo.python": {
      "lend": ["*"],
      "withhold": [
        "id",
        "label",
        "description",
        "implements",
        "specializations",
        "preferredSpecialization"
      ]
    }
  },
  "preferredSpecialization": "echo.python"
}
```

Both maps are explicit, bidirectional, and many-to-many.

## Borrow/Lend Negotiation

Inheritance is negotiated rather than copied in one direction:

- `borrow` lists the field paths a specialization requests from an implemented
  resource.
- `exclude` lists requested paths the specialization refuses to borrow.
- `lend` lists the field paths the implemented resource permits that
  specialization to receive.
- `withhold` lists paths the implemented resource refuses to lend.

For a field path `p`:

```text
inherits(p) =
  child borrows p
  AND parent lends p
  AND child does not exclude p
  AND parent does not withhold p
```

The default policy preserves normal inheritance while protecting identity and
relationship metadata:

```json
{
  "childDefault": {
    "borrow": ["*"],
    "exclude": []
  },
  "parentDefault": {
    "lend": ["*"],
    "withhold": [
      "id",
      "label",
      "description",
      "implements",
      "specializations",
      "preferredSpecialization"
    ]
  }
}
```

A child never inherits its parent's `id` under the default policy.

Selectors use dot paths. `*` matches every path, and `defaults.*` matches all
descendants of `defaults`. A child-local value always overrides an inherited
value after negotiation.

## Multiple Implemented Resources

A specialization may implement several resources. Each edge has its own
borrow/exclude and lend/withhold agreement.

If multiple implemented resources supply the same path with different values
and the specialization does not override that path locally, resolution must
report a conflict. It must not silently choose a parent by filesystem order.
The resource remains partial until the conflict is resolved by a local value or
more selective policies.

Cycles are invalid for inheritance resolution. The UI and runtime must show the
cycle rather than truncate it or return a success-shaped fallback.

## Preferred Specialization and Upward Behavior

Inheritance is not purely downward. A general resource can derive effective
behavior from its `preferredSpecialization`.

The parent retains its own identity and contract. It does not copy the child's
`id` or mutate its source. Instead, resolution may delegate the parent's job to
the preferred specialization and expose that specialization's resolved
execution behavior as the parent's effective behavior.

If the preferred specialization is abstract, missing, disabled, conflicted, or
otherwise unrunnable, the parent cannot claim runnable status from it. Runtime
resolution may continue through deeper preferred-specialization links until it
finds a runnable resource or reports the unresolved obligation.

## Derived Abstractness

Abstractness is the amount of implementation still missing for a resource to
get its job done.

It is not:

- a persisted boolean;
- synonymous with being a hierarchy root;
- determined only by whether `implements` is present;
- guaranteed to decrease with inheritance depth.

A specialization may implement part of a contract and remain abstract. A
previously concrete resource can become partial or abstract when:

- an `implements` edge is removed;
- a parent becomes unavailable or disabled;
- a parent withholds a required field;
- a child excludes a required field;
- a workspace override removes an inherited value;
- two implemented resources provide an unresolved conflict;
- the preferred specialization stops being runnable.

The UI derives and recomputes one of these presentation states:

| State | Meaning |
|---|---|
| Abstract | Required job obligations remain substantially unspecified. |
| Partial | Some implementation exists, but named obligations or conflicts remain. |
| Concrete | The resource contract is fully specified for a non-executable job. |
| Runnable | Required behavior and execution bindings resolve successfully. |

The runtime remains the authoritative execution validator.

## UI Contract

The Resource and Inheritance editor must:

1. Display `implements` as parent rows with editable **BORROW** and **EXCLUDE**
   selectors.
2. Display `specializations` as child rows with editable **LEND** and
   **WITHHOLD** selectors.
3. Default WITHHOLD to identity and hierarchy fields, including `id`.
4. Show local, borrowed, overridden, withheld, excluded, conflicted, and missing
   fields with provenance.
5. Derive Abstract, Partial, Concrete, or Runnable from the current unsaved
   draft plus the resolved hierarchy.
6. Recompute immediately when a policy, edge, parent, child, preferred
   specialization, availability state, or workspace override changes.
7. Explain every downgrade with the missing parent, conflict, withheld field,
   excluded field, or unresolved execution obligation.
8. Never persist the derived status as authoritative source data.

## Runtime Contract

Before execution, the resolver must:

1. Validate bidirectional relationship maps.
2. Reject missing implemented resources and inheritance cycles.
3. Apply borrow/lend negotiation per field path.
4. Reject unresolved multi-parent conflicts.
5. Apply child-local overrides.
6. Evaluate family-specific completeness requirements.
7. Follow `preferredSpecialization` when the current resource delegates behavior.
8. Return the complete resolution path and field provenance.
9. Execute only a resource whose resolved job is runnable.

## MeTTa Shape

The same model serializes to MeTTa:

```metta
(
  (kind operation)
  (id echo.python)
  (implements (
    (echo (
      (borrow ([] "*"))
      (exclude ([] description))
    ))
  ))
  (implementation python.callable)
)
```

```metta
(
  (kind operation)
  (id echo)
  (specializations (
    (echo.python (
      (lend ([] "*"))
      (withhold ([]
        id
        label
        description
        implements
        specializations
        preferredSpecialization
      ))
    ))
  ))
  (preferredSpecialization echo.python)
)
```

## Invariants

- `implements` and `specializations` are maps, never plain ID arrays.
- Every `implements[A]` edge has a matching `A.specializations[child]` edge.
- `preferredSpecialization` names a key in `specializations`.
- `id` is withheld by default.
- Local source is never overwritten by inherited values.
- Derived abstractness is contextual, reversible, and UI-only.
- Genuine domain-specific child structures may still use their own explicit
  fields; they must not reuse `specializations` unless they are inheritance
  alternatives.
