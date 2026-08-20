# Topics

[Back to repository README](../../../../README.md)

**Topics** are flat, top-level subject-matter labels that classify resources for
UI selection and filtering — "browse operations by topic", "find a prompt for
segmentation", and so on. A resource can belong to several topics at once, and a
topic is independent of *how* the resource executes.

Topics reuse the workbench's `artifact_category` query mechanism: each topic is a
saved category resource under `design/categories/`, and a resource "has" a topic
either by declaring it or by matching the topic's query.

## The taxonomy

Most topics are flat, top-level labels (`segmentation`, `vision`,
`world-modeling`, `symbolic`, `graphics`, `learning`, `datatypes`, `prompts`, …).
A few are nested one level, using a `parent/child` path:

```
workflow/                 (umbrella)
├── workflow-authoring     — generate/analyze workflows from specs
├── workflow-language      — the DSL primitives (loops, conditionals, values, memory)
└── workflow-values        — read/set/compare workflow values

systems/                  (umbrella)
├── systems-workbench      — backed by the workbench runtime
├── systems-llm            — backed by an LLM caller
├── systems-python         — backed by a Python runtime
├── systems-prolog         — backed by a Prolog runtime
└── systems-inspection     — inspect external systems
```

The tree nests by the set-resource `path`; the token a resource declares stays
flat (e.g. an operation declares `workflow-language`, and the tree shows it under
`workflow/`).

## How a resource gets its topics

- **Operations** declare an inline `topics` list, and every operation carries at
  least two topics. Example:

  ```metta
  (topics ([]
    segmentation
    world-modeling
  ))
  ```

- **Datatypes, prompts, models, and systems** are auto-bucketed by kind through
  query categories in `topic_buckets.artifact_category.metta`, so no per-resource
  edits are required. Each also receives **`todo-needs-categorization`** until a
  human (or the topic editor) assigns real topics.

## Topic-deriving properties

Topics are not the only classification signal on a resource. Several other
properties act as categorization dimensions, and topics are derived from — or
overlap with — them. This is the map:

| Property | Found on | How it relates to topics |
|---|---|---|
| `topics` | operations (inline) | the declared topics, verbatim |
| `implementation` (route) | operations | backend family → `systems-python` / `systems-prolog` / `systems-llm` / `systems-metta`, `core-primitives`, `resource-tools` |
| `provider` | systems, backends, models | drives the `systems-<provider>` topic (python / prolog / metta / llm) |
| `systemType` | systems | runtime class: `agent`, `runtime`, `llm_caller`, `communication` |
| `capabilities` | models, systems, backends, prompts | capability tags (`vision`, `reasoning`, `llm.vision`, `prolog.query`, `python.callable`, `metta.evaluate`, …); overlaps `vision` / `reasoning` and the `systems-*` topics |
| `targets` | prompts, prompt implementations | which models/targets a prompt is written for (applicability) |
| `inputs` / `outputs` datatypes | operations, prompts | semantic I/O typing (`Observation`, `EntityCollection`, `Image`, …); used to rank a prompt's applicability to a role |
| `kind` | every resource | the tree bucket topic (`datatypes` / `prompts` / `models` / `systems`) |
| `categories` (legacy) | operations (removed) | the old two-level category paths were converted into flat `topics` |

The strongest overlaps are `capabilities` (backend + `vision`/`reasoning`) and
`targets` (prompt→model applicability); these are candidates for folding directly
into the topic set.

## Topic set-resources

Each topic is an `artifact_category` document. A declared-topic set queries the
inline `topics` field:

```metta
(
  (kind artifact_category)
  (id topics.segmentation)
  (label "Segmentation")
  (path segmentation)
  (trees ([] operations ))
  (query (
    (kinds ([] operation ))
    (where ((topics ((contains segmentation)))))
  ))
  (parentMode show)
)
```

A bucket set matches by `kind` with no `where`, so it gathers every resource of
that kind (see `topic_buckets.artifact_category.metta`). Supported query
predicates include `equals`, `startsWith`, `contains`, `gte`, and `lte`, over any
document field (including derived properties like `provider` or `capabilities`).

## Editing topics

Topics are edited today as `design/categories/*.artifact_category.metta`
resources plus the inline `topics` on operations. A dedicated **topic editor**
(create / rename / reparent / delete topics and assign them to resources) is in
progress; until then, the `todo-needs-categorization` bucket collects everything
awaiting explicit topics.
