# First-Class Data Representations

The workbench separates **what information means** from **how that information is encoded**.

This is deliberately parallel to the task system:

```text
Abstract Task                 Abstract Data
    │                             │
    ├── Prolog                    ├── Bitmap
    ├── Python                    ├── SVG
    ├── LLM                       ├── LOGO/Turtle
    └── MeTTa                     ├── Scene Graph
                                  ├── Object List / Facts
                                  ├── Natural Language
                                  └── Embedding
```

A workflow should normally ask for an abstract datatype such as `image`, not for a file format such as JPEG. Likewise it should ask for an abstract task such as object extraction, not hard-code GPT or Prolog unless a specific implementation is required.

## Filesystem resources

Shared reusable definitions live in:

```text
workbench/workspaces/shared/
├── datatypes/
├── representations/
├── tasks/
├── models/
├── prompts/
└── workflows/
```

Ordinary workspaces inherit shared datatype and representation resources. A workspace may override a shared resource by declaring a local resource with the same `id`, just as it can override shared tasks and model configuration.

## Abstract datatype

Example:

```json
{
  "kind": "datatype",
  "id": "image",
  "label": "Image",
  "description": "A visual scene independent of its concrete representation.",
  "representationSelection": {
    "default": "bitmap",
    "variants": [
      "bitmap",
      "svg",
      "logo_program",
      "scene_graph",
      "object_list",
      "natural_language",
      "latent_embedding"
    ]
  }
}
```

The datatype is semantic. It says what the value means.

## Datatype representation

A representation says how the same semantic value is encoded.

```json
{
  "kind": "datatype_representation",
  "id": "scene_graph",
  "label": "Scene Graph",
  "implements": "image",
  "encodings": [
    {
      "id": "json",
      "mimeTypes": ["application/json"],
      "extensions": [".json"]
    }
  ]
}
```

PNG, JPEG, and BMP are treated as encodings of the `bitmap` representation rather than as separate semantic datatypes.

## Conversion tasks

Representation conversion is not a special execution mechanism. A conversion is an ordinary abstract task with a typed representation contract.

```json
{
  "kind": "task",
  "id": "bitmap_to_scene_graph",
  "inputs": {
    "image": {
      "datatype": "image",
      "representation": "bitmap"
    }
  },
  "outputs": {
    "image": {
      "datatype": "image",
      "representation": "scene_graph"
    }
  },
  "conversion": {
    "datatype": "image",
    "from": "bitmap",
    "to": "scene_graph"
  }
}
```

That task can later have Python, Prolog, LLM, or MeTTa implementations. The workbench therefore plans over two independent dimensions:

1. which task implementation should satisfy an abstract operation;
2. which representation-conversion path makes the available data compatible with that implementation.

## Representation planning graph

The server builds a graph from tasks containing a `conversion` contract and can plan a path between representations.

For example:

```text
bitmap
  ├── bitmap_to_scene_graph ──> scene_graph ──> scene_graph_to_logo ──> logo_program
  └── bitmap_to_objects ──────> object_list ──> objects_to_logo ──────> logo_program

natural_language ──> text_to_scene_graph ──> scene_graph
```

Conversion task definitions may provide planning metadata such as:

```json
{
  "planning": {
    "cost": 0.15,
    "expectedAccuracy": 0.96,
    "latencyClass": "medium",
    "lossy": true
  }
}
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

```json
{
  "artifactId": "art_1947",
  "datatype": "image",
  "representation": "scene_graph",
  "encoding": "json",
  "value": {},
  "provenance": {
    "producerTask": "bitmap_to_scene_graph",
    "producerImplementation": "bitmap_to_scene_graph.gpt56"
  }
}
```

`datatype` identifies meaning, `representation` identifies the concrete form, and `encoding` identifies serialization/file-level encoding. Older artifacts that only carry `datatype` remain readable during migration.

## Workflow contract

A representation-independent workflow can declare only the semantic contract:

```json
{
  "task": "object_extraction",
  "inputs": {
    "source": {"datatype": "image"}
  },
  "outputs": {
    "objects": {"datatype": "object_collection"}
  }
}
```

The long-term planner resolves both the task implementation and any conversion tasks needed to connect the available artifact representations to that implementation. This keeps workflows modular and allows implementations and data encodings to be swapped independently.
