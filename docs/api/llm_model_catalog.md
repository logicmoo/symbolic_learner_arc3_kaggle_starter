> [← Project README](../../README.md)

# Table of Contents

* [llm\_model\_catalog](#llm_model_catalog)
  * [ProviderBackend](#llm_model_catalog.ProviderBackend)
    * [backend\_id](#llm_model_catalog.ProviderBackend.backend_id)
    * [label](#llm_model_catalog.ProviderBackend.label)
    * [adapter](#llm_model_catalog.ProviderBackend.adapter)
    * [enabled](#llm_model_catalog.ProviderBackend.enabled)
    * [api\_key\_env](#llm_model_catalog.ProviderBackend.api_key_env)
    * [api\_key\_optional](#llm_model_catalog.ProviderBackend.api_key_optional)
    * [base\_url](#llm_model_catalog.ProviderBackend.base_url)
    * [base\_url\_env](#llm_model_catalog.ProviderBackend.base_url_env)
    * [health\_url](#llm_model_catalog.ProviderBackend.health_url)
    * [health\_url\_env](#llm_model_catalog.ProviderBackend.health_url_env)
    * [supports\_reasoning](#llm_model_catalog.ProviderBackend.supports_reasoning)
    * [timeout\_seconds](#llm_model_catalog.ProviderBackend.timeout_seconds)
    * [anthropic\_version](#llm_model_catalog.ProviderBackend.anthropic_version)
    * [default\_model](#llm_model_catalog.ProviderBackend.default_model)
    * [from\_mapping](#llm_model_catalog.ProviderBackend.from_mapping)
  * [ModelDefinition](#llm_model_catalog.ModelDefinition)
    * [model\_id](#llm_model_catalog.ModelDefinition.model_id)
    * [provider\_id](#llm_model_catalog.ModelDefinition.provider_id)
    * [label](#llm_model_catalog.ModelDefinition.label)
    * [model](#llm_model_catalog.ModelDefinition.model)
    * [model\_env](#llm_model_catalog.ModelDefinition.model_env)
    * [supports\_reasoning](#llm_model_catalog.ModelDefinition.supports_reasoning)
    * [vision](#llm_model_catalog.ModelDefinition.vision)
    * [default\_level](#llm_model_catalog.ModelDefinition.default_level)
    * [from\_mapping](#llm_model_catalog.ModelDefinition.from_mapping)
    * [resolved\_model](#llm_model_catalog.ModelDefinition.resolved_model)
  * [ProfileDefinition](#llm_model_catalog.ProfileDefinition)
    * [profile\_id](#llm_model_catalog.ProfileDefinition.profile_id)
    * [model\_id](#llm_model_catalog.ProfileDefinition.model_id)
    * [label](#llm_model_catalog.ProfileDefinition.label)
    * [analysis\_level](#llm_model_catalog.ProfileDefinition.analysis_level)
    * [single\_enabled](#llm_model_catalog.ProfileDefinition.single_enabled)
    * [batch\_enabled](#llm_model_catalog.ProfileDefinition.batch_enabled)
    * [max\_output\_tokens](#llm_model_catalog.ProfileDefinition.max_output_tokens)
    * [temperature](#llm_model_catalog.ProfileDefinition.temperature)
    * [top\_p](#llm_model_catalog.ProfileDefinition.top_p)
    * [reasoning\_effort](#llm_model_catalog.ProfileDefinition.reasoning_effort)
    * [current\_image\_detail](#llm_model_catalog.ProfileDefinition.current_image_detail)
    * [parent\_image\_detail](#llm_model_catalog.ProfileDefinition.parent_image_detail)
    * [timeout\_seconds](#llm_model_catalog.ProfileDefinition.timeout_seconds)
    * [seed](#llm_model_catalog.ProfileDefinition.seed)
    * [prompt\_text](#llm_model_catalog.ProfileDefinition.prompt_text)
    * [from\_mapping](#llm_model_catalog.ProfileDefinition.from_mapping)
  * [CatalogAwareLlmProviderRouter](#llm_model_catalog.CatalogAwareLlmProviderRouter)
    * [\_\_init\_\_](#llm_model_catalog.CatalogAwareLlmProviderRouter.__init__)
    * [\_\_del\_\_](#llm_model_catalog.CatalogAwareLlmProviderRouter.__del__)
    * [profile\_for\_spec](#llm_model_catalog.CatalogAwareLlmProviderRouter.profile_for_spec)
    * [model\_for\_profile](#llm_model_catalog.CatalogAwareLlmProviderRouter.model_for_profile)
    * [backend\_for\_profile](#llm_model_catalog.CatalogAwareLlmProviderRouter.backend_for_profile)
    * [profiles\_for\_model](#llm_model_catalog.CatalogAwareLlmProviderRouter.profiles_for_model)
    * [default\_profile\_for\_model](#llm_model_catalog.CatalogAwareLlmProviderRouter.default_profile_for_model)
    * [configured\_profile\_specs](#llm_model_catalog.CatalogAwareLlmProviderRouter.configured_profile_specs)
    * [configured\_model\_ids](#llm_model_catalog.CatalogAwareLlmProviderRouter.configured_model_ids)
    * [select\_model](#llm_model_catalog.CatalogAwareLlmProviderRouter.select_model)
    * [cycle\_model](#llm_model_catalog.CatalogAwareLlmProviderRouter.cycle_model)
    * [activate\_level](#llm_model_catalog.CatalogAwareLlmProviderRouter.activate_level)
    * [select\_profile](#llm_model_catalog.CatalogAwareLlmProviderRouter.select_profile)
    * [select](#llm_model_catalog.CatalogAwareLlmProviderRouter.select)
    * [batch\_profiles](#llm_model_catalog.CatalogAwareLlmProviderRouter.batch_profiles)
    * [active\_model](#llm_model_catalog.CatalogAwareLlmProviderRouter.active_model)
    * [describe\_current](#llm_model_catalog.CatalogAwareLlmProviderRouter.describe_current)
    * [profile\_environment](#llm_model_catalog.CatalogAwareLlmProviderRouter.profile_environment)

<a id="llm_model_catalog"></a>

# llm\_model\_catalog

<a id="llm_model_catalog.ProviderBackend"></a>

## ProviderBackend Objects

```python
@dataclass(frozen=True)
class ProviderBackend()
```

<a id="llm_model_catalog.ProviderBackend.backend_id"></a>

#### backend\_id: `str`

<a id="llm_model_catalog.ProviderBackend.label"></a>

#### label: `str`

<a id="llm_model_catalog.ProviderBackend.adapter"></a>

#### adapter: `str`

<a id="llm_model_catalog.ProviderBackend.enabled"></a>

#### enabled: `bool | str`

<a id="llm_model_catalog.ProviderBackend.api_key_env"></a>

#### api\_key\_env: `str | None`

<a id="llm_model_catalog.ProviderBackend.api_key_optional"></a>

#### api\_key\_optional: `bool`

<a id="llm_model_catalog.ProviderBackend.base_url"></a>

#### base\_url: `str | None`

<a id="llm_model_catalog.ProviderBackend.base_url_env"></a>

#### base\_url\_env: `str | None`

<a id="llm_model_catalog.ProviderBackend.health_url"></a>

#### health\_url: `str | None`

<a id="llm_model_catalog.ProviderBackend.health_url_env"></a>

#### health\_url\_env: `str | None`

<a id="llm_model_catalog.ProviderBackend.supports_reasoning"></a>

#### supports\_reasoning: `bool`

<a id="llm_model_catalog.ProviderBackend.timeout_seconds"></a>

#### timeout\_seconds: `float`

<a id="llm_model_catalog.ProviderBackend.anthropic_version"></a>

#### anthropic\_version: `str`

<a id="llm_model_catalog.ProviderBackend.default_model"></a>

#### default\_model: `str | None`

<a id="llm_model_catalog.ProviderBackend.from_mapping"></a>

#### from\_mapping

```python
@classmethod
def from_mapping(cls, raw: Mapping[str, Any]) -> "ProviderBackend"
```

<a id="llm_model_catalog.ModelDefinition"></a>

## ModelDefinition Objects

```python
@dataclass(frozen=True)
class ModelDefinition()
```

<a id="llm_model_catalog.ModelDefinition.model_id"></a>

#### model\_id: `str`

<a id="llm_model_catalog.ModelDefinition.provider_id"></a>

#### provider\_id: `str`

<a id="llm_model_catalog.ModelDefinition.label"></a>

#### label: `str`

<a id="llm_model_catalog.ModelDefinition.model"></a>

#### model: `str`

<a id="llm_model_catalog.ModelDefinition.model_env"></a>

#### model\_env: `str | None`

<a id="llm_model_catalog.ModelDefinition.supports_reasoning"></a>

#### supports\_reasoning: `bool | None`

<a id="llm_model_catalog.ModelDefinition.vision"></a>

#### vision: `bool`

<a id="llm_model_catalog.ModelDefinition.default_level"></a>

#### default\_level: `int`

<a id="llm_model_catalog.ModelDefinition.from_mapping"></a>

#### from\_mapping

```python
@classmethod
def from_mapping(cls, raw: Mapping[str, Any]) -> "ModelDefinition"
```

<a id="llm_model_catalog.ModelDefinition.resolved_model"></a>

#### resolved\_model

```python
def resolved_model() -> str
```

<a id="llm_model_catalog.ProfileDefinition"></a>

## ProfileDefinition Objects

```python
@dataclass(frozen=True)
class ProfileDefinition()
```

<a id="llm_model_catalog.ProfileDefinition.profile_id"></a>

#### profile\_id: `str`

<a id="llm_model_catalog.ProfileDefinition.model_id"></a>

#### model\_id: `str`

<a id="llm_model_catalog.ProfileDefinition.label"></a>

#### label: `str`

<a id="llm_model_catalog.ProfileDefinition.analysis_level"></a>

#### analysis\_level: `int`

<a id="llm_model_catalog.ProfileDefinition.single_enabled"></a>

#### single\_enabled: `bool`

<a id="llm_model_catalog.ProfileDefinition.batch_enabled"></a>

#### batch\_enabled: `bool`

<a id="llm_model_catalog.ProfileDefinition.max_output_tokens"></a>

#### max\_output\_tokens: `int`

<a id="llm_model_catalog.ProfileDefinition.temperature"></a>

#### temperature: `float | None`

<a id="llm_model_catalog.ProfileDefinition.top_p"></a>

#### top\_p: `float | None`

<a id="llm_model_catalog.ProfileDefinition.reasoning_effort"></a>

#### reasoning\_effort: `str`

<a id="llm_model_catalog.ProfileDefinition.current_image_detail"></a>

#### current\_image\_detail: `str`

<a id="llm_model_catalog.ProfileDefinition.parent_image_detail"></a>

#### parent\_image\_detail: `str`

<a id="llm_model_catalog.ProfileDefinition.timeout_seconds"></a>

#### timeout\_seconds: `float`

<a id="llm_model_catalog.ProfileDefinition.seed"></a>

#### seed: `int | None`

<a id="llm_model_catalog.ProfileDefinition.prompt_text"></a>

#### prompt\_text: `tuple[str, ...]`

<a id="llm_model_catalog.ProfileDefinition.from_mapping"></a>

#### from\_mapping

```python
@classmethod
def from_mapping(cls, raw: Mapping[str, Any]) -> "ProfileDefinition"
```

<a id="llm_model_catalog.CatalogAwareLlmProviderRouter"></a>

## CatalogAwareLlmProviderRouter Objects

```python
class CatalogAwareLlmProviderRouter(StudioAwareLlmProviderRouter)
```

Router over provider backends, models, and level-specific profiles.

The existing low-level adapters continue to receive a flat ProviderSpec.
This class expands each profile into that compatibility shape at startup,
while retaining the normalized three-layer catalog for the UI and runner.

<a id="llm_model_catalog.CatalogAwareLlmProviderRouter.__init__"></a>

#### \_\_init\_\_

```python
def __init__(config_path: str | Path, **kwargs: Any) -> None
```

<a id="llm_model_catalog.CatalogAwareLlmProviderRouter.__del__"></a>

#### \_\_del\_\_

```python
def __del__() -> None
```

<a id="llm_model_catalog.CatalogAwareLlmProviderRouter.profile_for_spec"></a>

#### profile\_for\_spec

```python
def profile_for_spec(spec: ProviderSpec | None = None) -> ProfileDefinition
```

<a id="llm_model_catalog.CatalogAwareLlmProviderRouter.model_for_profile"></a>

#### model\_for\_profile

```python
def model_for_profile(
        profile: str | ProfileDefinition | ProviderSpec) -> ModelDefinition
```

<a id="llm_model_catalog.CatalogAwareLlmProviderRouter.backend_for_profile"></a>

#### backend\_for\_profile

```python
def backend_for_profile(
        profile: str | ProfileDefinition | ProviderSpec) -> ProviderBackend
```

<a id="llm_model_catalog.CatalogAwareLlmProviderRouter.profiles_for_model"></a>

#### profiles\_for\_model

```python
def profiles_for_model(model_id: str) -> tuple[ProfileDefinition, ...]
```

<a id="llm_model_catalog.CatalogAwareLlmProviderRouter.default_profile_for_model"></a>

#### default\_profile\_for\_model

```python
def default_profile_for_model(model_id: str) -> ProfileDefinition
```

<a id="llm_model_catalog.CatalogAwareLlmProviderRouter.configured_profile_specs"></a>

#### configured\_profile\_specs

```python
def configured_profile_specs(
        *,
        single: bool | None = None,
        batch: bool | None = None) -> tuple[ProviderSpec, ...]
```

<a id="llm_model_catalog.CatalogAwareLlmProviderRouter.configured_model_ids"></a>

#### configured\_model\_ids

```python
def configured_model_ids() -> tuple[str, ...]
```

<a id="llm_model_catalog.CatalogAwareLlmProviderRouter.select_model"></a>

#### select\_model

```python
def select_model(model_id: str) -> ProviderSpec
```

<a id="llm_model_catalog.CatalogAwareLlmProviderRouter.cycle_model"></a>

#### cycle\_model

```python
def cycle_model() -> ProviderSpec
```

<a id="llm_model_catalog.CatalogAwareLlmProviderRouter.activate_level"></a>

#### activate\_level

```python
def activate_level(level: int, *, mode: str = "single") -> ProviderSpec
```

<a id="llm_model_catalog.CatalogAwareLlmProviderRouter.select_profile"></a>

#### select\_profile

```python
def select_profile(profile_id: str,
                   *,
                   mode: str | None = None) -> ProviderSpec
```

<a id="llm_model_catalog.CatalogAwareLlmProviderRouter.select"></a>

#### select

```python
def select(provider_id: str) -> ProviderSpec
```

<a id="llm_model_catalog.CatalogAwareLlmProviderRouter.batch_profiles"></a>

#### batch\_profiles

```python
def batch_profiles() -> tuple[ProfileDefinition, ...]
```

<a id="llm_model_catalog.CatalogAwareLlmProviderRouter.active_model"></a>

#### active\_model

```python
def active_model() -> ModelDefinition
```

<a id="llm_model_catalog.CatalogAwareLlmProviderRouter.describe_current"></a>

#### describe\_current

```python
def describe_current() -> str
```

<a id="llm_model_catalog.CatalogAwareLlmProviderRouter.profile_environment"></a>

#### profile\_environment

```python
@contextmanager
def profile_environment(
        profile: ProfileDefinition | str | None = None) -> Iterator[None]
```
