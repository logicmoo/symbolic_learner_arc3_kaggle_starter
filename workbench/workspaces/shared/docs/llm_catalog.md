# LLM Catalog

The LLM catalog is a single inheritance tree stored under `models/`.

- **Backend** nodes are roots. They define connectivity: provider, API adapter, endpoint, credentials environment variables, executable, health checks, and provider defaults.
- **Model** nodes inherit a backend or another model. They identify the concrete remote/local model and may override generation defaults.
- **Profile** nodes inherit a model or another profile. They are reusable execution presets such as light, deep, deterministic, exploratory, or high-budget.

Profiles are deliberately prompt-free. Changing temperature or reasoning effort should not silently change what task the LLM is being asked to perform.

A typical chain is:

```text
OpenAI backend
  -> GPT-5.6 model
      -> GPT-5.6 light profile
      -> GPT-5.6 deep profile
      -> GPT-5.6 extreme profile
```

The resolved runtime configuration is the merged result of the whole inheritance chain.
