# Plans and Strategy Variants

[Back to repository README](../../../../README.md)

Plans describe reusable strategies for pursuing one or more goals. A `plan` specification is the parent resource; `plan_variant` documents provide interchangeable concrete strategies.

## Filesystem convention

- Specifications: `plans/<id>.plan.json`
- Alternatives: `plans/<id>.<name>.plan_variant.json`
- Every alternative declares `"parents": ["<plan-id>"]`; the plan lists it in `children`.
- A variant may reference an existing filesystem workflow by ID.
- `preferredChild` identifies the preferred strategy.

Shared plans and variants are inherited by every project workspace. Workspace resources with the same semantic ID override Shared records.

## Editor workflow

Use **+ Abstract plan** to create a specification and **+ Alternative** to add a strategy. Persistent tabs, dirty markers, split comparison, direct JSON editing, and filesystem save behave the same way as other rich artifact editors. Changing **Preferred Variant** updates the parent plan document and must be saved there.

Runtime execution must record the resolved plan and variant rather than silently rewriting policy. Workflow Runs, Execs, Events, States, and Logs remain separate runtime evidence surfaces.
