[← Back to top-level README](../../README.md)

# First-Class Data Representations

The workbench separates **what information means** from **how that information is encoded**.

This is deliberately parallel to the operation system:

```text
Abstract Operation                 Abstract Data
    │                             │
    ├── Prolog                    ├── Bitmap
    ├── Python                    ├── SVG
    ├── LLM                       ├── LOGO/Turtle
    └── MeTTa                     ├── Scene Graph
                                  ├── Object List / Facts
                                  ├── Natural Language
                                  └── Embedding
```

A workflow should normally ask for an abstract datatype such as `image`, not for a file format such as JPEG. Likewise it should ask for an abstract operation such as object extraction, not hard-code GPT or Prolog unless a specific implementation is required.

## Filesystem resources

Shared reusable definitions live in:

```text
workbench/workspaces/shared_library_system/
├── datatypes/
├── representations/
├── operations/
├── models/
├── prompts/
└── workflows/
```

Ordinary workspaces inherit shared datatype and representation resources. A workspace may override a shared resource by declaring a local resource with the same `id`, just as it can override shared operations and model configuration.

## Abstract datatype

Example:

```metta
(
  (kind semantic_datatype)
  (id image)
  (label Image)
  (description "A visual scene independent of its concrete representation.")
  (children ([]
    bitmap
    svg
    logo_program
    scene_graph
    object_list
    natural_language
    latent_embedding
  ))
  (preferredChild bitmap)
)
```

The datatype is semantic. It says what the value means.

## Representation datatype

A representation says how the same semantic value is encoded.

```metta
(
  (kind representation_datatype)
  (id scene_graph)
  (label "Scene Graph")
  (parents ([]
    image
  ))
  (children ([]
    json
  ))
  (preferredChild json)
)
```

## Concrete datatype

Exact encodings are separate resources and may serve several representations:

```metta
(
  (kind concrete_datatype)
  (id json)
  (parents ([]
    json_object
    object_list
    scene_graph
  ))
  (mimeTypes ([]
    application/json
  ))
  (extensions ([]
    .json
  ))
)
```

PNG, JPEG, and BMP are concrete children of the `bitmap` representation rather than semantic datatypes.

## Conversion operations

Representation conversion is not a special execution mechanism. A conversion is an ordinary abstract operation with a typed representation contract.

```metta
(
  (kind operation)
  (id bitmap_to_scene_graph)
  (inputs (
    (image (
      (datatype image)
      (representation bitmap)
    ))
  ))
  (outputs (
    (image (
      (datatype image)
      (representation scene_graph)
    ))
  ))
  (conversion (
    (datatype image)
    (from bitmap)
    (to scene_graph)
  ))
)
```

That operation can later have Python, Prolog, LLM, or MeTTa implementations. The workbench therefore plans over two independent dimensions:

1. which operation implementation should satisfy an abstract operation;
2. which representation-conversion path makes the available data compatible with that implementation.

## Representation planning graph

The server builds a graph from operations containing a `conversion` contract and can plan a path between representations.

For example:

```text
bitmap
  ├── bitmap_to_scene_graph ──> scene_graph ──> scene_graph_to_logo ──> logo_program
  └── bitmap_to_objects ──────> object_list ──> objects_to_logo ──────> logo_program

natural_language ──> text_to_scene_graph ──> scene_graph
```

Conversion operation definitions may provide planning metadata such as:

```metta
(
  (planning (
    (cost 0.15)
    (expectedAccuracy 0.96)
    (latencyClass medium)
    (lossy true)
  ))
)
```

The current planner uses cost when choosing the shortest available conversion path. Accuracy, latency, and lossiness are retained as first-class metadata for richer planning policies.

## API

For a workspace named `arc3`:

```text
GET /api/workspaces/arc3/datatypes
GET /api/workspaces/arc3/representations
GET /api/workspaces/arc3/representation-graph
GET /api/workspaces/arc3/datatypes/image/resolve
GET /api/workspaces/arc3/datatypes/image/resolve?representation=scene_graph
GET /api/workspaces/arc3/datatypes/image/plan?source=bitmap&target=logo_program
```

The representation graph response includes effective shared/workspace datatype resources, representation resources, and conversion edges.

## Artifact contract

The canonical artifact contract is:

```metta
(
  (artifactId art_1947)
  (datatype image)
  (representation scene_graph)
  (encoding json)
  (value ())
  (provenance (
    (producerOperation bitmap_to_scene_graph)
    (producerImplementation bitmap_to_scene_graph.gpt56)
  ))
)
```

`datatype` identifies meaning, `representation` identifies the concrete form, and `encoding` identifies serialization/file-level encoding. Older artifacts that only carry `datatype` remain readable during migration.

## Workflow contract

A representation-independent workflow can declare only the semantic contract:

```metta
(
  (operation object_extraction)
  (inputs (
    (source (
      (datatype image)
    ))
  ))
  (outputs (
    (objects (
      (datatype object_collection)
    ))
  ))
)
```

The long-term planner resolves both the operation implementation and any conversion operations needed to connect the available artifact representations to that implementation. This keeps workflows modular and allows implementations and data encodings to be swapped independently.
