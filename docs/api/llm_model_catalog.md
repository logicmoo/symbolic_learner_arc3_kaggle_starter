# `llm_model_catalog`

> [← Project README](../../README.md)

## Classes

### `class CatalogAwareLlmProviderRouter(StudioAwareLlmProviderRouter)`

Router over provider backends, models, and level-specific profiles.

- `__init__(self, config_path: 'str | Path', **kwargs: 'Any') -> 'None'`
- `activate_level(self, level: 'int', *, mode: 'str' = 'single') -> 'ProviderSpec'`
- `active_model(self) -> 'ModelDefinition'`
- `backend_for_profile(self, profile: 'str | ProfileDefinition | ProviderSpec') -> 'ProviderBackend'`
- `batch_profiles(self) -> 'tuple[ProfileDefinition, ...]'`
- `compose_prompt(self, spec: 'ProviderSpec | None' = None) -> 'str'`
- `configured_model_ids(self) -> 'tuple[str, ...]'`
- `configured_profile_specs(self, *, single: 'bool | None' = None, batch: 'bool | None' = None) -> 'tuple[ProviderSpec, ...]'`
- `configured_specs(self) -> 'tuple[ProviderSpec, ...]'`
- `create_response(self: 'StudioAwareLlmProviderRouter', **kwargs: 'Any') -> 'Any'`
- `current_spec(self) -> 'ProviderSpec'`
- `cycle(self) -> 'ProviderSpec'`
- `cycle_model(self) -> 'ProviderSpec'`
- `default_profile_for_model(self, model_id: 'str') -> 'ProfileDefinition'`
- `describe_current(self) -> 'str'`
- `ensure_unsloth_model_loaded(self, spec: 'ProviderSpec', *, force: 'bool' = False) -> 'dict[str, Any]'`
- `model_for_profile(self, profile: 'str | ProfileDefinition | ProviderSpec') -> 'ModelDefinition'`
- `profile_environment(self, profile: 'ProfileDefinition | str | None' = None) -> 'Iterator[None]'`
- `profile_for_spec(self, spec: 'ProviderSpec | None' = None) -> 'ProfileDefinition'`
- `profiles_for_model(self, model_id: 'str') -> 'tuple[ProfileDefinition, ...]'`
- `prompt_section_names(self, spec: 'ProviderSpec | None' = None) -> 'tuple[str, ...]'`
- `prompt_sections(self, spec: 'ProviderSpec | None' = None) -> 'tuple[tuple[str, str], ...]'`
- `select(self, provider_id: 'str') -> 'ProviderSpec'`
- `select_model(self, model_id: 'str') -> 'ProviderSpec'`
- `select_profile(self, profile_id: 'str', *, mode: 'str | None' = None) -> 'ProviderSpec'`
- `statuses(self, *, probe: 'bool' = False) -> 'tuple[ProviderStatus, ...]'`

### `class ModelDefinition`

Fields:
- `model_id: str`
- `provider_id: str`
- `label: str`
- `model: str`
- `model_env: str | None`
- `supports_reasoning: bool | None`
- `vision: bool`
- `default_level: int`

- `resolved_model(self) -> 'str'`

### `class ProfileDefinition`

Fields:
- `profile_id: str`
- `model_id: str`
- `label: str`
- `analysis_level: int`
- `single_enabled: bool`
- `batch_enabled: bool`
- `max_output_tokens: int`
- `temperature: float | None`
- `top_p: float | None`
- `reasoning_effort: str`
- `current_image_detail: str`
- `parent_image_detail: str`
- `timeout_seconds: float`
- `seed: int | None`
- `prompt_text: tuple[str, ...]`


### `class ProviderBackend`

Fields:
- `backend_id: str`
- `label: str`
- `adapter: str`
- `enabled: bool | str`
- `api_key_env: str | None`
- `api_key_optional: bool`
- `base_url: str | None`
- `base_url_env: str | None`
- `health_url: str | None`
- `health_url_env: str | None`
- `supports_reasoning: bool`
- `timeout_seconds: float`
- `anthropic_version: str`
- `default_model: str | None`
