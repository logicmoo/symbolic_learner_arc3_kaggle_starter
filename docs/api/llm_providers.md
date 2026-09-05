> [← Project README](../../README.md)

# Table of Contents

* [llm\_providers](#llm_providers)
  * [LlmConfigurationError](#llm_providers.LlmConfigurationError)
  * [LlmRequestError](#llm_providers.LlmRequestError)
  * [LlmProviderRouter](#llm_providers.LlmProviderRouter)

<a id="llm_providers"></a>

# llm\_providers

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
