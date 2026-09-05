> [← Project README](../../README.md)

# Table of Contents

* [llm\_json](#llm_json)
  * [LlmJsonError](#llm_json.LlmJsonError)
  * [parse\_or\_repair\_json\_object](#llm_json.parse_or_repair_json_object)

<a id="llm_json"></a>

# llm\_json

<a id="llm_json.LlmJsonError"></a>

## LlmJsonError Objects

```python
class LlmJsonError(RuntimeError)
```

Raised when an LLM response cannot be recovered as the required object.

<a id="llm_json.parse_or_repair_json_object"></a>

#### parse\_or\_repair\_json\_object

```python
def parse_or_repair_json_object(
    text: str, *,
    required_keys: Iterable[str] = ()) -> tuple[dict[str, Any], bool]
```

Parse strict JSON, then deterministically repair common LLM defects.

Returns ``(object, repaired)``. The repair library handles missing commas,
quotes, brackets, literal newlines, trailing commentary, and truncation.
Required-key validation prevents a syntactically repaired but incomplete
bundle from being accepted silently.
