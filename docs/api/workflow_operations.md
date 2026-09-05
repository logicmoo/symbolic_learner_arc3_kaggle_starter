# `workflow_operations`

> [← Project README](../../README.md)

## Classes

### `class Impl`

Fields:
- `id: str`
- `label: str`
- `species: str`
- `handler: str | None`
- `transaction: str | None`
- `runner_method: str | None`


### `class Operation`

Fields:
- `id: str`
- `label: str`
- `description: str`
- `inputs: dict[str, str]`
- `outputs: dict[str, str]`
- `implementations: tuple[Impl, ...]`

- `impl(self, wanted: 'str | None') -> 'Impl'`

### `class OperationAwareWorkflowRouter(WorkflowAwareLlmProviderRouter)`

Catalog router extended with optional transactions and workflows.

- `__init__(self, config_path, *, workflow_path=None, operation_path=None, datatype_path=None, **kw)`
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

### `class Slot`

Fields:
- `datatype: str`
- `value: Any`
- `producer: str`

- `json(self)`

## Functions

### `advance_observation(e, inp, par)`

### `artifact_outputs(e, t)`

### `ask_upload(e, inp, par)`

### `await_human_arc3_action(e, inp, par)`

### `camera(e, inp, par)`

### `clipboard(e, inp, par)`

### `continue_human_observation(e, inp, par)`

### `copy_images(ps, dest, prefix)`

### `disk_directory(e, inp, par)`

### `display(e, inp, par)`

### `execute_operation(e, tx)`

### `expand_subworkflows(workflows)`

Expand reusable workflow calls while preserving typed slot bindings.

### `generated(e, inp, par)`

### `grab_arc3_state(e, inp, par)`

### `install_operation_workflows()`

### `load_operations(path: 'Path' = WindowsPath('C:/snet/PeTTa/repos/symbolic_learner_workbench/config/workflow_operations.json')) -> 'tuple[Operation, ...]'`

### `manifest(ps, source, dest)`

### `node_root(engine)`

### `normalize(e, inp, par)`

### `paths(v)`

### `read_obj(p: 'Path') -> 'dict[str, Any]'`

### `remote_url(e, inp, par)`

### `render_turtle(e, inp, par)`

### `report(e, inp, par)`

### `resolve_inputs(e, t, c)`

### `save_slots(e)`

### `seed(e)`

### `select_arc3_world(e, inp, par)`

### `slug(s: 'str') -> 'str'`

### `store_outputs(e, t, c, vals)`

### `sync_objects(e, inp, par)`

### `txt(v: 'Any') -> 'str'`

### `validate(e, inp, par)`

### `video_frames(e, inp, par)`
