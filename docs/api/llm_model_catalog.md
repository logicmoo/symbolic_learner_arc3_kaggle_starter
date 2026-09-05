> [← Project README](../../README.md)

# Table of Contents

* [llm\_model\_catalog](#llm_model_catalog)
  * [CatalogAwareLlmProviderRouter](#llm_model_catalog.CatalogAwareLlmProviderRouter)

<a id="llm_model_catalog"></a>

# llm\_model\_catalog

<a id="llm_model_catalog.CatalogAwareLlmProviderRouter"></a>

## CatalogAwareLlmProviderRouter Objects

```python
class CatalogAwareLlmProviderRouter(StudioAwareLlmProviderRouter)
```

Router over provider backends, models, and level-specific profiles.

The existing low-level adapters continue to receive a flat ProviderSpec.
This class expands each profile into that compatibility shape at startup,
while retaining the normalized three-layer catalog for the UI and runner.
