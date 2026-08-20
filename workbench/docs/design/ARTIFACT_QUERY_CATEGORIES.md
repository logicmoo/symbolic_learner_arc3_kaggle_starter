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

```metta
(
  (kind artifact_category)
  (id filtered.prolog)
  (path filtered/prolog)
  (trees ([]
    operations
  ))
  (query (
    (kinds ([]
      operation
    ))
    (where (
      (implementation (
        (startsWith prolog)
      ))
    ))
  ))
  (parentMode show)
)
```

Supported predicates currently include direct equality plus `equals`, `startsWith`, `contains`, `gte`, and `lte`. Dot-separated fields inspect nested values; `_resolved` accesses non-persisted inheritance data such as `_resolved.backendId`.

The backend evaluates queries against effective inherited resources and adds resolved memberships to its response without rewriting source JSON. Tree/kind incompatibilities are rejected. Query categories and inline categories then share the existing `All`, `Uncategorized`, filtering, and category-view controls.

## Operation topics

Operations are organized by **topics**: flat, top-level subject-matter labels declared directly on each operation.

```metta
(topics ([]
  segmentation
  world-modeling
))
```

Each topic is a saved query category in `design/categories/topics.artifact_category.metta` that gathers the operations declaring it:

```metta
(
  (kind artifact_category)
  (id topics.segmentation)
  (label "Segmentation")
  (path segmentation)
  (trees ([]
    operations
  ))
  (query (
    (kinds ([]
      operation
    ))
    (where (
      (topics (
        (contains segmentation)
      ))
    ))
  ))
  (parentMode show)
)
```

Topics are independent of an operation's execution route and of any other free-form `categories`: an operation participates in `segmentation` whether it runs through a prompt, Python, Prolog, or the automatic LLM fallback, and segmentation membership does not imply `vision`. Because a topic's `path` is a bare token, topics render as top-level branches in the operations tree; the UI enumerates operations "by topic" from this same query mechanism.
