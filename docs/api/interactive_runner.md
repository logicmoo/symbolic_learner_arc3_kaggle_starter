> [← Project README](../../README.md)

# Table of Contents

* [interactive\_runner](#interactive_runner)
  * [read\_key](#interactive_runner.read_key)
  * [register\_control\_mode](#interactive_runner.register_control_mode)

<a id="interactive_runner"></a>

# interactive\_runner

<a id="interactive_runner.read_key"></a>

#### read\_key

```python
def read_key() -> str
```

Read one keypress, including modified arrow escape sequences.

<a id="interactive_runner.register_control_mode"></a>

#### register\_control\_mode

```python
def register_control_mode(mode: str, *, title: str, key: str) -> None
```

Register an extensible debugger service without editing the input loop.
