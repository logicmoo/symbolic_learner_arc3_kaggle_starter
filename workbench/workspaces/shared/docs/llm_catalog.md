[← Back to top-level README](../../../../README.md)

# LLM Catalog

The LLM catalog is a single inheritance tree stored under `models/`.

- **Backend** nodes are roots. They define connectivity: provider, API adapter, endpoint, credentials environment variables, executable, health checks, and provider defaults.
- **Model** nodes inherit a backend. They identify the concrete remote/local model and may establish generation defaults.
- **Model Preset** nodes are still `kind model`, but inherit a model or another preset. The UI infers their role from that parent relationship. Presets specialize invocation settings for light, deep, deterministic, exploratory, or high-budget use.

Model Presets are deliberately prompt-free. Changing temperature or reasoning effort should not silently change what operation the LLM is being asked to perform. Prompt Profiles are a separate prompt-composition concept and are not Model Presets.

A typical chain is:

```text
OpenAI backend
  -> GPT-5.6 model
      -> GPT-5.6 light preset
      -> GPT-5.6 deep preset
          -> GPT-5.6 deep, long-output preset
```

The resolved runtime configuration is the merged result of the whole inheritance chain.
