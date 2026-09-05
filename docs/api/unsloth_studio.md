> [← Project README](../../README.md)

# Table of Contents

* [unsloth\_studio](#unsloth_studio)
  * [StudioAwareLlmProviderRouter](#unsloth_studio.StudioAwareLlmProviderRouter)
    * [\_\_init\_\_](#unsloth_studio.StudioAwareLlmProviderRouter.__init__)
    * [ensure\_unsloth\_model\_loaded](#unsloth_studio.StudioAwareLlmProviderRouter.ensure_unsloth_model_loaded)
    * [statuses](#unsloth_studio.StudioAwareLlmProviderRouter.statuses)
    * [create\_response](#unsloth_studio.StudioAwareLlmProviderRouter.create_response)

<a id="unsloth_studio"></a>

# unsloth\_studio

<a id="unsloth_studio.StudioAwareLlmProviderRouter"></a>

## StudioAwareLlmProviderRouter Objects

```python
class StudioAwareLlmProviderRouter(LlmProviderRouter)
```

LLM router that manages the resident model in Unsloth Studio.

Unsloth Studio can be healthy and authenticated while its llama-server has
no model loaded. Before an Unsloth `/v1/responses` request, this router uses
the authenticated management API to inspect `/api/inference/status`, load
the configured GGUF through `/api/inference/load` when necessary, and wait
until the requested model is resident.

<a id="unsloth_studio.StudioAwareLlmProviderRouter.__init__"></a>

#### \_\_init\_\_

```python
def __init__(*args: Any,
             sleep: Callable[[float], None] | None = None,
             clock: Callable[[], float] | None = None,
             **kwargs: Any) -> None
```

<a id="unsloth_studio.StudioAwareLlmProviderRouter.ensure_unsloth_model_loaded"></a>

#### ensure\_unsloth\_model\_loaded

```python
def ensure_unsloth_model_loaded(spec: ProviderSpec,
                                *,
                                force: bool = False) -> dict[str, Any]
```

<a id="unsloth_studio.StudioAwareLlmProviderRouter.statuses"></a>

#### statuses

```python
def statuses(*, probe: bool = False) -> tuple[ProviderStatus, ...]
```

<a id="unsloth_studio.StudioAwareLlmProviderRouter.create_response"></a>

#### create\_response

```python
def create_response(**kwargs: Any) -> Any
```
