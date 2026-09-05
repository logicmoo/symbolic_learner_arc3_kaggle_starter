> [← Project README](../../README.md)

# Table of Contents

* [interactive\_runner](#interactive_runner)
  * [PROJECT\_ROOT](#interactive_runner.PROJECT_ROOT)
  * [hook\_debugger](#interactive_runner.hook_debugger)
  * [KEY\_SEQUENCES](#interactive_runner.KEY_SEQUENCES)
  * [FALLBACK\_ACTION\_KEYS](#interactive_runner.FALLBACK_ACTION_KEYS)
  * [read\_key](#interactive_runner.read_key)
  * [build\_keymap](#interactive_runner.build_keymap)
  * [choose\_coordinate](#interactive_runner.choose_coordinate)
  * [print\_controls](#interactive_runner.print_controls)
  * [list\_games](#interactive_runner.list_games)
  * [show\_history](#interactive_runner.show_history)
  * [CONTROL\_MODES](#interactive_runner.CONTROL_MODES)
  * [CONTROL\_MODE\_KEYS](#interactive_runner.CONTROL_MODE_KEYS)
  * [CONTROL\_MODE\_HANDLERS](#interactive_runner.CONTROL_MODE_HANDLERS)
  * [register\_control\_mode](#interactive_runner.register_control_mode)
  * [register\_control\_command](#interactive_runner.register_control_command)
  * [print\_mode\_menu](#interactive_runner.print_mode_menu)
  * [dispatch\_control\_mode](#interactive_runner.dispatch_control_mode)
  * [main](#interactive_runner.main)

<a id="interactive_runner"></a>

# interactive\_runner

<a id="interactive_runner.PROJECT_ROOT"></a>

#### PROJECT\_ROOT

<a id="interactive_runner.hook_debugger"></a>

#### hook\_debugger

```python
def hook_debugger(host: str = "localhost",
                  port: int = 5678,
                  suspend: bool = True,
                  timeout: float = 3.0,
                  retry_interval: float = 0.25,
                  wait_for_user_if_not_started: bool = True) -> bool
```

<a id="interactive_runner.KEY_SEQUENCES"></a>

#### KEY\_SEQUENCES

<a id="interactive_runner.FALLBACK_ACTION_KEYS"></a>

#### FALLBACK\_ACTION\_KEYS

<a id="interactive_runner.read_key"></a>

#### read\_key

```python
def read_key() -> str
```

Read one keypress, including modified arrow escape sequences.

<a id="interactive_runner.build_keymap"></a>

#### build\_keymap

```python
def build_keymap(
        runner: Arc3Runner) -> tuple[dict[str, Any], list[dict[str, Any]]]
```

<a id="interactive_runner.choose_coordinate"></a>

#### choose\_coordinate

```python
def choose_coordinate() -> tuple[int, int] | None
```

<a id="interactive_runner.print_controls"></a>

#### print\_controls

```python
def print_controls(runner: Arc3Runner, rows: list[dict[str, Any]]) -> None
```

<a id="interactive_runner.list_games"></a>

#### list\_games

```python
def list_games(runner: Arc3Runner, games: list[Any],
               selected_index: int) -> None
```

<a id="interactive_runner.show_history"></a>

#### show\_history

```python
def show_history(runner: Arc3Runner, cursor: int | None = None) -> None
```

<a id="interactive_runner.CONTROL_MODES"></a>

#### CONTROL\_MODES: `dict[str, dict[str | int, str]]`

<a id="interactive_runner.CONTROL_MODE_KEYS"></a>

#### CONTROL\_MODE\_KEYS: `dict[str, str]`

<a id="interactive_runner.CONTROL_MODE_HANDLERS"></a>

#### CONTROL\_MODE\_HANDLERS: `dict[tuple[str, int], Any]`

<a id="interactive_runner.register_control_mode"></a>

#### register\_control\_mode

```python
def register_control_mode(mode: str, *, title: str, key: str) -> None
```

Register an extensible debugger service without editing the input loop.

<a id="interactive_runner.register_control_command"></a>

#### register\_control\_command

```python
def register_control_command(mode: str,
                             command_number: int,
                             label: str,
                             handler: Any | None = None) -> None
```

<a id="interactive_runner.print_mode_menu"></a>

#### print\_mode\_menu

```python
def print_mode_menu(mode: str) -> None
```

<a id="interactive_runner.dispatch_control_mode"></a>

#### dispatch\_control\_mode

```python
def dispatch_control_mode(runner: Arc3Runner, mode: str,
                          command_number: int) -> None
```

<a id="interactive_runner.main"></a>

#### main

```python
def main() -> None
```
