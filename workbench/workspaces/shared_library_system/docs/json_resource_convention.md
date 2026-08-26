[← Back to top-level README](../../../../README.md)

# MeTTa Resource Kind Convention

Every MeTTa resource in a workbench workspace is self-describing in two places:

1. The top-level map contains a `kind` property.
2. The filename normally ends in `.<kind>.metta`.

Kinds use `snake_case`. The canonical pattern is:

```text
<resource-id>.<kind>.metta
```

Examples:

```text
echo_into_titlecased.operation.metta
echo_into_titlecased_python.operation.metta
echo_into_titlecased_llm.operation.metta
titlecase_received_text.prompt.metta
openai.backend.metta
gpt-5.6.model.metta
gpt-5.6-deep.model.metta
observe_choose_record.workflow.metta
shared_library_system.workspace.metta
image.semantic_datatype.metta
bitmap.representation_datatype.metta
png.concrete_datatype.metta
```

The matching MeTTa map contains exactly the same semantic kind. Multiple maps may coexist in one file; each remains an independently editable resource identified by `id`:

```metta
(
  (kind operation)
  (id echo_into_titlecased)
)
```

```metta
(
  (kind operation)
  (id echo_into_titlecased_python)
  (implements (
    (echo_into_titlecased (
      (borrow ([] "*"))
      (exclude ([]))
    ))
  ))
)
```

## Abstract operations and implementations

A `operation` is the stable semantic stage identity. It defines the contract and the set of allowed implementation variants. It does not itself name Python, Prolog, MeTTa, or an LLM provider.

An `operation` with a same-kind `implements` entry specializes that contract. The child declares what it borrows or excludes, and the parent declares what it lends or withholds.

```text
echo_into_titlecased.operation.metta
  ├── echo_into_titlecased_python.operation.metta
  └── echo_into_titlecased_llm.operation.metta
```

A workflow step therefore points to the abstract operation:

```metta
(
  (kind workflow_step)
  (id step_titlecase)
  (operation echo_into_titlecased)
)
```

The abstract operation lists implementations in `specializations` and selects its default with `preferredSpecialization`. Each specialization points back with `implements`. A step may request an allowed specialization explicitly with `implementationVariant`; otherwise the preferred specialization is selected.

Directories and declared kinds are both part of the resource contract. Validate a changed resource through its loader and tests; do not run broad rewriting or normalization over hand-authored workspace MeTTa.
