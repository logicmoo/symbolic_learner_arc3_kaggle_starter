[← Back to top-level README](../../../../README.md)

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
image.semantic_datatype.json
bitmap.representation_datatype.json
png.concrete_datatype.json
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
  "parents": ["echo_into_titlecased"]
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

The parent operation lists implementations in `children` and selects its default with `preferredChild`. A step may request an allowed child explicitly with `implementationVariant`; otherwise the preferred child is selected.

Directories and declared kinds are both part of the resource contract. Validate a changed resource through its loader and tests; do not run broad rewriting or normalization over hand-authored workspace JSON.
