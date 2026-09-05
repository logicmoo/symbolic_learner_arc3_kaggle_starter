# `llm_json`

> [← Project README](../../README.md)

## Classes

### `class LlmJsonError(RuntimeError)`

Raised when an LLM response cannot be recovered as the required object.


## Functions

### `parse_or_repair_json_object(text: 'str', *, required_keys: 'Iterable[str]' = ()) -> 'tuple[dict[str, Any], bool]'`

Parse strict JSON, then deterministically repair common LLM defects.

### `strict_json_text(value: 'dict[str, Any]') -> 'str'`
