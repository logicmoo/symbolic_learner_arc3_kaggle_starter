> [← Project README](../../README.md)

# Table of Contents

* [unsloth\_studio](#unsloth_studio)
  * [StudioAwareLlmProviderRouter](#unsloth_studio.StudioAwareLlmProviderRouter)

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
