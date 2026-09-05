# `gpt_bridge`

> [← Project README](../../README.md)

## Classes

### `class GptArcAnalyzer`

One-call GPT analysis that splits a structured bundle into Prolog files.

- `__init__(self, prompts_path: 'str | Path', *, model: 'str | None' = None, client: 'Any | None' = None) -> 'None'`
- `configure_profile(self, level: 'int') -> 'dict[str, Any]'`
- `edit_prompts(self) -> 'None'`
- `ensure_differences(self, store: 'ActionTreeStore', node: 'StateNode', *, force: 'bool' = True)`
- `ensure_full_analysis(self, store: 'ActionTreeStore', node: 'StateNode', *, force: 'bool' = False, analysis_level: 'int' = 2) -> 'dict[str, Any]'`
- `generate_pair_artifact(self, store: 'ActionTreeStore', node: 'StateNode', prompt_name: 'str', filename: 'str', *, force: 'bool' = True)`
- `generate_single_artifact(self, store: 'ActionTreeStore', node: 'StateNode', prompt_name: 'str', filename: 'str', *, force: 'bool' = True)`
- `prompts(self) -> 'dict[str, str]'` — Return a compatibility combined prompt from the unified config.
