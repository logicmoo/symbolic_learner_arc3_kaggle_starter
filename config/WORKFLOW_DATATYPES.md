[← Back to top-level README](../README.md) · [Workflow orchestration](LLM_WORKFLOWS.md)

# Typed Workflow Data and Task Routes

ARC3 workflows distinguish five layers:

1. **Datatype** — the shape or semantic meaning of a value.
2. **Task type** — a reusable operation with typed input and output ports.
3. **Implementation** — one concrete route that performs the task.
4. **Workflow item** — binds task ports to named data slots and chooses an implementation.
5. **Workflow** — an ordered set of task and legacy transaction items.

## Physical and semantic datatypes

A physical or syntactic datatype describes storage, such as `image_file`, `image_collection`, `turtle_program`, `prolog_fact_set`, `file_path`, or `image_manifest`.

A semantic datatype describes meaning. `individual_object` is one semantic object even though it may be represented by:

- an `image_region`;
- a `turtle_program`;
- an `object_properties` Prolog fact set.

The checked-in manifest is [`workflow_datatypes.json`](workflow_datatypes.json). The rendered image is [`workflow_datatypes.svg`](workflow_datatypes.svg).

## Typed data slots

A task step maps input ports to existing slot names and output ports to new slots:

```json
{
  "id": "render_turtle",
  "task": "turtlized_objects_to_images",
  "implementation": "python_turtle_renderer",
  "inputs": {
    "turtle": "turtle_programs",
    "objects": "object_manifest"
  },
  "outputs": {
    "images": "turtle_images",
    "render_manifest": "turtle_render_manifest"
  }
}
```

At runtime ARC3 writes `workflow_data/slot_manifest.json` beneath the current action-tree node. It records every slot's datatype, producer, and value.

## Implementation species

Each task may expose several routes:

- `llm` — delegates to an LLM transaction and profile/model route;
- `prolog` — invokes a Prolog-oriented runner method;
- `python` — executes deterministic Python code for files, images, validation, or reporting.

The catalog is [`workflow_tasks.json`](workflow_tasks.json).

## Included tasks

The catalog includes eleven task types:

1. `grab_image_source`;
2. `normalize_image_collection`;
3. `extract_individual_objects`;
4. `synchronize_object_representations`;
5. `turtlized_objects_to_images`;
6. `images_displayer`;
7. `compare_scene_objects`;
8. `induce_transition_rules`;
9. `prolog_cherry_pick_evidence`;
10. `validate_artifact_bundle`;
11. `publish_workflow_report`.

`grab_image_source` can route through ARC3 state capture, video frame extraction, user file selection, a disk directory, clipboard image, remote URL, camera capture, or deterministic generated images.

## Typed example

[`example_typed_task_workflow.json`](example_typed_task_workflow.json) demonstrates all eleven tasks. It begins with a routed image source and ends with a Markdown workflow report.

Press uppercase `W` to open the task-aware workflow editor. Its tabs show workflows, task species and routes, the datatype manifest, and a button that opens the SVG graph.
