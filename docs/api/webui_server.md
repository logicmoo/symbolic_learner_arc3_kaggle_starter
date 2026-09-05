# `webui.server`

> [← Project README](../../README.md)

## Classes

### `class TerminalProcess`

Cross-platform pseudo-terminal wrapper.

- `__init__(self, argv: 'list[str]', *, cwd: 'Path', env: 'dict[str, str]', rows: 'int', cols: 'int') -> 'None'`
- `close(self) -> 'None'`
- `is_alive(self) -> 'bool'`
- `read(self, size: 'int' = 65536) -> 'str'`
- `resize(self, rows: 'int', cols: 'int') -> 'None'`
- `start(self) -> 'None'`
- `write(self, data: 'str') -> 'None'`

## Functions

### `create_app(*, default_game: 'str' = 'ls20', render_mode: 'str' = 'terminal', access_token: 'str | None' = None) -> 'FastAPI'`

### `main() -> 'None'`

### `parse_args() -> 'argparse.Namespace'`

### `subprocess_list2cmdline(argv: 'list[str]') -> 'str'`

Use Python's Windows quoting without importing subprocess globally.
