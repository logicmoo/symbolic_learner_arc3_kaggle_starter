# Legacy LLM Configuration Migration

The workbench no longer treats the old root-level LLM catalogs as its authoritative configuration.

## Sources inspected

The migration was based on the legacy `config/llm_providers.json` and `config/llm_workflows.json` catalogs.

## Where the old concepts went

- Provider/backend records -> `shared/models/*.json` with `kind: backend`.
- Concrete model records -> `shared/models/*.json` with `kind: model`.
- Light/deep/extreme and other execution presets -> `shared/models/*.json` with `kind: profile` and no prompt list.
- Reusable instruction fragments -> `shared/prompts/*.json`.
- Ordered `prompt_text` lists and old LLM transactions -> Task `promptSelection` in `shared/tasks/` or `arc3/tasks/`.

## Vision-first split

ARC3 was the application in which many of these prompts were first written, but much of the behavior is not ARC3-specific. Logical image coordinates, semantic object extraction, topology preservation, Turtle reconstruction, before/after change analysis, correspondence, rule induction, and artifact auditing are shared vision/symbolic capabilities.

Only ARC3 contracts remain under the ARC3 workspace: the ARC3 response keys, `object_registry.pl` identity convention, exact ARC3 artifact-file separation, and ARC3 root-state behavior.

## Legacy compatibility

The old root config files may remain temporarily while older debugger/runtime code still references them. New workbench editors and workspace snapshots should use the filesystem resources under `workbench/workspaces/` instead. Once every legacy caller is migrated, those root catalogs can be removed rather than maintained in parallel.
