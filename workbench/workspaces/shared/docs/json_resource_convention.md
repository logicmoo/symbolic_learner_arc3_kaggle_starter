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
echo_into_titlecased.operation.json
echo_into_titlecased_python.operation_implementation.json
echo_into_titlecased_llm.operation_implementation.json
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
  "kind": "operation",
  "id": "echo_into_titlecased"
}
```

```json
{
  "kind": "operation_implementation",
  "id": "echo_into_titlecased_python",
  "implements": "echo_into_titlecased"
}
```

## Abstract operations and implementations

A `operation` is the stable semantic stage identity. It defines the contract and the set of allowed implementation variants. It does not itself name Python, Prolog, MeTTa, or an LLM provider.

A `operation_implementation` is one concrete way to perform that operation. Several implementations may implement the same operation.

```text
echo_into_titlecased.operation.json
  ├── echo_into_titlecased_python.operation_implementation.json
  └── echo_into_titlecased_llm.operation_implementation.json
```

A workflow step therefore points to the abstract operation:

```json
{
  "kind": "workflow_step",
  "id": "step_titlecase",
  "operation": "echo_into_titlecased"
}
```

The runtime resolves the implementation according to the operation's `implementationSelection`. A step may request an allowed variant explicitly with `implementationVariant`; otherwise the operation's default variant is selected.

Directories remain useful organizational hints, but they are not the only way to identify a resource. A file can be understood from its name and contents even when copied elsewhere.

The normalizer at `workbench/scripts/normalize_workspace_json.py` enforces this convention across `workbench/workspaces/**.json` and is safe to run repeatedly.
