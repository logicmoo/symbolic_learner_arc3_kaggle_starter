# JSON Resource Kind Convention

Every JSON resource in a workbench workspace is self-describing in two places:

1. The JSON object contains a `kind` property.
2. The filename ends in `.<kind>.json`.

Kinds use `snake_case`. The canonical pattern is:

```text
<resource-id>.<kind>.json
```

Examples:

```text
echo_into_titlecased.task.json
echo_into_titlecased_python.task_implementation.json
echo_into_titlecased_llm.task_implementation.json
titlecase_received_text.prompt.json
openai.backend.json
gpt-5.6.model.json
gpt-5.6-deep.profile.json
observe_choose_record.workflow.json
shared.workspace.json
datatypes.datatype_catalog.json
```

The matching JSON contains exactly the same semantic kind:

```json
{
  "kind": "task",
  "id": "echo_into_titlecased"
}
```

```json
{
  "kind": "task_implementation",
  "id": "echo_into_titlecased_python",
  "implements": "echo_into_titlecased"
}
```

## Abstract tasks and implementations

A `task` is the stable semantic stage identity. It defines the contract and the set of allowed implementation variants. It does not itself name Python, Prolog, MeTTa, or an LLM provider.

A `task_implementation` is one concrete way to perform that task. Several implementations may implement the same task.

```text
echo_into_titlecased.task.json
  ├── echo_into_titlecased_python.task_implementation.json
  └── echo_into_titlecased_llm.task_implementation.json
```

A workflow step therefore points to the abstract task:

```json
{
  "kind": "workflow_step",
  "id": "step_titlecase",
  "task": "echo_into_titlecased"
}
```

The runtime resolves the implementation according to the task's `implementationSelection`. A step may request an allowed variant explicitly with `implementationVariant`; otherwise the task's default variant is selected.

Directories remain useful organizational hints, but they are not the only way to identify a resource. A file can be understood from its name and contents even when copied elsewhere.

The normalizer at `workbench/scripts/normalize_workspace_json.py` enforces this convention across `workbench/workspaces/**.json` and is safe to run repeatedly.
