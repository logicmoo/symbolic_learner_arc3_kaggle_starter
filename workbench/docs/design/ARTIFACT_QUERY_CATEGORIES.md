# Artifact Query Categories

[← Back to top-level README](../../../README.md)

Design trees support two complementary category mechanisms.

Inline `categories` arrays assign a resource directly to virtual paths. Saved query categories are first-class `artifact_category` JSON resources stored under `design/categories/`. They never move or duplicate the matched resource files.

Every query category requires:

- `path`: its virtual location, such as `filtered/prolog`;
- `trees`: the explicit Design editors where it may appear;
- `query.kinds`: compatible filesystem resource kinds;
- optional `query.where`: field predicates;
- `parentMode`: `hide`, `show`, or `user`.

Example:

```json
{
  "kind": "artifact_category",
  "id": "filtered.prolog",
  "path": "filtered/prolog",
  "trees": ["operations"],
  "query": {
    "kinds": ["operation_implementation"],
    "where": {
      "implementation": {"startsWith": "prolog"}
    }
  },
  "parentMode": "show"
}
```

Supported predicates currently include direct equality plus `equals`, `startsWith`, `contains`, `gte`, and `lte`. Dot-separated fields inspect nested values; `_resolved` accesses non-persisted inheritance data such as `_resolved.backendId`.

The backend evaluates queries against effective inherited resources and adds resolved memberships to its response without rewriting source JSON. Tree/kind incompatibilities are rejected. Query categories and inline categories then share the existing `All`, `Uncategorized`, filtering, and category-view controls.
