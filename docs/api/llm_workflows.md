> [← Project README](../../README.md)

# Table of Contents

* [llm\_workflows](#llm_workflows)
  * [WorkflowAwareLlmProviderRouter](#llm_workflows.WorkflowAwareLlmProviderRouter)

<a id="llm_workflows"></a>

# llm\_workflows

<a id="llm_workflows.WorkflowAwareLlmProviderRouter"></a>

## WorkflowAwareLlmProviderRouter Objects

```python
class WorkflowAwareLlmProviderRouter(CatalogAwareLlmProviderRouter)
```

Catalog router extended with optional transactions and workflows.

The normal lowercase-g / level-4 path remains unchanged. The companion
workflow file contributes additional models and profiles plus specialized
transactions that can be orchestrated only when requested.
