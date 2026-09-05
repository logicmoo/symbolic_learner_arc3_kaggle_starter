# `unsloth_studio`

> [← Project README](../../README.md)

## Classes

### `class StudioAwareLlmProviderRouter(LlmProviderRouter)`

LLM router that manages the resident model in Unsloth Studio.

- `__init__(self, *args: 'Any', sleep: 'Callable[[float], None] | None' = None, clock: 'Callable[[], float] | None' = None, **kwargs: 'Any') -> 'None'`
- `compose_prompt(self, spec: 'ProviderSpec | None' = None) -> 'str'`
- `configured_specs(self) -> 'tuple[ProviderSpec, ...]'`
- `create_response(self: 'StudioAwareLlmProviderRouter', **kwargs: 'Any') -> 'Any'`
- `current_spec(self) -> 'ProviderSpec'`
- `cycle(self) -> 'ProviderSpec'`
- `describe_current(self) -> 'str'`
- `ensure_unsloth_model_loaded(self, spec: 'ProviderSpec', *, force: 'bool' = False) -> 'dict[str, Any]'`
- `prompt_section_names(self, spec: 'ProviderSpec | None' = None) -> 'tuple[str, ...]'`
- `prompt_sections(self, spec: 'ProviderSpec | None' = None) -> 'tuple[tuple[str, str], ...]'`
- `select(self, provider_id: 'str') -> 'ProviderSpec'`
- `statuses(self, *, probe: 'bool' = False) -> 'tuple[ProviderStatus, ...]'`
