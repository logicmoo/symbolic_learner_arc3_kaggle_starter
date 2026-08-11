[Back to repository README](../../../README.md)

# Operations as delayed agent tasks

An Operation is a durable, inspectable task specification. It may be executed
now or later through an implementation ladder: Codex or another capable agent,
an LLM, progressively smaller task-specialized models, an ILP/program-synthesis
system, or deterministic code. The abstract Operation remains the stable
contract; an implementation is a selectable way to fulfill it.

The Workbench must preserve these fields throughout the lifecycle:

- declared inputs and parameter values;
- declared output contracts and produced output artifacts;
- selected implementation and model routing;
- status (`defined`, `running`, `completed`, or `failed`);
- durable invocation traces, logs, artifacts, provenance, and other evidence.

Before execution, the Operation Playground is an editable delayed-task form.
After execution, it is also an inspection surface for the result and evidence.
ILP and program-synthesis implementations are first-class non-model executors.
They learn or derive implementation programs from the Operation specification
and accumulated evidence, write the resulting implementation code, and can
promote that code into a smaller deterministic executor. Therefore the
non-model path is not limited to manually written callables. Python callables
remain useful deterministic implementations where available, whether authored
by a person or synthesized, but they do not erase the abstract Operation or its
alternative implementations.

The intended progression is evidence-driven, not mandatory: begin with a
capable agent when the task is underspecified, collect durable outcomes, move
to smaller models or symbolic synthesis as the contract becomes learnable, and
retain synthesized deterministic code when it satisfies the same Operation
contract reliably.

Workflow steps reference these durable Operations. A workflow therefore
coordinates delayed tasks, propagates typed outputs into downstream inputs,
and persists the status and evidence of the whole cascade.

## Optional inspection probes

A Gallery Curation Operation may be inserted as a non-blocking inspection
probe, analogous to a test point on a circuit board. A probe can observe an
upstream collection and materialize a Gallery Resource without becoming a
mandatory dependency of the primary dataflow. Disabled optional probes are
persisted as `skipped`, including a durable `step.skipped` event, while the
workflow continues.

Optionality is a default, not a universal restriction. The base Gallery
Operation declares a specializable probe policy. A child Operation or workflow
step may override it with `required true` and `blocking true`, turning the same
inspection point into a required review or production stage.
