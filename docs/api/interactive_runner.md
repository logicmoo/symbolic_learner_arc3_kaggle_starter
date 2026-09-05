# `interactive_runner`

> [← Project README](../../README.md)

## Functions

### `build_keymap(runner: 'Arc3Runner') -> 'tuple[dict[str, Any], list[dict[str, Any]]]'`

### `choose_coordinate() -> 'tuple[int, int] | None'`

### `dispatch_control_mode(runner: 'Arc3Runner', mode: 'str', command_number: 'int') -> 'None'`

### `hook_debugger(host: 'str' = 'localhost', port: 'int' = 5678, suspend: 'bool' = True, timeout: 'float' = 3.0, retry_interval: 'float' = 0.25, wait_for_user_if_not_started: 'bool' = True) -> 'bool'`

### `list_games(runner: 'Arc3Runner', games: 'list[Any]', selected_index: 'int') -> 'None'`

### `main() -> 'None'`

### `print_controls(runner: 'Arc3Runner', rows: 'list[dict[str, Any]]') -> 'None'`

### `print_mode_menu(mode: 'str') -> 'None'`

### `read_key() -> 'str'`

Read one keypress, including modified arrow escape sequences.

### `register_control_command(mode: 'str', command_number: 'int', label: 'str', handler: 'Any | None' = None) -> 'None'`

### `register_control_mode(mode: 'str', *, title: 'str', key: 'str') -> 'None'`

Register an extensible debugger service without editing the input loop.

### `show_history(runner: 'Arc3Runner', cursor: 'int | None' = None) -> 'None'`
