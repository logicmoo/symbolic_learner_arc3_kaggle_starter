# `arc3_runner`

> [← Project README](../../README.md)

## Classes

### `class Arc3Runner`

Debuggable ARC3 environment with a persistent deterministic action tree.

- `__init__(self, game_id: 'str' = 'ls20', render_mode: 'str | None' = 'terminal', arc_api_key: 'str | None' = None, capture_terminal: 'bool' = False, tree_root: 'str | Path | None' = None, capture_observers: 'Iterable[Any]' = ()) -> 'None'`
- `action_table(self) -> 'list[dict[str, Any]]'`
- `authorize_semantic_candidate(self, *, candidate_id: 'str', selected_identity_id: 'str', decision_id: 'str', decision_source: 'str' = 'explicit_registry_selection') -> 'Any'`
- `available_games(self) -> 'list[Any]'`
- `change_level(self, delta: 'int') -> 'Any'`
- `current_grid(self) -> 'Any'` — Return the newest logical grid used by capture observers.
- `current_level_label(self) -> 'str'`
- `current_selection_summary(self) -> 'str'`
- `execute_queued_step(self) -> 'Any'`
- `export_state(self, path: 'str | Path') -> 'Path'`
- `game_info(game: 'Any') -> 'dict[str, Any]'`
- `gpt_command_1(self) -> 'None'`
- `gpt_command_2(self) -> 'None'` — Fast demo analysis: low image detail, low reasoning, moderate tokens.
- `gpt_command_3(self) -> 'None'` — Deep analysis: high current image detail and larger token budget.
- `gpt_command_4(self) -> 'None'` — Extreme analysis: high detail for both images and maximum budget.
- `gpt_command_5(self) -> 'None'`
- `gpt_command_6(self) -> 'None'`
- `history(self) -> 'list[dict[str, Any]]'`
- `is_game_over(self) -> 'bool'`
- `is_win(self) -> 'bool'`
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

### `class StepRecord`

Fields:
- `step: int`
- `action: str`
- `data: dict[str, Any]`
- `state: str | None`
- `observation: Any`
- `terminal_output: str`
- `frame_path: str | None`
- `tree_node: str | None`

- `as_dict(self) -> 'dict[str, Any]'`

## Functions

### `action_name(action: 'Any') -> 'str'`

### `is_complex_action(action: 'Any') -> 'bool'`
