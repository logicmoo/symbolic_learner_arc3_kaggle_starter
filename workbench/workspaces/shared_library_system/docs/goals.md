# Goals and Interpretations

[Back to repository README](../../../../README.md)

Goals describe desired outcomes independently of the strategy used to pursue them. Every resource has `kind goal`; a goal with a same-kind parent is an implicit alternative beneath that parent.

## Filesystem convention

- Specifications and alternatives live in `design/goals/` and may share a file, with each resource as a separate top-level form.
- Separate files use `<id>.goal.metta` for both roots and alternatives.
- Every alternative declares `(parents ([] <goal-id>))`.
- Every specification lists its alternatives in `children`.
- `preferredChild` identifies the preferred alternative.

Shared goals are inherited by project workspaces. Saving an inherited goal from a project creates a workspace-local override instead of modifying Shared.

## Editor workflow

Use **+ Abstract goal** to create a specification and **+ Alternative** to create a concrete interpretation. Open resources in persistent tabs, compare two documents with Split view, edit the raw MeTTa or synchronized JSON view, and save to the filesystem. Changing the preferred alternative mutates the open goal specification; save that parent document to persist the selection.

Goal Runs are runtime history. They preserve the resolved goal version, selected interpretation, AtomSpace bindings, Planning Strategy, Workflow Runs, evidence, and outcome without modifying the design-time Goal.
