# `multillm_runner`

> [← Project README](../../README.md)

## Classes

### `class MultiLlmArc3Runner(Arc3Runner)`

Arc3Runner whose existing GPT artifact path uses a provider router.

- `__init__(self, *args: 'Any', **kwargs: 'Any') -> 'None'`
- `action_table(self) -> 'list[dict[str, Any]]'`
- `authorize_semantic_candidate(self, *, candidate_id: 'str', selected_identity_id: 'str', decision_id: 'str', decision_source: 'str' = 'explicit_registry_selection') -> 'Any'`
- `available_games(self) -> 'list[Any]'`
- `change_level(self, delta: 'int') -> 'Any'`
- `current_grid(self) -> 'Any'` — Return the newest logical grid used by capture observers.
- `current_level_label(self) -> 'str'`
- `current_llm_summary(self) -> 'str'`
- `current_selection_summary(self) -> 'str'`
- `cycle_llm_provider(self) -> 'ProviderSpec'`
- `execute_queued_step(self) -> 'Any'`
- `export_state(self, path: 'str | Path') -> 'Path'`
- `game_info(game: 'Any') -> 'dict[str, Any]'`
- `gpt_command_1(self) -> 'None'` — Restore a historical transcript or open the unified LLM config.
- `gpt_command_2(self) -> 'None'` — Fast demo analysis: low image detail, low reasoning, moderate tokens.
- `gpt_command_3(self) -> 'None'` — Deep analysis: high current image detail and larger token budget.
- `gpt_command_4(self) -> 'None'` — Extreme analysis: high detail for both images and maximum budget.
- `gpt_command_5(self) -> 'None'`
- `gpt_command_6(self) -> 'None'`
- `history(self) -> 'list[dict[str, Any]]'`
- `is_game_over(self) -> 'bool'`
- `is_win(self) -> 'bool'`
- `llm_provider_statuses(self, *, refresh: 'bool' = False) -> 'tuple[dict[str, Any], ...]'`
- `llm_router(self) -> 'StudioAwareLlmProviderRouter'`
- `open(self) -> 'Any'`
- `prolog_command_1(self) -> 'None'`
- `prolog_command_2(self) -> 'None'`
- `prolog_command_3(self) -> 'None'`
- `prolog_command_4(self) -> 'None'`
- `prolog_command_5(self) -> 'None'`
- `prolog_command_6(self) -> 'None'`
- `redraw(self) -> 'Any'`
- `reject_semantic_candidate(self, *, candidate_id: 'str', selected_identity_id: 'str', decision_id: 'str', decision_source: 'str' = 'explicit_registry_rejection') -> 'Any'`
- `replay(self, records: 'Sequence[StepRecord | Mapping[str, Any]] | None' = None) -> 'Any'`
- `reset(self, *, clear_history: 'bool' = True) -> 'Any'`
- `resolve_action(self, action: 'Any') -> 'Any'`
- `restart_game(self) -> 'Any'`
- `save_history(self, path: 'str | Path') -> 'Path'`
- `scorecard(self) -> 'Any'`
- `semantic_authorization_options(self) -> 'dict[str, tuple[str, ...]]'` — Collect explicit friendly-identity choices from semantic observers.
- `show_record(self, index: 'int') -> 'None'`
- `state_name(self) -> 'str | None'`
- `step(self, action: 'Any', *, x: 'int | None' = None, y: 'int | None' = None, data: 'Mapping[str, Any] | None' = None, reasoning: 'Mapping[str, Any] | None' = None) -> 'Any'`
- `summary_for_prolog(self) -> 'dict[str, Any]'`
- `switch_game(self, game_id: 'str') -> 'Any'`

## Functions

### `install_interactive_runner(ui_module: 'Any') -> 'None'`

Install multi-LLM behavior without duplicating the debugger UI loop.

### `last_runner() -> 'MultiLlmArc3Runner | None'`
