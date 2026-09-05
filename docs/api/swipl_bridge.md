# `swipl_bridge`

> [← Project README](../../README.md)

## Classes

### `class SWIPrologBridge`

Invoke a Prolog controller using a JSON snapshot from Arc3Runner.

- `__init__(self, agent_file: 'str | Path', swipl_executable: 'str' = 'swipl') -> 'None'`
- `choose_action(self, snapshot: 'Mapping[str, Any]') -> 'dict[str, Any]'`
- `execute_turtle(self, program: 'str', params: 'Mapping[str, Any] | None' = None) -> 'dict[str, Any]'` — Execute a turtle/2 program through the canonical Turtle DSL.
