# Models, Profiles, Tasks, and Prompts

The workbench keeps four concepts separate because they answer different questions.

## Backend

A backend is a root runtime/provider configuration. It describes **how to reach a capability**: API adapter, endpoint, credentials environment variables, executable, health check, and provider-level defaults.

Backends live in the unified `models/` catalog and are identified by:

```json
{"kind":"backend","id":"openai"}
```

## Model

A model selects a concrete remote/local model or inherits another model. It describes **what model is being used**. Model nodes may override generation defaults such as temperature, token limits, reasoning effort, timeout, or image detail.

```json
{
  "kind":"model",
  "id":"gpt-5.6",
  "inherits":"openai",
  "model":"gpt-5.6"
}
```

## Profile

A profile is a reusable model configuration. It describes **how we want to run a model for a class of jobs**, but it does not contain prompts.

```json
{
  "kind":"profile",
  "id":"gpt-5.6-deep",
  "inherits":"gpt-5.6",
  "defaults": {
    "temperature":0.05,
    "reasoningEffort":"medium",
    "maxOutputTokens":22000
  }
}
```

Profiles participate in the same inheritance graph as models. A profile can inherit a model or another profile.

## Prompt

A prompt is reusable instruction text. Prompts live under `prompts/` and are edited independently of models and profiles.

```json
{
  "kind":"prompt",
  "id":"coordinate_contract",
  "text":"Reason in logical grid coordinates..."
}
```

## Task

A task is the executable semantic operation. The old ARC3 `llm_profiles` records mixed two unrelated concerns: model execution settings and a `prompt_text` list. The workbench splits those concerns.

The execution settings become model/profile inheritance nodes. The `prompt_text` list belongs to the **task**, because choosing and ordering prompts defines what the task asks the LLM to do.

Conceptually:

```text
backend
  -> model
      -> profile

prompt fragments ------------------+
                                   |
task -> chooses model/profile -----+--> LLM invocation
     -> chooses ordered prompts ---+
```

A task can therefore use the same prompt composition with several model profiles, or the same model profile with completely different prompt compositions.

## ARC3 migration rule

For an old profile such as `openai-gpt-5.6-deep`:

- `model`, `temperature`, `top_p`, `reasoning_effort`, token limits, timeout, and image-detail settings become a model/profile node.
- `prompt_text` does **not** become part of that profile.
- The ordered `prompt_text` entries become the prompt selection/composition on the task that performs that ARC3 analysis.

This separation keeps the shared library reusable outside ARC3 while preserving the old behavior when an ARC3 task explicitly selects the same prompts and profile.
