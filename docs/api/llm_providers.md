> [← Project README](../../README.md)

# Table of Contents

* [llm\_providers](#llm_providers)
  * [DEFAULT\_CONFIG\_PATH](#llm_providers.DEFAULT_CONFIG_PATH)
  * [LlmConfigurationError](#llm_providers.LlmConfigurationError)
  * [LlmRequestError](#llm_providers.LlmRequestError)
  * [ProviderSpec](#llm_providers.ProviderSpec)
    * [provider\_id](#llm_providers.ProviderSpec.provider_id)
    * [label](#llm_providers.ProviderSpec.label)
    * [adapter](#llm_providers.ProviderSpec.adapter)
    * [model](#llm_providers.ProviderSpec.model)
    * [enabled](#llm_providers.ProviderSpec.enabled)
    * [model\_env](#llm_providers.ProviderSpec.model_env)
    * [api\_key\_env](#llm_providers.ProviderSpec.api_key_env)
    * [api\_key\_optional](#llm_providers.ProviderSpec.api_key_optional)
    * [base\_url](#llm_providers.ProviderSpec.base_url)
    * [base\_url\_env](#llm_providers.ProviderSpec.base_url_env)
    * [health\_url](#llm_providers.ProviderSpec.health_url)
    * [health\_url\_env](#llm_providers.ProviderSpec.health_url_env)
    * [supports\_reasoning](#llm_providers.ProviderSpec.supports_reasoning)
    * [timeout\_seconds](#llm_providers.ProviderSpec.timeout_seconds)
    * [anthropic\_version](#llm_providers.ProviderSpec.anthropic_version)
    * [prompt\_text](#llm_providers.ProviderSpec.prompt_text)
    * [from\_mapping](#llm_providers.ProviderSpec.from_mapping)
    * [resolved\_model](#llm_providers.ProviderSpec.resolved_model)
    * [resolved\_api\_key](#llm_providers.ProviderSpec.resolved_api_key)
    * [resolved\_base\_url](#llm_providers.ProviderSpec.resolved_base_url)
    * [resolved\_health\_url](#llm_providers.ProviderSpec.resolved_health_url)
    * [configuration\_state](#llm_providers.ProviderSpec.configuration_state)
  * [ProviderStatus](#llm_providers.ProviderStatus)
    * [provider\_id](#llm_providers.ProviderStatus.provider_id)
    * [label](#llm_providers.ProviderStatus.label)
    * [model](#llm_providers.ProviderStatus.model)
    * [configured](#llm_providers.ProviderStatus.configured)
    * [state](#llm_providers.ProviderStatus.state)
    * [active](#llm_providers.ProviderStatus.active)
    * [base\_url](#llm_providers.ProviderStatus.base_url)
  * [\_ResponsesFacade](#llm_providers._ResponsesFacade)
    * [\_\_init\_\_](#llm_providers._ResponsesFacade.__init__)
    * [create](#llm_providers._ResponsesFacade.create)
  * [LlmProviderRouter](#llm_providers.LlmProviderRouter)
    * [\_\_init\_\_](#llm_providers.LlmProviderRouter.__init__)
    * [configured\_specs](#llm_providers.LlmProviderRouter.configured_specs)
    * [current\_spec](#llm_providers.LlmProviderRouter.current_spec)
    * [prompt\_section\_names](#llm_providers.LlmProviderRouter.prompt_section_names)
    * [prompt\_sections](#llm_providers.LlmProviderRouter.prompt_sections)
    * [compose\_prompt](#llm_providers.LlmProviderRouter.compose_prompt)
    * [cycle](#llm_providers.LlmProviderRouter.cycle)
    * [select](#llm_providers.LlmProviderRouter.select)
    * [statuses](#llm_providers.LlmProviderRouter.statuses)
    * [describe\_current](#llm_providers.LlmProviderRouter.describe_current)
    * [create\_response](#llm_providers.LlmProviderRouter.create_response)

<a id="llm_providers"></a>

# llm\_providers

<a id="llm_providers.DEFAULT_CONFIG_PATH"></a>

#### DEFAULT\_CONFIG\_PATH

<a id="llm_providers.LlmConfigurationError"></a>

## LlmConfigurationError Objects

```python
class LlmConfigurationError(RuntimeError)
```

Raised when no usable LLM provider can be selected.

<a id="llm_providers.LlmRequestError"></a>

## LlmRequestError Objects

```python
class LlmRequestError(RuntimeError)
```

Raised when a provider request fails or returns no text.

<a id="llm_providers.ProviderSpec"></a>

## ProviderSpec Objects

```python
@dataclass(frozen=True)
class ProviderSpec()
```

<a id="llm_providers.ProviderSpec.provider_id"></a>

#### provider\_id: `str`

<a id="llm_providers.ProviderSpec.label"></a>

#### label: `str`

<a id="llm_providers.ProviderSpec.adapter"></a>

#### adapter: `str`

<a id="llm_providers.ProviderSpec.model"></a>

#### model: `str`

<a id="llm_providers.ProviderSpec.enabled"></a>

#### enabled: `bool | str`

<a id="llm_providers.ProviderSpec.model_env"></a>

#### model\_env: `str | None`

<a id="llm_providers.ProviderSpec.api_key_env"></a>

#### api\_key\_env: `str | None`

<a id="llm_providers.ProviderSpec.api_key_optional"></a>

#### api\_key\_optional: `bool`

<a id="llm_providers.ProviderSpec.base_url"></a>

#### base\_url: `str | None`

<a id="llm_providers.ProviderSpec.base_url_env"></a>

#### base\_url\_env: `str | None`

<a id="llm_providers.ProviderSpec.health_url"></a>

#### health\_url: `str | None`

<a id="llm_providers.ProviderSpec.health_url_env"></a>

#### health\_url\_env: `str | None`

<a id="llm_providers.ProviderSpec.supports_reasoning"></a>

#### supports\_reasoning: `bool`

<a id="llm_providers.ProviderSpec.timeout_seconds"></a>

#### timeout\_seconds: `float`

<a id="llm_providers.ProviderSpec.anthropic_version"></a>

#### anthropic\_version: `str`

<a id="llm_providers.ProviderSpec.prompt_text"></a>

#### prompt\_text: `tuple[str, ...]`

<a id="llm_providers.ProviderSpec.from_mapping"></a>

#### from\_mapping

```python
@classmethod
def from_mapping(cls, raw: Mapping[str, Any]) -> "ProviderSpec"
```

<a id="llm_providers.ProviderSpec.resolved_model"></a>

#### resolved\_model

```python
def resolved_model() -> str
```

<a id="llm_providers.ProviderSpec.resolved_api_key"></a>

#### resolved\_api\_key

```python
def resolved_api_key() -> str | None
```

<a id="llm_providers.ProviderSpec.resolved_base_url"></a>

#### resolved\_base\_url

```python
def resolved_base_url() -> str | None
```

<a id="llm_providers.ProviderSpec.resolved_health_url"></a>

#### resolved\_health\_url

```python
def resolved_health_url() -> str | None
```

<a id="llm_providers.ProviderSpec.configuration_state"></a>

#### configuration\_state

```python
def configuration_state() -> tuple[bool, str]
```

<a id="llm_providers.ProviderStatus"></a>

## ProviderStatus Objects

```python
@dataclass(frozen=True)
class ProviderStatus()
```

<a id="llm_providers.ProviderStatus.provider_id"></a>

#### provider\_id: `str`

<a id="llm_providers.ProviderStatus.label"></a>

#### label: `str`

<a id="llm_providers.ProviderStatus.model"></a>

#### model: `str`

<a id="llm_providers.ProviderStatus.configured"></a>

#### configured: `bool`

<a id="llm_providers.ProviderStatus.state"></a>

#### state: `str`

<a id="llm_providers.ProviderStatus.active"></a>

#### active: `bool`

<a id="llm_providers.ProviderStatus.base_url"></a>

#### base\_url: `str | None`

<a id="llm_providers._ResponsesFacade"></a>

## \_ResponsesFacade Objects

```python
class _ResponsesFacade()
```

<a id="llm_providers._ResponsesFacade.__init__"></a>

#### \_\_init\_\_

```python
def __init__(router: "LlmProviderRouter") -> None
```

<a id="llm_providers._ResponsesFacade.create"></a>

#### create

```python
def create(**kwargs: Any) -> Any
```

<a id="llm_providers.LlmProviderRouter"></a>

## LlmProviderRouter Objects

```python
class LlmProviderRouter()
```

OpenAI-Responses-shaped router over cloud and local LLM providers.

Provider definitions and reusable prompt sections share one JSON config.
Each provider selects an ordered list of ``prompt_text`` section names, so
expensive or irrelevant sections such as ``transitions`` can be omitted
without copying or editing one monolithic combined prompt.

<a id="llm_providers.LlmProviderRouter.__init__"></a>

#### \_\_init\_\_

```python
def __init__(config_path: str | Path | None = None,
             *,
             openai_client_factory: Callable[..., Any] | None = None,
             urlopen: Callable[..., Any] | None = None) -> None
```

<a id="llm_providers.LlmProviderRouter.configured_specs"></a>

#### configured\_specs

```python
def configured_specs() -> tuple[ProviderSpec, ...]
```

<a id="llm_providers.LlmProviderRouter.current_spec"></a>

#### current\_spec

```python
def current_spec() -> ProviderSpec
```

<a id="llm_providers.LlmProviderRouter.prompt_section_names"></a>

#### prompt\_section\_names

```python
def prompt_section_names(spec: ProviderSpec | None = None) -> tuple[str, ...]
```

<a id="llm_providers.LlmProviderRouter.prompt_sections"></a>

#### prompt\_sections

```python
def prompt_sections(
        spec: ProviderSpec | None = None) -> tuple[tuple[str, str], ...]
```

<a id="llm_providers.LlmProviderRouter.compose_prompt"></a>

#### compose\_prompt

```python
def compose_prompt(spec: ProviderSpec | None = None) -> str
```

<a id="llm_providers.LlmProviderRouter.cycle"></a>

#### cycle

```python
def cycle() -> ProviderSpec
```

<a id="llm_providers.LlmProviderRouter.select"></a>

#### select

```python
def select(provider_id: str) -> ProviderSpec
```

<a id="llm_providers.LlmProviderRouter.statuses"></a>

#### statuses

```python
def statuses(*, probe: bool = False) -> tuple[ProviderStatus, ...]
```

<a id="llm_providers.LlmProviderRouter.describe_current"></a>

#### describe\_current

```python
def describe_current() -> str
```

<a id="llm_providers.LlmProviderRouter.create_response"></a>

#### create\_response

```python
def create_response(**kwargs: Any) -> Any
```
