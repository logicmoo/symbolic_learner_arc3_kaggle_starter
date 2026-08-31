# Resource Relationship Model

[Back to repository README](../../../README.md) ·
[Filesystem resource model](FILESYSTEM_RESOURCE_MODEL.md)

## Purpose

Workbench resources use three independent, bidirectional graphs. No graph
implicitly creates an edge in another graph.

| Purpose | Child to parent | Parent to child |
|---|---|---|
| Availability | `dependsOn` | `dependedOnBy` |
| Implementation/classification | `implements` | `implementedBy` |
| Property inheritance | `inheritsFrom` | `inheritedBy` |

Generic `parents`, `children`, and `inherits` fields are not canonical.

## Implementation and classification

`implements` says which interface, datatype, classification, abstract
operation, prompt, goal, plan, model, or other contract a resource implements.
It carries no property-inheritance policy:

```json
{
  "kind": "operation",
  "id": "echo.python",
  "implements": {
    "echo": {}
  }
}
```

The implemented resource stores the reverse link:

```json
{
  "kind": "operation",
  "id": "echo",
  "implementedBy": {
    "echo.python": {}
  },
  "preferredImplementation": "echo.python"
}
```

`preferredImplementation` is optional. When present, it must name a key in
`implementedBy`. It is a selector stored only on the parent, not a Boolean and
not a child-side relationship. No speed- or quality-specific preferred fields
exist yet.

## Property inheritance

Property inheritance is negotiated exclusively through `inheritsFrom` and
`inheritedBy`.

```json
{
  "id": "echo.python",
  "inheritsFrom": {
    "echo": {
      "borrow": ["*"],
      "exclude": ["description"]
    }
  }
}
```

```json
{
  "id": "echo",
  "inheritedBy": {
    "echo.python": {
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
        "dependedOnBy"
      ]
    }
  }
}
```

For a field path `p`:

```text
inherits(p) =
  child borrows p
  AND parent lends p
  AND child does not exclude p
  AND parent does not withhold p
```

Selectors use dot paths. `*` matches every path and `defaults.*` matches that
subtree. Child-local values override inherited values. Conflicting values from
multiple inheritance parents require an explicit child override. Inheritance
cycles are errors.

`enabled` and all relationship fields are never inherited.

## Availability dependencies

`enabled` is local intent. Effective availability is resolved only through:

```json
{
  "id": "consumer",
  "enabled": true,
  "dependsOn": {
    "provider": {}
  }
}
```

```json
{
  "id": "provider",
  "dependedOnBy": {
    "consumer": {}
  }
}
```

A locally enabled resource is effectively disabled when a required dependency
is disabled, unavailable, cyclic, or invalid. `implements` and `inheritsFrom`
never affect enabled state. Enable/disable propagation may update the selected
resource, dependencies, dependents, or a user-selected combination, but never
rewrites implementation or inheritance edges.

## Relationships may coincide

A concrete resource may implement, inherit properties from, and depend on the
same parent when all three meanings are true:

```json
{
  "id": "BitmapImage",
  "implements": {"Image": {}},
  "inheritsFrom": {
    "Image": {"borrow": ["*"], "exclude": []}
  },
  "dependsOn": {"ImageRuntime": {}}
}
```

Pure classification or interface conformance uses `implements` without
`inheritsFrom`. Property reuse without implementation uses `inheritsFrom`
without `implements`.

## Compatibility

Readers accept legacy `specializations` and `preferredSpecialization`.
Normalization maps them to `implementedBy`, `inheritedBy`, and
`preferredImplementation`. Legacy `implements` entries containing
`borrow`/`exclude` are split into policy-free `implements` plus
`inheritsFrom`. Canonical writers never emit legacy names.

## UI contract

The Resource editor exposes all six relationship fields separately. TREE
FILTERS remains an expandable/collapsible chip above the independent TREE
chip. Where supported, the relationship selector rebuilds the tree as:

- **Implements**: `implements` / `implementedBy`
- **Inherits**: `inheritsFrom` / `inheritedBy`
- **Depends**: `dependsOn` / `dependedOnBy`

Changing the tree view does not modify resource data.

## MeTTa shape

```metta
(
  (kind operation)
  (id echo.python)
  (implements (
    (echo ())
  ))
  (inheritsFrom (
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
  (implementedBy (
    (echo.python ())
  ))
  (inheritedBy (
    (echo.python (
      (lend ([] "*"))
      (withhold ([] id label enabled implements implementedBy
        preferredImplementation inheritsFrom inheritedBy dependsOn dependedOnBy))
    ))
  ))
  (preferredImplementation echo.python)
)
```

## Invariants

- Every canonical relationship is a map, not a plain ID array.
- Every forward edge has the matching reverse edge.
- `preferredImplementation` names a key in `implementedBy`.
- `implements` never borrows fields.
- `inheritsFrom` never changes availability.
- `dependsOn` never supplies properties or implementation identity.
- Local source always overrides inherited values.
- Derived abstract/partial/concrete/runnable state remains contextual and is
  never persisted as an authoritative flag.
