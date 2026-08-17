[Back to repository README](../../../README.md)

# Operations and Executions

An Operation is a durable, inspectable capability specification. It may be executed now or later through an implementation ladder: Codex or another capable agent, an LLM, progressively smaller specialized models, an ILP/program-synthesis system, or deterministic code. The abstract Operation remains the stable contract; a same-kind child is a selectable implementation alternative.

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
