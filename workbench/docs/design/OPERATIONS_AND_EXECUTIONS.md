[Back to repository README](../../../README.md)

# Operations and Executions

An Operation is a durable, inspectable capability specification. It may be executed now or later through an implementation ladder: Codex or another capable agent, an LLM, progressively smaller specialized models, an ILP/program-synthesis system, or deterministic code. The abstract Operation remains the stable contract; a same-kind child is a selectable implementation alternative.

## Operations are the workbench's skills system

An Operation is what other ecosystems call a *skill*: a named, declared
capability the workbench can call directly — no model has to decide anything
for a deterministic implementation to run. The Video Import page's prepass
filters are the lightweight, file-based end of the same idea: drop a Python
file exporting `SKILL` metadata plus `apply(image, params)` into
`data/VideoImports/filter_skills/` and the workbench discovers, lists, and
executes it itself (built-ins, published parameter presets in
`filter_catalog.json`, `.cube` LUTs in `data/VideoImports/luts/`, and
downloaded libraries such as the MIT `pilgram` wrapper all surface through
`GET /api/video-import/filters` and run through `POST
/api/video-import/filter`). Skills graduate into the operations library as
resources — see `design/operations/image_filter_skills.operation.metta`
(`skill.apply_image_filter` and its specializations) in the shared library —
where they gain the full Operation contract: typed inputs/outputs, topics,
specialization alternatives, playground invocation, and durable Executions.
The distinction to keep: a *skill/Operation* is called by the workbench (or a
workflow) on its own; a model only enters when an implementation explicitly
routes to one (for example the Video Import page's turtle-program generation,
which is a model-backed step by design).

An Execution is one runtime attempt to invoke that Operation. The Workbench preserves:

- declared inputs and parameter values;
- declared output contracts and produced output artifacts;
- selected implementation and model routing;
- status (`defined`, `running`, `completed`, or `failed`);
- durable invocation traces, logs, artifacts, provenance, and evidence.

Before execution, the Operation Playground is an editable invocation form. After execution, it is also an inspection surface for the result and evidence. ILP and program-synthesis implementations are first-class non-model executors. They may derive code from the Operation specification and accumulated evidence, then promote that code into a smaller deterministic executor without erasing the abstract Operation or its alternatives.

The intended progression is evidence-driven, not mandatory: begin with a capable agent when an Operation is underspecified, collect durable outcomes, move to smaller models or symbolic synthesis as its contract becomes learnable, and retain deterministic code when it satisfies the same contract reliably.

Workflow steps reference Operations. A Workflow coordinates their Executions, propagates typed outputs into downstream inputs, and persists status and evidence for the complete cascade. A Codex task or thread is a separate collaboration record that may design, inspect, or repair these resources.

## Optional inspection probes

A Gallery Curation Operation may be inserted as a non-blocking inspection probe, analogous to a test point on a circuit board. A probe can observe an upstream collection and materialize a Gallery Resource without becoming a mandatory dependency of the primary dataflow. Disabled optional probes are persisted as `skipped`, including a durable `step.skipped` Event, while the Workflow continues.

Optionality is a default, not a universal restriction. The base Gallery Operation declares a specializable probe policy. A child Operation or Workflow step may override it with `required true` and `blocking true`, turning the same inspection point into a required review or production stage.
