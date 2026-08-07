# Goals and Variants

[Back to repository README](../../../../README.md)

Goals describe desired outcomes independently of the strategy used to pursue them. A `goal` specification is the parent resource; `goal_variant` or `goal_interpretation` documents are concrete alternatives beneath it.

## Filesystem convention

- Specifications: `goals/<id>.goal.json`
- Alternatives: `goals/<id>.<name>.goal_variant.json`
- Every alternative declares `"parents": ["<goal-id>"]`.
- Every specification lists its alternatives in `children`.
- `preferredChild` identifies the preferred alternative.

Shared goals are inherited by project workspaces. Saving an inherited goal from a project creates a workspace-local override instead of modifying Shared.

## Editor workflow

Use **+ Abstract goal** to create a specification and **+ Alternative** to create a concrete interpretation. Open resources in persistent tabs, compare two documents with Split view, edit the raw JSON, and save to the filesystem. Changing **Preferred Variant** mutates the open goal specification; save that parent document to persist the selection.

Goal Runs are runtime history. They should eventually preserve the resolved goal version, selected interpretation, context, plan, workflow runs, evidence, and outcome without modifying the design-time goal.
