# `llm_providers`

> [← Project README](../../README.md)

## Classes

### `class LlmConfigurationError(RuntimeError)`

Raised when no usable LLM provider can be selected.


### `class LlmProviderRouter`

OpenAI-Responses-shaped router over cloud and local LLM providers.

- `__init__(self, config_path: 'str | Path | None' = None, *, openai_client_factory: 'Callable[..., Any] | None' = None, urlopen: 'Callable[..., Any] | None' = None) -> 'None'`
- `compose_prompt(self, spec: 'ProviderSpec | None' = None) -> 'str'`
- `configured_specs(self) -> 'tuple[ProviderSpec, ...]'`
- `create_response(self, **kwargs: 'Any') -> 'Any'`
- `current_spec(self) -> 'ProviderSpec'`
- `cycle(self) -> 'ProviderSpec'`
- `describe_current(self) -> 'str'`
- `prompt_section_names(self, spec: 'ProviderSpec | None' = None) -> 'tuple[str, ...]'`
- `prompt_sections(self, spec: 'ProviderSpec | None' = None) -> 'tuple[tuple[str, str], ...]'`
- `select(self, provider_id: 'str') -> 'ProviderSpec'`
- `statuses(self, *, probe: 'bool' = False) -> 'tuple[ProviderStatus, ...]'`

### `class LlmRequestError(RuntimeError)`

Raised when a provider request fails or returns no text.


### `class ProviderSpec`

Fields:
- `provider_id: str`
- `label: str`
- `adapter: str`
- `model: str`
- `enabled: bool | str`
- `model_env: str | None`
- `api_key_env: str | None`
- `api_key_optional: bool`
- `base_url: str | None`
- `base_url_env: str | None`
- `health_url: str | None`
- `health_url_env: str | None`
- `supports_reasoning: bool`
- `timeout_seconds: float`
- `anthropic_version: str`
- `prompt_text: tuple[str, ...]`

- `configuration_state(self) -> 'tuple[bool, str]'`
- `resolved_api_key(self) -> 'str | None'`
- `resolved_base_url(self) -> 'str | None'`
- `resolved_health_url(self) -> 'str | None'`
- `resolved_model(self) -> 'str'`

### `class ProviderStatus`

Fields:
- `provider_id: str`
- `label: str`
- `model: str`
- `configured: bool`
- `state: str`
- `active: bool`
- `base_url: str | None`
