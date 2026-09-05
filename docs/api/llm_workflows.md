# `llm_workflows`

> [← Project README](../../README.md)

## Classes

### `class LlmWorkflowEngine`

- `__init__(self, runner: 'Any') -> 'None'`
- `run(self, workflow_id: 'str') -> 'None'`

### `class TransactionDefinition`

Fields:
- `transaction_id: str`
- `label: str`
- `kind: str`
- `requires_vision: bool`
- `include_parent_image: bool`
- `include_current_image: bool`
- `output_keys: tuple[str, ...]`
- `input_files: tuple[str, ...]`
- `instructions: str`
- `output_file: str | None`
- `runner_method: str | None`
- `combine_safe: bool`


### `class WorkflowAwareLlmProviderRouter(CatalogAwareLlmProviderRouter)`

Catalog router extended with optional transactions and workflows.

- `__init__(self, config_path: 'str | Path', *, workflow_path: 'str | Path | None' = None, urlopen: 'Callable[..., Any] | None' = None, **kwargs: 'Any') -> 'None'`
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
- `model_availability(self, model_id: 'str', *, refresh: 'bool' = False) -> 'tuple[bool, str]'`
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
- `transaction_for_profile(self, profile_id: 'str') -> 'TransactionDefinition'`

### `class WorkflowDefinition`

Fields:
- `workflow_id: str`
- `label: str`
- `description: str`
- `steps: tuple[WorkflowStep, ...]`
- `repeat_from: str | None`
- `repeat_while_slot: str | None`
- `max_iterations: int`


### `class WorkflowStep`

Fields:
- `step_id: str`
- `transaction_id: str`
- `profile_id: str | None`
- `model_id: str | None`
- `analysis_level: int | None`
- `combine_group: str | None`
- `continue_on_error: bool`


## Functions

### `install_workflow_router() -> 'None'`

### `install_workflow_ui(ui_module: 'Any') -> 'None'`

### `run_workflow_menu(runner: 'Any') -> 'None'`
