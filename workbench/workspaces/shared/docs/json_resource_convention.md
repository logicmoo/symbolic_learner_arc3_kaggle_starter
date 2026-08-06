# JSON Resource Kind Convention

Every JSON resource in a workbench workspace is self-describing in two places:

1. The JSON object contains a `kind` property.
2. The filename ends in `.<kind>.json`.

The canonical pattern is:

```text
<resource-id>.<kind>.json
```

Examples:

```text
echo_into_titlecased.task.json
titlecase_received_text.prompt.json
openai.backend.json
gpt-5.6.model.json
gpt-5.6-deep.profile.json
observe_choose_record.workflow.json
shared.workspace.json
datatypes.datatype-catalog.json
```

The matching JSON begins with the same semantic kind, for example:

```json
{
  "kind": "task",
  "id": "echo_into_titlecased"
}
```

or:

```json
{
  "kind": "profile",
  "id": "gpt-5.6-deep",
  "inherits": "gpt-5.6"
}
```

Directories remain useful organizational hints, but they are not the only way to identify a resource. A file can be understood from its name and contents even when copied elsewhere.

The normalizer at `workbench/scripts/normalize_workspace_json.py` enforces this convention across `workbench/workspaces/**.json` and is safe to run repeatedly.
