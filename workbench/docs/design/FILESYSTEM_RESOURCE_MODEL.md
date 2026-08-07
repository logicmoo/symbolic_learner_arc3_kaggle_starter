# Filesystem Resource Model

[Back to repository README](../../../README.md)

## Principle

The filesystem is the source of truth for semantic artifacts. Abstract specifications and concrete alternatives are independent JSON documents rather than entries folded into one catalog.

## Resource Families

Current conventions include:

- `operation` / `operation_implementation`
- `datatype` / `datatype_representation`
- `prompt` / `prompt_implementation`
- `backend` / `model` / `profile`
- `workflow`

Planned families include `goal` / `goal_interpretation` or `goal_variant`, `plan` / `plan_variant`, and `atomspace` / `atomspace_implementation`.

## Bidirectional many-to-many relationships

Specification/alternative relationships are explicit arrays in both files. A parent lists its `variants`, `implementations`, or `representations`; every child lists all parents through `implements` or, for datatypes, `represents`. For example, an operation contains `"implementations": ["python_echo"]` and that implementation contains `"implements": ["echo"]`. Datatype representations use the same graph rule: `image` lists `"representations": ["bitmap"]`, while `bitmap` lists `"represents": ["image"]`.

Arrays are required even when there is only one relationship. This permits one alternative to satisfy multiple specifications. Preferred/default selection stays on each parent because the same child can have a different priority under different specifications. Run `node scripts/sync_resource_relationships.mjs` after bulk resource edits to normalize pointers and add missing backlinks.

Canonical filenames carry the kind, for example `shared.echo.operation.json`, `echo_into_titlecased_python.operation_implementation.json`, and `bitmap.datatype_representation.json`. Resources live beneath a workspace in family directories such as `operations/`, `datatypes/`, `representations/`, `prompts/`, `models/`, and `workflows/`.

## Inheritance and Overrides

The `shared` workspace provides inherited defaults. A project workspace may add resources or override an inherited resource by semantic identity. API records must identify whether their effective document came from `shared` or the selected workspace. Editors saving an inherited resource into a project must create a workspace-local override rather than modify the shared file.

## API and Safety

Workspace snapshots enumerate effective resources and editable files. File reads/writes must remain inside the resolved workspace root, accept supported text formats only, infer and canonicalize JSON resource kinds, and preserve UTF-8. New resource families require loaders, snapshot/API exposure, override tests, and canonical path tests before UI data is displayed.
